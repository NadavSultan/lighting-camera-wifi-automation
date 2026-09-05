"use client";
/* eslint-disable jsx-a11y/label-has-associated-control -- Phase 6 field labels are visually adjacent to their controls; existing workspace markup uses this compact grid pattern. */

import { type ChangeEvent, type CSSProperties, useEffect, useMemo, useRef, useState } from "react";
import { EngineeringMap } from "./EngineeringMap";
import { CatalogManager } from "./CatalogManager";
import { PoleInspector as Phase2PoleInspector } from "./PoleInspector";
import { ReportPanel } from "./ReportPanel";
import { addCapCandidate, calculateCapPlan, calculateLighting, calculateWifiCoverage, createProject, deleteCapCandidate, downloadProjectJson, downloadUpdatedKml, getCameraCatalog, getFixtureCatalog, getIesLibrary, importProjectFile, openProject, recommendCapPlan, recalculateCameraGeometry, replaceCapCandidate, saveProject, validateCapPlan } from "../lib/api";
import { effectivePole, type CalculationArea, type CalculationAreaClassification, type CameraEquipmentCatalog, type EffectivePole, type FixtureModelCatalog, type FixtureType, type IesLibrary, type PoleEdit, type PoleFixtureConfiguration, type Project } from "../lib/types";
import { selectBulkPoleIds } from "../lib/phase2-workflows.mjs";
import { emptyPriorityRedrawDraft, renamePriorityArea, roundNormalizedFixtureAzimuth, validateAndClosePriorityRing } from "../lib/phase3-workflows.mjs";
import { invalidateLightingResults, lightingSignificantPoleChange, staleCalculationState, validateCalculationAreaDraft } from "../lib/phase4-workflows.mjs";
import { applyWifiFields, closeWifiArea, invalidateWifiIfSignificant, wifiBoundaryGapMessage } from "../lib/phase5-workflows.mjs";
import { CAP_DISCLAIMER, capBlockers, capOperationEnabled, invalidateCapIfSignificant } from "../lib/phase6-cap-workflows.mjs";
import { applyLastReportMetadata } from "../lib/phase7-report-workflows.mjs";

const FIXTURE_COLORS: Record<FixtureType, string> = { LITE: "var(--lite)", WIFI: "var(--wifi)", SMART: "var(--smart)" };
type LayerKey = "original_customer_poles" | "lite_fixtures" | "wifi_fixtures" | "smart_fixtures" | "camera_fov" | "camera_overlap" | "priority_areas" | "wifi_coverage" | "calculation_areas" | "calculation_points" | "lighting_heat_map" | "cap_locations" | "cap_connections" | "warnings";
const LAYERS: Array<{ key: LayerKey; label: string; color: string; phase?: number }> = [
  { key: "original_customer_poles", label: "Original customer poles", color: "#8795a4" },
  { key: "lite_fixtures", label: "LITE fixtures", color: "var(--lite)" },
  { key: "wifi_fixtures", label: "WIFI fixtures", color: "var(--wifi)" },
  { key: "smart_fixtures", label: "SMART fixtures", color: "var(--smart)" },
  { key: "camera_fov", label: "Camera 1 / Camera 2 FOV", color: "#8b5cf6" },
  { key: "camera_overlap", label: "Camera footprint overlap", color: "#ec4899" },
  { key: "priority_areas", label: "Priority areas", color: "#f59e0b" },
  { key: "wifi_coverage", label: "Conceptual Wi-Fi", color: "#22d3ee", phase: 5 },
  { key: "calculation_areas", label: "Calculation areas", color: "#14b8a6" },
  { key: "calculation_points", label: "Calculation points", color: "#e2e8f0" },
  { key: "lighting_heat_map", label: "Lighting results", color: "#f97316" },
  { key: "cap_locations", label: "CAP candidate / selected sites", color: "#34d399" },
  { key: "cap_connections", label: "CAP conceptual tree links", color: "#10b981" },
  { key: "warnings", label: "Warnings", color: "var(--warning)" },
];

function wifiFields(value: PoleFixtureConfiguration | null | undefined) {
  const wifi = value?.wifi_configuration;
  return { radius_override_m: wifi?.radius_override_m ?? null, enabled: wifi?.enabled ?? null, notes: wifi?.notes ?? "" };
}

function applyWifiRevision(previous: PoleFixtureConfiguration | null | undefined, next: PoleFixtureConfiguration | null | undefined) {
  if (!next?.wifi_configuration || JSON.stringify(wifiFields(previous)) === JSON.stringify(wifiFields(next))) return next;
  const priorRevision = previous?.wifi_configuration?.configuration_revision ?? 0;
  return { ...next, wifi_configuration: { ...next.wifi_configuration, configuration_revision: priorRevision + 1, modified_at: new Date().toISOString() } };
}

