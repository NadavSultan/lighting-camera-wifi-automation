"use client";

import { type ChangeEvent, type CSSProperties, useMemo, useRef, useState } from "react";
import { EngineeringMap } from "./EngineeringMap";
import { createProject, downloadProjectJson, downloadUpdatedKml, importProjectFile, openProject, saveProject } from "../lib/api";
import { effectivePole, type EffectivePole, type FixtureType, type PoleEdit, type Project } from "../lib/types";

const FIXTURE_COLORS: Record<FixtureType, string> = { LITE: "var(--lite)", WIFI: "var(--wifi)", SMART: "var(--smart)" };
type LayerKey = "original_customer_poles" | "lite_fixtures" | "wifi_fixtures" | "smart_fixtures" | "camera_fov" | "wifi_coverage" | "calculation_areas" | "calculation_points" | "lighting_heat_map" | "cap_locations" | "cap_connections" | "warnings";
const LAYERS: Array<{ key: LayerKey; label: string; color: string; phase?: number }> = [
  { key: "original_customer_poles", label: "Original customer poles", color: "#8795a4" },
  { key: "lite_fixtures", label: "LITE fixtures", color: "var(--lite)" },
  { key: "wifi_fixtures", label: "WIFI fixtures", color: "var(--wifi)" },
  { key: "smart_fixtures", label: "SMART fixtures", color: "var(--smart)" },
  { key: "camera_fov", label: "Camera FOV polygons", color: "#8b5cf6", phase: 3 },
  { key: "wifi_coverage", label: "Conceptual Wi-Fi", color: "#22d3ee", phase: 4 },
  { key: "calculation_areas", label: "Calculation areas", color: "#fb923c", phase: 5 },
  { key: "calculation_points", label: "Calculation points", color: "#e2e8f0", phase: 5 },
  { key: "lighting_heat_map", label: "Lighting heat map", color: "#f97316", phase: 5 },
  { key: "cap_locations", label: "Recommended CAP", color: "#34d399", phase: 6 },
  { key: "cap_connections", label: "CAP connections", color: "#10b981", phase: 6 },
  { key: "warnings", label: "Warnings", color: "var(--warning)" },
];

