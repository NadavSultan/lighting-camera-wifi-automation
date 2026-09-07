import test from "node:test";
import assert from "node:assert/strict";
import { associationRows } from "../app/lib/ies-association-view.mjs";

test("one file shows three simultaneously associated Phoenix models", () => {
  const models = ["lite", "wifi", "smart"].map((variant) => ({
    id: `phoenix-1-${variant}`,
    fixture_family: "Phoenix 1",
    capability_variant: variant.toUpperCase(),
    display_name: `Phoenix 1 ${variant.toUpperCase()}`,
  }));
  const pairs = models.map((model) => ({
    ies_file_id: "ies-a",
    fixture_model_id: model.id,
    active: true,
  }));
  assert.deepEqual(
    associationRows("ies-a", models, pairs).filter((row) => row.associated).map((row) => row.id).sort(),
    ["phoenix-1-lite", "phoenix-1-smart", "phoenix-1-wifi"],
  );
});

test("associations for a different file do not mark this file associated", () => {
  const models = [{ id: "phoenix-1-lite", fixture_family: "Phoenix 1", capability_variant: "LITE", display_name: "Phoenix 1 LITE" }];
  const pairs = [{ ies_file_id: "ies-b", fixture_model_id: "phoenix-1-lite", active: true }];
  assert.equal(associationRows("ies-a", models, pairs)[0].associated, false);
});

test("inactive pairs and duplicate model ids are handled safely", () => {
  const models = [
    { id: "m1", fixture_family: "A", capability_variant: "LITE", display_name: "A LITE" },
    { id: "m1", fixture_family: "A", capability_variant: "LITE", display_name: "A LITE dup" },
    { id: "m2", fixture_family: "A", capability_variant: "WIFI", display_name: "A WIFI" },
  ];
  const pairs = [
    { ies_file_id: "ies-a", fixture_model_id: "m1", active: false },
    { ies_file_id: "ies-a", fixture_model_id: "m2", active: true },
  ];
  const rows = associationRows("ies-a", models, pairs);
  assert.equal(rows.length, 2);
  assert.equal(rows.find((row) => row.id === "m1")?.associated, false);
  assert.equal(rows.find((row) => row.id === "m2")?.associated, true);
});

test("helper does not invent associations from family labels alone", () => {
  const models = [{ id: "x", fixture_family: "Phoenix 1", capability_variant: "LITE", display_name: "Phoenix 1 LITE" }];
  assert.equal(associationRows("ies-a", models, []).every((row) => !row.associated), true);
});
