from typing import Literal

from elasticsearch import ApiError
from fastapi import FastAPI, HTTPException, Query
from pydantic import BaseModel

from .filtering_recommendation import (
    apply_filters,
    recommend_content_based,
    rerank_with_profile,
    source_facets,
)
from .search_backend import (
    INDEX_NAME,
    build_extended_query,
    extract_phrase,
    get_document_by_id,
    get_es,
    get_search_backend,
    local_health,
    local_search_extended,
    local_suggestions,
    make_snippet,
    refine_query,
)


app = FastAPI(title="Information Retrieval API", version="0.1.0")


class SearchItem(BaseModel):
    id: str
    title: str
    snippet: str
    source: str
    published_at: str
    score: float
    url: str


class SearchResponse(BaseModel):
    query: str
    normalized_query: str
    suggested_query: str
    expanded_terms: list[str]
    mode: str
    page: int
    size: int
    total: int
    facets: dict[str, list[dict[str, int | str]]]
    filtering_summary: dict[str, int]
    items: list[SearchItem]


class SuggestResponse(BaseModel):
    query: str
    suggestions: list[str]


class RecommendationItem(BaseModel):
    id: str
    title: str
    snippet: str
    source: str
    published_at: str
    score: float
    url: str
    reason: str


class RecommendationResponse(BaseModel):
    seed_doc_id: str
    query: str
    total: int
    items: list[RecommendationItem]


@app.get("/health")
def health() -> dict[str, str]:
    backend = get_search_backend()
    if backend == "sqlite":
        return {"status": "ok", "search_backend": "sqlite", "sqlite": "up" if local_health() else "down"}

    es = get_es()
    es_ok = False
    try:
        es_ok = bool(es.ping())
    except Exception:
        es_ok = False
    return {"status": "ok", "search_backend": "elasticsearch", "elasticsearch": "up" if es_ok else "down"}


@app.get("/search", response_model=SearchResponse)
def search(
    q: str = Query(..., min_length=2),
    mode: Literal["bm25", "boolean", "probabilistic"] = Query("bm25"),
    phrase: str | None = Query(None),
    source: list[str] | None = Query(None),
    published_from: str | None = Query(None),
    published_to: str | None = Query(None),
    facets: bool = Query(True),
    must_include: list[str] | None = Query(None),
    exclude_terms: list[str] | None = Query(None),
    exclude_source: list[str] | None = Query(None),
    profile_interests: list[str] | None = Query(None),
    profile_preferred_sources: list[str] | None = Query(None),
    profile_excluded_sources: list[str] | None = Query(None),
    page: int = Query(1, ge=1),
    size: int = Query(10, ge=1, le=50),
) -> SearchResponse:
    if not q.strip():
        raise HTTPException(status_code=400, detail="q must not be empty")

    backend = get_search_backend()
    refinement = refine_query(q)
    phrase_query = phrase or extract_phrase(q)
    candidate_size = max(size * 5, 50)

    raw_rows: list[dict] = []
    if backend == "sqlite":
        _, rows, _ = local_search_extended(
            q=q,
            mode=mode,
            page=1,
            size=candidate_size,
            phrase=phrase_query,
            sources=source,
            published_from=published_from,
            published_to=published_to,
            with_facets=False,
        )
        raw_rows = rows
    else:
        es = get_es()
        body = build_extended_query(
            q=q,
            mode=mode,
            phrase=phrase_query,
            sources=source,
            published_from=published_from,
            published_to=published_to,
            with_facets=False,
        )

        try:
            if not es.indices.exists(index=INDEX_NAME):
                return SearchResponse(
                    query=q,
                    normalized_query=str(refinement["normalized_query"]),
                    suggested_query=str(refinement["suggested_query"]),
                    expanded_terms=list(refinement["expanded_terms"]),
                    mode=mode,
                    page=page,
                    size=size,
                    total=0,
                    facets={"sources": []},
                    filtering_summary={
                        "input_count": 0,
                        "kept_count": 0,
                        "dropped_source": 0,
                        "dropped_excluded_terms": 0,
                        "dropped_missing_must_terms": 0,
                    },
                    items=[],
                )

            query_size = candidate_size if mode != "probabilistic" else min(300, candidate_size * 2)
            result = es.search(index=INDEX_NAME, body=body, from_=0, size=query_size)
        except ApiError as exc:
            raise HTTPException(status_code=503, detail=f"Search backend error: {exc}")
        except Exception as exc:
            raise HTTPException(status_code=503, detail=f"Search backend unavailable: {exc}")

        hits = result.get("hits", {}).get("hits", [])
        if mode == "probabilistic":
            refined_terms = str(refinement["refined_query"]).split()

            def probabilistic_score(source_doc: dict) -> float:
                text = " ".join(
                    [
                        source_doc.get("title", ""),
                        source_doc.get("cleaned_text", ""),
                        source_doc.get("body", ""),
                    ]
                ).lower()
                token_count = max(len(text.split()), 1)
                score = 0.0
                for term in refined_terms:
                    tf = text.count(term)
                    score += (tf + 1.0) / (token_count + 1.0)
                return score / max(len(refined_terms), 1)

            rescored = []
            for hit in hits:
                src = hit.get("_source", {})
                rescored.append((probabilistic_score(src), hit))
            rescored.sort(key=lambda pair: pair[0], reverse=True)
            hits = [pair[1] for pair in rescored]

        for hit in hits:
            src = hit.get("_source", {})
            raw_rows.append(
                {
                    "id": str(src.get("id", hit.get("_id", ""))),
                    "title": src.get("title", ""),
                    "body": src.get("body", ""),
                    "source": src.get("source", ""),
                    "published_at": src.get("published_at", ""),
                    "score": float(hit.get("_score", 0.0) or 0.0),
                    "url": src.get("url", ""),
                }
            )

    blocked_sources = (exclude_source or []) + (profile_excluded_sources or [])
    filtered_rows, filtering_summary = apply_filters(
        rows=raw_rows,
        must_terms=must_include,
        exclude_terms=exclude_terms,
        blocked_sources=blocked_sources,
    )
    reranked_rows = rerank_with_profile(
        rows=filtered_rows,
        interests=profile_interests,
        preferred_sources=profile_preferred_sources,
    )

    total = len(reranked_rows)
    start = (page - 1) * size
    end = start + size
    page_rows = reranked_rows[start:end]

    facet_data = source_facets(filtered_rows) if facets else {"sources": []}
    items = [
        SearchItem(
            id=row["id"],
            title=row["title"],
            snippet=make_snippet(row.get("body", ""), q),
            source=row["source"],
            published_at=row["published_at"],
            score=float(row["score"]),
            url=row["url"],
        )
        for row in page_rows
    ]

    return SearchResponse(
        query=q,
        normalized_query=str(refinement["normalized_query"]),
        suggested_query=str(refinement["suggested_query"]),
        expanded_terms=list(refinement["expanded_terms"]),
        mode=mode,
        page=page,
        size=size,
        total=total,
        facets=facet_data,
        filtering_summary=filtering_summary,
        items=items,
    )


