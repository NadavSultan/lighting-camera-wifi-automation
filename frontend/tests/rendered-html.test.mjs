import assert from "node:assert/strict";
import { readFile } from "node:fs/promises";
import test from "node:test";
import { formatApiErrorDetail, selectBulkPoleIds, uploadIesAndRefresh, withoutCameraOverride } from "../app/lib/phase2-workflows.mjs";
import { closePriorityRing, emptyPriorityRedrawDraft, fixtureAzimuthFromHandle, formatEngineeringAzimuth, normalizeFixtureAzimuth, renamePriorityArea, roundNormalizedFixtureAzimuth, validateAndClosePriorityRing } from "../app/lib/phase3-workflows.mjs";
import { invalidateLightingResults, lightingSignificantPoleChange, MIN_GRID_SPACING_M, staleCalculationState, validateCalculationAreaDraft } from "../app/lib/phase4-workflows.mjs";
import { applyWifiFields, closeWifiArea, invalidateWifiIfSignificant, wifiBoundaryGapMessage, wifiEffectiveValues, wifiSignificantProjectChange } from "../app/lib/phase5-workflows.mjs";
import { CAP_DISCLAIMER, capBlockers, capOperationEnabled, capSignificantProjectChange, invalidateCapIfSignificant, isCapResultStale } from "../app/lib/phase6-cap-workflows.mjs";

async function render() {
  const workerUrl = new URL("../dist/server/index.js", import.meta.url);
  workerUrl.searchParams.set("test", `${process.pid}-${Date.now()}`);
  const { default: worker } = await import(workerUrl.href);
  return worker.fetch(new Request("http://localhost/", { headers: { accept: "text/html" } }), { ASSETS: { fetch: async () => new Response("Not found", { status: 404 }) } }, { waitUntil() {}, passThroughOnException() {} });
}

test("server-renders the Phase 5 engineering workspace", async () => {
  const response = await render();
  assert.equal(response.status, 200);
  const html = await response.text();
  assert.match(html, /<title>Lighting Camera WiFi Automation<\/title>/i);
  assert.match(html, /LCWA Studio/);
  assert.match(html, /Existing-pole mode/);
  assert.match(html, /Import KML\/KMZ/);
  assert.match(html, /Catalogs/);
  assert.match(html, /Customer coordinates are locked/);
  assert.match(html, /Phase 5/);
  assert.match(html, /Conceptual geometric visualization only/);
  assert.doesNotMatch(html, /codex-preview|Your site is taking shape|react-loading-skeleton/i);
});

