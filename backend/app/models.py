from __future__ import annotations

import base64
import binascii
import hashlib
import math
from datetime import datetime, timezone
from enum import Enum
from typing import Annotated, Any, Literal
from uuid import uuid4

from pydantic import AfterValidator, BaseModel, ConfigDict, Field, field_validator, model_validator
from shapely.geometry import Polygon
from shapely.validation import explain_validity

from app.crs import validate_projected_metre_crs


SCHEMA_VERSION = "2.7.0"
SOFTWARE_VERSION = "0.7.0"
REPORT_MODEL_VERSION = "report-package-1.0.0"
WIFI_MODEL_VERSION = "conceptual-circle-1.0.0"
MAX_REPORT_PACKAGE_BYTES = 50 * 1024 * 1024
MAX_REPORT_MEMBER_BYTES = 25 * 1024 * 1024
MAX_REPORT_TABULAR_ROWS = 250_000
MAX_REPORT_KML_FEATURES = 100_000
MAX_REPORT_PDF_TABLE_ROWS = 20_000
MAX_REPORT_SHEETS = 100
MAX_REPORT_SHEET_NAME_LEN = 31
MAX_REPORT_CELL_CHARS = 2_000
WIFI_RING_RESOLUTION = 32
MAX_WIFI_CIRCLES = 500
MAX_WIFI_CIRCLE_VERTICES = 64500
MAX_WIFI_CANDIDATE_OPERATIONS = 50000
MAX_WIFI_ANALYSIS_AREAS = 200
MAX_WIFI_AREA_VERTICES = 10000
MAX_WIFI_TOTAL_GEOMETRY_VERTICES = 250000
WIFI_INTERSECTION_TOLERANCE_M2 = 1e-8
MIN_GRID_SPACING_M = 0.01


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


class StrictModel(BaseModel):
    model_config = ConfigDict(extra="forbid", validate_assignment=True, allow_inf_nan=False)


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


class PoleWifiConfiguration(StrictModel):
    radius_override_m: Annotated[float | None, Field(gt=0, le=1000)] = None
    enabled: bool | None = None
    notes: str = ""
    modified_at: datetime = Field(default_factory=utc_now)
    configuration_revision: Annotated[int, Field(ge=1)] = 1
    legacy_metadata: dict[str, Any] = Field(default_factory=dict)


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
    wifi_configuration: PoleWifiConfiguration | None = None
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
    grid_spacing_m: Annotated[float, Field(ge=MIN_GRID_SPACING_M, le=1000)] = 2.0
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


class WifiAnalysisArea(StrictModel):
    id: Annotated[str, Field(min_length=1, max_length=120)]
    name: Annotated[str, Field(min_length=1, max_length=120)]
    wgs84_coordinates: Annotated[list[tuple[float, float]], Field(min_length=4)]
    created_at: datetime = Field(default_factory=utc_now)
    modified_at: datetime = Field(default_factory=utc_now)
    polygon_revision: Annotated[int, Field(ge=1)] = 1

    @model_validator(mode="after")
    def validate_polygon(self) -> "WifiAnalysisArea":
        if len(self.wgs84_coordinates) > MAX_WIFI_AREA_VERTICES + 1:
            raise ValueError(f"Wi-Fi analysis area exceeds the {MAX_WIFI_AREA_VERTICES:,}-vertex limit")
        if self.wgs84_coordinates[0] != self.wgs84_coordinates[-1]:
            raise ValueError("Wi-Fi analysis-area polygon must be closed")
        if len(set(self.wgs84_coordinates[:-1])) < 3:
            raise ValueError("Wi-Fi analysis-area polygon requires three distinct vertices")
        for longitude, latitude in self.wgs84_coordinates:
            if not math.isfinite(longitude) or not math.isfinite(latitude):
                raise ValueError("Wi-Fi analysis-area coordinates must be finite")
            if not (-180 <= longitude <= 180 and -90 <= latitude <= 90):
                raise ValueError("Wi-Fi analysis-area coordinate is outside WGS84 bounds")
        polygon = Polygon(self.wgs84_coordinates)
        if not polygon.is_valid:
            raise ValueError(f"Wi-Fi analysis-area polygon is invalid: {explain_validity(polygon)}")
        if polygon.area <= 1e-18:
            raise ValueError("Wi-Fi analysis-area polygon is degenerate and has no usable area")
        return self


