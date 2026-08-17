from __future__ import annotations

import base64
import binascii
import hashlib
import math
from datetime import datetime, timezone
from enum import Enum
from typing import Annotated, Any, Literal
from uuid import uuid4

from pydantic import BaseModel, ConfigDict, Field, model_validator
from shapely.geometry import Polygon
from shapely.validation import explain_validity


SCHEMA_VERSION = "2.4.0"
SOFTWARE_VERSION = "0.4.0"


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
    maintenance_factor: Annotated[float, Field(gt=0, le=1)] = 1.0
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
    ies_file_revision: Annotated[int | None, Field(ge=1)] = None
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
    camera_fov: bool = True
    camera_overlap: bool = True
    priority_areas: bool = True
    wifi_coverage: bool = False
    calculation_areas: bool = True
    calculation_points: bool = True
    lighting_heat_map: bool = True
    cap_locations: bool = False
    cap_connections: bool = False
    warnings: bool = True


class PriorityArea(StrictModel):
    id: str
    name: Annotated[str, Field(min_length=1, max_length=120)]
    wgs84_coordinates: Annotated[list[tuple[float, float]], Field(min_length=4)]
    created_at: datetime = Field(default_factory=utc_now)
    modified_at: datetime = Field(default_factory=utc_now)

    @model_validator(mode="after")
    def validate_polygon(self) -> "PriorityArea":
        if self.wgs84_coordinates[0] != self.wgs84_coordinates[-1]:
            raise ValueError("priority-area polygon must be closed")
        if len(set(self.wgs84_coordinates[:-1])) < 3:
            raise ValueError("priority-area polygon requires three distinct vertices")
        for longitude, latitude in self.wgs84_coordinates:
            if not math.isfinite(longitude) or not math.isfinite(latitude):
                raise ValueError("priority-area coordinates must be finite")
            if not (-180 <= longitude <= 180 and -90 <= latitude <= 90):
                raise ValueError("priority-area coordinate is outside WGS84 bounds")
        polygon = Polygon(self.wgs84_coordinates)
        if not polygon.is_valid:
            raise ValueError(f"priority-area polygon is invalid: {explain_validity(polygon)}")
        if polygon.area <= 1e-18:
            raise ValueError("priority-area polygon is degenerate and has no usable area")
        return self


class CalculationAreaClassification(str, Enum):
    ROAD = "ROAD"
    SIDEWALK = "SIDEWALK"
    PARKING = "PARKING"
    OTHER = "OTHER"


class CalculationAreaState(StrictModel):
    status: Literal["not-calculated", "calculated", "warning", "error"] = "not-calculated"
    polygon_revision: Annotated[int, Field(ge=1)] = 1
    last_calculated_at: datetime | None = None
    warnings: list[str] = Field(default_factory=list)
    assumptions: list[str] = Field(default_factory=list)
    provenance: dict[str, Any] = Field(default_factory=dict)


class CalculationArea(StrictModel):
    id: Annotated[str, Field(min_length=1, max_length=120)]
    name: Annotated[str, Field(min_length=1, max_length=120)]
    classification: CalculationAreaClassification
    wgs84_coordinates: Annotated[list[tuple[float, float]], Field(min_length=4)]
    calculation_plane_elevation_m: Annotated[float, Field(ge=-1000, le=10000)] = 0.0
    grid_spacing_m: Annotated[float, Field(gt=0, le=1000)] = 2.0
    maintenance_factor: Annotated[float, Field(gt=0, le=1)] = 1.0
    created_at: datetime = Field(default_factory=utc_now)
    modified_at: datetime = Field(default_factory=utc_now)
    calculation_state: CalculationAreaState = Field(default_factory=CalculationAreaState)

    @model_validator(mode="after")
    def validate_polygon(self) -> "CalculationArea":
        if not all(math.isfinite(value) for value in (self.calculation_plane_elevation_m, self.grid_spacing_m, self.maintenance_factor)):
            raise ValueError("calculation-area numeric settings must be finite")
        if self.wgs84_coordinates[0] != self.wgs84_coordinates[-1]:
            raise ValueError("calculation-area polygon must be closed")
        if len(set(self.wgs84_coordinates[:-1])) < 3:
            raise ValueError("calculation-area polygon requires three distinct vertices")
        for longitude, latitude in self.wgs84_coordinates:
            if not math.isfinite(longitude) or not math.isfinite(latitude):
                raise ValueError("calculation-area coordinates must be finite")
            if not (-180 <= longitude <= 180 and -90 <= latitude <= 90):
                raise ValueError("calculation-area coordinate is outside WGS84 bounds")
        polygon = Polygon(self.wgs84_coordinates)
        if not polygon.is_valid:
            raise ValueError(f"calculation-area polygon is invalid: {explain_validity(polygon)}")
        if polygon.area <= 1e-18:
            raise ValueError("calculation-area polygon is degenerate and has no usable area")
        return self


