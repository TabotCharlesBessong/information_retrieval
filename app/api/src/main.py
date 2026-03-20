from typing import Literal

from elasticsearch import ApiError
from fastapi import FastAPI, HTTPException, Query
from pydantic import BaseModel

from search_backend import (
    INDEX_NAME,
    build_query,
    get_es,
    get_search_backend,
    local_health,
    local_search,
    make_snippet,
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
    mode: str
    page: int
    size: int
    total: int
    items: list[SearchItem]


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
    mode: Literal["bm25", "boolean"] = Query("bm25"),
    page: int = Query(1, ge=1),
    size: int = Query(10, ge=1, le=50),
) -> SearchResponse:
    if not q.strip():
        raise HTTPException(status_code=400, detail="q must not be empty")

    backend = get_search_backend()
    items: list[SearchItem] = []

    if backend == "sqlite":
        total, rows = local_search(q, mode, page, size)
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
        body = build_query(q, mode)

        try:
            if not es.indices.exists(index=INDEX_NAME):
                return SearchResponse(query=q, mode=mode, page=page, size=size, total=0, items=[])

            result = es.search(index=INDEX_NAME, body=body, from_=from_, size=size)
        except ApiError as exc:
            raise HTTPException(status_code=503, detail=f"Search backend error: {exc}")
        except Exception as exc:
            raise HTTPException(status_code=503, detail=f"Search backend unavailable: {exc}")

        hits = result.get("hits", {}).get("hits", [])
        total_obj = result.get("hits", {}).get("total", 0)
        total = total_obj.get("value", 0) if isinstance(total_obj, dict) else int(total_obj)

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

    return SearchResponse(query=q, mode=mode, page=page, size=size, total=total, items=items)
