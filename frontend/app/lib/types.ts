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
  longitude?: number | null;
  latitude?: number | null;
  location_edit_authorized: boolean;
  modified_at?: string;
}

export interface Project {
  schema_version: "1.0.0";
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
  assumptions: string[];
  calculated_layers: Record<string, unknown>;
  recommended_layers: Record<string, unknown>;
  source_references: Record<string, string>;
}

export interface EffectivePole extends SourcePole {
  displayName: string;
  externalId: string;
  fixtureType: FixtureType;
  heightM: number | null;
  active: boolean;
  engineeringNotes: string;
  modified: boolean;
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
  };
}
