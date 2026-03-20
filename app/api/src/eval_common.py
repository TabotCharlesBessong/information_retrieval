from __future__ import annotations

import math
from typing import Literal

from search_backend import (
    INDEX_NAME,
    build_extended_query,
    get_es,
    get_search_backend,
    local_search_extended,
    refine_query,
)

QueryMode = Literal["bm25", "boolean", "probabilistic"]

DEFAULT_QUERIES: list[dict[str, str]] = [
    {"id": "q1", "text": "african fintech funding"},
    {"id": "q2", "text": "nigeria startup accelerator"},
    {"id": "q3", "text": "kenya mobile payments"},
    {"id": "q4", "text": "south africa ai startup"},
    {"id": "q5", "text": "ghana venture capital"},
]


def _probabilistic_score_from_source(source_doc: dict, refined_terms: list[str]) -> float:
    text = " ".join(
        [
            str(source_doc.get("title", "")),
            str(source_doc.get("cleaned_text", "")),
            str(source_doc.get("body", "")),
        ]
    ).lower()
    token_count = max(len(text.split()), 1)
    score = 0.0
    for term in refined_terms:
        tf = text.count(term)
        score += math.log((tf + 1.0) / (token_count + 1.0))
    return math.exp(score / max(len(refined_terms), 1))


def retrieve_results(query: str, mode: QueryMode, size: int = 20) -> list[dict]:
    backend = get_search_backend()
    if backend == "sqlite":
        _, rows, _ = local_search_extended(
            q=query,
            mode=mode,
            page=1,
            size=size,
            phrase=None,
            sources=None,
            published_from=None,
            published_to=None,
            with_facets=False,
        )
        return rows

    es = get_es()
    if not es.indices.exists(index=INDEX_NAME):
        return []

    body = build_extended_query(
        q=query,
        mode=mode,
        phrase=None,
        sources=None,
        published_from=None,
        published_to=None,
        with_facets=False,
    )

    query_size = size if mode != "probabilistic" else min(150, size * 5)
    result = es.search(index=INDEX_NAME, body=body, size=query_size)
    hits = result.get("hits", {}).get("hits", [])

    if mode == "probabilistic":
        refined_terms = str(refine_query(query)["refined_query"]).split()
        rescored: list[tuple[float, dict]] = []
        for hit in hits:
            src = hit.get("_source", {})
            rescored.append((_probabilistic_score_from_source(src, refined_terms), hit))
        rescored.sort(key=lambda pair: pair[0], reverse=True)
        hits = [pair[1] for pair in rescored[:size]]

    rows: list[dict] = []
    for hit in hits[:size]:
        src = hit.get("_source", {})
        rows.append(
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
    return rows
