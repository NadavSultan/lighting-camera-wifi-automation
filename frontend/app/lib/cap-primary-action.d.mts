export const CAP_PRIMARY_ACTION_LABEL: "Calculate CAP recommendation";

export function capPrimaryAction(
  project: object | null | undefined,
): { operation: "recommend"; label: string; enabled: boolean };
