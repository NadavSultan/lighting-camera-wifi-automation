import test from "node:test";
import assert from "node:assert/strict";
import * as densityMap from "../app/lib/camera-pixel-density-map.mjs";
import { densityBandFeatures, densityOverlapFeatures, densityOverlapLabelPoints, densityInspectionAt, densityLayerDefinitions, densityHeatmapTileTemplate } from "../app/lib/camera-pixel-density-map.mjs";

test("heatmap refresh discards the old raster cache and stale results have no raster source", () => {
  assert.equal(typeof densityMap.replaceDensityHeatmapSource, "function");
  const sources = new Map([["camera-density-heatmap", { staleTexture: true }]]);
  const layers = new Map([["camera-density-heatmap", {}]]);
  const removed = [];
  let beforeLayer;
  const map = {
    getSource: id => sources.get(id), getLayer: id => layers.get(id),
    removeLayer(id) { layers.delete(id); removed.push("layer"); },
    removeSource(id) { assert.equal(layers.has(id), false); sources.delete(id); removed.push("source"); },
    addSource(id, source) { sources.set(id, source); },
    addLayer(layer, before) { layers.set(layer.id, layer); beforeLayer = before; },
  };
  densityMap.replaceDensityHeatmapSource(map, "new-fingerprint/{z}/{x}/{y}.png");
  assert.deepEqual(removed, ["layer", "source"]);
  assert.deepEqual(sources.get("camera-density-heatmap").tiles, ["new-fingerprint/{z}/{x}/{y}.png"]);
  assert.equal(sources.get("camera-density-heatmap").staleTexture, undefined);
  assert.equal(beforeLayer, "camera-density-band-1");
  assert.equal(layers.get("camera-density-heatmap").paint["raster-resampling"], "linear");
  assert.equal(layers.get("camera-density-heatmap").paint["raster-opacity"], 1);
  densityMap.replaceDensityHeatmapSource(map, "");
  assert.equal(sources.size, 0); assert.equal(layers.size, 0);
  densityMap.replaceDensityHeatmapSource(map, "");
  assert.equal(sources.size, 0);
});

function project(status = "current", visible = true) {
  const ring = [[-80,25],[-79.9,25],[-79.9,25.1],[-80,25.1],[-80,25]];
  return { layer_state: { camera_pixel_density: visible }, camera_pixel_density: { state: { status, calculation_input_sha256: "a" }, result: { calculation_input_sha256: "a", camera_results: [{ footprint_id: "pole<script>/camera&1", bands: [{ band_id: "px-face-30", rank: 8, minimum_px_per_face: 30, maximum_px_per_face: 45, colour_token: "face-density-30", wgs84_rings: [[ring, [[-79.98,25.02],[-79.97,25.02],[-79.97,25.03],[-79.98,25.03],[-79.98,25.02]]]] }] }], overlap_regions: [{ overlap_region_id: "o1", camera_footprint_ids: ["pole<script>/camera&1", "pole-b/\u202ecamera"], multiplicity: 2, winning_camera_footprint_id: "pole<script>/camera&1", winning_band_id: "px-face-30", winning_band_rank: 8, wgs84_rings: [[ring]] }] } } };
}

test("bounded preview preserves envelopes including holes below density thresholds", () => {
  assert.equal(typeof densityMap.densityPreviewFeatures, "function");
  const current = project();
  const camera = current.camera_pixel_density.result.camera_results[0];
  const rings = camera.bands[0].wgs84_rings;
  camera.valid = true; camera.enabled = true;
  camera.projection_envelope = { wgs84_rings: rings };
  camera.bands = [];
  const before = structuredClone(current);
  const preview = densityMap.densityPreviewFeatures(current);
  assert.equal(preview.features.length, 1);
  assert.deepEqual(preview.features[0].geometry.coordinates, rings[0]);
  assert.equal(preview.features[0].geometry.coordinates.length, 2);
  assert.deepEqual(current, before);
  for (const status of ["stale", "invalid", "not-calculated"]) {
    current.camera_pixel_density.state.status = status;
    assert.equal(densityMap.densityPreviewFeatures(current).features.length, 0);
  }
  current.camera_pixel_density.state.status = "current";
  current.layer_state.camera_pixel_density = false;
  assert.equal(densityMap.densityPreviewFeatures(current).features.length, 0);
  current.layer_state.camera_pixel_density = true;
  current.camera_pixel_density.state.calculation_input_sha256 = "mismatch";
  assert.equal(densityMap.densityPreviewFeatures(current).features.length, 0);
  current.camera_pixel_density.state.calculation_input_sha256 = "a";
  camera.valid = false;
  assert.equal(densityMap.densityPreviewFeatures(current).features.length, 0);
  camera.valid = true; camera.enabled = false;
  assert.equal(densityMap.densityPreviewFeatures(current).features.length, 0);
});

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

