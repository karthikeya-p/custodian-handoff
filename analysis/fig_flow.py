"""Fig. 1: method flow, black-and-white block diagram drawn as vector shapes (8 pt Times, printed width 3.3 in)."""
import matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle, FancyArrowPatch
plt.rcParams.update({"font.family": "serif", "font.serif": ["Times New Roman", "Liberation Serif"], "font.size": 8})
W, H = 3.3, 4.25
fig, ax = plt.subplots(figsize=(W, H)); ax.set_xlim(0, 100); ax.set_ylim(0, 125); ax.axis("off")
fig.subplots_adjust(0.005, 0.005, 0.995, 0.995)
def box(x, y, w, h, title, sub=None):
    ax.add_patch(Rectangle((x, y), w, h, fc="white", ec="black", lw=0.8))
    if sub:
        ax.text(x + w / 2, y + h - 3.6, title, ha="center", va="center", fontweight="bold")
        ax.text(x + w / 2, y + (h - 6.5) / 2 + 0.4, sub, ha="center", va="center", linespacing=1.1)
    else:
        ax.text(x + w / 2, y + h / 2, title, ha="center", va="center", fontweight="bold")
def arrow(x1, y1, x2, y2):
    ax.add_patch(FancyArrowPatch((x1, y1), (x2, y2), arrowstyle="-|>", mutation_scale=7, lw=0.8, color="black", shrinkA=0, shrinkB=0))
def line(xs, ys): ax.plot(xs, ys, color="black", lw=0.8, solid_capstyle="butt")
box(6, 112, 88, 12, "NRC ADAMS public search API", "28 dockets: 23 with transfers, 5 controls")
arrow(50, 112, 50, 108)
box(6, 96, 88, 12, "Collection and de-duplication", "1,072,607 entries → 722,497 documents")
line([50, 50], [96, 93]); line([25, 75], [93, 93]); arrow(25, 93, 25, 90); arrow(75, 93, 75, 90)
box(1, 71, 48, 19, "Licensee-side\nsubmissions", "to the NRC, non-NRC\nauthor, names normalized:\n247,184")
box(51, 78, 48, 12, "NRC order search", "113 order clusters")
arrow(75, 78, 75, 74)
box(51, 62, 48, 12, "Manual curation", "38 handoff events")
line([25, 25], [71, 58]); line([75, 75], [62, 58]); line([25, 75], [58, 58]); arrow(50, 58, 50, 55)
box(6, 43, 88, 12, "Monthly author series", "predecessor vs. successor names")
line([50, 50], [43, 40]); line([13.25, 86.75], [40, 40])
xs = [13.25, 37.75, 62.25, 86.75]
for x in xs: arrow(x, 40, x, 37)
for x, (t, s) in zip(xs, [("Timing", "application,\norder,\ncrossover"), ("Boundary", "overlap,\nearly and\nlate names"),
                          ("Re-filing", "program\ncategories"), ("Chain", "rebuild from\nauthor\nlabels")]):
    box(x - 11.75, 20, 23.5, 17, t, s)
for x in xs: line([x, x], [20, 15.5])
line([13.25, 86.75], [15.5, 15.5]); arrow(50, 15.5, 50, 12)
box(6, 1, 88, 11, "Discontinuities and requirements")
for e in ("pdf", "svg"): fig.savefig(f"figs/fig_flow.{e}")
fig.savefig("figs/fig_flow.png", dpi=600)
