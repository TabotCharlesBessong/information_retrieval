# Phase B Implementation Guide

This guide maps directly to roadmap Phase B activities.

## 1. Feed ingestion and crawl-state tracking

Script: app/pipeline/src/ingest_sources.py

Actions:
1. Initializes schema from SQLAlchemy ORM metadata.
2. Parses docs/phase-a/source-allowlist.md.
3. Upserts sources into sources table.
4. Seeds crawl_queue with base URLs.

## 2. Duplicate detection and noise removal

Script: app/pipeline/src/fetch_and_dedupe.py

Actions:
1. Pulls pending URLs from crawl_queue.
2. Applies low-value URL noise rules.
3. Fetches HTML for non-noise URLs.
4. Stores content hash and marks duplicates in raw_documents.

## 3. Parsing and text transformation

Script: app/pipeline/src/parse_documents.py

Actions:
1. Parses raw HTML with BeautifulSoup.
2. Removes boilerplate tags.
3. Normalizes text.
4. Tokenizes, removes stopwords, stems, and builds bigrams/trigrams.
5. Writes outputs to parsed_documents.

## 4. Text-statistics instrumentation

Script: app/pipeline/src/text_stats_report.py

Actions:
1. Computes token and vocabulary sizes.
2. Prints top token frequencies (Zipf head).
3. Prints vocabulary growth points (Heaps trend).

## Local run order

1. python app/pipeline/src/ingest_sources.py
2. python app/pipeline/src/fetch_and_dedupe.py
3. python app/pipeline/src/parse_documents.py
4. python app/pipeline/src/text_stats_report.py

## Notes

1. Scripts assume PostgreSQL credentials from environment variables in .env.example.
2. Start database service before running scripts.
3. Extend the allowlist as source validation progresses.
4. app/pipeline/sql/schema.sql is kept as SQL reference and is not deleted.
