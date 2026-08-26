export const WIFI_DISCLAIMER = "Conceptual geometric visualization only; not verified RF coverage, performance, capacity, service quality, or standards compliance.";

function wifiPoleInputs(poleEdit) {
  const config = poleEdit?.fixture_configuration;
  const wifi = config?.wifi_configuration;
  return {
    fixture_type: poleEdit?.fixture_type ?? null,
    active: poleEdit?.active ?? true,
    longitude: poleEdit?.longitude ?? null,
    latitude: poleEdit?.latitude ?? null,
    fixture_model_id: config?.fixture_model_id ?? null,
    fixture_model_revision: config?.fixture_model_revision ?? null,
    radius_override_m: wifi?.radius_override_m ?? null,
    enabled: wifi?.enabled ?? null,
  };
}

export function wifiSignificantProjectChange(previous, next) {
  if ((previous?.projected_crs ?? null) !== (next?.projected_crs ?? null)) return true;
  if ((previous?.defaults?.wifi_radius_m ?? null) !== (next?.defaults?.wifi_radius_m ?? null)) return true;
  if ((previous?.defaults?.fixture_type ?? null) !== (next?.defaults?.fixture_type ?? null)) return true;
  const sourceInputs = (project) => (project?.source?.poles ?? []).map((pole) => ({ id: pole.id, sequence_index: pole.sequence_index, longitude: pole.longitude, latitude: pole.latitude }));
  if (JSON.stringify(sourceInputs(previous)) !== JSON.stringify(sourceInputs(next))) return true;
  const previousEdits = previous?.pole_edits ?? {};
  const nextEdits = next?.pole_edits ?? {};
  const ids = new Set([...Object.keys(previousEdits), ...Object.keys(nextEdits)]);
  for (const id of ids) if (JSON.stringify(wifiPoleInputs(previousEdits[id])) !== JSON.stringify(wifiPoleInputs(nextEdits[id]))) return true;
  const areaInputs = (project) => (project?.wifi_analysis_areas ?? []).map((area) => ({ id: area.id, name: area.name, polygon_revision: area.polygon_revision, wgs84_coordinates: area.wgs84_coordinates }));
  return JSON.stringify(areaInputs(previous)) !== JSON.stringify(areaInputs(next));
}

export function invalidateWifiResults(project) {
  if (!project?.wifi_coverage) return project;
  project.wifi_coverage.result = null;
  project.wifi_coverage.state = { ...project.wifi_coverage.state, status: "not-calculated", last_calculated_at: null, calculation_input_sha256: null, warnings: [], assumptions: [], provenance: {} };
  return project;
}

export function invalidateWifiIfSignificant(previous, next) {
  if (wifiSignificantProjectChange(previous, next)) invalidateWifiResults(next);
  return next;
}

export function closeWifiArea(points) {
  if (!Array.isArray(points) || points.length < 3) throw new Error("Wi-Fi analysis area needs at least three distinct vertices");
  if (points.length > 10000) throw new Error("Wi-Fi analysis area exceeds the 10,000-vertex limit");
  if (points.some((point) => !Array.isArray(point) || point.length !== 2 || !Number.isFinite(point[0]) || !Number.isFinite(point[1]) || point[0] < -180 || point[0] > 180 || point[1] < -90 || point[1] > 90)) throw new Error("Wi-Fi analysis-area coordinates must be finite numbers within WGS84 bounds");
  const distinct = new Set(points.map((point) => `${point[0]},${point[1]}`));
  if (distinct.size < 3) throw new Error("Wi-Fi analysis area needs at least three distinct vertices");
  const cross = (a, b, c) => (b[0] - a[0]) * (c[1] - a[1]) - (b[1] - a[1]) * (c[0] - a[0]);
  const intersects = (a, b, c, d) => cross(a, b, c) * cross(a, b, d) < 0 && cross(c, d, a) * cross(c, d, b) < 0;
  for (let i = 0; i < points.length; i += 1) for (let j = i + 1; j < points.length; j += 1) if (Math.abs(i - j) > 1 && !(i === 0 && j === points.length - 1) && intersects(points[i], points[(i + 1) % points.length], points[j], points[(j + 1) % points.length])) throw new Error("Wi-Fi analysis area is self-intersecting");
  return [...points, points[0]];
}

export function wifiEffectiveValues(project, poleId) {
  const edit = project?.pole_edits?.[poleId];
  const wifi = edit?.fixture_configuration?.wifi_configuration;
  return { radius_m: wifi?.radius_override_m ?? project?.defaults?.wifi_radius_m ?? 30, enabled: wifi?.enabled ?? true, enabled_override: wifi?.enabled ?? null, radius_override_m: wifi?.radius_override_m ?? null };
}

export function setWifiOverride(configuration, patch) {
  const current = configuration?.wifi_configuration ?? { radius_override_m: null, enabled: null, notes: "", modified_at: new Date().toISOString(), configuration_revision: 1, legacy_metadata: {} };
  return { ...configuration, wifi_configuration: { ...current, ...patch, configuration_revision: (current.configuration_revision ?? 1) + 1, modified_at: new Date().toISOString() } };
}
