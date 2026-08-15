from __future__ import annotations

import base64
import binascii
import hashlib
from datetime import datetime, timezone
from enum import Enum
from typing import Annotated, Any, Literal
from uuid import uuid4

from pydantic import BaseModel, ConfigDict, Field, model_validator


SCHEMA_VERSION = "2.1.0"
SOFTWARE_VERSION = "0.2.0"


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


class StrictModel(BaseModel):
    model_config = ConfigDict(extra="forbid", validate_assignment=True)


class OperatingMode(str, Enum):
    EXISTING_POLES = "existing-poles"
    PROPOSED_LAYOUT = "proposed-layout"


class FixtureType(str, Enum):
    LITE = "LITE"
    WIFI = "WIFI"
    SMART = "SMART"


class WarningSeverity(str, Enum):
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"


class ProjectWarning(StrictModel):
    code: str
    severity: WarningSeverity = WarningSeverity.WARNING
    message: str
    pole_ids: list[str] = Field(default_factory=list)
    details: dict[str, Any] = Field(default_factory=dict)


class SourceFile(StrictModel):
    filename: Annotated[str, Field(min_length=1, pattern=r"^[^/\\]+$")]
    media_type: Literal["application/vnd.google-earth.kml+xml", "application/vnd.google-earth.kmz"]
    sha256: Annotated[str, Field(pattern=r"^[0-9a-f]{64}$")]
    size_bytes: Annotated[int, Field(ge=1, le=50 * 1024 * 1024)]
    imported_at: datetime
    source_crs: Literal["EPSG:4326"] = "EPSG:4326"
    kml_entry: str | None = None
    content_base64: str = Field(description="Exact uploaded bytes for portable local project reopen/export")

    @model_validator(mode="after")
    def validate_embedded_content(self) -> "SourceFile":
        if self.filename in {".", ".."}:
            raise ValueError("source filename must be a safe basename")
        try:
            content = base64.b64decode(self.content_base64, validate=True)
        except (binascii.Error, ValueError) as exc:
            raise ValueError("source content_base64 is not valid Base64") from exc
        if len(content) != self.size_bytes:
            raise ValueError("source size_bytes does not match embedded content")
        if hashlib.sha256(content).hexdigest() != self.sha256:
            raise ValueError("source sha256 does not match embedded content")
        return self


class SourcePole(StrictModel):
    id: str
    sequence_index: int
    source_placemark_id: str | None = None
    name: str
    folder_path: list[str] = Field(default_factory=list)
    description: str = ""
    extended_data: dict[str, str] = Field(default_factory=dict)
    source_style_url: str | None = None
    source_style_color: str | None = None
    longitude: float
    latitude: float
    altitude_m: float | None = None
    raw_coordinates: str


class SourceLayer(StrictModel):
    file: SourceFile | None = None
    document_name: str | None = None
    poles: list[SourcePole] = Field(default_factory=list)
    unsupported_geometry_count: int = 0


class PoleEdit(StrictModel):
    pole_id: str
    display_name: str | None = None
    external_id: str | None = None
    fixture_type: FixtureType | None = None
    height_m: Annotated[float | None, Field(gt=0, le=100)] = None
    active: bool | None = None
    engineering_notes: str | None = None
    fixture_configuration: PoleFixtureConfiguration | None = None
    longitude: Annotated[float | None, Field(ge=-180, le=180)] = None
    latitude: Annotated[float | None, Field(ge=-90, le=90)] = None
    location_edit_authorized: bool = False
    modified_at: datetime = Field(default_factory=utc_now)

    @model_validator(mode="after")
    def validate_location_edit(self) -> "PoleEdit":
        has_lon = self.longitude is not None
        has_lat = self.latitude is not None
        if has_lon != has_lat:
            raise ValueError("longitude and latitude must be provided together")
        if (has_lon or has_lat) and not self.location_edit_authorized:
            raise ValueError("coordinate edits require location_edit_authorized=true")
        return self


class ProjectDefaults(StrictModel):
    fixture_type: FixtureType = FixtureType.LITE
    pole_height_m: Annotated[float | None, Field(gt=0, le=100)] = None
    maintenance_factor: Annotated[float, Field(gt=0, le=1)] = 0.8
    calculation_plane_height_m: float = 0.0
    wifi_radius_m: Annotated[float, Field(gt=0, le=1000)] = 30.0
    camera_downward_angle_deg: Annotated[float, Field(ge=0, le=90)] = 35.0


class PoleCameraOverride(StrictModel):
    slot_id: str
    camera_model_id: str | None = None
    camera_model_revision: Annotated[int | None, Field(ge=1)] = None
    lens_id: str | None = None
    lens_revision: Annotated[int | None, Field(ge=1)] = None
    enabled: bool | None = None
    relative_azimuth_deg: Annotated[float | None, Field(ge=-180, le=180)] = None
    downward_tilt_deg: Annotated[float | None, Field(ge=0, le=90)] = None
    metadata: dict[str, Any] = Field(default_factory=dict)


