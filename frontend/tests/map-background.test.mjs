import test from "node:test";
import assert from "node:assert/strict";
import { readFile } from "node:fs/promises";
import {
  OSM_ATTRIBUTION,
  SATELLITE_LOAD_FAILED,
  USE_STANDARD_MAP_LABEL,
  backgroundAvailability,
  backgroundLayerVisibility,
  readSatelliteConfigFromEnv,
  requestBackground,
  sessionBackground,
  rasterSourceSpec,
  isSatelliteTileError,
} from "../app/lib/map-background.mjs";

const VALID_FIXTURE = {
  tiles: ["https://imagery.invalid/{z}/{x}/{y}.png"],
  tileSize: 256,
  minZoom: 0,
  maxZoom: 18,
  attribution: "Test attribution",
};

test("null configuration is unavailable with the required reason", () => {
  assert.deepEqual(backgroundAvailability(null), {
    available: false,
    reason: "Satellite imagery is not configured",
  });
});

test("valid configuration is available with its attribution", () => {
  assert.deepEqual(backgroundAvailability(VALID_FIXTURE), {
    available: true,
    attribution: "Test attribution",
  });
});

test("rejects missing placeholders, http tiles, credentials, and bad numeric ranges", () => {
  assert.equal(backgroundAvailability({ ...VALID_FIXTURE, tiles: [] }).available, false);
  assert.equal(backgroundAvailability({
    ...VALID_FIXTURE,
    tiles: ["https://imagery.invalid/{z}/{x}.png"],
  }).available, false);
  assert.equal(backgroundAvailability({
    ...VALID_FIXTURE,
    tiles: ["http://imagery.invalid/{z}/{x}/{y}.png"],
  }).available, false);
  assert.equal(backgroundAvailability({
    ...VALID_FIXTURE,
    tiles: ["https://user:secret@imagery.invalid/{z}/{x}/{y}.png"],
  }).available, false);
  assert.equal(backgroundAvailability({ ...VALID_FIXTURE, tileSize: 0 }).available, false);
  assert.equal(backgroundAvailability({ ...VALID_FIXTURE, minZoom: 12, maxZoom: 4 }).available, false);
  assert.equal(backgroundAvailability({ ...VALID_FIXTURE, attribution: "  " }).available, false);
});

test("blank environment is not configured; complete env parses a config object", () => {
  assert.equal(readSatelliteConfigFromEnv({}), null);
  assert.equal(readSatelliteConfigFromEnv({
    NEXT_PUBLIC_SATELLITE_TILES: "",
    NEXT_PUBLIC_SATELLITE_TILE_SIZE: "",
    NEXT_PUBLIC_SATELLITE_MIN_ZOOM: "",
    NEXT_PUBLIC_SATELLITE_MAX_ZOOM: "",
    NEXT_PUBLIC_SATELLITE_ATTRIBUTION: "",
  }), null);
  assert.deepEqual(readSatelliteConfigFromEnv({
    NEXT_PUBLIC_SATELLITE_TILES: "https://imagery.invalid/{z}/{x}/{y}.png",
    NEXT_PUBLIC_SATELLITE_TILE_SIZE: "256",
    NEXT_PUBLIC_SATELLITE_MIN_ZOOM: "0",
    NEXT_PUBLIC_SATELLITE_MAX_ZOOM: "18",
    NEXT_PUBLIC_SATELLITE_ATTRIBUTION: "Test attribution",
  }), VALID_FIXTURE);
});

test("satellite request with missing config resets to standard", () => {
  const availability = backgroundAvailability(null);
  assert.deepEqual(requestBackground("satellite", availability), {
    choice: "standard",
    error: "Satellite imagery is not configured",
  });
  assert.deepEqual(requestBackground("standard", availability), {
    choice: "standard",
    error: null,
  });
});

test("tile failure keeps OSM visible and offers Use standard map", () => {
  const availability = backgroundAvailability(VALID_FIXTURE);
  const failed = sessionBackground({
    choice: "satellite",
    availability,
    tileFailed: true,
  });
  assert.equal(failed.visible, "standard");
  assert.equal(failed.choice, "satellite");
  assert.equal(failed.attribution, OSM_ATTRIBUTION);
  assert.equal(failed.error, SATELLITE_LOAD_FAILED);
  assert.equal(failed.offerUseStandard, true);
  assert.equal(USE_STANDARD_MAP_LABEL, "Use standard map");
  assert.deepEqual(backgroundLayerVisibility(failed.visible), {
    osm: "visible",
    satellite: "none",
  });
});

test("successful satellite session uses provider attribution and hides OSM", () => {
  const availability = backgroundAvailability(VALID_FIXTURE);
  const live = sessionBackground({
    choice: "satellite",
    availability,
    tileFailed: false,
  });
  assert.equal(live.visible, "satellite");
  assert.equal(live.attribution, "Test attribution");
  assert.equal(live.error, null);
  assert.equal(live.offerUseStandard, false);
  assert.deepEqual(backgroundLayerVisibility(live.visible), {
    osm: "none",
    satellite: "visible",
  });
  assert.deepEqual(rasterSourceSpec(VALID_FIXTURE), {
    type: "raster",
    tiles: VALID_FIXTURE.tiles,
    tileSize: 256,
    minzoom: 0,
    maxzoom: 18,
    attribution: "Test attribution",
  });
});

test("isSatelliteTileError ignores other map errors", () => {
  assert.equal(isSatelliteTileError({ sourceId: "satellite" }), true);
  assert.equal(isSatelliteTileError({ source: { id: "satellite" } }), true);
  assert.equal(isSatelliteTileError({ sourceId: "osm" }), false);
  assert.equal(isSatelliteTileError({}), false);
  assert.equal(isSatelliteTileError(null), false);
});

test("workspace keeps Standard/Satellite session-only and does not persist a provider", async () => {
  const workspace = await readFile(new URL("../app/components/EngineeringWorkspace.tsx", import.meta.url), "utf8");
  const map = await readFile(new URL("../app/components/EngineeringMap.tsx", import.meta.url), "utf8");
  const helper = await readFile(new URL("../app/lib/map-background.mjs", import.meta.url), "utf8");
  assert.match(workspace, /Standard/);
  assert.match(workspace, /Satellite/);
  assert.match(workspace, /USE_STANDARD_MAP_LABEL/);
  assert.doesNotMatch(workspace, /setProject\([^)]*background/);
  assert.doesNotMatch(workspace, /map_background|satellite_provider|eox/i);
  assert.doesNotMatch(map, /\.setStyle\(/);
  assert.match(map, /addSource\("satellite"/);
  assert.match(map, /addLayer\(\{ id: "satellite"/);
  assert.doesNotMatch(helper, /eox/i);
  assert.doesNotMatch(helper, /s2cloudless/i);
});
