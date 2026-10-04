// Exact revision resolution for read-only per-slot specification display.
export function resolveCameraSlotSpecifications(catalog, slot, override) {
  const warnings = [];
  function resolve(kind, idKey, revisionKey, current, history) {
    const explicit = override?.[idKey] != null;
    const id = explicit ? override[idKey] : slot[idKey];
    const revision = explicit ? override[revisionKey] : slot[revisionKey];
    if (!id) { warnings.push(`${kind} is unassigned.`); return null; }
    if (revision == null) { warnings.push(`${kind} ${id} has no pinned revision.`); return null; }
    const record = [...(current ?? []), ...(history ?? [])].find((item) => item.id === id && item.revision === revision);
    if (!record) warnings.push(`Pinned ${kind.toLowerCase()} ${id} r${revision} is unavailable.`);
    return record ?? null;
  }
  const camera = resolve("Camera", "camera_model_id", "camera_model_revision", catalog?.camera_models, catalog?.camera_model_history);
  const lens = resolve("Lens", "lens_id", "lens_revision", catalog?.lenses, catalog?.lens_history);
  if (camera && lens && !lens.compatible_camera_model_ids.includes(camera.id)) {
    warnings.push("The pinned camera and lens revisions are incompatible.");
  }
  return { camera, lens, warnings };
}
