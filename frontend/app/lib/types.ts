export type FixtureType = "LITE" | "WIFI" | "SMART";
export type WarningSeverity = "info" | "warning" | "error";

export interface ProjectWarning {
  code: string;
  severity: WarningSeverity;
  message: string;
  pole_ids: string[];
  details: Record<string, unknown>;
}

export interface SourceFile {
  filename: string;
  media_type: string;
  sha256: string;
  size_bytes: number;
  imported_at: string;
  source_crs: "EPSG:4326";
  kml_entry: string | null;
  content_base64: string;
}

export interface SourcePole {
  id: string;
  sequence_index: number;
  source_placemark_id: string | null;
  name: string;
  folder_path: string[];
  description: string;
  extended_data: Record<string, string>;
  source_style_url: string | null;
  source_style_color: string | null;
  longitude: number;
  latitude: number;
  altitude_m: number | null;
  raw_coordinates: string;
}

export interface PoleEdit {
  pole_id: string;
  display_name?: string | null;
  external_id?: string | null;
  fixture_type?: FixtureType | null;
  height_m?: number | null;
  active?: boolean | null;
  engineering_notes?: string | null;
  fixture_configuration?: PoleFixtureConfiguration | null;
  longitude?: number | null;
  latitude?: number | null;
  location_edit_authorized: boolean;
  modified_at?: string;
}

export interface Project {
  schema_version: "2.4.0";
  software_version: string;
  id: string;
  name: string;
  created_at: string;
  updated_at: string;
  mode: "existing-poles" | "proposed-layout";
  proposed_layout_authorized: boolean;
  source_crs: "EPSG:4326";
  projected_crs: string | null;
  defaults: {
    fixture_type: FixtureType;
    pole_height_m: number | null;
    maintenance_factor: number;
    calculation_plane_height_m: number;
    wifi_radius_m: number;
    camera_downward_angle_deg: number;
  };
  source: {
    file: SourceFile | null;
    document_name: string | null;
    poles: SourcePole[];
    unsupported_geometry_count: number;
  };
  pole_edits: Record<string, PoleEdit>;
  layer_state: Record<string, boolean>;
  warnings: ProjectWarning[];
  priority_areas: PriorityArea[];
  calculation_areas: CalculationArea[];
  lighting_calculations: LightingCalculationLayer;
  legacy_invalid_priority_areas: Array<Record<string, unknown>>;
  camera_geometry: CameraGeometryLayer;
  assumptions: string[];
  calculated_layers: Record<string, unknown>;
  recommended_layers: Record<string, unknown>;
  source_references: Record<string, string>;
  legacy_fixture_assignments_require_model_selection: boolean;
}

export interface PriorityArea { id: string; name: string; wgs84_coordinates: Array<[number, number]>; created_at: string; modified_at: string }
export type CalculationAreaClassification = "ROAD" | "SIDEWALK" | "PARKING" | "OTHER";
export interface CalculationArea {
  id: string; name: string; classification: CalculationAreaClassification; wgs84_coordinates: Array<[number, number]>;
  calculation_plane_elevation_m: number; grid_spacing_m: number; maintenance_factor: number; created_at: string; modified_at: string;
  calculation_state: { status: "not-calculated" | "calculated" | "warning" | "error"; polygon_revision: number; last_calculated_at: string | null; warnings: string[]; assumptions: string[]; provenance: Record<string, unknown> };
}
export interface LightingCalculationPoint { id: string; sequence_index: number; projected_coordinate_m: [number, number]; wgs84_coordinate: [number, number]; calculation_plane_elevation_m: number; maintained_horizontal_illuminance_lux: number; per_fixture_contributions_lux: Record<string, number> | null; warnings: string[] }
export interface LightingCalculationResult {
  calculation_area_id: string; calculation_area_name: string; calculation_model_version: "direct-horizontal-type-c-1.0.0"; calculated_at: string;
  polygon_revision: number; projected_crs: string; calculation_input_sha256: string | null; grid_origin_m: [number, number]; grid_anchor_policy: string; boundary_policy: string;
  points: LightingCalculationPoint[]; statistics: { point_count: number; grid_spacing_m: number; average_illuminance_lux: number | null; minimum_illuminance_lux: number | null; maximum_illuminance_lux: number | null; emin_over_eavg: number | null; emin_over_emax: number | null };
  contributing_fixture_count: number; fixture_provenance: Array<{ pole_id: string; fixture_model_id: string; fixture_model_revision: number; ies_file_id: string; ies_file_revision: number; ies_sha256: string; ies_original_filename: string; ies_parsed_metadata: { input_watts?: number; photometric_type?: string; vertical_angle_count?: number; horizontal_angle_count?: number }; mounting_height_m: number; fixture_azimuth_deg: number; origin_projected_m: [number, number, number]; warnings: string[] }>;
  assumptions: string[]; warnings: string[]; disclaimer: string;
}
export interface LightingCalculationLayer { calculation_model_version: "direct-horizontal-type-c-1.0.0"; results: Record<string, LightingCalculationResult> }
export interface CameraFootprintResult {
  pole_id: string; fixture_model_id: string; fixture_model_revision: number; mounting_template_revision: number;
  camera_slot_id: string; camera_model_id: string | null; camera_model_revision: number | null; lens_id: string | null; lens_revision: number | null;
  horizontal_fov_deg: number | null; vertical_fov_deg: number | null;
  fixture_height_m: number | null; fixture_azimuth_deg: number; template_relative_azimuth_deg: number; fixed_downward_tilt_deg: number;
  camera_absolute_azimuth_deg: number; origin_offset_xyz_m: [0, 0, 0]; geometry_contract_version: string | null; projected_crs: string | null; geometry_model_version: "flat-ground-pinhole-1.0.0";
  enabled: boolean; valid: boolean; warnings: string[]; assumptions: string[]; projected_coordinates_m: Array<[number, number]> | null;
  wgs84_coordinates: Array<[number, number]> | null; footprint_area_m2: number | null;
  pixel_density: { method: "not-calculated"; value: null; units: null; reason: string };
}
export interface CameraGeometryLayer {
  geometry_model_version: "flat-ground-pinhole-1.0.0"; calculated_at: string | null; projected_crs: string | null;
  footprints: CameraFootprintResult[];
  overlaps: Array<{ footprint_a: string; footprint_b: string; intersection_area_m2: number; wgs84_coordinates: Array<Array<[number, number]>> }>;
  priority_area_summaries: Array<{ priority_area_id: string; priority_area_name: string; area_m2: number; covered_area_m2: number; covered_percentage: number; intersecting_footprint_ids: string[]; warnings: string[]; assumption: string }>;
}

