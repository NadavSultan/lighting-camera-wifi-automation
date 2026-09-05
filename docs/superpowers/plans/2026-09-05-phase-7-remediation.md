# Phase 7 QA Remediation Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Resolve `P7-QA-01` through `P7-QA-09` under amended `P7-D08`, pass Phase 7 implementation readiness on a clean remediation commit, and record a new independent-QA handoff.

**Architecture:** Retain the current reporting service and add focused strict output contracts, deterministic writer settings, result-integrity checks, optimistic metadata persistence, selection-aware preview, and complete acceptance evidence. Camera freshness is additive and lossless: legacy geometry remains stored but is omitted from reports until recalculated with a fingerprint.

**Tech Stack:** Python 3.12, FastAPI, Pydantic 2, ReportLab, XlsxWriter, pytest, React/TypeScript, MapLibre, pnpm.

## Global Constraints

- Follow `AGENTS.md`, `harness/phases/phase-07.md`, and `docs/superpowers/specs/2026-09-05-phase-7-remediation-design.md`.
- Never change customer source bytes, pole identity/order/coordinates, accepted Phase 1–6 algorithms, or updated-KML semantics.
- Do not create a Phase 7 seal or claim acceptance.
- Write each regression test first, run it, and record the expected failure before changing production code.
- Preserve exact command, commit, warning, rendered-workflow, and source-boundary evidence.
- Stop normally only after readiness PASS on the clean remediation implementation commit and a new independent-QA handoff.

---

### Task 1: Remediation control pack and dependency preflight

**Files:**
- Modify: `harness/phases/phase-07.md`
- Modify: `harness/phases/2026-09-04-phase-7-implementation.md`
- Modify: `harness/logs/2026-09-04-phase-7-execution.md`
- Modify: `backend/pyproject.toml`
- Create: `backend/requirements.lock`

**Interfaces:**
- Consumes: QA findings `P7-QA-01`–`P7-QA-09`, approved remediation design, current Python environment.
- Produces: amended `P7-D08`, exact dependency graph, reconciled active work record and execution log.

- [ ] **Step 1: Record authority and amended P7-D08**

Change the contract’s P7-D08 row to state:

```markdown
| P7-D08 | Add `report-manifest.json` with versions, project/source hashes, generation timestamp, report-input fingerprint, included/omitted sections, warnings, and SHA-256/size for every non-manifest payload member. The manifest has no self-entry. Return the complete ZIP SHA-256 in the HTTP response and persist it in `last_report` metadata when requested. | Avoids an impossible circular self-hash while retaining independently verifiable payload and package integrity. |
```

Append the user authorization date, remediation scope, durable goal, base `fd8a43d34177ab558e2da898b989b067a0677cd6`, starting clean status, and design/plan links to the work record and execution log. Reconcile stale M0–M9 status while preserving the original chronology.

- [ ] **Step 2: Pin and lock dependencies**

Replace broad direct reporting ranges with environment-verified exact versions:

```toml
"reportlab==4.5.1",
"xlsxwriter==3.2.9",
```

Generate `backend/requirements.lock` from a clean resolution so every production and test transitive dependency is exact. Record the exact clean-install command, package versions, licenses, and vulnerability-review command/result. The resolved version numbers must be copied from command output; they must not be guessed.

- [ ] **Step 3: Run clean dependency and entry-point preflight**

Run:

```powershell
.\.venv\Scripts\python.exe -m pip check
.\.venv\Scripts\python.exe -m pip freeze --all
Set-Location .\frontend
pnpm install --frozen-lockfile --offline
pnpm run build
pnpm run test
pnpm run typecheck
pnpm run lint
```

Expected: dependency checks and all frontend entry points pass; known chunk advisory is recorded but not represented as a failure.

- [ ] **Step 4: Commit the control/preflight checkpoint**

```powershell
git add harness/phases/phase-07.md harness/phases/2026-09-04-phase-7-implementation.md harness/logs/2026-09-04-phase-7-execution.md backend/pyproject.toml backend/requirements.lock
git commit -m "chore: prepare Phase 7 remediation"
```

---

### Task 2: Deterministic XLSX and non-circular manifest integrity

**Files:**
- Modify: `backend/app/models.py`
- Modify: `backend/app/services/reporting.py`
- Modify: `backend/tests/test_phase7_reporting.py`

