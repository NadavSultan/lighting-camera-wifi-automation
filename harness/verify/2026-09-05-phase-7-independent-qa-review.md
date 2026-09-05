# Independent QA review — 2026-09-05 — Phase 7

Verdict: **FAIL**

## Scope, independence, and non-goals

- Exact implementation commit reviewed: `044c013b2fa23a29bee6fc2b8779896084daae44`.
- Exact clean evidence worktree reviewed: `8fbaa42806b261eca706d8224eea2aec2e9f8e56`; post-implementation commits `094fc49` and `8fbaa42` contain evidence records only.
- Controlling contract and acceptance IDs: `harness/phases/phase-07.md`; `P7-DM-01` through `P7-PRD-01`.
- Reviewer/session independence: fresh independent QA; implementation summaries were treated as claims rather than proof.
- Review scope: implementation diff, focused source/tests, evidence records, deterministic package probes, source/boundary state, and master-gate eligibility.
- Non-goals: no remediation, seal, master decision, push, merge, deployment, or later-phase authorization.

## QA milestones

| Milestone | Required evidence | Result |
|---|---|---|
| Repository/diff and authorization review | Exact HEAD/status/history; implementation diff; no Phase 7 seal | PASS |
| Deterministic verification | Independent delayed fixed-clock package probe | FAIL |
| Acceptance-matrix review | Contract-to-source/test/evidence inspection | FAIL |
| Rendered/manual workflow | Reproducible production browser/package evidence | FAIL — supplied M9 record is insufficient |
| Source/prior-phase regression review | Protected-path diff and clean-tree inspection | PARTIAL PASS; full suites not rerun after static gate failure |

## Acceptance criteria

| Acceptance ID / criterion | Independent method | Evidence | Result |
|---|---|---|---|
| P7-DM-01 | Strict-contract inspection | Strict request/selection models exist, but presentation output is an unvalidated dictionary with no strict schema/model | PARTIAL / NOT PROVEN |
| P7-SN-01 | Snapshot source/test inspection | Focused tests compare the complete project before/after snapshot construction and confirm separated snapshot generation does not mutate it | PASS |
| P7-ST-01 | Freshness inspection | CAP digest is not recomputed; camera results have no fingerprint check | FAIL |
| P7-FP-01 | Two generations with identical fixed-clock inputs separated by two seconds | ZIP SHA-256 changed and byte equality was false | FAIL |
| P7-MF-01 | Compare manifest self-entry to actual ZIP member | Declared self hash/size differ from actual member | FAIL |
| P7-CSV-01 | Static focused test inspection | No blocking CSV defect confirmed; full independent execution stopped at static gate failures | NOT FULLY RERUN |
| P7-XL-01 | Delayed fixed-clock workbook/package probe | Confirmed failure: XLSX core metadata uses runtime creation time, making the workbook and containing package nondeterministic | FAIL |
| P7-KM-01 | Source/test inspection | Structured coordinate provenance and complete artifact inspection not proven | NOT PROVEN |
| P7-KM-02 | Protected behavior/source inspection | No conflicting implementation change confirmed; full regression not rerun | NOT FULLY RERUN |
| P7-PDF-01 | PDF source/test/evidence inspection | “Local vector overview” is a coordinate table; test checks only the PDF header and M9 has no page inspection | FAIL |
| P7-PR-01 | Contract/model/test inspection | Presentation JSON is parsed but not schema-validated against a strict contract | FAIL |
| P7-SC-01 | Limit/security test inspection | Required complete boundary+1 and active-content matrix is not present | NOT PROVEN |
| P7-AP-01 | API source inspection | No optimistic conflict check/409 path around metadata persistence | FAIL |
| P7-AT-01 | Focused generation-failure test inspection | Tested generation failures preserve project state and leave no partial report artifact | PASS |
| P7-UI-01 | Frontend source/test inspection | Preview ignores selected options; initial preview errors are hidden | FAIL |
| P7-UI-02 | Frontend source/test inspection | Generation reloads persisted project and replaces unsaved in-memory state without undo history | FAIL |
| P7-REG-01 | Evidence and protected-path inspection | Historical summary only; full current-tree suites not rerun after concrete static blockers | NOT PROVEN |
| P7-PRD-01 | M9 evidence inspection | Summary records hashes/control presence but not the required browser download, console, CSV/XLSX/KMZ/PDF/presentation cross-checks | FAIL |

## Verification requirements