export function EngineeringWorkspace() {
  const [project, setProject] = useState<Project | null>(null);
  const [selectedId, setSelectedId] = useState<string | null>(null);
  const [leftCollapsed, setLeftCollapsed] = useState(false);
  const [rightCollapsed, setRightCollapsed] = useState(false);
  const [past, setPast] = useState<Project[]>([]);
  const [future, setFuture] = useState<Project[]>([]);
  const [busy, setBusy] = useState(false);
  const [status, setStatus] = useState("Ready - Phase 1 existing-pole workflow");
  const [error, setError] = useState<string | null>(null);
  const [bulkFolder, setBulkFolder] = useState("all");
  const importRef = useRef<HTMLInputElement>(null);
  const openRef = useRef<HTMLInputElement>(null);

  const effectivePoles = useMemo(() => project?.source.poles.map((pole) => effectivePole(project, pole)) ?? [], [project]);
  const selected = useMemo<EffectivePole | null>(() => effectivePoles.find((pole) => pole.id === selectedId) ?? null, [effectivePoles, selectedId]);
  const folders = useMemo(() => Array.from(new Set(effectivePoles.map((pole) => pole.folder_path.join(" / ") || "Unfiled"))).sort(), [effectivePoles]);
  const counts = useMemo(() => ({
    LITE: effectivePoles.filter((pole) => pole.fixtureType === "LITE").length,
    WIFI: effectivePoles.filter((pole) => pole.fixtureType === "WIFI").length,
    SMART: effectivePoles.filter((pole) => pole.fixtureType === "SMART").length,
  }), [effectivePoles]);
  const activeWarnings = project?.warnings.filter((warning) => warning.severity !== "info").length ?? 0;

  function replaceProject(next: Project, recordHistory = true) {
    if (recordHistory && project) setPast((items) => [...items.slice(-39), project]);
    if (recordHistory) setFuture([]);
    setProject(next);
  }

  function mutateProject(updater: (draft: Project) => void) {
    if (!project) return;
    const next = structuredClone(project);
    updater(next);
    next.updated_at = new Date().toISOString();
    replaceProject(next);
  }

  async function runAction(action: () => Promise<void>) {
    setBusy(true);
    setError(null);
    try { await action(); } catch (caught) { setError(caught instanceof Error ? caught.message : "Unexpected application error"); }
    finally { setBusy(false); }
  }

  async function handleNew() {
    await runAction(async () => {
      const next = await createProject();
      setProject(next); setPast([]); setFuture([]); setSelectedId(null);
      setStatus("New local project created - import a customer KML or KMZ");
    });
  }

  async function handleImport(event: ChangeEvent<HTMLInputElement>) {
    const file = event.target.files?.[0];
    event.target.value = "";
    if (!file) return;
    await runAction(async () => {
      const next = await importProjectFile(file);
      setProject(next); setPast([]); setFuture([]); setSelectedId(next.source.poles[0]?.id ?? null);
      setStatus(`Imported ${next.source.poles.length} authoritative customer poles from ${file.name}`);
    });
  }

  async function handleOpen(event: ChangeEvent<HTMLInputElement>) {
    const file = event.target.files?.[0];
    event.target.value = "";
    if (!file) return;
    await runAction(async () => {
      const parsed = JSON.parse(await file.text()) as Project;
      const next = await openProject(parsed);
      setProject(next); setPast([]); setFuture([]); setSelectedId(next.source.poles[0]?.id ?? null);
      setStatus(`Reopened ${next.name} from project JSON`);
    });
  }

  async function handleSave() {
    if (!project) return;
    await runAction(async () => {
      const saved = await saveProject(project);
      setProject(saved);
      setStatus(`Saved ${saved.name} locally at ${new Date(saved.updated_at).toLocaleTimeString()}`);
    });
  }

  function undo() {
    if (!project || !past.length) return;
    const previous = past[past.length - 1];
    setFuture((items) => [project, ...items].slice(0, 40));
    setPast((items) => items.slice(0, -1));
    setProject(previous);
    setStatus("Undid last project edit");
  }

  function redo() {
    if (!project || !future.length) return;
    const next = future[0];
    setPast((items) => [...items, project].slice(-40));
    setFuture((items) => items.slice(1));
    setProject(next);
    setStatus("Redid project edit");
  }

  function updatePole(poleId: string, patch: Partial<PoleEdit>) {
    mutateProject((draft) => {
      const existing = draft.pole_edits[poleId] ?? { pole_id: poleId, location_edit_authorized: false };
      draft.pole_edits[poleId] = { ...existing, ...patch, pole_id: poleId, modified_at: new Date().toISOString() };
    });
    setStatus("Pole edit staged separately from the customer source");
  }

  function restorePole(poleId: string) {
    mutateProject((draft) => { delete draft.pole_edits[poleId]; });
    setStatus("Restored all source/default values for the selected pole");
  }

  function applyBulkFixture(fixture: FixtureType) {
    if (!project) return;
    const targets = effectivePoles.filter((pole) => bulkFolder === "all" || (pole.folder_path.join(" / ") || "Unfiled") === bulkFolder);
    mutateProject((draft) => {
      for (const pole of targets) {
        const current = draft.pole_edits[pole.id] ?? { pole_id: pole.id, location_edit_authorized: false };
        draft.pole_edits[pole.id] = { ...current, fixture_type: fixture, modified_at: new Date().toISOString() };
      }
    });
    setStatus(`Assigned ${fixture} to ${targets.length} pole${targets.length === 1 ? "" : "s"}; source coordinates unchanged`);
  }

  function toggleLayer(key: LayerKey, enabled: boolean) {
    if (!project) return;
    mutateProject((draft) => { draft.layer_state[key] = enabled; });
  }

  function exportBoth() {
    if (!project) return;
    void runAction(async () => {
      const saved = await saveProject(project);
      setProject(saved);
      downloadProjectJson(saved);
      if (saved.source.file) await downloadUpdatedKml(saved);
      setStatus("Exported project JSON and updated KML");
    });
  }

  const workspaceClass = ["workspace", leftCollapsed && "left-collapsed", rightCollapsed && "right-collapsed"].filter(Boolean).join(" ");
  return (
    <main className="app-shell">
      <header className="topbar">
        <div className="brand"><div className="brand-mark" /><div><strong>LCWA Studio</strong><span>Lighting · Camera · Wi-Fi engineering</span></div></div>
        <nav className="toolbar-scroll" aria-label="Project actions">
          <button className="tool-button" onClick={() => void handleNew()} disabled={busy}>New Project</button>
          <button className="tool-button" onClick={() => openRef.current?.click()} disabled={busy}>Open Project</button>
          <button className="tool-button primary" onClick={() => importRef.current?.click()} disabled={busy}>Import KML/KMZ</button>
          <button className="tool-button" onClick={() => void handleSave()} disabled={!project || busy}>Save Project</button>
          <span className="toolbar-divider" />
          <button className="tool-button" onClick={undo} disabled={!past.length}>Undo</button>
          <button className="tool-button" onClick={redo} disabled={!future.length}>Redo</button>
          <span className="toolbar-divider" />
          <button className="tool-button" disabled title="Phase 5 after Phase 1 review">Draw Calculation Area</button>
          <button className="tool-button" disabled title="Phase 5 after validated IES conventions">Calculate Lighting</button>
          <button className="tool-button" disabled title="Phase 6 after CAP constraints are clarified">Recommend CAP</button>
          <button className="tool-button" onClick={exportBoth} disabled={!project || busy}>Export Project</button>
        </nav>
        <div className="mode-pill">Existing-pole mode</div>
        <input ref={importRef} className="sr-only" type="file" accept=".kml,.kmz" onChange={handleImport} />
        <input ref={openRef} className="sr-only" type="file" accept=".json,.lighting-project.json" onChange={handleOpen} />
      </header>

      <div className={workspaceClass}>
        <aside className="side-panel" aria-label="Map layers">
          {leftCollapsed ? <CollapsedRail label="Layers" symbol="›" onClick={() => setLeftCollapsed(false)} /> : (
            <div className="panel-scroll">
              <div className="panel-titlebar"><h2>Project & layers</h2><button className="icon-button" onClick={() => setLeftCollapsed(true)} aria-label="Collapse layer panel">‹</button></div>
              <section className="section">
                <p className="project-name">{project?.name ?? "No project loaded"}</p>
                <div className="project-meta">{project?.source.file ? `${project.source.file.filename} · ${project.source.poles.length} source poles` : "Create a project or import a customer layout."}</div>
                <div className="counts-grid">{(["LITE", "WIFI", "SMART"] as FixtureType[]).map((fixture) => <div className={`count-card ${fixture.toLowerCase()}`} key={fixture}><span>{fixture}</span><strong>{counts[fixture]}</strong></div>)}</div>
              </section>
              <section className="section">
                <div className="section-heading"><h3>Map layers</h3><span className="helper">Phase 1</span></div>
                {LAYERS.map((layer) => <label className="layer-row" key={layer.key}><input type="checkbox" checked={Boolean(project?.layer_state[layer.key])} disabled={!project || Boolean(layer.phase)} onChange={(event) => toggleLayer(layer.key, event.target.checked)} /><span className="layer-dot" style={{ "--dot": layer.color } as CSSProperties} /><span>{layer.label}</span>{layer.phase && <span className="phase-tag">P{layer.phase}</span>}</label>)}
              </section>
              <section className="section">
                <div className="section-heading"><h3>Bulk assignment</h3></div>
                <div className="field full"><label htmlFor="bulk-folder">Target folder</label><select id="bulk-folder" value={bulkFolder} onChange={(event) => setBulkFolder(event.target.value)} disabled={!project}><option value="all">All imported poles</option>{folders.map((folder) => <option key={folder}>{folder}</option>)}</select></div>
                <div className="bulk-row" style={{ marginTop: 8 }}><button className="quiet-button" disabled={!project} onClick={() => applyBulkFixture("LITE")}>Set LITE</button><button className="quiet-button" disabled={!project} onClick={() => applyBulkFixture("WIFI")}>Set WIFI</button></div>
                <button className="quiet-button" style={{ marginTop: 7, width: "100%" }} disabled={!project} onClick={() => applyBulkFixture("SMART")}>Set SMART</button>
                <p className="helper">Assignments create edit overlays. Folder names are never interpreted automatically.</p>
              </section>
              <section className="section">
                <div className="section-heading"><h3>Validation</h3><span className="helper">{activeWarnings} warnings</span></div>
                <div className="warning-list">{project?.warnings.slice(0, 8).map((warning, index) => <div className={`warning-card ${warning.severity}`} key={`${warning.code}-${index}`}>{warning.message}</div>)}{!project && <div className="empty-copy">Validation results appear after import.</div>}</div>
              </section>
            </div>
          )}
        </aside>

        <section className="map-stage" aria-label="Engineering map workspace">
          <EngineeringMap project={project} selected={selected} onSelect={setSelectedId} resizeSignal={`${leftCollapsed}-${rightCollapsed}`} />
          <div className="map-overlay map-caption"><strong>Customer coordinates are locked</strong><span>Phase 1 displays and classifies existing poles only. No locations are generated or moved.</span></div>
          {!project?.source.poles.length && <div className="map-overlay map-empty"><span className="eyebrow">Phase 1 · Existing-pole foundation</span><h1>Start with the customer’s pole layout</h1><p>Import a KML or KMZ to validate and display authoritative pole coordinates. Your changes remain separate and reversible.</p><button className="primary-button" onClick={() => importRef.current?.click()} disabled={busy}>Import KML/KMZ</button></div>}
        </section>

        <aside className="side-panel inspector" aria-label="Properties inspector">
          {rightCollapsed ? <CollapsedRail label="Properties" symbol="‹" onClick={() => setRightCollapsed(false)} /> : (
            <div className="panel-scroll">
              <div className="panel-titlebar"><h2>Properties</h2><button className="icon-button" onClick={() => setRightCollapsed(true)} aria-label="Collapse properties inspector">›</button></div>
              {selected && project ? <PoleInspector pole={selected} project={project} onChange={(patch) => updatePole(selected.id, patch)} onRestore={() => restorePole(selected.id)} /> : <section className="section"><h3>No pole selected</h3><p className="empty-copy">Click an imported pole to inspect source data and apply a separate engineering override.</p></section>}
            </div>
          )}
        </aside>
      </div>

      <footer className="statusbar"><span className="status-item"><span className="status-dot" />API-backed local project</span><span>CRS: {project?.projected_crs ?? "pending import"}</span><span>Source: {project?.source_crs ?? "WGS84"}</span><span>Edits: {project ? Object.keys(project.pole_edits).length : 0}</span><span className="status-message">{busy ? "Working…" : status}</span></footer>
      {error && <div className="toast" role="alert" onClick={() => setError(null)}>{error}</div>}
    </main>
  );
}

