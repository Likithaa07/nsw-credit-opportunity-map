"""Tests for the stewardship reality check, using a tiny made-up register."""
# STEP 1: Imports
import pandas as pd
import pytest

from stewardship_check import compare, load_bsa
from utils import DataValidationError


def write_register(path, rows):
    cols = ["agreement_id", "agreement_type", "agreement_status", "principal_agreement_area",
            "nsw_ibra_bioregion"]
    pd.DataFrame(rows, columns=cols).to_csv(path, index=False)
    return path


# STEP 2: Only stewardship agreements that are in force are counted
def test_load_keeps_only_bsa_in_force(tmp_path):
    path = write_register(tmp_path / "reg.csv", [
        ["BS1", "Biodiversity Stewardship Agreement", "In Force", 100, "Riverina"],
        ["BS2", "Biodiversity Stewardship Agreement", "Terminated", 50, "Riverina"],
        ["CA1", "Funded Conservation Agreement", "In Force", 70, "Riverina"],
    ])
    assert load_bsa(path)["agreement_id"].tolist() == ["BS1"]


def test_register_without_bsa_gives_clear_error(tmp_path):
    path = write_register(tmp_path / "reg.csv", [
        ["CA1", "Funded Conservation Agreement", "In Force", 70, "Riverina"]])
    with pytest.raises(DataValidationError):
        load_bsa(path)


# STEP 3: Shares add up to 100% and use the committed ranking
def test_compare_shares(tmp_path):
    path = write_register(tmp_path / "reg.csv", [
        ["BS1", "Biodiversity Stewardship Agreement", "In Force", 300, "Sydney Basin"],
        ["BS2", "Biodiversity Stewardship Agreement", "In Force", 100, "NSW South Western Slopes"],
    ])
    out = compare(load_bsa(path))[0].set_index("bioregion")
    assert out["score_share_pct"].sum() == pytest.approx(100)
    assert out["bsa_area_share_pct"].sum() == pytest.approx(100)
    assert out.loc["NSW South Western Slopes", "bsa_area_share_pct"] == pytest.approx(25)
    assert out["score_share_pct"].idxmax() == "NSW South Western Slopes"
