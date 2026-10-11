"""Score and rank IBRA subregions as areas for further investigation, and test the ranking."""
# STEP 1: Imports
import pandas as pd

from config import DEMAND, PROCESSED

MIN_HA = 10  # ignore slivers smaller than this


# STEP 2: Load the remnant table and BioNet % cleared
def load():
    by_sub = pd.read_csv(PROCESSED / "remnant_by_subregion.csv")
    pct = pd.read_csv(PROCESSED / "pct_targets.csv")
    cleared = dict(zip(pct["PCTID"], pct["PCTPercentCleared"]))
    s = by_sub[by_sub["unprot_ha"] >= MIN_HA].copy()
    s["share"] = s["unprot_ha"] / s.groupby("PCTID")["unprot_ha"].transform("sum")
    s["demand"] = s["PCTID"].map(DEMAND)
    s["cleared"] = s["PCTID"].map(cleared)
    return s


# STEP 3: Score = share of the PCT's unprotected remnant x demand x (1 + % cleared)
def score(s):
    s["score"] = s["share"] * s["demand"] * (1 + s["cleared"])
    rank = (s.groupby(["REG_NAME_7", "SUB_NAME_7"])
              .agg(score=("score", "sum"), unprot_ha=("unprot_ha", "sum"),
                   pcts=("PCTID", lambda x: ", ".join(map(str, sorted(x)))))
              .sort_values("score", ascending=False).reset_index())
    rank["rank"] = range(1, len(rank) + 1)
    rank["score"] = rank["score"].round(1)
    return rank


# STEP 4: Sensitivity test: does the top 5 change under other weightings?
def sensitivity(s):
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
if __name__ == "__main__":
    s = load()
    rank = score(s)
    rank.to_csv(PROCESSED / "subregion_ranking.csv", index=False)
    print(rank.head(10).to_string(index=False))
    sens = sensitivity(s)
    sens.to_csv(PROCESSED / "sensitivity_test.csv", index=False)
    print(sens.to_string(index=False))
