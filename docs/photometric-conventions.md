# Photometric conventions

## Source inventory boundary

The four supplied files are LM-63-2002 photometric files with `TILT=NONE`, Type C photometry, metre dimension units, 73 vertical angles from 0 to 180 degrees, and 145 horizontal angles from 0 to 360 degrees. Each contains the expected 10,585 candela values. This session inventories metadata only; it does not calculate illuminance.

`data/luminaires/ies-inventory.json` is authoritative for parsed IES header values. The luminaire catalog may repeat a value only when it includes an explicit authoritative reference back to the inventory.

## LM-63 coordinate concepts

- Type C photometry is the normal orientation for luminaires mounted with a vertical nadir axis. Vertical angles are gamma angles measured in a C-plane. For the supplied files, the array spans 0 through 180 degrees.
- Horizontal angles select C-planes around the photometric vertical axis. The supplied files contain the full 0 through 360 degree set; therefore no bilateral, quadrantal, or rotational symmetry reduction is assumed.
- Type B photometry uses a horizontal reference axis and rotating planes that are commonly relevant to floodlights. It must not be interpreted with Type C axes.
- Type A photometry uses an axis aligned with the principal light direction and is generally associated with vehicle or signal-type distributions. It must not be interpreted with Type B or C axes.

These descriptions define parser/orientation categories only. The exact relationship between the luminaire housing, bracket, roadway direction, IES C0 plane, and application azimuth still requires manufacturer confirmation and AGi32 comparison.

## Project azimuth and tilt proposal

No approved luminaire azimuth zero exists yet. Proposed convention for later validation:

1. Define a luminaire-local right-handed frame fixed to the housing.
2. Map the IES Type C axes into that frame using a manufacturer-approved C0-plane reference.
3. Apply luminaire tilt about the approved local transverse axis.
4. Apply luminaire azimuth about the world/project vertical axis.
5. Translate to the pole mounting point after orientation is established.

This proposed intrinsic-tilt-then-world-azimuth order is an `engineering_assumption`, not an implemented rule. `TILT=NONE` means the IES file supplies no lamp-tilt correction table; it does not prove that the installed luminaire has zero physical tilt.

## File-specific issues

- PHOENIX1 100 W and 120 W filenames, internal luminaire identifiers, and input-watt fields align.
- Both Solitaire filenames and numeric headers indicate 50 W, while their internal `[LUMINAIRE]` values contain `60W`.
- The Solitaire D02 file contains width and length values of `-0.692 m`. The raw values are preserved and flagged; their LM-63 luminous-opening shape interpretation must be checked before calculation.
- All files use `-1` lumens per lamp, the absolute-photometry sentinel. It is not a luminous-flux value.

## AGi32 validation still required

Before a Phase 4 engine is accepted, compare representative points and complete calculation areas against AGi32 using the same IES file, mounting height, luminaire position, azimuth, tilt, maintenance factor, calculation plane, and grid. Approve the C0-plane/housing mapping, rotation signs and order, angle interpolation at seams, boundary behavior, absolute-photometry handling, negative-dimension interpretation, and numeric tolerances. Record both pointwise and summary-statistic tolerances before implementation.