**Interfaces:**
- Consumes: injected `generation_time`, assembled report members.
- Produces: deterministic workbook bytes, strict manifest object, manifest hashes for non-manifest members only.

- [ ] **Step 1: Write delayed determinism and manifest tests**

Add focused tests equivalent to:

```python
def test_p7_qa_01_fixed_clock_remains_byte_identical_after_delay():
    project = bare_project()
    request = fixed_request()
    package_a, _, _ = generate_report_package(project, request)
    time.sleep(2.1)
    package_b, _, _ = generate_report_package(project, request)
    assert package_a == package_b


def test_p7_qa_02_manifest_hashes_every_payload_member_without_self_entry():
    package, manifest, _ = generate_report_package(bare_project(), fixed_request())
    members = _zip_members(package)
    assert "report-manifest.json" in members
    assert "report-manifest.json" not in manifest["members"]
    assert set(manifest["members"]) == set(members) - {"report-manifest.json"}
    for path, integrity in manifest["members"].items():
        assert integrity["size_bytes"] == len(members[path])
        assert integrity["sha256"] == hashlib.sha256(members[path]).hexdigest()
```

- [ ] **Step 2: Verify RED**

Run:

```powershell
Set-Location .\backend
..\.venv\Scripts\python.exe -m pytest -q -p no:cacheprovider tests/test_phase7_reporting.py -k "qa_01 or qa_02"
```

Expected: delayed XLSX determinism and no-self-entry assertions fail for the known QA reasons.

- [ ] **Step 3: Add strict manifest contracts and deterministic workbook properties**

Add strict member/manifest models with SHA-256 patterns, bounded sizes, typed dispositions, and forbidden extras. Pass `generation_time` into `_build_workbook` and set:

```python
workbook.set_properties({
    "title": f"Engineering report — {snapshot['project_name']}",
    "author": "Lighting Camera WiFi Automation",
    "created": _ensure_utc(generation_time).replace(tzinfo=None),
})
```

Build the final manifest once, validate it through the strict model, serialize it, and exclude `report-manifest.json` from `members`.

- [ ] **Step 4: Verify GREEN and adjacent integrity**

Run:

```powershell
..\.venv\Scripts\python.exe -m pytest -q -p no:cacheprovider tests/test_phase7_reporting.py -k "qa_01 or qa_02 or p7_fp or p7_manifest or p7_xlsx"
```

Expected: all selected tests pass.

- [ ] **Step 5: Commit**

```powershell
git add backend/app/models.py backend/app/services/reporting.py backend/tests/test_phase7_reporting.py
git commit -m "fix: make Phase 7 packages deterministic"
```

---

### Task 3: Camera freshness and CAP result integrity

**Files:**
- Modify: `backend/app/models.py`
- Modify: `backend/app/services/camera_geometry.py`
- Modify: `backend/app/services/cap_planning.py`
- Modify: `backend/app/services/reporting.py`
- Modify: `backend/tests/test_phase3_camera_geometry.py`
- Modify: `backend/tests/test_phase6_cap_planning.py`
- Modify: `backend/tests/test_phase7_reporting.py`

**Interfaces:**
- Produces: `camera_calculation_input_sha256(project) -> str`; reusable canonical CAP result digest verifier.
- Consumes: exact revision pins, persisted geometry provenance, and geometry-significant project state.

- [ ] **Step 1: Write failing freshness and tamper tests**

Cover:

```python
def test_p7_qa_03_legacy_camera_geometry_is_omitted_until_recalculated():
    project = camera_project_with_geometry()
    project.camera_geometry.calculation_input_sha256 = None
    snapshot = build_report_snapshot(project)
    assert snapshot["included_calculated"]["camera_geometry"] is None
    assert snapshot["dispositions"]["cameras"] == "stale_omitted"


def test_p7_qa_03_camera_input_change_invalidates_report_inclusion():
    project, fixtures, cameras = calculated_camera_project()
    project.pole_edits[next(iter(project.pole_edits))].fixture_configuration.fixture_azimuth_deg += 1
    snapshot = build_report_snapshot(project)
    assert snapshot["included_calculated"]["camera_geometry"] is None


def test_p7_qa_03_tampered_cap_result_blocks_generation():
    project = project_with_current_cap_result()
    project.cap_calculations.result.assignments[0].hop_count += 1
    with pytest.raises(ReportGenerationError, match="CAP result.*hash"):
        generate_report_package(project, fixed_request())
```

