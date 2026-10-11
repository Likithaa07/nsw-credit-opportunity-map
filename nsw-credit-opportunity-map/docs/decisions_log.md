# Decisions log

Each decision records what was decided, why, and its effect on the results.

| # | Decision | Why | Effect |
|---:|---|---|---|
| 1 | Dropped **PCT 1600** from the target list | Retired in the 2022 eastern NSW revision; no confirmed replacement; not in the SVTM | 6 target PCTs instead of 7 (1600 was ranked last of the seven) |
| 2 | Used **BioNet % cleared**, not the mapped 1750 extent, for threat | The pre-clearing map shows almost no clearing for most targets (e.g. 94% of PCT 290 left vs 67% cleared in BioNet) | Threat weighting follows the official BAM figures (see `extent_check.csv`) |
| 3 | Reviewed the **Biodiversity Values Map** but did not score it | It marks land where the BOS applies to development, not land suited to supply | No effect on the ranking |
| 4 | Queried the **SVTM map service** instead of downloading the 12.5 GB package | The SEED download is behind bot protection; the service gives the same polygons for just the target PCTs | Totals match the service statistics exactly |
| 5 | Measured protection with a **spatial index**, not a dissolve | The dissolve approach ran for 30+ minutes; the indexed approach takes seconds | Overlapping reserves are capped at the piece area, so nothing is double counted |
| 6 | Excluded remnants **under 10 ha** per subregion from scoring | Removes slivers from boundary cutting | PCT 1604 (5 ha) is not scored |
| 7 | Kept BioNet species counts as **context only** | Record counts reflect survey effort (the coast is surveyed far more) | Not part of the score |
| 8 | Reported species as **counts by subregion only** | BioNet Sensitive Species Data Policy | No coordinates are published |
