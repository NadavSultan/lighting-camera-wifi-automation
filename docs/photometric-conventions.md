# Photometric conventions

## Source inventory boundary

The four supplied files are LM-63-2002 photometric files with `TILT=NONE`, Type C photometry, metre dimension units, 73 vertical angles from 0 to 180 degrees, and 145 horizontal angles from 0 to 360 degrees. Each contains the expected 10,585 candela values. Phase 4 parses the original immutable bytes again at calculation time and uses the exact angle arrays, candela values, and multiplier.

`data/luminaires/ies-inventory.json` is authoritative for parsed IES header values. The luminaire catalog may repeat a value only when it includes an explicit authoritative reference back to the inventory.

## LM-63 coordinate concepts

- Type C photometry is the normal orientation for luminaires mounted with a vertical nadir axis. Vertical angles are gamma angles measured in a C-plane. For the supplied files, the array spans 0 through 180 degrees.
- Horizontal angles select C-planes around the photometric vertical axis. The supplied files contain the full 0 through 360 degree set; therefore no bilateral, quadrantal, or rotational symmetry reduction is assumed.
- Type B photometry uses a horizontal reference axis and rotating planes that are commonly relevant to floodlights. It must not be interpreted with Type C axes.
- Type A photometry uses an axis aligned with the principal light direction and is generally associated with vehicle or signal-type distributions. It must not be interpreted with Type B or C axes.

These descriptions define parser/orientation categories only. The exact relationship between the luminaire housing, bracket, roadway direction, IES C0 plane, and application azimuth still requires manufacturer confirmation and AGi32 comparison.

## Phase 4 approved azimuth and tilt convention

IES C0 aligns with the user-selected fixture azimuth. Zero degrees is project/grid north and positive azimuth is clockwise. World points are translated relative to the unchanged source-pole origin and rotated into the luminaire-local frame by subtracting fixture azimuth. No physical luminaire tilt is applied. `TILT=NONE` means the IES file supplies no lamp-tilt correction table; zero installed tilt remains the explicitly approved MVP engineering assumption, not a fact inferred from the file.

Linear interpolation is applied first across vertical angles within each adjacent C-plane and then across C-planes. Accepted horizontal domains are one rotationally symmetric plane, complete 0-90 or 0-180 symmetry domains, and a complete 0-360 domain. For 0-360 data, duplicated C0/C360 candela rows must agree point-for-point within `1e-9` relative or `1e-9 cd` absolute tolerance; a discontinuous seam is rejected rather than averaged or overwritten. Full calculation precision is retained internally.

The calculation grid is anchored at projected CRS `(0,0)`, uses the requested spacing without adjustment with a minimum of `0.01 m`, accepts polygon boundary points within `1e-7 m`, orders points by increasing Y then X, and rejects results over 25,000 points.

## File-specific issues

- PHOENIX1 100 W and 120 W filenames, internal luminaire identifiers, and input-watt fields align.
- Both Solitaire filenames and numeric headers indicate 50 W, while their internal `[LUMINAIRE]` values contain `60W`.
- The Solitaire D02 file contains width and length values of `-0.692 m`. The raw values are preserved and flagged; their LM-63 luminous-opening shape interpretation must be checked before calculation.
- All files use `-1` lumens per lamp, the absolute-photometry sentinel. It is not a luminous-flux value.

## AGi32 validation still required

Before Phase 4 is approved, compare representative points and complete calculation areas against AGi32 or another professional reference tool using identical inputs. Until that separately authorized comparison exists, all results carry the explicit unvalidated-reference disclaimer and cannot support equivalence or compliance claims.
