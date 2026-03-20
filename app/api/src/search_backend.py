from __future__ import annotations

import math
import os
import sqlite3
from datetime import datetime
from difflib import get_close_matches
from pathlib import Path
from typing import Literal

from elasticsearch import Elasticsearch

INDEX_NAME = os.getenv("ELASTICSEARCH_INDEX", "documents")

DOMAIN_TERMS = {
    "africa",
    "african",
    "startup",
    "startups",
    "fintech",
    "insurtech",
    "healthtech",
    "edtech",
    "funding",
    "investment",
    "vc",
    "venture",
    "accelerator",
    "incubator",
    "nigeria",
    "kenya",
    "ghana",
    "south",
    "africa",
    "lagos",
    "nairobi",
    "cairo",
    "payments",
    "mobile",
    "banking",
    "ai",
}

SYNONYM_MAP: dict[str, list[str]] = {
    "vc": ["venture", "capital"],
    "fundraise": ["funding", "investment"],
    "startup": ["startups", "venture"],
    "fintech": ["payments", "banking"],
    "ai": ["artificial", "intelligence"],
}


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


def normalize_query(q: str) -> str:
    return " ".join(q.lower().strip().split())


def extract_phrase(q: str) -> str | None:
    if '"' not in q:
        return None
    parts = q.split('"')
    if len(parts) < 3:
        return None
    phrase = " ".join(parts[1].split())
    return phrase if phrase else None


def query_terms(q: str) -> list[str]:
    compact = normalize_query(q.replace('"', " "))
    return [term for term in compact.split(" ") if term]


def refine_query(q: str) -> dict[str, object]:
    normalized = normalize_query(q)
    terms = query_terms(normalized)

    corrected_terms: list[str] = []
    for term in terms:
        if len(term) <= 2 or term in DOMAIN_TERMS:
            corrected_terms.append(term)
            continue
        candidate = get_close_matches(term, sorted(DOMAIN_TERMS), n=1, cutoff=0.84)
        corrected_terms.append(candidate[0] if candidate else term)

    expanded_terms: list[str] = []
    for term in corrected_terms:
        expanded_terms.extend(SYNONYM_MAP.get(term, []))

    suggestion = " ".join(corrected_terms)
    refined = " ".join(corrected_terms + expanded_terms)
    return {
        "normalized_query": normalized,
        "suggested_query": suggestion,
        "expanded_terms": expanded_terms,
        "refined_query": refined,
    }


def build_extended_query(
    q: str,
    mode: Literal["bm25", "boolean", "probabilistic"],
    phrase: str | None,
    sources: list[str] | None,
    published_from: str | None,
    published_to: str | None,
    with_facets: bool,
) -> dict:
    refined = refine_query(q)
    effective_query = str(refined["refined_query"]).strip() or q

    if mode == "boolean":
        text_clause: dict = {
            "simple_query_string": {
                "query": effective_query,
                "fields": ["title^2", "body", "cleaned_text"],
                "default_operator": "and",
            }
        }
    else:
        text_clause = {
            "multi_match": {
                "query": effective_query,
                "fields": ["title^2", "body", "cleaned_text"],
                "type": "best_fields",
            }
        }

    must: list[dict] = [text_clause]
    filters: list[dict] = []

    if phrase:
        must.append(
            {
                "multi_match": {
                    "query": phrase,
                    "fields": ["title^3", "body", "cleaned_text"],
                    "type": "phrase",
                }
            }
        )

    if sources:
        filters.append({"terms": {"source": sources}})

    if published_from or published_to:
        range_filter: dict[str, str] = {}
        if published_from:
            range_filter["gte"] = published_from
        if published_to:
            range_filter["lte"] = published_to
        filters.append({"range": {"published_at": range_filter}})

    body: dict = {
        "query": {
            "bool": {
                "must": must,
                "filter": filters,
            }
        }
    }
    if with_facets:
        body["aggs"] = {"sources": {"terms": {"field": "source", "size": 20}}}
    return body


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


def local_search_extended(
    q: str,
    mode: Literal["bm25", "boolean", "probabilistic"],
    page: int,
    size: int,
    phrase: str | None,
    sources: list[str] | None,
    published_from: str | None,
    published_to: str | None,
    with_facets: bool,
) -> tuple[int, list[dict], dict[str, list[dict[str, int | str]]]]:
    db_path = get_sqlite_path()
    refined = refine_query(q)
    effective_query = str(refined["refined_query"]).strip() or q
    terms = query_terms(effective_query)
    if not terms:
        return 0, [], {"sources": []}

    if not os.path.exists(db_path):
        return 0, [], {"sources": []}

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

    phrase_l = phrase.lower() if phrase else None
    allowed_sources = {s.lower() for s in sources} if sources else None
    facets_counter: dict[str, int] = {}
    scored: list[dict] = []

    for row in rows:
        title = row["title"] or ""
        body = row["body_text"] or ""
        cleaned = row["cleaned_text"] or ""
        source = row["source"] or ""
        processed_at = str(row["processed_at"] or datetime.utcnow().isoformat())
        haystack = f"{title} {cleaned} {body}".lower()

        if allowed_sources and source.lower() not in allowed_sources:
            continue
        if published_from and processed_at < published_from:
            continue
        if published_to and processed_at > published_to:
            continue
        if phrase_l and phrase_l not in haystack:
            continue
        if mode == "boolean" and not all(term in haystack for term in terms):
            continue
        if mode != "boolean" and not any(term in haystack for term in terms):
            continue

        title_l = title.lower()
        if mode == "probabilistic":
            token_count = max(len(cleaned.split()), 1)
            score = 0.0
            for term in terms:
                tf = haystack.count(term)
                score += math.log((tf + 1.0) / (token_count + 1.0))
            score = math.exp(score / max(len(terms), 1))
        else:
            score = float(sum(haystack.count(term) for term in terms) + 2 * sum(title_l.count(term) for term in terms))

        if score <= 0:
            continue

        facets_counter[source] = facets_counter.get(source, 0) + 1
        scored.append(
            {
                "id": str(row["id"]),
                "title": title,
                "body": body,
                "source": source,
                "published_at": processed_at,
                "score": score,
                "url": row["url"],
            }
        )

    scored.sort(key=lambda item: float(item["score"]), reverse=True)
    total = len(scored)
    start = (page - 1) * size
    end = start + size

    facets: dict[str, list[dict[str, int | str]]] = {"sources": []}
    if with_facets:
        facets["sources"] = [
            {"value": name, "count": count}
            for name, count in sorted(facets_counter.items(), key=lambda item: item[1], reverse=True)
        ]
    return total, scored[start:end], facets


def local_suggestions(q: str, limit: int = 5) -> list[str]:
    terms = query_terms(q)
    if not terms:
        return []

    corpus = sorted(DOMAIN_TERMS)
    suggestions: list[str] = []
    for term in terms:
        if term in DOMAIN_TERMS:
            continue
        suggestions.extend(get_close_matches(term, corpus, n=2, cutoff=0.75))

    unique: list[str] = []
    seen: set[str] = set()
    for suggestion in suggestions:
        if suggestion in seen:
            continue
        seen.add(suggestion)
        unique.append(suggestion)
        if len(unique) >= limit:
            break
    return unique
