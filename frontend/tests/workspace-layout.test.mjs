import test from "node:test";
import assert from "node:assert/strict";
import { readFile } from "node:fs/promises";

test("workspace and app shell stay inside the viewport", async () => {
  const css = await readFile(new URL("../app/globals.css", import.meta.url), "utf8");
  assert.match(css, /\.app-shell\s*\{[^}]*width:\s*100%/);
  assert.match(css, /\.app-shell\s*\{[^}]*max-width:\s*100%/);
  assert.match(css, /\.app-shell\s*\{[^}]*min-width:\s*0/);
  assert.match(css, /\.app-shell\s*\{[^}]*overflow:\s*hidden/);
  assert.match(css, /\.workspace\s*\{[^}]*width:\s*100%/);
  assert.match(css, /\.workspace\s*\{[^}]*max-width:\s*100%/);
  assert.match(css, /\.workspace\s*\{[^}]*grid-template-columns:\s*minmax\(0,\s*278px\)\s*minmax\(0,\s*1fr\)\s*minmax\(0,\s*318px\)/);
  assert.match(css, /\.topbar\s*\{[^}]*min-width:\s*0/);
  assert.match(css, /\.toolbar-scroll\s*\{[^}]*flex:\s*1\s+1\s+auto/);
  assert.match(css, /\.brand\s*\{[^}]*flex:\s*0\s+1/);
});

test("lighting result card keeps core statistics out of a 220px clip", async () => {
  const css = await readFile(new URL("../app/globals.css", import.meta.url), "utf8");
  const card = await readFile(new URL("../app/components/LightingResultCard.tsx", import.meta.url), "utf8");
  assert.doesNotMatch(css, /\.lighting-result-card\s*\{[^}]*max-height:\s*min\(220px/);
  assert.match(css, /\.lighting-result-stats\s*\{/);
  assert.match(card, /lighting-result-card-body/);
  assert.match(card, /<details/);
  assert.match(card, /Assumptions and limitations/);
  assert.match(card, /Emin\/Eavg/);
  assert.match(card, /Emin\/Emax/);
});

test("direction and lux canvases cancel frames through the shared scheduler", async () => {
  const mapSource = await readFile(new URL("../app/components/EngineeringMap.tsx", import.meta.url), "utf8");
  const labels = await readFile(new URL("../app/components/LightingPointLabels.tsx", import.meta.url), "utf8");
  assert.match(mapSource, /createMapFrameScheduler/);
  assert.match(mapSource, /cancelMapFrame/);
  assert.match(mapSource, /map\.on\("idle", schedule\)/);
  assert.match(labels, /createMapFrameScheduler/);
  assert.match(labels, /cancelMapFrame/);
});