function CollapsedRail({ label, symbol, onClick }: { label: string; symbol: string; onClick: () => void }) {
  return <div className="collapsed-rail"><button className="icon-button" onClick={onClick} aria-label={`Expand ${label}`}>{symbol}</button><span className="collapsed-label">{label}</span></div>;
}

function PoleInspector({ pole, project, onChange, onRestore }: { pole: EffectivePole; project: Project; onChange: (patch: Partial<PoleEdit>) => void; onRestore: () => void }) {
  return <>
    <section className="section">
      <div className="section-heading"><h3>Selected pole</h3>{pole.modified && <span className="phase-tag" style={{ color: "var(--accent)" }}>Modified</span>}</div>
      <div className="form-grid">
        <div className="field full"><label htmlFor="pole-name">Pole name</label><input id="pole-name" value={pole.displayName} onChange={(event) => onChange({ display_name: event.target.value })} /></div>
        <div className="field"><label htmlFor="pole-id">Engineering ID</label><input id="pole-id" value={pole.externalId} onChange={(event) => onChange({ external_id: event.target.value })} /></div>
        <div className="field"><label htmlFor="fixture-type">Fixture type</label><select id="fixture-type" value={pole.fixtureType} onChange={(event) => onChange({ fixture_type: event.target.value as FixtureType })}>{(["LITE", "WIFI", "SMART"] as FixtureType[]).map((fixture) => <option key={fixture}>{fixture}</option>)}</select></div>
        <div className="field"><label htmlFor="pole-height">Pole height (m)</label><input id="pole-height" type="number" min="0.1" max="100" step="0.1" value={pole.heightM ?? ""} placeholder="Required" onChange={(event) => onChange({ height_m: event.target.value ? Number(event.target.value) : null })} /></div>
        <label className="toggle-line"><input type="checkbox" checked={pole.active} onChange={(event) => onChange({ active: event.target.checked })} />Active pole</label>
        <div className="field full"><label htmlFor="notes">Engineering notes</label><textarea id="notes" value={pole.engineeringNotes} onChange={(event) => onChange({ engineering_notes: event.target.value })} placeholder="Field observations, assumptions, or follow-up…" /></div>
      </div>
      <button className="quiet-button" style={{ marginTop: 10 }} onClick={onRestore} disabled={!pole.modified}>Restore source/default values</button>
    </section>
    <section className="section">
      <div className="section-heading"><h3>Original customer data</h3><span className="layer-dot" style={{ "--dot": FIXTURE_COLORS[pole.fixtureType] } as CSSProperties} /></div>
      <div className="source-card"><dl><dt>Folder</dt><dd>{pole.folder_path.join(" / ") || "Unfiled"}</dd><dt>Source name</dt><dd>{pole.name}</dd><dt>Placemark ID</dt><dd>{pole.source_placemark_id ?? "Not provided"}</dd><dt>Coordinates</dt><dd>{pole.raw_coordinates}</dd><dt>Source style</dt><dd>{pole.source_style_url ?? "None"}</dd></dl></div>
      <p className="helper">Coordinates are read-only in Phase 1. The exact uploaded value remains available for restoration and export comparison.</p>
    </section>
    <section className="section"><div className="section-heading"><h3>Lighting</h3><span className="phase-tag">Phase 2/5</span></div><div className="future-card"><strong>Catalog and calculations are intentionally gated.</strong><br />Luminaire and IES assignment follows Phase 1 review; illuminance requires approved photometric conventions and validation cases.</div></section>
    {pole.fixtureType !== "LITE" && <section className="section"><div className="section-heading"><h3>Wi-Fi</h3><span className="phase-tag">Phase 4</span></div><div className="future-card">Default conceptual radius: {project.defaults.wifi_radius_m} m. No RF coverage is shown or claimed in Phase 1.</div></section>}
    {pole.fixtureType === "SMART" && <section className="section"><div className="section-heading"><h3>Camera & CAP</h3><span className="phase-tag">Phase 2/3/6</span></div><div className="future-card">Camera angle convention is stored as {project.defaults.camera_downward_angle_deg}° below horizontal. FOV and CAP participation remain disabled until their inputs are reviewed.</div></section>}
  </>;
}
