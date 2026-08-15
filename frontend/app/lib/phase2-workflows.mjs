export function selectBulkPoleIds(poles, mode, folder, manualIds) {
  const manual = new Set(manualIds);
  return poles
    .filter((pole) => mode === "all" || (mode === "folder" && (pole.folder_path.join(" / ") || "Unfiled") === folder) || (mode === "manual" && manual.has(pole.id)))
    .map((pole) => pole.id);
}

export function withoutCameraOverride(overrides, slotId) {
  return Object.fromEntries(Object.entries(overrides).filter(([key]) => key !== slotId));
}