class LightingFixtureProvenance(StrictModel):
    pole_id: str
    fixture_model_id: str
    fixture_model_revision: int
    ies_file_id: str
    ies_file_revision: int
    ies_sha256: str
    ies_original_filename: str
    ies_parsed_metadata: dict[str, Any] = Field(default_factory=dict)
    mounting_height_m: float
    fixture_azimuth_deg: float
    origin_projected_m: tuple[float, float, float]
    warnings: list[str] = Field(default_factory=list)


class LightingCalculationPoint(StrictModel):
    id: str
    sequence_index: Annotated[int, Field(ge=0)]
    projected_coordinate_m: tuple[float, float]
    wgs84_coordinate: tuple[float, float]
    calculation_plane_elevation_m: float
    maintained_horizontal_illuminance_lux: Annotated[float, Field(ge=0)]
    per_fixture_contributions_lux: dict[str, float] | None = None
    warnings: list[str] = Field(default_factory=list)


class LightingStatistics(StrictModel):
    point_count: Annotated[int, Field(ge=0)] = 0
    grid_spacing_m: float
    average_illuminance_lux: float | None = None
    minimum_illuminance_lux: float | None = None
    maximum_illuminance_lux: float | None = None
    emin_over_eavg: float | None = None
    emin_over_emax: float | None = None


class LightingCalculationResult(StrictModel):
    calculation_area_id: str
    calculation_area_name: str
    calculation_model_version: Literal["direct-horizontal-type-c-1.0.0"] = "direct-horizontal-type-c-1.0.0"
    calculated_at: datetime = Field(default_factory=utc_now)
    polygon_revision: Annotated[int, Field(ge=1)]
    projected_crs: str
    grid_origin_m: tuple[float, float] = (0.0, 0.0)
    grid_anchor_policy: Literal["projected-crs-zero-lattice"] = "projected-crs-zero-lattice"
    boundary_policy: Literal["inside-or-boundary-with-1e-7-m-tolerance"] = "inside-or-boundary-with-1e-7-m-tolerance"
    points: list[LightingCalculationPoint] = Field(default_factory=list)
    statistics: LightingStatistics
    contributing_fixture_count: Annotated[int, Field(ge=0)] = 0
    fixture_provenance: list[LightingFixtureProvenance] = Field(default_factory=list)
    assumptions: list[str] = Field(default_factory=list)
    warnings: list[str] = Field(default_factory=list)
    disclaimer: Literal["Not independently validated against AGi32 or another professional photometric reference tool."] = "Not independently validated against AGi32 or another professional photometric reference tool."


class LightingCalculationLayer(StrictModel):
    calculation_model_version: Literal["direct-horizontal-type-c-1.0.0"] = "direct-horizontal-type-c-1.0.0"
    results: dict[str, LightingCalculationResult] = Field(default_factory=dict)


class PixelDensityStatus(StrictModel):
    method: Literal["not-calculated"] = "not-calculated"
    value: None = None
    units: None = None
    reason: str = "Architecture reserved; no trustworthy Phase 3 pixel-density calculation is approved."


class CameraFootprintResult(StrictModel):
    pole_id: str
    fixture_model_id: str
    fixture_model_revision: int
    mounting_template_revision: int
    camera_slot_id: str
    camera_model_id: str | None
    camera_model_revision: int | None
    lens_id: str | None
    lens_revision: int | None
    horizontal_fov_deg: float | None = None
    vertical_fov_deg: float | None = None
    fixture_height_m: float | None
    fixture_azimuth_deg: float
    template_relative_azimuth_deg: float
    fixed_downward_tilt_deg: float
    camera_absolute_azimuth_deg: float
    origin_offset_xyz_m: tuple[Literal[0.0], Literal[0.0], Literal[0.0]] = (0.0, 0.0, 0.0)
    geometry_contract_version: str | None = None
    projected_crs: str | None
    geometry_model_version: Literal["flat-ground-pinhole-1.0.0"] = "flat-ground-pinhole-1.0.0"
    enabled: bool
    valid: bool
    warnings: list[str] = Field(default_factory=list)
    assumptions: list[str] = Field(default_factory=list)
    projected_coordinates_m: list[tuple[float, float]] | None = None
    wgs84_coordinates: list[tuple[float, float]] | None = None
    footprint_area_m2: float | None = None
    pixel_density: PixelDensityStatus = Field(default_factory=PixelDensityStatus)


