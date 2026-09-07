import test from "node:test";
import assert from "node:assert/strict";
import { wifiMapState } from "../app/lib/wifi-map-state.mjs";

test("null result is not-calculated even when visibility flag is true", () => {
  assert.equal(wifiMapState(null, true), "not-calculated");
});

test("zero circles is empty", () => {
  assert.equal(wifiMapState({ global_statistics: { circle_count: 0 } }, false), "empty");
});

test("one circle with layer off is hidden", () => {
  assert.equal(wifiMapState({ global_statistics: { circle_count: 1 } }, false), "hidden");
});

test("one circle with layer on is visible", () => {
  assert.equal(wifiMapState({ global_statistics: { circle_count: 1 } }, true), "visible");
});
