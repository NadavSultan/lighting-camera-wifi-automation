# Camera range/lens/distance UX — implementation verification
Date: 2026-10-04. Implementation: `fb1c522f2f14e2eebfa638f74af3cbde74920b1e`.
Worktree: `.worktrees/bl016-heatmap-correction`; base `98ac861e5eb9bc1587604f3f43be61908baabfb2`.
Status: implementation verified, awaiting clean readiness check and independent QA. This report is implementation evidence, not independent QA or acceptance.

## Authority and scope
The separately approved design and plan are `docs/superpowers/specs/2026-10-04-camera-range-lens-distance-design.md` and `docs/superpowers/plans/2026-10-04-camera-range-lens-distance.md`. Native sequential execution only. No merge, push, seal, Phase 8, source-pole movement, dependency change or calculation-engine change.

## Current deterministic evidence
Every `final4-*.txt` below records exact command, implementation HEAD, output and exit 0 under `harness/logs/2026-10-04-camera-ux/`.
- `final4-backend-before.txt` and `final4-backend-after.txt`: 387 tests each, unique short basetemp f4b/f4a.
- `final4-validator.txt`, `final4-schema.txt`, `final4-typecheck.txt`, `final4-lint.txt`: PASS.
- `final4-build.txt`: production build PASS with configured EOX 2025 Satellite assertion run and passed.
- `final4-frontend.txt`: 126 tests PASS, including rendered production HTML.
- `final4-generated-freshness.txt`: generated artifacts match implementation HEAD.
Non-failing Starlette/httpx and anyio deprecations and Vite chunk/plugin/route advisories are retained. Earlier test/build passes are historical after product changes and do not substitute for these.

## Production browser and independent measurements
Current browser evidence is `harness/verify/2026-10-04-camera-ux-browser/fb1c522f/browser-evidence.json` and adjacent PNGs. Fresh Chrome production app against owned isolated runtime-03; original 74-pole KML in five folders; explicit SMART, 10 m height and pinned 6 mm lens assignments.
- Default 50 m and recalculated 25/75 m previews/raster verified. Phase 3 geometry/metrics hash stayed `0893557a2fb6a098b2139e39a27a3c4f1fb06af869292ac405792828cd4e59a5`. Restoring final 50 m reproduces it.
- No raw FOV/overlap control or fill. Hide/show governs all camera visual layers. Stored two-contributor overlap popup retains winner/contributors.
- Both pinned r1 cards show 6 mm, 52°/40°, 4056×3040; historical/missing/incompatible resolution has unit coverage.
- A separate UI fixture edit on Cobra Head 7 (20 m, both 3.56 mm lenses, 300 m) yields a point at 280 m with independently computed 1.424015746905178 px/face. It lies in accepted preview but in no density band; subdued gray and no density popup observed. Sources remained unchanged. Test edits were then restored to 10 m/6 mm/50 m. The initial 10 m fixture did not cover the proposed 280 m sample, so its failed analytic-placement assertions are retained, not counted as product failures or evidence of coverage.
- Actual browser clicks produced 49.99288958546626 m, displayed 49.99 m, within 0.1 m of 50. Every successful response independently agrees with PyProj/hypot within 1e-6 m.
- Two clicks/ignored third click, Clear, unfinished/pending Esc, project reopen reset, controlled 422 with no fabricated value, delayed completion after Clear, all three drawing modes, pole/density click exclusion and azimuth-marker removal verified. Deferred unit tests additionally prove project/CRS late-response safety.
- Actual exported project JSON validated and reopened; its fields exactly match Project and exclude measurement state. Export performed while measurement complete. Download observer timeout is retained; actual file existence/validation/reopen, not that observer, proves success.
- Desktop, 600 px and 390 px layouts inspected; lower-left control fits and Cancel works. Standard/Satellite preserved. Final fresh tab error/warning log empty, including resize/recalculation.
Safe API assertions (20) are in `api-evidence.json`. Measurement request/response and read-only evidence are in `measurement-evidence.json`, with raw network observations retained.
Observer limitation: request-window file hashes include concurrent writes. Event index 5 overlapped the deliberate Open Project action and therefore changed project bytes; it cannot prove non-persistence. It is explicitly retained and excluded only from uncontended hash comparison. Seven uncontended requests are byte-identical, and 17 endpoint tests independently prove successful/error API read-only behavior. All eight network events remain visible.

## Acceptance evidence
- UX-01: range/default/calculate browser evidence; bounded vertex and metric regression tests.
- UX-02: preview gating/holes/no-band helper tests; live below-2 sample.
- UX-03: removed raw fills; unchanged engine/base paths and Phase 3 hashes.
- UX-04: exact-pin historical/missing/compatibility tests; both browser cards.
- UX-05: analytic 50 m, zero, invalid CRS/coordinate/transform tests; independent real-click reference.
- UX-06: eight workflow tests and actual Clear/Esc/error/delay/reopen.
- UX-07: shared dispatcher tests, three area modes and responsive browser.
- UX-08: source KML exact SHA, pole/source equivalence, read-only endpoint tests, export schema, preserved overlap and protected base comparison.
- UX-09: final deterministic/build/browser evidence, clean readiness manifest and QA handoff.
All implementation acceptance checks PASS; independent disposition remains NOT REVIEWED.

## Preservation and recovery
Boundary JSON compares all 384 non-boundary tracked paths to base: catalogs, inputs, engines, four non-OpenAPI schemas, locks/configuration and seals unchanged. Original KML SHA-256: `2f89f9f2be306c18221c643c98d5c1a9abdb6449aab8a77ea4b76b3694e8e328`.
Historical eight raster texture errors are retained in `resize-console-failure.json`; corrected raster source/cache lifecycle, full final suite rerun, fresh browser has zero errors.
The legacy live runner failed occupied port 3070 and incorrectly stopped an unknown pre-existing listener in unconditional cleanup. No guessed restart. Replacement checks both ports before launch and stops only manifest-owned worktree process trees. This execution incident remains disclosed; port 3000 application was preserved.
Initial source comparison included a different import timestamp; fixed to exact source poles and filename/hash/size/content/CRS. Failed observer blanket read-only assertion and sample-placement attempts retained. No deletion, unsafe rollback or engine change.