test("exposes conceptual Wi-Fi and the Phase 6 CAP graph workflow", async () => {
  const workspace = await readFile(new URL("../app/components/EngineeringWorkspace.tsx", import.meta.url), "utf8");
  const inspector = await readFile(new URL("../app/components/PoleInspector.tsx", import.meta.url), "utf8");
  const catalogs = await readFile(new URL("../app/components/CatalogManager.tsx", import.meta.url), "utf8");
  const types = await readFile(new URL("../app/lib/types.ts", import.meta.url), "utf8");
  const api = await readFile(new URL("../app/lib/api.ts", import.meta.url), "utf8");
  const packageJson = await readFile(new URL("../package.json", import.meta.url), "utf8");
  assert.match(workspace, /Draw Priority Area/);
  assert.match(workspace, /Draw Calculation Area/);
  assert.match(workspace, /calculateSelectedArea/);
  assert.match(workspace, /Approved simplified direct-light model/);
  assert.match(workspace, /Calculation and fixture provenance/);
  assert.match(workspace, /ies_sha256/);
  assert.match(workspace, /Not independently validated/);
  assert.match(workspace, /Conceptual Wi-Fi.*phase: 5/);
  assert.match(workspace, /Draw Wi-Fi analysis area/);
  assert.match(workspace, /Calculate conceptual Wi-Fi/);
  assert.match(workspace, /Clear radius to project default/);
  assert.match(workspace, /wifiBoundaryGapMessage/);
  assert.match(workspace, /Phase 6 — CAP \/ JNET1 graph planning/);
  assert.match(workspace, /CAP_DISCLAIMER/);
  assert.match(workspace, /Recommend CAP/);
  assert.match(workspace, /CAP candidate \/ selected sites/);
  assert.match(workspace, /Add distinct manual non-pole CAP site/);
  assert.match(workspace, /Manual non-pole site; never a customer lighting pole/);
  assert.match(workspace, /Mark test-only feasible/);
  assert.match(workspace, /Lock selected/);
  assert.match(workspace, /CAP topology, score trace, and provenance/);
  assert.match(workspace, /distance-qualified conceptual link; not RF-predicted/);
  assert.match(inspector, /Restore source\/default values/);
  assert.match(workspace, /Apply selected fields/);
  assert.match(inspector, /Explicit model selection required/);
  assert.match(inspector, /Explicitly enabled/);
  assert.match(inspector, /Explicitly disabled/);
  assert.match(inspector, /Clear to project default/);
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
  assert.match(api, /calculateLighting/);
  assert.match(workspace, /camera_overlap/);
  assert.match(workspace, /priority_area_summaries/);
  assert.match(workspace, /startPriorityRename/);
  assert.match(workspace, /startPriorityRedraw/);
  assert.match(workspace, /Replacement geometry starts empty/);
  assert.match(workspace, /cameraWarnings/);
  const map = await readFile(new URL("../app/components/EngineeringMap.tsx", import.meta.url), "utf8");
  assert.match(map, /camera-warning-indicator/);
  assert.match(map, /layer_state\.warnings/);
  assert.match(map, /calculation-area-fill/);
  assert.match(map, /lighting-calculation-points/);
  assert.match(map, /lighting-heat-points/);
  assert.match(map, /cap-candidate-sites/);
  assert.match(map, /cap-manual-candidate-sites/);
  assert.match(map, /#34d399/);
  assert.match(map, /Manual non-pole CAP site/);
  assert.match(packageJson, /maplibre-gl/);
  assert.doesNotMatch(packageJson, /react-loading-skeleton/);
});

test("Phase 5 workflow helpers preserve safe drafts, inheritance, and precise invalidation", () => {
  const base = { projected_crs: "EPSG:32617", defaults: { fixture_type: "LITE", wifi_radius_m: 30 }, source: { poles: [{ id: "p1", sequence_index: 0, longitude: -80, latitude: 25 }] }, pole_edits: { p1: { fixture_type: "WIFI", active: true, fixture_configuration: { fixture_model_id: "wifi", fixture_model_revision: 1, wifi_configuration: { radius_override_m: null, enabled: null, notes: "" } } } }, wifi_analysis_areas: [] , wifi_coverage: { result: { old: true }, state: { status: "calculated" } } };
  assert.deepEqual(closeWifiArea([[0, 0], [1, 0], [1, 1]]), [[0, 0], [1, 0], [1, 1], [0, 0]]);
  assert.throws(() => closeWifiArea([[0, 0], [1, 1]]), /three distinct vertices/);
  assert.deepEqual(wifiEffectiveValues(base, "p1"), { radius_m: 30, enabled: true, enabled_override: null, radius_override_m: null });
  const notes = structuredClone(base); notes.pole_edits.p1.fixture_configuration.wifi_configuration.notes = "field note";
  assert.equal(wifiSignificantProjectChange(base, notes), false);
  assert.equal(invalidateWifiIfSignificant(base, notes).wifi_coverage.result.old, true);
  const changed = structuredClone(base); changed.defaults.wifi_radius_m = 31;
  assert.equal(wifiSignificantProjectChange(base, changed), true);
  assert.equal(invalidateWifiIfSignificant(base, changed).wifi_coverage.result, null);
});

test("Phase 6 CAP helper keeps unknowns blocker-first and does not compare unrelated digests", () => {
  const unknown = { profile: { node_policy: { LITE: "unknown", WIFI: "unknown", SMART: "unknown" }, mode_permission: "unknown" }, candidates: [] };
  assert.ok(capBlockers(unknown).includes("product_mapping"));
  const ready = { profile: { operation_mode: "recommend", mode_permission: "recommend_from_approved_pool", node_policy: { LITE: "node", WIFI: "non_node", SMART: "non_node" }, ...Object.fromEntries(["product_mapping", "variant", "band_and_jurisdiction", "link_distance_m", "node_limit", "child_limit", "hop_limit", "gateway_appliance_counting", "colocated_fixture_counting", "redundancy"].map((key) => [key, { status: "known", conflict_state: "none" }])) }, candidates: [{ prohibited: false, mounting_confirmed: true, power_confirmed: true, backhaul_confirmed: true, enclosure_confirmed: true, survey_status: "confirmed", indoor_outdoor: "outdoor" }] };
  assert.equal(capOperationEnabled({ cap_planning_inputs: ready }, "recommend"), true);
  assert.equal(isCapResultStale({ cap_calculations: { status: "calculated", calculation_input_sha256: "input", result: { result_sha256: "result" } } }), false);
  assert.equal(isCapResultStale({ cap_calculations: { status: "not-calculated", calculation_input_sha256: null, result: { result_sha256: "result" } } }), true);
  assert.match(CAP_DISCLAIMER, /not RF-predicted/);
  assert.equal(capOperationEnabled({ cap_planning_inputs: ready }, "validate"), false);
  ready.profile.operation_mode = "validate";
  assert.equal(capOperationEnabled({ cap_planning_inputs: ready }, "validate"), true);
});

test("Phase 6 CAP invalidation clears results for graph inputs but not presentation notes", () => {
  const base = { projected_crs: "EPSG:32617", defaults: { fixture_type: "LITE" }, source: { poles: [{ id: "p1", sequence_index: 0, longitude: -80, latitude: 25 }] }, pole_edits: {}, cap_planning_inputs: { profile: { product_mapping: { status: "known" }, node_policy: {} }, candidates: [{ id: "cap-1", notes: "note", priority: 1 }], excluded_node_ids: [], excluded_candidate_ids: [], locked_selected_candidate_ids: [], primary_assignment_locks: {}, parent_locks: {} }, cap_calculations: { status: "calculated", calculation_input_sha256: "x", calculated_at: "now", result: { result_sha256: "y" }, warnings: [] }, cap_recommendations: { selected_candidate_ids: ["cap-1"], result_sha256: "y" } };
  const note = structuredClone(base); note.cap_planning_inputs.candidates[0].notes = "new note";
  assert.equal(capSignificantProjectChange(base, note), false);
  assert.equal(invalidateCapIfSignificant(base, note).cap_calculations.status, "calculated");
  const changed = structuredClone(base); changed.pole_edits.p1 = { active: false };
  assert.equal(capSignificantProjectChange(base, changed), true);
  assert.equal(invalidateCapIfSignificant(base, changed).cap_calculations.result, null);
});

test("Phase 5 Wi-Fi drafts reject every invalid ring and preserve both winding directions", () => {
  const invalid = [
    [[0, 0], [1, 0], [0, 0], [0, 1]],
    [[0, 0], [2, 2], [0, 2], [2, 0]],
    [[0, 0], [1, 0], [1, 1], [1, 0], [0, 1]],
    [[0, 0], [2, 0], [1, 0], [1, 1]],
    [[0, 0], [1, 0], [2, 0]],
    [[0, 0], [1, Number.NaN], [0, 1]],
    [[0, 0], [181, 0], [0, 1]],
  ];
  for (const ring of invalid) assert.throws(() => closeWifiArea(ring));
  const ccw = [[0, 0], [1, 0], [1, 1]];
  const cw = [...ccw].reverse();
  assert.equal(closeWifiArea(ccw).length, 4);
  assert.equal(closeWifiArea(cw).length, 4);
  const boundary = Array.from({ length: 10000 }, (_, index) => [Math.cos(index * 2 * Math.PI / 10000), Math.sin(index * 2 * Math.PI / 10000)]);
  assert.equal(closeWifiArea(boundary).length, 10001);
  assert.throws(() => closeWifiArea(Array.from({ length: 10001 }, (_, index) => [index / 100000, index % 2])) , /10,000/);
});

test("Phase 5 Wi-Fi bulk fields revise once only and ignore unchanged fields", () => {
  const base = { radius_override_m: null, enabled: null, notes: "", configuration_revision: 4, modified_at: "before" };
  assert.equal(applyWifiFields(base, { notes: "note" }, "after").configuration_revision, 5);
  assert.equal(applyWifiFields(base, { radius_override_m: 40 }, "after").configuration_revision, 5);
  assert.equal(applyWifiFields(base, { enabled: true }, "after").configuration_revision, 5);
  assert.equal(applyWifiFields(base, { notes: "note", radius_override_m: 40, enabled: true }, "after").configuration_revision, 5);
  assert.equal(applyWifiFields({ ...base, radius_override_m: 40, enabled: true }, { radius_override_m: null, enabled: null }, "after").configuration_revision, 5);
  assert.strictEqual(applyWifiFields(base, { notes: "", radius_override_m: null, enabled: null }, "after"), base);
});

test("QA-01 keeps the exact no-area boundary message in the post-calculation result branch", async () => {
  assert.equal(wifiBoundaryGapMessage({ analysis_area_statistics: [] }), "Boundary/gap statistics unavailable — draw a Wi-Fi analysis area.");
  assert.equal(wifiBoundaryGapMessage({ analysis_area_statistics: [{ analysis_area_id: "a" }] }), null);
  const workspace = await readFile(new URL("../app/components/EngineeringWorkspace.tsx", import.meta.url), "utf8");
  assert.match(workspace, /project\.wifi_coverage\.result\) && <p className="helper">\{wifiBoundaryGapMessage\(project\.wifi_coverage\.result\)\}<\/p>/);
  assert.match(workspace, /No result yet\. Circles and global metrics are available after calculation\.<\/p><p className="helper">\{wifiBoundaryGapMessage\(null\)\}/);
});

