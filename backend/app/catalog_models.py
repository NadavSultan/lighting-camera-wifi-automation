from __future__ import annotations

import base64
import binascii
import hashlib
from datetime import datetime
from typing import Annotated, Any, Literal

from pydantic import Field, model_validator

from app.models import FixtureType, StrictModel


class FixtureCapabilities(StrictModel):
    lighting: bool
    wifi: bool
    cameras: bool
    camera_slot_count: Annotated[int, Field(ge=0)] = 0


class CameraMountingSlot(StrictModel):
    id: str
    display_name: str
    relative_azimuth_deg: Annotated[float, Field(ge=-180, le=180)]
    downward_tilt_deg: Annotated[float, Field(ge=0, le=90)] = 35.0
    camera_model_id: str | None = None
    camera_model_revision: Annotated[int | None, Field(ge=1)] = None
    lens_id: str | None = None
    lens_revision: Annotated[int | None, Field(ge=1)] = None
    enabled: bool = True
    origin_offset_x_m: Literal[0.0] = 0.0
    origin_offset_y_m: Literal[0.0] = 0.0
    origin_offset_z_m: Literal[0.0] = 0.0
    metadata: dict[str, Any] = Field(default_factory=dict)


class CameraMountingTemplateRevision(StrictModel):
    revision: Annotated[int, Field(ge=1)]
    created_at: datetime
    notes: str = ""
    geometry_contract_version: Literal["fixed-zero-origin-1.0.0"] | None = None
    slots: list[CameraMountingSlot]

    @model_validator(mode="after")
    def unique_slots(self) -> "CameraMountingTemplateRevision":
        ids = [slot.id for slot in self.slots]
        if len(ids) != len(set(ids)):
            raise ValueError("camera mounting slot IDs must be unique")
        return self


class FixtureModel(StrictModel):
    id: str
    display_name: str
    fixture_family: str
    capability_variant: FixtureType
    capabilities: FixtureCapabilities
    manufacturer: str | None = None
    model_metadata: dict[str, Any] = Field(default_factory=dict)
    electrical_properties: dict[str, Any] = Field(default_factory=dict)
    photometric_properties: dict[str, Any] = Field(default_factory=dict)
    compatible_ies_file_ids: list[str] = Field(default_factory=list)
    default_ies_file_id: str | None = None
    mounting_template_revisions: list[CameraMountingTemplateRevision] = Field(default_factory=list)
    current_mounting_template_revision: int | None = None
    active: bool = True
    revision: Annotated[int, Field(ge=1)] = 1

    @model_validator(mode="after")
    def validate_capabilities_and_template(self) -> "FixtureModel":
        expected = {
            FixtureType.LITE: (True, False, False),
            FixtureType.WIFI: (True, True, False),
            FixtureType.SMART: (True, True, True),
        }[self.capability_variant]
        if (self.capabilities.lighting, self.capabilities.wifi, self.capabilities.cameras) != expected:
            raise ValueError(f"capabilities conflict with {self.capability_variant.value}")
        if self.capabilities.cameras:
            if self.capabilities.camera_slot_count < 1 or not self.mounting_template_revisions:
                raise ValueError("SMART fixture models require a mounting template")
            revisions = {item.revision for item in self.mounting_template_revisions}
            if self.current_mounting_template_revision not in revisions:
                raise ValueError("current mounting template revision is missing")
            current = next(item for item in self.mounting_template_revisions if item.revision == self.current_mounting_template_revision)
            if len(current.slots) != self.capabilities.camera_slot_count:
                raise ValueError("camera slot count does not match the current mounting template")
        elif self.capabilities.camera_slot_count or self.mounting_template_revisions or self.current_mounting_template_revision:
            raise ValueError("non-SMART fixtures cannot have camera mounting templates")
        if self.default_ies_file_id is not None and self.default_ies_file_id not in self.compatible_ies_file_ids:
            raise ValueError("default IES file must also be compatible")
        return self

    def current_template(self) -> CameraMountingTemplateRevision | None:
        return next(
            (item for item in self.mounting_template_revisions if item.revision == self.current_mounting_template_revision),
            None,
        )


