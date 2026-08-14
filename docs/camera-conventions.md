# Camera conventions

## Coordinate and angle convention

Camera downward angle is measured from the horizontal plane toward the ground:

- `0 deg_from_horizontal_down` means the optical axis is horizontal.
- `35 deg_from_horizontal_down` is the company-provided default.
- `90 deg_from_horizontal_down` means vertically downward.

Positive downward angles must not be converted to a conventional mathematical pitch without an explicit sign conversion. Fixture forward is absolute azimuth measured clockwise from true north. Camera absolute azimuth is the normalized sum of fixture azimuth and slot-relative azimuth. Phoenix 1 SMART uses -70/+70 degrees and Solitaire SMART uses -60/+60 degrees. Physical XYZ offsets remain undefined and must be approved before Phase 3 ground geometry.

## Catalog organization

`data/cameras/camera-catalog.json` is authoritative for shared camera/sensor data, lens configurations, and SMART-fixture integration defaults. Shared sensor and resolution values are stored once at camera-model level. Lens-specific focal length and FOV are stored under the lens record.

The catalog uses traceable values with one of the approved statuses: `manufacturer_specification`, `company_provided_requirement`, `engineering_assumption`, `derived_value`, or `unknown`. A null engineering value must be `unknown` and must explain the downstream dependency.

## Verified and unresolved values

The supplied workbook confirms three IMX477 lens rows, 4056 x 3040 pixels, 4:3 aspect ratio, and these real-angle pairs:

| Lens | Focal length | Horizontal FOV | Vertical FOV | State |
|---|---:|---:|---:|---|
| JL-LN039 | 6 mm | 52 deg | 40 deg | Workbook and brief agree |
| JL-LN042 | 3.9 mm | 69 deg | 54 deg | Workbook and brief agree |
| JL-LN037 | 3.56 mm | 87 deg | 68 deg | Workbook-backed value approved by the user on 2026-08-14 |

The earlier JL-LN037 87/90-degree discrepancy is resolved. The approved active value is 87 degrees horizontal by 68 degrees vertical, matching workbook cells `Sheet1!O11:Q11`. The superseded 90-degree candidate is not an active catalog value.

Camera manufacturer/enclosure model, physical mounting position/XYZ offsets, final lens assignments, and supported analytics remain unknown. Phoenix 1 SMART and Solitaire SMART each have two approved configurable mounting slots. The presence of a geometric FOV must never be treated as evidence of analytics-quality coverage.

## Future geometry prerequisites

Phase 3 must not start camera-footprint calculations until it has an approved lens selection per camera, pole/fixture mounting height, physical mounting offsets, and terrain assumption.
