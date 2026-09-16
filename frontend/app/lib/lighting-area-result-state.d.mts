export function lightingAreaResultState(
  area: { calculation_state?: { status?: string } } | null | undefined,
  result: object | null | undefined,
): "current" | "stale" | "not-calculated";

export function lightingAreaShowResultsEnabled(
  state: "current" | "stale" | "not-calculated",
): boolean;
