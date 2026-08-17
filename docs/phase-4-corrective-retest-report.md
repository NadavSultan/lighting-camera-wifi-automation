# Phase 4 focused corrective retest report

Date: 2026-08-17  
Role: independent Phase 4 QA engineer  
Scope: focused corrective retest of P4-IR-01 through P4-IR-07

## Overall result

**FAIL**

Phase 4 cannot be formally closed. Further corrective implementation and an independent retest are required for the unresolved P4-IR-05 save/open-path failure described below. Phase 5 conceptual Wi-Fi may not yet be considered for separate authorization. This report neither authorizes nor begins Phase 5.

Six findings pass their focused retests: P4-IR-01, P4-IR-02, P4-IR-03, P4-IR-04, P4-IR-06, and P4-IR-07. P4-IR-05 only partially passes: the lighting calculation endpoint now rejects invalid CRS and unsafe spacing with controlled 422 responses, but the shared project save/open paths still invoke Phase 3 camera recalculation with an uncaught `pyproj.exceptions.CRSError`, returning HTTP 500 for `projected_crs="NOT-A-CRS"`.

## Review boundary and environment

- Repository: `C:\Users\Nadav\Desktop\Automation Project\lighting-camera-wifi-automation`.
- Tested HEAD: `f170950f3b16e83a9cbae9ec06ea3a1e22754a12` (`docs: record Phase 4 corrective implementation`).
- Corrective implementation under test: `50fa336eee8a1619308aa9d25c189da8d0e4a3cd`, whose parent is `cce899b4df5fc56f6380bfee79b3cec10193499c`.
- Baselines retained: Phase 4 implementation `eafd320369600ff4c8d32b8dc32c80e1e81b3d24` and pre-QA correction `5ada5665ed26a85210da1ff1d4fa49d787cf276d`.
- Host: Windows NT `10.0.26200.0`; Python `3.12.13`; Node.js `24.19.0`.
- Production-rendered application: Vinext production build on `http://127.0.0.1:3031`, isolated FastAPI service on `http://127.0.0.1:8000`, and isolated QA project/catalog storage under the operating-system temporary directory.
- The corrective completion report was treated as an unverified claim set. Application code, schemas, tests, catalogs, source inputs, governance files, and prior reports were not modified. Temporary QA runtime projects and probes were isolated and removed where applicable. This report is the only repository write.

## Repository and evidence integrity

- The requested commit chain is linear: `eafd320` -> `9a7e5a4` -> `5ada566` -> `cce899b` -> `50fa336` -> `f170950`.
- `docs/phase-4-integration-review-and-qa.md` has SHA-256 `A2857EA33C5A92A2836575E51CD490D57EF9780A9DFF4BCF6C4E4953BFDDD96A`, exactly the required value. Its Git blob is `756507e952fe7ade5231e9b18e285f28c36efb16` at both corrective implementation and report commits.
- The original Phase 4 completion report remains Git blob `2c44e6096fdf19a8dc2aa33b4762e17419e56db3`; the pre-QA corrective report remains blob `60509a9d7dde7410c28607f8b86a892811a56eb0`.
- The `Input/` Git tree is identical at the governance baseline and corrective implementation: `7e39d2625dccfd5f72c936db5a1f87cafe61b2cd`. No `Input/` file or frozen Phase 1 fixture, camera, network, or luminaire catalog changed.
- The engineering/source validator passed all seven catalog/schema pairs and all supplied-source hashes. The rendered first pole retained raw coordinate `-80.26234411,25.74920999,0`.
- No Phase 5 Wi-Fi calculation, CAP recommendation, reporting, proposed-pole, optimization, or standards-compliance implementation was found. Phase 5+ controls remained disabled.
- `git diff --check` reported no whitespace defect. Existing ignored dependency, cache, build, runtime-data, and temporary directories were identified; no suspicious tracked or untracked application file preceded this report.

## Finding-by-finding retest

