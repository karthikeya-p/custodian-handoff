"""Robustness of the crossover rule (Table VI) and medians by handoff type."""
import pandas as pd, numpy as np
M = pd.read_pickle("monthly.pkl"); C = pd.read_csv("curated.csv", dtype=str, keep_default_na=False).set_index("id")
R = pd.read_csv("event_metrics.csv").set_index("id"); F = [i for i in R.index if i not in ("X01", "E04", "E37")]
rows = []
for win in (1, 3, 6):
    for mn in (2, 3, 5):
        oc, ov, tail = [], [], []
        for i in F:
            g = M[i]; o = pd.Period(C.loc[i, "order_date"], "M")
            a = g.rolling(win).sum().loc[o - 6:]; cr = a[(a.S > a.P) & (a.S >= mn)]
            c = cr.index[0]; oc.append((c - o).n)
            both = g.loc[c - 12:c + 12]; ov.append(int(((both.P > 0) & (both.S > 0)).sum()))
            lp = g.loc[c:][g.loc[c:].P > 0].index; tail.append((lp[-1] - c).n if len(lp) else 0)
        rows.append({"window_months": win, "min_count": mn, "median_order_to_crossover": np.median(oc), "within_6_months": sum(-6 <= x <= 6 for x in oc),
                     "median_overlap": np.median(ov), "predecessor_after_24_months": sum(t >= 24 for t in tail)})
S = pd.DataFrame(rows); S.to_csv("sensitivity.csv", index=False); print(S.to_string(index=False))
K = R.loc[F].groupby("kind").agg(n=("order", "size"), order_to_crossover=("order_to_cross_mo", "median"), overlap=("overlap_mo", "median"),
                                 successor_early=("succ_first_before_cross_mo", "median"), predecessor_after=("pred_tail_mo", "median"))
K.to_csv("by_type.csv"); print(K)