class FixtureModelCatalog(StrictModel):
    schema_version: Literal["1.2.0"] = "1.2.0"
    catalog_id: str = "fixture-model-catalog"
    fixture_models: list[FixtureModel]
    fixture_model_history: list[FixtureModel] = Field(default_factory=list)

    @model_validator(mode="after")
    def validate_catalog(self) -> "FixtureModelCatalog":
        ids = [item.id for item in self.fixture_models]
        pairs = [(item.fixture_family.casefold(), item.capability_variant.value) for item in self.fixture_models]
        if len(ids) != len(set(ids)):
            raise ValueError("duplicate fixture model identifiers")
        if len(pairs) != len(set(pairs)):
            raise ValueError("fixture family and capability variant combinations must be unique")
        history_keys = [(item.id, item.revision) for item in self.fixture_model_history]
        current_keys = {(item.id, item.revision) for item in self.fixture_models}
        if len(history_keys) != len(set(history_keys)) or current_keys.intersection(history_keys):
            raise ValueError("fixture model revisions must be immutable and unique")
        required = {
            "phoenix-1-lite": ("Phoenix 1", FixtureType.LITE),
            "phoenix-1-wifi": ("Phoenix 1", FixtureType.WIFI),
            "phoenix-1-smart": ("Phoenix 1", FixtureType.SMART),
            "solitaire-lite": ("Solitaire", FixtureType.LITE),
            "solitaire-wifi": ("Solitaire", FixtureType.WIFI),
            "solitaire-smart": ("Solitaire", FixtureType.SMART),
        }
        by_id = {item.id: item for item in self.fixture_models}
        if not set(required).issubset(by_id):
            raise ValueError("the six required fixture models must remain in the catalog")
        for model_id, (family, variant) in required.items():
            model = by_id[model_id]
            if (model.fixture_family, model.capability_variant) != (family, variant):
                raise ValueError(f"required fixture identity changed for {model_id}")
        self._validate_required_geometry(by_id["phoenix-1-smart"], (-70.0, 70.0), 140.0)
        self._validate_required_geometry(by_id["solitaire-smart"], (-60.0, 60.0), 120.0)
        return self

    @staticmethod
    def _validate_required_geometry(model: FixtureModel, offsets: tuple[float, float], separation: float) -> None:
        template = model.current_template()
        if template is None or len(template.slots) != 2:
            raise ValueError(f"{model.display_name} requires exactly two camera slots")
        actual = tuple(sorted(slot.relative_azimuth_deg for slot in template.slots))
        if actual != offsets or abs(actual[1] - actual[0]) != separation:
            raise ValueError(f"invalid mounting geometry for {model.display_name}")
        if any(slot.downward_tilt_deg != 35 for slot in template.slots):
            raise ValueError(f"{model.display_name} cameras require 35 degree downward tilt")
        if template.geometry_contract_version != "fixed-zero-origin-1.0.0":
            raise ValueError(f"{model.display_name} current template requires the approved fixed mounting contract")
        if any((slot.origin_offset_x_m, slot.origin_offset_y_m, slot.origin_offset_z_m) != (0, 0, 0) for slot in template.slots):
            raise ValueError(f"{model.display_name} cameras require zero XYZ origin offsets")


class CameraModel(StrictModel):
    id: str
    display_name: str
    manufacturer: str | None = None
    sensor: str | None = None
    resolution_width_px: Annotated[int | None, Field(gt=0)] = None
    resolution_height_px: Annotated[int | None, Field(gt=0)] = None
    compatible_lens_ids: list[str] = Field(default_factory=list)
    technical_properties: dict[str, Any] = Field(default_factory=dict)
    source_reference_id: str | None = None
    active: bool = True
    revision: Annotated[int, Field(ge=1)] = 1


class LensConfiguration(StrictModel):
    id: str
    display_name: str
    focal_length_mm: Annotated[float | None, Field(gt=0)] = None
    horizontal_fov_deg: Annotated[float | None, Field(gt=0, le=180)] = None
    vertical_fov_deg: Annotated[float | None, Field(gt=0, le=180)] = None
    compatible_camera_model_ids: list[str] = Field(default_factory=list)
    technical_properties: dict[str, Any] = Field(default_factory=dict)
    source_reference_id: str | None = None
    active: bool = True
    revision: Annotated[int, Field(ge=1)] = 1


