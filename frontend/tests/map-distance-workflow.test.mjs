import test from "node:test";
import assert from "node:assert/strict";
import * as workflow from "../app/lib/map-distance-workflow.mjs";

test("two clicks measure once; completed/clear/Esc state has no persistence", async () => {
  assert.equal(typeof workflow.createMeasurementController, "function");
  const calls = [];
  const controller = workflow.createMeasurementController(async (...args) => {
    calls.push(args); return { projected_crs: "EPSG:32617", distance_m: 50 };
  }, () => {});
  controller.setContext("project", "EPSG:32617");
  controller.start(false);
  assert.equal(controller.getState().status, "idle");
  controller.start(true);
  assert.equal(workflow.measurementBlocksMapInteractions(controller.getState()), true);
  await controller.click([-80, 25]);
  assert.equal(controller.getState().status, "second-point");
  await controller.click([-80.001, 25]);
  assert.equal(controller.getState().status, "complete");
  assert.equal(controller.getState().distanceM, 50);
  assert.equal(workflow.measurementBlocksMapInteractions(controller.getState()), false);
  await controller.click([-81, 26]);
  assert.equal(calls.length, 1);
  assert.equal(calls[0][0], "EPSG:32617");
  assert.deepEqual(calls[0][1], [-80, 25]);
  assert.deepEqual(calls[0][2], [-80.001, 25]);
  assert.ok(calls[0][3].signal);
  controller.cancel();
  assert.equal(controller.getState().status, "complete");
  controller.clear();
  assert.equal(controller.getState().status, "first-point");
  assert.equal(workflow.measurementFeatures(controller.getState()).features.length, 0);
  await controller.click([-80, 25]);
  controller.cancel();
  assert.equal(controller.getState().status, "idle");
});

for (const action of ["clear", "cancel", "replace-project", "change-crs"]) {
  test(`late response after ${action} cannot restore old measurement`, async () => {
    let finish, signal;
    const controller = workflow.createMeasurementController((...args) => {
      signal = args[3].signal;
      return new Promise((resolve) => { finish = resolve; });
    }, () => {});
    controller.setContext("p1", "EPSG:32617");
    controller.start(true);
    await controller.click([-80, 25]);
    const pending = controller.click([-80, 25.001]);
    assert.equal(controller.getState().status, "pending");
    await controller.click([-80, 26]);
    if (action === "replace-project") controller.setContext("p2", "EPSG:32617");
    else if (action === "change-crs") controller.setContext("p1", "EPSG:32618");
    else controller[action]();
    assert.equal(signal.aborted, true);
    finish({ distance_m: 50, projected_crs: "EPSG:32617" });
    await pending;
    assert.equal(controller.getState().distanceM, null);
    assert.equal(workflow.measurementFeatures(controller.getState()).features.length, 0);
  });
}

test("invalid click/request results show errors without a invented numeric value", async () => {
  for (const outcome of [new Error("Distance failed"), { distance_m: NaN }, { distance_m: -1 }]) {
    const controller = workflow.createMeasurementController(async () => {
      if (outcome instanceof Error) throw outcome;
      return outcome;
    }, () => {});
    controller.setContext("p1", "EPSG:32617"); controller.start(true);
    await controller.click([-80, 25]); await controller.click([-80, 25.001]);
    assert.equal(controller.getState().status, "error");
    assert.equal(controller.getState().distanceM, null);
    assert.ok(controller.getState().error);
    assert.equal(workflow.measurementFeatures(controller.getState()).features.length, 0);
  }
  const controller = workflow.createMeasurementController(async () => { throw new Error("should not request"); }, () => {});
  controller.setContext("p1", "EPSG:32617"); controller.start(true);
  await controller.click([Infinity, 25]);
  assert.equal(controller.getState().status, "error");
});

test("zero-length measurement is valid and yields labelled endpoints/line", async () => {
  const controller = workflow.createMeasurementController(async () => ({ distance_m: 0 }), () => {});
  controller.setContext("p", "EPSG:32617"); controller.start(true);
  await controller.click([-80, 25]); await controller.click([-80, 25]);
  assert.equal(controller.getState().distanceM, 0);
  const features = workflow.measurementFeatures(controller.getState());
  assert.equal(features.features.filter((f) => f.geometry.type === "LineString").length, 1);
  assert.ok(features.features.some((f) => f.properties.label === "0.00 m"));
});

test("shared interaction guard blocks all ordinary map callbacks while measuring or drawing", () => {
  for (const status of ["first-point", "second-point", "pending", "error"]) {
    assert.equal(workflow.mapInteractionBlocked({ status }, false), true);
  }
  for (const drawing of [true, false]) {
    assert.equal(workflow.mapInteractionBlocked({ status: "idle" }, drawing), drawing);
    assert.equal(workflow.mapInteractionBlocked({ status: "complete" }, drawing), drawing);
  }
});