### P4-IR-01 — PASS — stale lighting-result invalidation

Independent fingerprint probes confirmed immediate invalidation for height, fixture azimuth, active state, fixture type, fixture model revision, mounting-template revision, exact IES revision, lighting properties, restore-pole, authoritative source longitude, selected CRS, area geometry, plane elevation, spacing, and maintenance factor. Every changed case removed the result and reset the area to `not-calculated`.

The focused API exercise additionally passed per-pole save, bulk height/azimuth, fixture model, exact IES ID/revision, active-state, restore, explicit revision reselection/adoption, get/open, and recalculation paths. A client-submitted stale result with the prior fingerprint was removed before persistence. Note-only, camera-only, and Wi-Fi-only mutations retained the same fingerprint and did not invalidate the valid result.

Rendered evidence: a 156-point result displayed `Eavg 15.70 lx`, `Emin 1.48 lx`, and `Emax 46.06 lx`. Changing the contributing height from 10 m to 12 m immediately changed the row to `Not calculated`. Save and project-JSON reopen retained the 12 m input and no stale result. A later valid recalculation at 12 m produced a new 156-point result (`13.57/1.89/32.29 lx`), demonstrating that invalidation did not prevent legitimate recalculation.

### P4-IR-02 — PASS — historical metadata integrity

A revision-1 record with immutable bytes and SHA was resolved from `file_history` while revision 2 was current. Canonical revision 1 retained its exact SHA, filename, warning, metadata, 10 lx nadir output, and provenance until explicit adoption; explicit adoption alone moved the pin and output to revision 2 and 20 lx.

Independent corrupt-history probes altered input watts, photometric type, vertical and horizontal angle counts, and vertical and horizontal angle ranges without changing Base64 or SHA. Every mismatch failed clearly (`parsed metadata does not match its immutable bytes` or an earlier strict corrupt-record rejection). Missing metadata failed, unchanged canonical metadata calculated, and no current-record fallback occurred.

### P4-IR-03 — PASS — C-plane domains and seam

- Accepted: one rotationally symmetric plane, complete 0-90, complete 0-180, and complete 0-360 data.
- Rejected: `[10,20]`, non-zero-start `[10,90]`, duplicate planes, descending/non-monotonic planes, and a discontinuous C0/C360 row.
- Seam tolerance: absolute difference `0.999e-9 cd` passed and `1.001e-9 cd` failed; at a `1e9 cd` baseline, relative differences `0.999` passed and `1.001` failed, matching the stated `1e-9` relative-or-absolute rule.
- All four supplied IES files remained valid and calculation-eligible only through their approved paths. Prior exact sample, interpolation, symmetry, endpoint, and seam behavior remained green.

### P4-IR-04 — PASS — finite-value and persistence safety

The `1e308` candela by `1e308` multiplier file was rejected as producing non-finite scaled intensity. Strict result models rejected NaN, positive infinity, and negative infinity. Focused calculation cases covered finite guards at scaled intensity, interpolation, per-fixture output, summation, maintenance scaling, retained contributions, statistics, ratios, projected coordinates, and WGS84 transforms.

Expected numerical failures returned 422 on the lighting calculation path and did not save the working payload. A prior valid result/project reopened unchanged. A deliberately corrupt stored project with non-finite result data returned 422 `Stored project is invalid or corrupt`, not 404, and no JSON `null` substitution was accepted as a current lighting result.

### P4-IR-05 — FAIL — invalid CRS still returns 500 on shared save/open paths

Spacing and lighting-calculation checks passed: `5e-324` and `0.009999999999 m` were rejected; exact `0.01 m` and normal `2 m` were accepted; arithmetic/index overflow was converted to `Grid spacing and projected bounds produce unsafe lattice indices`. The lighting calculation endpoint returned controlled 422 responses for `NOT-A-CRS`, geographic `EPSG:4326`, and non-metre projected `EPSG:2263`, preserving the prior valid stored result.

