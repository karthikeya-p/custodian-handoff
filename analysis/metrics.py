"""Per-event handoff measurements from licensee-side documents addressed to the NRC."""
import pandas as pd, numpy as np, re
from load import isnrc
d = pd.read_pickle("docs.pkl"); L = pd.read_pickle("lic.pkl")
C = pd.read_csv("curated.csv", dtype=str, keep_default_na=False); C["order"] = pd.to_datetime(C.order_date)
t = d.set_index("AccessionNumber").DocumentTitle.str.lower()
APP = re.compile(r"application for (?:an )?order approving|application for (?:approval of )?(?:the )?(?:direct |indirect )?(?:license )?transfer|request for (?:approval of )?(?:the )?(?:direct |indirect )?(?:license )?transfer|application .*50\.80|application .*transfer of (?:the )?(?:facility )?(?:operating )?licen")
rows, monthly = [], {}
for _, e in C.iterrows():
    dks = e.dockets.split(";")
    s = L[L.dockets.isin(dks)].drop_duplicates(["AccessionNumber", "n"]).copy()
    s["m"] = s.date.dt.to_period("M")
    s["P"] = s.n.str.contains(e.pred); s["S"] = s.n.str.contains(e.succ) & ~s.P
    doc = s.groupby("AccessionNumber").agg(m=("m", "first"), P=("P", "any"), S=("S", "any"))
    o = e.order.to_period("M")
    rng = pd.period_range(o - 60, o + 72, freq="M")
    g = doc.groupby("m").agg(P=("P", "sum"), S=("S", "sum"), N=("P", "size")).reindex(rng, fill_value=0)
    monthly[e.id] = g
    roll = g.rolling(3).sum()
    after = roll.loc[o - 6:]
    cross = after[(after.S > after.P) & (after.S >= 3)]
    c = cross.index[0] if len(cross) else None
    r = {"id": e.id, "site": e.site, "kind": e.kind, "order": e.order.date()}
    r["app"] = e.app_date or None
    r["app_to_order_mo"] = round((e.order - pd.Timestamp(e.app_date)).days / 30.44, 1) if e.app_date else np.nan
    if c is None:
        r.update(cross=None, order_to_cross_mo=np.nan); rows.append(r); continue
    r["cross"] = str(c); r["order_to_cross_mo"] = (c - o).n
    w = g.loc[c:c + 11]
    r["pred_share_y1"] = round(w.P.sum() / max(w.P.sum() + w.S.sum(), 1), 3)
    late = g.loc[c + 12:c + 71]
    r["pred_docs_after_y1"] = int(late.P.sum())
    lastp = g.loc[c:][g.loc[c:].P > 0].index
    r["pred_tail_mo"] = (lastp[-1] - c).n if len(lastp) else 0
    both = g.loc[c - 12:c + 12]; r["overlap_mo"] = int(((both.P > 0) & (both.S > 0)).sum())
    firsts = g[g.S > 0].index; r["succ_first_before_cross_mo"] = (c - firsts[0]).n if len(firsts) else np.nan
    win = g.loc[c - 12:c + 12].N; base = g.loc[o - 60:o - 25].N
    r["base_med"] = float(base.median()); r["min3_near"] = float(win.rolling(3).mean().min())
    r["zero_months_near"] = int((win == 0).sum()); r["zero_months_base_per25"] = round((base == 0).mean() * 25, 1)
    r["succ_variants_24mo"] = int(s[(s.m >= c) & (s.m <= c + 23) & s.S].n.nunique())
    r["pred_variants_24mo_before"] = int(s[(s.m >= o - 24) & (s.m < o) & s.P].n.nunique())
    rows.append(r)
R = pd.DataFrame(rows); R.to_csv("event_metrics.csv", index=False)
pd.to_pickle(monthly, "monthly.pkl")
pd.set_option("display.width", 250)
print(R.to_string())
