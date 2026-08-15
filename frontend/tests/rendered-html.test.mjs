import assert from "node:assert/strict";
import { readFile } from "node:fs/promises";
import test from "node:test";
import { selectBulkPoleIds, withoutCameraOverride } from "../app/lib/phase2-workflows.mjs";

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
  assert.match(inspector, /Remove pole override and restore catalog default/);
  assert.match(inspector, /camera_model_revision/);
  assert.match(inspector, /lens_revision/);
  assert.match(workspace, /Manually selected poles/);
  assert.match(workspace, /Add current pole to bulk selection/);
  assert.match(workspace, /selectBulkPoleIds/);
  assert.match(catalogs, /Upload IES/);
  assert.match(catalogs, /New template revision/);
  assert.match(types, /location_edit_authorized/);
  assert.match(api, /Array\.isArray\(detail\)/);
  assert.match(api, /messages\.join\("; "\)/);
  assert.match(packageJson, /maplibre-gl/);
  assert.doesNotMatch(packageJson, /react-loading-skeleton/);
});

test("manual bulk targets and slot reset implement the Phase 2 corrective workflows", () => {
  const poles = [
    { id: "p1", folder_path: ["North"] },
    { id: "p2", folder_path: ["South"] },
    { id: "p3", folder_path: ["North"] },
  ];
  assert.deepEqual(selectBulkPoleIds(poles, "manual", "", ["p1", "p3"]), ["p1", "p3"]);
  assert.deepEqual(selectBulkPoleIds(poles, "folder", "North", []), ["p1", "p3"]);
  assert.deepEqual(selectBulkPoleIds(poles, "all", "", []), ["p1", "p2", "p3"]);
  const original = { "camera-1": { slot_id: "camera-1", lens_id: "lens-a" }, "camera-2": { slot_id: "camera-2", enabled: false } };
  assert.deepEqual(withoutCameraOverride(original, "camera-1"), { "camera-2": original["camera-2"] });
  assert.ok("camera-1" in original, "reset must not mutate the caller's prior project state");
});
