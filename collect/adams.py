"""Small client for the NRC ADAMS Public Search API (key in the ADAMS_KEY environment variable)."""
import json, os, sys, time, urllib.request, urllib.error

URL = "https://adams-api.nrc.gov/aps/api/search"

def search(q="", filters=None, skip=0, tries=5):
    key = os.environ.get("ADAMS_KEY")
    if not key:
        sys.exit("Set the key first:  read -s ADAMS_KEY; export ADAMS_KEY")
    body = json.dumps({"q": q, "filters": filters or [], "anyFilters": [], "skip": skip}).encode()
    for i in range(tries):
        req = urllib.request.Request(URL, data=body, method="POST", headers={
            "Ocp-Apim-Subscription-Key": key, "Content-Type": "application/json"})
        try:
            with urllib.request.urlopen(req, timeout=60) as r:
                return json.load(r)
        except urllib.error.HTTPError as e:
            msg = e.read().decode(errors="replace")[:300]
            if e.code in (429, 500, 502, 503, 504) and i < tries - 1:
                time.sleep(2 ** i * 2); continue
            sys.exit(f"HTTP {e.code}: {msg}")
        except (urllib.error.URLError, TimeoutError) as e:
            if i < tries - 1:
                time.sleep(2 ** i * 2); continue
            sys.exit(f"network error: {e}")

def docket(d):
    return [{"field": "DocketNumber", "value": d, "operator": "equals"}]
