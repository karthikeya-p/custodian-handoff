"""Step 1: learn how the API pages and check that each docket is the plant we think.
Run:  python3 probe.py > probe.txt"""
import csv, collections
from adams import search, docket

z = "05000295"
for q in ("", "*"):
    try:
        r = search(q, docket(z))
        print(f"q={q!r}: count={r.get('count')} page={len(r.get('results', []))}")
    except SystemExit as e:
        print(f"q={q!r}: {e}")
r = search("", docket(z))
n = r.get("count", 0)
for skip in (len(r["results"]), 1000, 5000, 10000, max(n - 5, 0)):
    try:
        p = search("", docket(z), skip=skip)
        print(f"skip={skip}: got {len(p.get('results', []))}")
    except SystemExit as e:
        print(f"skip={skip}: {e}")

print("\ndocket  plant  count  most frequent author affiliations | sample title")
for row in csv.DictReader(open("dockets.csv")):
    r = search("", docket(row["docket"]))
    docs = [x["document"] for x in r.get("results", [])]
    aff = collections.Counter(a for d in docs for a in d.get("AuthorAffiliation") or [])
    title = docs[0].get("DocumentTitle", "")[:70] if docs else ""
    print(row["docket"], row["plant"], r.get("count"), dict(aff.most_common(3)), "|", title)
