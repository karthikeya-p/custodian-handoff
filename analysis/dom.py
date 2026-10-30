"""Dominant licensee label per docket-quarter: most frequent non-NRC author among documents addressed to the NRC."""
import pandas as pd, re
from load import P, isnrc, norm
d = pd.read_pickle("docs.pkl")
to_nrc = d.AddresseeAffiliation.map(lambda a: any(isnrc(x) for x in a.split(" | ")) if a else False)
GEN = re.compile(r"NO KNOWN|NOT ASSIGNED|PUBLIC COMMENT|^INDIVIDUAL|LLP\b|LAW|ATTORNEY|CONGRESS|SENATE|HOUSE OF REP|STATE OF|COUNTY|CITY OF|DEPT|DEPARTMENT|UNIVERSITY|LABORATORY|^$")
L = pd.read_pickle("long.pkl")
L = L[~L.nrc & L.AccessionNumber.isin(set(d.AccessionNumber[to_nrc]))]
L = L[~L.n.str.contains(GEN)]
L["q"] = L.date.dt.to_period("Q")
L = L[L.date >= "1975-01-01"]
L.to_pickle("lic.pkl")
c = L.groupby(["dockets", "q", "n"]).size().rename("k").reset_index()
tot = c.groupby(["dockets", "q"]).k.transform("sum")
c["share"] = c.k / tot
top = c.sort_values("k", ascending=False).drop_duplicates(["dockets", "q"]).sort_values(["dockets", "q"])
top.to_pickle("dom.pkl")
for dk in ["05000301", "05000219", "05000302"]:
    s = top[top.dockets == dk]
    s = s[s.n != s.n.shift()]
    print("==", P[dk]); print(s[["q", "n", "k", "share"]].to_string(index=False))
