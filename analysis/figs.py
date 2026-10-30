"""Figs. 3-5: durations, event-aligned view, causes of late predecessor-named submissions."""
import pandas as pd, numpy as np, matplotlib
matplotlib.use("Agg"); import matplotlib.pyplot as plt
plt.rcParams.update({"font.family": "serif", "font.serif": ["Times New Roman", "Liberation Serif"], "font.size": 8, "axes.spines.top": False, "axes.spines.right": False,
                     "axes.edgecolor": "#52514e", "axes.labelcolor": "#0b0b0b", "xtick.color": "#52514e", "ytick.color": "#52514e", "axes.grid": True, "grid.color": "#e6e5e1", "grid.linewidth": 0.5})
BLUE, ORANGE, AQUA, INK2 = "#2a78d6", "#eb6834", "#1baf7a", "#52514e"
M = pd.read_pickle("monthly.pkl"); R = pd.read_csv("event_metrics.csv").set_index("id")
F = [i for i in R.index if i not in ("X01", "E04", "E37")]
# Fig 1: event-aligned label shares around the crossover month
rel = range(-24, 37); P, S, B = [], [], []
for i in F:
    g = M[i]; c = pd.Period(R.loc[i, "cross"], "M")
    sh = []; bo = []
    for k in rel:
        m = c + k
        if m in g.index:
            p, s = g.loc[m, "P"], g.loc[m, "S"]
            sh.append(s / (p + s) if p + s else np.nan); bo.append(1.0 if (p > 0 and s > 0) else 0.0)
        else: sh.append(np.nan); bo.append(np.nan)
    S.append(sh); B.append(bo)
S = np.array(S, float); B = np.array(B, float)
med = np.nanmedian(S, 0); q1 = np.nanpercentile(S, 25, 0); q3 = np.nanpercentile(S, 75, 0); both = np.nanmean(B, 0)
fig, ax = plt.subplots(figsize=(3.5, 2.2))
x = np.array(list(rel))
ax.fill_between(x, q1, q3, color=BLUE, alpha=0.18, lw=0)
ax.plot(x, med, color=BLUE, lw=1.6, label="Successor share (median, IQR)")
ax.plot(x, both, color=ORANGE, lw=1.4, ls="--", label="Events with both names")
ax.axvline(0, color=INK2, lw=0.7); ax.text(0.8, 0.04, "crossover", color=INK2, fontsize=7)
ax.set_xlabel("Months relative to crossover"); ax.set_ylabel("Share"); ax.set_ylim(0, 1.02); ax.set_xlim(-24, 36)
ax.legend(frameon=False, fontsize=7, loc="lower center", bbox_to_anchor=(0.5, 1.0), ncol=2, handlelength=1.8, columnspacing=1.0); fig.tight_layout(pad=0.3)
for ext in ("png", "pdf"): fig.savefig(f"figs/fig_aligned.{ext}", dpi=600)
# Fig: intervals (box plot, short two-line labels so the plot gets most of the width)
cols = [("app_to_order_mo", "Application\nto order"), ("order_to_cross_mo", "Order to\ncrossover"), ("overlap_mo", "Both names\n(\u00b112 mo)"),
        ("succ_first_before_cross_mo", "Successor\nearly"), ("pred_tail_mo", "Predecessor\nafter")]
fig, ax = plt.subplots(figsize=(3.5, 2.0))
data = [R.loc[F, c].dropna().values for c, _ in cols][::-1]
ax.boxplot(data, orientation="horizontal", widths=0.55, patch_artist=True, showfliers=True, whis=1.5,
           medianprops=dict(color=ORANGE, lw=1.6), boxprops=dict(facecolor="#cde2fb", edgecolor=BLUE, lw=0.9),
           whiskerprops=dict(color=BLUE, lw=0.9), capprops=dict(color=BLUE, lw=0.9),
           flierprops=dict(marker="o", markersize=3, markerfacecolor="white", markeredgecolor=BLUE, markeredgewidth=0.7))
ax.set_yticks(range(1, len(cols) + 1)); ax.set_yticklabels([f"{l} ({len(v)})" for (c, l), v in zip(cols[::-1], data)], fontsize=7, linespacing=1.0)
ax.set_xlabel("Months"); ax.set_xlim(-5, 72); ax.grid(axis="y", visible=False); fig.tight_layout(pad=0.25)
for ext in ("png", "pdf"): fig.savefig(f"figs/fig_intervals.{ext}", dpi=600)
# Fig 3: causes of predecessor-labelled records > 12 months after crossover
T = pd.read_csv("late_pred.csv"); T = T[T.id.isin(F)]
order = ["fitness-for-duty form", "plant document revision", "predecessor-only label", "co-tagged with successor", "residual financial role", "fleet letter (4+ dockets)"]
lab = {"fitness-for-duty form": "Fitness-for-duty form", "plant document revision": "Plant document revision", "predecessor-only label": "Other, predecessor only",
       "co-tagged with successor": "Co-tagged with successor", "residual financial role": "Residual financial role", "fleet letter (4+ dockets)": "Fleet letter (4+ dockets)"}
cnt = T.cat.value_counts().reindex(order).fillna(0); ev = T.groupby("cat").id.nunique().reindex(order).fillna(0)
fig, ax = plt.subplots(figsize=(3.5, 1.8))
y = np.arange(len(order))[::-1]
ax.barh(y, cnt.values, color=BLUE, height=0.6)
for yy, c, e in zip(y, cnt.values, ev.values): ax.text(c + 2, yy, f"{int(c)} ({int(e)} events)", va="center", fontsize=7, color="#0b0b0b")
ax.set_yticks(y); ax.set_yticklabels([lab[o] for o in order], fontsize=7); ax.set_xlabel("Documents"); ax.set_xlim(0, cnt.max() * 1.7); ax.grid(axis="y", visible=False)
fig.tight_layout(pad=0.3)
for ext in ("png", "pdf"): fig.savefig(f"figs/fig_causes.{ext}", dpi=600)
print("median successor share at -1,0,+1,+12:", [round(med[list(rel).index(k)], 2) for k in (-1, 0, 1, 12)], "both at 0:", round(both[24], 2), "both at +12:", round(both[36], 2), "both at -12", round(both[12],2))
print(len(T), T.id.nunique())
