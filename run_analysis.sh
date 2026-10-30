#!/usr/bin/env bash
# Reproduce every number, table and figure of the paper from data/docs.csv.xz and data/curated.csv.
# Usage: bash run_analysis.sh        (about 3 minutes, 8 GB RAM recommended)
set -euo pipefail
ROOT="$(cd "$(dirname "$0")" && pwd)"
W="$ROOT/work"; mkdir -p "$W/figs"; cd "$W"
ln -sf "$ROOT/data/docs.csv.xz" docs.csv.xz
cp "$ROOT/data/curated.csv" curated.csv
export PYTHONPATH="$ROOT/analysis"
run() { echo "== $1"; python3 "$ROOT/analysis/$1" > "log_${1%.py}.txt"; tail -n 12 "log_${1%.py}.txt"; }
run build.py; run events.py; run dom.py; run metrics.py; run rq34.py; run rq3.py; run rq4.py; run sensitivity.py; run figs.py; run fig_kew.py; run fig_flow.py
mkdir -p "$ROOT/results/figures"
cp event_metrics.csv late_pred.csv rq3.csv rq4_detect.csv sensitivity.csv by_type.csv "$ROOT/results/"
cp figs/* "$ROOT/results/figures/"
echo "Done: results/ updated."
