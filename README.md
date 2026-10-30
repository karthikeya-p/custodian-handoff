# Custodian handoffs in the U.S. NRC public record

Code and data for the paper *When the Custodian Changes: Measuring Record Attribution Across U.S. Nuclear License Transfers*.

The study measures how 37 changes of licensee at 15 U.S. nuclear sites (orders 1999–2022), plus one approved transfer that never closed, appear in the metadata of the NRC's public document library (ADAMS).

## Contents

```
collect/            collection from the ADAMS public search API
  dockets.csv         the 28 dockets (23 with transfers, 5 controls)
  adams.py            API client (key in the ADAMS_KEY environment variable)
  probe.py            checks paging and docket identity
  collect.py          full pull into raw/<docket>.jsonl (6 parallel requests, resumable)
  slim.py             merges raw/ into one de-duplicated table, docs.csv.gz
data/
  docs.csv.xz         722,497 document records (metadata only), pulled October 2026
  curated.csv         the 38 curated licensee changes, each with the NRC order's accession number
analysis/           every number, table and figure of the paper
run_analysis.sh     runs the whole analysis (about 3 minutes; 8 GB RAM recommended)
results/            outputs of run_analysis.sh: per-event measures, tables and figures
```

## Reproduce the paper

```bash
git clone https://github.com/Karthikeyap-dev/custodian-handoff.git && cd custodian-handoff
pip install -r requirements.txt
bash run_analysis.sh
```

| Paper item | Script | Output |
|---|---|---|
| Fig. 1, method | `fig_flow.py` | `results/figures/fig_flow.*` |
| Table I, dataset counts | `build.py`, `events.py` | `work/log_build.txt`, `work/log_events.txt` |
| Table II, events | `data/curated.csv` | — |
| Fig. 2, Kewaunee example | `fig_kew.py` | `results/figures/fig_kewaunee.*` |
| Timing and boundary, Figs. 3–4 | `metrics.py`, `figs.py` | `results/event_metrics.csv` |
| Fig. 5 | `rq34.py`, `figs.py` | `results/late_pred.csv` |
| Table III, re-filing | `rq3.py` | `results/rq3.csv` |
| Table IV, rebuilding the chain | `rq4.py` | `results/rq4_detect.csv`, `work/log_rq4.txt` |
| Table VI and by-type medians | `sensitivity.py` | `results/sensitivity.csv`, `results/by_type.csv` |

## Collect the data again

Get a free key from the [ADAMS API developer portal](https://adams-api-developer.nrc.gov/) (subscribe to *ADAMS Public Search API*). Then:

```bash
cd collect
read -s ADAMS_KEY; export ADAMS_KEY      # paste the key; it is not shown or saved
python3 probe.py                          # about 35 requests
python3 collect.py                        # about 1.1 million records, about 70 minutes
python3 slim.py                           # writes docs.csv.gz
```

The library changes over time, so a new pull will differ slightly from `data/docs.csv.xz`. `load.py` reads `docs.csv.xz` or `docs.csv.gz`.

## `data/curated.csv`

| Column | Meaning |
|---|---|
| `id` | E01–E37: licensee changes; X01: approved, never closed |
| `site`, `dockets` | site and NRC docket numbers (semicolon-separated) |
| `order_date`, `accession` | date and ADAMS accession number of the NRC order |
| `kind` | owner+operator, operator, intra-group, corporate separation, control, return to owner, approved not consummated |
| `pred`, `succ` | regular expressions on normalized author names for the predecessor and successor |
| `app_accession`, `app_date` | transfer application, where one could be identified |

## License

Code: MIT (see `LICENSE`). The ADAMS metadata in `data/docs.csv.xz` is a public record of the U.S. Nuclear Regulatory Commission. `data/curated.csv` and `results/` are released under CC BY 4.0.

## Citation

See `CITATION.cff`. Archived on Zenodo: doi:10.5281/zenodo.XXXXXXX
