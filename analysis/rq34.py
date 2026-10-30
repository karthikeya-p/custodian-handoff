"""RQ2: classify predecessor-named submissions more than 12 months after the crossover."""
import pandas as pd, numpy as np, re
from load import isnrc
d = pd.read_pickle("docs.pkl"); D = d.set_index("AccessionNumber"); L = pd.read_pickle("lic.pkl")
C = pd.read_csv("curated.csv", dtype=str, keep_default_na=False); R = pd.read_csv("event_metrics.csv").set_index("id")
C = C[~C.id.isin(["X01"])]
FIN = r"trust|fund|financial|insurance|indemn|guarant|decommissioning cost|funding"
HEAR = r"exhibit|hearing|petition|board"
cats = []; late_all = []
for _, e in C.iterrows():
    c = pd.Period(R.loc[e.id, "cross"], "M"); dks = e.dockets.split(";")
    s = L[L.dockets.isin(dks)].copy(); s["m"] = s.date.dt.to_period("M")
    P = s[s.n.str.contains(e.pred)]
    late = P[(P.m >= c + 12) & (P.m <= c + 71)].AccessionNumber.unique()
    for a in late:
        x = D.loc[a]; x = x.iloc[0] if isinstance(x, pd.DataFrame) else x
        affs = [y for y in x.AuthorAffiliation.split(" | ") if y]
        nd = len([k for k in x.DocketNumber.split(" | ") if k.startswith("050")])
        tl = x.DocumentTitle.lower()
        from load import norm
        succ = any(re.search(e.succ, norm(y)) for y in affs)
        if succ: k = "co-tagged with successor"
        elif re.search(FIN, tl): k = "residual financial role"
        elif nd >= 4: k = "fleet letter (4+ dockets)"
        elif re.search(HEAR, tl): k = "litigation exhibit"
        else: k = "predecessor-only label"
        cats.append({"id": e.id, "acc": a, "cat": k, "year": x.date.year, "title": x.DocumentTitle[:110], "added": x.name})
T = pd.DataFrame(cats)
po = T.cat == "predecessor-only label"
ffd = T.title.str.contains(r"positive test|drug and alcohol|fitness.for.duty", case=False)
eng = T.title.str.contains(r"drawing|calc|procedure|epip|revision|rev\b|ufsar|fsar|report|manual|notebook", case=False)
T.loc[po & ffd, "cat"] = "fitness-for-duty form"; T.loc[po & ~ffd & eng, "cat"] = "plant document revision"
T.to_csv("late_pred.csv", index=False)
M = T[~T.id.isin(["E04", "E37"])]
print(M.cat.value_counts(), len(M), "documents in", M.id.nunique(), "forward handoffs")
