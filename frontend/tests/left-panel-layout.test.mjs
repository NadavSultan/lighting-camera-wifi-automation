import test from "node:test";
import assert from "node:assert/strict";
import { readFile } from "node:fs/promises";

test("left panel uses a four-discipline switcher defaulting to Lighting", async () => {
  const workspace = await readFile(new URL("../app/components/EngineeringWorkspace.tsx", import.meta.url), "utf8");
  const css = await readFile(new URL("../app/globals.css", import.meta.url), "utf8");
  assert.match(workspace, /discipline-switcher/);
  assert.match(workspace, /\{ id: "lighting", label: "Lighting" \}/);
  assert.match(workspace, /\{ id: "camera", label: "Camera" \}/);
  assert.match(workspace, /\{ id: "wifi", label: "Wi-Fi" \}/);
  assert.match(workspace, /\{ id: "cap", label: "CAP" \}/);
  assert.match(workspace, /useState<LeftDiscipline>\("lighting"\)/);
  assert.match(workspace, /setLeftDiscipline\("lighting"\)/);
  assert.match(workspace, /hidden=\{leftDiscipline !== "cap"\}/);
  assert.match(workspace, /hidden=\{leftDiscipline !== "lighting"\}/);
  assert.match(workspace, /hidden=\{leftDiscipline !== "camera"\}/);
  assert.match(workspace, /hidden=\{leftDiscipline !== "wifi"\}/);
  assert.match(workspace, /setLeftDiscipline\("cap"\)/);
  assert.match(workspace, /openReportPackagePanel/);
  assert.match(workspace, /ReportPanel/);
  assert.match(css, /\.panel-scroll\s*\{[^}]*overflow-x:\s*hidden/);
  assert.match(css, /\.discipline-switcher\s*\{[^}]*minmax\(0,\s*1fr\)/);
  assert.match(css, /\.discipline-pane\[hidden\]/);
  assert.match(css, /\.section\s*\{[^}]*min-width:\s*0/);
  assert.match(css, /\.button-row\s*\{[^}]*flex-wrap:\s*wrap/);
});

test("CAP required inputs stay available and expandable rather than deleted", async () => {
  const capPanel = await readFile(new URL("../app/components/CapPlanningPanel.tsx", import.meta.url), "utf8");
  assert.match(capPanel, /CAP preflight blockers/);
  assert.match(capPanel, /<details className="cap-required-inputs">/);
  assert.doesNotMatch(capPanel, /<details className="cap-required-inputs" open>/);
  assert.match(capPanel, /Required CAP inputs/);
  assert.match(capPanel, /cap-field-operation_mode/);
  assert.match(capPanel, /id="cap-section-candidates"/);
  assert.match(capPanel, /Calculate \/ rank/);
  assert.match(capPanel, /Validate/);
});

test("CAP pane is result-first with one recommend primary action", async () => {
  const capPanel = await readFile(new URL("../app/components/CapPlanningPanel.tsx", import.meta.url), "utf8");
  const resultIdx = capPanel.indexOf("cap-result-summary");
  const primaryIdx = capPanel.indexOf("button-row cap-primary-action");
  const blockerIdx = capPanel.indexOf("CAP preflight blockers");
  const inputsIdx = capPanel.indexOf("Required CAP inputs");
  const candidatesIdx = capPanel.indexOf("id=\"cap-section-candidates\"");
  const secondaryIdx = capPanel.indexOf("Advanced operations");
  assert.ok(resultIdx >= 0 && primaryIdx > resultIdx);
  assert.ok(blockerIdx > primaryIdx);
  assert.ok(inputsIdx > blockerIdx);
  assert.ok(candidatesIdx > inputsIdx);
  assert.ok(secondaryIdx > candidatesIdx);
  assert.match(capPanel, /runCap\(primary.operation\)/);
  assert.match(capPanel, /Calculate CAP recommendation/);
  assert.doesNotMatch(capPanel, /onClick=\{\(\) => runCap\("recommend"\)\}/);
  assert.match(capPanel, /runCap\("calculate"\)/);
  assert.match(capPanel, /runCap\("validate"\)/);
  assert.match(capPanel, /Current result has zero selected CAP sites/);
  assert.match(capPanel, /unresolved node/);
});
