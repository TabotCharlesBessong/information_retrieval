# information_retrieval

Vertical information retrieval project aligned to DSC608, implemented incrementally by roadmap phase.

Current target vertical: **African technology and startup news**.

## Phase A status

Phase A deliverables are implemented:

1. Domain and relevance specification.
2. Architecture/service contracts.
3. Local development stack scaffold (FastAPI + Elasticsearch + PostgreSQL).

See:

1. docs/phase-a/domain-and-relevance-spec.md
2. docs/phase-a/service-contracts.md
3. docs/phase-a/phase-a-checklist.md
4. docs/phase-a/source-allowlist.md

## Project structure

1. architecture.md: high-level architecture narrative.
2. roadmap.md: semester-aligned roadmap and phases.
3. timeline.md: week-by-week implementation timeline.
4. app/api: FastAPI service scaffold.
5. app/pipeline: ingestion, parsing, and indexing pipeline.

## Local quickstart (recommended)

This mode uses SQLite for storage and local search from parsed documents.

1. Create and activate a virtual environment.
2. Install dependencies:

```bash
pip install -r app/pipeline/requirements.txt
pip install -r app/api/requirements.txt
```

3. Set local mode env vars in your shell:

```bash
$env:SEARCH_BACKEND="sqlite"
$env:DATABASE_URL="sqlite:///./.data/ir.db"
```

4. Run the pipeline:

```bash
python app/pipeline/src/ingest_sources.py
python app/pipeline/src/fetch_and_dedupe.py
python app/pipeline/src/parse_documents.py
```

5. Start API:

```bash
uvicorn app.api.src.main:app --reload --port 8000
```

6. Test:

```bash
curl "http://localhost:8000/health"
curl "http://localhost:8000/search?q=african%20startup%20funding&mode=bm25&page=1&size=10"
curl "http://localhost:8000/search?q=african%20startup%20funding&mode=boolean&page=1&size=10"
```

## Current status

Phase F implementation is complete: filtering, profile-aware reranking, and content-based recommendations are available in the API.

## Phase B quickstart

Artifacts:

