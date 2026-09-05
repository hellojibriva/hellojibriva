"""
PHASE 10: draft research figures.

Three figures, deliberately few. Design constraints applied throughout:
  * a disease-year with no WAHIS report is drawn as a GAP, never as zero;
  * the three diseases are never placed on a shared colour scale where their
    magnitudes differ by an order of magnitude;
  * every figure is backed by a CSV in outputs/tables/, which also discharges
    the contrast-relief requirement on the aqua series.

Palette: categorical slots 1-3 of the validated reference palette
(blue / orange / aqua), which pass all-pairs CVD and normal-vision separation
in light mode. Sequential shading uses the single-hue blue ramp.
"""
from __future__ import annotations

import sys
from pathlib import Path

import matplotlib as mpl
import numpy as np
import pandas as pd

mpl.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
from matplotlib.colors import LinearSegmentedColormap, Normalize  # noqa: E402

sys.path.insert(0, str(Path(__file__).resolve().parent))
import wahis_common as W  # noqa: E402

W.FIGURES.mkdir(parents=True, exist_ok=True)

SURFACE = "#fcfcfb"
INK = "#0b0b0b"
INK2 = "#52514e"
MUTED = "#8a8984"
GRID = "#e4e3df"
COLOR = {"Rabies": "#2a78d6", "HPAI": "#eb6834", "Trypanosomosis": "#1baf7a"}
BLUES = LinearSegmentedColormap.from_list(
    "wahis_blue",
    ["#cde2fb", "#9ec5f4", "#6da7ec", "#3987e5", "#256abf", "#184f95", "#0d366b"],
)

mpl.rcParams.update({
    "figure.facecolor": SURFACE, "axes.facecolor": SURFACE,
    "savefig.facecolor": SURFACE, "font.family": "DejaVu Sans",
    "font.size": 9, "axes.edgecolor": GRID, "axes.labelcolor": INK2,
    "xtick.color": INK2, "ytick.color": INK2, "text.color": INK,
    "axes.titlecolor": INK, "axes.grid": False, "figure.dpi": 110,
    "savefig.dpi": 300, "savefig.bbox": "tight",
})

YEARS = list(range(W.STUDY_START, W.STUDY_END + 1))
annual = pd.read_csv(W.TABLES / "t02_annual_outbreaks.csv", index_col=0)
annual = annual.reindex(YEARS).reindex(columns=W.DISEASE_ORDER)
mat = pd.read_csv(W.TABLES / "t05_state_disease_outbreak_matrix.csv", index_col=0)
yrs = pd.read_csv(W.TABLES / "t06_state_disease_reporting_years_matrix.csv",
                  index_col=0)
mat = mat.reindex(columns=W.DISEASE_ORDER)
yrs = yrs.reindex(columns=W.DISEASE_ORDER)


def tidy(ax, *, left=True, bottom=True) -> None:
    for side in ["top", "right"]:
        ax.spines[side].set_visible(False)
    ax.spines["left"].set_visible(left)
    ax.spines["bottom"].set_visible(bottom)
    ax.tick_params(length=3, width=0.8)


# ---------------------------------------------------------------- FIGURE 1
fig = plt.figure(figsize=(9.8, 9.2))
gs = fig.add_gridspec(4, 1, height_ratios=[2.6, 1, 1, 1], hspace=0.30,
                      top=0.885, bottom=0.105, left=0.085, right=0.985)

ax = fig.add_subplot(gs[0])
for y in YEARS:
    ax.axvline(y, color=GRID, lw=0.5, zorder=0)
for d in W.DISEASE_ORDER:
    s = annual[d]
    ax.plot(s.index, s.values, color=COLOR[d], lw=2, marker="o", ms=4.5,
            mfc=COLOR[d], mec=SURFACE, mew=1.2, label=d, zorder=3,
            clip_on=False)
ax.set_xlim(2005.5, 2023.5)
ax.set_ylim(0, 300)
ax.set_yticks([0, 50, 100, 150, 200, 250])
ax.set_xticks(YEARS)
ax.set_xticklabels(YEARS, rotation=45, ha="right", fontsize=8)
ax.set_ylabel("Reported new outbreaks")
ax.legend(frameon=False, ncol=3, loc="upper left", fontsize=9,
          bbox_to_anchor=(0, 1.03), handlelength=1.8, columnspacing=1.6)
tidy(ax)
ax.text(0.999, 1.03, "A · all three on one shared axis",
        transform=ax.transAxes, fontsize=8.5, color=MUTED, ha="right",
        va="top")

fig.suptitle(
    "Figure 1. Temporal patterns of reported zoonotic animal disease outbreaks "
    "in Nigeria, 2006\u20132023",
    x=0.008, ha="left", fontsize=12, fontweight="bold", y=0.985)
