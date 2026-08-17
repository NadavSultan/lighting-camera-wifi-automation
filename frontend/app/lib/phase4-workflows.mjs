import { validateAndClosePriorityRing } from "./phase3-workflows.mjs";

export function validateCalculationAreaDraft(points, settings) {
  const name = String(settings.name ?? "").trim();
  if (!name) throw new Error("Calculation-area name is required");
  if (!["ROAD", "SIDEWALK", "PARKING", "OTHER"].includes(settings.classification)) throw new Error("A valid lighting classification is required");
  const elevation = Number(settings.calculation_plane_elevation_m);
  const spacing = Number(settings.grid_spacing_m);
  const factor = Number(settings.maintenance_factor);
  if (!Number.isFinite(elevation) || elevation < -1000 || elevation > 10000) throw new Error("Calculation-plane elevation must be finite and between -1000 m and 10000 m");
  if (!Number.isFinite(spacing) || spacing <= 0 || spacing > 1000) throw new Error("Grid spacing must be finite, positive, and no greater than 1000 m");
  if (!Number.isFinite(factor) || factor <= 0 || factor > 1) throw new Error("Maintenance factor must be greater than 0 and no greater than 1");
  return { name, classification: settings.classification, calculation_plane_elevation_m: elevation, grid_spacing_m: spacing, maintenance_factor: factor, wgs84_coordinates: validateAndClosePriorityRing(points) };
}

export function staleCalculationState(previous, redraw) {
  return { status: "not-calculated", polygon_revision: previous.polygon_revision + (redraw ? 1 : 0), last_calculated_at: null, warnings: [], assumptions: [], provenance: {} };
}

