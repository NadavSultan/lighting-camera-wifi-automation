# Independent QA review — 2026-09-16 — Stage 3 P2 usability

Verdict: **PASS**

## Scope, independence, and non-goals

- Exact implementation commit/worktree reviewed: dirty checkout on `codex/bl-006-ies-associations` at HEAD `fa1cbcadda93a0fb2ac0b31fdf1023a3ff5688d6` (ahead of origin by 2 unrelated commits). No implementation commit was minted. Product and harness changes were uncommitted. This review used the dirty worktree, not implementer claims.
- Controlling contract, phase record, and acceptance IDs: `docs/superpowers/plans/2026-09-16-stage3-p2-usability.md`; `docs/superpowers/specs/2026-09-16-stage3-p2-usability-design.md`; `docs/web-app-review-2026-09-08.md` WA-06 / WA-07 / WA-08; `harness/phases/2026-09-16-stage3-p2-usability.md`. Acceptance IDs: BL-013 / WA-06, BL-014 / WA-07, BL-015 / WA-08.
- Reviewer/session independence: this session did not implement the Stage 3 product work. Implementer verification `harness/verify/2026-09-16-stage3-p2-usability-verification.md` was treated as claims only. Every required check was re-run. Live identity was isolated production Vinext on `127.0.0.1:3057` plus isolated FastAPI `127.0.0.1:8057` with `LCWA_DATA_DIR` temp store. Leftover node on `:3042` was not used. Ports `:3000`, `:3012`, and `:8000` were not used as identity evidence.
- Review scope: frontend presentation for BL-013 / BL-014 / BL-015 plus harness QA records.
- Non-goals and excluded phases: no product fixes; no commit, merge, push, or seal; no BL-016 / BL-019 / BL-020; Phases 1–7 remain closed; no backend, schema, catalog, lockfile, or `Input/` changes.

Exact `git status --short --branch` at review close:

```
## codex/bl-006-ies-associations...origin/codex/bl-006-ies-associations [ahead 2]
 M GOALS.md
 M OPERATIONS.md
 M PLANS.md
 M docs/current-status.md
 M docs/post-roadmap-backlog.md
 M frontend/app/components/CapPlanningPanel.tsx
 M frontend/app/components/EngineeringWorkspace.tsx
 M frontend/app/globals.css
 M frontend/app/lib/lighting-card-position.d.mts
 M frontend/app/lib/lighting-card-position.mjs
 M frontend/tests/left-panel-layout.test.mjs
 M frontend/tests/lighting-areas.test.mjs
 M frontend/tests/lighting-card-position.test.mjs
 M frontend/tests/rendered-html.test.mjs
?? .superpowers/
?? docs/superpowers/plans/2026-09-16-stage3-p2-usability.md
?? frontend/app/lib/camera-projection-legend.d.mts
?? frontend/app/lib/camera-projection-legend.mjs
?? frontend/app/lib/cap-primary-action.d.mts
?? frontend/app/lib/cap-primary-action.mjs
?? frontend/app/lib/lighting-area-result-state.d.mts
?? frontend/app/lib/lighting-area-result-state.mjs
?? frontend/tests/camera-projection-legend.test.mjs
?? frontend/tests/cap-primary-action.test.mjs
?? frontend/tests/lighting-area-result-state.test.mjs
?? harness/logs/2026-09-16-stage3-p2-usability.md
?? harness/phases/2026-09-16-stage3-p2-usability.md
?? harness/verify/2026-09-16-stage3-p2-usability-independent-qa-live.json
?? harness/verify/2026-09-16-stage3-p2-usability-live.json
?? harness/verify/2026-09-16-stage3-p2-usability-verification.md
?? harness/verify/run_stage3_p2_independent_qa_live.py
?? harness/verify/run_stage3_p2_usability_live.py
```

User-owned `.superpowers/` was preserved. Product diff stayed inside the authorized frontend presentation boundary. `EngineeringMap.tsx` was not modified.

## QA milestones