fig.text(0.008, 0.945,
         "Source: WOAH WAHIS six-monthly animal disease reports. Points are "
         "years with a report; a break in a line is a year with NO report, "
         "which is not the same as a reported zero.",
         fontsize=8.2, color=INK2, va="top")

for i, d in enumerate(W.DISEASE_ORDER):
    axi = fig.add_subplot(gs[i + 1])
    s = annual[d]
    gaps = [y for y in YEARS if pd.isna(s[y])]
    for y in gaps:
        axi.axvspan(y - 0.5, y + 0.5, color="#eceae4", zorder=0)
    axi.fill_between(s.index, 0, s.values, color=COLOR[d], alpha=0.16,
                     zorder=1)
    axi.plot(s.index, s.values, color=COLOR[d], lw=1.8, marker="o", ms=3.6,
             mec=SURFACE, mew=0.9, zorder=3, clip_on=False)
    top = float(np.nanmax(s.values))
    axi.set_xlim(2005.5, 2023.5)
    axi.set_ylim(0, top * 1.55)
    axi.set_yticks([0, round(top / 100) * 50 if top > 100 else 20,
                    round(top / 50) * 50 if top > 100 else 40])
    axi.set_xticks(YEARS)
    axi.set_xticklabels(YEARS if i == 2 else [], rotation=45, ha="right",
                        fontsize=8)
    peak = int(s.idxmax())
    axi.annotate(f"{int(s.max())}", (peak, s[peak]), xytext=(0, 4),
                 textcoords="offset points", ha="center", fontsize=7.5,
                 color=COLOR[d], fontweight="bold")
    note = f"   \u00b7   no report: {', '.join(str(g) for g in gaps)}" if gaps else ""
    axi.text(0.004, 0.97, d, transform=axi.transAxes, fontsize=9.5,
             fontweight="bold", color=COLOR[d], va="top")
    if note:
        axi.text(0.004 + 0.011 * len(d) + 0.02, 0.955, note.strip(),
                 transform=axi.transAxes, fontsize=7.2, color=MUTED, va="top")
    tidy(axi)
    if i == 0:
        axi.text(0.999, 0.97, "B \u00b7 each disease on its own scale",
                 transform=axi.transAxes, fontsize=8.5, color=MUTED,
                 ha="right", va="top")
    if i == 1:
        axi.set_ylabel("Reported new outbreaks")

fig.text(0.008, 0.008,
         "Panel B repeats the same counts with an independent y-scale per "
         "disease, so the shape of the smaller series stays legible; grey "
         "bands mark years with no report.\n"
         "Trypanosomosis reporting ends after 2021 because the WOAH disease "
         "name itself ends there \u2014 'Trypanosomosis (tsetse-transmitted) "
         "(-2021)'. The 2022\u20132023 blanks are a classification artefact, "
         "not an observed decline.",
         fontsize=7.8, color=INK2, va="bottom", linespacing=1.5)

fig.savefig(W.FIGURES / "figure1_temporal_outbreaks.png")
fig.savefig(W.FIGURES / "figure1_temporal_outbreaks.pdf")
plt.close(fig)
print("figure1_temporal_outbreaks.png/.pdf")

# ---------------------------------------------------------------- FIGURE 2
fig, axes = plt.subplots(1, 3, figsize=(11.4, 8.2))
for ax, d in zip(axes, W.DISEASE_ORDER):
    s = mat[d].dropna().sort_values()
    ax.barh(range(len(s)), s.values, color=COLOR[d], height=0.66, zorder=3)
    ax.set_yticks(range(len(s)))
    ax.set_yticklabels(s.index, fontsize=7.6)
    for i, v in enumerate(s.values):
        ax.text(v + s.max() * 0.02, i, f"{int(v)}", va="center", fontsize=7,
                color=INK2)
    ax.set_xlim(0, s.max() * 1.16)
    ax.set_title(f"{d}\n{int(s.sum())} outbreaks · {len(s)} of 37 states/FCT",
                 fontsize=9.5, fontweight="bold", color=COLOR[d], loc="left",
                 pad=8)
    ax.set_xlabel("Reported new outbreaks, 2006–2023", fontsize=8)
    ax.xaxis.grid(True, color=GRID, lw=0.6, zorder=0)
    tidy(ax, left=False)
fig.suptitle(
    "Figure 2. Geographic distribution of reported outbreaks by state/FCT, "
    "Nigeria 2006–2023",
    x=0.008, ha="left", fontsize=11.5, fontweight="bold", y=0.985)
fig.text(0.008, 0.008,
         "Each panel has its own x-scale; bar lengths are NOT comparable "
         "between panels. States absent from a panel reported that disease in "
         "no study year.\nCounts describe reported surveillance activity, not "
         "disease risk or incidence. National ('Nigeria') records are excluded "
         "from state totals.",
         fontsize=7.6, color=INK2, va="bottom")
