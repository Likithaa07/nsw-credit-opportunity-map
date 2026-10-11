"""Map series: a statewide overview plus a detail map for each of the top four target PCTs."""
# STEP 1: Imports
import geopandas as gpd
import matplotlib.patches as mpatches
import matplotlib.pyplot as plt
import pandas as pd

from config import (BASE, CRS, DEMAND, EDGE, MAPS, MUTED, PROCESSED, PROTECTED, RAMP, RAW,
                    REMNANT, SHORT_NAMES)

DETAIL_PCTS = [309, 290, 3406, 4047]
SOURCE = "Data: NSW SVTM C2.0M2.2, BioNet, IBRA v7.1, CAPAD 2024, BOS registers (Oct 2026)."


# STEP 2: Load layers and tables
def load():
    ibra = gpd.read_file(PROCESSED / "ibra_nsw.gpkg")
    pieces = gpd.read_file(PROCESSED / "pieces.gpkg")
    capad = gpd.read_file(RAW / "capad.zip")
    capad = capad[capad["STATE"] == "NSW"].to_crs(CRS)
    rank = pd.read_csv(PROCESSED / "subregion_ranking.csv")
    by_sub = pd.read_csv(PROCESSED / "remnant_by_subregion.csv")
    cleared = dict(pd.read_csv(PROCESSED / "pct_targets.csv")[["PCTID", "PCTPercentCleared"]].values)
    return ibra, pieces, capad, rank, by_sub, cleared


# STEP 3: Scale bar helper
def scale_bar(ax, box, side):
    km = 10 if side < 150_000 else 50 if side < 600_000 else 100
    x, y = box[0] + side * 0.05, box[1] + side * 0.05
    ax.plot([x, x + km * 1000], [y, y], color="#0b0b0b", lw=3)
    ax.text(x + km * 500, y + side * 0.015, f"{km} km", ha="center", fontsize=9)


# STEP 4: Map 1 - statewide overview, subregions shaded by opportunity score
def overview(ibra, rank):
    m = ibra.merge(rank[["SUB_NAME_7", "score", "rank"]], on="SUB_NAME_7", how="left")
    labels = ["Low (under 10)", "Moderate (10–30)", "High (30–100)", "Very high (100+)"]
    m["cls"] = pd.cut(m["score"], bins=[0, 10, 30, 100, 1e9], labels=labels)

    fig, ax = plt.subplots(figsize=(10, 9))
    m[m["cls"].isna()].plot(ax=ax, color="#e8e7e3", edgecolor="white", linewidth=0.4)
    for lab, col in zip(labels, RAMP):
        m[m["cls"] == lab].plot(ax=ax, color=col, edgecolor="white", linewidth=0.4)
    for _, r in m[m["rank"] <= 5].iterrows():
        p = r.geometry.representative_point()
        ax.annotate(f"{int(r['rank'])}. {r['SUB_NAME_7']}", (p.x, p.y), fontsize=9, weight="bold",
                    xytext=(6, 6), textcoords="offset points",
                    bbox=dict(boxstyle="round,pad=0.2", fc="white", ec="none", alpha=0.85))

    x0, y0 = ax.get_xlim()[0] + 40_000, ax.get_ylim()[0] + 40_000
    ax.plot([x0, x0 + 200_000], [y0, y0], color="#0b0b0b", lw=3)
    ax.text(x0 + 100_000, y0 + 15_000, "200 km", ha="center", fontsize=9)

    handles = [mpatches.Patch(color=c, label=l) for c, l in zip(RAMP, labels)]
    handles.append(mpatches.Patch(color="#e8e7e3", label="No target vegetation"))
    ax.legend(handles=handles, title="Opportunity score", loc="lower right", frameon=False)
    ax.set_title("Areas for further investigation: new biodiversity stewardship supply\n"
                 "Six under-supplied ecosystem credit types, by IBRA subregion", fontsize=13, loc="left")
    ax.set_axis_off()
    fig.text(0.02, 0.02, SOURCE + " Regional scale only: not for site decisions.", fontsize=7, color=MUTED)
    fig.savefig(MAPS / "01_statewide_overview.png", dpi=200, bbox_inches="tight")
    plt.close(fig)


# STEP 5: Maps 2-5 - one detail map per PCT, labels on the four largest subregions
def detail(p, n, ibra, pieces, capad, by_sub, cleared):
    v = pieces[pieces["PCTID"] == p]
    xmin, ymin, xmax, ymax = v.total_bounds
    side = max(xmax - xmin, ymax - ymin) * 1.25
    cx, cy = (xmin + xmax) / 2, (ymin + ymax) / 2
    box = (cx - side / 2, cy - side / 2, cx + side / 2, cy + side / 2)

    fig, ax = plt.subplots(figsize=(9, 9))
    ibra.plot(ax=ax, color=BASE, edgecolor=EDGE, linewidth=0.6)
    capad.cx[box[0]:box[2], box[1]:box[3]].plot(ax=ax, color=PROTECTED, edgecolor="none")
    v.plot(ax=ax, color=REMNANT, edgecolor=REMNANT, linewidth=0.8)

    offsets = [(15, 15), (-150, 20), (15, -40), (-150, -45)]
    rows = by_sub[(by_sub["PCTID"] == p) & (by_sub["unprot_ha"] >= 10)].nlargest(4, "ha")
    for k, (_, r) in enumerate(rows.iterrows()):
        pt = v[v["SUB_NAME_7"] == r["SUB_NAME_7"]].union_all().representative_point()
        ax.annotate(f"{r['SUB_NAME_7']}\n{r['ha']:,.0f} ha ({r['pct_protected']:.0f}% protected)",
                    (pt.x, pt.y), xytext=offsets[k], textcoords="offset points", fontsize=8.5,
                    bbox=dict(boxstyle="round,pad=0.25", fc="white", ec=EDGE, alpha=0.95),
                    arrowprops=dict(arrowstyle="-", color=MUTED, lw=0.6))

    scale_bar(ax, box, side)
    t = by_sub[by_sub["PCTID"] == p][["ha", "prot_ha"]].sum()
    line2 = (f"Remaining {t.ha:,.0f} ha · {100 * t.prot_ha / t.ha:.0f}% protected · "
             f"{100 * cleared[p]:.0f}% cleared · {DEMAND[p]} credits retired/yr, none available")
    ax.set_title(f"PCT {p}: {SHORT_NAMES[p]}\n{line2}", fontsize=11, loc="left")
    ax.set_xlim(box[0], box[2])
    ax.set_ylim(box[1], box[3])
    ax.set_axis_off()
    ax.legend(handles=[mpatches.Patch(color=REMNANT, label="Mapped remnant (SVTM)"),
                       mpatches.Patch(color=PROTECTED, label="Protected area (CAPAD 2024)")],
              loc="lower right", frameon=True, facecolor="white", edgecolor="none")
    fig.text(0.02, 0.02, SOURCE + " Regional scale (1:25,000 at best): field validation needed.",
             fontsize=7, color=MUTED)
    fig.savefig(MAPS / f"0{n}_pct_{p}.png", dpi=200, bbox_inches="tight")
    plt.close(fig)


# STEP 6: Run everything
if __name__ == "__main__":
    ibra, pieces, capad, rank, by_sub, cleared = load()
    overview(ibra, rank)
    for n, p in enumerate(DETAIL_PCTS, start=2):
        detail(p, n, ibra, pieces, capad, by_sub, cleared)
    print("Maps saved to", MAPS)
