from __future__ import annotations

from datetime import datetime, timezone
from enum import Enum
from typing import Annotated, Any, Literal
from uuid import uuid4

from pydantic import BaseModel, ConfigDict, Field, model_validator


SCHEMA_VERSION = "1.0.0"
SOFTWARE_VERSION = "0.1.0"


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
    filename: str
    media_type: Literal["application/vnd.google-earth.kml+xml", "application/vnd.google-earth.kmz"]
    sha256: str
    size_bytes: int
    imported_at: datetime
    source_crs: Literal["EPSG:4326"] = "EPSG:4326"
    kml_entry: str | None = None
    content_base64: str = Field(description="Exact uploaded bytes for portable local project reopen/export")


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
    schema_version: Literal["1.0.0"] = SCHEMA_VERSION
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

    @model_validator(mode="after")
    def enforce_phase_one_policy(self) -> "Project":
        if self.mode is OperatingMode.PROPOSED_LAYOUT and not self.proposed_layout_authorized:
            raise ValueError("proposed-layout mode requires explicit authorization")
        source_ids = {pole.id for pole in self.source.poles}
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
    phase: Literal[1] = 1
    version: str = SOFTWARE_VERSION