- [ ] **Step 2: Verify RED**

Run the exact three tests and confirm they fail because camera has no fingerprint and CAP payload integrity is not recomputed.

- [ ] **Step 3: Implement additive fingerprints and reusable CAP digest**

Add `calculation_input_sha256: str | None = None` to `CameraGeometryLayer`. Calculate and persist it only during explicit camera recalculation. Do not populate it in migration.

Extract Phase 6’s canonical digest operation into a reusable function:

```python
def cap_result_sha256(result: CapPlanningResult) -> str:
    payload = result.model_dump(mode="json", exclude={"result_sha256"})
    return hashlib.sha256(
        json.dumps(payload, sort_keys=True, separators=(",", ":"), allow_nan=False).encode("utf-8")
    ).hexdigest()
```

The extraction must preserve the exact existing payload convention. Reporting compares the recomputed digest before inclusion.

- [ ] **Step 4: Verify GREEN and prior-phase regression**

Run:

```powershell
..\.venv\Scripts\python.exe -m pytest -q -p no:cacheprovider tests/test_phase3_camera_geometry.py tests/test_phase6_cap_planning.py tests/test_phase7_reporting.py -k "camera or cap or p7_st or qa_03"
```

Expected: selected Phase 3, Phase 6, and Phase 7 tests pass.

- [ ] **Step 5: Commit**

```powershell
git add backend/app/models.py backend/app/services/camera_geometry.py backend/app/services/cap_planning.py backend/app/services/reporting.py backend/tests/test_phase3_camera_geometry.py backend/tests/test_phase6_cap_planning.py backend/tests/test_phase7_reporting.py
git commit -m "fix: verify report result freshness"
```

---

### Task 4: Conflict-safe package metadata and selection-aware preview

**Files:**
- Modify: `backend/app/models.py`
- Modify: `backend/app/main.py`
- Modify: `backend/tests/test_phase7_reporting.py`
- Modify: `frontend/app/lib/types.ts`
- Modify: `frontend/app/lib/api.ts`
- Modify: `frontend/app/lib/phase7-report-workflows.mjs`
- Modify: `frontend/app/lib/phase7-report-workflows.d.ts`
- Modify: `frontend/app/components/ReportPanel.tsx`
- Modify: `frontend/app/components/EngineeringWorkspace.tsx`
- Modify: `frontend/tests/rendered-html.test.mjs`

**Interfaces:**
- Request: `expected_project_updated_at` plus current formats/sections/KMZ layers.
- Response headers: complete ZIP SHA-256, report status, generated timestamp, resulting saved-project timestamp.
- UI callback: merge `last_report` metadata/timestamps only; never replace the project.

- [ ] **Step 1: Write backend concurrency and preview tests**

Add tests proving:

```python
def test_p7_qa_04_stale_expected_timestamp_returns_409_without_output_or_write():
    response = client.post(package_url, json={
        "expected_project_updated_at": stale_time,
        "persist_last_report_metadata": True,
    })
    assert response.status_code == 409
    assert store.load(project.id).model_dump(mode="json") == before


def test_p7_qa_06_preview_uses_requested_sections_and_formats():
    response = client.post(preview_url, json={
        "formats": {"pdf_summary": False},
        "sections": {"cap": False},
    })
    assert response.status_code == 200
    assert preview_item(response.json(), "cap")["enabled"] is False
    assert preview_format(response.json(), "pdf_summary")["enabled"] is False
```

Also simulate a store update between generation and metadata persistence and require a second `409` check.

- [ ] **Step 2: Verify backend RED**

Run focused `qa_04` and `qa_06` tests. Expected: missing request token/POST preview/409 behavior causes failures.

- [ ] **Step 3: Implement backend compare-and-save behavior**

Add strict expected timestamp validation. Compare against the loaded record before generation and re-load immediately before persistence. Return `409 Conflict` on either mismatch. Expose:

```text
X-Report-Package-SHA256
X-Report-Status
X-Report-Generated-At
X-Project-Updated-At
```

