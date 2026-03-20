# Project Roadmap (Aligned to DSC608 2023-2024)

This roadmap is now tied to the DSC608 course progression and the new course resources in assets. It moves from core IR foundations to evaluation and recommendation in the same order used in the semester.

---

## 1. Phase A: Foundations and Architecture (Weeks 1-3)

* Objectives
  * Align project scope with ad-hoc retrieval tasks and target users.
  * Finalize system architecture based on standard IR building blocks.

* Key activities
  1. Define domain corpus, relevance assumptions, and success criteria.
  2. Produce architecture baseline: text acquisition, transformation, indexing, interaction, ranking, evaluation.
  3. Set up development stack: Python, FastAPI, Elasticsearch, PostgreSQL, Docker.

* Deliverables
  * Problem statement and relevance definition.
  * Architecture diagram and component contracts.
  * Local development environment and seed dataset.

---

## 2. Phase B: Crawls, Feeds, and Text Transformation (Weeks 3-6)

* Objectives
  * Build a reliable ingestion pipeline and clean textual representation.

* Key activities
  1. Implement web/document feed ingestion and crawl-state tracking.
  2. Add duplicate detection and noise removal.
  3. Implement parsing, tokenization, stopping, stemming, and n-gram extraction.
  4. Add text-statistics instrumentation (frequency distribution and vocabulary growth).

* Deliverables
  * Working crawler/parser pipeline.
  * Clean document schema for indexing.
  * Text-statistics report (Zipf/Heaps observations on your corpus).

* Milestone
  1. Usable corpus snapshot with transformed terms and metadata.

---

## 3. Phase C: Indexing and Baseline Ranking (Weeks 6-8)

* Objectives
  * Deliver first complete search loop from query to ranked results.

* Key activities
  1. Build inverted index and query-processing path.
  2. Implement baseline retrieval models (Boolean and vector-space/BM25).
  3. Expose `/search` API with pagination and snippets.

* Deliverables
  * Indexed corpus in Elasticsearch/OpenSearch.
  * Search API returning ranked results.
  * Baseline retrieval benchmark.

* Milestone
  1. CA checkpoint readiness: stable and demonstrable baseline engine.

---

## 4. Phase D: Queries, Interfaces, and Retrieval Expansion (Weeks 8-10)

* Objectives
  * Improve search usability and retrieval quality.

* Key activities
  1. Add query transformation, spell suggestions, and refinement.
  2. Implement phrase queries, filters, and faceting.
  3. Extend ranking to probabilistic model variant and compare with baseline.
  4. Build UI features for result snippets and relevance-oriented interaction.

* Deliverables
  * Extended query parser and interface layer.
  * Retrieval model comparison report.
  * Improved result page UX.

---

## 5. Phase E: Evaluation and Tuning (Weeks 10-12)

* Objectives
  * Make relevance measurable and improve ranking with evidence.

* Key activities
  1. Build evaluation corpus and relevance judgements.
  2. Compute effectiveness metrics: Recall, Precision, MAP/NDCG, top-k quality.
  3. Add efficiency checks: indexing time, latency, throughput.
  4. Run parameter tuning and significance checks.

* Deliverables
  * Evaluation toolkit and reproducible reports.
  * Tuned ranking configuration with measured gains.

* Milestone
  1. Documented improvement over initial baseline on agreed metrics.

---

## 6. Phase F: Filtering, Recommendation, and Final Hardening (Week 12-13+)

* Objectives
  * Add user-facing intelligence beyond pure ranked retrieval.

* Key activities
  1. Implement filtering module (rule-based and profile-aware).
  2. Add recommendation prototype (content-based first, collaborative optional).
  3. Final documentation, revision, and release packaging.

* Deliverables
  * Filtering and recommendation feature set.
  * Final technical report and demo script.
  * Next-iteration backlog (semantic/hybrid expansion).

---

## 7. Cross-Cutting Practices (All Phases)

* Version control discipline and weekly milestone reviews.
* Unit/integration testing for pipeline and query behavior.
* Monitoring for crawl/index/query stages.
* Continuous documentation updates after each review week.

> This roadmap is semester-aware and should be updated at each review/revision slot.
