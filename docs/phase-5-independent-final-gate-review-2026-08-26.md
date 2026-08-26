# Phase 5 independent final gate review

Date: 2026-08-26

Role: independent final QA and gate reviewer

Final verdict: **FAIL**

## 1. Gate decision

Phase 5 does not pass its binding acceptance contract at the reviewed state. Two independently reproduced defects remain:

1. **Major — R-02:** after a successful calculation with zero Wi-Fi analysis areas, the rendered UI shows the 74-circle global metrics but removes the mandatory message that boundary/gap statistics are unavailable.
2. **Moderate — G-03/revision semantics:** the backend bulk API increments `configuration_revision` for an unchanged Wi-Fi patch, including an identical note and explicit false clear flags.

All other mandatory matrix items passed the evidence described below. A PASS requires every mandatory item, so neither the green automated suites nor the otherwise successful 74-pole workflow can soften these failures into acceptance. This report does not close Phase 5, authorize Phase 6, or modify implementation.

## 2. Reviewed repository state

- Worktree: `C:\Users\NadavSultan\.codex\worktrees\e0cc\lighting-camera-wifi-automation`.
- Branch state at review start: detached HEAD (`HEAD (no branch)`), clean.
- Expected and actual HEAD: `3fec841461b1c6d8a128a8089afac2b0aa082a5e` (`docs: clean Phase 5 QA evidence`).
- Approved planning baseline: `893f10ff990d2ce82fc6a8054bb1ce09bbf9a814` (`docs: approve Phase 5 planning decisions`).
- Independently reviewed diff: `893f10ff990d2ce82fc6a8054bb1ce09bbf9a814..3fec841461b1c6d8a128a8089afac2b0aa082a5e`, 26 files, 2,554 insertions and 90 deletions.
- Reviewed commits after the baseline, in repository order:
  - `e3bd388cc1eef9a6ca08c67336d69ad49d7219d3` — `feat: implement Phase 5 conceptual Wi-Fi geometry`
  - `932554c78bc962c68aaf6b6fb12f0611c9bdc062` — `docs: finalize Phase 5 handoff report`
  - `a4e8d0ca807032f0085491315914de62e6e6f4a5` — `fix: close Phase 5 Wi-Fi review findings`
  - `34ee95017a7d6a73329eeb8922a70fd8b150175c` — `docs: record Phase 5 corrective handoff`
  - `54d5e3704ac08444e8b2f9fafd7ced2431eb5d2f` — `docs: add supplied Wi-Fi acceptance evidence`
  - `773f73cccfcd5f38c632b263e06e5b8501869c0b` — `fix: complete final Phase 5 corrective pass`
  - `7db1a10f348471a4df61af4d52c4666d12042b81` — `docs: record final Phase 5 corrective evidence`
  - `3fec841461b1c6d8a128a8089afac2b0aa082a5e` — `docs: clean Phase 5 QA evidence`

The required startup and Phase 5 contract/evidence documents were read completely in the mandated order. Phase 4 regression boundaries were checked against `docs/phase-4-master-gate-decision-2026-08-26.md`, `docs/phase-4-final-p4-ir-05-independent-retest-2026-08-26.md`, and `docs/phase-4-final-focused-retest-report.md`. Implementation and rendered-evidence reports were treated as claims, not proof.

No file under `Input/` was changed. No implementation defect was fixed, no Phase 6 behavior was begun, and no customer pole was generated, moved, optimized, redistributed, or deleted.

## 3. Environment and verification commands

The review used the bundled Python 3.12.13 and Node 24.19.0 runtimes, pnpm 11.19.0, the lockfile-pinned frontend dependencies, FastAPI `TestClient` with isolated temporary stores for adversarial API probes, and isolated production servers at `127.0.0.1:8015` and `127.0.0.1:3015` for the rendered workflow.

| Verification | Result |
|---|---|
| `python -m pytest -q -p no:cacheprovider backend/tests` | **PASS — 132 tests**; one known non-failing Starlette/httpx deprecation warning |
| Focused supported-version migration set | **PASS — 11 tests**, covering schema `1.0.0`, `2.0.0`, `2.1.0`, `2.2.0`, `2.3.0`, and `2.4.0` through the existing migration suites plus Phase 5 idempotence |
| `python scripts/validate_engineering_data.py` | **PASS** — all seven frozen catalog/schema pairs and all supplied-source hashes |
| `python backend/scripts/export_schema.py` plus before/after SHA-256 | **PASS** — project schema and OpenAPI remained byte-identical; project-schema SHA-256 `3c30c6b2979caf325a8ca89e75c50ba6bdc7744ef323d6c3f630658da74eefc1`, OpenAPI SHA-256 `772f8a2bcf844a5a4804d3f733388d4c57b3ef6439d4fe2c4647696fab09b048` |
| Direct pinned `node --test tests/rendered-html.test.mjs` after production build | **PASS — 12/12** |
| Direct pinned TypeScript `tsc --noEmit` | **PASS** |
| Direct pinned ESLint | **PASS**, zero output/errors |
| Direct pinned Vinext production build | **PASS**; existing non-failing >500 kB chunk advisory only |
| `git diff --check` before report creation | **PASS** |
| `git diff --quiet 893f10f..HEAD -- Input` | **PASS — unchanged** |
| Supplied KML SHA-256 | **PASS — `2f89f9f2be306c18221c643c98d5c1a9abdb6449aab8a77ea4b76b3694e8e328`** |