class WifiCoverageState(StrictModel):
    status: Literal["not-calculated", "calculated", "warning", "error"] = "not-calculated"
    last_calculated_at: datetime | None = None
    warnings: list[str] = Field(default_factory=list)
    assumptions: list[str] = Field(default_factory=list)
    provenance: dict[str, Any] = Field(default_factory=dict)
    calculation_input_sha256: Annotated[str | None, Field(pattern=r"^[0-9a-f]{64}$")] = None
    model_version: Literal["conceptual-circle-1.0.0"] = WIFI_MODEL_VERSION


class WifiCircle(StrictModel):
    id: str
    pole_id: str
    effective_fixture_type: FixtureType
    center_projected_m: tuple[float, float]
    source_wgs84_coordinate: tuple[float, float]
    effective_wgs84_coordinate: tuple[float, float]
    projected_ring: list[tuple[float, float]] = Field(min_length=129, max_length=129)
    wgs84_ring: list[tuple[float, float]] = Field(min_length=129, max_length=129)
    effective_radius_m: Annotated[float, Field(gt=0, le=1000)]
    enabled: bool
    eligible: bool
    area_m2: float
    approximation_resolution: Literal[32] = 32
    source_provenance: dict[str, Any] = Field(default_factory=dict)
    warnings: list[str] = Field(default_factory=list)


class WifiGlobalStatistics(StrictModel):
    circle_count: int = 0
    individual_area_m2: float = 0.0
    union_covered_area_m2: float = 0.0
    overlap_area_m2: float = 0.0
    pairwise_overlap_area_m2: float = 0.0
    multiply_covered_union_area_m2: float = 0.0
    overlap_pair_count: int = 0
    union_over_individual_percentage: float | None = None


class WifiAnalysisAreaStatistics(StrictModel):
    analysis_area_id: str
    analysis_area_name: str
    area_m2: float
    covered_area_m2: float
    uncovered_area_m2: float
    covered_percentage: float
    uncovered_percentage: float
    boundary_covered_length_m: float
    boundary_covered_percentage: float


class WifiCoverageResult(StrictModel):
    model_version: Literal["conceptual-circle-1.0.0"] = WIFI_MODEL_VERSION
    calculated_at: datetime = Field(default_factory=utc_now)
    projected_crs: str
    approximation_resolution: Literal[32] = 32
    circles: list[WifiCircle] = Field(default_factory=list)
    global_statistics: WifiGlobalStatistics
    analysis_area_statistics: list[WifiAnalysisAreaStatistics] = Field(default_factory=list)
    calculation_input_sha256: Annotated[str, Field(pattern=r"^[0-9a-f]{64}$")]
    warnings: list[str] = Field(default_factory=list)
    assumptions: list[str] = Field(default_factory=list)
    disclaimer: Literal["Conceptual geometric visualization only; not verified RF coverage, performance, capacity, service quality, or standards compliance."] = "Conceptual geometric visualization only; not verified RF coverage, performance, capacity, service quality, or standards compliance."


class WifiCoverageLayer(StrictModel):
    model_version: Literal["conceptual-circle-1.0.0"] = WIFI_MODEL_VERSION
    state: WifiCoverageState = Field(default_factory=WifiCoverageState)
    result: WifiCoverageResult | None = None


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
    calculation_input_sha256: Annotated[str | None, Field(pattern=r"^[0-9a-f]{64}$")] = None
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
    calculation_input_sha256: Annotated[str | None, Field(pattern=r"^[0-9a-f]{64}$")] = None
    footprints: list[CameraFootprintResult] = Field(default_factory=list)
    overlaps: list[CameraOverlapResult] = Field(default_factory=list)
    priority_area_summaries: list[PriorityAreaCoverageSummary] = Field(default_factory=list)


# Phase 6 deliberately keeps operational values nullable/unknown.  The supplied
# JNET1 evidence is not a Miracle Mile design approval.
class CapKnowledge(str, Enum):
    UNKNOWN = "unknown"
    KNOWN = "known"


class CapNodeDisposition(str, Enum):
    NODE = "node"
    NON_NODE = "non_node"
    UNKNOWN = "unknown"


