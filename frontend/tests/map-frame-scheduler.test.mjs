import test from "node:test";
import assert from "node:assert/strict";
import { cancelMapFrame, createMapFrameScheduler } from "../app/lib/map-frame-scheduler.mjs";

function mockFrames() {
  let nextId = 1;
  const pending = new Map();
  return {
    hooks: {
      requestAnimationFrame(cb) {
        const id = nextId++;
        pending.set(id, cb);
        return id;
      },
      cancelAnimationFrame(id) {
        pending.delete(id);
      },
    },
    flush(id) {
      const cb = pending.get(id);
      pending.delete(id);
      if (cb) cb(0);
    },
    pendingCount() {
      return pending.size;
    },
  };
}

test("cancel without clearing the stored id prevents later schedules (WA-02/WA-03 leak)", () => {
  const frames = mockFrames();
  const frameRef = { current: null };
  const draws = [];
  const schedule = createMapFrameScheduler(frameRef, () => draws.push("draw"), frames.hooks);
  schedule();
  const leakedId = frameRef.current;
  frames.hooks.cancelAnimationFrame(leakedId);
  assert.equal(typeof leakedId, "number");
  schedule();
  assert.equal(frames.pendingCount(), 0, "stale id makes schedule a no-op");
  assert.equal(draws.length, 0);
});

test("cancelMapFrame clears the id so a later schedule can draw", () => {
  const frames = mockFrames();
  const frameRef = { current: null };
  const draws = [];
  const schedule = createMapFrameScheduler(frameRef, () => draws.push("draw"), frames.hooks);
  schedule();
  cancelMapFrame(frameRef, frames.hooks);
  assert.equal(frameRef.current, null);
  schedule();
  const id = frameRef.current;
  assert.equal(typeof id, "number");
  frames.flush(id);
  assert.equal(frameRef.current, null);
  assert.deepEqual(draws, ["draw"]);
});

test("schedule coalesces to one frame while a callback is pending", () => {
  const frames = mockFrames();
  const frameRef = { current: null };
  let count = 0;
  const schedule = createMapFrameScheduler(frameRef, () => { count += 1; }, frames.hooks);
  schedule();
  schedule();
  schedule();
  assert.equal(frames.pendingCount(), 1);
  frames.flush(frameRef.current);
  assert.equal(count, 1);
});