The ordinary pnpm wrappers attempted a dependency-status refresh in the non-interactive shell and aborted with `ERR_PNPM_ABORTED_REMOVE_MODULES_DIR_NO_TTY`. The same lockfile-pinned tools were then invoked directly and passed. The first frontend test command was intentionally launched concurrently with the production build and saw `dist/server/index.js` before the build had created it; the deterministic post-build rerun passed all 12 tests. Both are environmental/orchestration limitations, not product defects.

Independent Python probes additionally exercised eligibility, exact circle canonicalization, zero-circle behavior, invalid/geographic/non-metre CRS rejection, every approved numeric cap, significant/non-significant fingerprints, analytic two-circle equations, exact three-circle aggregate equations, and API preservation. Salient results included:

- exact 500-circle success with `64,500` persisted circle vertices;
- controlled rejection of 501 circles;
- controlled rejection of 318 coincident circles producing more than 50,000 indexed candidate pairs;
- controlled rejection above 200 areas, 10,000 vertices per area, and 250,000 total persisted vertices;
- API cap failures returned 422 and left the exact prior stored `project.json` bytes unchanged;
- `EPSG:4326` and projected non-metre `EPSG:2263` were rejected;
- two disjoint circles: individual and union `5652.596083 m²`, zero overlap;
- two circles 40 m apart: pairwise/multiply-covered overlap `618.891550 m²`, union `5033.704532 m²`;
- three circles: pairwise sum `6107.568022 m²` versus exact multiply-covered union `2809.260135 m²`.

## 4. Acceptance traceability matrix