class CapNodePolicy(StrictModel):
    LITE: CapNodeDisposition = CapNodeDisposition.UNKNOWN
    WIFI: CapNodeDisposition = CapNodeDisposition.UNKNOWN
    SMART: CapNodeDisposition = CapNodeDisposition.UNKNOWN


class CapConstraintValue(StrictModel):
    status: CapKnowledge = CapKnowledge.UNKNOWN
    value: str | float | int | bool | None = None
    unit: str | None = None
    classification: Literal["legal_regulatory_requirement", "manufacturer_hard_constraint", "manufacturer_guidance", "project_design_limit", "user_approved_assumption", "derived_value", "unknown"] = "unknown"
    source: str | None = None
    approver: str | None = None
    date: str | None = None
    applicability: str | None = None
    revision: str | None = None
    conflict_state: Literal["none", "unresolved"] = "none"
    notes: str = ""

    @model_validator(mode="after")
    def known_values_are_traceable(self) -> "CapConstraintValue":
        if self.status is CapKnowledge.UNKNOWN and self.value is not None:
            raise ValueError("unknown CAP values cannot carry an operational value")
        if self.status is CapKnowledge.KNOWN and (self.value is None or not self.source or not self.applicability):
            raise ValueError("known CAP values require value, source, and applicability provenance")
        return self


class CapCandidateSite(StrictModel):
    id: Annotated[str, Field(min_length=1, max_length=120)]
    kind: Literal["existing_pole", "manual_non_pole"]
    pole_id: str | None = None
    wgs84_coordinate: tuple[float, float] | None = None
    mounting_confirmed: bool | None = None
    power_confirmed: bool | None = None
    backhaul_confirmed: bool | None = None
    enclosure_confirmed: bool | None = None
    indoor_outdoor: Literal["indoor", "outdoor", "unknown"] = "unknown"
    mounting_height_m: float | None = Field(default=None, ge=0, le=500)
    survey_status: Literal["confirmed", "unknown", "failed"] = "unknown"
    priority: Annotated[int, Field(ge=0, le=100000)] = 1000
    notes: Annotated[str, Field(max_length=2000)] = ""
    revision: Annotated[int, Field(ge=1)] = 1
    created_at: datetime = Field(default_factory=utc_now)
    modified_at: datetime = Field(default_factory=utc_now)
    prohibited: bool = False
    preferred: bool = False
    locked_selected: bool = False

    @model_validator(mode="after")
    def identity_is_explicit(self) -> "CapCandidateSite":
        if self.kind == "existing_pole" and (not self.pole_id or self.wgs84_coordinate is not None):
            raise ValueError("existing-pole CAP candidates require only a source pole ID")
        if self.kind == "manual_non_pole" and (self.pole_id is not None or self.wgs84_coordinate is None):
            raise ValueError("manual non-pole CAP candidates require only an explicit coordinate")
        if self.wgs84_coordinate and not all(math.isfinite(value) for value in self.wgs84_coordinate):
            raise ValueError("manual CAP coordinates must be finite")
        if self.wgs84_coordinate and not (-180 <= self.wgs84_coordinate[0] <= 180 and -90 <= self.wgs84_coordinate[1] <= 90):
            raise ValueError("manual CAP coordinate is outside WGS84 bounds")
        return self


class CapPlanningProfile(StrictModel):
    model_version: Literal["jnet1-graph-planning-1.0.0"] = "jnet1-graph-planning-1.0.0"
    operation_mode: Literal["validate", "recommend"] = "recommend"
    product_mapping: CapConstraintValue = Field(default_factory=CapConstraintValue)
    variant: CapConstraintValue = Field(default_factory=CapConstraintValue)
    band_and_jurisdiction: CapConstraintValue = Field(default_factory=CapConstraintValue)
    link_distance_m: CapConstraintValue = Field(default_factory=CapConstraintValue)
    node_limit: CapConstraintValue = Field(default_factory=CapConstraintValue)
    child_limit: CapConstraintValue = Field(default_factory=CapConstraintValue)
    hop_limit: CapConstraintValue = Field(default_factory=CapConstraintValue)
    gateway_appliance_counting: CapConstraintValue = Field(default_factory=CapConstraintValue)
    colocated_fixture_counting: CapConstraintValue = Field(default_factory=CapConstraintValue)
    redundancy: CapConstraintValue = Field(default_factory=CapConstraintValue)
    node_policy: CapNodePolicy = Field(default_factory=CapNodePolicy)
    mode_permission: Literal["validate_only", "recommend_from_approved_pool", "unknown"] = "unknown"
    auto_assign_unlocked_nodes: bool = False
    disclaimer: Literal["Distance-qualified conceptual link; not RF-predicted. Graph-and-constraint planning only; not coverage, capacity, performance, service quality, installation feasibility, or compliance."] = "Distance-qualified conceptual link; not RF-predicted. Graph-and-constraint planning only; not coverage, capacity, performance, service quality, installation feasibility, or compliance."


