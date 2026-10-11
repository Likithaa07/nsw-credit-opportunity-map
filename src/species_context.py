"""Count threatened species records in the top subregions (BioNet). Counts only, no locations."""
# STEP 1: Imports
import pandas as pd
import requests

from config import BIONET, PROCESSED

THREAT = ("(stateConservation eq 'Vulnerable' or stateConservation eq 'Endangered' "
          "or stateConservation eq 'Critically Endangered')")


# STEP 2: Page through all threatened records in one subregion
def threatened_records(region, subregion):
    url = BIONET + "SpeciesSightings_CoreData"
    params = {"$filter": f"IBRASubregion eq '{region} - {subregion}' and {THREAT}",
              "$select": "scientificName,stateConservation,sensitivityClass"}
    recs = []
    while url:
        j = requests.get(url, params=params, timeout=300).json()
        recs += j.get("value", [])
        url, params = j.get("@odata.nextLink"), None
    return pd.DataFrame(recs)


# STEP 3: Summarise the top 5 subregions and save (no coordinates are kept)
if __name__ == "__main__":
    rank = pd.read_csv(PROCESSED / "subregion_ranking.csv").head(5)
    out = []
    for _, row in rank.iterrows():
        d = threatened_records(row["REG_NAME_7"], row["SUB_NAME_7"])
        out.append({"rank": row["rank"], "subregion": row["SUB_NAME_7"],
                    "threatened_records": len(d),
                    "threatened_species": d["scientificName"].nunique() if len(d) else 0,
                    "sensitive_records": int((d["sensitivityClass"] != "Not Sensitive").sum()) if len(d) else 0})
        print(row["SUB_NAME_7"], "done")
    species = pd.DataFrame(out)
    species.to_csv(PROCESSED / "threatened_species_top5.csv", index=False)
    print(species.to_string(index=False))