Change preview to a selection-bearing POST endpoint while retaining the GET endpoint only if compatibility tests require it.

- [ ] **Step 4: Write frontend state and error tests**

Add rendered/helper tests proving current selections reach preview, preview errors render as blockers, returned report metadata merges into the current project, unsaved engineering values remain equal, and undo/redo lengths do not change.

- [ ] **Step 5: Verify frontend RED**

Run `pnpm run test`. Expected: new tests fail because preview ignores options and generation reloads/replaces the project.

- [ ] **Step 6: Implement frontend metadata-only merge**

Return package response metadata from `downloadReportPackage`; remove `getProject` from `ReportPanel`; replace `onProjectRefreshed` with a metadata-only callback. Keep the current project object’s engineering fields and history arrays unchanged.

- [ ] **Step 7: Verify GREEN**

Run focused backend tests and:

```powershell
pnpm run test
pnpm run typecheck
pnpm run lint
pnpm run build
```

Expected: all pass.

- [ ] **Step 8: Commit**

Commit the listed backend/frontend/test files with:

```powershell
git commit -m "fix: make report generation conflict safe"
```

---

### Task 5: Genuine PDF vector overview and strict presentation model

**Files:**
- Modify: `backend/app/models.py`
- Modify: `backend/app/services/reporting.py`
- Modify: `backend/tests/test_phase7_reporting.py`

**Interfaces:**
- Produces: strict `PresentationModel`; deterministic ReportLab projected drawing.

- [ ] **Step 1: Write failing strict-model and PDF structure tests**

Require presentation validation to reject an extra key and require each generated PDF to contain vector path operators and bounded pole markers, not only a coordinate table. Include empty and single-coordinate projects.

- [ ] **Step 2: Verify RED**

Run:

```powershell
..\.venv\Scripts\python.exe -m pytest -q -p no:cacheprovider tests/test_phase7_reporting.py -k "qa_05 or p7_pdf or p7_presentation"
```

Expected: strict model is absent and vector assertions fail.

- [ ] **Step 3: Implement strict presentation output and vector drawing**

Define nested strict Pydantic output models for inventory, subsystems, and the presentation root. Validate before JSON encoding.

Use the project’s metre CRS to normalize pole points into a fixed ReportLab `Drawing` viewport. Draw a border, deterministic pole markers, and a north indicator with stable colors and source-order-independent coordinate ordering. For empty/single-point extents, render explicit bounded fallback geometry.

- [ ] **Step 4: Verify GREEN and render every page**

Run selected tests, then rasterize or render every generated PDF page with the repository-discovered local PDF tool. Record page count, dimensions, rendering exit code, and human inspection result in M9 evidence.

- [ ] **Step 5: Commit**

```powershell
git add backend/app/models.py backend/app/services/reporting.py backend/tests/test_phase7_reporting.py
git commit -m "fix: validate and render report summaries"
```

---

### Task 6: Complete security, limits, and KMZ provenance coverage

**Files:**
- Modify: `backend/app/services/reporting.py`
- Modify: `backend/tests/test_phase7_reporting.py`

**Interfaces:**
- Produces: explicit limit guards and artifact validators for every P7-D11/P7-D12 boundary.

- [ ] **Step 1: Parameterize every exact and boundary-plus-one test**

Create an enumerated matrix for package/member bytes, rows, features, PDF rows, sheets, and cell characters. Each row runs once at the exact limit and once at limit plus one. Add ZIP duplicate/traversal and OOXML active-content relationship inspections.

- [ ] **Step 2: Verify RED**

Run `-k "p7_limits or p7_security or qa_sc"` and record which missing guards or validators fail.

- [ ] **Step 3: Implement only missing guards and provenance**

Apply limits before expensive serialization where possible. Ensure derived KMZ feature descriptions include source pole ID, exact source WGS84 coordinate text/numeric coordinate, calculation model/version, result fingerprint, and derived/conceptual label as applicable.

- [ ] **Step 4: Verify GREEN**

Run all Phase 7 reporting tests. Expected: complete matrix passes with no skips.

- [ ] **Step 5: Commit**

```powershell
git add backend/app/services/reporting.py backend/tests/test_phase7_reporting.py
git commit -m "test: complete Phase 7 safety coverage"
```