test("heatmap tile source only loads a visible, matching current calculation", () => {
  const current = project();
  current.id = "project/a";
  assert.equal(densityHeatmapTileTemplate(current, "http://127.0.0.1:8070"),
    "http://127.0.0.1:8070/api/projects/project%2Fa/camera-pixel-density/heatmap/{z}/{x}/{y}.png?fingerprint=a");
  assert.equal(densityHeatmapTileTemplate(project("stale"), "http://127.0.0.1:8070"), null);
  assert.equal(densityHeatmapTileTemplate(project("current", false), "http://127.0.0.1:8070"), null);
  current.camera_pixel_density.state.calculation_input_sha256 = "different";
  assert.equal(densityHeatmapTileTemplate(current, "http://127.0.0.1:8070"), null);
});

test("inspection uses stored winner and sorted contributors without HTML", () => {
  const malicious = project().camera_pixel_density.result.overlap_regions[0];
  const inspected = densityInspectionAt([{ properties: malicious }]);
  assert.deepEqual(inspected.contributors, [...malicious.camera_footprint_ids].sort());
  assert.equal(inspected.winner, malicious.winning_camera_footprint_id);
  assert.equal("html" in inspected, false);
});

test("overlap features carry the stored winning camera's displayed px/face interval", () => {
  const overlap = densityOverlapFeatures(project()).features[0];
  assert.equal(overlap.properties.minimum_px_per_face, 30);
  assert.equal(overlap.properties.maximum_px_per_face, 45);
});

test("layered band hits select the overlap winner, complete contributors, and displayed range", () => {
  const current = project();
  const overlap = densityOverlapFeatures(current).features[0];
  const band = densityBandFeatures(current).features[0];
  const inspected = densityInspectionAt([band, overlap, band]);
  assert.deepEqual(inspected, {
    contributors: ["pole-b/\u202ecamera", "pole<script>/camera&1"].sort(),
    winner: "pole<script>/camera&1",
    winningBandId: "px-face-30",
    multiplicity: 2,
    minimumPxPerFace: 30,
    maximumPxPerFace: 45,
  });
});

test("MapLibre-serialized overlap contributors still outrank a single band hit", () => {
  const current = project();
  const overlap = densityOverlapFeatures(current).features[0];
  const band = densityBandFeatures(current).features[0];
  const serialized = { properties: { ...overlap.properties, camera_footprint_ids: JSON.stringify(overlap.properties.camera_footprint_ids) } };
  const inspected = densityInspectionAt([band, serialized]);
  assert.equal(inspected.multiplicity, 2);
  assert.deepEqual(inspected.contributors, ["pole-b/\u202ecamera", "pole<script>/camera&1"].sort());
  assert.equal(inspected.winner, "pole<script>/camera&1");
});

test("one map click over multiple density bands dispatches exactly one complete inspection", () => {
  assert.equal(typeof densityMap.attachDensityInspection, "function", "the map must use one click dispatcher");
  const current = project();
  const overlap = densityOverlapFeatures(current).features[0];
  const band = densityBandFeatures(current).features[0];
  const handlers = [];
  const shown = [];
  const map = {
    on(type, handler) { if (type === "click") handlers.push(handler); },
    queryRenderedFeatures(_point, { layers }) {
      return layers.includes("camera-density-overlap-hit") ? [band, overlap, band] : [band, band];
    },
  };
  densityMap.attachDensityInspection(map, (inspection) => shown.push(inspection), () => false);
  for (const handler of handlers) handler({ point: { x: 20, y: 30 }, lngLat: { lng: -80, lat: 25 } });
  assert.equal(handlers.length, 1);
  assert.equal(shown.length, 1);
  assert.equal(shown[0].multiplicity, 2);
  assert.equal(shown[0].contributors.length, 2);
  assert.equal(shown[0].minimumPxPerFace, 30);
});

test("dense overlap popup remains legible and scrollable inside the map", () => {
  assert.deepEqual(densityMap.densityInspectionStyle(), {
    color: "#17212c",
    maxHeight: "min(180px, calc(100vh - 160px))",
    overflowY: "auto",
    overflowWrap: "anywhere",
    width: "min(320px, calc(100vw - 88px))",
  });
});

test("ten layer definitions are ascending and use canonical colour and opacity", () => {
  const legend = { fill_opacity: 0.58, thresholds: Array.from({ length: 10 }, (_, index) => ({ colour: `#00000${index}`, token: `face-density-${index}` })) };
  const layers = densityLayerDefinitions(legend);
  assert.deepEqual(layers.map((layer) => layer.rank), [1,2,3,4,5,6,7,8,9,10]);
  assert.ok(layers.every((layer) => layer.opacity === 0.58));
  assert.equal(layers[9].colour, "#000009");
});
