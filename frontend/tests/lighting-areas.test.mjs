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
