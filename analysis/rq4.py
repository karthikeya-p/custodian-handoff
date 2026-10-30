"""RQ4: rebuilding the licensee chain from author labels; indirect transfers; unaffiliated share (Table IV)."""
import pandas as pd, numpy as np, re
L = pd.read_pickle("lic.pkl"); E = pd.read_pickle("orders.pkl")
C = pd.read_csv("curated.csv", dtype=str, keep_default_na=False); C = C[C.id != "X01"]
SITES = {}
for _, e in C.iterrows(): SITES.setdefault(e.site.split(" 1-")[0].replace("Indian Point 3", "Indian Point"), set()).update(e.dockets.split(";"))
SITES["Indian Point"] = {"05000003", "05000247", "05000286"}; SITES.pop("Indian Point 1-2", None)
CTRL = {"Diablo Canyon": {"05000275", "05000323"}, "San Onofre": {"05000361", "05000362"}, "Fort Calhoun": {"05000285"}}
def changes(dks, fam=None, start="1997-01-01"):
    s = L[L.dockets.isin(dks) & (L.date >= start)].drop_duplicates(["AccessionNumber", "n"]).copy()
    if fam is not None:
        s["n"] = s.n.map(fam)
    s["q"] = s.date.dt.to_period("Q")
    top = s.groupby(["q", "n"]).size().rename("k").reset_index().sort_values("k", ascending=False).drop_duplicates("q").set_index("q").sort_index().n
    top = top.reindex(pd.period_range(top.index.min(), top.index.max(), freq="Q")).ffill()
    # persistent label: must hold >= 2 consecutive quarters
    lab, out, prev = None, [], None
    vals = top.tolist(); idx = top.index
    for i in range(len(vals) - 1):
        v = vals[i]
        if v != lab and vals[i + 1] == v:
            if lab is not None: out.append((idx[i], lab, v))
            lab = v
    return out
FAM = [(r"EXELON|AMERGEN", "Exelon group"), (r"CONSTELLATION|EDF|R E GINNA|NINE MILE POINT NUCLEAR", "Constellation group"), (r"ENTERGY", "Entergy"), (r"HOLTEC", "Holtec"),
       (r"ENERGYSOLUTIONS|ZIONSOLUTIONS|LACROSSESOLUTIONS|TMI 2 SOLUTIONS|KEWAUNEE SOLUTIONS", "EnergySolutions group"), (r"DOMINION|VIRGINIA ELECTRIC", "Dominion"),
       (r"FPL|FLORIDA POWER AND LIGHT|NEXTERA", "NextEra group"), (r"NUCLEAR MANAGEMENT", "NMC"), (r"DUKE ENERGY|PROGRESS ENERGY|FLORIDA POWER$|FLORIDA POWER CORP", "Duke group"),
       (r"GPU|GENERAL PUBLIC UTILITIES|METROPOLITAN EDISON|JERSEY CENTRAL|FIRSTENERGY", "GPU/FirstEnergy"), (r"COMMONWEALTH EDISON|COMED", "ComEd"), (r"CONSOLIDATED EDISON", "Con Edison"),
       (r"POWER AUTHORITY", "NYPA"), (r"NIAGARA MOHAWK", "Niagara Mohawk"), (r"ROCHESTER GAS", "RG&E"), (r"NORTHEAST NUCLEAR|NORTHEAST UTILITIES", "Northeast Utilities"),
       (r"NORTH ATLANTIC ENERGY", "North Atlantic"), (r"ILLINOIS POWER", "Illinois Power"), (r"IES UTILITIES|IOWA ELECTRIC|ALLIANT|INTERSTATE POWER", "Alliant"),
       (r"WISCONSIN ELECTRIC", "Wisconsin Electric"), (r"WISCONSIN PUBLIC SERVICE", "WPS"), (r"DAIRYLAND", "Dairyland"), (r"ADP CR3|ACCELERATED DECOMMISSIONING", "ADP"),
       (r"PACIFIC GAS", "PG&E"), (r"SOUTHERN CALIFORNIA EDISON", "SCE"), (r"OMAHA PUBLIC POWER", "OPPD")]
def fam(n):
    for rx, f in FAM:
        if re.search(rx, n): return f
    return "other:" + n
res = []
for site, dks in {**SITES, **CTRL}.items():
    ev = C[C.dockets.str.split(";").map(lambda x: bool(set(x) & dks))]
    truth = sorted({pd.Period(o, "Q") for o in ev.order_date if o >= "1997-01-01"})
    for mode, f in (("raw", None), ("family", fam)):
        ch = changes(dks, f)
        hit = sum(any(abs((q - t).n) <= 4 for q, _, _ in ch) for t in truth)
        spurious = sum(not any(abs((q - t).n) <= 4 for t in truth) for q, _, _ in ch)
        res.append({"site": site, "mode": mode, "true": len(truth), "label_changes": len(ch), "detected": hit, "spurious": spurious})
X = pd.DataFrame(res); X.to_csv("rq4_detect.csv", index=False)
for m, g in X.groupby("mode"):
    print(m, "true", g.true.sum(), "changes", g.label_changes.sum(), "recall", round(g.detected.sum() / g.true.sum(), 2), "precision", round(1 - g.spurious.sum() / g.label_changes.sum(), 2), "spurious", g.spurious.sum())
print(X.to_string(index=False))
# indirect orders visibility
I = E[E.kind == "indirect"]
vis = 0; rows = []
for _, r in I.iterrows():
    site = next((s for s, dk in {**SITES, **CTRL}.items() if r.dk in dk), None)
    ch = changes({r.dk}, None, "1990-01-01"); q = pd.Period(r.date, "Q")
    v = any(abs((c - q).n) <= 4 for c, _, _ in ch)
    rows.append(v)
print("indirect order clusters", len(I), "with a raw label change within 1 year:", sum(rows))
# unaffiliated share by period among licensee-side docs addressed to NRC
d = pd.read_pickle("docs.pkl")
from load import isnrc, P
to_nrc = d.AddresseeAffiliation.map(lambda a: any(isnrc(x) for x in a.split(" | ")) if a else False)
dd = d[to_nrc].copy(); dd["un"] = dd.AuthorAffiliation.str.upper().str.contains("NO KNOWN|NOT ASSIGNED") | (dd.AuthorAffiliation == "")
dd["nrcauth"] = dd.AuthorAffiliation.map(lambda a: bool(a) and all(isnrc(x) for x in a.split(" | ")))
dd = dd[~dd.nrcauth]
dd["era"] = pd.cut(dd.date.dt.year, [1900, 1999, 2009, 2019, 2026], labels=["<=1999", "2000-09", "2010-19", "2020-26"])
print(dd.groupby("era", observed=True).un.agg(["mean", "size"]))