test("Phase 4 calculation-area validation and stale-state transitions are explicit", () => {
  const vertices = [[-80, 25], [-79.999, 25], [-79.999, 25.001]];
  const valid = validateCalculationAreaDraft(vertices, { name: " Road A ", classification: "ROAD", calculation_plane_elevation_m: "0", grid_spacing_m: "2", maintenance_factor: "1" });
  assert.equal(valid.name, "Road A");
  assert.equal(valid.grid_spacing_m, 2);
  assert.deepEqual(valid.wgs84_coordinates, [...vertices, vertices[0]]);
  assert.throws(() => validateCalculationAreaDraft(vertices, { name: "A", classification: "ROAD", calculation_plane_elevation_m: 0, grid_spacing_m: 0, maintenance_factor: 1 }), /at least 0.01 m/);
  assert.equal(validateCalculationAreaDraft(vertices, { name: "A", classification: "ROAD", calculation_plane_elevation_m: 0, grid_spacing_m: MIN_GRID_SPACING_M, maintenance_factor: 1 }).grid_spacing_m, MIN_GRID_SPACING_M);
  assert.throws(() => validateCalculationAreaDraft(vertices, { name: "A", classification: "ROAD", calculation_plane_elevation_m: 0, grid_spacing_m: 2, maintenance_factor: 1.1 }), /no greater than 1/);
  assert.equal(staleCalculationState({ polygon_revision: 4 }, false).polygon_revision, 4);
  assert.equal(staleCalculationState({ polygon_revision: 4 }, true).polygon_revision, 5);
});

