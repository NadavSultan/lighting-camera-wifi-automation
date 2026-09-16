/**
 * Open a collapsed CAP <details> section, then scroll and focus the blocker target.
 * Does not change CAP eligibility or fill inputs.
 */

/**
 * @param {ParentNode & { getElementById: (id: string) => Element | null }} root
 * @param {string} elementId
 * @param {(fn: () => void) => void} [afterOpen]
 * @returns {boolean}
 */
export function openAndFocusCapReviewTarget(root, elementId, afterOpen = scheduleAfterDetailsOpen) {
  const element = root.getElementById(elementId);
  if (!element || typeof element.focus !== "function") return false;
  const details = typeof element.closest === "function" ? element.closest("details") : null;
  const wasClosed = Boolean(details) && details.open !== true;
  if (wasClosed) details.open = true;
  const applyFocus = () => {
    const current = root.getElementById(elementId) ?? element;
    if (typeof current.scrollIntoView === "function") {
      current.scrollIntoView({ behavior: "smooth", block: "center" });
    }
    current.focus();
  };
  if (wasClosed) afterOpen(applyFocus);
  else applyFocus();
  return true;
}

/**
 * @param {() => void} fn
 */
export function scheduleAfterDetailsOpen(fn) {
  if (typeof requestAnimationFrame === "function") {
    requestAnimationFrame(() => requestAnimationFrame(fn));
    return;
  }
  setTimeout(fn, 0);
}
