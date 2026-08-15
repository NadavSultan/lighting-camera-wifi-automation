import type { CameraEquipmentCatalog, CameraModel, FixtureModel, FixtureModelCatalog, IesFileRecord, IesLibrary, LensConfiguration, Project } from "./types";
import { formatApiErrorDetail } from "./phase2-workflows.mjs";

const API_URL = process.env.NEXT_PUBLIC_API_URL ?? "http://127.0.0.1:8000";

async function api<T>(path: string, init?: RequestInit): Promise<T> {
  const response = await fetch(`${API_URL}${path}`, init);
  if (!response.ok) {
    let message = `${response.status} ${response.statusText}`;
    try {
      const body = (await response.json()) as { detail?: unknown };
      if (body.detail) message = formatApiErrorDetail(body.detail);
    } catch {
      // Keep the HTTP status when the response is not JSON.
    }
    throw new Error(message);
  }
  return response.json() as Promise<T>;
}

export function createProject(name = "Untitled lighting project") {
  return api<Project>("/api/projects", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ name }),
  });
}

export function importProjectFile(file: File) {
  return api<Project>("/api/projects/import", {
    method: "POST",
    headers: { "Content-Type": "application/octet-stream", "X-Filename": file.name },
    body: file,
  });
}

export function saveProject(project: Project) {
  return api<Project>(`/api/projects/${encodeURIComponent(project.id)}`, {
    method: "PUT",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(project),
  });
}

export function recalculateCameraGeometry(project: Project) {
  return api<Project>(`/api/projects/${encodeURIComponent(project.id)}/camera-geometry/recalculate`, {
    method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify(project),
  });
}

export function openProject(project: Project) {
  return api<Project>("/api/projects/open", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(project),
  });
}

export function getFixtureCatalog() { return api<FixtureModelCatalog>("/api/catalogs/fixtures"); }
export function getCameraCatalog() { return api<CameraEquipmentCatalog>("/api/catalogs/cameras"); }
export function getIesLibrary() { return api<IesLibrary>("/api/catalogs/ies"); }
export function saveFixtureModel(model: FixtureModel) {
  return api<FixtureModel>(`/api/catalogs/fixtures/${encodeURIComponent(model.id)}`, { method: "PUT", headers: { "Content-Type": "application/json" }, body: JSON.stringify(model) });
}
export function addFixtureTemplateRevision(fixtureId: string, revision: FixtureModel["mounting_template_revisions"][number]) {
  return api<FixtureModel>(`/api/catalogs/fixtures/${encodeURIComponent(fixtureId)}/template-revisions`, { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify(revision) });
}
export function saveCameraModel(model: CameraModel) {
  return api<CameraModel>(`/api/catalogs/cameras/${encodeURIComponent(model.id)}`, { method: "PUT", headers: { "Content-Type": "application/json" }, body: JSON.stringify(model) });
}
export function saveLens(lens: LensConfiguration) {
  return api<LensConfiguration>(`/api/catalogs/lenses/${encodeURIComponent(lens.id)}`, { method: "PUT", headers: { "Content-Type": "application/json" }, body: JSON.stringify(lens) });
}
export function uploadIes(file: File) {
  return api<IesFileRecord>("/api/catalogs/ies/upload", { method: "POST", headers: { "Content-Type": "application/octet-stream", "X-Filename": file.name }, body: file });
}
export function setIesActive(iesId: string, active: boolean) {
  return api<IesFileRecord>(`/api/catalogs/ies/${encodeURIComponent(iesId)}`, { method: "PATCH", headers: { "Content-Type": "application/json" }, body: JSON.stringify({ active }) });
}
export function associateIes(iesId: string, fixtureId: string) {
  return api(`/api/catalogs/ies/${encodeURIComponent(iesId)}/fixtures/${encodeURIComponent(fixtureId)}`, { method: "PUT", headers: { "Content-Type": "application/json" }, body: JSON.stringify({ active: true }) });
}
export async function removeIesAssociation(iesId: string, fixtureId: string) {
  const response = await fetch(`${API_URL}/api/catalogs/ies/${encodeURIComponent(iesId)}/fixtures/${encodeURIComponent(fixtureId)}`, { method: "DELETE" });
  if (!response.ok) throw new Error(`IES association removal failed: ${response.statusText}`);
}
export function setDefaultIes(fixtureId: string, iesId: string) {
  return api<FixtureModel>(`/api/catalogs/fixtures/${encodeURIComponent(fixtureId)}/default-ies/${encodeURIComponent(iesId)}`, { method: "PUT" });
}

export async function downloadUpdatedKml(project: Project) {
  const response = await fetch(`${API_URL}/api/projects/${encodeURIComponent(project.id)}/export/kml`);
  if (!response.ok) throw new Error(`KML export failed: ${response.statusText}`);
  downloadBlob(await response.blob(), `${baseName(project.source.file?.filename ?? project.name)}-updated.kml`);
}

export function downloadProjectJson(project: Project) {
  downloadBlob(new Blob([JSON.stringify(project, null, 2)], { type: "application/json" }), `${baseName(project.name)}.lighting-project.json`);
}

function baseName(value: string) {
  return value.replace(/\.(kml|kmz)$/i, "").replace(/[^a-z0-9._-]+/gi, "-").replace(/^-|-$/g, "") || "project";
}

function downloadBlob(blob: Blob, filename: string) {
  const href = URL.createObjectURL(blob);
  const anchor = document.createElement("a");
  anchor.href = href;
  anchor.download = filename;
  anchor.click();
  URL.revokeObjectURL(href);
}