1. docs/phase-b/implementation-guide.md
2. docs/phase-b/phase-b-checklist.md
3. app/pipeline/src/*.py

Install pipeline dependencies:

```bash
pip install -r app/pipeline/requirements.txt
```

Run Phase B scripts:

```bash
python app/pipeline/src/ingest_sources.py
python app/pipeline/src/fetch_and_dedupe.py
python app/pipeline/src/parse_documents.py
python app/pipeline/src/text_stats_report.py
```

## Migration workflow (Alembic)

From app/pipeline:

```bash
alembic upgrade head
alembic revision --autogenerate -m "describe change"
```

Reference docs: app/pipeline/migrations/README.md

## Phase C quickstart

Artifacts:

1. docs/phase-c/implementation-guide.md
2. docs/phase-c/phase-c-checklist.md
3. app/pipeline/src/index_documents.py
4. app/api/src/main.py

Index parsed documents (Elasticsearch mode):

```bash
python app/pipeline/src/index_documents.py
```

Run API:

```bash
uvicorn app.api.src.main:app --reload --port 8000
```

Search examples:

```bash
curl "http://localhost:8000/search?q=african%20startup%20funding&mode=bm25&page=1&size=10"
curl "http://localhost:8000/search?q=african%20startup%20funding&mode=boolean&page=1&size=10"
```

## Phase E quickstart

Artifacts:

1. docs/phase-e/implementation-guide.md
2. docs/phase-e/phase-e-checklist.md
3. app/api/src/build_eval_corpus.py
4. app/api/src/evaluate_metrics.py
5. app/api/src/efficiency_benchmark.py
6. app/api/src/tune_significance.py

Run evaluation workflow:

```bash
python app/api/src/build_eval_corpus.py
python app/api/src/evaluate_metrics.py
python app/api/src/efficiency_benchmark.py
python app/api/src/tune_significance.py
```

## Phase F quickstart

Artifacts:

1. docs/phase-f/implementation-guide.md
2. docs/phase-f/phase-f-checklist.md
3. app/api/src/filtering_recommendation.py
4. app/api/src/main.py
5. app/api/src/search_backend.py

Run API:

```bash
uvicorn app.api.src.main:app --reload --port 8000
```

Open UI:

1. Browser URL: http://localhost:8000/
2. The page calls `/search` and `/recommendations` on the same FastAPI server.

Try filtering/profile-aware search:

```bash
curl "http://localhost:8000/search?q=african%20fintech&must_include=funding&exclude_source=WeeTracker&profile_interests=payments&profile_preferred_sources=TechCabal"
```

Try recommendations:

```bash
curl "http://localhost:8000/recommendations?seed_doc_id=3&size=5"
```

Run Phase F tests:

```bash
python -m unittest app.api.src.test_phase_f
```

---

## Phase 2 — Basic Search Engine (4 weeks)

Build:

* crawler
* index
* search API

Stack:

Python + Elasticsearch.

Features:

* keyword search
* indexing
* basic ranking

---

## Phase 3 — Advanced Search (4 weeks)

Add:

* typo tolerance
* phrase search
* filters
* pagination

Example:

```
search?q=AI&site=arxiv.org
```

---

## Phase 4 — AI Search (4 weeks)

Add:

* embeddings
* semantic search

Using:

* sentence transformers
* FAISS

Now users can search:

```
"papers about transformer models"
```

instead of keywords.

---

## Phase 5 — Scaling (4–8 weeks)

Add:

* distributed crawling
* ranking improvements
* caching
* monitoring

Tools:

* Redis
* Kafka

---

# 6. Development Timeline

Realistic solo timeline:

| Phase           | Duration |
| --------------- | -------- |
| Foundations     | 3 weeks  |
| Basic engine    | 4 weeks  |
| Advanced search | 4 weeks  |
| AI search       | 4 weeks  |
| Scaling         | 6 weeks  |

Total:

**4–5 months**

---

# 7. Example Project Structure

```
search-engine/

crawler/
   spider.py
   parser.py

indexer/
   elastic_index.py

api/
   main.py
   search.py

ranking/
   ranker.py

frontend/
   nextjs-ui/

infra/
   local-dev-notes.md
```

---

# 8. Minimum Viable Search Engine

You only need:

Crawler → Parser → Elasticsearch → API → UI

Example flow:

```
crawler → fetch pages
parser → extract text
indexer → store in Elasticsearch
API → query Elasticsearch
frontend → display results
```

---

# 9. Essential Skills Needed

Learn these areas:

### Backend engineering

* APIs
* async programming

### Data engineering

* pipelines
* indexing

### Distributed systems

* queues
* scaling

### Information retrieval

Core concepts:

* inverted index
* BM25
* ranking

---

# 10. Methodology

Follow:

**Agile development**

Weekly sprints.

Example:

Week 1:

crawler prototype

Week 2:

indexing

Week 3:

search API

Week 4:

frontend

---

# 11. Example MVP Idea

Build:

**African Startup Search Engine**

Index:

* tech startups
* funding news
* incubators
* jobs

Unique niche.

---

# 12. Realistic Hardware Requirements

For MVP:

* 8GB RAM
* 4 CPU cores

For large scale:

* distributed cluster

---

# 13. Biggest Mistake Beginners Make

They try to build **Google-scale search engines immediately**.

Instead:

Build **domain-specific search** first.

---

# 14. What Would Make Your Search Engine Unique

Consider:

* AI summarization
* domain expertise
* regional search
* private search

---

✅ If you'd like, I can also show you:

* **How Google search actually works internally**
* **The 15 core algorithms behind Google ranking**
* **A system design diagram used in big tech interviews**
* **A realistic architecture for indexing 1 billion pages**.
