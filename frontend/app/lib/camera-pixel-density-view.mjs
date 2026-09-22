function validProfile(project) {
  const profile = project?.camera_pixel_density_profile;
  return Boolean(
    project?.projected_crs && profile
    && Number.isFinite(profile.lower_projection_height_m)
    && Number.isFinite(profile.upper_projection_height_m)
    && Number.isFinite(profile.maximum_visible_distance_m)
    && profile.lower_projection_height_m >= 0
    && profile.lower_projection_height_m < profile.upper_projection_height_m
    && profile.maximum_visible_distance_m > 0
  );
}

export function cameraPixelDensityView(project) {
  if (!project) return { status: "not-calculated", canCalculate: false, layerAvailable: false, message: "No camera pixel-density result" };
  const layer = project.camera_pixel_density;
  const current = layer?.state?.status === "current" && layer.result
    && layer.state.calculation_input_sha256 === layer.result.calculation_input_sha256;
  if (layer?.state?.status === "stale" && layer.result) {
    return { status: "stale", canCalculate: validProfile(project), layerAvailable: false, message: "Stale — recalculate required" };
  }
  if (!current) return { status: "not-calculated", canCalculate: validProfile(project), layerAvailable: false, message: "No camera pixel-density result" };
  return { status: "current", canCalculate: validProfile(project), layerAvailable: true, message: project.layer_state?.camera_pixel_density ? "Current camera pixel-density result" : "Current result — layer hidden" };
}

function significant(project) {
  const poles = [...(project.source?.poles ?? [])].sort((a, b) => (a.sequence_index - b.sequence_index) || a.id.localeCompare(b.id));
  return {
    projected_crs: project.projected_crs,
    profile: project.camera_pixel_density_profile,
    default_pole_height_m: project.defaults?.pole_height_m,
    poles: poles.map((pole) => {
      const edit = project.pole_edits?.[pole.id] ?? {};
      const config = edit.fixture_configuration;
      return {
        id: pole.id, sequence_index: pole.sequence_index,
        longitude: edit.longitude ?? pole.longitude, latitude: edit.latitude ?? pole.latitude,
        active: edit.active ?? true, fixture_type: edit.fixture_type ?? project.defaults?.fixture_type,
        height_m: edit.height_m ?? project.defaults?.pole_height_m,
        fixture_configuration: config ? {
          fixture_model_id: config.fixture_model_id,
          fixture_model_revision: config.fixture_model_revision,
          mounting_template_revision: config.mounting_template_revision,
          fixture_azimuth_deg: config.fixture_azimuth_deg,
          camera_overrides: Object.fromEntries(Object.entries(config.camera_overrides ?? {}).sort().map(([key, value]) => [key, {
            slot_id: value.slot_id, camera_model_id: value.camera_model_id ?? null,
            camera_model_revision: value.camera_model_revision ?? null, lens_id: value.lens_id ?? null,
            lens_revision: value.lens_revision ?? null, enabled: value.enabled ?? null,
            relative_azimuth_deg: value.relative_azimuth_deg ?? null, downward_tilt_deg: value.downward_tilt_deg ?? null,
          }]))
        } : null,
      };
    }),
  };
}

export function invalidateCameraPixelDensityIfSignificant(previous, next) {
  if (!previous?.camera_pixel_density?.result || previous.camera_pixel_density.state.status !== "current") return next;
  if (JSON.stringify(significant(previous)) === JSON.stringify(significant(next))) return next;
  const updated = structuredClone(next);
  updated.camera_pixel_density.state = {
    status: "stale",
    calculation_input_sha256: updated.camera_pixel_density.result.calculation_input_sha256,
    message: "Stale — recalculate required",
  };
  updated.layer_state.camera_pixel_density = false;
  return updated;
}
