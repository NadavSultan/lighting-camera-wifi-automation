# Scoped master handoff — 2026-09-07 — BL-001

## Requested decision

Record an **item-based scoped master decision** for post-roadmap item **BL-001** only. Independent QA recorded **PASS**. This handoff is not itself that decision, not BL-001 acceptance, not a phase seal, and not merge authority.

Write the decision at `docs/post-roadmap-bl-001-scoped-master-decision-2026-09-07.md`, following the structure of `docs/post-roadmap-bl-1-7-scoped-master-decision-2026-09-07.md`.

## Identity (re-inspect; do not trust this file as proof)

- Branch: `codex/bl-006-ies-associations`
- HEAD: `1febc8768ffac3ef38b212028867dab34790bff9` (`docs: authorize BL-001 free EOX tiles as a replaceable satellite backend`)
- Implementation identity: **dirty worktree** (uncommitted product + harness + Independent QA review). **No** sealed implementation commit.
- Stages 1–7 CONDITIONAL PASS remains `docs/post-roadmap-bl-1-7-scoped-master-decision-2026-09-07.md` (implementation commit `02c027ef`).
- Preserve the worktree. Do not reset, clean, stash, revert, merge, or create Phase 8 / any harness seal.

## Controlling records

- Backlog: `docs/post-roadmap-backlog.md` BL-001
- Plan Task 8: `docs/superpowers/plans/2026-09-06-post-roadmap-implementation-plan.md`
- Provider: `docs/post-roadmap-bl-001-provider-authorization-2026-09-07.md`
- Stage: `harness/phases/2026-09-07-stage-8-bl-001-gated.md`
- Independent QA PASS (claims until re-inspected): `harness/verify/2026-09-07-bl-001-independent-qa-review.md`
- Implementer claims only: `harness/verify/2026-09-07-bl-001-verification.md`

## Authority and still unauthorized

Authorized product: Standard = current OSM raster. Satellite = environment-configured public tiles. First authorized backend = free non-commercial EOX Sentinel-2 cloudless public WMTS with required attribution. Session-only Standard vs Satellite (not an EOX identity). Config in environment / `.env.example` names only; no live secrets; not project JSON.

Still unauthorized: OBS-01; Phase 8 / any harness seal; merge to `main`; project-schema change; baking a provider into saved projects; commercial/paid mosaic. Do not use `verify_phase_readiness.py` as the item gate.

## Required master actions

Independent QA is a claim set. Re-inspect git identity and the live diff. Re-run enough deterministic checks on this exact dirty tree to support PASS, CONDITIONAL PASS, or FAIL. Dispose `BL001-01`–`BL001-04` and QA findings `QA-BL001-LIVE`, `QA-BL001-ATTR`, `QA-BL001-ENV`, and excluded OBS-01.

Bound the live MapLibre residual: either run the Task 8 walkthrough, or formally accept `QA-BL001-LIVE` as residual risk (same pattern as Stages 1–7 `QA-PR-03`). Helper tests must not be treated as live overlay-survival proof.

If commit is authorized: one bounded commit of the reviewed tree plus the decision file. `frontend/.env.example` is gitignored by existing `.env*`; a later commit, if authorized, must `git add -f frontend/.env.example` unless master chooses a tracked alternative. Do not amend `.gitignore` without an explicit boundary finding. Merge and push remain unauthorized unless this decision explicitly says otherwise.

## Gate status

Independent QA PASS is recorded. Scoped master decision is the next gate. This handoff does not accept BL-001.
