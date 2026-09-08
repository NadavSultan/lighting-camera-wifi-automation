import test from "node:test";
import assert from "node:assert/strict";
import { readFile } from "node:fs/promises";
import { clampCard, ringAnchorLngLat, cardOffsetFromProjected } from "../app/lib/lighting-card-position.mjs";

test("clampCard keeps a 280x180 card inside an 800x600 viewport with 8px margin", () => {
  assert.deepEqual(
    clampCard({ x: 900, y: 700, width: 280, height: 180 }, { width: 800, height: 600 }),
    { x: 512, y: 412 },
  );
});

test("clampCard lifts negative coordinates to the margin", () => {
  assert.deepEqual(
    clampCard({ x: -20, y: -30, width: 280, height: 180 }, { width: 800, height: 600 }),
    { x: 8, y: 8 },
  );
});

test("ringAnchorLngLat uses the final non-closing vertex", () => {
  assert.deepEqual(
    ringAnchorLngLat([[0, 0], [1, 0], [1, 1], [0, 0]]),
    [1, 1],
  );
});

test("lighting result card stays interactive after map-overlay disables pointer events", async () => {
  const css = await readFile(new URL("../app/globals.css", import.meta.url), "utf8");
  const overlayNone = css.search(/\.map-overlay\s*\{[^}]*pointer-events:\s*none/);
  const cardAuto = css.search(/\.map-overlay\.lighting-result-card\s*\{[^}]*pointer-events:\s*auto/);
  assert.ok(overlayNone >= 0, "map-overlay must disable pointer events by default");
  assert.ok(cardAuto > overlayNone, "card must re-enable pointer events with a more specific rule after map-overlay");
});

test("WA-05 recorded card position matches subtracting the container viewport origin from map.project", () => {
  // Live review 2026-09-08: finish vertex ≈ screen (390, 505); card opened at (286, 459).
  // Map stage origin is not page (0,0): ~278px left panel + ~58px topbar.
  const container = { left: 278, top: 58, width: 1324, height: 739 };
  const vertexScreen = { x: 390, y: 505 };
  const projected = { x: vertexScreen.x - container.left, y: vertexScreen.y - container.top };
  assert.deepEqual(projected, { x: 112, y: 447 });

  const incorrect = {
    x: projected.x - container.left + 12,
    y: projected.y - container.top + 12,
  };
  const clampedIncorrect = clampCard(
    { ...incorrect, width: 280, height: 220 },
    { width: container.width, height: container.height },
  );
  assert.deepEqual(clampedIncorrect, { x: 8, y: 401 });
  assert.deepEqual(
    { left: container.left + clampedIncorrect.x, top: container.top + clampedIncorrect.y },
    { left: 286, top: 459 },
  );
});

test("cardOffsetFromProjected keeps a 12px offset in map-container coordinates", () => {
  const container = { left: 278, top: 58 };
  const projected = { x: 112, y: 447 };
  const next = cardOffsetFromProjected(projected, 12);
  assert.deepEqual(next, { x: 124, y: 459 });
  assert.deepEqual(
    { left: container.left + next.x, top: container.top + next.y },
    { left: 402, top: 517 },
  );
});

test("LightingResultCard does not subtract container viewport origin from map.project", async () => {
  const source = await readFile(new URL("../app/components/LightingResultCard.tsx", import.meta.url), "utf8");
  assert.match(source, /cardOffsetFromProjected/);
  assert.doesNotMatch(source, /projected\.x\s*-\s*container\.left/);
  assert.doesNotMatch(source, /projected\.y\s*-\s*container\.top/);
});
