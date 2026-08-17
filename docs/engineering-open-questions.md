# Engineering open questions

`Can continue` means repository/data preparation can continue without the answer; it does not authorize the dependent calculation or recommendation.

Phase 4 implementation decisions for C0 alignment, zero physical tilt, interpolation, grid anchoring, boundary tolerance, point limit, area-level maintenance factor, and synthetic validation were explicitly authorized on 2026-08-17 and are recorded in DL-011. Manufacturer confirmation and professional-reference comparison remain open acceptance work; they do not permit claims beyond the displayed simplified-model disclaimer.

## Camera

| Question | Why required | Dependent phase | Can continue? | Assumption risk | Recommended owner/source |
|---|---|---|---|---|---|
| What are the camera manufacturer, enclosure model, quantity per SMART fixture, and lens assignment rules? | Identifies deployable configurations and multiplicity. | Phases 2-3 | Catalog framework yes | Invalid BOM and missing/extra footprints. | Juganu product engineering/BOM. |
| What are mounting position, local axes, XYZ offsets, and azimuth zero? | Converts optical axes to project coordinates. | Phase 3 | No geometry | Systematic footprint displacement/rotation. | Mechanical drawing and installation guide. |
| Which analytics are supported and at what pixel-density/quality thresholds? | Separates geometric visibility from usable analytics. | Phases 3 and 7 | Geometry may continue if clearly separated | Unsupported performance claims. | Analytics product specification and acceptance criteria. |

## Luminaire

| Question | Why required | Dependent phase | Can continue? | Assumption risk | Recommended owner/source |
|---|---|---|---|---|---|
| Which orderable Solitaire model/optic corresponds to D01/D02, and can the internal `60W` identifier be manufacturer-confirmed? | Resolves the remaining product-identity conflict; Phase 4 already controls at the matching filename/numeric-input value of 50 W and preserves the `60W` warning. | Phases 4, 5, 7 | Simplified Phase 4 calculation yes; automatic default no | Wrong automatic BOM/optic selection. | Manufacturer luminaire datasheet and photometric report. |
| What are flux, CCT, recommended mounting heights, and LITE/WIFI/SMART compatibility for each model? | Completes selection and reporting fields. | Phases 2, 5, 7 | Framework yes | Invalid selection and misleading schedules. | Approved product datasheets/BOM. |
| What does optic code D01/D02 mean physically? | Links distribution to product variant. | Phases 2 and 5 | Parsing yes | Wrong optic assignment. | Manufacturer optical catalog. |

## IES

| Question | Why required | Dependent phase | Can continue? | Assumption risk | Recommended owner/source |
|---|---|---|---|---|---|
| Can the approved Phase 4 C0-to-fixture-azimuth convention be confirmed for each housing/bracket? | Validates the implemented simplified world orientation. | Phase 4 QA | Implemented with disclaimer; no professional equivalence claim | Rotated distributions and wrong uniformity. | Photometric lab drawing plus AGi32 reference model. |
| What do the D02 negative width/length values represent, and are they accepted by the target engine? | Affects luminous-opening/shape interpretation. | Phase 4 | Metadata yes | Parser incompatibility or incorrect near-field treatment. | LM-63 expert, photometric lab, and AGi32 comparison. |
| What professional-reference cases and tolerances will independently validate the approved interpolation, seam, boundary, and absolute-photometry rules? | Defines the future external comparison gate for the implemented reproducible engine. | Phase 4 QA | Synthetic implementation validation yes | Undetected divergence from a professional reference. | Lighting engineer and AGi32 validation cases. |
| What are the missing test report IDs? | Establishes photometric provenance. | Phases 2, 5, 7 | Yes with warning | Weak audit trail or obsolete data. | JUGANU photometric lab reports. |

## Wi-Fi

