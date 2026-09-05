import type { CameraEquipmentCatalog, CameraModel, CapCandidateSite, CapPlanningInputs, FixtureModel, FixtureModelCatalog, IesFileRecord, IesLibrary, LastReportMetadata, LensConfiguration, Project, ReportPackageDownloadResult, ReportPackageRequest, WifiAnalysisArea } from "./types";
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

export function getProject(projectId: string) {
  return api<Project>(`/api/projects/${encodeURIComponent(projectId)}`);
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

export function calculateLighting(project: Project, areaId: string) {
  return api<Project>(`/api/projects/${encodeURIComponent(project.id)}/lighting/calculate/${encodeURIComponent(areaId)}`, {
    method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify(project),
  });
}

export function calculateWifiCoverage(project: Project) {
  return api<Project>(`/api/projects/${encodeURIComponent(project.id)}/wifi-coverage/calculate`, {
    method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify(project),
  });
}

export function saveCapPlanningInputs(projectId: string, inputs: CapPlanningInputs) {
  return api<Project>(`/api/projects/${encodeURIComponent(projectId)}/cap-planning-inputs`, { method: "PUT", headers: { "Content-Type": "application/json" }, body: JSON.stringify(inputs) });
}

export function calculateCapPlan(project: Project) {
  return api<Project>(`/api/projects/${encodeURIComponent(project.id)}/cap-planning/calculate`, { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify(project) });
}
export function validateCapPlan(project: Project) { return api<Project>(`/api/projects/${encodeURIComponent(project.id)}/cap-planning/validate`, { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify(project) }); }
export function recommendCapPlan(project: Project) { return api<Project>(`/api/projects/${encodeURIComponent(project.id)}/cap-planning/recommend`, { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify(project) }); }
export function addCapCandidate(projectId: string, candidate: CapCandidateSite) { return api<Project>(`/api/projects/${encodeURIComponent(projectId)}/cap-planning/candidates`, { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify(candidate) }); }
export function replaceCapCandidate(projectId: string, candidate: CapCandidateSite) { return api<Project>(`/api/projects/${encodeURIComponent(projectId)}/cap-planning/candidates/${encodeURIComponent(candidate.id)}`, { method: "PUT", headers: { "Content-Type": "application/json" }, body: JSON.stringify(candidate) }); }
export function deleteCapCandidate(projectId: string, candidateId: string) { return api<Project>(`/api/projects/${encodeURIComponent(projectId)}/cap-planning/candidates/${encodeURIComponent(candidateId)}`, { method: "DELETE" }); }

export function addWifiAnalysisArea(projectId: string, area: WifiAnalysisArea) {
  return api<Project>(`/api/projects/${encodeURIComponent(projectId)}/wifi-analysis-areas`, { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify(area) });
}
export function replaceWifiAnalysisArea(projectId: string, area: WifiAnalysisArea) {
  return api<Project>(`/api/projects/${encodeURIComponent(projectId)}/wifi-analysis-areas/${encodeURIComponent(area.id)}`, { method: "PUT", headers: { "Content-Type": "application/json" }, body: JSON.stringify(area) });
}
export function deleteWifiAnalysisArea(projectId: string, areaId: string) {
  return api<Project>(`/api/projects/${encodeURIComponent(projectId)}/wifi-analysis-areas/${encodeURIComponent(areaId)}`, { method: "DELETE" });
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

export function previewReport(projectId: string, options?: ReportPackageRequest | null) {
  return api<Record<string, unknown>>(`/api/projects/${encodeURIComponent(projectId)}/reports/preview`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(options ?? {}),
  });
}

export async function downloadReportPackage(
  project: Project,
  request?: ReportPackageRequest | null,
): Promise<ReportPackageDownloadResult> {
  const payload: ReportPackageRequest = {
    ...(request ?? {}),
    expected_project_updated_at: request?.expected_project_updated_at ?? project.updated_at,
  };
  const response = await fetch(`${API_URL}/api/projects/${encodeURIComponent(project.id)}/reports/package`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
  });
  if (!response.ok) {
    let message = `Report package failed: ${response.status} ${response.statusText}`;
    try {
      const body = (await response.json()) as { detail?: unknown };
      if (body.detail) message = formatApiErrorDetail(body.detail);
    } catch {
      // Keep HTTP status when body is not JSON.
    }
    throw new Error(message);
  }
  const packageSha = response.headers.get("X-Report-Package-SHA256") ?? "";
  const status = response.headers.get("X-Report-Status") ?? "";
  const generatedAt = response.headers.get("X-Report-Generated-At") ?? "";
  const projectUpdatedAt = response.headers.get("X-Project-Updated-At") ?? "";
  const metadataHeader = response.headers.get("X-Report-Last-Metadata");
  let lastReport: LastReportMetadata | null = null;
  if (metadataHeader) {
    lastReport = JSON.parse(metadataHeader) as LastReportMetadata;
  }
  downloadBlob(await response.blob(), `${baseName(project.source.file?.filename ?? project.name)}-report-package.zip`);
  return {
    package_sha256: packageSha,
    status,
    generated_at: generatedAt,
    project_updated_at: projectUpdatedAt,
    last_report: lastReport,
  };
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
