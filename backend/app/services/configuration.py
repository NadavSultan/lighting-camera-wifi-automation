from __future__ import annotations

from copy import deepcopy
from typing import Any

from pydantic import Field

from app.catalog_models import CameraEquipmentCatalog, FixtureModelCatalog, IesLibrary
from app.models import PoleCameraOverride, PoleEdit, PoleFixtureConfiguration, PoleWifiConfiguration, Project, StrictModel, utc_now
from app.services.ies import resolve_pinned_ies_revision
from app.services.lighting_calculation import invalidate_stale_lighting_results


class BulkPoleConfigurationPatch(StrictModel):
    fixture_model_id: str | None = None
    ies_file_id: str | None = None
    pole_height_m: float | None = Field(default=None, gt=0, le=100)
    fixture_azimuth_deg: float | None = Field(default=None, ge=0, lt=360)
    lighting_properties: dict[str, Any] | None = None
    wifi_configuration: dict[str, Any] | None = None
    wifi_radius_override_m: float | None = Field(default=None, gt=0, le=1000)
    clear_wifi_radius_override: bool = False
    wifi_enabled: bool | None = None
    clear_wifi_enabled_override: bool = False
    wifi_notes: str | None = None
    camera_model_by_slot: dict[str, str] | None = None
    lens_by_slot: dict[str, str] | None = None
    camera_enabled_by_slot: dict[str, bool] | None = None


class BulkPoleConfigurationRequest(StrictModel):
    pole_ids: list[str] = Field(min_length=1)
    patch: BulkPoleConfigurationPatch


def validate_project_configuration(
    project: Project,
    fixtures: FixtureModelCatalog,
    cameras: CameraEquipmentCatalog,
    ies: IesLibrary,
) -> list[str]:
    errors: list[str] = []
    fixture_current = {item.id: item for item in fixtures.fixture_models}
    fixture_revisions = {(item.id, item.revision): item for item in [*fixtures.fixture_models, *fixtures.fixture_model_history]}
    camera_current = {item.id: item for item in cameras.camera_models}
    camera_revisions = {(item.id, item.revision): item for item in [*cameras.camera_models, *cameras.camera_model_history]}
    lens_current = {item.id: item for item in cameras.lenses}
    lens_revisions = {(item.id, item.revision): item for item in [*cameras.lenses, *cameras.lens_history]}
    for pole_id, edit in project.pole_edits.items():
        config = edit.fixture_configuration
        if config is None:
            continue
        current_model = fixture_current.get(config.fixture_model_id)
        model = fixture_revisions.get((config.fixture_model_id, config.fixture_model_revision))
        if current_model is None or not current_model.active:
            errors.append(f"{pole_id}: unknown or inactive fixture model")
            continue
        if model is None:
            errors.append(f"{pole_id}: pinned fixture revision does not exist")
            continue
        if edit.fixture_type != model.capability_variant:
            errors.append(f"{pole_id}: legacy fixture classification conflicts with selected fixture model")
        if model.capabilities.cameras:
            revisions = {item.revision: item for item in model.mounting_template_revisions}
            template = revisions.get(config.mounting_template_revision or -1)
            if template is None:
                errors.append(f"{pole_id}: pinned mounting template revision does not exist")
                continue
            slot_ids = {slot.id for slot in template.slots}
            if not set(config.camera_overrides).issubset(slot_ids):
                errors.append(f"{pole_id}: camera override references an unknown mounting slot")
            for slot in template.slots:
                override = config.camera_overrides.get(slot.id)
                camera_id = override.camera_model_id if override and override.camera_model_id is not None else slot.camera_model_id
                camera_revision = override.camera_model_revision if override and override.camera_model_id is not None else slot.camera_model_revision
                lens_id = override.lens_id if override and override.lens_id is not None else slot.lens_id
                lens_revision = override.lens_revision if override and override.lens_id is not None else slot.lens_revision
                enabled = override.enabled if override and override.enabled is not None else slot.enabled
                if enabled and camera_id is None:
                    errors.append(f"{pole_id}/{slot.id}: missing camera assignment")
                camera = camera_revisions.get((camera_id, camera_revision)) if camera_id is not None and camera_revision is not None else None
                lens = lens_revisions.get((lens_id, lens_revision)) if lens_id is not None and lens_revision is not None else None
                if camera_id is not None and (camera_revision is None or camera is None or not camera_current.get(camera_id) or not camera_current[camera_id].active):
                    errors.append(f"{pole_id}/{slot.id}: unknown or inactive camera")
                if lens_id is not None and (lens_revision is None or lens is None or not lens_current.get(lens_id) or not lens_current[lens_id].active):
                    errors.append(f"{pole_id}/{slot.id}: unknown or inactive lens")
                if camera is not None and lens is not None and camera.id not in lens.compatible_camera_model_ids:
                    errors.append(f"{pole_id}/{slot.id}: camera and lens are incompatible")
        elif config.camera_overrides:
            errors.append(f"{pole_id}: camera configuration is incompatible with a non-SMART fixture")
        if model.capabilities.wifi:
            pass
        elif config.wifi_configuration is not None:
            errors.append(f"{pole_id}: Wi-Fi configuration is incompatible with a LITE fixture")
        if config.ies_file_id is not None:
            try:
                resolve_pinned_ies_revision(ies, config.ies_file_id, config.ies_file_revision, model.id)
            except ValueError as exc:
                errors.append(f"{pole_id}: {exc}")
    return errors


