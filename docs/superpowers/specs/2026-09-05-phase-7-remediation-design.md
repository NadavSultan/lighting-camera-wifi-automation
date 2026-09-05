# Phase 7 QA Remediation Design

Date: 2026-09-05

Status: approved for implementation planning

## Authority and objective

The user approved bounded remediation of findings `P7-QA-01` through `P7-QA-09` from `harness/verify/2026-09-05-phase-7-independent-qa-review.md` and approved the non-circular amendment to `P7-D08`.

The remediation must restore Phase 7 implementation readiness without changing source coordinates, accepted Phase 1–6 engineering algorithms, existing updated-KML behavior, or the existing-pole operating boundary. Completion means the Phase 7 readiness verifier passes against a clean remediation implementation commit and a new independent-QA handoff is recorded. Independent QA, master PASS, and sealing remain later gates.

## Selected approach

Use targeted in-place remediation. Preserve the current reporting-service architecture and add focused contracts, validation, concurrency control, deterministic output, tests, and evidence. Do not split the reporting service into a new subsystem or perform unrelated refactoring.

## Amended manifest integrity contract

`P7-D08` is amended as follows:

- `report-manifest.json` records SHA-256 and byte size for every ZIP payload member except itself.
- The manifest must not contain a misleading self-entry.
- The SHA-256 of the complete ZIP is external to the ZIP and is exposed in the package HTTP response and persisted `last_report` metadata when persistence is requested.
- Validation must reject a missing, duplicate, unsafe, size-mismatched, or hash-mismatched payload member.

The package response will expose the complete package digest through a deterministic response header. Existing `LastReportMetadata.package_sha256` remains the persisted representation.

## Freshness and integrity

Camera geometry gains an additive calculation-input SHA-256. Camera calculation writes this fingerprint from all geometry-significant project and catalog inputs. Existing results without the fingerprint are valid legacy project data but are unverifiable for reporting and must be omitted with an incomplete-report finding until explicitly recalculated. Migration must not invent a fingerprint.

Reporting recomputes the CAP result payload digest using the canonical Phase 6 digest contract and compares it with `result_sha256`. A mismatch blocks generation as corrupt data. This supplements the existing CAP input-fingerprint and recommendation-reference checks without changing CAP planning behavior.

Lighting and Wi-Fi freshness behavior remains unchanged except for additional regression coverage.

## Deterministic formats and strict contracts

XLSX core properties, including creation and modification timestamps, use the injected report generation time. A delayed fixed-clock test must prove complete workbook and package byte equality.

The PDF local vector overview is a genuine deterministic projected vector drawing. It displays the bounded project pole extent without a network basemap and uses stable styling and ordering. Empty and degenerate extents have explicit deterministic rendering.

Presentation-model and manifest payloads use strict Pydantic output contracts. Generated JSON is validated through those contracts before serialization. Unknown, non-finite, malformed, or oversized output data fails generation.

## API concurrency and frontend state

Preview accepts the same format, section, and KMZ-layer selections as generation. The frontend sends current selections for automatic and manual preview and displays preview failures as blockers.

Report generation carries the saved project `updated_at` value as an optimistic concurrency token. The API verifies it before generation and again immediately before metadata persistence. A mismatch returns `409 Conflict`, returns no package, and persists nothing.

After successful download, the frontend merges only returned report metadata and the new saved-project timestamp into current local state. It does not reload or replace engineering fields and does not clear or append undo/redo history. Unsaved engineering edits remain intact.

## Dependencies

The approved ReportLab and XlsxWriter direct dependencies use exact versions. A repository-owned backend lock records exact transitive production and test dependencies and is verified by installation into a clean environment. The remediation evidence records package versions, licenses, vulnerability-review method and result, and the exact materialization command. No additional reporting library or external service is introduced.

## Safety and limit verification

Tests enumerate exact-limit and boundary-plus-one behavior for:

- 50 MiB package size;
- 25 MiB member size;
- 250,000 total tabular rows;
- 100,000 KML features;
- 20,000 PDF table rows with deterministic summarized overflow;
- 100 unique sanitized workbook sheets;
- 2,000 characters per cell;
- ZIP traversal and duplicate paths;
- spreadsheet formula prefixes;
- macros, hyperlinks, external images, relationships, and other active content.

Failures are atomic and leave project, source, engineering results, metadata, and temporary output unchanged.

## Evidence and control documents

The existing Phase 7 work record and execution log are reconciled rather than replaced. They record the original implementation chronology, QA failure, user-approved contract amendment, remediation commands, exact commits, and current milestone state.

`AGENTS.md`, `docs/implementation-plan.md`, and `OPERATIONS.md` are corrected to state that Phase 7 implementation was authorized, failed independent QA, and is in bounded remediation. Historical statements remain clearly labelled historical where needed.

M9 evidence must preserve reproducible commands and machine-readable results for the production 74-pole workflow: browser download, zero console errors, ZIP path/hash checks, CSV parsing, XLSX inspection, KMZ/KML parsing, structural and visual inspection of every PDF page, presentation-model validation, and cross-format counts and values.

## Test-driven execution

Each implementation correction starts with a focused failing regression that demonstrates the corresponding QA finding. The test is run and its expected failure recorded before production code changes. Minimal implementation follows, then focused and adjacent regression tests pass before moving to the next finding.

Final verification runs the complete contract block: backend tests before and after schema generation, engineering-data validation, frontend build/test/typecheck/lint, source and protected-path checks, delayed deterministic package probes, complete rendered M9 workflow, clean diff checks, and the Phase 7 readiness verifier on the remediation implementation commit.

## Authorized boundary

The remediation may change:

- the Phase 7 contract, work record, execution log, verification/readiness/handoff records, and affected current control documents;
- focused backend models, reporting, camera fingerprint, CAP digest reuse, API, dependency metadata/lock, generated schemas, and tests;
- focused frontend report API/types/component/workflow code and rendered tests;
- deterministic M9 verification helpers and evidence records.

It may not change `Input/`, frozen engineering catalogs, runtime projects, generated report packages, accepted engineering algorithms, source coordinates, proposed-layout policy, prior phase seals, or unrelated application behavior.

## Gate result

The remediation session may stop normally only after implementation readiness passes and a new independent-QA handoff is recorded. It must not create a Phase 7 seal, claim Phase 7 acceptance, or authorize post-roadmap work.
