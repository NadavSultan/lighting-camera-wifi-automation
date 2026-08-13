# CAP datasheet extraction

## Source and terminology

Source: `Input/CAP/CAP datasheet.pdf`, five pages, Juganu document `JL-DS-GC JNET1 GW _2308`, Rev 1.2.

The document calls the product a **JNET1 Gateway (Group Controller)**. It does not use the project term CAP. The mapping between CAP and this gateway is provisional and must be confirmed before Phase 6.

## Extraction policy

`data/network/cap-constraints.json` separates manufacturer specifications, company requirements, derived values, engineering assumptions, and missing information. Each constraint records a value, unit, source page/section/field, status, confidence, and notes.

Marketing maxima are preserved as statements but are not converted into design constraints. In particular:

- Up to 1,000 nodes is a manufacturer maximum, not a recommended loading target.
- Up to 10 km open air and 8 km dense urban are manufacturer claims without propagation or reliability conditions, not recommended operating distances.
- 64 hops is a protocol maximum, not an approved design-hop target.
- Node roaming is a stated capability, not a redundancy requirement.

## Successfully extracted topics

The catalog records the four ordering variants; gateway function; node and child maxima; source-routing-tree topology; two frequency ranges; data rates, aggregate goodput, transmitter output, receiver sensitivity, and hop delay; indoor Ethernet and outdoor cellular backhaul; indoor/outdoor power; mounting form; IP ratings; operating temperature and humidity; roaming capability; and the page 3 standards list.

## Missing recommendation inputs

The datasheet does not define LITE/WIFI/SMART node compatibility, recommended design distance, antenna gain/pattern/polarization/height, line-of-sight rules, fiber requirements, project band selection, redundancy/overlap rule, recommended hop limit, load/latency target, siting restrictions, or candidate-site power/backhaul availability. These remain null and `unknown`.

No CAP recommendation engine is implemented or authorized by this extraction.
