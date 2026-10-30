"""Step 3: merge raw/*.jsonl into one de-duplicated table, docs.csv.gz (one row per document).
Run:  python3 slim.py"""
import csv, glob, gzip, json

def j(v):
    return " | ".join(v) if isinstance(v, list) else (v or "")

COLS = ["AccessionNumber", "DocumentDate", "DateAdded", "DocumentType", "AuthorAffiliation",
        "AddresseeAffiliation", "DocketNumber", "LicenseNumber", "CaseReferenceNumber",
        "EstimatedPageCount", "DocumentTitle"]
seen, rows_in = set(), 0
with gzip.open("docs.csv.gz", "wt", newline="") as f:
    w = csv.writer(f); w.writerow(COLS)
    for path in sorted(glob.glob("raw/*.jsonl")):
        for line in open(path):
            rows_in += 1
            d = json.loads(line); acc = d.get("AccessionNumber")
            if not acc or acc in seen:
                continue
            seen.add(acc)
            w.writerow([j(d.get(c))[:400] if c == "DocumentTitle" else j(d.get(c)) for c in COLS])
print(f"read {rows_in:,} rows, wrote {len(seen):,} unique documents to docs.csv.gz")
