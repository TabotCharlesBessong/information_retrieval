from __future__ import annotations

import os
import sqlite3
from datetime import datetime
from pathlib import Path
from typing import Literal

from elasticsearch import Elasticsearch

INDEX_NAME = os.getenv("ELASTICSEARCH_INDEX", "documents")


def get_search_backend() -> Literal["elasticsearch", "sqlite"]:
    backend = os.getenv("SEARCH_BACKEND", "sqlite").strip().lower()
    return "elasticsearch" if backend == "elasticsearch" else "sqlite"


def get_es() -> Elasticsearch:
    es_url = os.getenv("ELASTICSEARCH_URL", "http://localhost:9200")
    return Elasticsearch(es_url)


def get_sqlite_path() -> str:
    explicit = os.getenv("SQLITE_DB_PATH", "").strip()
    if explicit:
        path = Path(explicit)
        if not path.is_absolute():
            path = Path(__file__).resolve().parents[3] / path
        path.parent.mkdir(parents=True, exist_ok=True)
        return str(path)

    database_url = os.getenv("DATABASE_URL", "").strip()
    if database_url.startswith("sqlite:///"):
        raw_path = database_url.replace("sqlite:///", "", 1)
        path = Path(raw_path)
        if not path.is_absolute():
            path = Path(__file__).resolve().parents[3] / path
        path.parent.mkdir(parents=True, exist_ok=True)
        return str(path)

    project_root = Path(__file__).resolve().parents[3]
    path = project_root / ".data" / "ir.db"
    path.parent.mkdir(parents=True, exist_ok=True)
    return str(path)


def local_health() -> bool:
    db_path = get_sqlite_path()
    if not os.path.exists(db_path):
        return False

    with sqlite3.connect(db_path) as conn:
        row = conn.execute(
            "SELECT name FROM sqlite_master WHERE type='table' AND name='parsed_documents'"
        ).fetchone()
        return row is not None


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


def local_search(q: str, mode: Literal["bm25", "boolean"], page: int, size: int) -> tuple[int, list[dict]]:
    db_path = get_sqlite_path()
    terms = [part.lower() for part in q.split() if part.strip()]
    if not terms:
        return 0, []

    if not os.path.exists(db_path):
        return 0, []

    with sqlite3.connect(db_path) as conn:
        conn.row_factory = sqlite3.Row
        rows = conn.execute(
            """
            SELECT
                p.id,
                COALESCE(p.title, '') AS title,
                COALESCE(p.body_text, '') AS body_text,
                COALESCE(p.cleaned_text, '') AS cleaned_text,
                p.url,
                p.processed_at,
                COALESCE(s.name, '') AS source
            FROM parsed_documents p
            LEFT JOIN raw_documents r ON r.id = p.raw_document_id
            LEFT JOIN sources s ON s.id = r.source_id
            """
        ).fetchall()

    scored: list[dict] = []
    for row in rows:
        title = row["title"] or ""
        body = row["body_text"] or ""
        cleaned = row["cleaned_text"] or ""
        haystack = f"{title} {cleaned} {body}".lower()

        if mode == "boolean" and not all(term in haystack for term in terms):
            continue
        if mode != "boolean" and not any(term in haystack for term in terms):
            continue

        title_l = title.lower()
        score = float(sum(haystack.count(term) for term in terms) + 2 * sum(title_l.count(term) for term in terms))
        if score <= 0:
            continue

        processed_at = row["processed_at"] or datetime.utcnow().isoformat()
        scored.append(
            {
                "id": str(row["id"]),
                "title": title,
                "body": body,
                "source": row["source"],
                "published_at": str(processed_at),
                "score": score,
                "url": row["url"],
            }
        )

    scored.sort(key=lambda item: item["score"], reverse=True)
    total = len(scored)
    start = (page - 1) * size
    end = start + size
    return total, scored[start:end]
