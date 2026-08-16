# Risk register

Last reviewed: 2026-08-15

| ID | Risk / limitation | Current treatment | Blocks |
|---|---|---|---|
| R-01 | Missing authoritative fixture-to-IES/electrical BOM mapping | IES compatibility is explicit user assignment only; no family/model mapping is inferred. | Authoritative photometric/BOM automation. |
| R-02 | Unresolved Solitaire 50 W / 60 W conflict | Both supplied files and parsed headers remain preserved; no wattage choice is promoted to a fixture default. | Default Solitaire electrical/photometric selection. |
| R-03 | Physical camera XYZ offset was previously unspecified | Resolved for Phase 3 MVP by approved immutable X=0 m, Y=0 m, Z=0 m optical-center offsets at the fixture origin; future non-zero geometry requires a new immutable template revision. | None for approved Phase 3 MVP. |
| R-04 | Missing default lens assignments for SMART slots | Lens remains explicitly unassigned until a user chooses a compatible model/revision. | Default camera FOV configuration. |
| R-05 | IES support limited to LM-63-1995/2002 Type C with `TILT=NONE` | Unsupported uploads are retained as inactive records with errors and cannot be associated/defaulted. | Other LM-63 forms and tilted photometry. |
| R-06 | Flat-ground Phase 3 omits terrain, slope, objects, and occlusion | Approved Phase 3 calculations explicitly use local Z=0 and label this limitation in every result; no terrain or obstacle inference is made. | Terrain-aware or visibility-qualified coverage claims. |
| R-07 | Initial Phase 2 contract approval lacked a pre-implementation repository artifact | Retrospective ratification and its limits remain recorded in DL-001; independent corrective QA closed IR-11 and the final NIR-01 retest granted unconditional Phase 2 acceptance. | None; retained as historical governance evidence. |
| R-08 | Catalog record deactivation can invalidate assigned projects if storage is altered outside the API | API blocks referenced deactivation; configuration validation returns readable 4xx errors instead of server failures. | None for supported API workflow; direct filesystem edits remain administrative risk. |
| R-09 | A closed flat-ground frustum footprint may not exist for shallow, horizontal, upward, non-finite, or numerically unstable boundary rays | Return no complete polygon and an explicit deterministic warning; never clip or fabricate geometry. | Footprint and downstream overlap/intersection for the affected camera. |
| R-10 | Geometric coverage and optional future pixel density can be mistaken for analytics performance | Results are labeled geometric only, carry model/revision provenance and assumptions, and define no recognition/LPR/analytics thresholds. | Analytics-quality or compliance claims. |
| R-11 | A malformed priority-area redraw could replace a previously valid ring | Rename and redraw are distinct; redraw starts empty, validates finite/distinct/simple/non-degenerate geometry before mutation, and preserves the prior polygon on failure or cancel. Invalid legacy records are quarantined losslessly. | None for supported corrective workflow. |
| R-12 | Camera configuration warnings could be missed when no pole is selected | Enabled-camera warnings are aggregated globally and shown at affected map poles; the Warnings layer controls the indicator. Disabled slots are excluded. | None for supported UI workflow. |