test("P4-IR-01 immediately invalidates lighting results only for significant pole edits", async () => {
  const base = { pole_id: "p1", height_m: 10, active: true, engineering_notes: "before", fixture_type: "LITE", fixture_configuration: { fixture_model_id: "phoenix-1-lite", fixture_model_revision: 1, mounting_template_revision: null, ies_file_id: "ies-1", ies_file_revision: 1, fixture_azimuth_deg: 0, lighting_properties: {}, wifi_configuration: null, camera_overrides: {} } };
  assert.equal(lightingSignificantPoleChange(base, { ...base, engineering_notes: "after" }), false);
  for (const changed of [
    { ...base, height_m: 12 },
    { ...base, active: false },
    { ...base, fixture_type: "SMART" },
    { ...base, fixture_configuration: { ...base.fixture_configuration, fixture_model_id: "solitaire-lite" } },
    { ...base, fixture_configuration: { ...base.fixture_configuration, ies_file_id: "ies-2", ies_file_revision: 2 } },
    { ...base, fixture_configuration: { ...base.fixture_configuration, fixture_azimuth_deg: 90 } },
    undefined,
  ]) assert.equal(lightingSignificantPoleChange(base, changed), true);
  const project = { lighting_calculations: { results: { area: { stale: true } } }, calculation_areas: [{ id: "area", calculation_state: { status: "calculated", polygon_revision: 3, last_calculated_at: "before", warnings: ["old"], assumptions: ["old"], provenance: { old: true } } }] };
  invalidateLightingResults(project);
  assert.deepEqual(project.lighting_calculations.results, {});
  assert.equal(project.calculation_areas[0].calculation_state.status, "not-calculated");
  assert.equal(project.calculation_areas[0].calculation_state.polygon_revision, 3);
  const workspace = await readFile(new URL("../app/components/EngineeringWorkspace.tsx", import.meta.url), "utf8");
  assert.match(workspace, /lightingSignificantPoleChange\(existing, updated\)/);
  assert.match(workspace, /lightingSignificantPoleChange\(existing, undefined\)/);
  assert.match(workspace, /lightingInputsChanged \|\|= lightingSignificantPoleChange\(current, updated\)/);
  assert.match(workspace, /if \(lightingInputsChanged\) invalidateLightingResults\(draft\)/);
});

