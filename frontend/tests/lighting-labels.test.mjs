import test from "node:test";
import assert from "node:assert/strict";
import { readFile } from "node:fs/promises";
import { formatLux, formatLuxWithUnit, lightingLabelPoints } from "../app/lib/lighting-labels.mjs";

test("formatLux matches required numeric cases", () => {
  assert.equal(formatLux(0), "0.00");
  assert.equal(formatLux(12.345), "12.35");
  assert.equal(formatLux(0.01), "0.01");
  assert.equal(formatLux(0.00123), "<0.01");
  assert.equal(formatLux(0.0000359329), "<0.01");
  assert.equal(formatLux(null), "—");
  assert.equal(formatLux(Number.NaN), "—");
});

test("formatLuxWithUnit distinguishes zero, tiny positives, and unavailable", () => {
  assert.equal(formatLuxWithUnit(0), "0.00 lx");
  assert.equal(formatLuxWithUnit(0.0000359329), "<0.01 lx");
  assert.equal(formatLuxWithUnit(13.0629), "13.06 lx");
  assert.equal(formatLuxWithUnit(null), "—");
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
  assert.equal(points[0].longitude, -80.26);
  assert.equal(points[0].latitude, 25.75);
});

test("tiny positive lux labels keep stored values and use the threshold policy", () => {
  const points = lightingLabelPoints({
    a1: {
      calculation_area_id: "a1",
      points: [{ id: "p1", wgs84_coordinate: [-80.26, 25.75], maintained_horizontal_illuminance_lux: 0.0000359 }],
    },
  });
  assert.equal(points[0].label, "<0.01");
  assert.equal(points[0].lux, 0.0000359);
});

test("card and left-panel summaries format lux through formatLuxWithUnit and keep stored ratios", async () => {
  const card = await readFile(new URL("../app/components/LightingResultCard.tsx", import.meta.url), "utf8");
  const workspace = await readFile(new URL("../app/components/EngineeringWorkspace.tsx", import.meta.url), "utf8");
  assert.match(card, /formatLuxWithUnit\(stats\?\.average_illuminance_lux\)/);
  assert.match(card, /formatRatio\(stats\?\.emin_over_eavg\)/);
  assert.doesNotMatch(card, /average_illuminance_lux\)\}\s*lx/);
  assert.match(workspace, /formatLuxWithUnit\(stats\.average_illuminance_lux\)/);
  assert.match(workspace, /emin_over_eavg\?\.toFixed\(3\)/);
  assert.doesNotMatch(workspace, /average_illuminance_lux\?\.toFixed\(2\)/);
});

test("map lux labels sit in a compositor layer above the MapLibre canvas", async () => {
  const css = await readFile(new URL("../app/globals.css", import.meta.url), "utf8");
  assert.match(css, /\.lighting-point-labels\s*\{[^}]*z-index:\s*2/);
  assert.match(css, /\.lighting-point-labels\s*\{[^}]*translateZ\(0\)/);
});

test("EngineeringMap draws helper label points for current lighting results", async () => {
  const source = await readFile(new URL("../app/components/EngineeringMap.tsx", import.meta.url), "utf8");
  assert.match(source, /lightingLabelPoints\(project\?\.lighting_calculations\.results\)/);
  assert.match(source, /layer_state\.calculation_points \?\? true/);
  assert.doesNotMatch(source, /function lightingLabelPoints\(project/);
});
