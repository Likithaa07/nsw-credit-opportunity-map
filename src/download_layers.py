"""Download the spatial layers: IBRA subregions, protected areas and the target PCT polygons."""
# STEP 1: Imports
import time
import urllib.request

import geopandas as gpd
import pandas as pd
import requests

from config import CAPAD_ZIP, CRS, IBRA_ZIP, PROCESSED, RAW, STATES_ZIP, SVTM, TARGETS


# STEP 2: Download a file once (skipped if it is already there)
def download(url, path):
    if not path.exists():
        print("Downloading", path.name)
        urllib.request.urlretrieve(url, path)
    return path


# STEP 3: IBRA v7.1 subregions, clipped to NSW, with border slivers removed
def nsw_subregions():
    ibra = gpd.read_file(download(IBRA_ZIP, RAW / "ibra.zip")).to_crs(CRS)
    states = gpd.read_file(download(STATES_ZIP, RAW / "states.zip"))
    nsw = states[states["name"] == "New South Wales"].to_crs(CRS)

    ibra["full_ha"] = ibra.area / 10_000
    clipped = gpd.clip(ibra, nsw)
    clipped["area_ha"] = clipped.area / 10_000
    share = clipped["area_ha"] / clipped["full_ha"]
    slivers = (share < 0.01) & (clipped["area_ha"] < 5000)      # Qld/Vic pieces from a rough outline
    print("Dropped slivers:", clipped.loc[slivers, "SUB_NAME_7"].tolist())
    out = clipped[~slivers]
    out.to_file(PROCESSED / "ibra_nsw.gpkg")
    print(len(out), "NSW subregions")


# STEP 4: Protected areas (CAPAD 2024), NSW only
def nsw_protected_areas():
    download(CAPAD_ZIP, RAW / "capad.zip")
    print("CAPAD saved (filtered to NSW when used)")


# STEP 5: Target PCT polygons from the SVTM map service, 1,000 at a time
def fetch_pct(pct):
    parts, offset, t0 = [], 0, time.time()
    while True:
        r = requests.get(SVTM, params={"where": f"PCTID = {pct}", "outFields": "PCTID,PCTName",
                                       "resultOffset": offset, "resultRecordCount": 1000,
                                       "outSR": CRS, "f": "geojson"}, timeout=300)
        r.raise_for_status()
        page = gpd.read_file(r.text)
        if page.empty:
            break
        parts.append(page)
        offset += len(page)
    gdf = pd.concat(parts, ignore_index=True).set_crs(CRS, allow_override=True)
    print(f"PCT {pct}: {len(gdf)} polygons ({time.time() - t0:.0f}s)")
    return gdf


def svtm_targets():
    out = RAW / "svtm_targets.gpkg"
    done = gpd.list_layers(out)["name"].tolist() if out.exists() else []
    for pct in TARGETS:
        if f"pct_{pct}" in done:
            print(f"PCT {pct} already downloaded")
            continue
        fetch_pct(pct).to_file(out, layer=f"pct_{pct}")


# STEP 6: Run everything
if __name__ == "__main__":
    nsw_subregions()
    nsw_protected_areas()
    svtm_targets()
