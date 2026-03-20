# Phase E Implementation Guide

This phase makes retrieval quality measurable and adds repeatable tuning and performance checks.

## 1. Build evaluation corpus and relevance judgments

Script: `app/api/src/build_eval_corpus.py`

What it does:
1. Writes evaluation queries to `docs/phase-e/eval_queries.json`.
2. Pools top results from BM25, Boolean, and Probabilistic modes.
3. Writes candidate judgment rows to `docs/phase-e/qrels_template.csv`.

How to use:
1. Run the script.
2. Copy `qrels_template.csv` to `qrels.csv`.
3. Fill `relevance` values manually (e.g., 0, 1, 2).

## 2. Compute effectiveness metrics

Script: `app/api/src/evaluate_metrics.py`

Inputs:
1. `docs/phase-e/eval_queries.json`
2. `docs/phase-e/qrels.csv`

Outputs:
1. `docs/phase-e/effectiveness_report_<timestamp>.json`

Reported metrics (aggregate and per-query):
1. Precision@5, Precision@10
2. Recall@5, Recall@10
3. MAP@10
4. NDCG@10
5. MRR@10
6. Hits@10 (top-k quality indicator)

## 3. Efficiency checks

Script: `app/api/src/efficiency_benchmark.py`

What it measures:
1. Query latency (avg/p95/min/max by mode)
2. Throughput (queries per second)
3. Indexing time and docs/sec in Elasticsearch mode (or skip notice in SQLite mode)

Output:
1. `docs/phase-e/efficiency_report_<timestamp>.json`

## 4. Tuning and significance checks

Script: `app/api/src/tune_significance.py`

What it does:
1. Loads the latest effectiveness report.
2. Ranks retrieval modes by NDCG@10 then MAP@10.
3. Runs paired randomization significance test for Probabilistic vs BM25 on NDCG@10.

Output:
1. `docs/phase-e/tuning_significance_<timestamp>.json`

## 5. Recommended run order

```bash
python app/api/src/build_eval_corpus.py
# copy docs/phase-e/qrels_template.csv -> docs/phase-e/qrels.csv and annotate relevance
python app/api/src/evaluate_metrics.py
python app/api/src/efficiency_benchmark.py
python app/api/src/tune_significance.py
```
