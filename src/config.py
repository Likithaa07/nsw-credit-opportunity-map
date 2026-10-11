# STEP 1: Shared settings for every script
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / "data" / "raw"
PROCESSED = ROOT / "data" / "processed"
MAPS = ROOT / "outputs" / "maps"
for folder in (RAW, PROCESSED, MAPS):
    folder.mkdir(parents=True, exist_ok=True)

CRS = 3308  # NSW Lambert (GDA94), used by the SVTM service and for all area calculations

# STEP 2: Target credit types (zero supply), with credits retired per year
# PCT 1600 is left out: it was retired in the 2022 eastern NSW revision and is not in the SVTM.
DEMAND = {309: 507, 290: 289, 24: 155, 4047: 153, 1604: 137, 3406: 127}
TARGETS = list(DEMAND)

SHORT_NAMES = {
    309: "Black Cypress Pine – Red Stringybark low open forest",
    290: "Red Stringybark – Red Box – Long-leaved Box low open forest",
    24: "Canegrass swamp tall grassland wetland",
    4047: "Northern Swamp Mahogany–Bottlebrush Swamp Forest",
    1604: "Narrow-leaved Ironbark – Grey Box – Spotted Gum woodland",
    3406: "Southwest Ranges White Box Woodland",
}

# STEP 3: Data services (all public, no login)
BIONET = "https://data.bionet.nsw.gov.au/biosvcapp/odata/"
SVTM = "https://mapprod3.environment.nsw.gov.au/arcgis/rest/services/VIS/SVTM_NSW_Extant_PCT/MapServer/3/query"
SVTM_1750 = "https://mapprod3.environment.nsw.gov.au/arcgis/rest/services/VIS/SVTM_NSW_1750_PCT/MapServer/3/query"
IBRA_ZIP = "https://fed.dcceew.gov.au/api/download/v1/items/38e668537a2141be85b8418ac8b6f3ed/shapefile?layers=0"
CAPAD_ZIP = "https://fed.dcceew.gov.au/api/download/v1/items/ec356a872d8048459fe78fc80213dc70/shapefile?layers=0"
STATES_ZIP = "https://naciscdn.org/naturalearth/10m/cultural/ne_10m_admin_1_states_provinces.zip"

# STEP 4: Colours (colour-blind-safe palette)
REMNANT = "#eb6834"
PROTECTED = "#c9c8c2"
BASE = "#f5f4f1"
EDGE = "#b5b3ad"
MUTED = "#52514e"
RAMP = ["#9ec5f4", "#5598e7", "#256abf", "#104281"]
