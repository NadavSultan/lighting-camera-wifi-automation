export function selectBulkPoleIds(poles, mode, folder, manualIds) {
  const manual = new Set(manualIds);
  return poles
    .filter((pole) => mode === "all" || (mode === "folder" && (pole.folder_path.join(" / ") || "Unfiled") === folder) || (mode === "manual" && manual.has(pole.id)))
    .map((pole) => pole.id);
}

export function withoutCameraOverride(overrides, slotId) {
  return Object.fromEntries(Object.entries(overrides).filter(([key]) => key !== slotId));
}

export function formatApiErrorDetail(detail) {
  if (typeof detail === "string") return detail;
  if (Array.isArray(detail)) {
    return detail.map((item) => item && typeof item === "object" && "msg" in item ? String(item.msg) : JSON.stringify(item)).join("; ");
  }
  if (detail && typeof detail === "object" && "message" in detail && typeof detail.message === "string") {
    return detail.message;
  }
  return JSON.stringify(detail);
}

export async function uploadIesAndRefresh(upload, refresh) {
  try {
    return { value: await upload(), error: null };
  } catch (error) {
    await refresh();
    return { value: null, error };
  }
}
