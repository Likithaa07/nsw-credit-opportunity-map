"""Look up the target Plant Community Types (PCTs) in the BioNet Vegetation Classification."""
# STEP 1: Imports
from __future__ import annotations

import pandas as pd

from config import BIONET, PROCESSED, TARGETS, make_folders
from utils import DataValidationError, get_json, get_logger, require_columns

log = get_logger("get_targets")

COLUMNS = ["PCTID", "PCTName", "status", "classificationType", "vegetationFormation", "IBRA",
           "PCTPercentCleared", "preEuropeanExtent", "currentExtent", "stateTECProfileID"]


# STEP 2: Fetch one PCT definition
def fetch_pct(pct_id: int) -> dict:
    url = BIONET + "VegetationClassification_PCTDefinition"
    records = get_json(url, {"$filter": f"PCTID eq {pct_id}"}, timeout=60).get("value", [])
    if not records:
        raise DataValidationError(f"PCT {pct_id} was not found in the BioNet classification.")
    return records[0]


# STEP 3: Check the facts before they are used
def check_targets(facts: pd.DataFrame) -> pd.DataFrame:
    require_columns(facts, COLUMNS, "BioNet PCT definitions")
    facts = facts[COLUMNS]
    cleared = facts["PCTPercentCleared"]
    if cleared.isna().any() or not cleared.between(0, 1).all():
        raise DataValidationError("PCTPercentCleared should be a share between 0 and 1.")
    retired = facts[facts["status"] != "Approved"]
    if len(retired):
        log.warning("These PCTs are no longer current: %s", retired["PCTID"].tolist())
    return facts


# STEP 4: Fetch all targets, check them and save
def main() -> pd.DataFrame:
    make_folders()
    facts = check_targets(pd.DataFrame([fetch_pct(p) for p in TARGETS]))
    facts.to_csv(PROCESSED / "pct_targets.csv", index=False)
    log.info("PCT facts:\n%s", facts[["PCTID", "status", "PCTPercentCleared"]].to_string(index=False))
    return facts


if __name__ == "__main__":
    main()
