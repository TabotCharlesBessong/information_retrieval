from __future__ import annotations

import os
from typing import Literal

from elasticsearch import Elasticsearch

INDEX_NAME = os.getenv("ELASTICSEARCH_INDEX", "documents")


def get_es() -> Elasticsearch:
    es_url = os.getenv("ELASTICSEARCH_URL", "http://localhost:9200")
    return Elasticsearch(es_url)


def build_query(q: str, mode: Literal["bm25", "boolean"]) -> dict:
    if mode == "boolean":
        return {
            "query": {
                "simple_query_string": {
                    "query": q,
                    "fields": ["title^2", "body", "cleaned_text"],
                    "default_operator": "and",
                }
            }
        }

    return {
        "query": {
            "multi_match": {
                "query": q,
                "fields": ["title^2", "body", "cleaned_text"],
                "type": "best_fields",
            }
        }
    }


def make_snippet(text: str, query: str, max_len: int = 220) -> str:
    if not text:
        return ""

    normalized = " ".join(text.split())
    if len(normalized) <= max_len:
        return normalized

    needle = query.split()[0].lower() if query.split() else ""
    if needle:
        lower = normalized.lower()
        pos = lower.find(needle)
        if pos >= 0:
            start = max(0, pos - 60)
            end = min(len(normalized), start + max_len)
            return normalized[start:end]

    return normalized[:max_len]
