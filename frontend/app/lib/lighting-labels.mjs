/**
 * Formatting helpers for maintained-illuminance map labels.
 */

/**
 * @param {unknown} value maintained lux
 * @returns {string}
 */
export function formatLux(value) {
  if (typeof value !== "number" || !Number.isFinite(value) || value < 0) return "—";
  if (value === 0 || value >= 0.01) return value.toFixed(2);
  return value.toPrecision(2);
}

/**
 * Flatten lighting calculation results into label-ready points.
 * @param {Record<string, {calculation_area_id?: string, points?: Array<{id: string, wgs84_coordinate: [number, number], maintained_horizontal_illuminance_lux: number}>}> | null | undefined} results
 */
export function lightingLabelPoints(results) {
  if (!results || typeof results !== "object") return [];
  const points = [];
  for (const result of Object.values(results)) {
    if (!result || !Array.isArray(result.points)) continue;
    for (const point of result.points) {
      if (!point || !Array.isArray(point.wgs84_coordinate) || point.wgs84_coordinate.length < 2) continue;
      points.push({
        id: `${result.calculation_area_id ?? "area"}:${point.id}`,
        coordinate: [point.wgs84_coordinate[0], point.wgs84_coordinate[1]],
        lux: point.maintained_horizontal_illuminance_lux,
        label: formatLux(point.maintained_horizontal_illuminance_lux),
      });
    }
  }
  return points;
}
