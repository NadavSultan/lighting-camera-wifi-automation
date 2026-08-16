# Phase 3 final focused corrective completion report

Date: 2026-08-16

Scope: final, focused correction of P3-IR-05 only. Phase 4 and all later-phase implementation remained excluded.

Implementation commit: `ba7e1b5fd56fa10792e8fbb153de4f8d85abd74c`

Gate statement: this report records implementation and local verification claims. It does **not** declare Phase 3 approved. A further independent focused QA retest is required.

## Root cause

`formatEngineeringAzimuth` normalized the raw double and then formatted it with `toFixed(3)`. A value such as `359.9999` was therefore normalized to a valid value below 360 and only afterward rounded across north to the string `360`. The map-handle callback separately used `Number(azimuth.toFixed(3))`, so its near-north edit path could also stage the invalid contract value 360.

The previous modulo expression `((value % 360) + 360) % 360` also introduced avoidable binary noise for already-positive, in-range values because it added and removed 360.

## Correction

- `normalizeFixtureAzimuth` now preserves a non-negative remainder directly and adds 360 only for a negative remainder. Negative zero becomes zero.
- New shared `roundNormalizedFixtureAzimuth` applies the governing sequence: normalize, round to the requested precision, then normalize again. The second normalization converts a rounded 360 to 0.
- `formatEngineeringAzimuth` uses that shared rule and removes trailing fractional zeroes. It remains presentation-only and never writes the existing backend value.
- `fixtureAzimuthFromHandle` uses the shared rule, and `EngineeringWorkspace` applies the same rule again at the intentional map-handle edit boundary. A map-handle edit can create a new three-decimal value, but never 360.
- No backend geometry precision, persisted project contract, schema, catalog, or coordinate behavior changed.

## Changed files

- `frontend/app/lib/phase3-workflows.mjs`
- `frontend/app/lib/phase3-workflows.d.ts`
- `frontend/app/components/EngineeringWorkspace.tsx`
- `frontend/tests/rendered-html.test.mjs`
- `docs/current-status.md`
- `docs/phase-3-corrective-retest-report.md` — added unchanged as independent QA evidence

This completion report is committed separately after the implementation commit so it can identify that commit exactly.

## Required boundary results

| Input | Display | Rounded normalized number |
|---:|---:|---:|
| `359.9999` | `0` | `0` |
| `-0.0001` | `0` | `0` |
| `360` | `0` | `0` |
| `720` | `0` | `0` |
| `721.23456` | `1.235` | `1.235` |
| `-1` | `359` | `359` |
| `51.888999999999996` | `51.889` | `51.889` |

Every numeric result above is asserted to satisfy `value >= 0 && value < 360`. Display strings contain at most three fractional digits and no unnecessary trailing zeroes.

Automated north-boundary map-handle cases use points infinitesimally east and west of true north. Both produce numeric `0`, never `360`, and satisfy the normalized-range invariant. The test also verifies that the workspace no longer uses the former unnormalized `Number(azimuth.toFixed(3))` write path.

## Automated verification

- Frontend rendered/workflow tests: `6 passed`, `0 failed`.
- Strict TypeScript: PASS with zero errors.
- ESLint: PASS with zero errors or warnings.
- Production Vinext build: PASS for client references, server references, RSC, client, and SSR.
- Full backend suite: `85 passed`; the pre-existing non-failing Starlette/httpx deprecation warning remains.
- Existing build advisories remain non-failing: MapLibre chunk size and Vinext route classification.

## Rendered production smoke test

The corrected production build ran at `http://127.0.0.1:3000/` against the Phase 3 API at port 8000.

1. Opened the saved 74-pole Miracle Mile project with a Phoenix 1 SMART fixture and explicit lenses.
2. Set fixture azimuth to `69.9999`, producing authoritative camera-1 absolute azimuth `359.9999`.
3. The inspector displayed camera 1 as `Absolute azimuth 0°`, camera 2 as `140°`, and contained no `Absolute azimuth 360°`.
4. Saved and inspected persisted JSON: fixture azimuth remained exactly `69.9999`; camera-1 absolute azimuth remained exactly `359.9999`. This proves display formatting did not rewrite backend precision.
5. Reopened through the rendered control. The fixture input remained `69.9999` and the camera display remained `0°`.
6. Dragged the fixture map handle near north from the west side and obtained `340.223`; crossed north to the east side and obtained `29.742`. Both values were non-negative, below 360, and exactly three-decimal intentional edits.
7. Saved and reopened the east-side handle result. Persisted and reopened fixture azimuth was exactly `29.742`, within `[0, 360)`. The project still contained 74 source poles.
8. Browser console errors: none.

The smoke test exercises both inspector presentation and the real map-handle update path. The automated infinitesimal cases provide the exact rounding-boundary proof that is impractical to target by physical pixel dragging.

## QA evidence integrity

`docs/phase-3-corrective-retest-report.md` was added without modification.

Required and verified SHA-256:

`072BE55FACE17627A6CD1E03D1864147A47ACC09D875144BE9DDEE8EA5DE0115`

The same SHA-256 was verified for both the working file and the staged Git blob before the implementation commit.

## Phase boundary

No Phase 4 Wi-Fi coverage, Phase 5 photometry, Phase 6 CAP, reporting, automatic pole placement, proposed pole, or coordinate-optimization work was performed. Later-phase controls remain gated. Phase 3 remains pending independent focused QA and is not declared approved by this implementation session.

## Recommended handoff

Run an independent focused P3-IR-05 QA retest against implementation commit `ba7e1b5fd56fa10792e8fbb153de4f8d85abd74c` and this report. Confirm the exact boundary table, both sides of north in the map-handle helper and rendered interaction, presentation-only behavior, legal save/reopen values, preserved QA hash, and continued Phase 4 gating.
