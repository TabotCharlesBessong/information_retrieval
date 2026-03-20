from typing import Literal

from elasticsearch import ApiError
from fastapi import FastAPI, HTTPException, Query
from pydantic import BaseModel

from search_backend import (
    INDEX_NAME,
    build_extended_query,
    extract_phrase,
    get_es,
    get_search_backend,
    local_suggestions,
    local_health,
    local_search_extended,
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
    items: list[SearchItem]


class SuggestResponse(BaseModel):
    query: str
    suggestions: list[str]


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
    page: int = Query(1, ge=1),
    size: int = Query(10, ge=1, le=50),
) -> SearchResponse:
    if not q.strip():
        raise HTTPException(status_code=400, detail="q must not be empty")

    backend = get_search_backend()
    refinement = refine_query(q)
    phrase_query = phrase or extract_phrase(q)
    items: list[SearchItem] = []
    facet_data: dict[str, list[dict[str, int | str]]] = {"sources": []}

    if backend == "sqlite":
        total, rows, facet_data = local_search_extended(
            q=q,
            mode=mode,
            page=page,
            size=size,
            phrase=phrase_query,
            sources=source,
            published_from=published_from,
            published_to=published_to,
            with_facets=facets,
        )
        for row in rows:
            items.append(
                SearchItem(
                    id=row["id"],
                    title=row["title"],
                    snippet=make_snippet(row["body"], q),
                    source=row["source"],
                    published_at=row["published_at"],
                    score=float(row["score"]),
                    url=row["url"],
                )
            )
    else:
        es = get_es()
        from_ = (page - 1) * size
        body = build_extended_query(
            q=q,
            mode=mode,
            phrase=phrase_query,
            sources=source,
            published_from=published_from,
            published_to=published_to,
            with_facets=facets,
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
                    facets=facet_data,
                    items=[],
                )

            page_size = size if mode != "probabilistic" else min(150, size * 5)
            result = es.search(index=INDEX_NAME, body=body, from_=0 if mode == "probabilistic" else from_, size=page_size)
        except ApiError as exc:
            raise HTTPException(status_code=503, detail=f"Search backend error: {exc}")
        except Exception as exc:
            raise HTTPException(status_code=503, detail=f"Search backend unavailable: {exc}")

        hits = result.get("hits", {}).get("hits", [])
        total_obj = result.get("hits", {}).get("total", 0)
        total = total_obj.get("value", 0) if isinstance(total_obj, dict) else int(total_obj)

        agg_sources = result.get("aggregations", {}).get("sources", {}).get("buckets", [])
        facet_data = {
            "sources": [
                {"value": bucket.get("key", ""), "count": int(bucket.get("doc_count", 0))}
                for bucket in agg_sources
            ]
        }

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
            total = len(rescored)
            hits = [pair[1] for pair in rescored[from_ : from_ + size]]

        for hit in hits:
            src = hit.get("_source", {})
            items.append(
                SearchItem(
                    id=str(src.get("id", hit.get("_id", ""))),
                    title=src.get("title", ""),
                    snippet=make_snippet(src.get("body", ""), q),
                    source=src.get("source", ""),
                    published_at=src.get("published_at", ""),
                    score=float(hit.get("_score", 0.0) or 0.0),
                    url=src.get("url", ""),
                )
            )

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
        items=items,
    )


@app.get("/search/suggest", response_model=SuggestResponse)
def suggest(q: str = Query(..., min_length=2), limit: int = Query(5, ge=1, le=10)) -> SuggestResponse:
    return SuggestResponse(query=q, suggestions=local_suggestions(q, limit=limit))
