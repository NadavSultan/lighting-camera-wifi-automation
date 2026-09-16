import test from "node:test";
import assert from "node:assert/strict";
import { capPrimaryAction, CAP_PRIMARY_ACTION_LABEL } from "../app/lib/cap-primary-action.mjs";
import { capOperationEnabled } from "../app/lib/phase6-cap-workflows.mjs";

function eligibleProject(operationMode = "recommend") {
  return {
    cap_planning_inputs: {
      profile: {
        product_mapping: { status: "known" },
        variant: { status: "known" },
        band_and_jurisdiction: { status: "known" },
        link_distance_m: { status: "known" },
        node_limit: { status: "known" },
        child_limit: { status: "known" },
        hop_limit: { status: "known" },
        gateway_appliance_counting: { status: "known" },
        colocated_fixture_counting: { status: "known" },
        redundancy: { status: "known" },
        node_policy: { LITE: "node", WIFI: "node", SMART: "node" },
        mode_permission: "recommend_from_approved_pool",
        operation_mode: operationMode,
      },
      candidates: [{
        prohibited: false,
        mounting_confirmed: true,
        power_confirmed: true,
        backhaul_confirmed: true,
        enclosure_confirmed: true,
        survey_status: "confirmed",
        indoor_outdoor: "outdoor",
      }],
    },
  };
}

test("primary action is recommend with the approved label", () => {
  assert.equal(CAP_PRIMARY_ACTION_LABEL, "Calculate CAP recommendation");
  const action = capPrimaryAction(eligibleProject());
  assert.equal(action.operation, "recommend");
  assert.equal(action.label, "Calculate CAP recommendation");
  assert.equal(action.enabled, true);
  assert.equal(action.enabled, capOperationEnabled(eligibleProject(), "recommend"));
});

test("primary action stays recommend and disabled when blockers exist", () => {
  const blocked = { cap_planning_inputs: { profile: { node_policy: { LITE: "unknown", WIFI: "unknown", SMART: "unknown" }, mode_permission: "unknown", operation_mode: "recommend" }, candidates: [] } };
  const action = capPrimaryAction(blocked);
  assert.equal(action.operation, "recommend");
  assert.equal(action.enabled, false);
  assert.equal(action.enabled, capOperationEnabled(blocked, "recommend"));
});

test("validate-only mode does not fake recommendation availability", () => {
  const project = eligibleProject("validate");
  const action = capPrimaryAction(project);
  assert.equal(action.operation, "recommend");
  assert.equal(action.enabled, false);
  assert.equal(capOperationEnabled(project, "validate"), true);
});

test("null project does not enable recommendation", () => {
  assert.deepEqual(capPrimaryAction(null), {
    operation: "recommend",
    label: "Calculate CAP recommendation",
    enabled: false,
  });
});
