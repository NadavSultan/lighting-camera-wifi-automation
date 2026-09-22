# BL-016 camera pixel-density — Independent QA handoff

Date: 2026-09-22

## Handoff identity and gate

- Exact implementation commit: `8a271bf12b070c5c9883f2b2942ad54c6ace4f77`.
- Base commit: `05257e87b4d6500146239f62f4ebafa4b2217b67`.
- Controlling specification: `docs/superpowers/specs/2026-09-22-bl-016-camera-pixel-density-engineering-design.md`.
- Controlling plan: `docs/superpowers/plans/2026-09-22-bl-016-camera-pixel-density.md`.
- Work record: `harness/phases/2026-09-22-bl-016-camera-pixel-density.md`.
- Execution log: `harness/logs/2026-09-22-bl-016-camera-pixel-density.md`.
- Verification summary: `harness/verify/2026-09-22-bl-016-camera-pixel-density-verification.md`.
- Live evidence: `harness/verify/2026-09-22-bl-016-camera-pixel-density-live.json`.
- Readiness manifest: `harness/verify/2026-09-22-bl-016-camera-pixel-density-readiness.json`.

This handoff records implementation readiness only. BL-016 is unaccepted. Independent QA and a separate scoped master PASS remain required. No seal exists or is authorized.

## Implementation verification to reproduce

Run on the exact implementation commit in a clean representative worktree:

```powershell
Push-Location backend
..\.venv\Scripts\python.exe -m pytest -q -p no:cacheprovider
Pop-Location
.\.venv\Scripts\python.exe scripts\validate_engineering_data.py
Push-Location backend
..\.venv\Scripts\python.exe -m scripts.export_schema
Pop-Location
Push-Location frontend
corepack pnpm install --frozen-lockfile
corepack pnpm run test
corepack pnpm run typecheck
corepack pnpm run lint
corepack pnpm run build
Pop-Location
git diff --check
git diff --exit-code -- Input
Get-FileHash Input\Miracle_Mile_Lighting_Poles.kml -Algorithm SHA256
.\.venv\Scripts\python.exe harness\verify\run_bl016_camera_pixel_density_live.py
git diff --exit-code -- schemas
```

Expected source SHA-256: `2F89F9F2BE306C18221C643C98D5C1A9ABDB6449AAB8A77EA4B76B3694E8E328`.

The implementation run passed the backend suite, 8-catalog validator, five-path schema export/freshness check, frozen frontend install, 107 frontend tests, typecheck, lint, production build, Input diff, exact source hash, and isolated live assertions. The live runner uses a fresh temporary data directory and ports 8070/3070; it records server listener identities and releases both listeners.

## Required independent scope

Use `harness/templates/qa-review-template.md` and independently dispose `BL016-01` through `BL016-20`. In addition to rerunning deterministic checks, perform the complete interactive production-browser workflow from plan Task 10, including:

- all three supplied lenses and an isolated invalid camera;
- standard and satellite backgrounds with identical Option A colour/opacity behavior;
- one-camera transparency, `2×`/`3×` overlap styles and labels;
- point inspection showing the stored winner and complete contributor list;
- significant edit, save/close/reopen, controlled failure, and successful recalculation;
- Phase 3, lighting, Wi-Fi, CAP, project JSON/KML, and Phase 7 report regression checks;
- zero browser console/page errors and exact source/coordinate preservation.

Implementation live evidence combines real production API workflow assertions, deterministic frontend rendering tests, and a production-shell Chrome screenshot. It does not substitute for the required independent interactive rendered walkthrough.

## Residual warnings

- Known Starlette/httpx and anyio deprecation warnings.
- Vinext large-chunk, plugin-timing, and unknown-route classification advisories.
- Windows Git CRLF conversion warnings; `git diff --check` passes.
- The implementation log preserves a recovered Chrome launch failure and a recovered orphaned test-listener attempt. The final live record has clean production server logs, all assertions true, Chrome exit `0`, and no remaining listeners.

## Non-goals and authority boundary

Do not merge, push, self-approve, start BL-019/BL-020 or any later backlog item, begin Phase 8, create a seal, invent analytics/detection thresholds, alter the supplied source, or change the existing-pole constraint. Report findings against the exact implementation commit; if implementation changes, invalidate affected results and retest.
