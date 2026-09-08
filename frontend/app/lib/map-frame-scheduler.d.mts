export type FrameRef = { current: number | null };

export type FrameHooks = {
  requestAnimationFrame: (cb: FrameRequestCallback) => number;
  cancelAnimationFrame: (id: number) => void;
};

export function createMapFrameScheduler(
  frameRef: FrameRef,
  draw: () => void,
  hooks?: FrameHooks,
): () => void;

export function cancelMapFrame(frameRef: FrameRef, hooks?: FrameHooks): void;
