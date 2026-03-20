from fastapi import FastAPI, HTTPException, Query
from pydantic import BaseModel


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
    page: int
    size: int
    total: int
    items: list[SearchItem]


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.get("/search", response_model=SearchResponse)
def search(
    q: str = Query(..., min_length=2),
    page: int = Query(1, ge=1),
    size: int = Query(10, ge=1, le=50),
) -> SearchResponse:
    if not q.strip():
        raise HTTPException(status_code=400, detail="q must not be empty")

    # Phase A stub response keeps API contract stable while indexing is built.
    return SearchResponse(query=q, page=page, size=size, total=0, items=[])
