"""Shared helpers: docket names, affiliation normalization, NRC-author test, loading docs.csv.gz."""
import pandas as pd, re
P = {"05000295":"Zion 1","05000304":"Zion 2","05000409":"La Crosse","05000320":"Three Mile Island 2","05000289":"Three Mile Island 1","05000219":"Oyster Creek","05000003":"Indian Point 1","05000247":"Indian Point 2","05000286":"Indian Point 3","05000302":"Crystal River 3","05000305":"Kewaunee","05000244":"Ginna","05000220":"Nine Mile Point 1","05000410":"Nine Mile Point 2","05000245":"Millstone 1","05000336":"Millstone 2","05000423":"Millstone 3","05000443":"Seabrook","05000333":"FitzPatrick","05000461":"Clinton","05000331":"Duane Arnold","05000266":"Point Beach 1","05000301":"Point Beach 2","05000275":"Diablo Canyon 1","05000323":"Diablo Canyon 2","05000361":"San Onofre 2","05000362":"San Onofre 3","05000285":"Fort Calhoun"}
SUF = r"\b(CO|COMPANY|CORP|CORPORATION|INC|INCORPORATED|LLC|L L C|LP|L P|LTD|THE|OF)\b"
def norm(a):
    a = a.upper().replace("&", " AND ")
    a = re.sub(r"\(.*?\)", " ", a)
    a = re.sub(r"[^A-Z0-9 ]", " ", a)
    a = re.sub(SUF, " ", a)
    return re.sub(r"\s+", " ", a).strip()
def load():
    import os
    src = "docs.csv.xz" if os.path.exists("docs.csv.xz") else "docs.csv.gz"
    d = pd.read_csv(src, dtype=str, keep_default_na=False)
    d["date"] = pd.to_datetime(d.DocumentDate, errors="coerce")
    d["dockets"] = d.DocketNumber.str.split(r" \| ")
    d["auth"] = d.AuthorAffiliation.str.split(r" \| ")
    return d
def isnrc(a):
    u = a.upper()
    return u.startswith("NRC") or "NUCLEAR REGULATORY COMMISSION" in u or "ATOMIC ENERGY COMMISSION" in u or "(AEC)" in u
