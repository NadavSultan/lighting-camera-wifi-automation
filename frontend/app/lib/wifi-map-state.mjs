/**
 * Presentation state for conceptual Wi-Fi coverage on the map.
 * Does not recreate or invalidate results; only classifies current data + visibility.
 */

/**
 * @param {{ global_statistics?: { circle_count?: number } } | null | undefined} result
 * @param {boolean} visible
 * @returns {"not-calculated" | "empty" | "hidden" | "visible"}
 */
export function wifiMapState(result, visible) {
  if (result == null) return "not-calculated";
  const count = result.global_statistics?.circle_count;
  const circleCount = typeof count === "number" && Number.isFinite(count) ? count : 0;
  if (circleCount <= 0) return "empty";
  return visible ? "visible" : "hidden";
}
