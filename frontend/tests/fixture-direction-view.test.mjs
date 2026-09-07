import test from "node:test";
import assert from "node:assert/strict";
import { directionSignificantKey, screenArrow } from "../app/lib/fixture-direction-view.mjs";

test("screenArrow normalizes cardinal pixel vectors", () => {
  assert.deepEqual(screenArrow({ x: 10, y: 20 }, { x: 10, y: 19 }), { dx: 0, dy: -24 });
  assert.deepEqual(screenArrow({ x: 10, y: 20 }, { x: 11, y: 20 }), { dx: 24, dy: 0 });
  assert.equal(screenArrow({ x: 10, y: 20 }, { x: 10, y: 20 }), null);
});

test("screenArrow rejects nonfinite and non-positive length", () => {
  assert.equal(screenArrow({ x: Number.NaN, y: 0 }, { x: 1, y: 0 }), null);
  assert.equal(screenArrow({ x: 0, y: 0 }, { x: 1, y: 0 }, 0), null);
});

test("directionSignificantKey ignores pan-only fields and reacts to azimuth", () => {
  const project = {
    id: "p1",
    projected_crs: "EPSG:32617",
    source: { poles: [{ id: "a", longitude: -80, latitude: 25 }] },
    pole_edits: {
      a: {
        active: true,
        fixture_configuration: {
          fixture_model_id: "phoenix-1-lite",
          fixture_model_revision: 1,
          fixture_azimuth_deg: 0,
        },
      },
    },
  };
  const first = directionSignificantKey(project);
  const panOnly = structuredClone(project);
  panOnly.name = "ignored";
  assert.equal(directionSignificantKey(panOnly), first);
  const rotated = structuredClone(project);
  rotated.pole_edits.a.fixture_configuration.fixture_azimuth_deg = 90;
  assert.notEqual(directionSignificantKey(rotated), first);
});
