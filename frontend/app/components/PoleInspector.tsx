"use client";

import type { CSSProperties } from "react";
import type { CameraEquipmentCatalog, EffectivePole, FixtureModelCatalog, IesLibrary, PoleEdit, PoleFixtureConfiguration, Project } from "../lib/types";
import { withoutCameraOverride } from "../lib/phase2-workflows.mjs";

const COLORS = { LITE: "var(--lite)", WIFI: "var(--wifi)", SMART: "var(--smart)" };

export function PoleInspector({ pole, project, fixtureCatalog, cameraCatalog, iesLibrary, onAssignModel, onChange, onRestore }: { pole: EffectivePole; project: Project; fixtureCatalog: FixtureModelCatalog | null; cameraCatalog: CameraEquipmentCatalog | null; iesLibrary: IesLibrary | null; onAssignModel: (modelId: string) => void; onChange: (patch: Partial<PoleEdit>) => void; onRestore: () => void }) {
  const config = pole.fixtureConfiguration;
  const currentModel = fixtureCatalog?.fixture_models.find((item) => item.id === config?.fixture_model_id);
  const model = [...(fixtureCatalog?.fixture_models ?? []), ...(fixtureCatalog?.fixture_model_history ?? [])].find((item) => item.id === config?.fixture_model_id && item.revision === config.fixture_model_revision);
  const template = model?.mounting_template_revisions.find((item) => item.revision === config?.mounting_template_revision);
  const associatedIes = iesLibrary?.fixture_associations.filter((item) => item.fixture_model_id === model?.id && item.active).map((item) => item.ies_file_id) ?? [];

  function updateConfig(patch: Partial<PoleFixtureConfiguration>) {
    if (config) onChange({ fixture_configuration: { ...config, ...patch } });
  }

  function updateSlot(slotId: string, patch: Record<string, string | boolean | number | null>) {
    if (!config) return;
    const current = config.camera_overrides[slotId] ?? { slot_id: slotId, metadata: {} };
    updateConfig({ camera_overrides: { ...config.camera_overrides, [slotId]: { ...current, ...patch, slot_id: slotId } } });
  }

  function removeSlotOverride(slotId: string) {
    if (!config) return;
    updateConfig({ camera_overrides: withoutCameraOverride(config.camera_overrides, slotId) });
  }

  return <>
    <section className="section">
      <div className="section-heading"><h3>Selected pole</h3>{pole.modified && <span className="phase-tag modified-tag">Modified</span>}</div>
      <div className="form-grid">
        <div className="field full"><label htmlFor="pole-name">Pole name</label><input id="pole-name" value={pole.displayName} onChange={(event) => onChange({ display_name: event.target.value })} /></div>
        <div className="field"><label htmlFor="pole-id">Engineering ID</label><input id="pole-id" value={pole.externalId} onChange={(event) => onChange({ external_id: event.target.value })} /></div>
        <div className="field"><label htmlFor="fixture-model">Fixture model</label><select id="fixture-model" value={model?.id ?? ""} onChange={(event) => onAssignModel(event.target.value)}><option value="" disabled>Explicit selection required</option>{fixtureCatalog?.fixture_models.filter((item) => item.active).map((item) => <option value={item.id} key={item.id}>{item.display_name}</option>)}</select></div>
        <div className="field"><label htmlFor="pole-height">Pole height (m)</label><input id="pole-height" type="number" min="0.1" max="100" step="0.1" value={pole.heightM ?? ""} placeholder="Required" onChange={(event) => onChange({ height_m: event.target.value ? Number(event.target.value) : null })} /></div>
        <label className="toggle-line"><input type="checkbox" checked={pole.active} onChange={(event) => onChange({ active: event.target.checked })} />Active pole</label>
        <div className="field full"><label htmlFor="notes">Engineering notes</label><textarea id="notes" value={pole.engineeringNotes} onChange={(event) => onChange({ engineering_notes: event.target.value })} placeholder="Field observations, assumptions, or follow-up" /></div>
      </div>
      <button className="quiet-button restore-button" onClick={onRestore} disabled={!pole.modified}>Restore source/default values</button>
    </section>
    <section className="section">
      <div className="section-heading"><h3>Original customer data</h3><span className="layer-dot" style={{ "--dot": COLORS[pole.fixtureType] } as CSSProperties} /></div>
      <div className="source-card"><dl><dt>Folder</dt><dd>{pole.folder_path.join(" / ") || "Unfiled"}</dd><dt>Source name</dt><dd>{pole.name}</dd><dt>Placemark ID</dt><dd>{pole.source_placemark_id ?? "Not provided"}</dd><dt>Coordinates</dt><dd>{pole.raw_coordinates}</dd><dt>Source style</dt><dd>{pole.source_style_url ?? "None"}</dd></dl></div>
      <p className="helper">Coordinates are read-only and remain exactly as imported.</p>
    </section>
    <section className="section">
      <div className="section-heading"><h3>Lighting configuration</h3><span className="phase-tag">Phase 2</span></div>
      {config && model ? <div className="form-grid">
        <div className="field full"><label htmlFor="ies-file">IES file</label><select id="ies-file" value={config.ies_file_id ?? ""} onChange={(event) => updateConfig({ ies_file_id: event.target.value || null })}><option value="">No associated IES selected</option>{iesLibrary?.files.filter((item) => associatedIes.includes(item.id) && item.active).map((item) => <option value={item.id} key={item.id}>{item.original_filename}</option>)}</select></div>
        <div className="field"><label htmlFor="fixture-azimuth">Fixture azimuth (°)</label><input id="fixture-azimuth" type="number" min="0" max="359.999" step="1" value={config.fixture_azimuth_deg} onChange={(event) => updateConfig({ fixture_azimuth_deg: Number(event.target.value) })} /></div>
        <div className="field"><label htmlFor="catalog-revision">Catalog revision</label><input id="catalog-revision" disabled value={`${config.fixture_model_revision} / template ${config.mounting_template_revision ?? "none"}`} /></div>
      </div> : <div className="future-card"><strong>Explicit model selection required.</strong><br />The legacy {pole.fixtureType} classification does not identify Phoenix 1 or Solitaire.</div>}
      {config && currentModel && (config.fixture_model_revision !== currentModel.revision || config.mounting_template_revision !== currentModel.current_mounting_template_revision) && <button className="quiet-button restore-button" onClick={() => updateConfig({ fixture_model_revision: currentModel.revision, mounting_template_revision: currentModel.current_mounting_template_revision })}>Explicitly adopt current catalog/template revision</button>}
    </section>
    {model?.capabilities.wifi && config && <section className="section"><div className="section-heading"><h3>Wi-Fi configuration</h3><span className="phase-tag">Phase 2</span></div><div className="field full"><label htmlFor="wifi-notes">Configuration notes</label><input id="wifi-notes" value={String(config.wifi_configuration?.notes ?? "")} onChange={(event) => updateConfig({ wifi_configuration: { ...(config.wifi_configuration ?? {}), notes: event.target.value } })} /></div><p className="helper">Configuration only; RF coverage remains deferred to Phase 4.</p></section>}
    {model?.capabilities.cameras && config && <section className="section">
      <div className="section-heading"><h3>SMART cameras</h3><span className="phase-tag">Template r{config.mounting_template_revision}</span></div>
      {template?.slots.map((slot) => {
        const override = config.camera_overrides[slot.id];
        const cameraId = override?.camera_model_id ?? slot.camera_model_id ?? "";
        const lensId = override?.lens_id ?? slot.lens_id ?? "";
        const enabled = override?.enabled ?? slot.enabled;
        return <div className="camera-slot" key={slot.id}><div className="section-heading"><h3>{slot.display_name}</h3><span className="helper">{override ? "Pole override" : "Catalog default"}</span></div><div className="form-grid">
          <div className="field"><label htmlFor={`${slot.id}-camera`}>Camera</label><select id={`${slot.id}-camera`} value={cameraId} onChange={(event) => { const selectedCamera = cameraCatalog?.camera_models.find((item) => item.id === event.target.value); updateSlot(slot.id, { camera_model_id: selectedCamera?.id ?? null, camera_model_revision: selectedCamera?.revision ?? null }); }}><option value="">Unassigned</option>{cameraCatalog?.camera_models.filter((item) => item.active).map((item) => <option key={item.id} value={item.id}>{item.display_name}</option>)}</select></div>
          <div className="field"><label htmlFor={`${slot.id}-lens`}>Lens</label><select id={`${slot.id}-lens`} value={lensId} onChange={(event) => { const selectedLens = cameraCatalog?.lenses.find((item) => item.id === event.target.value); updateSlot(slot.id, { lens_id: selectedLens?.id ?? null, lens_revision: selectedLens?.revision ?? null }); }}><option value="">Unassigned</option>{cameraCatalog?.lenses.filter((item) => item.active && (!cameraId || item.compatible_camera_model_ids.includes(cameraId))).map((item) => <option key={item.id} value={item.id}>{item.display_name}</option>)}</select></div>
          <div className="field"><label htmlFor={`${slot.id}-azimuth`}>Relative azimuth (°)</label><input id={`${slot.id}-azimuth`} type="number" min="-180" max="180" value={override?.relative_azimuth_deg ?? slot.relative_azimuth_deg} onChange={(event) => updateSlot(slot.id, { relative_azimuth_deg: Number(event.target.value) })} /></div>
          <div className="field"><label htmlFor={`${slot.id}-tilt`}>Downward tilt (°)</label><input id={`${slot.id}-tilt`} type="number" min="0" max="90" value={override?.downward_tilt_deg ?? slot.downward_tilt_deg} onChange={(event) => updateSlot(slot.id, { downward_tilt_deg: Number(event.target.value) })} /></div>
          <label className="toggle-line"><input type="checkbox" checked={enabled} onChange={(event) => updateSlot(slot.id, { enabled: event.target.checked })} />Camera enabled</label>
        </div>{override && <button type="button" className="quiet-button restore-button" onClick={() => removeSlotOverride(slot.id)}>Remove pole override and restore catalog default</button>}</div>;
      })}
      <p className="helper">Downward tilt is positive below horizontal. FOV rendering remains deferred to Phase 3.</p>
    </section>}
    {model && !model.capabilities.cameras && <section className="section"><div className="future-card">This {model.capability_variant} model has no camera capability. Camera controls are intentionally unavailable.</div></section>}
    <section className="section"><div className="future-card"><strong>Later engines remain gated.</strong><br />No illuminance, camera FOV, Wi-Fi coverage, CAP recommendation, or automatic pole placement is performed in Phase 2.</div><p className="helper">Conceptual Wi-Fi default retained: {project.defaults.wifi_radius_m} m.</p></section>
  </>;
}
