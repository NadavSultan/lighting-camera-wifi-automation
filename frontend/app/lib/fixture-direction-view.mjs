/**
 * Screen-space helpers for fixture-direction arrows.
 * Metre-CRS geometry is handled by the backend preview; this module only normalizes display pixels.
 */

/**
 * @param {{x: number, y: number}} origin
 * @param {{x: number, y: number}} endpoint
 * @param {number} [length=24]
 * @returns {{dx: number, dy: number} | null}
 */
export function screenArrow(origin, endpoint, length = 24) {
  if (!origin || !endpoint) return null;
  const values = [origin.x, origin.y, endpoint.x, endpoint.y, length];
  if (!values.every((value) => typeof value === "number" && Number.isFinite(value))) return null;
  if (!(length > 0)) return null;
  const dx = endpoint.x - origin.x;
  const dy = endpoint.y - origin.y;
  const mag = Math.hypot(dx, dy);
  if (!(mag > 0)) return null;
  return { dx: (dx / mag) * length, dy: (dy / mag) * length };
}

/**
 * Stable key of direction-significant project inputs for sequenced preview refresh.
 * @param {{
 *   id?: string,
 *   projected_crs?: string | null,
 *   source?: { poles?: Array<{ id: string, longitude: number, latitude: number }> },
 *   pole_edits?: Record<string, {
 *     active?: boolean | null,
 *     fixture_configuration?: {
 *       fixture_model_id?: string,
 *       fixture_model_revision?: number,
 *       fixture_azimuth_deg?: number,
 *     } | null,
 *   }>,
 * } | null | undefined} project
 * @returns {string}
 */
export function directionSignificantKey(project) {
  if (!project) return "";
  const poles = project.source?.poles ?? [];
  const edits = project.pole_edits ?? {};
  const parts = [project.id ?? "", project.projected_crs ?? ""];
  for (const pole of poles) {
    const edit = edits[pole.id];
    const config = edit?.fixture_configuration;
    parts.push(
      [
        pole.id,
        pole.longitude,
        pole.latitude,
        edit?.active === false ? "0" : "1",
        config?.fixture_model_id ?? "",
        config?.fixture_model_revision ?? "",
        config?.fixture_azimuth_deg ?? "",
      ].join(":"),
    );
  }
  return parts.join("|");
}
