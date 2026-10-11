# NSW Biodiversity Credit Opportunity Map

**Where does native vegetation remain for the NSW biodiversity credit types that have run out?**

This project maps the remaining native vegetation for six ecosystem credit types that have **zero
credits available** on the NSW Biodiversity Offsets Scheme (BOS) register but are still in demand. It
then ranks IBRA subregions as **areas for further investigation** for new Biodiversity Stewardship
Agreements.

It follows on from my [BOS Credit Market Gap Analysis](https://github.com/Likithaa07/nsw-biodiversity-credit-gap)
(Project 1), which identified the under-supplied credit types.

**[Briefing note (PDF)](outputs/reports/Briefing_Note.pdf)** ·
**[Overview map](outputs/maps/01_statewide_overview.png)** ·
**[Metadata (ANZLIC)](outputs/reports/Metadata_ANZLIC.pdf)** ·
**[Decisions log](outputs/reports/Decisions_Log.pdf)**

---

## Key findings

| Rank | IBRA subregion | Why it stands out |
|---:|---|---|
| 1 | **Inland Slopes** (NSW South Western Slopes) | Holds almost all remaining PCT 290 and 99% of PCT 309, the two most-demanded types |
| 2 | **Macleay Hastings** (NSW North Coast) | Largest unprotected area of Northern Swamp Mahogany–Bottlebrush Swamp Forest (PCT 4047) |
| 3 | **Hill End** (South Eastern Highlands) | Largest area of PCT 3406, which is 89% cleared and almost entirely unprotected |
| 4 | **Orange** (South Eastern Highlands) | Second-largest area of PCT 3406 |
| 5 | **Karuah Manning** (NSW North Coast) | Second-largest area of PCT 4047 |

- **Southwest Ranges White Box Woodland (PCT 3406)** is the standout case:
  - 89% cleared.
  - Only **0.6%** of its 14,988 remaining hectares is protected.
  - 83% of it lies in Hill End and Orange.
- **Supply is concentrated.** The two most-demanded types (507 and 289 credits retired a year)
  survive almost only in Inland Slopes.
- **The ranking is robust.** The top five are unchanged under four different weightings.
- **Biodiversity value is high.** Each top subregion has 66–211 threatened species recorded in BioNet.

| PCT | Credit type | Remaining | Protected | % cleared | Retired/yr |
|---|---|---:|---:|---:|---:|
| 309 | Black Cypress Pine – Red Stringybark low open forest | 7,424 ha | 39% | 15% | 507 |
| 290 | Red Stringybark – Red Box – Long-leaved Box low open forest | 42,852 ha | 23% | 67% | 289 |
| 24 | Canegrass swamp tall grassland wetland | 790,654 ha | 10% | 20% | 155 |
| 4047 | Northern Swamp Mahogany–Bottlebrush Swamp Forest | 4,746 ha | 45% | 33% | 153 |
| 1604 | Narrow-leaved Ironbark – Grey Box – Spotted Gum woodland | 5 ha | 0% | 71% | 137 |
| 3406 | Southwest Ranges White Box Woodland | 14,988 ha | 0.6% | 89% | 127 |

## Map series

| Map | Shows |
|---|---|
| [01 Statewide overview](outputs/maps/01_statewide_overview.png) | Subregions shaded by opportunity score; top five labelled |
| [02 PCT 309](outputs/maps/02_pct_309.png) | Black Cypress Pine – Red Stringybark |
| [03 PCT 290](outputs/maps/03_pct_290.png) | Red Stringybark – Red Box – Long-leaved Box |
| [04 PCT 3406](outputs/maps/04_pct_3406.png) | Southwest Ranges White Box Woodland |
| [05 PCT 4047](outputs/maps/05_pct_4047.png) | Northern Swamp Mahogany–Bottlebrush Swamp Forest |

## Data

| Dataset | Custodian | Used for |
|---|---|---|
| [State Vegetation Type Map](https://datasets.seed.nsw.gov.au/dataset/nsw-state-vegetation-type-map) C2.0M2.2 (extant and 1750) | NSW DCCEEW | Where each target PCT is mapped (queried from the [ArcGIS service](https://mapprod3.environment.nsw.gov.au/arcgis/rest/services/VIS/SVTM_NSW_Extant_PCT/MapServer)) |
| [BioNet Vegetation Classification](https://www.environment.nsw.gov.au/topics/animals-and-plants/biodiversity/nsw-bionet/nsw-plant-community-type-classification) | NSW DCCEEW | PCT IDs, status (current or retired) and official % cleared |
| BioNet Species Sightings ([OData API](https://data.bionet.nsw.gov.au/biosvcapp/odata/)) | NSW DCCEEW | Threatened species counts per subregion (context only) |
| [IBRA v7.1 subregions](https://fed.dcceew.gov.au/datasets/erin::interim-biogeographic-regionalisation-for-australia-ibra-version-7-subregions) | Australian Government DCCEEW | Ranking units |
| [CAPAD 2024 terrestrial](https://data.gov.au/data/dataset/erin-collaborative-australian-protected-areas-database-capad-2024-terrestrial-) | Australian Government DCCEEW | Protected areas (1,018 in NSW) |
| BOS registers (from Project 1) | NSW DCCEEW | Target credit types and demand (credits retired per year) |

### How the data was sourced

- **The vegetation map.** The full SVTM download is 12.5 GB and sits behind bot protection that
  blocks scripted downloads. Instead, `download_layers.py` queries the official **ArcGIS map
  service**, 1,000 polygons at a time, for just the six target PCTs (105,009 polygons).
  - The totals match the service's own statistics exactly.
- **PCT IDs and % cleared** come straight from the **BioNet OData API**, so the pipeline always uses
  the current classification.

### Data files

| File | What it is |
|---|---|
| `data/processed/pct_targets.csv` | The six target PCTs: status, % cleared, BioNet extent |
| `data/processed/ibra_nsw.gpkg` | 132 NSW IBRA subregions (EPSG:3308) |
| `data/processed/remnant_by_subregion.csv` | Remaining, protected and unprotected hectares per PCT and subregion |
| `data/processed/subregion_ranking.csv` | **Main result.** Score and rank for each subregion |
| `data/processed/sensitivity_test.csv` | Top five under four weightings |
| `data/processed/threatened_species_top5.csv` | Threatened species counts for the top five subregions (no locations) |
| `data/processed/extent_check.csv` | Mapped extent vs BioNet figures (why BioNet % cleared is used) |

The large spatial files (`svtm_targets.gpkg`, `pieces.gpkg`, `capad.zip`) are **not committed**
because they are over GitHub's size limit. Running the pipeline re-creates them.

## Data source and licence

Source data © State of New South Wales (DCCEEW) and © Commonwealth of Australia (DCCEEW), licensed
under Creative Commons Attribution. The derived outputs in this repository are released under
[CC BY 4.0](https://creativecommons.org/licenses/by/4.0/). Species data is reported only as counts by
subregion, in line with the
[BioNet Sensitive Species Data Policy](https://www.environment.nsw.gov.au/topics/animals-and-plants/wildlife-management/wildlife-policies-and-guidelines/sensitive-species-data-policy-wildlife-management).

## Installation

Requirements: Python 3.10 or later.

```bash
git clone https://github.com/Likithaa07/nsw-credit-opportunity-map.git
cd nsw-credit-opportunity-map
pip install -r requirements.txt
```

It also runs in Google Colab, where geopandas is pre-installed.

## How to run it

```bash
cd src
python run_all.py
```

Or run the steps one at a time:

| Order | Script | What it does | Time |
|---:|---|---|---|
| 1 | `get_targets.py` | Looks up the target PCTs in BioNet and warns if any are retired | seconds |
| 2 | `download_layers.py` | Downloads IBRA, CAPAD and the target PCT polygons (skips files it already has) | 15–30 min |
| 3 | `overlay.py` | Splits vegetation by subregion and measures protected area | about 5 min |
| 4 | `rank_subregions.py` | Scores, ranks and runs the sensitivity test | seconds |
| 5 | `species_context.py` | Counts threatened species in the top five subregions | a few minutes |
| 6 | `make_maps.py` | Draws the five maps | about 1 min |

To change the target credit types, edit `DEMAND` in `src/config.py`.

## Method

1. **Targets.** I took the top-ranked zero-supply ecosystem credit types from Project 1 and looked up
   their PCT IDs in BioNet.
   - PCT 1600 had been retired in the 2022 eastern NSW revision, so it was dropped.
2. **Remaining extent.** The target PCT polygons from the SVTM were intersected with IBRA v7.1
   subregions in NSW Lambert (EPSG:3308).
3. **Protection.** Overlap with CAPAD 2024 protected areas was measured using a spatial index.
   - Each piece's protected area is capped at its own area, so overlapping reserves are never counted
     twice.
4. **Score.** For each PCT in each subregion:

   > share of that PCT's unprotected remnant × credits retired per year × (1 + BioNet % cleared)

   - The subregion score is the sum across PCTs. In plain words, it estimates how much unmet demand
     a subregion could help supply, weighted towards the most threatened types.
   - Remnants under 10 ha are ignored.
5. **Sensitivity.** The ranking was re-run without threat, without demand and with equal weights.
   The top five did not change.
6. **Context.** BioNet threatened species counts were added for the top five subregions. They are not
   part of the score, because record counts reflect survey effort.

The scoring follows the logic of systematic conservation planning (Margules & Pressey, 2000). It is
also close to the approach of the
[Biodiversity Conservation Investment Strategy 2018](https://www.environment.nsw.gov.au/publications/biodiversity-conservation-investment-strategy-2018),
which ranked IBRA subregions by % cleared, connectivity and threat.

## Limitations

- **Vegetation map accuracy.**
  - SVTM accuracy at PCT level is 57–76% by region (2022 technical notes). No figure is published for
    C2.0M2.2.
  - A field check in the Upper Hunter found only 17% of PCT labels were correct (Hunter, 2016).
  - The map is regional scale (1:25,000 at best). **Every area needs field validation.**
- **Map vs official figures.** The mapped pre-clearing (1750) extent shows very little clearing for
  most targets, which conflicts with BioNet. For example, PCT 290 shows 94% remaining on the map but is
  67% cleared in BioNet. BioNet's official figures were used (see `extent_check.csv`).
- **Reclassified vegetation.** PCT 1600 was retired in 2022, and PCT 1604 maps to only 5 ha, because
  the 2022 revision re-labelled most of it. There is no public old-to-new lookup.
- **Clearing data is dated.** The SVTM extent reflects clearing to 2021, and clearing has continued
  (66,498 ha in 2023, SLATS).
- **Remnant is not supply.**
  - Tenure, condition, landholder willingness and existing agreements are unknown.
  - The Biodiversity Conservation Trust (BCT) agreements layer is internal-use only, so existing
    stewardship sites could not be removed.
- **Demand is a lower bound.** Demand comes from retirements (Project 1), which miss unmet
  obligations.
- **Sensitive species.** Only subregion-level counts are used. Locations of sensitive species are
  generalised or withheld by BioNet.

## Repository structure

```
src/                config, get_targets, download_layers, overlay, rank_subregions,
                    species_context, make_maps, run_all
data/processed/     result tables and NSW subregions
outputs/maps/       the five maps (PNG, 200 dpi)
outputs/reports/    briefing note, metadata and decisions log (PDF)
docs/               briefing note, decisions log, stakeholder feedback (Markdown)
metadata/           ANZLIC-profile metadata record
```

## References

- Audit Office of NSW (2022). *Effectiveness of the Biodiversity Offsets Scheme*.
  https://www.audit.nsw.gov.au/our-work/reports/effectiveness-of-the-biodiversity-offsets-scheme
- IPART (2026). *Biodiversity Credits Market Monitoring: Annual Report 2024–25*.
- Henry, K., Mrdak, M., Keniry, J. & Leishman, M. (2023). *Independent Review of the Biodiversity
  Conservation Act 2016: Final Report*.
- DCCEEW (2025). *NSW State Vegetation Type Map technical notes, release C2.0M2.2*.
- DPIE (2020). *Biodiversity Assessment Method 2020*.
- OEH (2018). *Biodiversity Conservation Investment Strategy 2018*.
- Hunter, J.T. (2016). Validation of the Greater Hunter Native Vegetation Mapping. *Ecological
  Management & Restoration* 17(1), 40–46. https://doi.org/10.1111/emr.12195
- Margules, C.R. & Pressey, R.L. (2000). Systematic conservation planning. *Nature* 405, 243–253.
  https://doi.org/10.1038/35012251
- Kukkala, A.S. & Moilanen, A. (2013). Core concepts of spatial prioritisation in systematic
  conservation planning. *Biological Reviews* 88(2), 443–464.
- Maron, M. et al. (2012). Faustian bargains? Restoration realities in the context of biodiversity
  offset policies. *Biological Conservation* 155, 141–148. https://doi.org/10.1016/j.biocon.2012.06.003
- Bradshaw, C.J.A. (2012). Little left to lose: deforestation and forest degradation in Australia
  since European colonization. *Journal of Plant Ecology* 5(1), 109–120.
  https://doi.org/10.1093/jpe/rtr038
- ANZLIC (2007). *ANZLIC Metadata Profile v1.1*.

## Author

Likitha Vankadoth, Macquarie University · [GitHub](https://github.com/Likithaa07)