@app.get("/search/suggest", response_model=SuggestResponse)
def suggest(q: str = Query(..., min_length=2), limit: int = Query(5, ge=1, le=10)) -> SuggestResponse:
    return SuggestResponse(query=q, suggestions=local_suggestions(q, limit=limit))


@app.get("/recommendations", response_model=RecommendationResponse)
def recommendations(
    seed_doc_id: str = Query(..., min_length=1),
    q: str | None = Query(None),
    profile_excluded_sources: list[str] | None = Query(None),
    size: int = Query(10, ge=1, le=30),
) -> RecommendationResponse:
    seed = get_document_by_id(seed_doc_id)
    if seed is None:
        raise HTTPException(status_code=404, detail="seed document not found")

    query_text = (q or "").strip() or str(seed.get("title", "")).strip() or str(seed.get("body", "")).strip()[:120]
    if not query_text:
        raise HTTPException(status_code=400, detail="unable to build recommendation query")

    backend = get_search_backend()
    candidate_size = max(size * 8, 100)
    candidates: list[dict] = []

    if backend == "sqlite":
        _, rows, _ = local_search_extended(
            q=query_text,
            mode="bm25",
            page=1,
            size=candidate_size,
            phrase=None,
            sources=None,
            published_from=None,
            published_to=None,
            with_facets=False,
        )
        candidates = rows
    else:
        es = get_es()
        body = build_extended_query(
            q=query_text,
            mode="bm25",
            phrase=None,
            sources=None,
            published_from=None,
            published_to=None,
            with_facets=False,
        )
        try:
            if es.indices.exists(index=INDEX_NAME):
                result = es.search(index=INDEX_NAME, body=body, from_=0, size=candidate_size)
                hits = result.get("hits", {}).get("hits", [])
                for hit in hits:
                    src = hit.get("_source", {})
                    candidates.append(
                        {
                            "id": str(src.get("id", hit.get("_id", ""))),
                            "title": src.get("title", ""),
                            "body": src.get("body", ""),
                            "source": src.get("source", ""),
                            "published_at": src.get("published_at", ""),
                            "score": float(hit.get("_score", 0.0) or 0.0),
                            "url": src.get("url", ""),
                        }
                    )
        except ApiError as exc:
            raise HTTPException(status_code=503, detail=f"Search backend error: {exc}")
        except Exception as exc:
            raise HTTPException(status_code=503, detail=f"Search backend unavailable: {exc}")

    rec_rows = recommend_content_based(
        seed_doc=seed,
        candidates=candidates,
        top_k=size,
        blocked_sources=profile_excluded_sources,
    )

    items = [
        RecommendationItem(
            id=row["id"],
            title=row["title"],
            snippet=make_snippet(row.get("body", ""), query_text),
            source=row["source"],
            published_at=row["published_at"],
            score=float(row["score"]),
            url=row["url"],
            reason=str(row.get("reason", "content similarity")),
        )
        for row in rec_rows
    ]

    return RecommendationResponse(seed_doc_id=seed_doc_id, query=query_text, total=len(items), items=items)