class CapPlanningInputs(StrictModel):
    profile: CapPlanningProfile = Field(default_factory=CapPlanningProfile)
    candidates: list[CapCandidateSite] = Field(default_factory=list)
    excluded_node_ids: list[str] = Field(default_factory=list)
    excluded_candidate_ids: list[str] = Field(default_factory=list)
    locked_selected_candidate_ids: list[str] = Field(default_factory=list)
    primary_assignment_locks: dict[str, str] = Field(default_factory=dict)
    parent_locks: dict[str, str] = Field(default_factory=dict)


class CapManualConstraints(StrictModel):
    excluded_node_ids: list[str] = Field(default_factory=list)
    excluded_candidate_ids: list[str] = Field(default_factory=list)
    locked_selected_candidate_ids: list[str] = Field(default_factory=list)
    primary_assignment_locks: dict[str, str] = Field(default_factory=dict)
    parent_locks: dict[str, str] = Field(default_factory=dict)


class CapAssignment(StrictModel):
    node_id: str
    gateway_id: str
    parent_id: str
    hop: Annotated[int, Field(ge=1, le=64)]
    distance_m: Annotated[float, Field(ge=0)]


class CapScoreTrace(StrictModel):
    candidate_id: str
    marginal_serviceable_nodes: Annotated[int, Field(ge=0)]
    priority: Annotated[int, Field(ge=0)]


class CapGraphLink(StrictModel):
    id: str
    left_id: str
    right_id: str
    distance_m: Annotated[float, Field(ge=0)]


class CapVertexSnapshot(StrictModel):
    id: str
    kind: Literal["fixture_node", "gateway_root"]
    source_pole_id: str | None = None
    candidate_id: str | None = None
    projected_x_m: float
    projected_y_m: float


class CapPlanningLimits(StrictModel):
    link_distance_m: Annotated[float, Field(gt=0)]
    node_limit: Annotated[int, Field(ge=1, le=1000)]
    child_limit: Annotated[int, Field(ge=1, le=16)]
    hop_limit: Annotated[int, Field(ge=1, le=64)]
    edge_evaluations: Annotated[int, Field(ge=0)]
    canonical_link_count: Annotated[int, Field(ge=0)]
    improvement_passes: Annotated[int, Field(ge=1)]


class CapPlanningResult(StrictModel):
    model_version: Literal["jnet1-graph-planning-1.0.0"] = "jnet1-graph-planning-1.0.0"
    projected_crs: str
    disclaimer: str
    heuristic: str
    selected_candidate_ids: list[str] = Field(default_factory=list)
    assignments: list[CapAssignment] = Field(default_factory=list)
    canonical_links: list[CapGraphLink] = Field(default_factory=list)
    node_snapshots: list[CapVertexSnapshot] = Field(default_factory=list)
    candidate_snapshots: list[CapVertexSnapshot] = Field(default_factory=list)
    unresolved_node_ids: list[str] = Field(default_factory=list)
    objective_trace: list[CapScoreTrace] = Field(default_factory=list)
    limits: CapPlanningLimits
    provenance: dict[str, Any] = Field(default_factory=dict)
    warnings: list[str] = Field(default_factory=list)
    result_sha256: str


class CapPlanningLayer(StrictModel):
    status: Literal["not-calculated", "calculated", "error"] = "not-calculated"
    calculation_input_sha256: str | None = None
    calculated_at: datetime | None = None
    result: CapPlanningResult | None = None
    warnings: list[str] = Field(default_factory=list)


