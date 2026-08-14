import assert from "node:assert/strict";
import { readFile } from "node:fs/promises";
import test from "node:test";

async function render() {
  const workerUrl = new URL("../dist/server/index.js", import.meta.url);
  workerUrl.searchParams.set("test", `${process.pid}-${Date.now()}`);
  const { default: worker } = await import(workerUrl.href);
  return worker.fetch(new Request("http://localhost/", { headers: { accept: "text/html" } }), { ASSETS: { fetch: async () => new Response("Not found", { status: 404 }) } }, { waitUntil() {}, passThroughOnException() {} });
}

test("server-renders the Phase 2 engineering workspace", async () => {
  const response = await render();
  assert.equal(response.status, 200);
  const html = await response.text();
  assert.match(html, /<title>Lighting Camera WiFi Automation<\/title>/i);
  assert.match(html, /LCWA Studio/);
  assert.match(html, /Existing-pole mode/);
  assert.match(html, /Import KML\/KMZ/);
  assert.match(html, /Catalogs/);
  assert.match(html, /Customer coordinates are locked/);
  assert.doesNotMatch(html, /codex-preview|Your site is taking shape|react-loading-skeleton/i);
});

test("exposes Phase 2 catalogs while keeping later engines gated", async () => {
  const workspace = await readFile(new URL("../app/components/EngineeringWorkspace.tsx", import.meta.url), "utf8");
  const inspector = await readFile(new URL("../app/components/PoleInspector.tsx", import.meta.url), "utf8");
  const catalogs = await readFile(new URL("../app/components/CatalogManager.tsx", import.meta.url), "utf8");
  const types = await readFile(new URL("../app/lib/types.ts", import.meta.url), "utf8");
  const api = await readFile(new URL("../app/lib/api.ts", import.meta.url), "utf8");
  const packageJson = await readFile(new URL("../package.json", import.meta.url), "utf8");
  assert.match(workspace, /Draw Calculation Area/);
  assert.match(workspace, /Recommend CAP/);
  assert.match(workspace, /disabled title="Phase 6/);
  assert.match(inspector, /Restore source\/default values/);
  assert.match(workspace, /Apply selected fields/);
  assert.match(inspector, /Explicit model selection required/);
  assert.match(inspector, /Catalog default/);
  assert.match(inspector, /Pole override/);
  assert.match(catalogs, /Upload IES/);
  assert.match(catalogs, /New template revision/);
  assert.match(types, /location_edit_authorized/);
  assert.match(api, /Array\.isArray\(detail\)/);
  assert.match(api, /messages\.join\("; "\)/);
  assert.match(packageJson, /maplibre-gl/);
  assert.doesNotMatch(packageJson, /react-loading-skeleton/);
});
