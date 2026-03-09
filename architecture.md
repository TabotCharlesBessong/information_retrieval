# Architectural Design for a Vertical AI‑Powered Search Engine

This document describes the proposed system architecture including components, data flow, and technology choices. Diagrams use Mermaid syntax for quick visualization.

---

## 1. High‑Level Overview

```mermaid
flowchart TD
    Internet((Internet)) -->|seed URLs| Crawler[Web Crawler]
    Crawler --> Parser[HTML Parser]
    Parser -->|documents| Indexer[Elasticsearch Index]
    Parser -->|to embed| Embed[(Embedding Pipeline)]
    Indexer --> API[Search API (FastAPI)]
    Embed --> VectorDB[FAISS/Weaviate]
    API -->|keyword hits| Ranker[Ranking Engine]
    API -->|hybrid results| VectorDB
    Ranker --> UI[Frontend (Next.js)]
    UI --> Users((Users))
```

This architecture is modular; most components can be scaled independently and replaced as needed.

---

## 2. Component Breakdown

| Component | Responsibility | Tech & Notes |
|-----------|----------------|--------------|
| **Crawler** | Discover and download pages, follow links | Scrapy + Playwright; respects robots.txt; distributed via Kafka/Redis queue for scale |
| **Parser** | Extract text, metadata, links; clean and normalize | BeautifulSoup/lxml; built as a microservice or library called by crawler |
| **Indexer** | Create inverted index and store documents | Elasticsearch; use custom analyzers (standard, n‑gram, edge‑ngram); index metadata fields for filtering |
| **Embedding Pipeline** | Compute vector representations for docs and queries | SentenceTransformers; batch process on GPU/CPU; store in FAISS or Weaviate; update incrementally as new docs arrive |
| **Search API** | Handle client queries, orchestrate searches | FastAPI; endpoints `/search`, `/semantic_search`, `/doc/{id}`; input validation; caching layer (Redis) to store frequent query results |
| **Ranking Engine** | Combine signals and produce ordered results | BM25 from ES, PageRank scores, clickthrough logs, semantic similarity; implemented as Python module invoked by API service |
| **Frontend** | User interface | Next.js with SSR; components for search box, results, facets, login; communicates with API via REST/JSON |
| **Metadata DB** | Persistent relational store | PostgreSQL; stores crawl status, user accounts, analytics, configuration settings |
| **Message Queue** | Decouples producers and consumers | Apache Kafka or Redis Streams; used in crawling and embedding pipelines |
| **Vector Database** | ANN search for vectors | FAISS (local), Weaviate (managed), or similar; exposes k‑NN APIs to the API service |
| **Monitoring & Logging** | Observability | Prometheus for metrics; Grafana dashboards; ELK/EFK stack for logs; alerting via PagerDuty/Slack |

---

## 3. Data Flow

1. **Crawling**: 
   * Seeds are inserted into PostgreSQL with status `pending`.
   * Crawler workers pull next URL from queue, fetch content, and push HTML to parser service.

2. **Parsing & Indexing**: 
   * Parser extracts text and metadata; returns JSON document.
   * Document is sent to Elasticsearch for indexing and to embedding pipeline.
   * Embedder computes vector and writes to FAISS/Weaviate.

3. **Query Handling**:
   * Client sends query to FastAPI.
   * API runs keyword search against ES; receives hits with scores.
   * API optionally computes query embedding and performs ANN search.
   * Ranking engine merges ES scores with vector similarity and other signals.
   * Final result list returned to frontend.

4. **Feedback Loop**:
   * User clicks logged to PostgreSQL or a dedicated analytics store.
   * Periodic jobs compute query reformulation statistics and update ranking weights.

---

## 4. Scaling & Resilience

* **Horizontal scaling**: Each service runs in Docker containers managed by Kubernetes or ECS.  
* **Stateless design**: Crawler, parser, API, and ranker are stateless; state lives in queue/DBs.  
* **Index sharding**: Elasticsearch index split across nodes; replica shards for fault tolerance.  
* **Backpressure**: Kafka queues allow producers to write faster than consumers process; consumers scale out.  
* **Cache layer**: Redis caches top queries and document metadata to reduce load on ES.
* **Health checks**: Kubernetes liveness/readiness probes ensure unhealthy pods restart.

---

## 5. Security Considerations

* All external traffic passes through HTTPS with TLS termination.
* API endpoints require API keys or OAuth tokens; rate limits applied using Redis.
* Crawler respects robots.txt and uses rotating IPs if necessary.
* Elasticsearch is secured with authentication and network ACLs (VPC or firewall).  
* Sensitive configuration values (API keys, DB credentials) stored in Vault or Kubernetes Secrets.

---

## 6. Development Principles

* **Modularity** – write components as small services with well‑defined interfaces.  
* **Testability** – each module has unit and integration tests; mocks for external systems.  
* **Observability** – instrument code early with metrics and structured logs.  
* **Incrementality** – deploy minimal working system first, then add features.  
* **Documentation** – generate API docs (e.g., OpenAPI) and maintain architecture diagrams.


> _This design is a living document; revisit as the system grows or requirements change._