class CapRecommendations(StrictModel):
    selected_candidate_ids: list[str] = Field(default_factory=list)
    result_sha256: str | None = None


class ReportSectionSelection(StrictModel):
    project_inventory: bool = True
    poles_fixtures: bool = True
    cameras: bool = True
    lighting: bool = True
    wifi: bool = True
    cap: bool = True
    warnings_assumptions: bool = True
    validation_findings: bool = True
    provenance: bool = True


class ReportFormatSelection(StrictModel):
    project_json: bool = True
    engineering_kmz: bool = True
    csv_schedules: bool = True
    xlsx_workbook: bool = True
    pdf_summary: bool = True
    presentation_model: bool = True


class ReportKmzLayerSelection(StrictModel):
    camera_geometry: bool = True
    lighting: bool = True
    wifi: bool = True
    cap: bool = True
    priority_areas: bool = True
    calculation_areas: bool = True
    wifi_analysis_areas: bool = True


class ReportPreferences(StrictModel):
    model_version: Literal["report-package-1.0.0"] = REPORT_MODEL_VERSION
    formats: ReportFormatSelection = Field(default_factory=ReportFormatSelection)
    sections: ReportSectionSelection = Field(default_factory=ReportSectionSelection)
    kmz_layers: ReportKmzLayerSelection = Field(default_factory=ReportKmzLayerSelection)


ReportStatus = Literal["complete", "complete_with_warnings", "incomplete"]
ReportSectionDisposition = Literal[
    "included",
    "omitted",
    "not_configured",
    "not_calculated",
    "stale_omitted",
    "disabled",
]


def validate_report_member_path(path: str) -> str:
    if path == "report-manifest.json":
        raise ValueError("report payload member path must not be the manifest self path")
    if "\\" in path:
        raise ValueError("report payload member path must use forward slashes")
    if any(ord(character) < 32 for character in path):
        raise ValueError("report payload member path must not contain control characters")
    if path.startswith("/") or (
        len(path) >= 3 and path[0].isalpha() and path[1] == ":" and path[2] == "/"
    ):
        raise ValueError("report payload member path must be relative")
    if any(segment in {"", ".", ".."} for segment in path.split("/")):
        raise ValueError("report payload member path contains an empty or dot segment")
    return path


ReportMemberPath = Annotated[
    str,
    Field(min_length=1),
    AfterValidator(validate_report_member_path),
]


class ReportMemberIntegrity(StrictModel):
    sha256: Annotated[str, Field(pattern=r"^[0-9a-f]{64}$")]
    size_bytes: Annotated[int, Field(ge=0, le=MAX_REPORT_MEMBER_BYTES)]


class ReportManifest(StrictModel):
    report_model_version: Literal["report-package-1.0.0"] = REPORT_MODEL_VERSION
    schema_version: Literal["2.7.0"] = SCHEMA_VERSION
    software_version: Literal["0.7.0"] = SOFTWARE_VERSION
    generator: Literal["lcwa-report-package"]
    project_id: str
    project_name: str
    generation_time: datetime
    status: ReportStatus
    report_input_sha256: Annotated[str, Field(pattern=r"^[0-9a-f]{64}$")]
    source_sha256: Annotated[str | None, Field(pattern=r"^[0-9a-f]{64}$")]
    formats: ReportFormatSelection
    sections: ReportSectionSelection
    kmz_layers: ReportKmzLayerSelection
    section_dispositions: dict[str, ReportSectionDisposition]
    included_sections: list[str]
    omitted_sections: list[str]
    warnings: list[str]
    validation_findings: list[str]
    members: dict[ReportMemberPath, ReportMemberIntegrity]
    disclaimer: str

    @model_validator(mode="after")
    def reject_manifest_self_entry(self) -> "ReportManifest":
        if "report-manifest.json" in self.members:
            raise ValueError("report manifest must not contain a self-entry")
        return self