| Milestone | Required evidence | Result |
|---|---|---|
| Repository/diff and authorization review | HEAD, branch, dirty product/harness diff, protected paths | **PASS** |
| Deterministic verification | typecheck, lint, 98 tests, production build, `git diff --check`, `Input/` | **PASS** |
| Acceptance-matrix review | independent disposition for BL-013, BL-014, BL-015 | **PASS** |
| Rendered/manual workflow | isolated production UI `:3057` and isolated FastAPI store `:8057` | **PASS** (stored CAP recommend live states not produced; see findings) |
| Source/prior-phase regression review | `Input/` hash, no backend/schema/catalog/lockfile edits, Stage 2 overflow/draft/collapse | **PASS** |

## Acceptance criteria

| Acceptance ID / criterion | Independent method | Evidence | Result |
|---|---|---|---|
| BL-013 / WA-06 — Show results, one card, independent session restore, draft/delete | source review of `showLightingResults` / session helpers; 98 frontend tests; isolated production Miracle Mile workflow | Live JSON `harness/verify/2026-09-16-stage3-p2-usability-independent-qa-live.json`. Two areas calculated (810 and 1124 points). Both **Show results** enabled only while current. One `.lighting-result-card`. A→B→A restored area 1 dragged session with delta **0 / 0**. Show results added no `/lighting/calculate/` requests. Create-then-cancel draft left two enabled Show results. Edit/save of area 2 deleted the stored result, disabled that row's Show results, showed **Not calculated**, and kept the open card as unavailable copy. Delete of that area closed its card (`cardCount` 0) and left area 1 Show results enabled; reopening area 1 restored css **869 / 538**. | **PASS** |
| BL-014 / WA-07 — result-first CAP pane and primary recommend action | source review of `CapPlanningPanel.tsx` / `cap-primary-action.mjs`; helper and panel tests; isolated CAP pane | Live not-calculated pane showed **No current CAP result**, primary **Calculate CAP recommendation** visible and disabled, 15 Review-input blockers, then closed Required CAP inputs / Candidates and locks / Advanced operations. Opening those sections exposed `#cap-field-operation_mode`, candidates, and Calculate / rank plus Validate. `capPrimaryAction` stays `recommend` and uses `capOperationEnabled(project, "recommend")`. `capResultSummary` tests keep not-calculated / current / current-with-unresolved / error / zero-selected distinct. Live stored recommend was **not** produced after three recoveries; those live states are **not** copied from implementer PASS. | **PASS** with findings `S3P2-QA-01` and `S3P2-QA-02` |
| BL-015 / WA-08 — Camera projection-boundary copy; no new map layer | legend helper/tests; `EngineeringMap.tsx` unchanged; isolated Camera pane | Camera pane rendered `.camera-projection-legend` titled **Projection boundary** with the approved flat-local-ground-plane paragraph, including the non-claim that the boundary is not detection range, recognition performance, pixel density, terrain/occlusion analysis, or proof of unobstructed visibility. No `.pixel-density-layer` / `.projection-boundary-layer`. | **PASS** |
| Stage 2 regressions | isolated 1920 and 1024 viewports; collapse; four-discipline draft | `panelOverflowX` false at **1920** and **1024**. Collapse rail hid the left switcher. Lighting→Camera→Wi-Fi→CAP→Lighting kept a one-vertex polygon draft. No `pageerror` / captured console errors. | **PASS** |

## Verification requirements

| Exact command/workflow | Commit/worktree | Exit/result | Notes |
|---|---|---|---|
| `git rev-parse HEAD` | dirty @ `fa1cbca` | `fa1cbcadda93a0fb2ac0b31fdf1023a3ff5688d6` | matches assigned identity |
| `corepack pnpm run typecheck` (frontend) | same | 0 | fresh this session |
| `corepack pnpm run lint` (frontend) | same | 0 | fresh this session |
| `corepack pnpm run test` (frontend) | same | 0, 98/98 | fresh this session |
| `corepack pnpm run build` (frontend, default API) | same | 0 | MapLibre chunk-size advisory; unclassified-route note |
| isolated rebuild `NEXT_PUBLIC_API_URL=http://127.0.0.1:8057` | same | 0 | `8057` present in `EngineeringWorkspace` client chunk |
| `git diff --check` | same | 0 | fresh |
| `git diff --exit-code -- Input` | same | 0 | source unchanged |
| Miracle Mile SHA-256 | same | match | file and imported project `2f89f9f2be306c18221c643c98d5c1a9abdb6449aab8a77ea4b76b3694e8e328` |
| Isolated FastAPI health | UI `:3057` / API `:8057` | `{status: ok, phase: 7, version: 0.7.0}` | `LCWA_DATA_DIR` temp store; 74 poles; `existing-poles` |
| Isolated Playwright matrix | same dirty tree | summary keys all true on final run | JSON cited above; leftover `:3042` unused |

