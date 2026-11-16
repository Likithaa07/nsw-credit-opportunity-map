"""Score and rank IBRA subregions as areas for further investigation, and test the ranking."""
# STEP 1: Imports
from __future__ import annotations

from pathlib import Path

import pandas as pd

from config import DEMAND, PROCESSED
from utils import DataValidationError, get_logger, require_columns, require_files

log = get_logger("rank_subregions")

MIN_HA = 10  # ignore slivers smaller than this


# STEP 2: Load the remnant table and BioNet % cleared
def load(processed_dir: Path = PROCESSED) -> pd.DataFrame:
    processed_dir = Path(processed_dir)
    require_files(processed_dir / "remnant_by_subregion.csv", processed_dir / "pct_targets.csv",
                  hint="Run get_targets.py and overlay.py first.")
    by_sub = pd.read_csv(processed_dir / "remnant_by_subregion.csv")
    pct = pd.read_csv(processed_dir / "pct_targets.csv")
    require_columns(by_sub, ["PCTID", "REG_NAME_7", "SUB_NAME_7", "unprot_ha"],
                    "remnant_by_subregion")
    require_columns(pct, ["PCTID", "PCTPercentCleared"], "pct_targets")
    cleared = dict(zip(pct["PCTID"], pct["PCTPercentCleared"]))
    s = by_sub[by_sub["unprot_ha"] >= MIN_HA].copy()
    s["share"] = s["unprot_ha"] / s.groupby("PCTID")["unprot_ha"].transform("sum")
    s["demand"] = s["PCTID"].map(DEMAND)
    s["cleared"] = s["PCTID"].map(cleared)
    if s[["demand", "cleared"]].isna().any().any():
        raise DataValidationError("Some PCTs have no demand or % cleared figure. Check config.DEMAND.")
    return s


# STEP 3: Score = share of the PCT's unprotected remnant x demand x (1 + % cleared)
def score(s: pd.DataFrame) -> pd.DataFrame:
    s["score"] = s["share"] * s["demand"] * (1 + s["cleared"])
    rank = (s.groupby(["REG_NAME_7", "SUB_NAME_7"])
              .agg(score=("score", "sum"), unprot_ha=("unprot_ha", "sum"),
                   pcts=("PCTID", lambda x: ", ".join(map(str, sorted(x)))))
              .sort_values("score", ascending=False).reset_index())
    rank["rank"] = range(1, len(rank) + 1)
    rank["score"] = rank["score"].round(1)
    return rank


# STEP 4: Sensitivity test: does the top 5 change under other weightings?
def sensitivity(s: pd.DataFrame) -> pd.DataFrame:
    variants = {
        "main": s["share"] * s["demand"] * (1 + s["cleared"]),
        "no_threat": s["share"] * s["demand"],
        "no_demand": s["share"] * (1 + s["cleared"]),
        "equal": s["share"],
    }
    rows = []
    for name, values in variants.items():
        top = s.assign(v=values).groupby("SUB_NAME_7")["v"].sum().nlargest(5).index.tolist()
        rows.append({"weighting": name, **{f"rank_{i + 1}": t for i, t in enumerate(top)}})
    return pd.DataFrame(rows)


# STEP 5: Run and save
def main(processed_dir: Path = PROCESSED) -> pd.DataFrame:
    s = load(processed_dir)
    rank = score(s)
    rank.to_csv(Path(processed_dir) / "subregion_ranking.csv", index=False)
    log.info("Top 10 subregions:\n%s", rank.head(10).to_string(index=False))
    sens = sensitivity(s)
    sens.to_csv(Path(processed_dir) / "sensitivity_test.csv", index=False)
    log.info("Sensitivity test:\n%s", sens.to_string(index=False))
    return rank


if __name__ == "__main__":
    main()