| Exact command/workflow | Commit/worktree | Exit/result | Notes |
|---|---|---|---|
| `git status --short --branch; git rev-parse HEAD; git log --oneline --decorate -8; git diff --stat; git diff --check; git diff --name-status 8a177b7..044c013` | `8fbaa428` | exit 0 | Clean tree; implementation commit is an ancestor; no uncommitted diff |
| Independent Python fixed-clock package generation, two runs separated by two seconds; compare ZIP bytes/SHA-256 and manifest self-entry | `8fbaa428` / implementation `044c013` | probe ran; acceptance failed | ZIP hashes `c0e55858...` and `9edae38a...`; declared manifest self size 4510 vs actual 4656 |
| `.\.venv\Scripts\python.exe harness\verify\verify_phase_readiness.py --manifest harness\verify\phase-07-readiness.json` | `8fbaa428` | exit 0 / readiness PASS | Confirms manifest mechanics only; does not override independent QA failures |
| Full backend/frontend/generated/rendered block | not run | gate stopped | Static Major failures make an expensive full rerun unnecessary until remediation |

Historical implementation evidence guided selection but did not replace independent checks.

## Findings

| ID | Severity | Requirement/evidence | Finding | Required correction |
|---|---|---|---|---|
| P7-QA-01 | Major | P7-D15, P7-FP-01 | Fixed-clock package bytes are not deterministic because XLSX core properties use runtime creation time. | Pin workbook properties to the injected generation time and add a delayed deterministic regression. |
| P7-QA-02 | Major | P7-D08, P7-MF-01 | Manifest self-entry hash/size describe a preliminary body, not the actual `report-manifest.json` ZIP member. A manifest cannot contain its own final SHA-256 without a circular dependency, so literal P7-D08 compliance requires explicit user/master amendment. | Amend P7-D08 to hash every payload member except the manifest itself, store the overall package hash externally, and make validation enforce that non-circular contract. |
| P7-QA-03 | Major | P7-ST-01 | CAP result integrity is not recomputed and camera freshness is accepted without fingerprint matching. | Validate result integrity/currentness against canonical fingerprints or explicitly omit unverifiable results under the approved policy. |
| P7-QA-04 | Major | P7-AP-01, P7-UI-02 | Generation can save a stale project snapshot and the UI then replaces unsaved local engineering edits without history. Tested generation failures themselves are atomic under P7-AT-01. | Add conflict-safe metadata persistence and preserve/reconcile in-memory edits; add concurrency and undo/redo tests. |
| P7-QA-05 | Major | P7-PDF-01, P7-PR-01 | PDF vector overview and strict presentation-model validation required by contract are absent. | Render a genuine deterministic local vector overview and add a strict presentation schema/model with cross-format validation. |
| P7-QA-06 | Moderate | P7-UI-01 | Preview/checklist/blockers do not use current format/section selections; automatic preview failures are silent. | Preview the selected request and expose failures as visible blockers. |
| P7-QA-07 | Major | M0, P7-D05 | Approved reporting dependencies are broad version ranges and no reproducible backend lock evidence is recorded. | Pin/lock approved exact versions and record dependency/security/license verification. |
| P7-QA-08 | Major | AGENTS.md evidence rules, M0-M9, P7-REG-01, P7-PRD-01 | Work/execution records remain internally incomplete, and M9 does not preserve the required reproducible artifact/browser inspection evidence. | Complete exact command records on the remediation commit and independently reproduce all required production artifact/UI checks. |
| P7-QA-09 | Major | Control-document consistency | `AGENTS.md`, `docs/implementation-plan.md`, and `OPERATIONS.md` still state that Phase 7 implementation is unauthorized, contradicting the active contract, status, and completed implementation evidence. | Reconcile the stale control documents through the authorized evidence/control-document process before the next gate. |

## Definition of Done

- [x] Complete implementation diff and file boundary reviewed.
- [x] Mandatory acceptance items were mapped; blocking failures and unproven rows are explicit.
- [ ] Required deterministic and rendered checks completed successfully on the exact reviewed commit.
- [ ] Source preservation, migration, prior-phase regressions, and later-phase exclusion fully verified.
- [x] Verdict is supported without relying on unverified claims.

## Recovery protocol

1. Preserve this QA evidence and exact reviewed commit identity.
2. Remediate all findings holistically on a new implementation commit.
3. Complete and reconcile the work record, execution log, readiness manifest, and M9 evidence.
4. Rerun independent QA from the final clean tree; prior affected results are invalid.

## Allowed stopping conditions

QA is complete with a supported FAIL verdict. No seal is created and no next phase is authorized.

## Verdict and next gate

- Verdict: **FAIL**
- Open findings: `P7-QA-01` through `P7-QA-09`
- Master gate eligibility: **NO**
- Exact next action: authorize and complete bounded Phase 7 remediation, then rerun independent QA on the new exact commit.
