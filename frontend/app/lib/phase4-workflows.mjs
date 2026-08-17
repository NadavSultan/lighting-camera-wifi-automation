import { validateAndClosePriorityRing } from "./phase3-workflows.mjs";

export const MIN_GRID_SPACING_M = 0.01;

function validateAndCloseCalculationRing(points) {
  try {
    return validateAndClosePriorityRing(points);
  } catch (caught) {
    const message = caught instanceof Error ? caught.message : "Lighting calculation area is invalid.";
    const replacements = new Map([
      ["A priority area requires at least three distinct vertices.", "A lighting calculation area requires at least three distinct vertices."],
      ["Priority-area coordinates must be finite numbers.", "Lighting calculation area coordinates must be finite numbers."],
      ["A priority-area coordinate is outside WGS84 bounds.", "A lighting calculation area coordinate is outside WGS84 bounds."],
      ["The replacement priority area is self-intersecting.", "The lighting calculation area is self-intersecting."],
      ["The replacement priority area is degenerate and has no usable area.", "The lighting calculation area is degenerate and has no usable area."],
    ]);
    throw new Error(replacements.get(message) ?? `Lighting calculation area is invalid: ${message}`);
  }
}

export function lightingSignificantPoleEdit(edit) {
  const config = edit?.fixture_configuration;
  return {
    active: edit?.active ?? null,
    fixture_type: edit?.fixture_type ?? null,
    height_m: edit?.height_m ?? null,
    fixture_configuration: config ? {
      fixture_model_id: config.fixture_model_id,
      fixture_model_revision: config.fixture_model_revision,
      mounting_template_revision: config.mounting_template_revision,
      ies_file_id: config.ies_file_id,
      ies_file_revision: config.ies_file_revision,
      fixture_azimuth_deg: config.fixture_azimuth_deg,
      lighting_properties: config.lighting_properties,
    } : null,
  };
}

export function lightingSignificantPoleChange(before, after) {
  return JSON.stringify(lightingSignificantPoleEdit(before)) !== JSON.stringify(lightingSignificantPoleEdit(after));
}

export function invalidateLightingResults(project) {
  project.lighting_calculations.results = {};
  for (const area of project.calculation_areas) area.calculation_state = staleCalculationState(area.calculation_state, false);
}

export function validateCalculationAreaDraft(points, settings) {
  const name = String(settings.name ?? "").trim();
  if (!name) throw new Error("Calculation-area name is required");
  if (!["ROAD", "SIDEWALK", "PARKING", "OTHER"].includes(settings.classification)) throw new Error("A valid lighting classification is required");
  const elevation = Number(settings.calculation_plane_elevation_m);
  const spacing = Number(settings.grid_spacing_m);
  const factor = Number(settings.maintenance_factor);
  if (!Number.isFinite(elevation) || elevation < -1000 || elevation > 10000) throw new Error("Calculation-plane elevation must be finite and between -1000 m and 10000 m");
  if (!Number.isFinite(spacing) || spacing < MIN_GRID_SPACING_M || spacing > 1000) throw new Error(`Grid spacing must be finite, at least ${MIN_GRID_SPACING_M} m, and no greater than 1000 m`);
  if (!Number.isFinite(factor) || factor <= 0 || factor > 1) throw new Error("Maintenance factor must be greater than 0 and no greater than 1");
  return { name, classification: settings.classification, calculation_plane_elevation_m: elevation, grid_spacing_m: spacing, maintenance_factor: factor, wgs84_coordinates: validateAndCloseCalculationRing(points) };
}

export function staleCalculationState(previous, redraw) {
  return { status: "not-calculated", polygon_revision: previous.polygon_revision + (redraw ? 1 : 0), last_calculated_at: null, warnings: [], assumptions: [], provenance: {} };
}
