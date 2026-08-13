import type { Project } from "./types";

const API_URL = process.env.NEXT_PUBLIC_API_URL ?? "http://127.0.0.1:8000";

async function api<T>(path: string, init?: RequestInit): Promise<T> {
  const response = await fetch(`${API_URL}${path}`, init);
  if (!response.ok) {
    let message = `${response.status} ${response.statusText}`;
    try {
      const body = (await response.json()) as { detail?: string };
      if (body.detail) message = body.detail;
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

export function openProject(project: Project) {
  return api<Project>("/api/projects/open", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(project),
  });
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
