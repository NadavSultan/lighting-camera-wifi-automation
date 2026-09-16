export function openAndFocusCapReviewTarget(
  root: { getElementById(id: string): { focus(): void; closest?(selector: string): { open?: boolean } | null; scrollIntoView?(options?: object): void } | null },
  elementId: string,
  afterOpen?: (fn: () => void) => void,
): boolean;

export function scheduleAfterDetailsOpen(fn: () => void): void;
