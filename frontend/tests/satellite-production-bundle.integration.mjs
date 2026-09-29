import test from "node:test";
import assert from "node:assert/strict";
import { readdir, readFile } from "node:fs/promises";

const PUBLIC_KEYS = [
  "NEXT_PUBLIC_SATELLITE_TILES",
  "NEXT_PUBLIC_SATELLITE_TILE_SIZE",
  "NEXT_PUBLIC_SATELLITE_MIN_ZOOM",
  "NEXT_PUBLIC_SATELLITE_MAX_ZOOM",
  "NEXT_PUBLIC_SATELLITE_ATTRIBUTION",
];

test("configured Satellite URL and attribution reach the production client bundle", async (context) => {
  const supplied = PUBLIC_KEYS.filter((key) => process.env[key] !== undefined);
  if (supplied.length === 0) {
    context.skip("Satellite is intentionally unconfigured for this build");
    return;
  }
  assert.deepEqual(supplied, PUBLIC_KEYS, "a configured Satellite build needs all five public values");

  const chunkDirectory = new URL("../dist/client/_next/static/chunks/", import.meta.url);
  const chunkNames = (await readdir(chunkDirectory)).filter((name) => name.endsWith(".js"));
  assert.ok(chunkNames.length > 0, "production client chunks must exist");
  const clientBundle = (await Promise.all(chunkNames.map((name) => readFile(new URL(name, chunkDirectory), "utf8")))).join("\n");

  for (const key of PUBLIC_KEYS) {
    const value = process.env[key];
    assert.ok(value, `${key} must be nonempty`);
    const compiledEntries = [
      `${key}:\`${value}\``,
      `${key}:"${value}"`,
      `${key}:'${value}'`,
    ];
    assert.ok(
      compiledEntries.some((entry) => clientBundle.includes(entry)),
      `${key} must be compiled with its configured value into the browser client`,
    );
  }
});