class LastReportMetadata(StrictModel):
    model_version: Literal["report-package-1.0.0"] = REPORT_MODEL_VERSION
    generated_at: datetime
    status: ReportStatus
    report_input_sha256: Annotated[str, Field(pattern=r"^[0-9a-f]{64}$")]
    package_sha256: Annotated[str, Field(pattern=r"^[0-9a-f]{64}$")]
    package_size_bytes: Annotated[int, Field(ge=1, le=MAX_REPORT_PACKAGE_BYTES)]
    member_count: Annotated[int, Field(ge=1)]
    member_sha256: dict[str, Annotated[str, Field(pattern=r"^[0-9a-f]{64}$")]] = Field(default_factory=dict)
    included_sections: list[str] = Field(default_factory=list)
    omitted_sections: list[str] = Field(default_factory=list)
    warnings: list[str] = Field(default_factory=list)
    validation_finding_count: Annotated[int, Field(ge=0)] = 0


class ReportPackageRequest(StrictModel):
    """Synchronous report generation options. Defaults mirror project preferences when omitted by callers."""

    formats: ReportFormatSelection | None = None
    sections: ReportSectionSelection | None = None
    kmz_layers: ReportKmzLayerSelection | None = None
    persist_last_report_metadata: bool = True
    generation_time: datetime | None = None
    expected_project_updated_at: datetime | None = None


class PresentationInventory(StrictModel):
    pole_count: Annotated[int, Field(ge=0)]
    priority_area_count: Annotated[int, Field(ge=0)]
    calculation_area_count: Annotated[int, Field(ge=0)]
    wifi_analysis_area_count: Annotated[int, Field(ge=0)]
    cap_candidate_count: Annotated[int, Field(ge=0)]


class PresentationSubsystems(StrictModel):
    lighting_included_area_ids: list[str]
    wifi_included: bool
    cap_included: bool
    camera_included: bool


class PresentationModel(StrictModel):
    """Strict future presentation input — never a generated PPTX artifact."""

    kind: Literal["presentation-model"]
    label: str
    presentation_generated: Literal[False]
    pptx_supported: Literal[False]
    report_model_version: Literal["report-package-1.0.0"] = REPORT_MODEL_VERSION
    schema_version: Literal["2.7.0"] = SCHEMA_VERSION
    software_version: Literal["0.7.0"] = SOFTWARE_VERSION
    project_id: str
    project_name: str
    generation_time: str
    status: ReportStatus
    report_input_sha256: Annotated[str, Field(pattern=r"^[0-9a-f]{64}$")]
    section_dispositions: dict[str, ReportSectionDisposition]
    warnings: list[str]
    findings: list[str]
    inventory: PresentationInventory
    subsystems: PresentationSubsystems
    disclaimer: str


class Project(StrictModel):
    schema_version: Literal["2.7.0"] = SCHEMA_VERSION
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
    wifi_analysis_areas: list[WifiAnalysisArea] = Field(default_factory=list)
    wifi_coverage: WifiCoverageLayer = Field(default_factory=WifiCoverageLayer)
    cap_planning_inputs: CapPlanningInputs = Field(default_factory=CapPlanningInputs)
    cap_calculations: CapPlanningLayer = Field(default_factory=CapPlanningLayer)
    cap_recommendations: CapRecommendations = Field(default_factory=CapRecommendations)
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
    report_preferences: ReportPreferences = Field(default_factory=ReportPreferences)
    last_report: LastReportMetadata | None = None

    @field_validator("projected_crs")
    @classmethod
    def enforce_engineering_crs(cls, value: str | None) -> str | None:
        # Blank projects have no engineering CRS until a source is imported.
        if value is not None:
            validate_projected_metre_crs(value)
        return value

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
        candidate_ids = set()
        for candidate in self.cap_planning_inputs.candidates:
            if candidate.id in candidate_ids:
                raise ValueError(f"CAP candidate IDs must be unique: {candidate.id}")
            candidate_ids.add(candidate.id)
            if candidate.pole_id and candidate.pole_id not in source_ids:
                raise ValueError(f"CAP candidate references unknown source pole: {candidate.pole_id}")
        inputs = self.cap_planning_inputs
        node_ids = {f"fixture/{pole_id}" for pole_id in source_ids}
        unknown_nodes = set(inputs.excluded_node_ids) - node_ids
        unknown_candidates = (set(inputs.excluded_candidate_ids) | set(inputs.locked_selected_candidate_ids)) - candidate_ids
        if unknown_nodes:
            raise ValueError(f"CAP constraints reference unknown nodes: {sorted(unknown_nodes)}")
        if unknown_candidates:
            raise ValueError(f"CAP constraints reference unknown candidates: {sorted(unknown_candidates)}")
        for key, edit in self.pole_edits.items():
            if edit.pole_id != key:
                raise ValueError(f"pole edit key {key!r} does not match pole_id")
        if len(self.wifi_analysis_areas) > MAX_WIFI_ANALYSIS_AREAS:
            raise ValueError(f"Wi-Fi analysis areas exceed the {MAX_WIFI_ANALYSIS_AREAS:,}-area limit")
        total_area_vertices = sum(len(area.wgs84_coordinates) for area in self.wifi_analysis_areas)
        result_vertices = sum(len(circle.projected_ring) for circle in (self.wifi_coverage.result.circles if self.wifi_coverage.result else []))
        if result_vertices + total_area_vertices > MAX_WIFI_TOTAL_GEOMETRY_VERTICES:
            raise ValueError(f"Wi-Fi persisted geometry exceeds the {MAX_WIFI_TOTAL_GEOMETRY_VERTICES:,}-vertex limit")
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
    phase: Literal[7] = 7
    version: str = SOFTWARE_VERSION


