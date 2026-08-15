# Data model

## Layer separation

| Layer | Phase 1 representation | Mutation policy |
|---|---|---|
| Original customer data | `source.poles` and immutable uploaded file | Never overwritten |
| User-edited data | `pole_edits`, keyed by stable source pole ID | Explicit edits only; source values remain available |
| Calculated data | `calculated_layers` | Empty in Phase 1 |
| Recommended data | `recommended_layers` | Empty in Phase 1; no pole or CAP generation |
| Exported data | Generated response plus export event | Never treated as source |

## Pole identity

The importer preserves a KML Placemark `id` when present. Otherwise it creates a deterministic ID from the source filename, folder path, placemark name, exact coordinate text, and document order. The original name, description, folder path, style URL, resolved KML colour, ExtendedData, raw coordinate text, and numeric coordinate are retained.

## User edits

`PoleEdit` retains Phase 1 fields and may contain a Phase 2 `fixture_configuration`. That configuration references a stable fixture model and pinned complete model/template revision, an explicitly associated IES file, fixture azimuth, capability-specific settings, and slot-keyed camera override deltas. Camera and lens assignments also pin their exact operational revisions. Location changes still require `location_edit_authorized=true`; the UI never exposes them.

Operational fixture, camera, and lens catalogs retain the current record plus immutable previous complete records keyed by `(id, revision)`. Historical lookup is used for assigned poles; current active state controls whether a new save/assignment is allowed. Lens `compatible_camera_model_ids` is the authoritative compatibility relation and the camera-side list is derived and reciprocity-validated.

## Phase 2 transition and lifecycle policy

- Choosing a different fixture model is an explicit replacement of the pole's capability-specific configuration baseline. The new current fixture/template revision is pinned, its explicit default IES (if any) is used, and incompatible prior Wi-Fi/camera overrides are not carried across models.
- Updating a catalog record never changes an assigned pole. The user must select **Explicitly adopt current catalog/template revision** or make a new equipment selection.
- Removing one camera-slot override deletes only that pole's delta and restores the pinned template values. Restoring the whole pole remains a separate action.
- API deactivation of equipment referenced by stored projects returns `409 Conflict`. If administrative filesystem changes nevertheless leave a project referencing inactive equipment, save/open validation returns a readable `422` error rather than mutating or crashing the project.
- Bulk patch values omitted or explicitly `null` mean unchanged. Bulk clearing is intentionally not implicit; a specific per-pole or override-reset action is required.

## Effective values

The effective pole is a view, not stored replacement data:

- name: edited name or source name
- fixture type: edited type or project default (`LITE`)
- height: edited height or project default (unset until supplied)
- active: edited state or `true`
- coordinate: authorized edited coordinate or exact source coordinate

## Project integrity metadata

Every project records source filename, SHA-256 hash, import timestamp, source CRS, selected projected CRS, software/schema version, mode, defaults, warnings, edits, assumptions, source catalog references, and calculation/recommendation placeholders.

The formal JSON Schema is `schemas/project.schema.json` and is generated from the Pydantic `Project` model. HTTP input/output and error-response contracts are published in `schemas/openapi.json`.

## Phase 1 invariants

- `mode` is `existing-poles`; `proposed-layout_authorized` remains false.
- A `PoleEdit` key must identify a source pole and must match its `pole_id`.
- Longitude and latitude edits must be supplied together and require `location_edit_authorized=true`.
- The Phase 1 UI never emits coordinate edits.
- Unknown fields are rejected by the backend models.
- Original uploaded bytes are SHA-256 identified and cannot be silently replaced at the same stored project path.

## Versioning and regeneration

The current project schema version is `2.1.0` and software version is `0.2.0`. Phase 1 JSON (`1.0.0`) and initial Phase 2 JSON (`2.0.0`) migrate without family inference: coordinates and edits are preserved, legacy `fixture_configuration` content remains explicit, and missing camera/lens pins are resolved to the current corrective-baseline revision on open/save. Regenerate checked-in contracts from the backend directory with:

```powershell
..\.venv\Scripts\python.exe .\scripts\export_schema.py
```

Any future schema change requires an explicit migration/compatibility decision before the version is changed.
