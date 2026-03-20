from __future__ import annotations

import re
from typing import Iterable


TOKEN_RE = re.compile(r"[a-zA-Z0-9]{2,}")


def _tokens(text: str) -> set[str]:
    return {tok.lower() for tok in TOKEN_RE.findall(text or "")}


def _norm_list(values: Iterable[str] | None) -> list[str]:
    if not values:
        return []
    cleaned = [v.strip().lower() for v in values if v and v.strip()]
    return list(dict.fromkeys(cleaned))


def apply_filters(
    rows: list[dict],
    must_terms: list[str] | None,
    exclude_terms: list[str] | None,
    blocked_sources: list[str] | None,
) -> tuple[list[dict], dict[str, int]]:
    must = _norm_list(must_terms)
    excluded = _norm_list(exclude_terms)
    blocked = set(_norm_list(blocked_sources))

    kept: list[dict] = []
    dropped_source = 0
    dropped_excluded = 0
    dropped_must = 0

    for row in rows:
        source = str(row.get("source", "")).strip().lower()
        haystack = f"{row.get('title', '')} {row.get('body', '')}".lower()

        if blocked and source in blocked:
            dropped_source += 1
            continue

        if excluded and any(term in haystack for term in excluded):
            dropped_excluded += 1
            continue

        if must and not all(term in haystack for term in must):
            dropped_must += 1
            continue

        kept.append(row)

    summary = {
        "input_count": len(rows),
        "kept_count": len(kept),
        "dropped_source": dropped_source,
        "dropped_excluded_terms": dropped_excluded,
        "dropped_missing_must_terms": dropped_must,
    }
    return kept, summary


def rerank_with_profile(
    rows: list[dict],
    interests: list[str] | None,
    preferred_sources: list[str] | None,
) -> list[dict]:
    terms = _norm_list(interests)
    preferred = set(_norm_list(preferred_sources))

    if not terms and not preferred:
        return rows

    scored: list[dict] = []
    for row in rows:
        base = float(row.get("score", 0.0) or 0.0)
        text = f"{row.get('title', '')} {row.get('body', '')}".lower()
        source = str(row.get("source", "")).strip().lower()

        interest_bonus = 0.0
        for term in terms:
            if term in text:
                interest_bonus += 0.15

        source_bonus = 0.2 if source in preferred else 0.0
        row_copy = dict(row)
        row_copy["score"] = base + interest_bonus + source_bonus
        scored.append(row_copy)

    scored.sort(key=lambda item: float(item.get("score", 0.0)), reverse=True)
    return scored


def source_facets(rows: list[dict], limit: int = 20) -> dict[str, list[dict[str, int | str]]]:
    counts: dict[str, int] = {}
    for row in rows:
        source = str(row.get("source", ""))
        counts[source] = counts.get(source, 0) + 1

    ordered = sorted(counts.items(), key=lambda item: item[1], reverse=True)[:limit]
    return {"sources": [{"value": src, "count": cnt} for src, cnt in ordered]}


def recommend_content_based(
    seed_doc: dict,
    candidates: list[dict],
    top_k: int,
    blocked_sources: list[str] | None = None,
) -> list[dict]:
    blocked = set(_norm_list(blocked_sources))

    seed_text = f"{seed_doc.get('title', '')} {seed_doc.get('body', '')}"
    seed_tokens = _tokens(seed_text)
    seed_id = str(seed_doc.get("id", ""))

    scored: list[tuple[float, dict]] = []
    for row in candidates:
        doc_id = str(row.get("id", ""))
        if doc_id == seed_id:
            continue

        source = str(row.get("source", "")).strip().lower()
        if blocked and source in blocked:
            continue

        cand_text = f"{row.get('title', '')} {row.get('body', '')}"
        cand_tokens = _tokens(cand_text)
        if not cand_tokens:
            continue

        inter = seed_tokens & cand_tokens
        union = seed_tokens | cand_tokens
        similarity = (len(inter) / len(union)) if union else 0.0

        if similarity <= 0:
            continue

        overlap = sorted(inter)[:5]
        row_copy = dict(row)
        row_copy["score"] = float(similarity)
        row_copy["reason"] = "shared terms: " + ", ".join(overlap)
        scored.append((similarity, row_copy))

    scored.sort(key=lambda item: item[0], reverse=True)
    return [row for _, row in scored[:top_k]]