The broader required no-500 contract failed on project persistence:

- **Severity:** Major.
- **Affected components:** `backend/app/main.py` shared `recalculate()` use in `save_project` and `open_project`; `backend/app/services/camera_geometry.py` `calculate_camera_geometry()` CRS construction.
- **Reproduction:** (1) create an isolated blank project; (2) submit a project payload whose `projected_crs` is `NOT-A-CRS` to `PUT /api/projects/{id}`, or open an isolated no-source project JSON carrying that CRS through the rendered **Open Project** workflow; (3) observe the response and server trace.
- **Expected:** readable 4xx invalid-CRS feedback, no internal-server failure, and preservation of the prior project.
- **Actual:** save returned HTTP 500. Rendered open displayed `Failed to fetch`; the access log recorded `POST /api/projects/open` 500. Both traces terminate at `camera_geometry.py` `CRS.from_user_input(project.projected_crs)` with uncaught `pyproj.exceptions.CRSError: Invalid projection: NOT-A-CRS`.
- **Preservation evidence:** evaluation occurs before `project_store.save`, so the prior stored project remained readable. The separate valid rendered project still contained all 74 poles, its valid CRS, source bytes, and camera priority area.
- **Phase-gate impact:** gate-failing. The correction protects the lighting endpoint but does not meet the requested controlled CRS behavior across supported save/open workflow paths.

### P4-IR-06 — PASS — boundary tolerance

For minimum X, maximum X, minimum Y, and maximum Y edges, lattice points exactly on the boundary passed, points `9.99e-8 m` outside passed, and points `1.001e-7 m` outside failed. Corner/vertex cases followed the same Euclidean tolerance. Candidate enumeration was expanded before `ceil`/`floor`; buffered acceptance remained authoritative. No duplicate appeared, ordinary grids were unchanged, ordering remained deterministic Y-then-X, identities were stable, and the candidate safeguard and 25,000 accepted-point limit remained active.

### P4-IR-07 — PASS — lighting wording

The focused frontend suite covered fewer than three vertices, duplicate-only vertices, self-intersection, degeneracy, non-finite coordinates, and WGS84 bounds. Every Phase 4 error used `calculation area` or `lighting calculation area` and none used `priority area`.

Rendered empty redraw displayed `A lighting calculation area requires at least three distinct vertices.` The invalid redraw preserved the prior polygon and 156-point result. The separate Phase 3 camera collection continued to display `QA camera priority`; Phase 3 priority-area wording and geometry regressions remained green.

## Rendered smoke and authorized deletion

The production-rendered application imported `Input/Miracle_Mile_Lighting_Poles.kml` as exactly 74 source poles. The Phoenix 100 W file was uploaded through the real catalog workflow, retained its filename and `4a897fb04b6d...` SHA prefix, was explicitly associated to Phoenix 1 LITE, and was explicitly selected at revision 1. One representative pole was configured at 10 m and 0 degrees, then used for the valid 156-point calculation described above.

Calculation Areas, Calculation Points, and Lighting Results remained distinct from camera FOV, overlap, warnings, and Priority Areas. The professional-reference disclaimer and non-compliance wording remained visible. Conceptual Wi-Fi P5, Recommended CAP P6, and CAP Connections P6 stayed disabled.

The authorized temporary deletion was exercised in the rendered application. Before deletion there were 74 poles, one temporary calculation area with its same-ID 156-point result, and one camera priority area. Clicking the calculation area's **Delete** removed only `qa-lighting-1` and its result. After save and API reopen there were 74 poles, zero calculation areas, zero lighting-result keys, and the unchanged camera priority area `qa-priority-1`; the first raw source coordinate remained exact. No source pole, source file, catalog, or camera priority area was deleted.

Browser console error/warning logs were empty. Valid rendered workflow requests were 2xx. The expected invalid-spacing action was handled locally with the controlled message `Grid spacing must be finite, at least 0.01 m, and no greater than 1000 m`; the stored 2 m setting remained. The invalid-CRS open request was the single relevant failed network request and is the confirmed HTTP 500 defect above.

