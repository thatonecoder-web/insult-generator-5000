"""A small HTTP server for the web interface: a JSON API plus static files.

Standard library only. It is meant for local use and demos. For a public deployment, run
the API behind a production web server.
"""

from __future__ import annotations

import gzip
import json
import mimetypes
import sys
from collections.abc import Callable
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from typing import Any
from urllib.parse import unquote, urlsplit

from insultgen import __version__
from insultgen.service import ApiError, InsultService

MAX_BODY_BYTES = 4096
GZIP_MIN_BYTES = 1024
SECURITY_HEADERS = {
    "X-Content-Type-Options": "nosniff",
    "Referrer-Policy": "no-referrer",
    "X-Frame-Options": "DENY",
    "Content-Security-Policy": (
        "default-src 'self'; img-src 'self' data:; style-src 'self' 'unsafe-inline'; "
        "frame-ancestors 'none'"
    ),
}
CHARSET_TYPES = ("application/json", "application/javascript", "text/javascript")
COMPRESSIBLE = ("text/", "application/json", "application/javascript", "image/svg+xml")
NOT_BUILT_MESSAGE = (
    "The web interface has not been built yet. Run `npm install && npm run build` "
    "inside the web/ directory, then restart the server. The API is available at /api/."
)


class InsultServer(ThreadingHTTPServer):
    """HTTP server that carries the service and the static directory for its handlers."""

    daemon_threads = True

    def __init__(
        self, address: tuple[str, int], service: InsultService, web_dir: Path | None
    ) -> None:
        super().__init__(address, _Handler)
        self.service = service
        self.web_dir = web_dir.resolve() if web_dir is not None else None
        self.cache: dict[str, bytes] = {}


class _Handler(BaseHTTPRequestHandler):
    server: InsultServer
    server_version = f"insultgen/{__version__}"

    def do_GET(self) -> None:
        path = urlsplit(self.path).path
        try:
            if path == "/api/health":
                self._send_json({"status": "ok", "version": __version__})
            elif path == "/api/meta":
                self._send_json(self.server.service.meta())
            elif path == "/api/vocabulary":
                self._send_cached_json("vocabulary", self.server.service.vocabulary_payload)
            elif path.startswith("/api/"):
                raise ApiError(404, "unknown API endpoint")
            else:
                self._send_static(path)
        except ApiError as error:
            self._send_json({"error": error.message}, error.status)

    def do_HEAD(self) -> None:
        self.do_GET()

    def do_POST(self) -> None:
        path = urlsplit(self.path).path
        try:
            if path != "/api/generate":
                raise ApiError(404, "unknown API endpoint")
            payload = self._read_json()
            self._send_json(self.server.service.generate(payload))
        except ApiError as error:
            self._send_json({"error": error.message}, error.status)

    def _read_json(self) -> object:
        content_type = self.headers.get("Content-Type", "").split(";")[0].strip().lower()
        if content_type != "application/json":
            raise ApiError(415, "Content-Type must be application/json")
        try:
            length = int(self.headers.get("Content-Length", "0"))
        except ValueError:
            raise ApiError(400, "invalid Content-Length") from None
        if length > MAX_BODY_BYTES:
            raise ApiError(413, f"request body must be at most {MAX_BODY_BYTES} bytes")
        try:
            return json.loads(self.rfile.read(length) or b"null")
        except (UnicodeDecodeError, json.JSONDecodeError):
            raise ApiError(400, "request body is not valid JSON") from None

    def _send_cached_json(self, key: str, build: Callable[[], dict[str, Any]]) -> None:
        if key not in self.server.cache:
            self.server.cache[key] = json.dumps(build(), separators=(",", ":")).encode("utf-8")
        self._send_bytes(self.server.cache[key], "application/json")

    def _send_json(self, payload: object, status: int = 200) -> None:
        body = json.dumps(payload, separators=(",", ":")).encode("utf-8")
        self._send_bytes(body, "application/json", status)

    def _send_static(self, url_path: str) -> None:
        web_dir = self.server.web_dir
        if web_dir is None or not (web_dir / "index.html").is_file():
            self._send_bytes(NOT_BUILT_MESSAGE.encode("utf-8"), "text/plain", 404)
            return

        relative = unquote(url_path).lstrip("/") or "index.html"
        candidate = (web_dir / relative).resolve()
        if not candidate.is_relative_to(web_dir):
            self._send_bytes(b"not found", "text/plain", 404)
            return
        if candidate.is_dir():
            candidate = candidate / "index.html"
        if not candidate.is_file():
            if "." in Path(relative).name:
                self._send_bytes(b"not found", "text/plain", 404)
                return
            candidate = web_dir / "index.html"

        content_type = mimetypes.guess_type(candidate.name)[0] or "application/octet-stream"
        self._send_bytes(candidate.read_bytes(), content_type)

    def _send_bytes(self, body: bytes, content_type: str, status: int = 200) -> None:
        if content_type.startswith("text/") or content_type in CHARSET_TYPES:
            content_type = f"{content_type}; charset=utf-8"
        headers = {"Content-Type": content_type, "Vary": "Accept-Encoding"}
        headers["Cache-Control"] = "no-cache"
        if (
            len(body) >= GZIP_MIN_BYTES
            and content_type.startswith(COMPRESSIBLE)
            and "gzip" in self.headers.get("Accept-Encoding", "")
        ):
            body = gzip.compress(body, compresslevel=6)
            headers["Content-Encoding"] = "gzip"
        headers["Content-Length"] = str(len(body))

        self.send_response(status)
        for name, value in {**headers, **SECURITY_HEADERS}.items():
            self.send_header(name, value)
        self.end_headers()
        if self.command != "HEAD":
            self.wfile.write(body)

    def log_message(self, format: str, *args: Any) -> None:
        sys.stderr.write(f"{self.address_string()} {format % args}\n")


def make_server(
    host: str, port: int, service: InsultService | None = None, web_dir: Path | None = None
) -> InsultServer:
    """Create (but do not start) a server. ``port=0`` picks a free port."""
    return InsultServer((host, port), service or InsultService(), web_dir)
