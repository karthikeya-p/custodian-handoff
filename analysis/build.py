"""Step 1: build the docket-author table (docs.pkl, long.pkl) from data/docs.csv.xz."""
from load import *
d = load()
d[["AccessionNumber","date","DocumentType","AuthorAffiliation","AddresseeAffiliation","CaseReferenceNumber","LicenseNumber","EstimatedPageCount","DocumentTitle","DocketNumber"]].to_pickle("docs.pkl")
e = d[["AccessionNumber","date","dockets","auth"]].explode("dockets")
e = e[e.dockets.isin(P.keys())].explode("auth")
e = e[e.auth != ""]
e["nrc"] = e.auth.map(isnrc); e["n"] = e.auth.map(norm)
e.to_pickle("long.pkl"); print(len(e), e.nrc.mean())
