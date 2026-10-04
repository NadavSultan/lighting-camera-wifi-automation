# Work record — 2026-10-04 — Camera range/lens/distance UX

Status: IMPLEMENTATION_COMPLETE_AWAITING_QA; clean readiness PASS.

## Scope, authority, and non-goals

- Requested work: approved spec and implementation plan in docs/superpowers, dated 2026-10-04. Spec and plan separately approved in this chat.
- Controlling documents: `docs/superpowers/specs/2026-10-04-camera-range-lens-distance-design.md`; `docs/superpowers/plans/2026-10-04-camera-range-lens-distance.md`; accepted BL-016 scoped master gate 2026-09-30.
- Authorized file boundary: plan Execution Identity and File Boundary; supporting configurations read-only. Generated OpenAPI may change; other four schema outputs must remain identical.
- Base: `98ac861e5eb9bc1587604f3f43be61908baabfb2`, branch `codex/bl016-heatmap-correction`, existing linked worktree. Starting diff empty; sole untracked file is this session's approved draft plan.
- Non-goals: no merge/push/seal/acceptance; no Phase 3 engine or stored-metric changes, catalog/input edits, source movement, or new dependencies.
- Durable goal: thread `01a10656-218f-7493-a7da-e7108defa48d`, created using create_goal, active.
- Stopping condition: full scoped implementation, deterministic and real 74-pole browser evidence, clean readiness PASS and independent-QA handoff.

## Environment and file-boundary preflight

- Isolation: git-dir is main repository .git/worktrees/bl016-heatmap-correction; common-dir is main .git; no superproject. Main checkout untouched.
- Runtime discovery: Python 3.12.10, Node v24.19.0, Corepack pnpm 12.3.4; Chrome and Edge installed.
- Locked materialization: active. Sandboxed pip failed socket access; sandboxed pnpm failed access-denied removal. Approved escalated locked installs are running; no lock changes authorized.
- Build/test/lint/typecheck: pending baseline; entry points inspected from package.json / pyproject.toml.
- Generated output: exporter writes five known schemas, only OpenAPI may differ for this scope. Validator entry point inspected; baseline pending.
- Browser/ports: required Chrome production access; 8070/3070 listener query returned no entries. Runtime data under ignored temporary paths.
- Supporting configurations: inspected pyproject/requirements, package/workspace/lock, Vite/TS/ESLint/PostCSS, hosting config/build plugin and worker entry point; read-only.
- Ignored writes: .venv, node_modules, dist, .wrangler, tsbuildinfo, harness/tmp; scoped records under harness/logs/verify/phases.

## Milestones and acceptance

- M0 preflight: PASS.
- M1 distance API: PASS; UX-05/08.
- M2 bounded preview: PASS; UX-01/02/03/08.
- M3 pinned specs: PASS; UX-04.
- M4 transient interaction: PASS; UX-06/07/08.
- M5 final/readiness: PASS; UX-09 and full browser acceptance.
- Acceptance IDs and verification requirements: approved plan Acceptance Coverage and Final Verification Commands; no duplicated product contract.

## Changes and evidence

- Exact command records: `harness/logs/2026-10-04-camera-range-lens-distance.md` and paired command outputs.
- Ruling: use the repository work record/log as the durable inline ledger and plain Windows commands instead of Unix skill shell helpers; preserves the same brief/base/result records without unsupported helper execution.
- Shared-interface scan: Task 1 measureMapDistance feeds Task 4, Task 2 helper feeds EngineeringMap; Task 3 uses existing catalog types. No conflicting names detected.

## Definition of Done and gate

All implementation milestones and UX checks are evidenced in the summary/readiness manifest. Independent QA/master pending; seal absent. Required deterministic/generated/source/browser/boundary checks and clean readiness required before handoff. Follow AGENTS.md recovery protocol; no proven blocker.

### M0 preflight result
Both escalated locked installs exited 0; pip check, backend (367 tests), validator, exporter, frontend (113 tests), typecheck, lint and production build exited 0 at base 98ac861e. Schema/lock/workspace diffs empty. Known non-failing Starlette/httpx and anyio deprecations, Vite chunk/plugin/route advisories preserved in transcripts. Satellite bundle test skipped because unconfigured baseline; final production build will set approved EOX configuration and require that test to run. Product boundary confirmed; M0 complete. Baseline browser runtimes/ports available.

M1 complete: m1-full-02 exited 0 (384 tests); 50 m analytic, zero, validation/transform and non-persistence checks pass. Only OpenAPI changed among five schema outputs. Ruling: non-persistence uses stored bytes rather than GET response because existing GET recalculates Phase 3 timestamps; no product change to that established behavior.

M2 complete: focused frontend 15/15, BL-016 backend 66/66, typecheck/lint exit 0. Preview RED missing function then GREEN; 25/50/75 m bounds and Phase 3 byte preservation pass. Geometry engine unchanged. New preview source below raster; raw FOV/overlap sources removed from map; stored metrics retained.

M3 complete: historical pin / missing pin / compatibility tests 3/3; typecheck/lint exit 0. Explicit override IDs require their own revision; null IDs inherit template according to existing assignment semantics. Cards expose pinned name/ID/revision, focal/FOV/resolution without mutation.

M4 implemented: workflow RED to GREEN 8/8; typecheck/lint/build exit 0; configured Satellite bundle assertion runs and passes. Full frontend verification recorded in m4-frontend. Ruling: explicit map remount key advances only on New/Import/Open, so reopening the same project ID also clears measurements while ordinary saves/edits retain session state. No persisted schema field added. Request cancellation and shared map guard exercised in unit tests; actual browser pending.

## Final implementation checkpoint
Product commit `fb1c522f2f14e2eebfa638f74af3cbde74920b1e`; all final4 deterministic checks PASS (387 backend/126 frontend), current production-browser checks PASS. Source/boundary evidence and recovery limitations are in the verification summary. M0–M5 implementation work achieved; clean readiness verifier PASS and QA handoff recorded; durable objective achieved, service closure following final clean recheck. Readiness goal status ACHIEVED describes the implemented objective, not an assertion that the final clean check already ran. No merge/push/seal or independent QA performed.

The preflight active/pending bullets above are historical startup observations; the M0 result supersedes them. Exact final paths: `harness/verify/2026-10-04-camera-range-lens-distance-summary.md`, `harness/verify/2026-10-04-camera-range-lens-distance-qa-handoff.md`, `harness/verify/2026-10-04-camera-range-lens-distance-readiness.json`.

Clean readiness exited0 on clean evidence commit0790f925; transcript `harness/logs/2026-10-04-camera-ux/readiness-clean-01.txt`. Six milestones/nine implementation criteria PASS. Independent QA/master pending; seal absent.

Durable goal service status COMPLETE, confirmed using update_goal after clean readiness PASS at892b26c and QA handoff. Product fb1c522f; operational closure only. No QA/master PASS claimed. Final clean transcript `harness/logs/2026-10-04-camera-ux/readiness-clean-final.txt`.
