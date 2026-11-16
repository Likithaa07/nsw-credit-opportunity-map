"""Count threatened species records in the top subregions (BioNet). Counts only, no locations."""
# STEP 1: Imports
from __future__ import annotations

import pandas as pd

from config import BIONET, PROCESSED
from utils import get_json, get_logger, require_files

log = get_logger("species_context")

THREAT = ("(stateConservation eq 'Vulnerable' or stateConservation eq 'Endangered' "
          "or stateConservation eq 'Critically Endangered')")


# STEP 2: Page through all threatened records in one subregion
def threatened_records(region: str, subregion: str) -> pd.DataFrame:
    url = BIONET + "SpeciesSightings_CoreData"
    params = {"$filter": f"IBRASubregion eq '{region} - {subregion}' and {THREAT}",
              "$select": "scientificName,stateConservation,sensitivityClass"}
    recs = []
    while url:
        j = get_json(url, params, timeout=300)
        recs += j.get("value", [])
        url, params = j.get("@odata.nextLink"), None
    return pd.DataFrame(recs)


# STEP 3: Summarise the top 5 subregions and save (no coordinates are kept)
def main() -> pd.DataFrame:
    require_files(PROCESSED / "subregion_ranking.csv", hint="Run rank_subregions.py first.")
    rank = pd.read_csv(PROCESSED / "subregion_ranking.csv").head(5)
    out = []
    for _, row in rank.iterrows():
        d = threatened_records(row["REG_NAME_7"], row["SUB_NAME_7"])
        out.append({"rank": row["rank"], "subregion": row["SUB_NAME_7"],
                    "threatened_records": len(d),
                    "threatened_species": d["scientificName"].nunique() if len(d) else 0,
                    "sensitive_records": int((d["sensitivityClass"] != "Not Sensitive").sum()) if len(d) else 0})
        log.info("%s done", row["SUB_NAME_7"])
    species = pd.DataFrame(out)
    species.to_csv(PROCESSED / "threatened_species_top5.csv", index=False)
    log.info("Threatened species in the top 5:\n%s", species.to_string(index=False))
    return species


if __name__ == "__main__":
    main()