| ID | Result | Independent evidence | Limitation |
|---|---|---|---|
| G-01 | **PASS** | One-circle test and independent probe confirmed stable `wifi-circle/<pole-id>`, 129-point closed CCW canonical ring (128 sides plus closure), 9-decimal projected and 10-decimal WGS84 output, `2826.298041 m²` area, deterministic transform, and unchanged source tuple. | Polygon is the approved fixed approximation, not RF coverage. |
| G-02 | **PASS** | Independent five-state matrix: LITE excluded; WIFI and SMART included; inactive and explicitly disabled excluded; assigned LITE model/WIFI classification conflict warned and excluded. Full configuration validation remains atomic. | No RF capability beyond catalog Boolean eligibility is inferred. |
| G-03 | **FAIL** | Visible 74-pole set/clear/inherit/model workflow worked, but an API no-op patch changed revision 7 to 8. See finding QA-02. | Exact backend revision semantics are not satisfied. |
| G-04 | **PASS** | Pydantic/service/API probes rejected non-finite, zero, negative, >1000 m, invalid topology, missing CRS, geographic CRS, and non-metre projected CRS with controlled errors and preservation. | None. |
| S-01 | **PASS** | Independent two-disjoint-circle reference matched exact approved Shapely approximation: sum equals union and all overlap outputs are zero. | None. |
| S-02 | **PASS** | Independent 40 m-separation reference matched individual, union, overlap, pairwise, multiply-covered, count, and percentage within the required persisted tolerances. | Approximation model only. |
| S-03 | **PASS** | Independent three-circle reference matched pairwise sum and unary-unioned multiply-covered region; pairwise intentionally exceeded multiply-covered union. No deferred multiplicity output appeared. | None. |
| S-04 | **PASS** | No area produced no inferred summaries; valid projected area produced covered/uncovered and boundary-line metrics; LITE-only zero-circle project returned 0 covered, 100% uncovered, and 0% boundary coverage. | The rendered post-calculation no-area copy fails separately under R-02. |
| S-05 | **PASS** | Boundary and over-cap probes covered 500, 64,500, 50,000, 200, 10,000, and 250,000 limits. Circle/candidate API failures returned 422 and preserved exact prior bytes; topology/radius/CRS failures also preserved stored state. | Large-cap probes used synthetic geometry and isolated stores. |
| F-01 | **PASS** | Backend probes and full tests covered defaults, coordinates, fixture type/model, active/enabled/radius, CRS, and area inputs; notes, timestamps, general revision, and layer visibility retained results. Browser verified note retention, radius invalidation, and that undo/redo did not resurrect stale results. Save/open/get/bulk paths revalidate fingerprints. | Catalog capability is represented through pinned model identity/revision and lifecycle validation rather than copied Boolean data in the fingerprint payload. |
| M-01 | **PASS** | Focused 11-test migration run plus complete suite covered every supported schema. Exact source bytes/raw coordinates/IDs and earlier camera/lighting collections were preserved by their controlling migration regressions; 2.4.0 Wi-Fi-note/unknown-key migration was additive and idempotent. | Legacy-version coverage is distributed across Phase 2–5 regression files rather than one monolithic test. |
| A-01 | **PASS** | Calculate returned complete typed result with provenance, assumptions, warnings, model/CRS/fingerprint, and exact disclaimer. Independent API checks returned 404/409/422 as required. Source archive hash and source pole tuple remained unchanged. | Browser download events were not exposed by the in-app surface; API/export content was inspected directly after the visible export action. |
| A-02 | **PASS** | Invalid bow-tie area returned 422 and left saved areas/result unchanged; 501-circle and candidate-cap errors preserved exact stored bytes. Successful significant changes cleared results before recalculation. | No-op revision defect is classified under G-03 because stored geometry/result correctly remained current. |
| R-01 | **PASS** | Genuine production-rendered supplied KML showed 74 poles, visible 30 m source/default, editable inherited 40 m effective radius, exact disclaimer, yellow WIFI markers, and distinct translucent cyan conceptual circles. LITE red/SMART blue definitions remained unchanged in the rendered map source. | Workflow configured all 74 as WIFI; red/blue preservation was also verified through source and rendered layer legend. |
| R-02 | **FAIL** | Before calculation, the required unavailable-boundary copy appeared. After calculating 74 circles with zero areas, global metrics appeared and the unavailable-boundary copy disappeared. See finding QA-01. | Mandatory rendered state is absent. |
| R-03 | **PASS** | Genuine UI create/select/rename/redraw-from-empty/cancel/delete/save/reopen workflow passed. Bow-tie replacement showed `Wi-Fi analysis area has a self-touch or self-intersection` while retaining the prior polygon and exact result. | Reopen used the saved portable-equivalent project JSON because the browser provider did not expose a filesystem path for its download. |
| R-04 | **PASS** | Wi-Fi remained a separate map/result/area collection; camera priority and lighting calculation layers remained present and independently gated. `Recommend CAP`, recommended CAP, and CAP connections remained disabled; `recommended_layers` stayed empty. | No new Phase 4 calculation was authored during this Phase 5-only review. Existing full regressions passed. |
| R-05 | **PASS** | Full backend, rendered suite, TypeScript, ESLint, production build, and genuine browser console inspection all passed; console error list was `[]`. | Known deprecation and chunk-size advisories are non-failing. |

## 5. Production-rendered 74-pole workflow

The in-app browser controlled a production Vinext build from the exact reviewed worktree against the exact reviewed FastAPI backend. This was a genuine UI workflow, not SSR/helper-only evidence.

1. Imported `Input/Miracle_Mile_Lighting_Poles.kml` through the visible chooser. The app rendered 74 source poles, zero import warnings, `EPSG:32617`, and the locked first raw coordinate `-80.26234411,25.74920999,0`.
2. Bulk-selected Phoenix 1 WIFI for all 74 poles, 35 m explicit radius, explicit enabled, and a note. Counters changed to WIFI 74, LITE 0, SMART 0.
3. Changed the project default to 40 m, bulk-cleared radius and enabled overrides, and visibly confirmed `Inherit (true)` plus `Effective radius: 40 m · project default inherited`.
4. Calculated with no area. The app rendered 74 circles, individual `371815.208984 m²`, union `91075.840279 m²`, aggregate overlap `280739.368704 m²`, pairwise `783037.421624 m²`, multiply-covered union `80211.336769 m²`, and 467 overlap pairs. This step reproduced finding QA-01.
5. Drew and saved `Independent QA Coverage`, calculated bounded metrics (`26582.000869 m²` covered, `20778.206152 m²` uncovered, boundary `215.440655 m`), rejected a bow-tie redraw without replacing the valid polygon/result, cancelled, renamed it `Independent QA Final`, created/deleted a second temporary area, and recalculated.
6. Enabled the distinct `Conceptual Wi-Fi` map layer. Yellow pole markers remained visible above translucent cyan circle geometry; the separate analysis-area boundary was lime/dashed. Camera, priority, lighting, warnings, and CAP layer controls remained separate.
7. Saved and invoked the visible combined project-JSON/updated-KML export. Reopened the saved project JSON through the visible Open Project chooser; 74 poles, 74 circles, final area name, exact disclaimer, and Phase 5 state remained present.
8. Visible UI mutation checks confirmed notes did not invalidate, radius did invalidate, and undo/redo did not resurrect stale results.
9. Final browser console error inspection returned an empty list.

