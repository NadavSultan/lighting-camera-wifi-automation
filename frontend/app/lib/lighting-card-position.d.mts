export function clampCard(
  card: { x: number; y: number; width: number; height: number },
  viewport: { width: number; height: number },
  margin?: number,
): { x: number; y: number };

export function ringAnchorLngLat(
  ring: Array<[number, number]> | null | undefined,
): [number, number] | null;

export function cardOffsetFromProjected(
  projected: { x?: number; y?: number } | null | undefined,
  offsetPx?: number,
): { x: number; y: number };
