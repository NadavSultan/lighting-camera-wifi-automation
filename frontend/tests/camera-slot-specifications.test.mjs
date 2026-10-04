import test from "node:test";
import assert from "node:assert/strict";
import * as specifications from "../app/lib/camera-slot-specifications.mjs";

const slot = { camera_model_id: "camera", camera_model_revision: 1, lens_id: "lens", lens_revision: 1 };
const oldCamera = { id: "camera", revision: 1, display_name: "Pinned camera", resolution_width_px: 4056, resolution_height_px: 3040 };
const oldLens = { id: "lens", revision: 1, display_name: "Pinned lens", focal_length_mm: 3.9, horizontal_fov_deg: 87, vertical_fov_deg: 62, compatible_camera_model_ids: ["camera"] };
const catalog = { camera_models: [{ ...oldCamera, revision: 2, resolution_width_px: 9999 }], camera_model_history: [oldCamera], lenses: [{ ...oldLens, revision: 2, focal_length_mm: 99 }], lens_history: [oldLens] };

test("historical slot specs retain exact pins instead of current or footprint values", () => {
  assert.equal(typeof specifications.resolveCameraSlotSpecifications, "function");
  const before = structuredClone({ catalog, slot });
  const view = specifications.resolveCameraSlotSpecifications(catalog, slot);
  assert.equal(view.camera.display_name, "Pinned camera");
  assert.equal(view.camera.resolution_width_px, 4056);
  assert.equal(view.camera.resolution_height_px, 3040);
  assert.equal(view.lens.focal_length_mm, 3.9);
  assert.equal(view.lens.horizontal_fov_deg, 87);
  assert.equal(view.lens.vertical_fov_deg, 62);
  assert.deepEqual(view.warnings, []);
  assert.deepEqual({ catalog, slot }, before);
});

test("explicit override IDs require their own pins; unassigned or missing never guesses", () => {
  const resolve = specifications.resolveCameraSlotSpecifications;
  for (const override of [{ lens_id: "lens" }, { lens_id: "lens", lens_revision: 999 }, { lens_id: "" }]) {
    const view = resolve(catalog, slot, override);
    assert.equal(view.lens, null);
    assert.ok(view.warnings.length);
  }
  assert.equal(resolve(catalog, slot, { camera_model_id: "camera" }).camera, null);
  assert.equal(resolve(null, slot).camera, null);
  assert.equal(resolve(catalog, { ...slot, lens_id: null }).lens, null);
  // Existing null overrides mean inherit; null must not accidentally adopt a latest revision.
  assert.equal(resolve(catalog, slot, { lens_id: null, lens_revision: 2 }).lens.revision, 1);
});

test("pinned compatibility and nullable fields remain explicit", () => {
  const missing = structuredClone(catalog);
  missing.lens_history[0].compatible_camera_model_ids = [];
  missing.lens_history[0].focal_length_mm = null;
  const view = specifications.resolveCameraSlotSpecifications(missing, slot);
  assert.equal(view.lens.focal_length_mm, null);
  assert.ok(view.warnings.some((warning) => /incompatible/i.test(warning)));
});
