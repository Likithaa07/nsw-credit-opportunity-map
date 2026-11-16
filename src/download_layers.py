"""Download the spatial layers: IBRA subregions, protected areas and the target PCT polygons."""
# STEP 1: Imports
from __future__ import annotations

import time

import geopandas as gpd
import pandas as pd

from config import (CAPAD_ZIP, CRS, IBRA_ZIP, PROCESSED, RAW, STATES_ZIP, SVTM, TARGETS,
                    make_folders)
from utils import DataValidationError, download, get, get_logger, require_columns

log = get_logger("download_layers")
PAGE_SIZE = 1000


# STEP 2: IBRA v7.1 subregions, clipped to NSW, with border slivers removed
def drop_slivers(clipped: gpd.GeoDataFrame) -> gpd.GeoDataFrame:
    """Drop Qld/Vic pieces that come from the rough state outline (under 1% and 5,000 ha)."""
    share = clipped["area_ha"] / clipped["full_ha"]
    slivers = (share < 0.01) & (clipped["area_ha"] < 5000)
    log.info("Dropped slivers: %s", clipped.loc[slivers, "SUB_NAME_7"].tolist())
    return clipped[~slivers]


def nsw_subregions() -> gpd.GeoDataFrame:
    ibra = gpd.read_file(download(IBRA_ZIP, RAW / "ibra.zip")).to_crs(CRS)
    states = gpd.read_file(download(STATES_ZIP, RAW / "states.zip"))
    require_columns(ibra, ["SUB_CODE_7", "SUB_NAME_7", "REG_NAME_7"], "IBRA layer")
    nsw = states[states["name"] == "New South Wales"].to_crs(CRS)
    if nsw.empty:
        raise DataValidationError("New South Wales not found in the states layer.")

    ibra["full_ha"] = ibra.area / 10_000
    clipped = gpd.clip(ibra, nsw)
    clipped["area_ha"] = clipped.area / 10_000
    out = drop_slivers(clipped)
    out.to_file(PROCESSED / "ibra_nsw.gpkg")
    log.info("%d NSW subregions", len(out))
    return out


# STEP 3: Protected areas (CAPAD 2024), NSW only
def nsw_protected_areas() -> None:
    download(CAPAD_ZIP, RAW / "capad.zip")
    log.info("CAPAD saved (filtered to NSW when used)")


# STEP 4: Target PCT polygons from the SVTM map service, 1,000 at a time
def fetch_pct(pct: int) -> gpd.GeoDataFrame:
    parts, offset, t0 = [], 0, time.time()
    while True:
        r = get(SVTM, {"where": f"PCTID = {pct}", "outFields": "PCTID,PCTName",
                       "resultOffset": offset, "resultRecordCount": PAGE_SIZE,
                       "outSR": CRS, "f": "geojson"}, timeout=300)
        if '"error"' in r.text[:200]:
            raise DataValidationError(f"SVTM returned an error for PCT {pct}: {r.text[:200]}")
        page = gpd.read_file(r.text)
        if page.empty:
            break
        parts.append(page)
        offset += len(page)
    if not parts:
        raise DataValidationError(f"SVTM returned no polygons for PCT {pct}.")
    gdf = pd.concat(parts, ignore_index=True).set_crs(CRS, allow_override=True)
    log.info("PCT %d: %d polygons (%.0fs)", pct, len(gdf), time.time() - t0)
    return gdf


def svtm_targets() -> None:
    """Saves each PCT as its own layer, so a stopped run carries on where it left off."""
    out = RAW / "svtm_targets.gpkg"
    done = gpd.list_layers(out)["name"].tolist() if out.exists() else []
    for pct in TARGETS:
        if f"pct_{pct}" in done:
            log.info("PCT %d already downloaded", pct)
            continue
        fetch_pct(pct).to_file(out, layer=f"pct_{pct}")


# STEP 5: Run everything
def main() -> None:
    make_folders()
    nsw_subregions()
    nsw_protected_areas()
    svtm_targets()


if __name__ == "__main__":
    main()