fig.tight_layout(rect=[0, 0.045, 1, 0.965])
fig.savefig(W.FIGURES / "figure2_geographic_distribution.png")
fig.savefig(W.FIGURES / "figure2_geographic_distribution.pdf")
plt.close(fig)
print("figure2_geographic_distribution.png/.pdf")

# ---------------------------------------------------------------- FIGURE 3
order = mat.notna().sum(axis=1).astype(str) + "_" + \
    mat.sum(axis=1, min_count=1).fillna(0).map(lambda v: f"{v:09.0f}")
states = order.sort_values(ascending=False).index.tolist()

fig, axes = plt.subplots(1, 2, figsize=(9.2, 9.6),
                         gridspec_kw={"wspace": 0.62})

# Panel A - outbreaks, shaded WITHIN each disease column.
axA = axes[0]
A = mat.reindex(states)
shade = A.copy()
for d in W.DISEASE_ORDER:
    mx = A[d].max()
    shade[d] = A[d] / mx if mx else np.nan
axA.imshow(np.ma.masked_invalid(shade.values), cmap=BLUES,
           norm=Normalize(0, 1), aspect="auto")
for i in range(len(states)):
    for j, d in enumerate(W.DISEASE_ORDER):
        v = A.iloc[i, j]
        if pd.isna(v):
            axA.text(j, i, "·", ha="center", va="center", color=MUTED,
                     fontsize=10)
        else:
            axA.text(j, i, f"{int(v)}", ha="center", va="center", fontsize=7,
                     color="#ffffff" if shade.iloc[i, j] > 0.55 else INK)
axA.set_title("A. Reported new outbreaks\nshaded within each column",
              fontsize=9.5, fontweight="bold", loc="left", pad=24)

# Panel B - reporting years, one shared 0-18 scale (genuinely comparable).
axB = axes[1]
B = yrs.reindex(states)
axB.imshow(np.ma.masked_invalid(B.values), cmap=BLUES, norm=Normalize(0, 18),
           aspect="auto")
for i in range(len(states)):
    for j in range(3):
        v = B.iloc[i, j]
        if pd.isna(v):
            axB.text(j, i, "·", ha="center", va="center", color=MUTED,
                     fontsize=10)
        else:
            axB.text(j, i, f"{int(v)}", ha="center", va="center", fontsize=7,
                     color="#ffffff" if v / 18 > 0.55 else INK)
axB.set_title("B. Years with a report (of 18)\nshared 0–18 scale",
              fontsize=9.5, fontweight="bold", loc="left", pad=24)

for ax in (axA, axB):
    ax.xaxis.set_ticks_position("top")
    ax.set_xticks(range(3))
    ax.set_xticklabels(["Rabies", "HPAI", "Tryp.\u00b9"], fontsize=8.5)
    for lbl, d in zip(ax.get_xticklabels(), W.DISEASE_ORDER):
        lbl.set_color(COLOR[d])
        lbl.set_fontweight("bold")
    ax.set_yticks(range(len(states)))
    ax.set_yticklabels(states, fontsize=7.4)
    ax.set_xticks(np.arange(-0.5, 3, 1), minor=True)
    ax.set_yticks(np.arange(-0.5, len(states), 1), minor=True)
    ax.grid(which="minor", color=SURFACE, lw=1.6)
    ax.tick_params(which="minor", length=0)
    ax.tick_params(length=0)
    for s in ax.spines.values():
        s.set_visible(False)

fig.suptitle(
    "Figure 3. Disease × state reporting matrix, Nigeria 2006–2023",
    x=0.008, ha="left", fontsize=11.5, fontweight="bold", y=0.975)
fig.text(0.008, 0.012,
         "States ordered by number of diseases reported, then by cumulative "
         "outbreaks. '·' = the state reported that disease in no study year.\n"
         "Panel A is shaded column-wise because the three diseases differ by an "
         "order of magnitude; shading is NOT comparable across columns — the "
         "printed numbers are.\nCumulative count (A) and persistence (B) measure "
         "different things and rank states differently.\n"
         "\u00b9 Tryp. = Trypanosomosis (tsetse-transmitted); reportable "
         "under this WAHIS name only to 2021, so its column covers "
         "2006\u20132021, not 2006\u20132023.",
         fontsize=7.6, color=INK2, va="bottom", linespacing=1.5)
fig.tight_layout(rect=[0, 0.075, 1, 0.955])
fig.savefig(W.FIGURES / "figure3_disease_state_matrix.png")
fig.savefig(W.FIGURES / "figure3_disease_state_matrix.pdf")
plt.close(fig)
print("figure3_disease_state_matrix.png/.pdf")
print(f"\nFigures written to {W.FIGURES}")
