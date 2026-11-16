"""Reality check: are existing Biodiversity Stewardship Agreement (BSA) sites already in the
areas the ranking points to, or are those areas under-served?

The public register gives each agreement's IBRA bioregion and area (not its boundary, which is
internal-use only), so the comparison is made by bioregion.

Download the register CSV first and save it as data/raw/bct_public_register.csv:
https://www.nsw.gov.au/environment-land-and-water/conservation-on-private-land/public-register
"""
# STEP 1: Imports and settings
from __future__ import annotations

import matplotlib.pyplot as plt
import pandas as pd
from scipy.stats import spearmanr

from pathlib import Path

from config import MAPS, MUTED, PROCESSED, RAW, REMNANT, make_folders
from utils import DataValidationError, get_logger, require_columns, require_files

log = get_logger("stewardship_check")

REGISTER = RAW / "bct_public_register.csv"
GREY = "#8a8984"


# STEP 2: Load the register and keep stewardship agreements that are in force
def load_bsa(register: Path = REGISTER) -> pd.DataFrame:
    require_files(register, hint="Download the 'Public register of conservation agreements' CSV "
                                 "from the link at the top of this file and save it with that name.")
    reg = pd.read_csv(register)
    require_columns(reg, ["agreement_id", "agreement_type", "agreement_status",
                          "principal_agreement_area", "nsw_ibra_bioregion"], "BCT register")
    bsa = reg[(reg["agreement_type"] == "Biodiversity Stewardship Agreement")
              & (reg["agreement_status"] == "In Force")]
    if bsa.empty:
        raise DataValidationError("No Biodiversity Stewardship Agreements in force in the register.")
    log.info("Stewardship agreements in force: %d, %s ha", len(bsa),
             f"{bsa['principal_agreement_area'].sum():,.0f}")
    return bsa


# STEP 3: Compare each bioregion's share of the opportunity score with its share of BSA area
def compare(bsa: pd.DataFrame, processed_dir: Path = PROCESSED) -> tuple[pd.DataFrame, float, float]:
    rank = pd.read_csv(processed_dir / "subregion_ranking.csv")
    remnant = pd.read_csv(processed_dir / "remnant_by_subregion.csv")
    regions = (rank.groupby("REG_NAME_7")["score"].sum().to_frame("score")
               .join(remnant.groupby("REG_NAME_7")["unprot_ha"].sum()))
    sites = bsa.groupby("nsw_ibra_bioregion").agg(
        bsa_agreements=("agreement_id", "size"), bsa_ha=("principal_agreement_area", "sum"))
    out = regions.join(sites, how="outer").fillna(0)
    out["score_share_pct"] = 100 * out["score"] / out["score"].sum()
    out["bsa_area_share_pct"] = 100 * out["bsa_ha"] / out["bsa_ha"].sum()
    out = out.sort_values("score", ascending=False).reset_index(names="bioregion")
    rho, p = spearmanr(out["score"], out["bsa_ha"])
    return out, rho, p


# STEP 4: Chart - opportunity share vs stewardship share, top bioregions
def chart(out: pd.DataFrame, rho: float) -> None:
    d = out[(out["score_share_pct"] >= 1) | (out["bsa_area_share_pct"] >= 5)].iloc[::-1]
    fig, ax = plt.subplots(figsize=(9, 5.5))
    y = range(len(d))
    ax.barh([i + 0.2 for i in y], d["score_share_pct"], height=0.38, color=REMNANT,
            label="Share of opportunity score (this project)")
    ax.barh([i - 0.2 for i in y], d["bsa_area_share_pct"], height=0.38, color=GREY,
            label="Share of stewardship site area (existing)")
    ax.set_yticks(list(y))
    ax.set_yticklabels(d["bioregion"])
    ax.set_xlabel("% of NSW total")
    for side in ["top", "right"]:
        ax.spines[side].set_visible(False)
    ax.tick_params(axis="y", length=0)
    ax.grid(axis="x", color="#e4e3df")
    ax.set_axisbelow(True)
    ax.set_title("Existing stewardship sites are mostly outside the top opportunity areas",
                 loc="left", fontweight="bold", pad=28)
    ax.text(0, 1.02, f"By IBRA bioregion. Rank correlation between score and stewardship area: "
                     f"ρ = {rho:.2f}", transform=ax.transAxes, color=MUTED, fontsize=9.5)
    ax.legend(loc="lower right", frameon=False)
    fig.savefig(MAPS / "06_stewardship_check.png", dpi=200, bbox_inches="tight", facecolor="white")
    plt.close(fig)


# STEP 5: Run and save (skipped with a warning if the register has not been downloaded)
def main() -> pd.DataFrame | None:
    make_folders()
    if not REGISTER.exists():
        log.warning("Skipped: %s not found. Download it to run this check.", REGISTER.name)
        return None
    out, rho, p = compare(load_bsa())
    out.round(1).to_csv(PROCESSED / "stewardship_by_bioregion.csv", index=False)
    chart(out, rho)
    log.info("Opportunity vs stewardship by bioregion:\n%s", out.round(1).to_string(index=False))
    log.info("Spearman rank correlation (score vs BSA area): rho = %.2f, p = %.2f", rho, p)
    return out


if __name__ == "__main__":
    main()
