# Phase E Checklist

## Roadmap Activity Coverage

- [x] Build evaluation corpus and relevance judgments workflow.
- [x] Compute effectiveness metrics: Recall, Precision, MAP/NDCG, top-k quality.
- [x] Add efficiency checks: indexing time, latency, throughput.
- [x] Add tuning and significance-check script.

## Validation Steps

- [ ] `build_eval_corpus.py` generates `eval_queries.json` and `qrels_template.csv`.
- [ ] Annotated `qrels.csv` exists with relevance labels.
- [ ] `evaluate_metrics.py` writes an effectiveness report JSON.
- [ ] `efficiency_benchmark.py` writes an efficiency report JSON.
- [ ] `tune_significance.py` writes a tuning/significance report JSON.
- [ ] Phase E reports reviewed and committed.
