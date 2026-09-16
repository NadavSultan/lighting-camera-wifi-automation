# Scoped master decision — post-roadmap Stage 2

Date: 2026-09-16

Decision: **PASS**

This is an item-based scoped master decision for Stage 2 items **BL-012 / WA-05**, **BL-017 / WA-10**, and **BL-018 / WA-11** only. It is not a phase seal, does not create Phase 8, does not authorize merge to `main`, and does not by itself authorize Stage 3 implementation.

## Identity reviewed

| Field | Value |
|---|---|
| Branch | `codex/bl-006-ies-associations` |
| Product implementation | `eb3a606253d794bf8ef685eb69d6c885368823ea` |
| Base | `2f0f4a9c42a3a7bdbb51971591aaced5c57a8d38` |
| Reviewed checkout | `a0cf9ceae6f5097a12a858592b2ec249d988587c` (documentation-only descendant) |
| Independent QA | PASS — `harness/verify/2026-09-08-stage2-bl-012-017-018-independent-qa-review.md` |

Both the product implementation and base are ancestors of the reviewed checkout. The product diff changes only the authorized frontend presentation, helper, test, plan, and harness paths. It does not change backend engines, schemas, catalogs, lockfiles, or `Input/`.

## Verdict

Stage 2 **passes the scoped master gate**.

- BL-012 passes: the lighting result card uses the correct MapLibre/container coordinate chain, opens beside the finish vertex, clamps inside the map, follows pan/zoom and panel geometry changes, supports drag and exact Reset, and does not persist its session position in project JSON.
- BL-017 passes: exact zero, unavailable values, tiny positive lux, and ordinary lux values use the approved display policy without changing stored values or deriving uniformity ratios from formatted strings.
- BL-018 passes: the four-discipline left-panel switcher defaults to Lighting, preserves active drafts, keeps CAP prerequisites available, keeps Report Package on the toolbar, and avoids horizontal overflow at the tested viewports.

No Critical, Major, or Minor product defect remains open. `S2-QA-01` is closed. `S2-QA-02` is informational documentation whitespace only; the later documentation-only descendant already removes it.

## Master verification

Fresh master checks on 2026-09-16:

| Check | Result |
|---|---|
| Implementation/base ancestry | PASS; both ancestor checks exited 0 |
| Authorized file boundary | PASS; no backend/schema/catalog/lockfile/`Input/` changes |
| `corepack pnpm run typecheck` | PASS |
| `corepack pnpm run lint` | PASS |
| `corepack pnpm run test` | PASS — 78 passed, 0 failed |
| `corepack pnpm run build` | PASS; existing chunk-size and route-classification advisories only |
| `scripts/validate_engineering_data.py` | PASS; seven catalogs and supplied-source hashes valid |
| Protected source and implementation-path checks | PASS; empty diffs |
| Miracle Mile KML SHA-256 | PASS — `2f89f9f2be306c18221c643c98d5c1a9abdb6449aab8a77ea4b76b3694e8e328` |

Master inspected the independent live JSON and screenshot set rather than repeating the same browser run. The evidence contains five anchor positions, zero harness errors, pan/zoom, collapse/restore, drag, Reset, session-only JSON verification, 1920/1024 overflow measurements, CAP prerequisite visibility, and seven screenshots.

Backend pytest and schema generation were not rerun because the reviewed product diff contains no backend or schema changes. Engineering-data validation and protected-path checks passed.

## Evidence disposition and authorized commit

The following evidence/documentation changes may be committed as one bounded evidence-only commit on `codex/bl-006-ies-associations`:

- `harness/logs/2026-09-16-stage2-bl-012-017-018-independent-qa-execution.md`
- `harness/verify/2026-09-08-stage2-bl-012-017-018-independent-qa-review.md`
- `harness/verify/2026-09-16-stage2-bl-012-017-018-independent-qa-live.json`
- `harness/verify/run_stage2_independent_qa_live.py`
- `docs/post-roadmap-stage2-scoped-master-decision-2026-09-16.md`
- Stage 2 status-only updates in `GOALS.md`, `PLANS.md`, `OPERATIONS.md`, `docs/current-status.md`, and `docs/post-roadmap-backlog.md`

Do not commit `.superpowers/`, `harness/tmp/` screenshots, caches, build output, runtime projects, uploads, generated exports, virtual environments, or `node_modules`.

## Gate decision

| Question | Answer |
|---|---|
| Stage 2 item set accepted | YES |
| Independent QA | PASS |
| Scoped master gate | PASS |
| Evidence-only commit authorized | YES, bounded list above |
| Merge to `main` authorized | NO |
| Push authorized | NO |
| Stage 3 implementation authorized | NO — no controlling Stage 3 contract exists |
| Phase 8 or harness seal authorized | NO |

## Exact next action

Create the bounded evidence-only commit and record its SHA. Then prepare a dedicated Stage 3 contract that settles the exact item set, UI behavior, dependencies, file boundary, acceptance criteria, and verification. Stage 3 implementation may begin only after that contract receives explicit authorization.
