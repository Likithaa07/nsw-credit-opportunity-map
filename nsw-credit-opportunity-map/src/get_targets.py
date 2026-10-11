"""Look up the target Plant Community Types (PCTs) in the BioNet Vegetation Classification."""
# STEP 1: Imports
import pandas as pd
import requests

from config import BIONET, PROCESSED, TARGETS

COLUMNS = ["PCTID", "PCTName", "status", "classificationType", "vegetationFormation", "IBRA",
           "PCTPercentCleared", "preEuropeanExtent", "currentExtent", "stateTECProfileID"]


# STEP 2: Fetch one PCT definition
def fetch_pct(pct_id):
    url = BIONET + "VegetationClassification_PCTDefinition"
    r = requests.get(url, params={"$filter": f"PCTID eq {pct_id}"}, timeout=60)
    r.raise_for_status()
    return r.json()["value"][0]


# STEP 3: Fetch all targets, check they are current, and save
if __name__ == "__main__":
    facts = pd.DataFrame([fetch_pct(p) for p in TARGETS])[COLUMNS]
    retired = facts[facts["status"] != "Approved"]
    if len(retired):
        print("Warning: these PCTs are no longer current:", retired["PCTID"].tolist())
    facts.to_csv(PROCESSED / "pct_targets.csv", index=False)
    print(facts[["PCTID", "status", "PCTPercentCleared"]])
