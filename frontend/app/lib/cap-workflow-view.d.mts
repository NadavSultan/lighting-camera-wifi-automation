export type CapResultPresentationState =
  | "not-calculated"
  | "current"
  | "current-with-unresolved"
  | "error";

export type CapResultSummary = {
  state: CapResultPresentationState;
  selectedIds: string[];
  unresolvedIds: string[];
};

export function capResultSummary(project: unknown): CapResultSummary;

export function blockerLabel(key: string): string;

export function blockerFocusTarget(key: string): string | null;

export function candidateDisplayLabel(project: unknown, candidateId: string): string;
