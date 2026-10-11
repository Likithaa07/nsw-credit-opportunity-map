"""Measure remaining, protected and unprotected vegetation for each target PCT in each IBRA subregion."""
# STEP 1: Imports
import json

import geopandas as gpd
import numpy as np
import pandas as pd
import requests
import shapely

from config import CRS, PROCESSED, RAW, SVTM, SVTM_1750, TARGETS


# STEP 2: Load the target PCT polygons and the NSW subregions
def load_inputs():
    path = RAW / "svtm_targets.gpkg"
    layers = gpd.list_layers(path)["name"].tolist()
    veg = pd.concat([gpd.read_file(path, layer=l) for l in layers],
                    ignore_index=True).set_crs(CRS, allow_override=True)
    veg["geometry"] = veg.geometry.make_valid()
    sub = gpd.read_file(PROCESSED / "ibra_nsw.gpkg")[["SUB_CODE_7", "SUB_NAME_7", "REG_NAME_7", "geometry"]]
    capad = gpd.read_file(RAW / "capad.zip")
    capad = capad[capad["STATE"] == "NSW"].to_crs(CRS)
    capad["geometry"] = capad.geometry.make_valid()
    return veg, sub, capad


# STEP 3: Cut the vegetation by subregion
def split_by_subregion(veg, sub):
    pieces = gpd.overlay(veg[["PCTID", "geometry"]], sub, how="intersection", keep_geom_type=True)
    pieces["ha"] = pieces.area / 10_000
    return pieces.reset_index(drop=True)


# STEP 4: Protected hectares per piece (spatial index, no dissolve, so it runs in seconds)
def add_protected(pieces, capad):
    pa = capad[["geometry"]].reset_index(drop=True)
    pairs = gpd.sjoin(pieces[["geometry"]], pa, predicate="intersects", how="inner")
    a = np.asarray(pieces.geometry.values[pairs.index])
    b = np.asarray(pa.geometry.values[pairs["index_right"].values])
    pairs["prot_m2"] = shapely.area(shapely.intersection(a, b))
    per_piece = pairs.groupby(level=0)["prot_m2"].sum()
    # cap at the piece's own area, so overlapping reserves are not counted twice
    pieces["prot_ha"] = np.minimum(per_piece.reindex(pieces.index).fillna(0), pieces.area) / 10_000
    return pieces


# STEP 5: Summarise by PCT and subregion
def summarise(pieces):
    by_sub = (pieces.groupby(["PCTID", "REG_NAME_7", "SUB_NAME_7"])[["ha", "prot_ha"]].sum()
              .reset_index().sort_values(["PCTID", "ha"], ascending=[True, False]))
    by_sub["ha"] = by_sub["ha"].round(0)
    by_sub["unprot_ha"] = (by_sub["ha"] - by_sub["prot_ha"]).clip(lower=0).round(0)
    by_sub["pct_protected"] = (100 * by_sub["prot_ha"] / by_sub["ha"]).round(1)
    return by_sub


# STEP 6: Compare mapped extent with BioNet's official figures (why BioNet % cleared is used)
def extent_check():
    stats = json.dumps([{"statisticType": "sum", "onStatisticField": "Shape_Area",
                         "outStatisticFieldName": "m2"}])
    where = f"PCTID IN ({','.join(map(str, TARGETS))})"
    rows = {}
    for label, url in [("mapped_today_ha", SVTM), ("mapped_1750_ha", SVTM_1750)]:
        r = requests.get(url, params={"where": where, "groupByFieldsForStatistics": "PCTID",
                                      "outStatistics": stats, "f": "json"}, timeout=120).json()
        rows[label] = {f["attributes"]["PCTID"]: f["attributes"]["m2"] / 10_000 for f in r["features"]}
    check = pd.DataFrame(rows).round(0)
    bionet = pd.read_csv(PROCESSED / "pct_targets.csv").set_index("PCTID")
    check["map_pct_left"] = (100 * check["mapped_today_ha"] / check["mapped_1750_ha"]).round(0)
    check["bionet_pct_cleared"] = (100 * bionet["PCTPercentCleared"]).round(0)
    check.index.name = "PCTID"
    check.to_csv(PROCESSED / "extent_check.csv")
    print(check)


# STEP 7: Run everything
if __name__ == "__main__":
    veg, sub, capad = load_inputs()
    pieces = add_protected(split_by_subregion(veg, sub), capad)
    pieces.to_file(PROCESSED / "pieces.gpkg")
    by_sub = summarise(pieces)
    by_sub.to_csv(PROCESSED / "remnant_by_subregion.csv", index=False)
    print(by_sub.groupby("PCTID")[["ha", "prot_ha", "unprot_ha"]].sum().round(0))
    extent_check()
