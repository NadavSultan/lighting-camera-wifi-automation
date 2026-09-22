import test from "node:test";
import assert from "node:assert/strict";
import { cameraPixelDensityView, invalidateCameraPixelDensityIfSignificant } from "../app/lib/camera-pixel-density-view.mjs";

function project() {
  return {
    projected_crs: "EPSG:32617",
    defaults: { pole_height_m: 10 },
    source: { poles: [{ id: "p1", sequence_index: 0, longitude: -80, latitude: 25 }] },
    pole_edits: { p1: { height_m: 10, engineering_notes: "note", active: true, fixture_type: "SMART", fixture_configuration: { fixture_model_id: "smart", fixture_model_revision: 1, mounting_template_revision: 1, fixture_azimuth_deg: 0, camera_overrides: { "camera-1": { slot_id: "camera-1", camera_model_id: "camera", camera_model_revision: 1, lens_id: "lens", lens_revision: 1, enabled: true } } } } },
    camera_pixel_density_profile: { lower_projection_height_m: 0.5, upper_projection_height_m: 2, measurement_height_mode: "midpoint", maximum_visible_distance_m: 50, legend_id: "face-density-0.16m-v1" },
    camera_pixel_density: { state: { status: "current", calculation_input_sha256: "a".repeat(64), message: null }, result: { calculation_input_sha256: "a".repeat(64) } },
    layer_state: { camera_pixel_density: true },
  };
}

test("camera density view distinguishes current, hidden, stale, and invalid results", () => {
  assert.deepEqual(cameraPixelDensityView(null), { status: "not-calculated", canCalculate: false, layerAvailable: false, message: "No camera pixel-density result" });
  const current = project();
  assert.equal(cameraPixelDensityView(current).status, "current");
  assert.equal(cameraPixelDensityView(current).layerAvailable, true);
  current.layer_state.camera_pixel_density = false;
  assert.equal(cameraPixelDensityView(current).layerAvailable, true);
  current.camera_pixel_density.state.status = "stale";
  assert.equal(cameraPixelDensityView(current).message, "Stale — recalculate required");
  current.camera_pixel_density.state.status = "current";
  current.camera_pixel_density.result = null;
  assert.equal(cameraPixelDensityView(current).status, "not-calculated");
});

test("local invalidation retains results and ignores presentation-only edits", () => {
  const base = project();
  const notes = structuredClone(base); notes.pole_edits.p1.engineering_notes = "changed";
  assert.equal(invalidateCameraPixelDensityIfSignificant(base, notes).camera_pixel_density.state.status, "current");
  const layers = structuredClone(base); layers.layer_state.camera_pixel_density = false;
  assert.equal(invalidateCameraPixelDensityIfSignificant(base, layers).camera_pixel_density.state.status, "current");
  for (const mutate of [
    (value) => { value.camera_pixel_density_profile.maximum_visible_distance_m = 60; },
    (value) => { value.pole_edits.p1.height_m = 11; },
    (value) => { value.pole_edits.p1.fixture_configuration.fixture_azimuth_deg = 90; },
    (value) => { value.pole_edits.p1.fixture_configuration.camera_overrides["camera-1"].lens_revision = 2; },
    (value) => { value.pole_edits.p1.fixture_configuration.camera_overrides["camera-1"].enabled = false; },
  ]) {
    const changed = structuredClone(base); mutate(changed);
    const stale = invalidateCameraPixelDensityIfSignificant(base, changed);
    assert.equal(stale.camera_pixel_density.state.status, "stale");
    assert.equal(stale.camera_pixel_density.state.message, "Stale — recalculate required");
    assert.equal(stale.camera_pixel_density.result.calculation_input_sha256, "a".repeat(64));
    assert.equal(stale.layer_state.camera_pixel_density, false);
  }
});
