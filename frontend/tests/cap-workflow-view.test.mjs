import test from "node:test";
import assert from "node:assert/strict";
import { blockerFocusTarget, blockerLabel, capResultSummary } from "../app/lib/cap-workflow-view.mjs";

test("initial project without calculation is not-calculated", () => {
  assert.deepEqual(capResultSummary({
    cap_calculations: { status: "not-calculated", result: null },
    cap_recommendations: { selected_candidate_ids: [], result_sha256: null },
  }), { state: "not-calculated", selectedIds: [], unresolvedIds: [] });
});

test("successful current result uses selected recommendation IDs", () => {
  const project = {
    cap_calculations: {
      status: "calculated",
      calculation_input_sha256: "input-a",
      result: {
        result_sha256: "result-a",
        selected_candidate_ids: ["pool-a", "pool-b"],
        unresolved_node_ids: [],
      },
    },
    cap_recommendations: { selected_candidate_ids: ["site-a"], result_sha256: "result-a" },
  };
  assert.deepEqual(capResultSummary(project), {
    state: "current",
    selectedIds: ["site-a"],
    unresolvedIds: [],
  });
});

test("unresolved nodes mark current-with-unresolved", () => {
  const project = {
    cap_calculations: {
      status: "calculated",
      calculation_input_sha256: "input-a",
      result: {
        result_sha256: "result-a",
        selected_candidate_ids: ["site-a"],
        unresolved_node_ids: ["fixture/p1"],
      },
    },
    cap_recommendations: { selected_candidate_ids: ["site-a"], result_sha256: "result-a" },
  };
  assert.deepEqual(capResultSummary(project), {
    state: "current-with-unresolved",
    selectedIds: ["site-a"],
    unresolvedIds: ["fixture/p1"],
  });
});

test("error status is distinct from not-calculated", () => {
  assert.deepEqual(capResultSummary({
    cap_calculations: { status: "error", result: null },
    cap_recommendations: { selected_candidate_ids: ["stale"], result_sha256: null },
  }), { state: "error", selectedIds: [], unresolvedIds: [] });
});

test("invalidated result does not keep prior count labeled current", () => {
  const stale = {
    cap_calculations: { status: "not-calculated", result: null },
    cap_recommendations: { selected_candidate_ids: [], result_sha256: null },
  };
  assert.deepEqual(capResultSummary(stale), {
    state: "not-calculated",
    selectedIds: [],
    unresolvedIds: [],
  });
});

test("blocker labels and focus targets are readable", () => {
  assert.equal(blockerLabel("link_distance_m"), "Link distance");
  assert.equal(blockerFocusTarget("feasible_candidate"), "cap-section-candidates");
  assert.match(blockerLabel("totally_unknown_key"), /Unknown prerequisite/);
});
