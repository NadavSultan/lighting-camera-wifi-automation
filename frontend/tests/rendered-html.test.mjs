import assert from "node:assert/strict";
import { readFile } from "node:fs/promises";
import test from "node:test";
import { formatApiErrorDetail, selectBulkPoleIds, uploadIesAndRefresh, withoutCameraOverride } from "../app/lib/phase2-workflows.mjs";
import { closePriorityRing, emptyPriorityRedrawDraft, fixtureAzimuthFromHandle, formatEngineeringAzimuth, normalizeFixtureAzimuth, renamePriorityArea, validateAndClosePriorityRing } from "../app/lib/phase3-workflows.mjs";

async function render() {
  const workerUrl = new URL("../dist/server/index.js", import.meta.url);
  workerUrl.searchParams.set("test", `${process.pid}-${Date.now()}`);
  const { default: worker } = await import(workerUrl.href);
  return worker.fetch(new Request("http://localhost/", { headers: { accept: "text/html" } }), { ASSETS: { fetch: async () => new Response("Not found", { status: 404 }) } }, { waitUntil() {}, passThroughOnException() {} });
}

test("server-renders the Phase 3 engineering workspace", async () => {
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

test("exposes Phase 3 camera geometry while keeping later engines gated", async () => {
  const workspace = await readFile(new URL("../app/components/EngineeringWorkspace.tsx", import.meta.url), "utf8");
  const inspector = await readFile(new URL("../app/components/PoleInspector.tsx", import.meta.url), "utf8");
  const catalogs = await readFile(new URL("../app/components/CatalogManager.tsx", import.meta.url), "utf8");
  const types = await readFile(new URL("../app/lib/types.ts", import.meta.url), "utf8");
  const api = await readFile(new URL("../app/lib/api.ts", import.meta.url), "utf8");
  const packageJson = await readFile(new URL("../package.json", import.meta.url), "utf8");
  assert.match(workspace, /Draw Priority Area/);
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
  assert.match(inspector, /Inherited relative azimuth/);
  assert.match(inspector, /Inherited downward tilt/);
  assert.match(inspector, /Explicitly reset orientation to immutable template/);
  assert.doesNotMatch(inspector, /onChange=\{\(event\) => updateSlot\(slot\.id, \{ relative_azimuth_deg/);
  assert.doesNotMatch(inspector, /onChange=\{\(event\) => updateSlot\(slot\.id, \{ downward_tilt_deg/);
  assert.match(workspace, /Manually selected poles/);
  assert.match(workspace, /Add current pole to bulk selection/);
  assert.match(workspace, /selectBulkPoleIds/);
  assert.match(catalogs, /Upload IES/);
  assert.match(catalogs, /New template revision/);
  assert.match(types, /location_edit_authorized/);
  assert.match(api, /formatApiErrorDetail/);
  assert.match(api, /recalculateCameraGeometry/);
  assert.match(workspace, /camera_overlap/);
  assert.match(workspace, /priority_area_summaries/);
  assert.match(workspace, /startPriorityRename/);
  assert.match(workspace, /startPriorityRedraw/);
  assert.match(workspace, /Replacement geometry starts empty/);
  assert.match(workspace, /cameraWarnings/);
  const map = await readFile(new URL("../app/components/EngineeringMap.tsx", import.meta.url), "utf8");
  assert.match(map, /camera-warning-indicator/);
  assert.match(map, /layer_state\.warnings/);
  assert.match(packageJson, /maplibre-gl/);
  assert.doesNotMatch(packageJson, /react-loading-skeleton/);
});

test("NIR-01 refreshes and reports a rejected retained IES record without raw JSON", async () => {
  const retainedRecord = { id: "ies-bad", validation_status: "unsupported", active: false, validation_errors: ["Unsupported IES format"] };
  const detail = { message: "Unsupported IES format; LM-63-1995 or LM-63-2002 is required", record: retainedRecord };
  assert.equal(formatApiErrorDetail(detail), detail.message);
  assert.doesNotMatch(formatApiErrorDetail(detail), /"record"|"validation_status"/);
  let refreshCount = 0;
  const rejection = new Error(formatApiErrorDetail(detail));
  const result = await uploadIesAndRefresh(async () => { throw rejection; }, async () => { refreshCount += 1; });
  assert.equal(refreshCount, 1);
  assert.equal(result.value, null);
  assert.equal(result.error, rejection);
  const catalog = await readFile(new URL("../app/components/CatalogManager.tsx", import.meta.url), "utf8");
  assert.match(catalog, /setIesId\(""\)/);
  assert.match(catalog, /disabled=\{!file\.active && file\.validation_status !== "valid"\}/);
  assert.match(catalog, /usableIes/);
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

test("Phase 3 fixture rotation and priority-area helpers are deterministic", () => {
  assert.equal(normalizeFixtureAzimuth(-70), 290);
  assert.equal(normalizeFixtureAzimuth(430), 70);
  assert.equal(fixtureAzimuthFromHandle(-80, 25, -80, 25.001), 0);
  assert.ok(Math.abs(fixtureAzimuthFromHandle(-80, 25, -79.999, 25) - 90) < 1e-9);
  const vertices = [[-80, 25], [-79.999, 25], [-79.999, 25.001]];
  assert.deepEqual(closePriorityRing(vertices), [...vertices, vertices[0]]);
  assert.throws(() => closePriorityRing(vertices.slice(0, 2)), /three distinct vertices/);
  assert.deepEqual(emptyPriorityRedrawDraft(), []);
  const area = { id: "a", name: "Old", wgs84_coordinates: closePriorityRing(vertices), modified_at: "before" };
  const renamed = renamePriorityArea(area, "Renamed", "after");
  assert.equal(renamed.name, "Renamed");
  assert.strictEqual(renamed.wgs84_coordinates, area.wgs84_coordinates);
  assert.throws(() => validateAndClosePriorityRing([[0, 0], [1, 1], [0, 1], [1, 0]]), /self-intersecting/);
  assert.throws(() => validateAndClosePriorityRing([[0, 0], [1, 1], [2, 2]]), /degenerate/);
  assert.equal(formatEngineeringAzimuth(51.888999999999996), "51.889");
  assert.equal(formatEngineeringAzimuth(360), "0");
});
