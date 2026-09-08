/**
 * Clamp a floating card rectangle inside a viewport with margin.
 */

/**
 * @param {{x: number, y: number, width: number, height: number}} card
 * @param {{width: number, height: number}} viewport
 * @param {number} [margin=8]
 * @returns {{x: number, y: number}}
 */
export function clampCard(card, viewport, margin = 8) {
  const width = Math.max(0, Number(card?.width) || 0);
  const height = Math.max(0, Number(card?.height) || 0);
  const viewW = Math.max(0, Number(viewport?.width) || 0);
  const viewH = Math.max(0, Number(viewport?.height) || 0);
  const m = Number.isFinite(margin) ? margin : 8;
  const maxX = Math.max(m, viewW - width - m);
  const maxY = Math.max(m, viewH - height - m);
  const x = Math.min(maxX, Math.max(m, Number(card?.x) || 0));
  const y = Math.min(maxY, Math.max(m, Number(card?.y) || 0));
  return { x, y };
}

/**
 * Final non-closing vertex of a closed WGS84 ring, or null.
 * @param {Array<[number, number]> | null | undefined} ring
 * @returns {[number, number] | null}
 */
export function ringAnchorLngLat(ring) {
  if (!Array.isArray(ring) || ring.length < 2) return null;
  const first = ring[0];
  const last = ring[ring.length - 1];
  const closed =
    Array.isArray(first)
    && Array.isArray(last)
    && first.length >= 2
    && last.length >= 2
    && first[0] === last[0]
    && first[1] === last[1]
    && ring.length >= 3;
  const anchor = closed ? ring[ring.length - 2] : last;
  return Array.isArray(anchor) && anchor.length >= 2
    ? /** @type {[number, number]} */ ([anchor[0], anchor[1]])
    : null;
}

/**
 * Convert a MapLibre `map.project()` point into CSS left/top for a card that is
 * `position:absolute` inside `.map-stage`.
 *
 * MapLibre documents `project()` as pixels relative to the map container.
 * `.map-container` fills `.map-stage` (`inset: 0`), so those coordinates are
 * already the card's containing-block coordinates. Subtracting the container's
 * viewport `left`/`top` double-offsets the card whenever the map is not at page
 * origin (0, 0).
 *
 * @param {{x?: number, y?: number} | null | undefined} projected
 * @param {number} [offsetPx=12] small placement offset from the finish vertex
 * @returns {{x: number, y: number}}
 */
export function cardOffsetFromProjected(projected, offsetPx = 12) {
  const x = Number(projected?.x);
  const y = Number(projected?.y);
  const offset = Number.isFinite(offsetPx) ? offsetPx : 12;
  return {
    x: (Number.isFinite(x) ? x : 0) + offset,
    y: (Number.isFinite(y) ? y : 0) + offset,
  };
}