def apply_bulk_configuration(
    project: Project,
    request: BulkPoleConfigurationRequest,
    fixtures: FixtureModelCatalog,
    cameras: CameraEquipmentCatalog | None = None,
    ies: IesLibrary | None = None,
) -> Project:
    next_project = deepcopy(project)
    source_ids = {pole.id for pole in project.source.poles}
    unknown = set(request.pole_ids) - source_ids
    if unknown:
        raise ValueError(f"bulk configuration references unknown poles: {sorted(unknown)}")
    model_by_id = {item.id: item for item in fixtures.fixture_models if item.active}
    fields = {name for name in request.patch.model_fields_set if getattr(request.patch, name) is not None}
    camera_by_id = {item.id: item for item in (cameras.camera_models if cameras else []) if item.active}
    lens_by_id = {item.id: item for item in (cameras.lenses if cameras else []) if item.active}
    for pole_id in request.pole_ids:
        edit = next_project.pole_edits.get(pole_id) or PoleEdit(pole_id=pole_id)
        config = edit.fixture_configuration
        if "fixture_model_id" in fields:
            model = model_by_id.get(request.patch.fixture_model_id or "")
            if model is None:
                raise ValueError("bulk fixture assignment references an unknown or inactive model")
            if config is None or config.fixture_model_id != model.id:
                config = PoleFixtureConfiguration(
                    fixture_model_id=model.id,
                    fixture_model_revision=model.revision,
                    mounting_template_revision=model.current_mounting_template_revision,
                    ies_file_id=model.default_ies_file_id,
                )
            edit.fixture_type = model.capability_variant
        if "pole_height_m" in fields:
            edit.height_m = request.patch.pole_height_m
        nested_fields = fields - {"fixture_model_id", "pole_height_m"}
        if nested_fields and config is None:
            raise ValueError("assign a fixture model before applying fixture configuration")
        if config is not None:
            if "ies_file_id" in fields:
                selected_id = request.patch.ies_file_id
                if ies is None:
                    raise ValueError("IES library is required for an explicit IES assignment or reselection")
                selected = next((item for item in (ies.files if ies else []) if item.id == selected_id), None)
                if selected is None or not selected.active or selected.validation_status != "valid":
                    raise ValueError("bulk IES assignment references an unknown, inactive, invalid, or unsupported current record")
                config.ies_file_id = selected_id
                config.ies_file_revision = selected.revision
            if "fixture_azimuth_deg" in fields and request.patch.fixture_azimuth_deg is not None:
                config.fixture_azimuth_deg = request.patch.fixture_azimuth_deg
            if "lighting_properties" in fields and request.patch.lighting_properties is not None:
                config.lighting_properties.update(request.patch.lighting_properties)
            if "wifi_configuration" in fields:
                config.wifi_configuration = PoleWifiConfiguration.model_validate(request.patch.wifi_configuration) if request.patch.wifi_configuration is not None else None
            wifi_fields = {"wifi_radius_override_m", "clear_wifi_radius_override", "wifi_enabled", "clear_wifi_enabled_override", "wifi_notes"}
            if fields & wifi_fields:
                wifi = config.wifi_configuration or PoleWifiConfiguration()
                if "wifi_radius_override_m" in fields:
                    wifi.radius_override_m = request.patch.wifi_radius_override_m
                if request.patch.clear_wifi_radius_override:
                    wifi.radius_override_m = None
                if "wifi_enabled" in fields:
                    wifi.enabled = request.patch.wifi_enabled
                if request.patch.clear_wifi_enabled_override:
                    wifi.enabled = None
                if "wifi_notes" in fields and request.patch.wifi_notes is not None:
                    wifi.notes = request.patch.wifi_notes
                wifi.configuration_revision += 1
                wifi.modified_at = utc_now()
                config.wifi_configuration = wifi
            for field_name, values in (
                ("camera_model_by_slot", request.patch.camera_model_by_slot),
                ("lens_by_slot", request.patch.lens_by_slot),
                ("camera_enabled_by_slot", request.patch.camera_enabled_by_slot),
            ):
                if field_name not in fields or values is None:
                    continue
                for slot_id, value in values.items():
                    override = config.camera_overrides.get(slot_id) or PoleCameraOverride(slot_id=slot_id)
                    if field_name == "camera_model_by_slot":
                        override.camera_model_id = str(value)
                        camera = camera_by_id.get(str(value))
                        if camera is None:
                            raise ValueError("bulk camera assignment references an unknown or inactive camera")
                        override.camera_model_revision = camera.revision
                    elif field_name == "lens_by_slot":
                        override.lens_id = str(value)
                        lens = lens_by_id.get(str(value))
                        if lens is None:
                            raise ValueError("bulk lens assignment references an unknown or inactive lens")
                        override.lens_revision = lens.revision
                    else:
                        override.enabled = bool(value)
                    config.camera_overrides[slot_id] = override
            edit.fixture_configuration = config
        edit.modified_at = utc_now()
        next_project.pole_edits[pole_id] = edit
    invalidate_stale_lighting_results(next_project)
    return next_project