class PoleFixtureConfiguration(StrictModel):
    fixture_model_id: str
    fixture_model_revision: Annotated[int, Field(ge=1)]
    mounting_template_revision: Annotated[int | None, Field(ge=1)] = None
    ies_file_id: str | None = None
    fixture_azimuth_deg: Annotated[float, Field(ge=0, lt=360)] = 0.0
    lighting_properties: dict[str, Any] = Field(default_factory=dict)
    wifi_configuration: dict[str, Any] | None = None
    camera_overrides: dict[str, PoleCameraOverride] = Field(default_factory=dict)

    @model_validator(mode="after")
    def validate_override_keys(self) -> "PoleFixtureConfiguration":
        for key, override in self.camera_overrides.items():
            if key != override.slot_id:
                raise ValueError(f"camera override key {key!r} does not match slot_id")
        return self


class LayerState(StrictModel):
    original_customer_poles: bool = True
    lite_fixtures: bool = True
    wifi_fixtures: bool = True
    smart_fixtures: bool = True
    camera_fov: bool = False
    wifi_coverage: bool = False
    calculation_areas: bool = False
    calculation_points: bool = False
    lighting_heat_map: bool = False
    cap_locations: bool = False
    cap_connections: bool = False
    warnings: bool = True


class Project(StrictModel):
    schema_version: Literal["2.1.0"] = SCHEMA_VERSION
    software_version: str = SOFTWARE_VERSION
    id: str = Field(default_factory=lambda: str(uuid4()))
    name: str = "Untitled lighting project"
    created_at: datetime = Field(default_factory=utc_now)
    updated_at: datetime = Field(default_factory=utc_now)
    mode: OperatingMode = OperatingMode.EXISTING_POLES
    proposed_layout_authorized: bool = False
    source_crs: Literal["EPSG:4326"] = "EPSG:4326"
    projected_crs: str | None = None
    defaults: ProjectDefaults = Field(default_factory=ProjectDefaults)
    source: SourceLayer = Field(default_factory=SourceLayer)
    pole_edits: dict[str, PoleEdit] = Field(default_factory=dict)
    layer_state: LayerState = Field(default_factory=LayerState)
    warnings: list[ProjectWarning] = Field(default_factory=list)
    assumptions: list[str] = Field(default_factory=lambda: [
        "Existing-pole mode is active; no pole locations are generated or optimized.",
        "Customer KML/KMZ coordinates are authoritative and stored in WGS84.",
    ])
    calculated_layers: dict[str, Any] = Field(default_factory=dict)
    recommended_layers: dict[str, Any] = Field(default_factory=dict)
    source_references: dict[str, str] = Field(default_factory=dict)
    legacy_fixture_assignments_require_model_selection: bool = True

    @model_validator(mode="after")
    def enforce_phase_one_policy(self) -> "Project":
        if self.mode is OperatingMode.PROPOSED_LAYOUT and not self.proposed_layout_authorized:
            raise ValueError("proposed-layout mode requires explicit authorization")
        source_ids = {pole.id for pole in self.source.poles}
        if len(source_ids) != len(self.source.poles):
            raise ValueError("source pole IDs must be unique")
        unknown = set(self.pole_edits) - source_ids
        if unknown:
            raise ValueError(f"pole edits reference unknown source poles: {sorted(unknown)}")
        for key, edit in self.pole_edits.items():
            if edit.pole_id != key:
                raise ValueError(f"pole edit key {key!r} does not match pole_id")
        return self


class ProjectSummary(StrictModel):
    id: str
    name: str
    mode: OperatingMode
    pole_count: int
    warning_count: int
    updated_at: datetime


class HealthResponse(StrictModel):
    status: Literal["ok"] = "ok"
    phase: Literal[2] = 2
    version: str = SOFTWARE_VERSION


def migrate_project_payload(payload: dict[str, Any]) -> dict[str, Any]:
    """Migrate a portable Phase 1 project without guessing a fixture family."""
    version = payload.get("schema_version", "1.0.0")
    if version == SCHEMA_VERSION:
        return payload
    if version not in {"1.0.0", "2.0.0"}:
        raise ValueError(f"Unsupported project schema version: {version}")
    migrated = dict(payload)
    migrated["schema_version"] = SCHEMA_VERSION
    migrated["software_version"] = SOFTWARE_VERSION
    migrated["legacy_fixture_assignments_require_model_selection"] = True
    assumptions = list(migrated.get("assumptions", []))
    notice = "Phase 1 fixture classifications were preserved; fixture family/model selection remains explicit."
    if notice not in assumptions:
        assumptions.append(notice)
    migrated["assumptions"] = assumptions
    return migrated