class CameraOverlapResult(StrictModel):
    footprint_a: str
    footprint_b: str
    intersection_area_m2: float
    wgs84_coordinates: list[list[tuple[float, float]]] = Field(default_factory=list)


class PriorityAreaCoverageSummary(StrictModel):
    priority_area_id: str
    priority_area_name: str
    area_m2: float
    covered_area_m2: float
    covered_percentage: float
    intersecting_footprint_ids: list[str]
    warnings: list[str] = Field(default_factory=list)
    assumption: str = "Geometric flat-ground intersection only; percentage is not analytics quality."


class CameraGeometryLayer(StrictModel):
    geometry_model_version: Literal["flat-ground-pinhole-1.0.0"] = "flat-ground-pinhole-1.0.0"
    calculated_at: datetime | None = None
    projected_crs: str | None = None
    footprints: list[CameraFootprintResult] = Field(default_factory=list)
    overlaps: list[CameraOverlapResult] = Field(default_factory=list)
    priority_area_summaries: list[PriorityAreaCoverageSummary] = Field(default_factory=list)


class Project(StrictModel):
    schema_version: Literal["2.4.0"] = SCHEMA_VERSION
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
    priority_areas: list[PriorityArea] = Field(default_factory=list)
    calculation_areas: list[CalculationArea] = Field(default_factory=list)
    lighting_calculations: LightingCalculationLayer = Field(default_factory=LightingCalculationLayer)
    legacy_invalid_priority_areas: list[dict[str, Any]] = Field(default_factory=list)
    camera_geometry: CameraGeometryLayer = Field(default_factory=CameraGeometryLayer)
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
    phase: Literal[4] = 4
    version: str = SOFTWARE_VERSION


def migrate_project_payload(payload: dict[str, Any]) -> dict[str, Any]:
    """Migrate a portable Phase 1 project without guessing a fixture family."""
    version = payload.get("schema_version", "1.0.0")
    if version == SCHEMA_VERSION:
        return payload
    if version not in {"1.0.0", "2.0.0", "2.1.0", "2.2.0", "2.3.0"}:
        raise ValueError(f"Unsupported project schema version: {version}")
    migrated = dict(payload)
    migrated["schema_version"] = SCHEMA_VERSION
    migrated["software_version"] = SOFTWARE_VERSION
    migrated["legacy_fixture_assignments_require_model_selection"] = True
    migrated.setdefault("priority_areas", [])
    migrated.setdefault("calculation_areas", [])
    migrated.setdefault("lighting_calculations", {})
    migrated.setdefault("legacy_invalid_priority_areas", [])
    if version == "2.2.0":
        valid_areas: list[dict[str, Any]] = []
        legacy_areas = list(migrated["legacy_invalid_priority_areas"])
        for area in migrated["priority_areas"]:
            try:
                PriorityArea.model_validate(area)
                valid_areas.append(area)
            except ValueError:
                legacy_areas.append(area)
        migrated["priority_areas"] = valid_areas
        migrated["legacy_invalid_priority_areas"] = legacy_areas
    migrated.setdefault("camera_geometry", {})
    layer_state = dict(migrated.get("layer_state", {}))
    layer_state.setdefault("camera_overlap", True)
    layer_state.setdefault("priority_areas", True)
    layer_state.setdefault("calculation_areas", True)
    layer_state.setdefault("calculation_points", True)
    layer_state.setdefault("lighting_heat_map", True)
    migrated["layer_state"] = layer_state
    assumptions = list(migrated.get("assumptions", []))
    notice = "Phase 1 fixture classifications were preserved; fixture family/model selection remains explicit."
    if notice not in assumptions:
        assumptions.append(notice)
    if migrated["legacy_invalid_priority_areas"]:
        assumptions.append("Invalid legacy Phase 3 priority-area records are preserved losslessly but quarantined from calculations until explicitly redrawn.")
    migrated["assumptions"] = assumptions
    return migrated
