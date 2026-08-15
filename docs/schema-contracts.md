# Engineering data schema contracts

Review date: 2026-08-15 corrective addendum

Contract version: `1.0.0`

Review decision: **APPROVED AND FROZEN FOR PHASE 2 INTEGRATION**

This approval covers data-contract structure and semantics only. It does not authorize Phase 2 implementation and does not convert unknown engineering inputs into verified specifications.

## Approved contracts

| Contract | Authoritative data file | Purpose |
|---|---|---|
| `schemas/fixture-types.schema.json` | `data/fixtures/fixture-types.json` | LITE/WIFI/SMART capabilities and CAP-participation state. |
| `schemas/camera-catalog.schema.json` | `data/cameras/camera-catalog.json` | Shared camera/sensor fields, lens/FOV configurations, and SMART-fixture integration inputs. |
| `schemas/luminaire-catalog.schema.json` | `data/luminaires/luminaire-catalog.json` | Luminaire identity, product attributes, applicability, and IES associations. |
| `schemas/ies-inventory.schema.json` | `data/luminaires/ies-inventory.json` | Parsed LM-63 metadata, hashes, dimensions, warnings/errors, and luminaire links. |
| `schemas/cap-constraints.schema.json` | `data/network/cap-constraints.json` | Status-separated JNET1/CAP specifications, requirements, assumptions, derived values, and missing inputs. |
| `schemas/wifi-defaults.schema.json` | `data/network/wifi-defaults.json` | Conceptual Wi-Fi circle defaults, applicability, exclusions, and disclaimer. |
| `schemas/calculation-area-types.schema.json` | `data/standards/calculation-area-types.json` | Area types, grid defaults, statistics, and nullable approved targets. |

The existing Phase 1 application contracts remain `schemas/project.schema.json` and `schemas/openapi.json`; this review does not change them.

## Approved Phase 2 operational contracts

These contracts are separate from and do not modify the seven frozen engineering catalogs above. Their original pre-implementation repository provenance was missing (IR-11). The user retrospectively ratified the corrective contract scope on 2026-08-15; see `docs/phase-2-contract-ratification.md` and `docs/decision-log.md`. This does not backdate or erase the QA finding.

| Contract | Seed data | Purpose |
|---|---|---|
| `schemas/fixture-model-catalog.schema.json` | `data/phase2/fixture-model-catalog.json` | Six family-plus-variant fixture models, capabilities, IES selection, immutable complete-model history, and immutable mounting-template revisions. |
| `schemas/ies-library.schema.json` | `data/phase2/ies-library.json` | Immutable original IES uploads, checksums, optional parsed metadata, warnings/errors, validation state, and explicit many-to-many fixture associations. |
| `schemas/camera-equipment-catalog.schema.json` | `data/phase2/camera-equipment-catalog.json` | Operational camera/lens CRUD, immutable complete-record histories, reciprocal compatibility, active state, and revisions seeded from the approved reference catalog. |

The Phase 3 application project contract is `2.2.0`. Its migration accepts Phase 1 `1.0.0`, initial Phase 2 `2.0.0`, and corrective Phase 2 `2.1.0` projects, preserves data and coordinates exactly, retains legacy fixture classifications and orientation overrides, and never guesses Phoenix 1 versus Solitaire. The fixture-model operational contract advances additively to `1.2.0` with an immutable fixed-zero-origin mounting-template contract; camera-equipment and IES contracts remain `1.1.0`. Existing projects remain pinned and adopt template revision 2 only explicitly.

All generated application and Phase 2 schema documents declare JSON Schema Draft 2020-12 explicitly. Corrective additions use minor-version migrations; no Phase 1 engineering catalog schema or data version changed.

## Finalized contract decisions

- All engineering catalog schemas use JSON Schema Draft 2020-12 and version `1.0.0`.
- Identifiers are stable strings and unique within their catalog collection.
- Every engineering value uses the traceability tuple `value`, `unit`, `status`, `source`, `confidence`, and `notes`.
- Status is restricted to `manufacturer_specification`, `company_provided_requirement`, `engineering_assumption`, `derived_value`, or `unknown`.
- A null engineering value means unresolved information and must use `status: unknown`; non-null values cannot use `unknown`.
- Repository source paths are relative to the repository root and must exist when non-null. Session-provided requirements may use a null file with an explicit session section.
- Approved units are centrally enforced by `scripts/validate_engineering_data.py`.
- Catalog IDs and cross-catalog IES/luminaire/camera references are validation-enforced.
- The IES inventory is authoritative for parsed photometric header values; duplicated luminaire wattage records carry an explicit authoritative reference.
- Source files under `Input/` remain immutable and hash-locked by validation.
- JL-LN037 is finalized at 87 degrees horizontal by 68 degrees vertical, matching the workbook and the user's 2026-08-14 decision.
- Unknown engineering inputs remain allowed and explicit. They block only the dependent feature/calculation, not schema consumption.

## Versioning policy

- Additive optional fields that preserve existing meaning require a reviewed minor-version change.
- Removing or renaming fields, changing units/status semantics, tightening an accepted value domain incompatibly, or changing identifier/reference meaning requires a major-version change and migration plan.
- Editorial documentation changes and additional catalog records that already conform to the contract do not change the schema version.
- Generated application contracts remain governed separately by the Pydantic/OpenAPI regeneration policy in `docs/data-model.md`.

## Validation and approval evidence

Approval requires all seven catalogs to validate against their schemas plus domain checks for identifiers, traceability, units, source existence, camera bounds and the JL-LN037 decision, fixture consistency, IES reparsing and hashes, reciprocal luminaire links, CAP missing-value handling, calculation-area invariants, and immutable supplied-source hashes.

Latest approval run on 2026-08-14:

- Engineering data validator: passed all seven catalog/schema pairs and domain/source-integrity checks.
- Backend: 23 passed; one existing non-failing Starlette/httpx deprecation warning.
- Frontend rendered-output tests: 2 passed, 0 failed.
- TypeScript: passed with zero errors.
- ESLint: passed with zero errors or warnings.
- Production build was not rerun because the catalogs are not consumed by the application build and no application/build contract changed. The last production build remains passing.

No unresolved schema-shape, naming, traceability, unit, nullability, identifier, cross-reference, authority, or versioning decision remains. Remaining entries in `docs/engineering-open-questions.md` are engineering-input questions for later phases, not contract decisions.