def migrate_project_payload(payload: dict[str, Any]) -> dict[str, Any]:
    """Migrate a portable Phase 1 project without guessing a fixture family."""
    version = payload.get("schema_version", "1.0.0")
    if version == SCHEMA_VERSION:
        return payload
    if version not in {"1.0.0", "2.0.0", "2.1.0", "2.2.0", "2.3.0", "2.4.0", "2.5.0", "2.6.0"}:
        raise ValueError(f"Unsupported project schema version: {version}")
    migrated = dict(payload)
    migrated["schema_version"] = SCHEMA_VERSION
    migrated["software_version"] = SOFTWARE_VERSION
    migrated["legacy_fixture_assignments_require_model_selection"] = True
    migrated.setdefault("priority_areas", [])
    migrated.setdefault("calculation_areas", [])
    migrated.setdefault("lighting_calculations", {})
    migrated.setdefault("wifi_analysis_areas", [])
    migrated.setdefault("wifi_coverage", {})
    migrated.setdefault("cap_planning_inputs", {})
    migrated.setdefault("cap_calculations", {})
    migrated.setdefault("cap_recommendations", {})
    migrated.setdefault("legacy_invalid_priority_areas", [])
    migrated.setdefault("report_preferences", {})
    migrated.setdefault("last_report", None)
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
    wifi_coverage = dict(migrated.get("wifi_coverage", {}))
    wifi_coverage.setdefault("state", {})
    wifi_coverage.setdefault("result", None)
    migrated["wifi_coverage"] = wifi_coverage
    for edit in migrated.get("pole_edits", {}).values():
        config = edit.get("fixture_configuration") if isinstance(edit, dict) else None
        if not isinstance(config, dict) or "wifi_configuration" not in config:
            continue
        legacy = config.get("wifi_configuration")
        if isinstance(legacy, dict):
            known = {"radius_override_m", "enabled", "notes", "modified_at", "configuration_revision", "legacy_metadata"}
            metadata = dict(legacy.get("legacy_metadata", {}))
            metadata.update({key: value for key, value in legacy.items() if key not in known})
            config["wifi_configuration"] = {
                "radius_override_m": legacy.get("radius_override_m"),
                "enabled": legacy.get("enabled"),
                "notes": str(legacy.get("notes", "")),
                "modified_at": legacy.get("modified_at", edit.get("modified_at", utc_now().isoformat())),
                "configuration_revision": legacy.get("configuration_revision", 1),
                "legacy_metadata": metadata,
            }
    assumptions = list(migrated.get("assumptions", []))
    notice = "Phase 1 fixture classifications were preserved; fixture family/model selection remains explicit."
    if notice not in assumptions:
        assumptions.append(notice)
    if migrated["legacy_invalid_priority_areas"]:
        assumptions.append("Invalid legacy Phase 3 priority-area records are preserved losslessly but quarantined from calculations until explicitly redrawn.")
    wifi_notice = "Conceptual Wi-Fi circles are projected-plane geometry only and have not been calculated as verified RF coverage."
    if wifi_notice not in assumptions:
        assumptions.append(wifi_notice)
    migrated["assumptions"] = assumptions
    return migrated
