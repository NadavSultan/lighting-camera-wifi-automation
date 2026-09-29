const empty = () => ({ type: "FeatureCollection", features: [] });

function visibleResult(project) {
  const layer = project?.camera_pixel_density;
  return project?.layer_state?.camera_pixel_density
    && layer?.state?.status === "current"
    && layer.result
    && layer.state.calculation_input_sha256 === layer.result.calculation_input_sha256
    ? layer.result : null;
}

export function densityBandFeatures(project) {
  const result = visibleResult(project);
  if (!result) return empty();
  return { type: "FeatureCollection", features: result.camera_results.flatMap((camera) => camera.bands.flatMap((band) => band.wgs84_rings.map((rings, part) => ({
    type: "Feature", id: `${camera.footprint_id}/${band.band_id}/${part}`,
    properties: { footprint_id: camera.footprint_id, band_id: band.band_id, rank: band.rank, minimum: band.minimum_px_per_face, maximum: band.maximum_px_per_face, colour_token: band.colour_token },
    geometry: { type: "Polygon", coordinates: rings },
  })))) };
}

export function densityOverlapFeatures(project) {
  const result = visibleResult(project);
  if (!result) return empty();
  const winningBands = new Map(result.camera_results.flatMap((camera) => camera.bands.map((band) => [`${camera.footprint_id}\0${band.band_id}`, band])));
  return { type: "FeatureCollection", features: result.overlap_regions.flatMap((region) => region.wgs84_rings.map((rings, part) => ({
    type: "Feature", id: `${region.overlap_region_id}/${part}`, properties: {
      ...region,
      minimum_px_per_face: winningBands.get(`${region.winning_camera_footprint_id}\0${region.winning_band_id}`)?.minimum_px_per_face ?? null,
      maximum_px_per_face: winningBands.get(`${region.winning_camera_footprint_id}\0${region.winning_band_id}`)?.maximum_px_per_face ?? null,
    }, geometry: { type: "Polygon", coordinates: rings },
  }))) };
}

export function densityOverlapLabelPoints(project) {
  return densityOverlapFeatures(project).features.map((feature) => {
    const ring = feature.geometry.coordinates[0];
    const coordinates = ring.slice(0, -1);
    const coordinate = coordinates.reduce((sum, point) => [sum[0] + point[0] / coordinates.length, sum[1] + point[1] / coordinates.length], [0, 0]);
    return { id: String(feature.id), coordinate, label: `${feature.properties.multiplicity}×` };
  });
}

function contributorIds(value) {
  if (typeof value === "string") {
    try { value = JSON.parse(value); } catch { return null; }
  }
  return Array.isArray(value) && value.length > 1 && value.every((id) => typeof id === "string") ? value : null;
}

export function densityInspectionAt(features) {
  const overlap = features.map((feature) => feature.properties).find((properties) => contributorIds(properties?.camera_footprint_ids));
  if (overlap) return {
    contributors: [...contributorIds(overlap.camera_footprint_ids)].sort(),
    winner: overlap.winning_camera_footprint_id,
    winningBandId: overlap.winning_band_id,
    multiplicity: overlap.multiplicity,
    minimumPxPerFace: overlap.minimum_px_per_face,
    maximumPxPerFace: overlap.maximum_px_per_face,
  };
  const band = features.map((feature) => feature.properties).find((properties) => properties?.footprint_id && properties?.band_id);
  return band ? {
    contributors: [String(band.footprint_id)], winner: String(band.footprint_id), winningBandId: String(band.band_id), multiplicity: 1,
    minimumPxPerFace: band.minimum, maximumPxPerFace: band.maximum,
  } : null;
}

export function attachDensityInspection(map, onInspect, isDrawing) {
  const layers = ["camera-density-overlap-hit", ...Array.from({ length: 10 }, (_, index) => `camera-density-band-${index + 1}`)];
  map.on("click", (event) => {
    if (isDrawing()) return;
    const inspection = densityInspectionAt(map.queryRenderedFeatures(event.point, { layers }));
    if (inspection) onInspect(inspection, event.lngLat);
  });
}

export function densityInspectionStyle() {
  return {
    color: "#17212c",
    maxHeight: "min(180px, calc(100vh - 160px))",
    overflowY: "auto",
    overflowWrap: "anywhere",
    width: "min(320px, calc(100vw - 88px))",
  };
}

export function densityLayerDefinitions(legend) {
  return legend.thresholds.map((threshold, index) => ({ rank: index + 1, token: threshold.token, colour: threshold.colour, opacity: legend.fill_opacity }));
}
