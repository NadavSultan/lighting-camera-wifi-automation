import test from "node:test";
import assert from "node:assert/strict";
import { readFile } from "node:fs/promises";
import { clampCard, ringAnchorLngLat } from "../app/lib/lighting-card-position.mjs";

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
