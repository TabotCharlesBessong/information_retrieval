# Phase C Implementation Guide

This phase delivers indexing and baseline ranking with a complete query loop.

## 1. Inverted index and query-processing path

Script: app/pipeline/src/index_documents.py

Actions:
1. Ensures Elasticsearch index exists with baseline mapping.
2. Loads parsed documents from PostgreSQL.
3. Bulk-indexes documents into Elasticsearch.

## 2. Baseline retrieval models

API supports two modes through query parameter `mode`:

1. bm25
- Multi-match ranking over title/body/cleaned_text.

2. boolean
- Simple query string with default AND semantics.

Endpoint:
- GET /search?q=...&mode=bm25
- GET /search?q=...&mode=boolean

## 3. /search API with pagination and snippets

Implemented in app/api/src/main.py:

1. Pagination via page + size.
2. Total hit count returned.
3. Snippet extraction from indexed body field.

## 4. Baseline benchmark output

Script: app/api/src/benchmark_retrieval.py

Actions:
1. Runs representative startup/news queries.
2. Captures top-10 hits for BM25 and Boolean modes.
3. Writes JSON output for quick comparison.
