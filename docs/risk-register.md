# Risk register

Last reviewed: 2026-08-15

| ID | Risk / limitation | Current treatment | Blocks |
|---|---|---|---|
| R-01 | Missing authoritative fixture-to-IES/electrical BOM mapping | IES compatibility is explicit user assignment only; no family/model mapping is inferred. | Authoritative photometric/BOM automation. |
| R-02 | Unresolved Solitaire 50 W / 60 W conflict | Both supplied files and parsed headers remain preserved; no wattage choice is promoted to a fixture default. | Default Solitaire electrical/photometric selection. |
| R-03 | Missing physical camera XYZ offsets | Mounting templates store orientation slots only; no offsets are invented. | Phase 3 ground-FOV geometry. |
| R-04 | Missing default lens assignments for SMART slots | Lens remains explicitly unassigned until a user chooses a compatible model/revision. | Default camera FOV configuration. |
| R-05 | IES support limited to LM-63-1995/2002 Type C with `TILT=NONE` | Unsupported uploads are retained as inactive records with errors and cannot be associated/defaulted. | Other LM-63 forms and tilted photometry. |
| R-06 | Terrain/ground-plane assumption is not approved | No camera-ground or lighting calculation is implemented. | Phase 3 and later geometry/calculation. |
| R-07 | Initial Phase 2 contract approval lacked a pre-implementation repository artifact | Retrospective ratification and its limits are recorded in DL-001; independent QA must retest IR-11. | Final corrective acceptance until QA retest. |
| R-08 | Catalog record deactivation can invalidate assigned projects if storage is altered outside the API | API blocks referenced deactivation; configuration validation returns readable 4xx errors instead of server failures. | None for supported API workflow; direct filesystem edits remain administrative risk. |