## Performance advisory

A focused service-level supported case generated exactly 19,319 ordered points from 64 contributors (1,236,416 point-contributor products) in 5.909 seconds on this host. Statistics were finite, all 64 fixture provenance records were retained, and per-point contributions were omitted above the 100,000 threshold as designed. This is not a contractual latency threshold and is not directly comparable to the prior roughly 80-second rendered end-to-end observation, but no material corrective regression was observed in the calculation service.

## Regression and contract results

- Focused Phase 4 corrective backend suite: PASS, 31 tests.
- Complete backend suite: PASS, 116 tests, one existing Starlette/httpx2 deprecation warning.
- Focused Phase 1-3 files: PASS, 84 tests.
- Engineering/source validator: PASS, seven catalog/schema pairs and supplied hashes.
- Exact fresh project JSON Schema and OpenAPI comparison: PASS.
- Exact operational fixture/camera/IES schema generation, including IES contract `1.2.0`: PASS.
- Supported migrations from `1.0.0`, `2.0.0`, `2.1.0`, `2.2.0`, and `2.3.0`: PASS, five cases.
- Project schema `2.4.0` and software/API `0.4.0`: confirmed.
- Frontend rendered/workflow tests: PASS, 9 tests.
- Strict TypeScript: PASS.
- ESLint: PASS using the pinned direct ESLint binary. The package-manager wrapper attempted a noninteractive dependency-directory refresh and aborted before lint; this was a wrapper/toolchain condition, not a lint failure.
- Production Vinext build: PASS with existing non-failing route-classification and large-chunk advisories.
- `git diff --check`: PASS.

No Phase 1, Phase 2, or Phase 3 regression caused by the correction was confirmed.

## Confirmed defects

- **P4-IR-05 remains unresolved (Major):** invalid CRS can still produce HTTP 500 and rendered `Failed to fetch` on supported project save/open paths because shared Phase 3 camera recalculation does not control `CRSError`. Full reproduction, evidence, and gate impact are recorded in the P4-IR-05 section.

## Regressions

None confirmed. The P4-IR-05 save/open failure is an incomplete cross-path correction, not evidence that the corrective commit broke a previously passing Phase 1-3 behavior.

## Accepted limitations

- The simplified direct horizontal Type C model remains unvalidated against AGi32 or another professional reference.
- Terrain, slope, occlusion, obstruction, shadow, reflected light, interreflection, atmosphere, near-field luminous-opening geometry, physical tilt, and depreciation beyond the explicit maintenance factor remain excluded.
- No compliance, suitability, target recommendation, professional-grade equivalence, proposed-pole, optimization, Wi-Fi coverage, CAP recommendation, or reporting claim was introduced.

## Advisory toolchain findings

- Existing non-failing Starlette/httpx2 deprecation warning.
- Existing production-build MapLibre/large-chunk and route-classification advisories.
- The `pnpm run lint` wrapper attempted dependency refresh and aborted in a non-TTY environment; direct pinned ESLint passed with exit code 0.
- Performance timing is advisory only and introduces no latency requirement.

## Environmental blockers and unverified claims

None. The required focused behaviors, rendered deletion, rendered failure path, performance case, regressions, contracts, migrations, source integrity, and phase gating were all independently exercised. The browser interface exposed console logs but not a separate request ledger; backend access logs and traces provided exact status and failure evidence for every relevant local request.

## Final gate

**FAIL**

- **Can Phase 4 be formally closed?** No.
- **Is further corrective implementation and retest required?** Yes. P4-IR-05 must be corrected across save/open/shared recalculation paths and independently retested; the six passing corrective findings do not require reopening unless that correction affects them.
- **May Phase 5 be considered for separate authorization?** No, not while this Phase 4 gate remains failed. This report does not authorize or begin Phase 5.
