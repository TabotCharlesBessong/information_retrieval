# Phase D Implementation Guide

This phase extends search usability and retrieval options beyond the Phase C baseline.

## 1. Query transformation and refinement

Implemented in `app/api/src/search_backend.py` and surfaced by `app/api/src/main.py`.

Capabilities:
1. Query normalization (`normalized_query`).
2. Spelling correction suggestion for common domain terms (`suggested_query`).
3. Synonym-based expansion (`expanded_terms`, `refined_query`).
4. Suggestions endpoint (`GET /search/suggest?q=...`).

## 2. Phrase queries, filters, and faceting

Implemented in `GET /search` with additional parameters:

1. `phrase`: Enforces phrase matching on title/body/cleaned_text.
2. `source`: Multi-value filter by source name.
3. `published_from`, `published_to`: Date filtering over `published_at`.
4. `facets`: Enables source facet counts in response.

Response additions:
1. `facets.sources`: Source distribution of matched documents.
2. Query refinement metadata (`normalized_query`, `suggested_query`, `expanded_terms`).

## 3. Probabilistic retrieval variant

Mode `probabilistic` added to `GET /search`.

Behavior:
1. SQLite backend: smoothed term-likelihood style score computed from term frequency and document length.
2. Elasticsearch backend: candidate retrieval plus probabilistic-style client-side re-scoring.

This provides a distinct ranking variant for comparison against BM25 and Boolean.

## 4. Retrieval model comparison output

Updated script: `app/api/src/benchmark_retrieval.py`.

Now benchmarks:
1. `bm25`
2. `boolean`
3. `probabilistic`

Outputs:
1. `benchmark_results_<timestamp>.json`
2. `benchmark_comparison_<timestamp>.json` with overlap metrics vs BM25.

## 5. Quick usage examples

```bash
curl "http://localhost:8000/search?q=african fintech fundraise&mode=probabilistic"
curl "http://localhost:8000/search?q=african startup\" &phrase=mobile%20payments&source=TechCabal&facets=true"
curl "http://localhost:8000/search/suggest?q=fintch"
```
