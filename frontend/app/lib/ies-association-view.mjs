/**
 * Presentation rows for IES ↔ fixture-model associations.
 * Does not infer compatibility; only reflects explicit association records.
 */

/**
 * @param {string} fileId
 * @param {Array<{id: string, fixture_family?: string, capability_variant?: string, display_name?: string}>} fixtureModels
 * @param {Array<{ies_file_id: string, fixture_model_id: string, active?: boolean}>} associations
 */
export function associationRows(fileId, fixtureModels, associations) {
  const models = Array.isArray(fixtureModels) ? fixtureModels : [];
  const pairs = Array.isArray(associations) ? associations : [];
  const seen = new Set();
  const rows = [];
  for (const model of models) {
    if (!model || typeof model.id !== "string" || seen.has(model.id)) continue;
    seen.add(model.id);
    const associated = pairs.some(
      (pair) => pair
        && pair.ies_file_id === fileId
        && pair.fixture_model_id === model.id
        && pair.active !== false,
    );
    rows.push({
      id: model.id,
      fixture_family: model.fixture_family ?? "",
      capability_variant: model.capability_variant ?? "",
      display_name: model.display_name ?? model.id,
      associated,
    });
  }
  return rows;
}

/**
 * Group association rows by fixture family for display.
 * @param {ReturnType<typeof associationRows>} rows
 */
export function groupAssociationRowsByFamily(rows) {
  const groups = new Map();
  for (const row of rows) {
    const key = row.fixture_family || "Ungrouped";
    if (!groups.has(key)) groups.set(key, []);
    groups.get(key).push(row);
  }
  return [...groups.entries()].map(([family, items]) => ({ family, items }));
}