class CameraEquipmentCatalog(StrictModel):
    schema_version: Literal["1.1.0"] = "1.1.0"
    catalog_id: str = "camera-equipment-catalog"
    camera_models: list[CameraModel]
    lenses: list[LensConfiguration]
    camera_model_history: list[CameraModel] = Field(default_factory=list)
    lens_history: list[LensConfiguration] = Field(default_factory=list)

    @model_validator(mode="after")
    def validate_compatibility(self) -> "CameraEquipmentCatalog":
        camera_ids = [item.id for item in self.camera_models]
        lens_ids = [item.id for item in self.lenses]
        if len(camera_ids) != len(set(camera_ids)) or len(lens_ids) != len(set(lens_ids)):
            raise ValueError("duplicate camera or lens identifiers")
        camera_history_keys = [(item.id, item.revision) for item in self.camera_model_history]
        lens_history_keys = [(item.id, item.revision) for item in self.lens_history]
        if len(camera_history_keys) != len(set(camera_history_keys)) or len(lens_history_keys) != len(set(lens_history_keys)):
            raise ValueError("historical camera and lens revisions must be unique")
        if {(item.id, item.revision) for item in self.camera_models}.intersection(camera_history_keys):
            raise ValueError("current camera revisions cannot also be historical")
        if {(item.id, item.revision) for item in self.lenses}.intersection(lens_history_keys):
            raise ValueError("current lens revisions cannot also be historical")
        camera_set, lens_set = set(camera_ids), set(lens_ids)
        for camera in self.camera_models:
            if not set(camera.compatible_lens_ids).issubset(lens_set):
                raise ValueError(f"{camera.id} references an unknown lens")
        for lens in self.lenses:
            if not set(lens.compatible_camera_model_ids).issubset(camera_set):
                raise ValueError(f"{lens.id} references an unknown camera")
        for camera in self.camera_models:
            derived = {lens.id for lens in self.lenses if camera.id in lens.compatible_camera_model_ids}
            if set(camera.compatible_lens_ids) != derived:
                raise ValueError(f"{camera.id} compatibility must be reciprocal; lens compatibility is authoritative")
        return self


class IesParsedMetadata(StrictModel):
    manufacturer: str | None = None
    luminaire_catalog_number: str | None = None
    lamp_count: int
    input_watts: float
    photometric_type: Literal["C"]
    units: Literal["m", "ft"]
    vertical_angle_count: int
    horizontal_angle_count: int
    vertical_angle_range_deg: tuple[float, float]
    horizontal_angle_range_deg: tuple[float, float]
    candela_value_count: int


class IesFileRecord(StrictModel):
    id: str
    original_filename: str
    sha256: Annotated[str, Field(pattern=r"^[0-9a-f]{64}$")]
    uploaded_at: datetime
    ies_format_version: str
    original_content_base64: str
    parsed_metadata: IesParsedMetadata | None = None
    validation_status: Literal["valid", "invalid", "unsupported"]
    validation_errors: list[str] = Field(default_factory=list)
    validation_warnings: list[str] = Field(default_factory=list)
    active: bool = True
    revision: Annotated[int, Field(ge=1)] = 1

    @model_validator(mode="after")
    def validate_original_content(self) -> "IesFileRecord":
        try:
            content = base64.b64decode(self.original_content_base64, validate=True)
        except (binascii.Error, ValueError) as exc:
            raise ValueError("original IES content is not valid Base64") from exc
        if hashlib.sha256(content).hexdigest() != self.sha256:
            raise ValueError("IES checksum does not match original content")
        if self.validation_status == "valid" and self.validation_errors:
            raise ValueError("valid IES records cannot contain validation errors")
        if self.validation_status == "valid" and self.parsed_metadata is None:
            raise ValueError("valid IES records require parsed metadata")
        if self.validation_status != "valid" and not self.validation_errors:
            raise ValueError("invalid or unsupported IES records require validation errors")
        return self


class IesFixtureAssociation(StrictModel):
    ies_file_id: str
    fixture_model_id: str
    active: bool = True


class IesLibrary(StrictModel):
    schema_version: Literal["1.1.0"] = "1.1.0"
    catalog_id: str = "ies-library"
    files: list[IesFileRecord] = Field(default_factory=list)
    fixture_associations: list[IesFixtureAssociation] = Field(default_factory=list)

    @model_validator(mode="after")
    def validate_library(self) -> "IesLibrary":
        ids = [item.id for item in self.files]
        hashes = [item.sha256 for item in self.files]
        if len(ids) != len(set(ids)):
            raise ValueError("duplicate IES identifiers")
        if len(hashes) != len(set(hashes)):
            raise ValueError("duplicate IES file checksum")
        known = set(ids)
        pairs: set[tuple[str, str]] = set()
        for association in self.fixture_associations:
            if association.ies_file_id not in known:
                raise ValueError("IES association references an unknown file")
            pair = (association.ies_file_id, association.fixture_model_id)
            if pair in pairs:
                raise ValueError("duplicate IES fixture association")
            record = next(item for item in self.files if item.id == association.ies_file_id)
            if association.active and (not record.active or record.validation_status != "valid"):
                raise ValueError("active IES associations require an active valid file")
            pairs.add(pair)
        return self


def normalize_azimuth(value: float) -> float:
    normalized = value % 360.0
    return 0.0 if normalized == 0 else normalized


def camera_absolute_azimuth(fixture_azimuth_deg: float, relative_azimuth_deg: float) -> float:
    return normalize_azimuth(fixture_azimuth_deg + relative_azimuth_deg)
