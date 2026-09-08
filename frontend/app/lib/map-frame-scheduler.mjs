/**
 * Schedule overlay draws once per animation frame.
 * Cancel must clear the stored id so a later schedule can run.
 */

/**
 * @typedef {{ current: number | null }} FrameRef
 * @typedef {{ requestAnimationFrame: (cb: FrameRequestCallback) => number, cancelAnimationFrame: (id: number) => void }} FrameHooks
 */

/**
 * @param {FrameRef} frameRef
 * @param {() => void} draw
 * @param {FrameHooks} [hooks]
 * @returns {() => void}
 */
export function createMapFrameScheduler(frameRef, draw, hooks = globalThis) {
  return () => {
    if (frameRef.current != null) return;
    frameRef.current = hooks.requestAnimationFrame(() => {
      frameRef.current = null;
      draw();
    });
  };
}

/**
 * @param {FrameRef} frameRef
 * @param {FrameHooks} [hooks]
 */
export function cancelMapFrame(frameRef, hooks = globalThis) {
  if (frameRef.current == null) return;
  hooks.cancelAnimationFrame(frameRef.current);
  frameRef.current = null;
}
