# Development Timeline (DSC608 Semester Plan)

This timeline maps the implementation directly to the DSC608 2023-2024 week structure (13 teaching weeks, 2 slots per week, with review/CA windows).

---

## Weeks 1-2: IR Orientation and Architecture

| Week | Course Theme | Implementation Focus | Output |
|---|---|---|---|
| 1 | Intro to IR, ad-hoc retrieval, system classification | Define retrieval scope, target corpus, relevance criteria, and acceptance metrics | Project charter and evaluation goals |
| 2 | Search engine architecture building blocks | Freeze service boundaries: acquisition, transformation, indexing, ranking, query interface, evaluation | Architecture baseline and service contracts |

Milestone: architecture and measurable objectives approved.

---

## Weeks 3-4: Crawls, Feeds, and Text Transformation Core

| Week | Course Theme | Implementation Focus | Output |
|---|---|---|---|
| 3 | Crawls and feeds | Build crawler/feed ingestion, storage of raw docs, duplicate and noise checks | Running ingestion pipeline |
| 4 | Processing text Ia/Ib | Implement parsing, tokenization, stopping, stemming, phrase and n-gram support | Transformation module with tests |

Milestone: transformed document objects ready for indexing.

---

## Weeks 5-6: Structure-Aware Processing and Indexing

| Week | Course Theme | Implementation Focus | Output |
|---|---|---|---|
| 5 | Processing text Ic + review | Add markup/link-aware parsing and extraction of structural fields | Enriched document schema |
| 6 | Ranking with indexes I/II | Build inverted index pipeline, index mappings, and query-time lookup path | Searchable index and baseline query API |

Milestone: end-to-end lexical search is operational.

---

## Week 7: Consolidation and CA Checkpoint

| Week | Course Theme | Implementation Focus | Output |
|---|---|---|---|
| 7 | Tutorials, revision, CA test | Stabilize baseline engine, run smoke/load tests, package demo | CA-ready baseline release |

Milestone: first formal checkpoint complete.

---

## Weeks 8-9: Query and Interface Expansion

| Week | Course Theme | Implementation Focus | Output |
|---|---|---|---|
| 8 | Query transformation, spell suggestions, personalization | Add query rewriting, spelling suggestions, and basic personalization hooks | Enhanced query parser |
| 9 | Results display, snippets, clustering, cross-language awareness | Improve result rendering, snippets, and grouping logic in API/UI | Improved result UX layer |

Milestone: usability-focused search experience in place.

---

## Weeks 9-10: Retrieval Model Broadening

| Week | Course Theme | Implementation Focus | Output |
|---|---|---|---|
| 9-10 | Boolean, vector-space, probabilistic models | Implement model variants and compare their retrieval behavior | Model comparison benchmark |

Milestone: model selection backed by measurements.

---

## Weeks 10-12: Evaluation-Driven Improvement

| Week | Course Theme | Implementation Focus | Output |
|---|---|---|---|
| 10 | Why evaluate, corpus and logging | Build relevance set and logging pipeline | Evaluation dataset + logs |
| 11 | Effectiveness metrics | Compute recall, precision, MAP/NDCG, top-k analysis | Effectiveness report |
| 12 | Efficiency metrics and testing | Measure latency/throughput, significance checks, parameter tuning | Performance and tuning report |

Milestone: validated and tuned ranking configuration.

---

## Weeks 12-13: Filtering, Recommendation, and Final Revision

| Week | Course Theme | Implementation Focus | Output |
|---|---|---|---|
| 12-13 | Filtering and recommendation + revision | Add filtering/recommendation prototype and finalize documentation | Final demo package and handover docs |

Milestone: semester-complete IR system aligned to course outcomes.

---

## Continuous Tasks (Every Week)

1. Maintain test suite for crawler, parser, index, and query layers.
2. Track text-statistics dashboards (term frequency skew, vocabulary growth).
3. Keep weekly retrospective notes and risk register.
4. Update roadmap and architecture after each review slot.
