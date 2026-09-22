import test from "node:test";
import assert from "node:assert/strict";
import { densityBandFeatures, densityOverlapFeatures, densityOverlapLabelPoints, densityInspectionAt, densityLayerDefinitions } from "../app/lib/camera-pixel-density-map.mjs";

function project(status = "current", visible = true) {
  const ring = [[-80,25],[-79.9,25],[-79.9,25.1],[-80,25.1],[-80,25]];
  return { layer_state: { camera_pixel_density: visible }, camera_pixel_density: { state: { status, calculation_input_sha256: "a" }, result: { calculation_input_sha256: "a", camera_results: [{ footprint_id: "pole<script>/camera&1", bands: [{ band_id: "px-face-30", rank: 8, minimum_px_per_face: 30, maximum_px_per_face: 45, colour_token: "face-density-30", wgs84_rings: [[ring, [[-79.98,25.02],[-79.97,25.02],[-79.97,25.03],[-79.98,25.03],[-79.98,25.02]]]] }] }], overlap_regions: [{ overlap_region_id: "o1", camera_footprint_ids: ["pole<script>/camera&1", "pole-b/\u202ecamera"], multiplicity: 2, winning_camera_footprint_id: "pole<script>/camera&1", winning_band_id: "px-face-30", winning_band_rank: 8, wgs84_rings: [[ring]] }] } } };
}

test("density GeoJSON requires a matching current visible result and preserves holes", () => {
  assert.equal(densityBandFeatures(project("stale")).features.length, 0);
  assert.equal(densityBandFeatures(project("current", false)).features.length, 0);
  const feature = densityBandFeatures(project()).features[0];
  assert.equal(feature.geometry.type, "Polygon");
  assert.equal(feature.geometry.coordinates.length, 2);
  assert.equal(feature.properties.rank, 8);
  assert.equal(densityOverlapFeatures(project()).features[0].properties.multiplicity, 2);
  assert.equal(densityOverlapLabelPoints(project())[0].label, "2×");
});

test("inspection uses stored winner and sorted contributors without HTML", () => {
  const malicious = project().camera_pixel_density.result.overlap_regions[0];
  const inspected = densityInspectionAt([{ properties: malicious }]);
  assert.deepEqual(inspected.contributors, [...malicious.camera_footprint_ids].sort());
  assert.equal(inspected.winner, malicious.winning_camera_footprint_id);
  assert.equal("html" in inspected, false);
});

test("ten layer definitions are ascending and use canonical colour and opacity", () => {
  const legend = { fill_opacity: 0.58, thresholds: Array.from({ length: 10 }, (_, index) => ({ colour: `#00000${index}`, token: `face-density-${index}` })) };
  const layers = densityLayerDefinitions(legend);
  assert.deepEqual(layers.map((layer) => layer.rank), [1,2,3,4,5,6,7,8,9,10]);
  assert.ok(layers.every((layer) => layer.opacity === 0.58));
  assert.equal(layers[9].colour, "#000009");
});
