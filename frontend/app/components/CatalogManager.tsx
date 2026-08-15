"use client";

import { type ChangeEvent, useRef, useState } from "react";
import { addFixtureTemplateRevision, associateIes, removeIesAssociation, saveCameraModel, saveFixtureModel, saveLens, setDefaultIes, setIesActive, uploadIes } from "../lib/api";
import type { CameraEquipmentCatalog, CameraModel, FixtureModel, FixtureModelCatalog, FixtureType, IesLibrary, LensConfiguration } from "../lib/types";
import { uploadIesAndRefresh } from "../lib/phase2-workflows.mjs";

interface Props {
  fixtures: FixtureModelCatalog;
  cameras: CameraEquipmentCatalog;
  ies: IesLibrary;
  onClose: () => void;
  onRefresh: () => Promise<void>;
  onError: (message: string | null) => void;
}

export function CatalogManager({ fixtures, cameras, ies, onClose, onRefresh, onError }: Props) {
  const iesRef = useRef<HTMLInputElement>(null);
  const [fixtureId, setFixtureId] = useState(fixtures.fixture_models[0]?.id ?? "");
  const [iesId, setIesId] = useState(ies.files.find((item) => item.active && item.validation_status === "valid")?.id ?? "");

  async function action(callback: () => Promise<unknown>) {
    try {
      await callback();
      await onRefresh();
    } catch (caught) {
      onError(caught instanceof Error ? caught.message : "Catalog action failed");
    }
  }

  function editJson<T>(label: string, value: T, save: (next: T) => Promise<unknown>) {
    const entered = window.prompt(`Edit ${label} JSON`, JSON.stringify(value, null, 2));
    if (entered) void action(() => save(JSON.parse(entered) as T));
  }

  function addFixture() {
    const id = window.prompt("Stable fixture model ID");
    const family = id && window.prompt("Fixture family");
    if (!id || !family) return;
    const variant = (window.prompt("Fixture variant: LITE or WIFI", "LITE") ?? "LITE") as FixtureType;
    const model: FixtureModel = {
      id, display_name: `${family} ${variant}`, fixture_family: family, capability_variant: variant,
      capabilities: { lighting: true, wifi: variant === "WIFI", cameras: false, camera_slot_count: 0 },
      manufacturer: null, model_metadata: {}, electrical_properties: {}, photometric_properties: {},
      compatible_ies_file_ids: [], default_ies_file_id: null, mounting_template_revisions: [],
      current_mounting_template_revision: null, active: true, revision: 1,
    };
    editJson("new fixture model", model, saveFixtureModel);
  }

  function addCamera() {
    const id = window.prompt("Stable camera ID");
    if (!id) return;
    const model: CameraModel = { id, display_name: id, manufacturer: null, sensor: null, resolution_width_px: null, resolution_height_px: null, compatible_lens_ids: [], technical_properties: {}, source_reference_id: null, active: true, revision: 1 };
    editJson("new camera", model, saveCameraModel);
  }

  function addLens() {
    const id = window.prompt("Stable lens ID");
    if (!id) return;
    const lens: LensConfiguration = { id, display_name: id, focal_length_mm: null, horizontal_fov_deg: null, vertical_fov_deg: null, compatible_camera_model_ids: [], technical_properties: {}, source_reference_id: null, active: true, revision: 1 };
    editJson("new lens", lens, saveLens);
  }

  async function handleIes(event: ChangeEvent<HTMLInputElement>) {
    const file = event.target.files?.[0];
    event.target.value = "";
    if (!file) return;
    const result = await uploadIesAndRefresh(() => uploadIes(file), onRefresh);
    if (result.error) {
      setIesId("");
      onError(result.error instanceof Error ? result.error.message : "IES upload was rejected");
      return;
    }
    await onRefresh();
  }

  const usableIes = ies.files.filter((item) => item.active && item.validation_status === "valid");
  return <div className="catalog-backdrop">
    <section className="catalog-dialog" role="dialog" aria-modal="true" aria-label="Phase 2 catalog manager">
      <div className="catalog-header"><div><h2>Phase 2 catalogs</h2><p>Operational records · immutable catalog and mounting-template revisions</p></div><button className="icon-button" onClick={onClose} aria-label="Close catalog manager">×</button></div>
      <div className="catalog-body">
        <section className="catalog-column">
          <div className="section-heading"><h3>Fixture models</h3><button className="quiet-button" onClick={addFixture}>Add</button></div>
          {fixtures.fixture_models.map((model) => <div className="catalog-row" key={model.id}>
            <div><strong>{model.display_name}</strong><span>{model.fixture_family} · {model.capability_variant} · r{model.revision}</span></div>
            <button className="quiet-button" onClick={() => editJson("fixture model", model, saveFixtureModel)}>Edit</button>
            <button className="quiet-button" onClick={() => void action(() => saveFixtureModel({ ...model, active: !model.active }))}>{model.active ? "Deactivate" : "Activate"}</button>
            {model.capabilities.cameras && <button className="quiet-button" onClick={() => {
              const current = model.mounting_template_revisions.find((item) => item.revision === model.current_mounting_template_revision);
              if (!current) return;
              const next = { ...current, revision: Math.max(...model.mounting_template_revisions.map((item) => item.revision)) + 1, created_at: new Date().toISOString(), notes: "Explicit UI template revision" };
              editJson("new immutable template revision", next, (value) => addFixtureTemplateRevision(model.id, value));
            }}>New template revision</button>}
          </div>)}
        </section>

        <section className="catalog-column">
          <div className="section-heading"><h3>IES library</h3><button className="quiet-button" onClick={() => iesRef.current?.click()}>Upload IES</button><input ref={iesRef} className="sr-only" type="file" accept=".ies" onChange={(event) => void handleIes(event)} /></div>
          {ies.files.map((file) => <div className="catalog-row" key={file.id}>
            <div><strong>{file.original_filename}</strong><span>{file.ies_format_version} · {file.validation_status} · r{file.revision} · {file.sha256.slice(0, 12)}</span>{file.validation_errors.map((message) => <span key={`error-${message}`}>Error: {message}</span>)}{file.validation_warnings.map((message) => <span key={`warning-${message}`}>Warning: {message}</span>)}</div>
            <button className="quiet-button" disabled={!file.active && file.validation_status !== "valid"} onClick={() => void action(() => setIesActive(file.id, !file.active))}>{file.active ? "Deactivate" : "Activate"}</button>
          </div>)}
          {!ies.files.length && <p className="empty-copy">No operational IES files uploaded.</p>}
          <div className="association-grid">
            <select aria-label="IES file association" value={iesId} onChange={(event) => setIesId(event.target.value)}><option value="">Active valid IES file</option>{usableIes.map((item) => <option value={item.id} key={item.id}>{item.original_filename}</option>)}</select>
            <select aria-label="Fixture association" value={fixtureId} onChange={(event) => setFixtureId(event.target.value)}>{fixtures.fixture_models.map((item) => <option value={item.id} key={item.id}>{item.display_name}</option>)}</select>
            <button className="quiet-button" disabled={!iesId || !fixtureId} onClick={() => void action(() => associateIes(iesId, fixtureId))}>Associate</button>
            <button className="quiet-button" disabled={!iesId || !fixtureId} onClick={() => void action(() => setDefaultIes(fixtureId, iesId))}>Set default</button>
            <button className="quiet-button" disabled={!iesId || !fixtureId || !ies.fixture_associations.some((item) => item.ies_file_id === iesId && item.fixture_model_id === fixtureId)} onClick={() => void action(() => removeIesAssociation(iesId, fixtureId))}>Remove association</button>
          </div>
        </section>

        <section className="catalog-column">
          <div className="section-heading"><h3>Cameras & lenses</h3><div><button className="quiet-button" onClick={addCamera}>Add camera</button> <button className="quiet-button" onClick={addLens}>Add lens</button></div></div>
          <p className="helper">Lens compatible-camera IDs are authoritative; camera compatible-lens IDs are derived and reciprocity-validated.</p>
          {cameras.camera_models.map((camera) => <div className="catalog-row" key={camera.id}><div><strong>{camera.display_name}</strong><span>{camera.sensor ?? "Sensor unspecified"} · r{camera.revision}</span></div><button className="quiet-button" onClick={() => editJson("camera", camera, saveCameraModel)}>Edit</button><button className="quiet-button" onClick={() => void action(() => saveCameraModel({ ...camera, active: !camera.active }))}>{camera.active ? "Deactivate" : "Activate"}</button></div>)}
          {cameras.lenses.map((lens) => <div className="catalog-row" key={lens.id}><div><strong>{lens.display_name}</strong><span>{lens.horizontal_fov_deg ?? "?"}° × {lens.vertical_fov_deg ?? "?"}° · r{lens.revision}</span></div><button className="quiet-button" onClick={() => editJson("lens", lens, saveLens)}>Edit</button><button className="quiet-button" onClick={() => void action(() => saveLens({ ...lens, active: !lens.active }))}>{lens.active ? "Deactivate" : "Activate"}</button></div>)}
        </section>
      </div>
    </section>
  </div>;
}
