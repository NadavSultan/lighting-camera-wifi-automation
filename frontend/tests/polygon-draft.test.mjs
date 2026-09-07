import test from "node:test";
import assert from "node:assert/strict";
import { buildPolygonDraft, polygonDraftGuidance } from "../app/lib/polygon-draft.mjs";

test("one placed point is visible without inventing a saved edge", () => {
  const input = [[-80.26, 25.75]];
  const draft = buildPolygonDraft(input, [-80.259, 25.751]);
  assert.equal(draft.vertices.features.length, 1);
  assert.equal(draft.edges.features.length, 0);
  assert.equal(draft.fill.features.length, 0);
  assert.equal(draft.preview.features.length, 1);
  assert.deepEqual(input, [[-80.26, 25.75]]);
});

test("zero points yields empty collections and no preview", () => {
  const input = [];
  const draft = buildPolygonDraft(input, [-80.26, 25.75]);
  assert.equal(draft.vertices.features.length, 0);
  assert.equal(draft.edges.features.length, 0);
  assert.equal(draft.fill.features.length, 0);
  assert.equal(draft.preview.features.length, 0);
  assert.deepEqual(input, []);
});

test("two points create an open edge without fill", () => {
  const input = [[-80.26, 25.75], [-80.25, 25.76]];
  const draft = buildPolygonDraft(input, [-80.24, 25.77]);
  assert.equal(draft.vertices.features.length, 2);
  assert.equal(draft.edges.features.length, 1);
  assert.equal(draft.edges.features[0].geometry.type, "LineString");
  assert.equal(draft.edges.features[0].geometry.coordinates.length, 2);
  assert.equal(draft.fill.features.length, 0);
  assert.equal(draft.preview.features.length, 1);
  assert.deepEqual(input, [[-80.26, 25.75], [-80.25, 25.76]]);
});

test("three points create fill and mark the last vertex", () => {
  const input = [[-80.26, 25.75], [-80.25, 25.76], [-80.24, 25.74]];
  const draft = buildPolygonDraft(input, null);
  assert.equal(draft.vertices.features.length, 3);
  assert.equal(draft.vertices.features[2].properties.last, true);
  assert.equal(draft.edges.features.length, 1);
  assert.equal(draft.fill.features.length, 1);
  assert.equal(draft.fill.features[0].geometry.type, "Polygon");
  assert.equal(draft.preview.features.length, 0);
  assert.deepEqual(input, [[-80.26, 25.75], [-80.25, 25.76], [-80.24, 25.74]]);
});

test("duplicate cursor on last point suppresses preview", () => {
  const input = [[-80.26, 25.75]];
  const draft = buildPolygonDraft(input, [-80.26, 25.75]);
  assert.equal(draft.preview.features.length, 0);
});

test("cancel clears preview by omitting cursor", () => {
  const draft = buildPolygonDraft([[-80.26, 25.75], [-80.25, 25.76]], undefined);
  assert.equal(draft.preview.features.length, 0);
});

test("guidance copy advances with vertex count", () => {
  assert.equal(polygonDraftGuidance(0), "Click to add the first point");
  assert.equal(polygonDraftGuidance(1), "Click to add the next point");
  assert.equal(polygonDraftGuidance(2), "Click to add the next point");
  assert.equal(polygonDraftGuidance(3), "Add another point or finish polygon");
});
