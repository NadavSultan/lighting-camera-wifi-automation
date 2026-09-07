import test from "node:test";
import assert from "node:assert/strict";
import { formatLux, lightingLabelPoints } from "../app/lib/lighting-labels.mjs";

test("formatLux matches required numeric cases", () => {
  assert.equal(formatLux(0), "0.00");
  assert.equal(formatLux(12.345), "12.35");
  assert.equal(formatLux(0.00123), "0.0012");
  assert.equal(formatLux(null), "—");
  assert.equal(formatLux(Number.NaN), "—");
});

test("lightingLabelPoints composites area and point ids", () => {
  const points = lightingLabelPoints({
    a1: {
      calculation_area_id: "a1",
      points: [{ id: "p1", wgs84_coordinate: [-80.26, 25.75], maintained_horizontal_illuminance_lux: 10 }],
    },
  });
  assert.equal(points.length, 1);
  assert.equal(points[0].id, "a1:p1");
  assert.equal(points[0].label, "10.00");
});
