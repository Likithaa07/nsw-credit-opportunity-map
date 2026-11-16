"""Tests for the subregion score. Re-runs the ranking from the committed tables and checks it
matches the published results exactly."""
# STEP 1: Imports
import pandas as pd
import pytest

from config import PROCESSED
from get_targets import check_targets
from rank_subregions import load, score, sensitivity


# STEP 2: The published ranking can be rebuilt exactly
def test_ranking_matches_published_results():
    rank = score(load())
    published = pd.read_csv(PROCESSED / "subregion_ranking.csv")
    pd.testing.assert_frame_equal(rank.reset_index(drop=True), published, check_dtype=False)


def test_sensitivity_matches_published_results():
    published = pd.read_csv(PROCESSED / "sensitivity_test.csv")
    pd.testing.assert_frame_equal(sensitivity(load()), published)


def test_headline_findings():
    rank = score(load())
    assert rank.iloc[0]["SUB_NAME_7"] == "Inland Slopes"
    remnant = pd.read_csv(PROCESSED / "remnant_by_subregion.csv")
    assert remnant["ha"].sum() == pytest.approx(860_669, abs=5)
    pct_3406 = remnant[remnant["PCTID"] == 3406]
    top2 = pct_3406.nlargest(2, "ha")
    assert set(top2["SUB_NAME_7"]) == {"Hill End", "Orange"}
    assert top2["ha"].sum() / pct_3406["ha"].sum() == pytest.approx(0.83, abs=0.01)


# STEP 3: The score formula on a tiny example
def test_score_formula():
    s = pd.DataFrame({"REG_NAME_7": ["R", "R"], "SUB_NAME_7": ["A", "B"], "PCTID": [1, 1],
                      "unprot_ha": [75, 25], "share": [0.75, 0.25], "demand": [100, 100],
                      "cleared": [0.5, 0.5]})
    rank = score(s).set_index("SUB_NAME_7")
    assert rank.loc["A", "score"] == pytest.approx(0.75 * 100 * 1.5)
    assert rank.loc["A", "rank"] == 1


# STEP 4: BioNet facts are checked before use
def test_check_targets_rejects_bad_percent_cleared():
    facts = pd.read_csv(PROCESSED / "pct_targets.csv")
    check_targets(facts)
    facts.loc[0, "PCTPercentCleared"] = 89     # a percentage instead of a share
    with pytest.raises(ValueError, match="between 0 and 1"):
        check_targets(facts)
