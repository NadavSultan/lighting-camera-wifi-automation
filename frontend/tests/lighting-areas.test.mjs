import test from "node:test";
import assert from "node:assert/strict";
import { readFile } from "node:fs/promises";
import { calculateAllLightingAreas } from "../app/lib/phase4-workflows.mjs";

test("Draw Calculation Area clears the selected area so a second polygon is created", async () => {
  const workspace = await readFile(new URL("../app/components/EngineeringWorkspace.tsx", import.meta.url), "utf8");
  const start = workspace.match(/function startCalculationArea\(\) \{[\s\S]*?\n {2}\}/)?.[0] ?? "";
  assert.match(start, /setSelectedCalculationAreaId\(null\)/);
  assert.doesNotMatch(start, /loadCalculationForm\(selectedCalculationAreaId\)/);
});

test("Calculate Lighting chains every calculation area onto the previous project", async () => {
  const calls = [];
  const result = await calculateAllLightingAreas(
    {
      calculation_areas: [{ id: "area-a" }, { id: "area-b" }],
      lighting_calculations: { results: {} },
    },
    async (project, areaId) => {
      calls.push({ from: Object.keys(project.lighting_calculations.results), areaId });
      return {
        ...project,
        lighting_calculations: {
          results: { ...project.lighting_calculations.results, [areaId]: { calculation_area_id: areaId } },
        },
      };
    },
  );
  assert.deepEqual(calls.map((item) => item.areaId), ["area-a", "area-b"]);
  assert.deepEqual(calls[1].from, ["area-a"]);
  assert.deepEqual(Object.keys(result.lighting_calculations.results), ["area-a", "area-b"]);
});

test("workspace calculates every lighting area from one Calculate Lighting action", async () => {
  const workspace = await readFile(new URL("../app/components/EngineeringWorkspace.tsx", import.meta.url), "utf8");
  assert.match(workspace, /calculateAllLightingAreas\(project, calculateLighting\)/);
  assert.match(workspace, /disabled=\{!project \|\| !project\.calculation_areas\.length \|\| busy\}/);
});

test("Show results opens a stored current result without calculating", async () => {
  const workspace = await readFile(new URL("../app/components/EngineeringWorkspace.tsx", import.meta.url), "utf8");
  const show = workspace.match(/function showLightingResults\([\s\S]*?\n {2}\}/)?.[0] ?? "";
  assert.match(workspace, /Show results/);
  assert.match(show, /lightingAreaResultState\(area, result\) !== "current"/);
  assert.match(show, /setSelectedCalculationAreaId\(areaId\)/);
  assert.match(show, /resolveLightingCardSession/);
  assert.match(show, /setLightingCardAreaId\(areaId\)/);
  assert.doesNotMatch(show, /calculateLighting/);
  assert.doesNotMatch(show, /calculateAllLightingAreas/);
  assert.doesNotMatch(show, /calculateSelectedArea/);
});

test("only one lighting result card identity exists", async () => {
  const workspace = await readFile(new URL("../app/components/EngineeringWorkspace.tsx", import.meta.url), "utf8");
  assert.match(workspace, /const \[lightingCardAreaId, setLightingCardAreaId\] = useState<string \| null>\(null\)/);
  assert.doesNotMatch(workspace, /lightingCardAreaIds/);
});

test("creating or cancelling a lighting draft does not discard stored results or sessions", async () => {
  const workspace = await readFile(new URL("../app/components/EngineeringWorkspace.tsx", import.meta.url), "utf8");
  const start = workspace.match(/function startCalculationArea\(\) \{[\s\S]*?\n {2}\}/)?.[0] ?? "";
  const cancel = workspace.match(/function cancelCalculationArea\(\) \{[\s\S]*?\n {2}\}/)?.[0] ?? "";
  assert.doesNotMatch(start, /lighting_calculations\.results/);
  assert.doesNotMatch(start, /setLightingCardSessions/);
  assert.doesNotMatch(cancel, /lighting_calculations\.results/);
  assert.doesNotMatch(cancel, /setLightingCardSessions/);
  assert.doesNotMatch(cancel, /setLightingCardAreaId/);
});

test("deleting a lighting area removes its session and closes its card", async () => {
  const workspace = await readFile(new URL("../app/components/EngineeringWorkspace.tsx", import.meta.url), "utf8");
  const remove = workspace.match(/function deleteCalculationArea\([\s\S]*?\n {2}\}/)?.[0] ?? "";
  assert.match(remove, /delete draft\.lighting_calculations\.results\[areaId\]/);
  assert.match(remove, /if \(lightingCardAreaId === areaId\) setLightingCardAreaId\(null\)/);
  assert.match(remove, /delete next\[areaId\]/);
});

test("discipline switching does not clear an active lighting polygon draft", async () => {
  const workspace = await readFile(new URL("../app/components/EngineeringWorkspace.tsx", import.meta.url), "utf8");
  assert.match(workspace, /onClick=\{\(\) => setLeftDiscipline\(item.id\)\}/);
  assert.doesNotMatch(workspace, /setLeftDiscipline\(item.id\); setCalculationDraft/);
  assert.doesNotMatch(workspace, /setLeftDiscipline\(item.id\); setDrawingCalculationArea\(false\)/);
});
