export const OSM_ATTRIBUTION: string;
export const SATELLITE_NOT_CONFIGURED: string;
export const SATELLITE_LOAD_FAILED: string;
export const USE_STANDARD_MAP_LABEL: string;

export type SatelliteRasterConfig = {
  tiles: string[];
  tileSize: number;
  minZoom: number;
  maxZoom: number;
  attribution: string;
};

export type BackgroundChoice = "standard" | "satellite";

export type BackgroundAvailability =
  | { available: true; attribution: string }
  | { available: false; reason: string };

export function backgroundAvailability(
  config: SatelliteRasterConfig | null | undefined,
): BackgroundAvailability;

export function readSatelliteConfigFromEnv(
  env?: NodeJS.ProcessEnv | Record<string, string | undefined>,
): SatelliteRasterConfig | null;

export function requestBackground(
  requested: BackgroundChoice,
  availability: BackgroundAvailability,
): { choice: BackgroundChoice; error: string | null };

export function sessionBackground(input: {
  choice: BackgroundChoice;
  availability: BackgroundAvailability;
  tileFailed: boolean;
}): {
  choice: BackgroundChoice;
  visible: BackgroundChoice;
  attribution: string;
  error: string | null;
  offerUseStandard: boolean;
};

export function backgroundLayerVisibility(visible: BackgroundChoice): {
  osm: "visible" | "none";
  satellite: "visible" | "none";
};

export function rasterSourceSpec(config: SatelliteRasterConfig): {
  type: "raster";
  tiles: string[];
  tileSize: number;
  minzoom: number;
  maxzoom: number;
  attribution: string;
};

export function isSatelliteTileError(event: unknown): boolean;
