"""Extract NRC transfer orders and licensee transfer applications per docket."""
import pandas as pd, re
from load import P, isnrc
d = pd.read_pickle("docs.pkl")
t = d.DocumentTitle.str.lower()
order = t.str.contains(r"order approving", regex=False) & t.str.contains("transfer|merger|restructur|holding company", regex=True)
noise = t.str.contains(r"application for|request for (?:an )?extension|extension of|supplement|request for additional|response to|exhibit|notification of significant|proposed issuance|forwards proposed|acceptance review|condition \(|easement|withdraw|correction|modifying order|modification of order|in response to|biweekly", regex=True)
nrc_auth = d.AuthorAffiliation.map(lambda a: any(isnrc(x) for x in a.split(" | ")) if a else False)
o = d[order & ~noise].copy()
def kind(s):
    s = s.lower()
    if re.search(r"indirect|merger|holding company|restructur|control", s): return "indirect"
    if re.search(r"operating authority|operations & maintenance|operations and maintenance", s): return "operator"
    if re.search(r"ownership interest|% |percent|interest in", s): return "share"
    return "direct"
o["kind"] = o.DocumentTitle.map(kind)
o["dk"] = o.DocketNumber.str.split(" | ", regex=False)
o = o.explode("dk"); o = o[o.dk.isin(P.keys())]
o = o.sort_values("date")
ev = []
for dk, g in o.groupby("dk"):
    cur = None
    for _, r in g.iterrows():
        if cur is not None and (r.date - cur["date"]).days <= 120:
            cur["docs"].append(r.AccessionNumber)
            if r.kind == "direct" and cur["kind"] != "direct" and cur["kind"] != "indirect": cur["kind"] = "direct"
            continue
        cur = {"dk": dk, "plant": P[dk], "date": r.date, "kind": r.kind, "title": r.DocumentTitle[:160], "docs": [r.AccessionNumber]}
        ev.append(cur)
E = pd.DataFrame(ev); E["ndocs"] = E.docs.map(len)
app = t.str.contains(r"application for (?:an )?order approving|application for (?:approval of )?(?:the )?(?:direct |indirect )?(?:license )?transfer|request for (?:approval of )?(?:the )?(?:direct |indirect )?(?:license )?transfer|application .*pursuant to 10 ?cfr ?50\.80", regex=True) & ~t.str.contains("supplement|request for additional|response to|acceptance|notice of|frn|federal register", regex=True)
A = d[app].copy(); A["dk"] = A.DocketNumber.str.split(" | ", regex=False)
A = A.explode("dk"); A = A[A.dk.isin(P.keys())]
E.to_pickle("orders.pkl"); A[["AccessionNumber","date","dk","DocumentTitle","AuthorAffiliation"]].to_pickle("apps.pkl")
print(E.groupby("kind").size()); print(len(E), "events;", len(A), "applications")
pd.set_option("display.width", 250); pd.set_option("display.max_colwidth", 110)
print(E[["plant","date","kind","ndocs","title"]].to_string())
