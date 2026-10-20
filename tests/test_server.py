import gzip
import http.client
import json
import threading
from collections.abc import Iterator
from pathlib import Path

import pytest

from insultgen.server import InsultServer, make_server
from insultgen.service import InsultService


@pytest.fixture(scope="module")
def service() -> InsultService:
    return InsultService()


@pytest.fixture
def web_dir(tmp_path: Path) -> Path:
    root = tmp_path / "dist"
    (root / "assets").mkdir(parents=True)
    (root / "index.html").write_text("<!doctype html><title>app</title>", encoding="utf-8")
    (root / "assets" / "app.js").write_text("console.log('hi');", encoding="utf-8")
    (root / "assets" / "big.css").write_text("a{color:red}" * 400, encoding="utf-8")
    (tmp_path / "secret.txt").write_text("top secret", encoding="utf-8")
    return root


@pytest.fixture
def server(service: InsultService, web_dir: Path) -> Iterator[InsultServer]:
    httpd = make_server("127.0.0.1", 0, service, web_dir)
    thread = threading.Thread(target=httpd.serve_forever, daemon=True)
    thread.start()
    yield httpd
    httpd.shutdown()
    httpd.server_close()


def _request(
    httpd: InsultServer,
    method: str,
    path: str,
    body: bytes | None = None,
    headers: dict[str, str] | None = None,
) -> tuple[int, dict[str, str], bytes]:
    host, port = httpd.server_address[:2]
    connection = http.client.HTTPConnection(str(host), port, timeout=10)
    try:
        connection.request(method, path, body=body, headers=headers or {})
        response = connection.getresponse()
        data = response.read()
        return response.status, {k.lower(): v for k, v in response.getheaders()}, data
    finally:
        connection.close()


def _post_json(httpd: InsultServer, payload: object) -> tuple[int, dict[str, str], bytes]:
    return _request(
        httpd,
        "POST",
        "/api/generate",
        json.dumps(payload).encode(),
        {"Content-Type": "application/json"},
    )


def test_health(server: InsultServer) -> None:
    status, headers, body = _request(server, "GET", "/api/health")
    assert status == 200
    assert json.loads(body)["status"] == "ok"
    assert headers["content-type"].startswith("application/json")


def test_responses_carry_security_headers(server: InsultServer) -> None:
    _, headers, _ = _request(server, "GET", "/api/health")
    assert headers["x-content-type-options"] == "nosniff"
    assert "default-src 'self'" in headers["content-security-policy"]
    assert headers["x-frame-options"] == "DENY"


def test_vocabulary_is_gzipped_when_accepted(server: InsultServer, service: InsultService) -> None:
    status, headers, body = _request(
        server, "GET", "/api/vocabulary", headers={"Accept-Encoding": "gzip"}
    )
    assert status == 200
    assert headers["content-encoding"] == "gzip"
    payload = json.loads(gzip.decompress(body))
    assert len(payload["entries"]) == len(service.vocabulary_payload()["entries"])


def test_vocabulary_is_plain_without_accept_encoding(server: InsultServer) -> None:
    _, headers, body = _request(server, "GET", "/api/vocabulary")
    assert "content-encoding" not in headers
    assert json.loads(body)["concepts"]


def test_meta_endpoint(server: InsultServer) -> None:
    status, _, body = _request(server, "GET", "/api/meta")
    assert status == 200
    assert len(json.loads(body)["registers"]) == 6


def test_generate_endpoint(server: InsultServer) -> None:
    payload = {"register": "legal", "severity": 6, "seed": 3, "count": 2}
    status, _, body = _post_json(server, payload)
    assert status == 200
    results = json.loads(body)["results"]
    assert [r["seed"] for r in results] == [3, 4]
    assert all(r["register"] == "legal" for r in results)


@pytest.mark.parametrize(
    ("payload", "status"),
    [({"severity": 99}, 400), ({"register": "pirate"}, 400), ({"concept": "nope"}, 422)],
)
def test_generate_errors_are_json(server: InsultServer, payload: object, status: int) -> None:
    code, _, body = _post_json(server, payload)
    assert code == status
    assert "error" in json.loads(body)


def test_generate_rejects_bad_bodies(server: InsultServer) -> None:
    json_type = {"Content-Type": "application/json"}
    assert _request(server, "POST", "/api/generate", b"{nope", json_type)[0] == 400
    plain = {"Content-Type": "text/plain"}
    assert _request(server, "POST", "/api/generate", b"{}", plain)[0] == 415
    assert _request(server, "POST", "/api/generate", b"{}")[0] == 415
    assert _request(server, "POST", "/api/generate", b"x" * 5000, json_type)[0] == 413


def test_unknown_api_paths_are_404(server: InsultServer) -> None:
    assert _request(server, "GET", "/api/nope")[0] == 404
    json_type = {"Content-Type": "application/json"}
    assert _request(server, "POST", "/api/nope", b"{}", json_type)[0] == 404


def test_static_files_are_served(server: InsultServer) -> None:
    status, headers, body = _request(server, "GET", "/")
    assert status == 200
    assert b"<title>app</title>" in body
    assert headers["content-type"].startswith("text/html")
    status, headers, _ = _request(server, "GET", "/assets/app.js")
    assert status == 200
    assert "javascript" in headers["content-type"]


def test_large_text_assets_are_compressed(server: InsultServer) -> None:
    _, headers, body = _request(
        server, "GET", "/assets/big.css", headers={"Accept-Encoding": "gzip"}
    )
    assert headers["content-encoding"] == "gzip"
    assert gzip.decompress(body).startswith(b"a{color:red}")


def test_unknown_routes_fall_back_to_the_app(server: InsultServer) -> None:
    status, _, body = _request(server, "GET", "/lexicon/deep/link")
    assert status == 200
    assert b"<title>app</title>" in body


def test_missing_assets_are_404(server: InsultServer) -> None:
    assert _request(server, "GET", "/assets/missing.js")[0] == 404


@pytest.mark.parametrize(
    "path", ["/../secret.txt", "/%2e%2e/secret.txt", "/assets/../../secret.txt"]
)
def test_path_traversal_is_blocked(server: InsultServer, path: str) -> None:
    status, _, body = _request(server, "GET", path)
    assert b"top secret" not in body
    assert status in (200, 404)
    if status == 200:
        assert b"<title>app</title>" in body


def test_head_requests_have_no_body(server: InsultServer) -> None:
    status, headers, body = _request(server, "HEAD", "/")
    assert status == 200
    assert body == b""
    assert int(headers["content-length"]) > 0


def test_missing_web_build_explains_itself(service: InsultService) -> None:
    httpd = make_server("127.0.0.1", 0, service, None)
    thread = threading.Thread(target=httpd.serve_forever, daemon=True)
    thread.start()
    try:
        status, _, body = _request(httpd, "GET", "/")
        assert status == 404
        assert b"npm run build" in body
        assert _request(httpd, "GET", "/api/health")[0] == 200
    finally:
        httpd.shutdown()
        httpd.server_close()
