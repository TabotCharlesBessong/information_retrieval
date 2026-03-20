# Phase A Architecture Contracts

This document defines service boundaries and API contracts for the baseline architecture.

## Service Boundaries

1. Acquisition Service
- Responsibility: fetch raw pages and enqueue parsing jobs.
- Inputs: seed URLs, crawl schedule, robots policies.
- Outputs: raw document payloads with metadata.

2. Transformation Service
- Responsibility: parse HTML, normalize text, emit structured documents.
- Inputs: raw document payloads.
- Outputs: normalized document records with terms and fields.

3. Index Service
- Responsibility: store searchable records and metadata in Elasticsearch.
- Inputs: normalized document records.
- Outputs: indexed searchable corpus.

4. Query Service (FastAPI)
- Responsibility: parse query request, search index, return ranked responses.
- Inputs: query text and pagination parameters.
- Outputs: ranked result list with snippets and metadata.

5. Metadata Service (PostgreSQL schema)
- Responsibility: store crawl state, source registry, and operational telemetry.
- Inputs: crawler and parser events.
- Outputs: state records for orchestration and monitoring.

## API Contract: Query Service

### GET /health
- Description: readiness/liveness endpoint.
- Success response: {"status":"ok"}

### GET /search
- Query params:
  - q (required): user query string
  - page (optional, default 1)
  - size (optional, default 10, max 50)
- Success response shape:
  - query: string
  - page: int
  - size: int
  - total: int
  - items: array of {id, title, snippet, source, published_at, score, url}

## Elasticsearch Index Contract (baseline)

Index name: documents

Required fields:
1. id (keyword)
2. title (text)
3. body (text)
4. source (keyword)
5. url (keyword)
6. published_at (date)
7. tags (keyword)

## PostgreSQL Contract (baseline)

Tables (phase-a skeleton):
1. sources
- id, name, base_url, enabled, created_at
2. crawl_queue
- id, url, source_id, status, priority, created_at, updated_at
3. crawl_events
- id, url, status, message, created_at

## Non-Functional Baseline

1. Query latency target (local baseline): p95 under 500 ms for small dataset.
2. API contract stability: no breaking changes without version note.
3. Observability minimum: request log + health endpoint.
