import test from "node:test";
import assert from "node:assert/strict";
import {
  lightingAreaResultState,
  lightingAreaShowResultsEnabled,
} from "../app/lib/lighting-area-result-state.mjs";

const area = (status) => ({ calculation_state: { status } });
const result = { calculation_area_id: "area-a", statistics: { point_count: 12 } };

test("missing stored result is not-calculated", () => {
  assert.equal(lightingAreaResultState(area("not-calculated"), null), "not-calculated");
  assert.equal(lightingAreaResultState(area("calculated"), undefined), "not-calculated");
  assert.equal(lightingAreaShowResultsEnabled("not-calculated"), false);
});

test("stored result with calculated or warning status is current", () => {
  assert.equal(lightingAreaResultState(area("calculated"), result), "current");
  assert.equal(lightingAreaResultState(area("warning"), result), "current");
  assert.equal(lightingAreaShowResultsEnabled("current"), true);
});

test("stored result without a current area status is stale", () => {
  assert.equal(lightingAreaResultState(area("not-calculated"), result), "stale");
  assert.equal(lightingAreaResultState(area("error"), result), "stale");
  assert.equal(lightingAreaShowResultsEnabled("stale"), false);
});

test("helper does not treat a missing result as current even if status is calculated", () => {
  assert.equal(lightingAreaResultState(area("calculated"), null), "not-calculated");
});