export interface PoleCameraOverride {
  slot_id: string;
  camera_model_id?: string | null;
  camera_model_revision?: number | null;
  lens_id?: string | null;
  lens_revision?: number | null;
  enabled?: boolean | null;
  relative_azimuth_deg?: number | null;
  downward_tilt_deg?: number | null;
  metadata?: Record<string, unknown>;
}

export interface PoleFixtureConfiguration {
  fixture_model_id: string;
  fixture_model_revision: number;
  mounting_template_revision: number | null;
  ies_file_id: string | null;
  ies_file_revision: number | null;
  fixture_azimuth_deg: number;
  lighting_properties: Record<string, unknown>;
  wifi_configuration: Record<string, unknown> | null;
  camera_overrides: Record<string, PoleCameraOverride>;
}

export interface CameraMountingSlot {
  id: string;
  display_name: string;
  relative_azimuth_deg: number;
  downward_tilt_deg: number;
  camera_model_id: string | null;
  camera_model_revision: number | null;
  lens_id: string | null;
  lens_revision: number | null;
  enabled: boolean;
  origin_offset_x_m: 0;
  origin_offset_y_m: 0;
  origin_offset_z_m: 0;
  metadata: Record<string, unknown>;
}

export interface FixtureModel {
  id: string;
  display_name: string;
  fixture_family: string;
  capability_variant: FixtureType;
  capabilities: { lighting: boolean; wifi: boolean; cameras: boolean; camera_slot_count: number };
  manufacturer: string | null;
  model_metadata: Record<string, unknown>;
  electrical_properties: Record<string, unknown>;
  photometric_properties: Record<string, unknown>;
  compatible_ies_file_ids: string[];
  default_ies_file_id: string | null;
  mounting_template_revisions: Array<{ revision: number; created_at: string; notes: string; geometry_contract_version: "fixed-zero-origin-1.0.0" | null; slots: CameraMountingSlot[] }>;
  current_mounting_template_revision: number | null;
  active: boolean;
  revision: number;
}

export interface FixtureModelCatalog { schema_version: "1.2.0"; catalog_id: string; fixture_models: FixtureModel[]; fixture_model_history: FixtureModel[] }
export interface CameraModel { id: string; display_name: string; manufacturer: string | null; sensor: string | null; resolution_width_px: number | null; resolution_height_px: number | null; compatible_lens_ids: string[]; technical_properties: Record<string, unknown>; source_reference_id: string | null; active: boolean; revision: number }
export interface LensConfiguration { id: string; display_name: string; focal_length_mm: number | null; horizontal_fov_deg: number | null; vertical_fov_deg: number | null; compatible_camera_model_ids: string[]; technical_properties: Record<string, unknown>; source_reference_id: string | null; active: boolean; revision: number }
export interface CameraEquipmentCatalog { schema_version: "1.1.0"; catalog_id: string; camera_models: CameraModel[]; lenses: LensConfiguration[]; camera_model_history: CameraModel[]; lens_history: LensConfiguration[] }
export interface IesFileRecord { id: string; original_filename: string; sha256: string; uploaded_at: string; ies_format_version: string; parsed_metadata: Record<string, unknown> | null; validation_status: "valid" | "invalid" | "unsupported"; validation_errors: string[]; validation_warnings: string[]; active: boolean; revision: number }
export interface IesLibrary { schema_version: "1.2.0"; catalog_id: string; files: IesFileRecord[]; file_history: IesFileRecord[]; fixture_associations: Array<{ ies_file_id: string; fixture_model_id: string; active: boolean }> }

export interface EffectivePole extends SourcePole {
  displayName: string;
  externalId: string;
  fixtureType: FixtureType;
  heightM: number | null;
  active: boolean;
  engineeringNotes: string;
  modified: boolean;
  fixtureConfiguration: PoleFixtureConfiguration | null;
}

export function effectivePole(project: Project, pole: SourcePole): EffectivePole {
  const edit = project.pole_edits[pole.id];
  return {
    ...pole,
    displayName: edit?.display_name ?? pole.name,
    externalId: edit?.external_id ?? pole.source_placemark_id ?? "",
    fixtureType: edit?.fixture_type ?? project.defaults.fixture_type,
    heightM: edit?.height_m ?? project.defaults.pole_height_m,
    active: edit?.active ?? true,
    engineeringNotes: edit?.engineering_notes ?? "",
    modified: Boolean(edit),
    fixtureConfiguration: edit?.fixture_configuration ?? null,
  };
}
