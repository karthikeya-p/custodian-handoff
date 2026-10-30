"""Fig. 1: method flow, black-and-white block diagram drawn as vector shapes."""
import matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle, FancyArrowPatch
plt.rcParams.update({"font.family": "serif", "font.serif": ["Times New Roman", "Liberation Serif"], "font.size": 6.8})
fig, ax = plt.subplots(figsize=(3.45, 3.6)); ax.set_xlim(0, 100); ax.set_ylim(0, 104); ax.axis("off")
fig.subplots_adjust(0.01, 0.01, 0.99, 0.99)
def box(x, y, w, h, title, sub=None):
    ax.add_patch(Rectangle((x, y), w, h, fc="white", ec="black", lw=0.8))
    if sub:
        ax.text(x + w / 2, y + h - 3.2, title, ha="center", va="center", fontweight="bold")
        ax.text(x + w / 2, y + (h - 5.5) / 2 + 0.6, sub, ha="center", va="center", linespacing=1.15)
    else:
        ax.text(x + w / 2, y + h / 2, title, ha="center", va="center", fontweight="bold")
def arrow(x1, y1, x2, y2):
    ax.add_patch(FancyArrowPatch((x1, y1), (x2, y2), arrowstyle="-|>", mutation_scale=7, lw=0.8, color="black", shrinkA=0, shrinkB=0))
def line(xs, ys): ax.plot(xs, ys, color="black", lw=0.8, solid_capstyle="butt")
box(12, 93, 76, 10, "NRC ADAMS public search API", "28 reactor dockets: 23 with transfers, 5 controls")
arrow(50, 93, 50, 89)
box(12, 79, 76, 10, "Collection and de-duplication", "1,072,607 docket entries → 722,497 documents")
line([50, 50], [79, 76]); line([25, 75], [76, 76]); arrow(25, 76, 25, 73); arrow(75, 76, 75, 73)
box(2, 58, 46, 15, "Licensee-side submissions", "addressed to the NRC, non-NRC author,\nnames normalized: 247,184")
box(52, 63, 46, 10, "Title search for NRC orders", "113 transfer-order clusters")
arrow(75, 63, 75, 59)
box(52, 49, 46, 10, "Manual curation", "38 events, each tied to an order")
line([25, 25], [58, 46]); line([75, 75], [49, 46]); line([25, 75], [46, 46]); arrow(50, 46, 50, 43)
box(12, 33, 76, 10, "Per-event monthly author series", "predecessor-named vs. successor-named")
line([50, 50], [33, 30]); line([13.25, 86.75], [30, 30])
xs = [13.25, 37.75, 62.25, 86.75]
for x in xs: arrow(x, 30, x, 27)
for x, (t, s) in zip(xs, [("Timing", "application, order,\ncrossover"), ("Boundary", "overlap, early and\nlingering names"),
                          ("Re-filing", "program\ncategories"), ("Chain", "rebuild from\nauthor labels")]):
    box(x - 11.25, 15, 22.5, 12, t, s)
for x in xs: line([x, x], [15, 11.5])
line([13.25, 86.75], [11.5, 11.5]); arrow(50, 11.5, 50, 8.5)
box(12, 1, 76, 7.5, "Taxonomy of discontinuities and requirements")
for e in ("pdf", "svg"): fig.savefig(f"figs/fig_flow.{e}")
fig.savefig("figs/fig_flow.png", dpi=600)
