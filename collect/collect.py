"""Step 2: pull every document's metadata for each docket into raw/<docket>.jsonl.
Fetches several pages at once (WORKERS). Resumable: finished pages are listed in raw/<docket>.pages.
Run:  caffeinate -i python3 collect.py      (re-run the same command to continue after a stop)"""
import csv, json, os, sys, time
from concurrent.futures import ThreadPoolExecutor, as_completed
from adams import search, docket

WORKERS = int(os.environ.get("WORKERS", "6"))
KEEP = ["AccessionNumber", "DocumentDate", "DateAdded", "DocumentTitle", "DocumentType",
        "AuthorName", "AuthorAffiliation", "AddresseeName", "AddresseeAffiliation",
        "DocketNumber", "LicenseNumber", "CaseReferenceNumber", "Keyword",
        "DocumentReportNumber", "EstimatedPageCount", "Availability"]
os.makedirs("raw", exist_ok=True)
log = csv.writer(open("collect_log.csv", "a", newline=""))
start = time.time(); fetched = 0

for row in csv.DictReader(open("dockets.csv")):
    d = row["docket"]; path = f"raw/{d}.jsonl"; pages_path = f"raw/{d}.pages"
    seen = {json.loads(l)["AccessionNumber"] for l in open(path)} if os.path.exists(path) else set()
    done = {int(x) for x in open(pages_path)} if os.path.exists(pages_path) else set()
    total = search("", docket(d)).get("count", 0)
    todo = [s for s in range(0, total, 100) if s not in done]
    if not todo:
        print(f"{d} {row['plant']}: done ({len(seen)}/{total})"); continue
    out, pg = open(path, "a"), open(pages_path, "a")
    with ThreadPoolExecutor(WORKERS) as ex:
        futs = {ex.submit(search, "", docket(d), s): s for s in todo}
        for f in as_completed(futs):
            for x in f.result().get("results", []):
                doc = x["document"]; acc = doc.get("AccessionNumber")
                if acc in seen:
                    continue
                seen.add(acc)
                out.write(json.dumps({k: doc.get(k) for k in KEEP}) + "\n")
            out.flush(); pg.write(f"{futs[f]}\n"); pg.flush()
            fetched += 100
            rate = fetched / max(time.time() - start, 1) * 60
            print(f"\r{d} {row['plant']}: {len(seen)}/{total}   ({rate:,.0f} records/min)", end="", flush=True)
    out.close(); pg.close(); print()
    log.writerow([d, row["plant"], total, len(seen), time.strftime("%Y-%m-%d %H:%M")])
    if len(seen) < total * 0.995:
        print(f"  NOTE: {len(seen)} of {total} unique; send me collect_log.csv")
