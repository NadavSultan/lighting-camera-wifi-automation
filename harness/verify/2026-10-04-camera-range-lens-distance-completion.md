# Camera range/lens/distance UX — implementation handoff
Date: 2026-10-04. Product commit `fb1c522f2f14e2eebfa638f74af3cbde74920b1e`.
Implemented the approved single distance-bounded preview/heatmap workflow, exact pinned camera/lens cards, and transient projected-metre measurement with exclusive map interaction and late-response safety. Raster lifecycle correction removes stale/empty caches during visibility and fingerprint transitions.

Verification summary: `harness/verify/2026-10-04-camera-range-lens-distance-summary.md`. Current deterministic results: 387 backend, 126 frontend, validator/schema/typecheck/lint/build PASS; configured Satellite build check runs. Current real 74-pole production browser evidence and independent projected measurement comparison PASS. Protected sources/catalogs/engines/dependencies preserved.

Readiness manifest: `harness/verify/2026-10-04-camera-range-lens-distance-readiness.json`. Clean verifier PASS at evidence commit0790f925; transcript `harness/logs/2026-10-04-camera-ux/readiness-clean-01.txt`. Final clean recheck follows this evidence checkpoint. The manifest's legacy phase value 16 is the existing BL-016 harness namespace, not a new numbered roadmap phase.

Independent QA handoff: `harness/verify/2026-10-04-camera-range-lens-distance-qa-handoff.md`. QA NOT REVIEWED; master PENDING; no seal. No merge or push. The prior accepted BL-016 decision remains historical authority for its own product commit; it does not accept this UX implementation.

All recoveries and limitations, including the legacy port-cleanup incident and concurrent-reopen observer limitation, remain in the execution log/summary. Main checkout and user-owned files preserved.
