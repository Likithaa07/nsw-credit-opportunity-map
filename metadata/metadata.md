# Metadata record: NSW Biodiversity Credit Opportunity Map

This record follows the core elements of the **ANZLIC Metadata Profile v1.1** (AS/NZS ISO 19115).
It describes the main output layer, `subregion_ranking.csv`, which joins to `ibra_nsw.gpkg`, and the
supporting tables.

## Identification

| Element | Value |
|---|---|
| **Title** | NSW Biodiversity Credit Opportunity Map: areas for further investigation |
| **Alternative title** | Remnant vegetation of six under-supplied ecosystem credit types by IBRA subregion |
| **Abstract** | Remaining mapped extent, protected extent and an opportunity score for six Plant Community Types (PCTs) that have zero credits available on the NSW Biodiversity Offsets Scheme (BOS) credit supply register but continue to be retired. Values are summarised by IBRA v7.1 subregion and ranked to show regions worth investigating for new Biodiversity Stewardship Agreements. |
| **Purpose** | Portfolio analysis to support targeting of new biodiversity credit supply. Not for site-scale decisions. |
| **Keywords** | biodiversity offsets; biodiversity credits; plant community type; remnant vegetation; IBRA; stewardship; NSW |
| **Topic category (ISO 19115)** | biota; environment; planningCadastre |
| **Status** | Completed |
| **Maintenance frequency** | As needed (re-run when the SVTM or BOS registers are updated) |

## Extent

| Element | Value |
|---|---|
| **Geographic extent** | New South Wales, Australia |
| **Bounding box (WGS84)** | West 141.0°, East 153.7°, South −37.5°, North −28.1° |
| **Temporal extent** | Vegetation as mapped in SVTM C2.0M2.2 (clearing to 2021); BOS demand from Nov 2019 to Oct 2026; CAPAD 2024 |
| **Reference date** | 11 October 2026 (creation) |

## Spatial representation

| Element | Value |
|---|---|
| **Spatial representation type** | Vector (polygons); tabular summaries |
| **Coordinate reference system** | GDA94 / NSW Lambert (EPSG:3308) |
| **Scale or resolution** | Derived from a 5 m raster vegetation map; suitable for regional analysis (1:25,000 at best) |
| **Spatial unit** | IBRA v7.1 subregion (132 subregions in NSW) |

## Data quality

| Element | Value |
|---|---|
| **Lineage** | 1. PCT IDs and % cleared from the BioNet Vegetation Classification (OData). 2. IBRA v7.1 subregions (DCCEEW) clipped to NSW; 5 border slivers removed. 3. Target PCT polygons (105,009) queried from the SVTM C2.0M2.2 ArcGIS service. 4. Vegetation intersected with subregions (106,176 pieces). 5. Protected area measured against CAPAD 2024 NSW (1,018 areas) using a spatial index, capped at piece area so overlapping reserves are not double counted. 6. Score = share of the PCT's unprotected remnant × credits retired per year (BOS registers) × (1 + BioNet % cleared). 7. Sensitivity tested under four weightings. |
| **Positional accuracy** | Inherited from the SVTM (line work accurate to about 5 m; regional scale). IBRA and CAPAD boundaries as supplied. |
| **Thematic accuracy** | SVTM PCT-level accuracy reported as 57–76% by region (2022 technical notes). No new figure is published for C2.0M2.2. |
| **Completeness** | PCT 1600 is excluded (retired in 2022, not in the SVTM). PCT 1604 maps to only 5 ha. Remnants under 10 ha per subregion are excluded from scoring. |
| **Logical consistency** | Mapped totals match the SVTM service statistics exactly for all six PCTs. Ranking re-runs reproduce identical results. |
| **Known issues** | Mapped pre-clearing (1750) extents disagree with BioNet % cleared, so BioNet figures are used for threat (see `extent_check.csv`). |

## Distribution and constraints

| Element | Value |
|---|---|
| **Format** | CSV, GeoPackage, PNG maps |
| **Online resource** | github.com/Likithaa07 (repository: nsw-credit-opportunity-map) |
| **Licence** | Derived data released under CC BY 4.0. Source data © State of NSW (DCCEEW) and Commonwealth of Australia (DCCEEW), CC BY. |
| **Use limitation** | Areas for further investigation only. Not a substitute for a Biodiversity Assessment Method site survey. |
| **Security constraints** | No sensitive species locations are included; only counts by subregion (BioNet Sensitive Species Data Policy). |

## Metadata about the metadata

| Element | Value |
|---|---|
| **Metadata standard** | ANZLIC Metadata Profile v1.1 (AS/NZS ISO 19115:2005) |
| **Metadata date** | 11 October 2026 |
| **Point of contact** | Likitha Vankadoth (github.com/Likithaa07) |
| **Language and character set** | English; UTF-8 |

## Source datasets

| Dataset | Custodian | Version | Licence |
|---|---|---|---|
| NSW State Vegetation Type Map (extant and pre-clearing) | NSW DCCEEW | C2.0M2.2 (Dec 2025) | CC BY |
| BioNet Vegetation Classification | NSW DCCEEW | C2.0 | CC BY 4.0 |
| BioNet Species Sightings (Atlas of NSW Wildlife) | NSW DCCEEW | Accessed 11 Oct 2026 | BioNet terms |
| IBRA v7.1 subregions | Australian Government DCCEEW | v7.1 (Sept 2025) | CC BY 4.0 |
| CAPAD 2024 terrestrial | Australian Government DCCEEW | 2024 | CC BY 4.0 |
| BOS credit supply and transactions registers | NSW DCCEEW | Extracted 5 Oct 2026 | CC BY 4.0 |
| Natural Earth admin-1 states (NSW outline for clipping) | Natural Earth | 10 m | Public domain |