| Question | Why required | Dependent phase | Can continue? | Assumption risk | Recommended owner/source |
|---|---|---|---|---|---|
| What bands, antennas, mounting heights, EIRP, receiver thresholds, throughput, client density, and channel plan apply? | Required for any RF prediction. | Phase 5 | Conceptual circles only | False coverage/capacity claims. | RF engineer, radio datasheets, and site survey. |
| How should buildings, trees/foliage, terrain, materials, interference, and backhaul be modeled? | Determines attenuation and service feasibility. | Phase 5 | Conceptual circles only | Large coverage gaps hidden. | Site survey/GIS, RF design standard, network team. |
| Is 30 m retained as a planning-only default or replaced per project? | Controls conceptual visualization. | Phase 5 | Yes | Users may over-trust the circle. | Company engineering owner. |

## CAP

| Question | Why required | Dependent phase | Can continue? | Assumption risk | Recommended owner/source |
|---|---|---|---|---|---|
| Does project term CAP mean the supplied JNET1 Gateway/Group Controller? | Confirms product identity. | Phase 6 | Extraction yes | Engine targets wrong product. | Network system owner/Juganu. |
| Which LITE/WIFI/SMART fixtures are JNET1 nodes and count toward capacity? | Defines topology membership and load. | Phase 6 | No recommendations | Capacity and connectivity errors. | System architecture/BOM. |
| What recommended range, hop target, design load, latency, and interference margin apply? | Converts protocol maxima into design constraints. | Phase 6 | No recommendations | Brittle or non-performing topology. | Juganu network engineering/design guide. |
| What antenna/LOS rules, band, redundancy, backhaul, power, siting, and legal constraints apply at this site? | Determines feasible CAP candidates. | Phase 6 | No recommendations | Uninstallable, illegal, or single-point-failure design. | RF/network engineer, AHJ, utility and site survey. |

## KML/KMZ

| Question | Why required | Dependent phase | Can continue? | Assumption risk | Recommended owner/source |
|---|---|---|---|---|---|
| Where are the project boundary and classified road/sidewalk/parking polygons? | Defines coverage and lighting calculation extents. | Phases 4-5 | Catalog work yes | Statistics omit or include wrong areas. | Customer GIS/KML deliverable. |
| Are folder names allowed to drive fixture or luminaire assignments? | Current policy deliberately does not infer assignments. | Phase 2 | Yes with manual assignments | Silent misclassification. | Customer/engineering assignment schedule. |
| Are there additional representative KMZ files with overlays/resources? | Expands real-world importer acceptance coverage. | Phase 1 maintenance | Yes | Edge cases emerge later. | Customer GIS owner. |

## Calculation areas

| Question | Why required | Dependent phase | Can continue? | Assumption risk | Recommended owner/source |
|---|---|---|---|---|---|
| Which approved standard and project targets apply to each area type? | Supplies target illuminance/uniformity without invention. | Phase 4 | Grid framework yes | False compliance result. | Lighting engineer/client standard/AHJ. |
| Should a future professional-reference comparison use the approved projected-CRS-zero grid origin, `1e-7 m` boundary tolerance, exterior-ring-only scope, and explicit zero-point policy unchanged? | Aligns the implemented deterministic grid with an external comparison setup. | Phase 4 QA | Implemented with provenance | Different reference point sets and statistics. | Lighting engineer plus AGi32 reference setup. |
| Which approved maintenance factor should users enter per calculation area? | The engine applies the explicit area value but does not invent the project value. | Phase 4 | Calculation yes with explicit input | Systematic over/understatement from an incorrect user input. | Approved lighting design standard. |

## Reporting

| Question | Why required | Dependent phase | Can continue? | Assumption risk | Recommended owner/source |
|---|---|---|---|---|---|
| Which deliverables, units, precision, coordinate system, disclaimers, and approval signatures are required? | Defines auditable report outputs. | Phase 7 | Data work yes | Rework or noncompliant reports. | Client/project manager and QA. |
| How should unknown, assumed, derived, and conflicting values appear in schedules and maps? | Prevents unverified values appearing authoritative. | Phase 7 | Yes if status retained | Misleading engineering claims. | Engineering QA/reporting standard. |
| What source-file/page citation granularity is required in exports? | Preserves traceability outside JSON. | Phase 7 | Yes | Lost audit chain. | QA/document-control owner. |