test("P4-IR-07 lighting-area validation never uses priority-area wording", () => {
  const settings = { name: "Lighting", classification: "ROAD", calculation_plane_elevation_m: 0, grid_spacing_m: 2, maintenance_factor: 1 };
  const cases = [
    [[[0, 0], [1, 0]], /three distinct vertices/],
    [[[0, 0], [0, 0], [1, 1]], /three distinct vertices/],
    [[[0, 0], [1, 1], [0, 1], [1, 0]], /self-intersecting/],
    [[[0, 0], [1, 1], [2, 2]], /degenerate/],
    [[[0, 0], [1, Number.NaN], [2, 1]], /finite numbers/],
    [[[0, 0], [181, 0], [1, 1]], /WGS84 bounds/],
  ];
  for (const [points, expected] of cases) {
    let message = "";
    try { validateCalculationAreaDraft(points, settings); } catch (caught) { message = caught.message; }
    assert.match(message, expected);
    assert.doesNotMatch(message, /priority area|priority-area/i);
    assert.match(message, /lighting calculation area/i);
  }
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

test("P3-IR-05 keeps rounded display and map-handle azimuths in the normalized range", async () => {
  const cases = [
    [359.9999, "0", 0],
    [-0.0001, "0", 0],
    [360, "0", 0],
    [720, "0", 0],
    [721.23456, "1.235", 1.235],
    [-1, "359", 359],
    [51.888999999999996, "51.889", 51.889],
  ];
  for (const [input, expected, expectedNumber] of cases) {
    assert.equal(formatEngineeringAzimuth(input), expected);
    const rounded = roundNormalizedFixtureAzimuth(input);
    assert.equal(rounded, expectedNumber);
    assert.ok(rounded >= 0 && rounded < 360, `${input} rounded outside [0, 360): ${rounded}`);
  }
  const eastOfNorth = fixtureAzimuthFromHandle(-80, 25, -80 + 1e-12, 25.001);
  const westOfNorth = fixtureAzimuthFromHandle(-80, 25, -80 - 1e-12, 25.001);
  assert.equal(eastOfNorth, 0);
  assert.equal(westOfNorth, 0);
  assert.ok(eastOfNorth >= 0 && eastOfNorth < 360);
  assert.ok(westOfNorth >= 0 && westOfNorth < 360);
  const workspace = await readFile(new URL("../app/components/EngineeringWorkspace.tsx", import.meta.url), "utf8");
  assert.match(workspace, /fixture_azimuth_deg: roundNormalizedFixtureAzimuth\(azimuth\)/);
  assert.doesNotMatch(workspace, /fixture_azimuth_deg: Number\(azimuth\.toFixed\(3\)\)/);
});
