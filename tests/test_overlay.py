"""Tests for the area calculations, on squares with known areas."""
# STEP 1: Imports and test shapes
import geopandas as gpd
import pandas as pd
import pytest
from shapely.geometry import box

from download_layers import drop_slivers
from overlay import add_protected, split_by_subregion, summarise, validate

CRS = 3308
HA = 10_000  # square metres in a hectare


def square(x, y, side_m):
    return box(x, y, x + side_m, y + side_m)


@pytest.fixture
def pieces():
    # One 100 ha patch of PCT 309 (1 km x 1 km) that crosses two subregions half and half
    veg = gpd.GeoDataFrame({"PCTID": [309]}, geometry=[square(0, 0, 1000)], crs=CRS)
    sub = gpd.GeoDataFrame({"SUB_CODE_7": ["A", "B"], "SUB_NAME_7": ["West", "East"],
                            "REG_NAME_7": ["R", "R"]},
                           geometry=[box(-5000, -5000, 500, 5000), box(500, -5000, 5000, 5000)],
                           crs=CRS)
    return split_by_subregion(veg, sub)


# STEP 2: Splitting by subregion
def test_split_keeps_total_area(pieces):
    assert pieces["ha"].sum() == pytest.approx(100)
    assert sorted(pieces["ha"].round(0)) == [50, 50]


# STEP 3: Protected area, with two reserves that overlap each other
def test_overlapping_reserves_are_not_counted_twice(pieces):
    # Both reserves cover the whole West half, so protection there must be 50 ha, not 100
    capad = gpd.GeoDataFrame(geometry=[box(-100, -100, 500, 1100), box(-200, -200, 500, 1200)],
                             crs=CRS)
    out = add_protected(pieces, capad).set_index("SUB_NAME_7")
    assert out.loc["West", "prot_ha"] == pytest.approx(50)
    assert out.loc["East", "prot_ha"] == pytest.approx(0)


def test_summary_and_checks(pieces):
    capad = gpd.GeoDataFrame(geometry=[box(0, 0, 250, 1000)], crs=CRS)   # 25 ha of West
    by_sub = summarise(add_protected(pieces, capad)).set_index("SUB_NAME_7")
    assert by_sub.loc["West", "unprot_ha"] == 25
    assert by_sub.loc["West", "pct_protected"] == 50.0
    validate(by_sub.reset_index())


def test_validate_rejects_impossible_protection():
    bad = pd.DataFrame({"ha": [10], "prot_ha": [20], "pct_protected": [200]})
    with pytest.raises(ValueError):
        validate(bad)


# STEP 4: Border slivers from the rough state outline are dropped
def test_drop_slivers():
    gdf = pd.DataFrame({"SUB_NAME_7": ["Real", "Sliver", "Big but partial"],
                        "full_ha": [1000, 500_000, 500_000],
                        "area_ha": [1000, 2000, 400_000]})
    assert drop_slivers(gdf)["SUB_NAME_7"].tolist() == ["Real", "Big but partial"]
