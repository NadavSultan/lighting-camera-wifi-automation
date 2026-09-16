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

export function resolveLightingCardSession(
  sessions: Record<string, { anchorLngLat?: [number, number] | null; draggedPosition?: { x: number; y: number } | null }> | null | undefined,
  areaId: string,
  fallbackAnchor: [number, number] | null,
): { anchorLngLat: [number, number] | null; draggedPosition: { x: number; y: number } | null };
