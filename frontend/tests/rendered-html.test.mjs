import assert from "node:assert/strict";
import { readFile } from "node:fs/promises";
import test from "node:test";

async function render() {
  const workerUrl = new URL("../dist/server/index.js", import.meta.url);
  workerUrl.searchParams.set("test", `${process.pid}-${Date.now()}`);
  const { default: worker } = await import(workerUrl.href);
  return worker.fetch(new Request("http://localhost/", { headers: { accept: "text/html" } }), { ASSETS: { fetch: async () => new Response("Not found", { status: 404 }) } }, { waitUntil() {}, passThroughOnException() {} });
}

test("server-renders the Phase 1 engineering workspace", async () => {
  const response = await render();
  assert.equal(response.status, 200);
  const html = await response.text();
  assert.match(html, /<title>Lighting Camera WiFi Automation<\/title>/i);
  assert.match(html, /LCWA Studio/);
  assert.match(html, /Existing-pole mode/);
  assert.match(html, /Import KML\/KMZ/);
  assert.match(html, /Customer coordinates are locked/);
  assert.doesNotMatch(html, /codex-preview|Your site is taking shape|react-loading-skeleton/i);
});

test("keeps Phase 1 controls explicit and future engines gated", async () => {
  const workspace = await readFile(new URL("../app/components/EngineeringWorkspace.tsx", import.meta.url), "utf8");
  const types = await readFile(new URL("../app/lib/types.ts", import.meta.url), "utf8");
  const packageJson = await readFile(new URL("../package.json", import.meta.url), "utf8");
  assert.match(workspace, /Draw Calculation Area/);
  assert.match(workspace, /Recommend CAP/);
  assert.match(workspace, /disabled title="Phase 6/);
  assert.match(workspace, /Restore source\/default values/);
  assert.match(types, /location_edit_authorized/);
  assert.match(packageJson, /maplibre-gl/);
  assert.doesNotMatch(packageJson, /react-loading-skeleton/);
});
