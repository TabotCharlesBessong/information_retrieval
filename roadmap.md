# Project Roadmap: Vertical AI-Powered Search Engine

This document presents a comprehensive roadmap for building a vertical, AI-enhanced search engine. It is organised into clearly defined phases with milestones, required skills, and suggested deliverables for each stage.

---

## 1. Phase 0 – Preparation & Research (1–2 weeks)

* **Objectives**
  * Understand core concepts of information retrieval (IR).
  * Finalise domain/niche for the vertical engine.
  * Assemble technology stack and development environment.

* **Key Activities**
  1. Read *Introduction to Information Retrieval* (Chapters 1–4).
  2. Explore sample datasets within chosen domain (e.g. open‑access papers, job listings).
  3. Prototype simple TF‑IDF calculator in Python.
  4. Set up version control, issue tracker, and basic repo structure.
  5. Prepare development environment: Python venv, Docker, PostgreSQL/Elasticsearch containers.

* **Deliverables**
  * Domain specification document (target users, sources).
  * Glossary of IR terms.
  * Basic proof‑of‑concept script computing term frequencies.

---

## 2. Phase 1 – Core Engine & Crawler (4 weeks)

* **Objectives**
  * Develop an end‑to‑end pipeline from URL discovery to search API response.

* **Key Activities**
  1. **Crawler**
     - Build Scrapy/Playwright spiders.
     - Handle politeness (robots.txt, rate limits).
     - Store crawl state in PostgreSQL (URL queue, status, last‑seen).
  2. **Parser**
     - Strip HTML, extract title, text, metadata, and outgoing links using BeautifulSoup/lxml.
     - Normalize text (lowercase, remove stopwords, tokenize).
  3. **Indexer**
     - Design Elasticsearch index mappings (analyzers, fields, metadata).
     - Write Python code to feed parsed documents into ES.
     - Implement bulk indexing with error handling.
  4. **Search API**
     - FastAPI service exposing `/search` and `/document/{id}` endpoints.
     - Integrate ES query DSL (match, boolean queries).
     - Add pagination, simple ranking by score.

* **Deliverables**
  * `crawler/` module with spider and scheduler.
  * `parser/` module and unit tests.
  * Elasticsearch index configured & populated with initial data.
  * Running FastAPI service returning keyword search results.

* **Milestones**
  1. Crawl 1,000 pages from target domain.
  2. First successful query via API.
  3. Continuous integration pipeline running basic tests.

---

## 3. Phase 2 – Rich Query Features (4 weeks)

* **Objectives**
  * Improve the quality of search results and usability.

* **Key Activities**
  1. **Ranking Enhancements**
     - Experiment with BM25 parameters.
     - Add PageRank calculation over crawled graph.
     - Collect basic user feedback (click logs) and integrate signals.
  2. **Query Parsing**
     - Support phrase search (`"exact phrase"`).
     - Implement fielded search (e.g. `title:python site:example.com`).
     - Add filter and facet support.
  3. **Typo Tolerance**
     - Enable fuzzy matching in Elasticsearch.
     - Use n‑gram/edge‑ngram analyzers for autocomplete.
  4. **Advanced Indexing**
     - Store additional metadata (publish date, author, tags).
     - Pre‑compute and store document vectors for hybrid search.
  5. **User Interface (stub)**
     - Simple HTML/Next.js page calling the search API.

* **Deliverables**
  * Extended search API with filtering and advanced query syntax.
  * Benchmarks comparing TF‑IDF vs. BM25 vs. hybrid scoring.
  * Frontend prototype with autocomplete and facets.

* **Milestones**
  1. Deployable 2‑page UI (search box + results).
  2. Successful handling of 10,000 concurrent queries (load test).

---

## 4. Phase 3 – AI & Semantic Search (4 weeks)

* **Objectives**
  * Integrate embedding‑based search for semantic understanding.

* **Key Activities**
  1. **Embedding Generation**
     - Select a model (e.g. `all-MiniLM-L6-v2` from SentenceTransformers).
     - Batch‑embed documents during indexing; store vectors in FAISS or Weaviate.
  2. **Query Embeddings**
     - Convert incoming queries to vectors.
     - Perform nearest‑neighbor search (ANN) and merge with keyword results.
  3. **Hybrid Ranking**
     - Combine ES score and cosine similarity via weighted sum.
     - Tuning weights based on sample queries.
  4. **Interactive Features**
     - Support natural‑language queries (“papers about transformer models”).
     - Add “Did you mean?” or “Related topics” suggestions using embeddings.

* **Deliverables**
  * Semantically‑aware search endpoint (`/semantic_search`).
  * FAISS index built and updated incrementally.
  * Evaluation report showing improvements on sample queries.

* **Milestones**
  1. 20‑point increase in NDCG on held‑out query set.
  2. Real‑time embedding pipeline running within 100 ms per document.

---

## 5. Phase 4 – Scaling & Distribution (6–8 weeks)

* **Objectives**
  * Prepare system for production load and distributed operation.

* **Key Activities**
  1. **Distributed Crawler**
     - Use Kafka/Redis queue to distribute URLs among multiple workers.
     - Containerize crawler with Docker; orchestrate with Docker Compose or Kubernetes.
  2. **Data Pipeline**
     - Implement ETL stages: crawl → parse → index → embed.
     - Add back‑pressure and retry logic.
  3. **Caching & CDN**
     - Add Redis or Varnish layer for frequently seen queries.
     - Serve static frontend assets via CDN (e.g. CloudFront).  
  4. **Monitoring & Logging**
     - Integrate Prometheus & Grafana for metrics (crawls/sec, qps, latency).
     - Centralize logs with ELK/EFK stack.
  5. **Security & Access Control**
     - Add API key/token authentication.
     - Rate‑limit abusive clients; implement CORS policies.
  6. **Continuous Deployment**
     - Set up CI/CD (GitHub Actions) to build images and deploy to cloud.

* **Deliverables**
  * Multi‑worker crawler running in cloud (AWS/GCP/DO).
  * Auto‑scaling search API behind load‑balancer.
  * Full observability dashboard with alerting rules.

* **Milestones**
  1. Handle 100 k DAS per day with <200 ms 99th‑percentile latency.
  2. Zero‑downtime deployments via rolling updates.

---

## 6. Phase 5 – Product & UX Polishing (ongoing)

* **Objectives**
  * Improve usability, add user features, iterate based on analytics.

* **Key Activities**
  - Add user accounts, saved searches, and personalization.
  - Analyze click‑through and dwell‑time for ranking signals.
  - Implement A/B tests for UI changes.
  - Expand crawl scope (additional domains) and re‑train ranking models.
  - Explore multi‑modal search (images/audio) and conversational interfaces.

* **Deliverables**
  * Roadmap for next 6‑12 months.
  * Design system for frontend components.
  * Documentation and API reference for external developers.

---

> _The roadmap is iterative; phases may overlap and priorities will shift depending on user feedback and technical discoveries._
