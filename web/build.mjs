import { cp, mkdir, rm } from "node:fs/promises";
import * as esbuild from "esbuild";

const watch = process.argv.includes("--watch");

await rm("dist", { recursive: true, force: true });
await mkdir("dist/assets", { recursive: true });
await cp("public", "dist", { recursive: true });
await cp("index.html", "dist/index.html");

const options = {
  entryPoints: ["src/main.jsx"],
  bundle: true,
  outdir: "dist/assets",
  entryNames: "[name]",
  format: "esm",
  target: ["es2020"],
  jsx: "automatic",
  minify: !watch,
  sourcemap: watch,
  external: ["/fonts/*"],
  define: { "process.env.NODE_ENV": JSON.stringify(watch ? "development" : "production") },
  logLevel: "info",
};

if (watch) {
  const context = await esbuild.context(options);
  await context.watch();
  console.log("Watching src/ for changes. Reload the page after each rebuild.");
} else {
  await esbuild.build(options);
}
