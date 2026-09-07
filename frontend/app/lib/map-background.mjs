/**
 * Session-only map background selection. Provider URLs stay in environment config.
 */

export const OSM_ATTRIBUTION = "© OpenStreetMap contributors";
export const SATELLITE_NOT_CONFIGURED = "Satellite imagery is not configured";
export const SATELLITE_LOAD_FAILED = "Satellite imagery could not be loaded. The standard map is still available.";
export const USE_STANDARD_MAP_LABEL = "Use standard map";

const TILE_PLACEHOLDERS = ["{z}", "{x}", "{y}"];

/**
 * @typedef {{ tiles: string[], tileSize: number, minZoom: number, maxZoom: number, attribution: string }} SatelliteRasterConfig
 * @typedef {{ available: true, attribution: string } | { available: false, reason: string }} BackgroundAvailability
 * @typedef {"standard" | "satellite"} BackgroundChoice
 */

/**
 * @param {unknown} config
 * @returns {string | null}
 */
function validationError(config) {
  if (config == null || typeof config !== "object") return SATELLITE_NOT_CONFIGURED;
  const record = /** @type {Record<string, unknown>} */ (config);
  const tiles = record.tiles;
  if (!Array.isArray(tiles) || tiles.length === 0 || tiles.some((item) => typeof item !== "string" || !item.trim())) {
    return "Satellite imagery is not configured";
  }
  for (const tile of tiles) {
    let parsed;
    try {
      parsed = new URL(tile.replaceAll("{z}", "0").replaceAll("{x}", "0").replaceAll("{y}", "0"));
    } catch {
      return "Satellite tile URL is invalid";
    }
    if (parsed.protocol !== "https:") return "Satellite tile URL must use HTTPS";
    if (parsed.username || parsed.password) return "Satellite tile URL must not include credentials";
    for (const token of TILE_PLACEHOLDERS) {
      if (!tile.includes(token)) return "Satellite tile URL must include {z}, {x}, and {y}";
    }
  }
  const tileSize = record.tileSize;
  if (!Number.isInteger(tileSize) || /** @type {number} */ (tileSize) <= 0) {
    return "Satellite tile size is invalid";
  }
  const minZoom = record.minZoom;
  const maxZoom = record.maxZoom;
  if (!Number.isInteger(minZoom) || !Number.isInteger(maxZoom) || minZoom < 0 || maxZoom < minZoom) {
    return "Satellite zoom range is invalid";
  }
  const attribution = typeof record.attribution === "string" ? record.attribution.trim() : "";
  if (!attribution) return "Satellite attribution is required";
  return null;
}

/**
 * @param {SatelliteRasterConfig | null | undefined} config
 * @returns {BackgroundAvailability}
 */
export function backgroundAvailability(config) {
  if (config == null) {
    return { available: false, reason: SATELLITE_NOT_CONFIGURED };
  }
  const reason = validationError(config);
  if (reason) return { available: false, reason };
  return { available: true, attribution: config.attribution.trim() };
}

/**
 * @param {NodeJS.ProcessEnv | Record<string, string | undefined> | undefined} env
 * @returns {SatelliteRasterConfig | null}
 */
export function readSatelliteConfigFromEnv(env) {
  const source = env ?? {};
  const tiles = typeof source.NEXT_PUBLIC_SATELLITE_TILES === "string" ? source.NEXT_PUBLIC_SATELLITE_TILES.trim() : "";
  const tileSizeRaw = typeof source.NEXT_PUBLIC_SATELLITE_TILE_SIZE === "string" ? source.NEXT_PUBLIC_SATELLITE_TILE_SIZE.trim() : "";
  const minZoomRaw = typeof source.NEXT_PUBLIC_SATELLITE_MIN_ZOOM === "string" ? source.NEXT_PUBLIC_SATELLITE_MIN_ZOOM.trim() : "";
  const maxZoomRaw = typeof source.NEXT_PUBLIC_SATELLITE_MAX_ZOOM === "string" ? source.NEXT_PUBLIC_SATELLITE_MAX_ZOOM.trim() : "";
  const attribution = typeof source.NEXT_PUBLIC_SATELLITE_ATTRIBUTION === "string" ? source.NEXT_PUBLIC_SATELLITE_ATTRIBUTION.trim() : "";
  if (!tiles && !tileSizeRaw && !minZoomRaw && !maxZoomRaw && !attribution) return null;
  return {
    tiles: tiles ? [tiles] : [],
    tileSize: tileSizeRaw === "" ? Number.NaN : Number(tileSizeRaw),
    minZoom: minZoomRaw === "" ? Number.NaN : Number(minZoomRaw),
    maxZoom: maxZoomRaw === "" ? Number.NaN : Number(maxZoomRaw),
    attribution,
  };
}

/**
 * @param {BackgroundChoice} requested
 * @param {BackgroundAvailability} availability
 * @returns {{ choice: BackgroundChoice, error: string | null }}
 */
export function requestBackground(requested, availability) {
  if (requested === "satellite" && !availability.available) {
    return { choice: "standard", error: availability.reason };
  }
  return { choice: requested, error: null };
}

/**
 * @param {{ choice: BackgroundChoice, availability: BackgroundAvailability, tileFailed: boolean }} input
 */
export function sessionBackground({ choice, availability, tileFailed }) {
  if (choice !== "satellite") {
    return {
      choice: "standard",
      visible: "standard",
      attribution: OSM_ATTRIBUTION,
      error: null,
      offerUseStandard: false,
    };
  }
  if (!availability.available) {
    return {
      choice: "standard",
      visible: "standard",
      attribution: OSM_ATTRIBUTION,
      error: availability.reason,
      offerUseStandard: true,
    };
  }
  if (tileFailed) {
    return {
      choice: "satellite",
      visible: "standard",
      attribution: OSM_ATTRIBUTION,
      error: SATELLITE_LOAD_FAILED,
      offerUseStandard: true,
    };
  }
  return {
    choice: "satellite",
    visible: "satellite",
    attribution: availability.attribution,
    error: null,
    offerUseStandard: false,
  };
}

/**
 * @param {"standard" | "satellite"} visible
 */
export function backgroundLayerVisibility(visible) {
  return {
    osm: visible === "standard" ? "visible" : "none",
    satellite: visible === "satellite" ? "visible" : "none",
  };
}

/**
 * @param {SatelliteRasterConfig} config
 */
export function rasterSourceSpec(config) {
  return {
    type: "raster",
    tiles: config.tiles,
    tileSize: config.tileSize,
    minzoom: config.minZoom,
    maxzoom: config.maxZoom,
    attribution: config.attribution,
  };
}

/**
 * @param {unknown} event
 */
export function isSatelliteTileError(event) {
  if (!event || typeof event !== "object") return false;
  const record = /** @type {{ sourceId?: unknown, source?: { id?: unknown } }} */ (event);
  return record.sourceId === "satellite" || record.source?.id === "satellite";
}
