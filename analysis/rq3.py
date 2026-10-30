"""RQ3: successor submissions by program category, first year vs months 25-48 (Table III)."""
import pandas as pd, numpy as np, re
d = pd.read_pickle("docs.pkl"); L = pd.read_pickle("lic.pkl")
C = pd.read_csv("curated.csv", dtype=str, keep_default_na=False); R = pd.read_csv("event_metrics.csv").set_index("id")
C = C[~C.id.isin(["X01", "E04", "E37"])]
title = d.set_index("AccessionNumber").DocumentTitle.str.lower()
title = title[~title.index.duplicated()]
CAT = {
 "Quality assurance program": r"quality assurance",
 "Emergency plan": r"emergency plan|epip|emergency response",
 "Security plan": r"security plan|physical security|safeguards contingency|cyber security",
 "Financial assurance": r"decommissioning (?:funding|trust|fund)|financial assurance|nuclear property insurance|insurance|indemnity|guarantee|price-anderson",
 "Identity/organization": r"name change|change of name|change in name|organization|signature authority|letterhead|corporate|management change|officer",
 "Licensing basis (UFSAR/TS bases)": r"ufsar|updated final safety analysis|fsar|technical specification bases|ts bases",
}
rows = []
for _, e in C.iterrows():
    c = pd.Period(R.loc[e.id, "cross"], "M"); o = pd.Period(e.order_date, "M")
    s = L[L.dockets.isin(e.dockets.split(";"))].copy(); s["m"] = s.date.dt.to_period("M")
    S = s[s.n.str.contains(e.succ)].drop_duplicates("AccessionNumber")
    P = s[s.n.str.contains(e.pred)].drop_duplicates("AccessionNumber")
    w1 = S[(S.m >= c) & (S.m <= c + 11)]; w3 = S[(S.m >= c + 24) & (S.m <= c + 47)]
    wb = P[(P.m >= o - 48) & (P.m <= o - 25)]
    for k, rx in CAT.items():
        f = lambda w: int(title.reindex(w.AccessionNumber).str.contains(rx, na=False).sum())
        rows.append({"id": e.id, "cat": k, "y1": f(w1), "ss": f(w3), "base": f(wb), "n_y1": len(w1), "n_ss": len(w3), "n_base": len(wb)})
    rows.append({"id": e.id, "cat": "All licensee documents", "y1": len(w1), "ss": len(w3), "base": len(wb), "n_y1": len(w1), "n_ss": len(w3), "n_base": len(wb)})
X = pd.DataFrame(rows)
out = []
for k, g in X.groupby("cat", sort=False):
    y1 = g.y1.sum() / 12; ss = g.ss.sum() / 24; b = g.base.sum() / 24
    up = ((g.y1 / 12) > (g.ss / 24)).sum(); ne = ((g.y1 > 0) | (g.ss > 0)).sum()
    out.append({"category": k, "events_with_any": int(((g.y1 + g.ss + g.base) > 0).sum()), "y1_per_mo": round(y1, 2), "steady_per_mo": round(ss, 2), "pre_per_mo": round(b, 2), "ratio_y1_vs_steady": round(y1 / ss, 2) if ss else np.nan, "events_y1_higher": f"{up}/{ne}"})
O = pd.DataFrame(out); O.to_csv("rq3.csv", index=False); print(O.to_string(index=False)); print(C.shape[0], "events")
