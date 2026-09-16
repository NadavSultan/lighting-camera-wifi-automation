import test from "node:test";
import assert from "node:assert/strict";
import { readFile } from "node:fs/promises";
import {
  CAMERA_PROJECTION_BOUNDARY_TITLE,
  CAMERA_PROJECTION_BOUNDARY_EXPLANATION,
} from "../app/lib/camera-projection-legend.mjs";

test("camera explanation uses the approved flat-ground meaning", () => {
  assert.equal(CAMERA_PROJECTION_BOUNDARY_TITLE, "Projection boundary");
  assert.match(CAMERA_PROJECTION_BOUNDARY_EXPLANATION, /intersection of the camera field-of-view corner rays/);
  assert.match(CAMERA_PROJECTION_BOUNDARY_EXPLANATION, /flat local ground plane/);
  assert.match(CAMERA_PROJECTION_BOUNDARY_EXPLANATION, /pinned camera\/lens FOV/);
  assert.match(CAMERA_PROJECTION_BOUNDARY_EXPLANATION, /mounting height/);
  assert.match(CAMERA_PROJECTION_BOUNDARY_EXPLANATION, /fixture azimuth/);
  assert.match(CAMERA_PROJECTION_BOUNDARY_EXPLANATION, /fixed relative camera azimuth/);
  assert.match(CAMERA_PROJECTION_BOUNDARY_EXPLANATION, /fixed downward tilt/);
  assert.match(CAMERA_PROJECTION_BOUNDARY_EXPLANATION, /Footprint area and overlap are geometric results only/);
  assert.match(CAMERA_PROJECTION_BOUNDARY_EXPLANATION, /not detection range, recognition performance, pixel density, terrain\/occlusion analysis, or proof of unobstructed visibility/);
});

test("camera explanation does not claim detection capability or calculated pixel density", () => {
  assert.doesNotMatch(CAMERA_PROJECTION_BOUNDARY_EXPLANATION, /detection range is/);
  assert.doesNotMatch(CAMERA_PROJECTION_BOUNDARY_EXPLANATION, /pixel density is calculated/);
  assert.doesNotMatch(CAMERA_PROJECTION_BOUNDARY_EXPLANATION, /recognition threshold/);
});

test("Camera pane renders the legend beside existing footprint metrics", async () => {
  const workspace = await readFile(new URL("../app/components/EngineeringWorkspace.tsx", import.meta.url), "utf8");
  const map = await readFile(new URL("../app/components/EngineeringMap.tsx", import.meta.url), "utf8");
  assert.match(workspace, /CAMERA_PROJECTION_BOUNDARY_EXPLANATION/);
  assert.match(workspace, /geometry-metrics/);
  assert.match(workspace, /valid footprints/);
  assert.doesNotMatch(map, /pixel-density-layer/);
  assert.doesNotMatch(map, /projection-boundary-layer/);
});