def pin_missing_equipment_revisions(project: Project, fixtures: FixtureModelCatalog, cameras: CameraEquipmentCatalog, ies: IesLibrary | None = None) -> Project:
    """One-time corrective migration: pin unversioned Phase 2 camera/lens assignments to the current revision."""
    migrated = deepcopy(project)
    fixture_by_id = {item.id: item for item in fixtures.fixture_models}
    camera_by_id = {item.id: item for item in cameras.camera_models}
    lens_by_id = {item.id: item for item in cameras.lenses}
    ies_by_id = {item.id: item for item in (ies.files if ies else [])}
    for edit in migrated.pole_edits.values():
        config = edit.fixture_configuration
        model = fixture_by_id.get(config.fixture_model_id) if config else None
        template = next((item for item in model.mounting_template_revisions if item.revision == config.mounting_template_revision), None) if model and config else None
        if config and config.ies_file_id and config.ies_file_revision is None and config.ies_file_id in ies_by_id:
            config.ies_file_revision = ies_by_id[config.ies_file_id].revision
        if not config or not template:
            continue
        for slot in template.slots:
            override = config.camera_overrides.get(slot.id)
            if override and override.camera_model_id and override.camera_model_revision is None and override.camera_model_id in camera_by_id:
                override.camera_model_revision = camera_by_id[override.camera_model_id].revision
            if override and override.lens_id and override.lens_revision is None and override.lens_id in lens_by_id:
                override.lens_revision = lens_by_id[override.lens_id].revision
    return migrated
