/**
 * Presentation state for one lighting calculation-area row.
 * Does not modify Project data or recreate invalidated results.
 *
 * @param {{ calculation_state?: { status?: string } } | null | undefined} area
 * @param {object | null | undefined} result stored lighting_calculations.results[area.id]
 * @returns {"current" | "stale" | "not-calculated"}
 */
export function lightingAreaResultState(area, result) {
  if (result == null) return "not-calculated";
  const status = area?.calculation_state?.status;
  if (status === "calculated" || status === "warning") return "current";
  return "stale";
}

/**
 * @param {"current" | "stale" | "not-calculated"} state
 */
export function lightingAreaShowResultsEnabled(state) {
  return state === "current";
}
