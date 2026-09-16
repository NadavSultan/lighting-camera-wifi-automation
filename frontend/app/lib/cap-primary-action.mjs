import { capOperationEnabled } from "./phase6-cap-workflows.mjs";

export const CAP_PRIMARY_ACTION_LABEL = "Calculate CAP recommendation";

/**
 * @param {object | null | undefined} project
 * @returns {{ operation: "recommend", label: string, enabled: boolean }}
 */
export function capPrimaryAction(project) {
  return {
    operation: "recommend",
    label: CAP_PRIMARY_ACTION_LABEL,
    enabled: capOperationEnabled(project, "recommend"),
  };
}