export function EngineeringWorkspace() {
  const [project, setProject] = useState<Project | null>(null);
  const [selectedId, setSelectedId] = useState<string | null>(null);
  const [leftCollapsed, setLeftCollapsed] = useState(false);
  const [rightCollapsed, setRightCollapsed] = useState(false);
  const [past, setPast] = useState<Project[]>([]);
  const [future, setFuture] = useState<Project[]>([]);
  const [busy, setBusy] = useState(false);
  const [status, setStatus] = useState("Ready - existing-pole engineering workflow with CAP/JNET1 graph planning and Phase 7 reporting");
  const [error, setError] = useState<string | null>(null);
  const [bulkFolder, setBulkFolder] = useState("all");
  const [bulkTargetMode, setBulkTargetMode] = useState<"all" | "folder" | "manual">("all");
  const [bulkManualPoleIds, setBulkManualPoleIds] = useState<string[]>([]);
  const [bulkModelId, setBulkModelId] = useState("");
  const [bulkHeight, setBulkHeight] = useState("");
  const [bulkAzimuth, setBulkAzimuth] = useState("");
  const [bulkIesId, setBulkIesId] = useState("");
  const [bulkWifiNotes, setBulkWifiNotes] = useState("");
  const [bulkWifiRadius, setBulkWifiRadius] = useState("");
  const [bulkClearWifiRadius, setBulkClearWifiRadius] = useState(false);
  const [bulkWifiEnabled, setBulkWifiEnabled] = useState<"unchanged" | "inherit" | "enabled" | "disabled">("unchanged");
  const [bulkCameraId, setBulkCameraId] = useState("");
  const [bulkLensId, setBulkLensId] = useState("");
  const [catalogOpen, setCatalogOpen] = useState(false);
  const [fixtureCatalog, setFixtureCatalog] = useState<FixtureModelCatalog | null>(null);
  const [cameraCatalog, setCameraCatalog] = useState<CameraEquipmentCatalog | null>(null);
  const [iesLibrary, setIesLibrary] = useState<IesLibrary | null>(null);
  const [drawingPriorityArea, setDrawingPriorityArea] = useState(false);
  const [priorityDraft, setPriorityDraft] = useState<Array<[number, number]>>([]);
  const [priorityAreaName, setPriorityAreaName] = useState("Priority area");
  const [selectedPriorityAreaId, setSelectedPriorityAreaId] = useState<string | null>(null);
  const [renamingPriorityArea, setRenamingPriorityArea] = useState(false);
  const [drawingCalculationArea, setDrawingCalculationArea] = useState(false);
  const [calculationDraft, setCalculationDraft] = useState<Array<[number, number]>>([]);
  const [selectedCalculationAreaId, setSelectedCalculationAreaId] = useState<string | null>(null);
  const [editingCalculationArea, setEditingCalculationArea] = useState(false);
  const [calculationAreaName, setCalculationAreaName] = useState("Calculation area 1");
  const [calculationClassification, setCalculationClassification] = useState<CalculationAreaClassification>("ROAD");
  const [calculationPlane, setCalculationPlane] = useState("0");
  const [calculationSpacing, setCalculationSpacing] = useState("2");
  const [calculationMaintenance, setCalculationMaintenance] = useState("1");
  const [drawingWifiArea, setDrawingWifiArea] = useState(false);
  const [wifiDraft, setWifiDraft] = useState<Array<[number, number]>>([]);
  const [wifiAreaName, setWifiAreaName] = useState("Wi-Fi analysis area");
  const [selectedWifiAreaId, setSelectedWifiAreaId] = useState<string | null>(null);
  const [renamingWifiArea, setRenamingWifiArea] = useState(false);
  const [manualCapLongitude, setManualCapLongitude] = useState("");
  const [manualCapLatitude, setManualCapLatitude] = useState("");
  const geometrySignatureRef = useRef("");
  const importRef = useRef<HTMLInputElement>(null);
  const openRef = useRef<HTMLInputElement>(null);

  useEffect(() => {
    void refreshCatalogs().catch((caught) => setError(caught instanceof Error ? caught.message : "Could not load Phase 2 catalogs"));
  }, []);

  useEffect(() => {
    if (!project || !fixtureCatalog || !cameraCatalog) return;
    const signature = JSON.stringify({ id: project.id, projected_crs: project.projected_crs, defaults: project.defaults.pole_height_m, pole_edits: project.pole_edits, priority_areas: project.priority_areas });
    if (geometrySignatureRef.current === signature) return;
    geometrySignatureRef.current = signature;
    const timer = window.setTimeout(() => {
      void recalculateCameraGeometry(project).then((calculated) => {
        if (geometrySignatureRef.current !== signature) return;
        setProject((current) => current?.id === calculated.id ? { ...current, camera_geometry: calculated.camera_geometry } : current);
      }).catch((caught) => setError(caught instanceof Error ? caught.message : "Camera geometry calculation failed"));
    }, 180);
    return () => window.clearTimeout(timer);
  }, [project, fixtureCatalog, cameraCatalog]);

  async function refreshCatalogs() {
    const [fixtures, cameras, ies] = await Promise.all([getFixtureCatalog(), getCameraCatalog(), getIesLibrary()]);
    setFixtureCatalog(fixtures); setCameraCatalog(cameras); setIesLibrary(ies);
  }

  const effectivePoles = useMemo(() => project?.source.poles.map((pole) => effectivePole(project, pole)) ?? [], [project]);
  const selected = useMemo<EffectivePole | null>(() => effectivePoles.find((pole) => pole.id === selectedId) ?? null, [effectivePoles, selectedId]);
  const folders = useMemo(() => Array.from(new Set(effectivePoles.map((pole) => pole.folder_path.join(" / ") || "Unfiled"))).sort(), [effectivePoles]);
  const counts = useMemo(() => ({
    LITE: effectivePoles.filter((pole) => pole.fixtureType === "LITE").length,
    WIFI: effectivePoles.filter((pole) => pole.fixtureType === "WIFI").length,
    SMART: effectivePoles.filter((pole) => pole.fixtureType === "SMART").length,
  }), [effectivePoles]);
  const cameraWarnings = project?.camera_geometry.footprints.filter((footprint) => footprint.enabled && footprint.warnings.length > 0) ?? [];
  const lightingWarnings = project ? Object.values(project.lighting_calculations.results).flatMap((result) => result.warnings.map((warning) => ({ areaId: result.calculation_area_id, warning }))) : [];
  const activeWarnings = (project?.warnings.filter((warning) => warning.severity !== "info").length ?? 0) + cameraWarnings.length + lightingWarnings.length;

  function replaceProject(next: Project, recordHistory = true) {
    if (recordHistory && project) setPast((items) => [...items.slice(-39), project]);
    if (recordHistory) setFuture([]);
    const wifiSafe = project ? invalidateWifiIfSignificant(project, next) : next;
    setProject(project ? invalidateCapIfSignificant(project, wifiSafe) : wifiSafe);
  }

  function mutateProject(updater: (draft: Project) => void) {
    if (!project) return;
    const next = structuredClone(project);
    updater(next);
    next.updated_at = new Date().toISOString();
    replaceProject(invalidateWifiIfSignificant(project, next));
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
      setProject(next); setPast([]); setFuture([]); setSelectedId(null); setBulkManualPoleIds([]);
      setStatus("New local project created - import a customer KML or KMZ");
    });
  }

  async function handleImport(event: ChangeEvent<HTMLInputElement>) {
    const file = event.target.files?.[0];
    event.target.value = "";
    if (!file) return;
    await runAction(async () => {
      const next = await importProjectFile(file);
      setProject(next); setPast([]); setFuture([]); setSelectedId(next.source.poles[0]?.id ?? null); setBulkManualPoleIds([]);
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
      setProject(next); setPast([]); setFuture([]); setSelectedId(next.source.poles[0]?.id ?? null); setBulkManualPoleIds([]);
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
    setProject(invalidateWifiIfSignificant(project, previous));
    setStatus("Undid last project edit");
  }

  function redo() {
    if (!project || !future.length) return;
    const next = future[0];
    setPast((items) => [...items, project].slice(-40));
    setFuture((items) => items.slice(1));
    setProject(invalidateWifiIfSignificant(project, next));
    setStatus("Redid project edit");
  }

  function updatePole(poleId: string, patch: Partial<PoleEdit>) {
    mutateProject((draft) => {
      const existing = draft.pole_edits[poleId] ?? { pole_id: poleId, location_edit_authorized: false };
      const updated = { ...existing, ...patch, pole_id: poleId, fixture_configuration: applyWifiRevision(existing.fixture_configuration, patch.fixture_configuration ?? existing.fixture_configuration), modified_at: new Date().toISOString() };
      draft.pole_edits[poleId] = updated;
      if (lightingSignificantPoleChange(existing, updated)) invalidateLightingResults(draft);
    });
    setStatus("Pole edit staged separately from the customer source");
  }

  function restorePole(poleId: string) {
    mutateProject((draft) => {
      const existing = draft.pole_edits[poleId];
      delete draft.pole_edits[poleId];
      if (existing && lightingSignificantPoleChange(existing, undefined)) invalidateLightingResults(draft);
    });
    setStatus("Restored all source/default values for the selected pole");
  }

  function applyBulkConfiguration() {
    if (!project) return;
    const targetIds = new Set(selectBulkPoleIds(effectivePoles, bulkTargetMode, bulkFolder, bulkManualPoleIds));
    const targets = effectivePoles.filter((pole) => targetIds.has(pole.id));
    if (!targets.length) { setError("Select at least one target pole for the bulk operation"); return; }
    const selectedModel = fixtureCatalog?.fixture_models.find((item) => item.id === bulkModelId && item.active);
    const fixtureRevisions = [...(fixtureCatalog?.fixture_models ?? []), ...(fixtureCatalog?.fixture_model_history ?? [])];
    const models = targets.map((pole) => selectedModel ?? fixtureRevisions.find((item) => item.id === pole.fixtureConfiguration?.fixture_model_id && item.revision === pole.fixtureConfiguration.fixture_model_revision));
    const needsConfiguration = Boolean(bulkIesId || bulkAzimuth || bulkWifiNotes || bulkWifiRadius || bulkClearWifiRadius || bulkWifiEnabled !== "unchanged" || bulkCameraId || bulkLensId);
    if (needsConfiguration && models.some((item) => !item)) { setError("Every selected pole needs an explicit fixture model before applying configuration fields"); return; }
    if ((bulkWifiNotes || bulkWifiRadius || bulkClearWifiRadius || bulkWifiEnabled !== "unchanged") && models.some((item) => !item?.capabilities.wifi)) { setError("Wi-Fi bulk configuration is allowed only when every selected fixture supports Wi-Fi"); return; }
    if (bulkWifiRadius && (!Number.isFinite(Number(bulkWifiRadius)) || Number(bulkWifiRadius) <= 0 || Number(bulkWifiRadius) > 1000)) { setError("Wi-Fi radius must be greater than 0 and at most 1000 m"); return; }
    if ((bulkCameraId || bulkLensId) && models.some((item) => !item?.capabilities.cameras)) { setError("Camera and lens bulk configuration is allowed only when every selected fixture is SMART"); return; }
    if (bulkIesId && models.some((model) => !iesLibrary?.fixture_associations.some((item) => item.active && item.ies_file_id === bulkIesId && item.fixture_model_id === model?.id))) { setError("The selected IES file is not explicitly associated with every target fixture model"); return; }
    mutateProject((draft) => {
      let lightingInputsChanged = false;
      for (const [index, pole] of targets.entries()) {
        const current = draft.pole_edits[pole.id] ?? { pole_id: pole.id, location_edit_authorized: false };
        const model = models[index];
        let config = current.fixture_configuration ? structuredClone(current.fixture_configuration) : current.fixture_configuration;
        if (selectedModel && config?.fixture_model_id !== selectedModel.id) config = { fixture_model_id: selectedModel.id, fixture_model_revision: selectedModel.revision, mounting_template_revision: selectedModel.current_mounting_template_revision, ies_file_id: selectedModel.default_ies_file_id, ies_file_revision: selectedModel.default_ies_file_id ? iesLibrary?.files.find((item) => item.id === selectedModel.default_ies_file_id)?.revision ?? null : null, fixture_azimuth_deg: 0, lighting_properties: {}, wifi_configuration: selectedModel.capabilities.wifi ? {} : null, camera_overrides: {} };
        if (config) {
          if (bulkIesId) { config.ies_file_id = bulkIesId; config.ies_file_revision = iesLibrary?.files.find((item) => item.id === bulkIesId)?.revision ?? null; }
          if (bulkAzimuth) config.fixture_azimuth_deg = Number(bulkAzimuth);
          const wifiPatch: Record<string, unknown> = {};
          if (bulkWifiNotes) wifiPatch.notes = bulkWifiNotes;
          if (bulkClearWifiRadius) wifiPatch.radius_override_m = null;
          else if (bulkWifiRadius) wifiPatch.radius_override_m = Number(bulkWifiRadius);
          if (bulkWifiEnabled !== "unchanged") wifiPatch.enabled = bulkWifiEnabled === "inherit" ? null : bulkWifiEnabled === "enabled";
          if (Object.keys(wifiPatch).length) config.wifi_configuration = applyWifiFields(config.wifi_configuration, wifiPatch);
          if (bulkCameraId || bulkLensId) {
            const template = model?.mounting_template_revisions.find((item) => item.revision === config?.mounting_template_revision);
            for (const slot of template?.slots ?? []) {
              const override = config.camera_overrides[slot.id] ?? { slot_id: slot.id, metadata: {} };
              if (bulkCameraId) { const camera = cameraCatalog?.camera_models.find((item) => item.id === bulkCameraId); override.camera_model_id = bulkCameraId; override.camera_model_revision = camera?.revision ?? null; }
              if (bulkLensId) { const lens = cameraCatalog?.lenses.find((item) => item.id === bulkLensId); override.lens_id = bulkLensId; override.lens_revision = lens?.revision ?? null; }
              config.camera_overrides[slot.id] = override;
            }
          }
        }
        const updated = { ...current, fixture_type: selectedModel?.capability_variant ?? current.fixture_type, height_m: bulkHeight ? Number(bulkHeight) : current.height_m, fixture_configuration: config, modified_at: new Date().toISOString() };
        draft.pole_edits[pole.id] = updated;
        lightingInputsChanged ||= lightingSignificantPoleChange(current, updated);
      }
      if (lightingInputsChanged) invalidateLightingResults(draft);
    });
    setStatus(`Applied only the selected Phase 2 fields to ${targets.length} pole${targets.length === 1 ? "" : "s"}; source coordinates unchanged`);
  }

  function assignFixtureModel(poleId: string, modelId: string) {
    const model = fixtureCatalog?.fixture_models.find((item) => item.id === modelId && item.active);
    if (!model) return;
    updatePole(poleId, {
      fixture_type: model.capability_variant,
      fixture_configuration: {
        fixture_model_id: model.id, fixture_model_revision: model.revision,
        mounting_template_revision: model.current_mounting_template_revision,
        ies_file_id: model.default_ies_file_id, ies_file_revision: model.default_ies_file_id ? iesLibrary?.files.find((item) => item.id === model.default_ies_file_id)?.revision ?? null : null, fixture_azimuth_deg: 0,
        lighting_properties: {}, wifi_configuration: model.capabilities.wifi ? {} : null, camera_overrides: {},
      },
    });
  }

  function toggleLayer(key: LayerKey, enabled: boolean) {
    if (!project) return;
    mutateProject((draft) => { draft.layer_state[key] = enabled; });
  }

  function calculateConceptualWifi() {
    if (!project) return;
    void runAction(async () => { const calculated = await calculateWifiCoverage(project); setProject(calculated); setStatus(`Calculated ${calculated.wifi_coverage.result?.global_statistics.circle_count ?? 0} conceptual Wi-Fi circles`); });
  }
  function runCap(operation: "calculate" | "validate" | "recommend") {
    if (!project) return;
    void runAction(async () => {
      // CAP operations deliberately reload authoritative storage. Persist this complete
      // draft first so a local profile, candidate, or lock cannot be calculated as stale.
      const persisted = await saveProject(project);
      const updated = operation === "calculate" ? await calculateCapPlan(persisted) : operation === "validate" ? await validateCapPlan(persisted) : await recommendCapPlan(persisted);
      replaceProject(updated, false); setStatus(`CAP ${operation} completed as conceptual graph planning`);
    });
  }
  function addSelectedPoleCapCandidate() {
    if (!project || !selected) return;
    const now = new Date().toISOString();
    const candidate = { id: crypto.randomUUID(), kind: "existing_pole" as const, pole_id: selected.id, wgs84_coordinate: null, mounting_confirmed: null, power_confirmed: null, backhaul_confirmed: null, enclosure_confirmed: null, indoor_outdoor: "unknown" as const, mounting_height_m: null, survey_status: "unknown" as const, priority: 1000, notes: "", revision: 1, created_at: now, modified_at: now, prohibited: false, preferred: false, locked_selected: false };
    void runAction(async () => { const persisted = await saveProject(project); const updated = await addCapCandidate(persisted.id, candidate); replaceProject(updated); setStatus(`Added ${selected.displayName} as a separate existing-pole CAP candidate`); });
  }
  function addManualCapCandidate() {
    if (!project) return;
    const longitude = Number(manualCapLongitude), latitude = Number(manualCapLatitude);
    if (!Number.isFinite(longitude) || longitude < -180 || longitude > 180 || !Number.isFinite(latitude) || latitude < -90 || latitude > 90) { setError("Manual non-pole CAP longitude must be -180 to 180 and latitude must be -90 to 90"); return; }
    const now = new Date().toISOString();
    const candidate = { id: crypto.randomUUID(), kind: "manual_non_pole" as const, pole_id: null, wgs84_coordinate: [longitude, latitude] as [number, number], mounting_confirmed: null, power_confirmed: null, backhaul_confirmed: null, enclosure_confirmed: null, indoor_outdoor: "unknown" as const, mounting_height_m: null, survey_status: "unknown" as const, priority: 1000, notes: "Manual non-pole site; never a customer lighting pole.", revision: 1, created_at: now, modified_at: now, prohibited: false, preferred: false, locked_selected: false };
    void runAction(async () => { const persisted = await saveProject(project); const updated = await addCapCandidate(persisted.id, candidate); replaceProject(updated); setManualCapLongitude(""); setManualCapLatitude(""); setStatus("Added a distinct manual non-pole CAP site; no customer pole was created or changed"); });
  }
  function updateCapCandidate(candidate: import("../lib/types").CapCandidateSite, patch: Partial<import("../lib/types").CapCandidateSite>) {
    if (!project) return;
    void runAction(async () => { const persisted = await saveProject(project); const now = new Date().toISOString(); const updated = await replaceCapCandidate(persisted.id, { ...candidate, ...patch, revision: candidate.revision + 1, modified_at: now }); replaceProject(updated); setStatus("Updated CAP candidate feasibility without changing any customer pole"); });
  }
  function removeCapCandidate(candidateId: string) { if (!project) return; void runAction(async () => { const persisted = await saveProject(project); const updated = await deleteCapCandidate(persisted.id, candidateId); replaceProject(updated); setStatus("Removed CAP candidate; no customer pole was changed"); }); }

  function finishWifiArea() {
    if (!project) return;
    let closed: Array<[number, number]>;
    try { closed = closeWifiArea(wifiDraft); } catch (caught) { setError(caught instanceof Error ? caught.message : "Wi-Fi analysis area is invalid"); return; }
    const now = new Date().toISOString();
    mutateProject((draft) => { const index = selectedWifiAreaId ? draft.wifi_analysis_areas.findIndex((item) => item.id === selectedWifiAreaId) : -1; if (index >= 0) { const prior = draft.wifi_analysis_areas[index]; draft.wifi_analysis_areas[index] = { ...prior, name: wifiAreaName.trim() || prior.name, wgs84_coordinates: closed, modified_at: now, polygon_revision: prior.polygon_revision + 1 }; } else draft.wifi_analysis_areas.push({ id: crypto.randomUUID(), name: wifiAreaName.trim() || "Wi-Fi analysis area", wgs84_coordinates: closed, created_at: now, modified_at: now, polygon_revision: 1 }); });
    setWifiDraft([]); setDrawingWifiArea(false); setSelectedWifiAreaId(null); setRenamingWifiArea(false); setStatus("Wi-Fi analysis area saved separately; calculate conceptual Wi-Fi to refresh statistics");
  }

  function startWifiRedraw(areaId: string) { const area = project?.wifi_analysis_areas.find((item) => item.id === areaId); if (!area) return; setSelectedWifiAreaId(area.id); setWifiAreaName(area.name); setWifiDraft([]); setDrawingWifiArea(true); setRenamingWifiArea(false); setStatus("Redrawing Wi-Fi analysis area from an empty draft; saved geometry remains until validation succeeds"); }
  function startWifiRename(areaId: string) { const area = project?.wifi_analysis_areas.find((item) => item.id === areaId); if (!area) return; setSelectedWifiAreaId(area.id); setWifiAreaName(area.name); setDrawingWifiArea(false); setRenamingWifiArea(true); }
  function finishWifiRename() { if (!project || !selectedWifiAreaId || !wifiAreaName.trim()) { setError("Wi-Fi analysis-area name is required"); return; } mutateProject((draft) => { const area = draft.wifi_analysis_areas.find((item) => item.id === selectedWifiAreaId); if (area) { area.name = wifiAreaName.trim(); area.modified_at = new Date().toISOString(); } }); setRenamingWifiArea(false); setSelectedWifiAreaId(null); setStatus("Wi-Fi analysis area renamed; its geometry was preserved"); }
  function deleteWifiArea(areaId: string) { mutateProject((draft) => { draft.wifi_analysis_areas = draft.wifi_analysis_areas.filter((item) => item.id !== areaId); }); setSelectedWifiAreaId(null); setStatus("Wi-Fi analysis area deleted; source, camera, and lighting data unchanged"); }

  function startPriorityArea() {
    setSelectedPriorityAreaId(null);
    setPriorityAreaName(`Priority area ${(project?.priority_areas.length ?? 0) + 1}`);
    setPriorityDraft(emptyPriorityRedrawDraft());
    setRenamingPriorityArea(false);
    setDrawingPriorityArea(true);
    setStatus("Drawing a new priority area; click at least three distinct map vertices");
  }

  function startPriorityRedraw(areaId: string) {
    const area = project?.priority_areas.find((item) => item.id === areaId);
    if (!area) return;
    setSelectedPriorityAreaId(area.id); setPriorityAreaName(area.name);
    setPriorityDraft(emptyPriorityRedrawDraft()); setRenamingPriorityArea(false); setDrawingPriorityArea(true);
    setStatus("Redrawing priority-area geometry from an empty draft; the saved polygon remains until replacement succeeds");
  }

  function startPriorityRename(areaId: string) {
    const area = project?.priority_areas.find((item) => item.id === areaId);
    if (!area) return;
    setSelectedPriorityAreaId(area.id); setPriorityAreaName(area.name); setPriorityDraft([]); setDrawingPriorityArea(false); setRenamingPriorityArea(true);
  }

  function finishPriorityRename() {
    if (!project || !selectedPriorityAreaId) return;
    try {
      mutateProject((draft) => { const index = draft.priority_areas.findIndex((item) => item.id === selectedPriorityAreaId); if (index >= 0) draft.priority_areas[index] = renamePriorityArea(draft.priority_areas[index], priorityAreaName, new Date().toISOString()); });
      setRenamingPriorityArea(false); setSelectedPriorityAreaId(null); setStatus("Priority area renamed; its saved geometry was preserved exactly");
    } catch (caught) { setError(caught instanceof Error ? caught.message : "Could not rename priority area"); }
  }

  function finishPriorityArea() {
    if (!project) return;
    let closed: Array<[number, number]>;
    try { closed = validateAndClosePriorityRing(priorityDraft); }
    catch (caught) { setError(caught instanceof Error ? caught.message : "The replacement priority area is invalid"); return; }
    const now = new Date().toISOString();
    mutateProject((draft) => {
      const index = selectedPriorityAreaId ? draft.priority_areas.findIndex((item) => item.id === selectedPriorityAreaId) : -1;
      if (index >= 0) draft.priority_areas[index] = { ...draft.priority_areas[index], wgs84_coordinates: closed, modified_at: now };
      else draft.priority_areas.push({ id: crypto.randomUUID(), name: priorityAreaName.trim() || "Priority area", wgs84_coordinates: closed, created_at: now, modified_at: now });
    });
    setDrawingPriorityArea(false); setPriorityDraft([]); setSelectedPriorityAreaId(null); setRenamingPriorityArea(false);
    setStatus("Priority area saved as project user data; projected intersection summary recalculating");
  }

  function deletePriorityArea(areaId: string) {
    mutateProject((draft) => { draft.priority_areas = draft.priority_areas.filter((item) => item.id !== areaId); });
    setSelectedPriorityAreaId(null); setStatus("Priority area deleted; source poles and coordinates unchanged");
  }

  function loadCalculationForm(areaId: string | null) {
    const area = project?.calculation_areas.find((item) => item.id === areaId);
    setSelectedCalculationAreaId(area?.id ?? null);
    setCalculationAreaName(area?.name ?? `Calculation area ${(project?.calculation_areas.length ?? 0) + 1}`);
    setCalculationClassification(area?.classification ?? "ROAD");
    setCalculationPlane(String(area?.calculation_plane_elevation_m ?? 0));
    setCalculationSpacing(String(area?.grid_spacing_m ?? 2));
    setCalculationMaintenance(String(area?.maintenance_factor ?? 1));
  }

  function startCalculationArea() {
    loadCalculationForm(null); setCalculationDraft([]); setDrawingCalculationArea(true); setEditingCalculationArea(true);
    setDrawingPriorityArea(false); setStatus("Drawing a new lighting calculation area from an empty draft");
  }

  function editCalculationArea(areaId: string, redraw = false) {
    loadCalculationForm(areaId); setCalculationDraft([]); setDrawingCalculationArea(redraw); setEditingCalculationArea(true);
    setDrawingPriorityArea(false); setStatus(redraw ? "Redrawing from an empty draft; the prior valid lighting polygon remains stored until validation succeeds" : "Editing calculation-area settings; source and camera polygons remain unchanged");
  }

  function cancelCalculationArea() {
    setCalculationDraft([]); setDrawingCalculationArea(false); setEditingCalculationArea(false);
  }

  function finishCalculationArea() {
    if (!project) return;
    const existing = project.calculation_areas.find((item) => item.id === selectedCalculationAreaId);
    const points = drawingCalculationArea ? calculationDraft : existing?.wgs84_coordinates.slice(0, -1) ?? [];
    try {
      const validated = validateCalculationAreaDraft(points, { name: calculationAreaName, classification: calculationClassification, calculation_plane_elevation_m: calculationPlane, grid_spacing_m: calculationSpacing, maintenance_factor: calculationMaintenance });
      const now = new Date().toISOString();
      mutateProject((draft) => {
        const index = selectedCalculationAreaId ? draft.calculation_areas.findIndex((item) => item.id === selectedCalculationAreaId) : -1;
        if (index >= 0) {
          const prior = draft.calculation_areas[index];
          draft.calculation_areas[index] = { ...prior, ...validated, modified_at: now, calculation_state: staleCalculationState(prior.calculation_state, drawingCalculationArea) as CalculationArea["calculation_state"] };
          delete draft.lighting_calculations.results[prior.id];
        } else {
          const id = crypto.randomUUID();
          draft.calculation_areas.push({ id, ...validated, created_at: now, modified_at: now, calculation_state: { status: "not-calculated", polygon_revision: 1, last_calculated_at: null, warnings: [], assumptions: [], provenance: {} } });
          setSelectedCalculationAreaId(id);
        }
      });
      setCalculationDraft([]); setDrawingCalculationArea(false); setEditingCalculationArea(false);
      setStatus(existing ? "Calculation area updated and prior derived result marked stale" : "Lighting calculation area created separately from camera priority areas");
    } catch (caught) { setError(caught instanceof Error ? caught.message : "Calculation area is invalid"); }
  }

  function deleteCalculationArea(areaId: string) {
    mutateProject((draft) => { draft.calculation_areas = draft.calculation_areas.filter((item) => item.id !== areaId); delete draft.lighting_calculations.results[areaId]; });
    if (selectedCalculationAreaId === areaId) setSelectedCalculationAreaId(null);
    setStatus("Calculation area and its derived result deleted; source poles and camera priority areas unchanged");
  }

  async function calculateSelectedArea() {
    if (!project || !selectedCalculationAreaId) { setError("Select a lighting calculation area first"); return; }
    await runAction(async () => {
      const calculated = await calculateLighting(project, selectedCalculationAreaId);
      setProject(calculated); setStatus(`Calculated ${calculated.lighting_calculations.results[selectedCalculationAreaId]?.statistics.point_count ?? 0} deterministic lighting points`);
    });
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
          <button className="tool-button" onClick={() => setCatalogOpen(true)}>Catalogs</button>
          <button className="tool-button" onClick={() => startPriorityArea()} disabled={!project || drawingPriorityArea || drawingCalculationArea}>Draw Priority Area</button>
          <button className="tool-button" onClick={startCalculationArea} disabled={!project || drawingCalculationArea || drawingPriorityArea || drawingWifiArea}>Draw Calculation Area</button>
          <button className="tool-button" onClick={() => { setDrawingWifiArea(true); setWifiDraft([]); setDrawingPriorityArea(false); setDrawingCalculationArea(false); }} disabled={!project || drawingPriorityArea || drawingCalculationArea}>Draw Wi-Fi analysis area</button>
          <button className="tool-button primary" onClick={calculateConceptualWifi} disabled={!project || busy}>Calculate conceptual Wi-Fi</button>
          <button className="tool-button primary" onClick={() => void calculateSelectedArea()} disabled={!project || !selectedCalculationAreaId || busy}>Calculate Lighting</button>
          <button className="tool-button" onClick={() => runCap("recommend")} disabled={!capOperationEnabled(project, "recommend") || busy}>Recommend CAP</button>
          <button className="tool-button" onClick={exportBoth} disabled={!project || busy}>Export Project</button>
          <button className="tool-button primary" onClick={() => setLeftCollapsed(false)} disabled={!project || busy}>Report Package</button>
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
                <div className="section-heading"><h3>Phase 6 — CAP / JNET1 graph planning</h3><span className="helper">Blocker-first</span></div>
                <p className="lighting-disclaimer">{CAP_DISCLAIMER}</p>
                {project ? <>
                  <p className="helper">Product, variant, band/jurisdiction, explicit LITE/WIFI/SMART node dispositions, design limits, counting, redundancy, and surveyed candidates remain separate user inputs.</p>
                  {capBlockers(project.cap_planning_inputs).length ? <div className="warning-card"><strong>CAP preflight blockers</strong><p>{capBlockers(project.cap_planning_inputs).join(", ")}</p></div> : <div className="warning-card info">Preflight complete for the selected test/project inputs.</div>}
                  <div className="form-grid"><div className="field"><label>Operation mode</label><select value={project.cap_planning_inputs.profile.operation_mode} onChange={(event) => mutateProject((draft) => { draft.cap_planning_inputs.profile.operation_mode = event.target.value as "validate" | "recommend"; })}><option value="validate">Validate explicit CAP selection</option><option value="recommend">Recommend from approved pool</option></select></div><div className="field"><label>Mode permission</label><select value={project.cap_planning_inputs.profile.mode_permission} onChange={(event) => mutateProject((draft) => { draft.cap_planning_inputs.profile.mode_permission = event.target.value as "validate_only" | "recommend_from_approved_pool" | "unknown"; })}><option value="unknown">Unknown — blocks planning</option><option value="validate_only">Validate only</option><option value="recommend_from_approved_pool">Recommend from approved pool</option></select></div><div className="field"><label>Gateway appliance counting</label><select value={String(project.cap_planning_inputs.profile.gateway_appliance_counting.value ?? "")} onChange={(event) => mutateProject((draft) => { const field = draft.cap_planning_inputs.profile.gateway_appliance_counting; field.value = event.target.value || null; field.status = event.target.value ? "known" : "unknown"; field.source = event.target.value ? "TEST-ONLY user-entered project input" : null; field.applicability = event.target.value ? "test-only" : null; field.classification = event.target.value ? "user_approved_assumption" : "unknown"; })}><option value="">Unknown — blocks planning</option><option value="included">Included in per-CAP node count</option><option value="excluded">Excluded from per-CAP node count</option></select></div><div className="field"><label>Co-located fixture counting</label><select value={String(project.cap_planning_inputs.profile.colocated_fixture_counting.value ?? "")} onChange={(event) => mutateProject((draft) => { const field = draft.cap_planning_inputs.profile.colocated_fixture_counting; field.value = event.target.value || null; field.status = event.target.value ? "known" : "unknown"; field.source = event.target.value ? "TEST-ONLY user-entered project input" : null; field.applicability = event.target.value ? "test-only" : null; field.classification = event.target.value ? "user_approved_assumption" : "unknown"; })}><option value="">Unknown — blocks planning</option><option value="distinct_managed_node_once">Distinct managed fixture node once</option><option value="merged_not_separate">Merged, not a separate fixture node</option></select></div><div className="field"><label>Redundancy policy</label><select value={String(project.cap_planning_inputs.profile.redundancy.value ?? "")} onChange={(event) => mutateProject((draft) => { const field = draft.cap_planning_inputs.profile.redundancy; field.value = event.target.value || null; field.status = event.target.value ? "known" : "unknown"; field.source = event.target.value ? "TEST-ONLY user-entered project input" : null; field.applicability = event.target.value ? "test-only" : null; field.classification = event.target.value ? "user_approved_assumption" : "unknown"; })}><option value="">Unknown — blocks planning</option><option value="single_allowed_with_warning">Single allowed with warning</option><option value="n_plus_one_validation">N+1 graph validation</option><option value="user_supplied_only">User supplied only</option></select></div></div>
                  <div className="form-grid">{(["LITE", "WIFI", "SMART"] as FixtureType[]).map((type) => <div className="field" key={type}><label>{type} node disposition</label><select value={project.cap_planning_inputs.profile.node_policy[type]} onChange={(event) => mutateProject((draft) => { draft.cap_planning_inputs.profile.node_policy[type] = event.target.value as "node" | "non_node" | "unknown"; })}><option value="unknown">Unknown — blocks planning</option><option value="node">Node</option><option value="non_node">Non-node</option></select></div>)}</div>
                  <div className="form-grid">{(["product_mapping", "variant", "band_and_jurisdiction", "link_distance_m", "node_limit", "child_limit", "hop_limit"] as const).map((field) => <div className="field" key={field}><label>{field.replaceAll("_", " ")} · provenance-bearing</label><input value={String(project.cap_planning_inputs.profile[field].value ?? "")} onChange={(event) => mutateProject((draft) => { const value = event.target.value; const target = draft.cap_planning_inputs.profile[field]; target.value = field.endsWith("limit") || field === "link_distance_m" ? (value === "" ? null : Number(value)) : value || null; target.status = value ? "known" : "unknown"; target.source = value ? "user-entered project input" : null; target.applicability = value ? "project planning" : null; target.classification = value ? "user_approved_assumption" : "unknown"; })} /></div>)}</div>
                  <div className="button-row"><button className="quiet-button" onClick={addSelectedPoleCapCandidate} disabled={!selected || busy}>Add selected pole as CAP site</button><button className="quiet-button" disabled={!selected || busy} onClick={() => selected && mutateProject((draft) => { const nodeId = `fixture/${selected.id}`; const ids = draft.cap_planning_inputs.excluded_node_ids; draft.cap_planning_inputs.excluded_node_ids = ids.includes(nodeId) ? ids.filter((id) => id !== nodeId) : [...ids, nodeId]; })}>{selected && project.cap_planning_inputs.excluded_node_ids.includes(`fixture/${selected.id}`) ? "Include current CAP node" : "Exclude current CAP node"}</button></div>
                  <div className="form-grid"><div className="field"><label htmlFor="manual-cap-longitude">Manual non-pole longitude</label><input id="manual-cap-longitude" type="number" min="-180" max="180" step="any" value={manualCapLongitude} onChange={(event) => setManualCapLongitude(event.target.value)} /></div><div className="field"><label htmlFor="manual-cap-latitude">Manual non-pole latitude</label><input id="manual-cap-latitude" type="number" min="-90" max="90" step="any" value={manualCapLatitude} onChange={(event) => setManualCapLatitude(event.target.value)} /></div></div><div className="button-row"><button className="quiet-button" onClick={addManualCapCandidate} disabled={busy}>Add distinct manual non-pole CAP site</button></div>
                  {project.cap_planning_inputs.candidates.map((candidate) => <div className="priority-row" key={candidate.id}><strong>{candidate.kind === "existing_pole" ? `Pole ${candidate.pole_id}` : "Manual non-pole site"}</strong><span>mounting {String(candidate.mounting_confirmed)} · power {String(candidate.power_confirmed)} · backhaul {String(candidate.backhaul_confirmed)} · survey {candidate.survey_status} · priority {candidate.priority}</span><div><button className="quiet-button" onClick={() => updateCapCandidate(candidate, { mounting_confirmed: true, power_confirmed: true, backhaul_confirmed: true, enclosure_confirmed: true, indoor_outdoor: "outdoor", survey_status: "confirmed", notes: "TEST-ONLY feasibility values; not approved site engineering." })}>Mark test-only feasible</button><button className="quiet-button" onClick={() => updateCapCandidate(candidate, { preferred: !candidate.preferred })}>{candidate.preferred ? "Remove preference" : "Prefer"}</button><button className="quiet-button" onClick={() => updateCapCandidate(candidate, { prohibited: !candidate.prohibited })}>{candidate.prohibited ? "Allow" : "Prohibit"}</button><button className="quiet-button" onClick={() => updateCapCandidate(candidate, { locked_selected: !candidate.locked_selected })}>{candidate.locked_selected ? "Unlock selected" : "Lock selected"}</button><button className="quiet-button" disabled={!selected} onClick={() => selected && mutateProject((draft) => { const nodeId = `fixture/${selected.id}`; const gatewayId = `gateway/${candidate.id}`; const locks = draft.cap_planning_inputs.primary_assignment_locks; if (locks[nodeId] === gatewayId) delete locks[nodeId]; else locks[nodeId] = gatewayId; })}>{selected && project.cap_planning_inputs.primary_assignment_locks[`fixture/${selected.id}`] === `gateway/${candidate.id}` ? "Unlock current node assignment" : "Lock current node to this CAP"}</button><button className="quiet-button" disabled={!selected} onClick={() => selected && mutateProject((draft) => { const nodeId = `fixture/${selected.id}`; const gatewayId = `gateway/${candidate.id}`; const locks = draft.cap_planning_inputs.parent_locks; if (locks[nodeId] === gatewayId) delete locks[nodeId]; else locks[nodeId] = gatewayId; })}>{selected && project.cap_planning_inputs.parent_locks[`fixture/${selected.id}`] === `gateway/${candidate.id}` ? "Unlock current parent" : "Lock current parent to this CAP"}</button><button className="quiet-button" onClick={() => mutateProject((draft) => { const ids = draft.cap_planning_inputs.excluded_candidate_ids; draft.cap_planning_inputs.excluded_candidate_ids = ids.includes(candidate.id) ? ids.filter((id) => id !== candidate.id) : [...ids, candidate.id]; })}>{project.cap_planning_inputs.excluded_candidate_ids.includes(candidate.id) ? "Include candidate" : "Exclude candidate"}</button><button className="quiet-button" onClick={() => removeCapCandidate(candidate.id)}>Delete site</button></div></div>)}
                  <div className="button-row"><button className="quiet-button" onClick={() => runCap("calculate")} disabled={!capOperationEnabled(project, "calculate") || busy}>Calculate / rank</button><button className="quiet-button" onClick={() => runCap("validate")} disabled={!capOperationEnabled(project, "validate") || busy}>Validate</button><button className="quiet-button" onClick={() => runCap("recommend")} disabled={!capOperationEnabled(project, "recommend") || busy}>Recommend</button></div>
                  <p>{project.cap_planning_inputs.candidates.length} explicit CAP candidate sites · {project.cap_recommendations.selected_candidate_ids.length} selected.</p>
                  {project.cap_calculations.result && <details className="lighting-provenance"><summary>CAP topology, score trace, and provenance</summary><p>Fingerprint {project.cap_calculations.calculation_input_sha256} · CRS {project.cap_calculations.result.projected_crs}</p>{project.cap_calculations.result.assignments.map((item) => <p key={item.node_id}>{item.node_id} → {item.parent_id} · hop {item.hop} · {item.distance_m.toFixed(6)} m · distance-qualified conceptual link; not RF-predicted</p>)}{project.cap_calculations.result.warnings.map((warning) => <p key={warning}>{warning}</p>)}</details>}
                </> : <p className="helper">Import or create a project to preserve unknown CAP inputs and inspect blockers.</p>}
              </section>
              {project && (
                <ReportPanel
                  key={`${project.id}:${project.updated_at}`}
                  project={project}
                  busy={busy}
                  onBusy={setBusy}
                  onStatus={setStatus}
                  onError={setError}
                  onReportMetadataApplied={(next) => {
                    setProject((current) =>
                      current
                        ? applyLastReportMetadata(current, next.last_report, next.updated_at) ?? current
                        : next,
                    );
                  }}
                />
              )}
              <section className="section">
                <p className="project-name">{project?.name ?? "No project loaded"}</p>
                <div className="project-meta">{project?.source.file ? `${project.source.file.filename} · ${project.source.poles.length} source poles` : "Create a project or import a customer layout."}</div>
                <div className="counts-grid">{(["LITE", "WIFI", "SMART"] as FixtureType[]).map((fixture) => <div className={`count-card ${fixture.toLowerCase()}`} key={fixture}><span>{fixture}</span><strong>{counts[fixture]}</strong></div>)}</div>
              </section>
              <section className="section">
                <div className="section-heading"><h3>Map layers</h3><span className="helper">Phase 4</span></div>
                {LAYERS.map((layer) => <label className="layer-row" key={layer.key}><input type="checkbox" checked={Boolean(project?.layer_state[layer.key])} disabled={!project || (layer.key === "wifi_coverage" && !project?.wifi_coverage.result)} onChange={(event) => toggleLayer(layer.key, event.target.checked)} /><span className="layer-dot" style={{ "--dot": layer.color } as CSSProperties} /><span>{layer.label}</span>{layer.phase && <span className="phase-tag">P{layer.phase}</span>}</label>)}
                <div className="geometry-metrics"><strong>{project?.camera_geometry.footprints.filter((item) => item.valid).length ?? 0} valid footprints</strong><span>{project?.camera_geometry.overlaps.length ?? 0} overlap pairs · {(project?.camera_geometry.overlaps.reduce((sum, item) => sum + item.intersection_area_m2, 0) ?? 0).toFixed(1)} m² summed pairwise overlap</span><small>Camera 1 purple · Camera 2 cyan · overlap pink · priority area amber</small></div>
              </section>
              <section className="section">
                <div className="section-heading"><h3>Phase 5 — Conceptual Wi-Fi</h3><span className="helper">Projected geometry only</span></div>
                <p className="lighting-disclaimer">Conceptual geometric visualization only; not verified RF coverage, performance, capacity, service quality, or standards compliance.</p>
                <div className="field"><label htmlFor="wifi-default-radius">Project default radius (m) · engineering assumption</label><input id="wifi-default-radius" type="number" min="0.01" max="1000" step="0.01" value={project?.defaults.wifi_radius_m ?? 30} onChange={(event) => { const value = Number(event.target.value); if (Number.isFinite(value) && value > 0 && value <= 1000) mutateProject((draft) => { draft.defaults.wifi_radius_m = value; }); }} /><small>Source/default: 30 m · 0 &lt; radius ≤ 1000 m</small></div>
                {drawingWifiArea && <div className="warning-card info"><div className="field full"><label htmlFor="wifi-area-name">Analysis-area name</label><input id="wifi-area-name" value={wifiAreaName} onChange={(event) => setWifiAreaName(event.target.value)} /></div><p>Replacement/new area starts empty; {wifiDraft.length} vertices.</p><button className="quiet-button" onClick={finishWifiArea}>Save Wi-Fi area</button><button className="quiet-button" onClick={() => { setDrawingWifiArea(false); setWifiDraft([]); }}>Cancel</button></div>}
                {renamingWifiArea && <div className="warning-card info"><div className="field full"><label htmlFor="wifi-rename">Area name</label><input id="wifi-rename" value={wifiAreaName} onChange={(event) => setWifiAreaName(event.target.value)} /></div><button className="quiet-button" onClick={finishWifiRename}>Save name</button><button className="quiet-button" onClick={() => { setRenamingWifiArea(false); setSelectedWifiAreaId(null); }}>Cancel</button></div>}
                {project?.wifi_coverage.result ? <><p>{project.wifi_coverage.result.global_statistics.circle_count} circles · individual {project.wifi_coverage.result.global_statistics.individual_area_m2.toFixed(6)} m² · union {project.wifi_coverage.result.global_statistics.union_covered_area_m2.toFixed(6)} m² · overlap {project.wifi_coverage.result.global_statistics.overlap_area_m2.toFixed(6)} m²</p><p>Aggregate pairwise overlap {project.wifi_coverage.result.global_statistics.pairwise_overlap_area_m2.toFixed(6)} m² · multiply-covered union {project.wifi_coverage.result.global_statistics.multiply_covered_union_area_m2.toFixed(6)} m² · {project.wifi_coverage.result.global_statistics.overlap_pair_count} overlap pairs</p>{wifiBoundaryGapMessage(project.wifi_coverage.result) && <p className="helper">{wifiBoundaryGapMessage(project.wifi_coverage.result)}</p>}{project.wifi_coverage.result.analysis_area_statistics.map((stats) => <div className="calculation-row" key={stats.analysis_area_id}><strong>{stats.analysis_area_name}</strong><span>{stats.covered_area_m2.toFixed(6)} m² covered ({stats.covered_percentage.toFixed(1)}%) · {stats.uncovered_area_m2.toFixed(6)} m² uncovered ({stats.uncovered_percentage.toFixed(1)}%) · boundary {stats.boundary_covered_length_m.toFixed(6)} m ({stats.boundary_covered_percentage.toFixed(1)}%)</span></div>)}<details className="lighting-provenance"><summary>Wi-Fi assumptions and provenance</summary><p>Model {project.wifi_coverage.result.model_version} · CRS {project.wifi_coverage.result.projected_crs} · approximation {project.wifi_coverage.result.approximation_resolution} segments/quarter<br />Fingerprint {project.wifi_coverage.result.calculation_input_sha256}</p>{project.wifi_coverage.result.assumptions.map((assumption) => <p key={assumption}>{assumption}</p>)}{project.wifi_coverage.result.circles.map((circle) => <p key={circle.id}><strong>{circle.pole_id}</strong> · source {circle.source_wgs84_coordinate.join(", ")} · effective {circle.effective_wgs84_coordinate.join(", ")} · radius {circle.effective_radius_m} m · enabled {String(circle.enabled)}</p>)}{project.wifi_coverage.result.warnings.map((warning) => <div className="warning-card" key={warning}>{warning}</div>)}<p>{project.wifi_coverage.result.disclaimer}</p></details></> : <><p className="helper">No result yet. Circles and global metrics are available after calculation.</p><p className="helper">{wifiBoundaryGapMessage(null)}</p></>}
                {project?.wifi_analysis_areas.map((area) => <div className={`priority-row ${selectedWifiAreaId === area.id ? "selected" : ""}`} key={area.id}><strong>{area.name}</strong><span>{area.wgs84_coordinates.length - 1} vertices · revision {area.polygon_revision}</span><div><button className="quiet-button" onClick={() => setSelectedWifiAreaId(area.id)}>Select</button><button className="quiet-button" onClick={() => startWifiRename(area.id)}>Rename</button><button className="quiet-button" onClick={() => startWifiRedraw(area.id)}>Redraw</button><button className="quiet-button" onClick={() => deleteWifiArea(area.id)}>Delete</button></div></div>)}
              </section>
              <section className="section">
                <div className="section-heading"><h3>Lighting calculation areas</h3><span className="helper">Separate from camera</span></div>
                <p className="lighting-disclaimer">Not independently validated against AGi32 or another professional photometric reference tool.</p>
                {editingCalculationArea && <div className="warning-card info"><div className="form-grid">
                  <div className="field full"><label htmlFor="calculation-area-name">Name</label><input id="calculation-area-name" value={calculationAreaName} onChange={(event) => setCalculationAreaName(event.target.value)} /></div>
                  <div className="field"><label htmlFor="calculation-classification">Classification</label><select id="calculation-classification" value={calculationClassification} onChange={(event) => setCalculationClassification(event.target.value as CalculationAreaClassification)}><option value="ROAD">Road</option><option value="SIDEWALK">Sidewalk</option><option value="PARKING">Parking</option><option value="OTHER">Other</option></select></div>
                  <div className="field"><label htmlFor="calculation-plane">Plane elevation (m)</label><input id="calculation-plane" type="number" value={calculationPlane} onChange={(event) => setCalculationPlane(event.target.value)} /></div>
                  <div className="field"><label htmlFor="calculation-spacing">Grid spacing (m)</label><input id="calculation-spacing" type="number" min="0.01" max="1000" value={calculationSpacing} onChange={(event) => setCalculationSpacing(event.target.value)} /></div>
                  <div className="field"><label htmlFor="calculation-maintenance">Maintenance factor</label><input id="calculation-maintenance" type="number" min="0.01" max="1" step="0.01" value={calculationMaintenance} onChange={(event) => setCalculationMaintenance(event.target.value)} /></div>
                </div>{drawingCalculationArea && <p>{selectedCalculationAreaId ? "Replacement begins empty; the stored polygon is preserved until this draft validates." : "New polygon"} · {calculationDraft.length} vertices.</p>}<button className="quiet-button" onClick={finishCalculationArea}>{drawingCalculationArea ? "Validate and save polygon" : "Save details"}</button><button className="quiet-button" onClick={cancelCalculationArea}>Cancel</button></div>}
                {project?.calculation_areas.map((area) => { const result = project.lighting_calculations.results[area.id]; const stats = result?.statistics; return <div className={`calculation-row ${selectedCalculationAreaId === area.id ? "selected" : ""}`} key={area.id}><strong>{area.name} · {area.classification}</strong><span>{stats ? `${stats.point_count} points · Eavg ${stats.average_illuminance_lux?.toFixed(2) ?? "—"} lx · Emin ${stats.minimum_illuminance_lux?.toFixed(2) ?? "—"} lx · Emax ${stats.maximum_illuminance_lux?.toFixed(2) ?? "—"} lx` : "Not calculated"}</span>{stats && <small>Emin/Eavg {stats.emin_over_eavg?.toFixed(3) ?? "—"} · Emin/Emax {stats.emin_over_emax?.toFixed(3) ?? "—"} · {result.contributing_fixture_count} fixtures</small>}<div><button className="quiet-button" onClick={() => setSelectedCalculationAreaId(area.id)}>Select</button><button className="quiet-button" onClick={() => editCalculationArea(area.id)}>Edit</button><button className="quiet-button" onClick={() => editCalculationArea(area.id, true)}>Redraw</button><button className="quiet-button" onClick={() => deleteCalculationArea(area.id)}>Delete</button></div>{result && <><p className="lighting-disclaimer">{result.disclaimer}</p><p className="helper">Approved simplified direct-light model; not a standards-compliance determination.</p><details className="lighting-provenance"><summary>Calculation and fixture provenance</summary><p>Model {result.calculation_model_version} · CRS {result.projected_crs} · polygon r{result.polygon_revision}<br />Grid {result.statistics.grid_spacing_m} m · origin {result.grid_origin_m.join(", ")} m · {result.grid_anchor_policy}<br />Boundary {result.boundary_policy} · plane {area.calculation_plane_elevation_m} m · maintenance factor {area.maintenance_factor}</p>{result.fixture_provenance.map((fixture) => <p key={fixture.pole_id}><strong>{fixture.pole_id}</strong><br />{fixture.fixture_model_id} r{fixture.fixture_model_revision} · {fixture.ies_original_filename} r{fixture.ies_file_revision}<br />SHA-256 {fixture.ies_sha256} · parsed Type {fixture.ies_parsed_metadata.photometric_type ?? "—"}, {fixture.ies_parsed_metadata.input_watts ?? "—"} W, {fixture.ies_parsed_metadata.vertical_angle_count ?? "—"}×{fixture.ies_parsed_metadata.horizontal_angle_count ?? "—"} angles<br />Height {fixture.mounting_height_m} m · azimuth {fixture.fixture_azimuth_deg}° · origin {fixture.origin_projected_m.join(", ")} m{fixture.warnings.length ? <><br />Warnings: {fixture.warnings.join(" ")}</> : null}</p>)}</details>{result.warnings.map((warning) => <div className="warning-card" key={warning}>{warning}</div>)}</>}</div>; })}
                {!project?.calculation_areas.length && <p className="helper">Draw a Road, Sidewalk, Parking, or Other polygon. Defaults: 0.0 m plane, 2.0 m grid, maintenance factor 1.0.</p>}
              </section>
              <section className="section">
                <div className="section-heading"><h3>Priority areas</h3><span className="helper">Geometric only</span></div>
                {drawingPriorityArea && <div className="warning-card info"><p>{selectedPriorityAreaId ? "Replacement geometry starts empty. The saved polygon remains unchanged unless this replacement validates." : "New priority area"}</p><p>{priorityDraft.length} vertices. Click the map to add at least three distinct points.</p><button className="quiet-button" onClick={finishPriorityArea}>Save polygon</button><button className="quiet-button" onClick={() => { setDrawingPriorityArea(false); setPriorityDraft([]); setSelectedPriorityAreaId(null); }}>Cancel</button></div>}
                {renamingPriorityArea && <div className="warning-card info"><div className="field full"><label htmlFor="priority-name">Area name</label><input id="priority-name" value={priorityAreaName} onChange={(event) => setPriorityAreaName(event.target.value)} /></div><p>Renaming preserves every saved vertex.</p><button className="quiet-button" onClick={finishPriorityRename}>Save name</button><button className="quiet-button" onClick={() => { setRenamingPriorityArea(false); setSelectedPriorityAreaId(null); }}>Cancel</button></div>}
                {project?.priority_areas.map((area) => { const summary = project.camera_geometry.priority_area_summaries.find((item) => item.priority_area_id === area.id); return <div className="priority-row" key={area.id}><strong>{area.name}</strong><span>{summary ? `${summary.covered_area_m2.toFixed(1)} / ${summary.area_m2.toFixed(1)} m² · ${summary.covered_percentage.toFixed(1)}%` : "Awaiting valid geometry"}</span><div><button className="quiet-button" onClick={() => startPriorityRename(area.id)}>Rename</button><button className="quiet-button" onClick={() => startPriorityRedraw(area.id)}>Redraw</button><button className="quiet-button" onClick={() => deletePriorityArea(area.id)}>Delete</button></div></div>; })}
                {!project?.priority_areas.length && <p className="helper">Draw project-specific polygons to summarize geometric camera intersections.</p>}
              </section>
              <section className="section">
                <div className="section-heading"><h3>Bulk assignment</h3></div>
                <div className="field full"><label htmlFor="bulk-target-mode">Target poles</label><select id="bulk-target-mode" value={bulkTargetMode} onChange={(event) => setBulkTargetMode(event.target.value as "all" | "folder" | "manual")} disabled={!project}><option value="all">All imported poles</option><option value="folder">One source folder</option><option value="manual">Manually selected poles</option></select></div>
                {bulkTargetMode === "folder" && <div className="field full" style={{ marginTop: 8 }}><label htmlFor="bulk-folder">Target folder</label><select id="bulk-folder" value={bulkFolder} onChange={(event) => setBulkFolder(event.target.value)} disabled={!project}>{folders.map((folder) => <option key={folder}>{folder}</option>)}</select></div>}
                {bulkTargetMode === "manual" && <div className="future-card" style={{ marginTop: 8 }}><strong>{bulkManualPoleIds.length} manually selected</strong><br />Click a pole on the map, then add or remove it here.<button type="button" className="quiet-button restore-button" disabled={!selectedId} onClick={() => selectedId && setBulkManualPoleIds((ids) => ids.includes(selectedId) ? ids.filter((id) => id !== selectedId) : [...ids, selectedId])}>{selectedId && bulkManualPoleIds.includes(selectedId) ? "Remove current pole from bulk selection" : "Add current pole to bulk selection"}</button>{bulkManualPoleIds.length > 0 && <button type="button" className="quiet-button restore-button" onClick={() => setBulkManualPoleIds([])}>Clear manual selection</button>}</div>}
                <div className="field full" style={{ marginTop: 8 }}><label htmlFor="bulk-model">Explicit fixture model</label><select id="bulk-model" value={bulkModelId} onChange={(event) => setBulkModelId(event.target.value)} disabled={!project}><option value="">Choose model…</option>{fixtureCatalog?.fixture_models.filter((item) => item.active).map((model) => <option value={model.id} key={model.id}>{model.display_name}</option>)}</select></div>
                <div className="bulk-row" style={{ marginTop: 8 }}><div className="field"><label htmlFor="bulk-height">Height (m)</label><input id="bulk-height" type="number" min="0.1" max="100" value={bulkHeight} placeholder="Unchanged" onChange={(event) => setBulkHeight(event.target.value)} /></div><div className="field"><label htmlFor="bulk-azimuth">Azimuth (°)</label><input id="bulk-azimuth" type="number" min="0" max="359.999" value={bulkAzimuth} placeholder="Unchanged" onChange={(event) => setBulkAzimuth(event.target.value)} /></div></div>
                <div className="field full" style={{ marginTop: 8 }}><label htmlFor="bulk-ies">IES file</label><select id="bulk-ies" value={bulkIesId} onChange={(event) => setBulkIesId(event.target.value)}><option value="">Unchanged</option>{iesLibrary?.files.filter((item) => item.active).map((item) => <option value={item.id} key={item.id}>{item.original_filename}</option>)}</select></div>
                <div className="field full" style={{ marginTop: 8 }}><label htmlFor="bulk-wifi-radius">Wi-Fi radius override (m)</label><input id="bulk-wifi-radius" type="number" min="0.01" max="1000" step="0.01" value={bulkWifiRadius} placeholder="Unchanged" onChange={(event) => setBulkWifiRadius(event.target.value)} /><label className="toggle-line"><input type="checkbox" checked={bulkClearWifiRadius} onChange={(event) => setBulkClearWifiRadius(event.target.checked)} />Clear radius to project default</label></div>
                <div className="field full" style={{ marginTop: 8 }}><label htmlFor="bulk-wifi-enabled">Wi-Fi enabled override</label><select id="bulk-wifi-enabled" value={bulkWifiEnabled} onChange={(event) => setBulkWifiEnabled(event.target.value as typeof bulkWifiEnabled)}><option value="unchanged">Unchanged</option><option value="inherit">Clear to inherit (true)</option><option value="enabled">Set enabled</option><option value="disabled">Set disabled</option></select></div>
                <div className="field full" style={{ marginTop: 8 }}><label htmlFor="bulk-wifi">Wi-Fi notes</label><input id="bulk-wifi" value={bulkWifiNotes} placeholder="Unchanged" onChange={(event) => setBulkWifiNotes(event.target.value)} /></div>
                <div className="bulk-row" style={{ marginTop: 8 }}><div className="field"><label htmlFor="bulk-camera">SMART camera</label><select id="bulk-camera" value={bulkCameraId} onChange={(event) => setBulkCameraId(event.target.value)}><option value="">Unchanged</option>{cameraCatalog?.camera_models.filter((item) => item.active).map((item) => <option value={item.id} key={item.id}>{item.display_name}</option>)}</select></div><div className="field"><label htmlFor="bulk-lens">SMART lens</label><select id="bulk-lens" value={bulkLensId} onChange={(event) => setBulkLensId(event.target.value)}><option value="">Unchanged</option>{cameraCatalog?.lenses.filter((item) => item.active).map((item) => <option value={item.id} key={item.id}>{item.display_name}</option>)}</select></div></div>
                <button className="quiet-button" style={{ marginTop: 7, width: "100%" }} disabled={!project || !(bulkModelId || bulkHeight || bulkAzimuth || bulkIesId || bulkWifiNotes || bulkWifiRadius || bulkClearWifiRadius || bulkWifiEnabled !== "unchanged" || bulkCameraId || bulkLensId)} onClick={applyBulkConfiguration}>Apply selected fields</button>
                <p className="helper">Assignments create edit overlays. Manual selections, all-pole targeting, and folder targeting are explicit; folder names are never interpreted automatically.</p>
              </section>
              <section className="section">
                <div className="section-heading"><h3>Validation</h3><span className="helper">{activeWarnings} warnings</span></div>
                <div className="warning-list">{project?.warnings.slice(0, 8).map((warning, index) => <div className={`warning-card ${warning.severity}`} key={`${warning.code}-${index}`}>{warning.message}</div>)}{cameraWarnings.slice(0, 8).map((footprint) => <button className="warning-card warning" key={`${footprint.pole_id}-${footprint.camera_slot_id}`} onClick={() => setSelectedId(footprint.pole_id)}><strong>{footprint.pole_id} · {footprint.camera_slot_id}</strong><span>{footprint.warnings.join(" ")}</span></button>)}{lightingWarnings.slice(0, 8).map((item, index) => <button className="warning-card warning" key={`${item.areaId}-${index}`} onClick={() => setSelectedCalculationAreaId(item.areaId)}><strong>Lighting · {item.areaId}</strong><span>{item.warning}</span></button>)}{!project && <div className="empty-copy">Validation results appear after import.</div>}</div>
              </section>
            </div>
          )}
        </aside>

        <section className="map-stage" aria-label="Engineering map workspace">
          <EngineeringMap project={project} selected={selected} onSelect={setSelectedId} onFixtureAzimuthChange={(azimuth) => selected?.fixtureConfiguration && updatePole(selected.id, { fixture_configuration: { ...selected.fixtureConfiguration, fixture_azimuth_deg: roundNormalizedFixtureAzimuth(azimuth) } })} drawingPriorityArea={drawingPriorityArea} priorityDraft={priorityDraft} onPriorityDraftPoint={(coordinate) => setPriorityDraft((points) => [...points, coordinate])} onSelectPriorityArea={(id) => setSelectedPriorityAreaId(id)} drawingCalculationArea={drawingCalculationArea} calculationDraft={calculationDraft} onCalculationDraftPoint={(coordinate) => setCalculationDraft((points) => [...points, coordinate])} onSelectCalculationArea={setSelectedCalculationAreaId} drawingWifiArea={drawingWifiArea} wifiDraft={wifiDraft} onWifiDraftPoint={(coordinate) => setWifiDraft((points) => [...points, coordinate])} onSelectWifiArea={setSelectedWifiAreaId} resizeSignal={`${leftCollapsed}-${rightCollapsed}`} />
          <div className="map-overlay map-caption"><strong>Customer coordinates are locked</strong><span>Phase 4 lighting rotates distributions around unchanged existing-pole origins. No customer location is generated or moved.</span></div>
          {!project?.source.poles.length && <div className="map-overlay map-empty"><span className="eyebrow">Phase 1 · Existing-pole foundation</span><h1>Start with the customer’s pole layout</h1><p>Import a KML or KMZ to validate and display authoritative pole coordinates. Your changes remain separate and reversible.</p><button className="primary-button" onClick={() => importRef.current?.click()} disabled={busy}>Import KML/KMZ</button></div>}
        </section>

        <aside className="side-panel inspector" aria-label="Properties inspector">
          {rightCollapsed ? <CollapsedRail label="Properties" symbol="‹" onClick={() => setRightCollapsed(false)} /> : (
            <div className="panel-scroll">
              <div className="panel-titlebar"><h2>Properties</h2><button className="icon-button" onClick={() => setRightCollapsed(true)} aria-label="Collapse properties inspector">›</button></div>
              {selected && project ? <Phase2PoleInspector pole={selected} project={project} fixtureCatalog={fixtureCatalog} cameraCatalog={cameraCatalog} iesLibrary={iesLibrary} onAssignModel={(modelId) => assignFixtureModel(selected.id, modelId)} onChange={(patch) => updatePole(selected.id, patch)} onRestore={() => restorePole(selected.id)} /> : <section className="section"><h3>No pole selected</h3><p className="empty-copy">Click an imported pole to inspect source data and apply a separate engineering override.</p></section>}
            </div>
          )}
        </aside>
      </div>

      <footer className="statusbar"><span className="status-item"><span className="status-dot" />API-backed local project</span><span>CRS: {project?.projected_crs ?? "pending import"}</span><span>Source: {project?.source_crs ?? "WGS84"}</span><span>Edits: {project ? Object.keys(project.pole_edits).length : 0}</span><span className="status-message">{busy ? "Working…" : status}</span></footer>
      {error && <button type="button" className="toast" aria-live="assertive" onClick={() => setError(null)}>{error}</button>}
      {catalogOpen && fixtureCatalog && cameraCatalog && iesLibrary && <CatalogManager fixtures={fixtureCatalog} cameras={cameraCatalog} ies={iesLibrary} onClose={() => setCatalogOpen(false)} onRefresh={refreshCatalogs} onError={setError} />}
    </main>
  );
}

function CollapsedRail({ label, symbol, onClick }: { label: string; symbol: string; onClick: () => void }) {
  return <div className="collapsed-rail"><button className="icon-button" onClick={onClick} aria-label={`Expand ${label}`}>{symbol}</button><span className="collapsed-label">{label}</span></div>;
}

export function LegacyPhaseOnePoleInspector({ pole, project, onChange, onRestore }: { pole: EffectivePole; project: Project; onChange: (patch: Partial<PoleEdit>) => void; onRestore: () => void }) {
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
    {pole.fixtureType === "SMART" && <section className="section"><div className="section-heading"><h3>Camera & CAP</h3><span className="phase-tag">Phase 2/3/6</span></div><div className="future-card">Camera angle convention is stored as {project.defaults.camera_downward_angle_deg}° below horizontal. CAP participation is controlled only by the explicit Phase 6 node disposition and candidate/profile inputs; it is never inferred from fixture capability.</div></section>}
  </>;
}