Historical implementation evidence in `harness/verify/2026-09-16-stage3-p2-usability-verification.md` guided selection only and did not replace these checks.

## Findings

| ID | Severity | Requirement/evidence | Finding | Required correction |
|---|---|---|---|---|
| S3P2-QA-01 | Important | Plan Task 9: Review input still focuses existing field/section ids | With Required CAP inputs collapsed, the first **Review input** left `document.activeElement` as `#cap-planning-panel` and left the product-mapping `<details>` closed. Field ids still exist and are reachable after manually expanding Required CAP inputs. | In an authorized remediation session, `reviewCapInput` should open the owning `<details>` and focus the blocker target id. Not a product-engine defect. |
| S3P2-QA-02 | Info | Task 9 live current / current-with-unresolved / error / zero-selected after a stored recommend | Independent live did fill existing Required CAP inputs until only **Feasible CAP candidate** remained. Three recoveries (profile-then-add, add-then-profile, manual non-pole while `busy`) did not persist a candidate, so **Calculate CAP recommendation** stayed disabled. `cap_after_profile_text` still showed “No CAP candidates yet.” Those stored-result live states are **not independently disposed** and are **not** copied from implementer PASS. Helper/source tests still distinguish the four result states and zero-selected copy. | None required to close this QA. A later live session may retry a feasible candidate after `busy` clears. Do not treat implementer live recommend PASS as this identity. |
| S3P2-QA-03 | Info | Primary label wiring | The visible primary button text is the approved string `Calculate CAP recommendation` but is hardcoded rather than `{primary.label}`. Tests and helper currently agree. | Optional consistency cleanup in an authorized session. |

## Definition of Done

- [x] Complete implementation diff and file boundary reviewed.
- [x] Every mandatory acceptance item independently disposed as PASS or recorded as a blocking finding.
- [x] Required deterministic and rendered checks completed on the exact reviewed dirty worktree at `fa1cbca`.
- [x] Source preservation, prior-phase regressions, and later-phase exclusion verified.
- [x] Verdict is supported without relying on unverified claims.

## Recovery protocol

1. Preserve QA evidence and the exact reviewed HEAD `fa1cbcadda93a0fb2ac0b31fdf1023a3ff5688d6`.
2. Record failed/interrupted checks and whether implementation changed afterward. Implementation product files were not edited by this QA session.
3. If implementation changes, invalidate affected QA results and retest the new exact worktree.
4. Resume only from evidence that remains applicable.

Ordinary recoveries in this session: close the lighting card / use left-panel **Validate and save polygon** when the result card intercepts map Finish; wait for attached candidate controls; fall back to manual non-pole add (blocked by `busy`); continue Camera/regression checks after CAP recommend stayed ineligible.

## Allowed stopping conditions

- The reviewed commit changes or cannot be identified.
- Required evidence/runtime is unavailable and no truthful disposition is possible.
- A Critical/Major safety, authorization, source-preservation, or phase-boundary issue requires correction first.
- QA is complete and the supported PASS/FAIL verdict is recorded. QA never authorizes the next phase.

## Verdict and next gate

- Verdict: **PASS** (BL-013 PASS; BL-014 PASS with `S3P2-QA-01` / `S3P2-QA-02`; BL-015 PASS).
- Open findings: `S3P2-QA-01` Important (Review input vs collapsed details); `S3P2-QA-02` Info (stored CAP recommend live not produced); `S3P2-QA-03` Info.
- Master gate eligibility: **YES for scoped Stage 3 P2 master review only**. This QA PASS does not authorize merge, push, BL-016 / BL-019 / BL-020, Phase 8, or a seal.
- Exact next action: scoped Stage 3 P2 master review on this dirty checkout at HEAD `fa1cbca`, or an implementation commit if the user later asks to commit. Merge, push, and seals remain unauthorized.