---

### Task 7: Generated contracts, control-document consistency, and full regression

**Files:**
- Modify: `schemas/project.schema.json`
- Modify: `schemas/openapi.json`
- Modify: `AGENTS.md`
- Modify: `PROJECT_CONTEXT.md`
- Modify: `docs/current-status.md`
- Modify: `docs/implementation-plan.md`
- Modify: `OPERATIONS.md`
- Modify: `GOALS.md`
- Modify: `PLANS.md`
- Modify: `harness/phases/2026-09-04-phase-7-implementation.md`
- Modify: `harness/logs/2026-09-04-phase-7-execution.md`

**Interfaces:**
- Produces: fresh schemas and one consistent control-state statement: remediation complete awaiting independent QA only after readiness passes.

- [ ] **Step 1: Regenerate contracts**

Run:

```powershell
Set-Location .\backend
..\.venv\Scripts\python.exe -m scripts.export_schema
```

Expected: generated schemas reflect strict output/request and camera fingerprint fields.

- [ ] **Step 2: Reconcile current control documents**

Remove stale statements that Phase 7 implementation is unauthorized. Preserve dated history and state that implementation failed QA at `fd8a43d`, remediation was authorized on 2026-09-05, and no gate/seal exists.

- [ ] **Step 3: Run the full deterministic block**

Run the exact final verification block from `harness/phases/phase-07.md`, with isolated pytest temp paths where required. Run backend before and after schema generation. Record exact counts, exits, warnings, commit/worktree identity, and protected-path diff.

- [ ] **Step 4: Commit implementation**

Review `git diff --check`, protected files, and all changed paths. Commit all product, test, generated, dependency, and control-document remediation changes as the Phase 7 remediation implementation commit.

---

### Task 8: Production M9, readiness, and independent-QA handoff

**Files:**
- Modify: `harness/verify/2026-09-04-phase-7-m9-summary.json` or create a new dated remediation M9 summary
- Create: `harness/verify/2026-09-05-phase-7-remediation-verification-summary.md`
- Modify: `harness/verify/phase-07-readiness.json`
- Create: `docs/phase-7-independent-qa-remediation-handoff-2026-09-05.md`
- Modify: `harness/phases/2026-09-04-phase-7-implementation.md`
- Modify: `harness/logs/2026-09-04-phase-7-execution.md`

**Interfaces:**
- Consumes: clean remediation implementation commit.
- Produces: reproducible M9 artifacts, readiness PASS, evidence-only handoff commit.

- [ ] **Step 1: Execute production 74-pole M9**

Start production backend/frontend on recorded temporary ports. Through the browser, import `Input/Miracle_Mile_Lighting_Poles.kml`, open report preview, select options, download the package, and record zero console errors.

Validate:

```text
ZIP safe paths, uniqueness, member count, payload hashes, package response hash
all CSV files parsed with stable rows/columns
XLSX opened and checked against CSV canonical rows and active-content prohibitions
KMZ and KML parsed with provenance and derived/conceptual labels
every PDF page structurally parsed, rendered, and visually inspected
presentation-model JSON validated through the strict schema
cross-format source hash, pole count, subsystem status, values, warnings, and fingerprints
updated KML remains CAP/report-free and contains all 74 source poles
```

- [ ] **Step 2: Create current verification summary and readiness manifest**

List every milestone and acceptance ID with exact evidence. Reference the remediation implementation commit, not the original implementation commit. Do not mark unexecuted checks PASS.

- [ ] **Step 3: Commit evidence-only records**

Commit M9, verification, work/log reconciliation, readiness manifest, and handoff records without product changes.

- [ ] **Step 4: Run readiness against the clean evidence tree**

```powershell
.\.venv\Scripts\python.exe harness\verify\verify_phase_readiness.py --manifest harness\verify\phase-07-readiness.json
git status --short
```

Expected: readiness PASS and clean worktree.

- [ ] **Step 5: Final handoff state**

The handoff must state:

```text
Implementation: remediation complete
Independent QA: pending fresh review
Master gate: ineligible until QA PASS
Phase 7 seal: absent
Next action: fresh independent QA on the exact clean evidence commit
```

Do not create a seal or mark the durable goal complete until the readiness PASS and handoff are both recorded.