The visible export action completed with status `Exported project JSON and updated KML`. The browser provider did not expose the download filesystem paths/events, so the exact API endpoint used by that UI action was independently inspected from the saved project:

- updated KML: 74 placemarks, fixture update text present, no `wifi-circle`, conceptual Wi-Fi, analysis-area, or `wifi_coverage` geometry markers;
- source archive: 34,385 bytes and exact SHA-256 `2f89f9f2be306c18221c643c98d5c1a9abdb6449aab8a77ea4b76b3694e8e328`;
- project JSON: schema 2.5.0 with 74 poles, 74 Wi-Fi circles, one final Wi-Fi area, false CAP layer flags, and empty recommendations.

The browser surface returned screenshot bytes and two key screenshots were captured into the review transcript (the no-boundary defect and final cyan-overlay state), but it exposed no durable repository path. Because authorization permits committing only this report, no generated binary screenshot was added to the repository. This is the screenshot evidence boundary.

## 6. Findings ordered by severity

### QA-01 — Major — post-calculation no-analysis-area state omits mandatory unavailable-boundary copy

- **Acceptance impact:** R-02 fails; Phase 5 gate fails.
- **Reproduction:** import the supplied 74-pole KML; bulk-assign a Wi-Fi-capable WIFI model; keep `wifi_analysis_areas` empty; click **Calculate conceptual Wi-Fi**.
- **Expected:** global circle/overlap metrics remain visible and the UI explicitly says `Boundary/gap statistics unavailable — draw a Wi-Fi analysis area.` No boundary is inferred.
- **Actual:** global metrics render, per-area rows are absent, and no unavailable-boundary message is rendered. The message exists only before a result exists.
- **File/line evidence:** `frontend/app/components/EngineeringWorkspace.tsx:487` renders the unavailable-boundary copy exclusively in the `result ? ... : ...` false branch; the true branch has no `analysis_area_statistics.length === 0` empty state.
- **Preservation:** calculation and metrics are correct; this is a mandatory truthfulness/UI-state defect, not a geometry defect.

### QA-02 — Moderate — backend bulk no-op increments Wi-Fi configuration revision

- **Acceptance impact:** G-03 exact revision semantics fail.
- **Reproduction:** start with a WIFI pole whose typed Wi-Fi configuration has `notes="same"`, null radius/enabled overrides, and `configuration_revision=7`; call `PATCH /api/projects/{id}/poles/bulk` with `{"pole_ids":["p"],"patch":{"wifi_notes":"same","clear_wifi_radius_override":false,"clear_wifi_enabled_override":false}}`.
- **Expected:** unchanged fields are a no-op; revision remains 7 and `modified_at` is unchanged. This matches the final corrective report's claimed rule that unchanged fields produce no revision.
- **Actual:** HTTP 200; revision becomes 8 and `modified_at` changes even though the effective and stored user values are unchanged.
- **File/line evidence:** `backend/app/services/configuration.py:153-169`. Explicit false clear flags enter `fields` because only `None` is excluded; any Wi-Fi field then unconditionally increments revision and timestamp without comparing before/after values.
- **State impact:** geometry fingerprint correctly excludes the general revision, so this does not stale or alter a valid Wi-Fi result. It does create false edit history/provenance.

## 7. Residual risks and evidence limitations

- The product remains intentionally conceptual geometry, not verified RF design. Terrain, obstacles, antenna patterns, bands, EIRP, receiver sensitivity, propagation, interference, throughput, capacity, service quality, standards compliance, backhaul, and CAP topology/recommendations remain out of scope.
- The browser provider did not expose download paths or a persistent screenshot artifact API. Export content was checked through the exact API endpoint after the visible UI export; screenshots are transcript-only.
- The installed frontend dependency tree, production build output, temporary test stores, and browser runtime projects are ignored QA environment artifacts and are not part of the report commit.
- The known Starlette/httpx deprecation warning and MapLibre/Vinext chunk-size advisory remain non-failing.
- No professional RF or external reference validation was attempted or claimed.

## 8. Final gate verdict

**FAIL.** G-03 and R-02 are mandatory and are not satisfied. Phase 5 remains unaccepted and unclosed. The master task must review this evidence; any correction requires a separately authorized implementation pass followed by focused independent retest. Phase 6 remains gated.
