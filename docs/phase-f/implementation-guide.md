# Phase F Implementation Guide

Phase F introduces filtering, recommendation, and release-hardening artifacts.

## 1. Filtering module (rule-based + profile-aware)

Implemented in:
1. `app/api/src/filtering_recommendation.py`
2. `app/api/src/main.py` (`GET /search`)

### Rule-based filters
`GET /search` now supports:
1. `must_include`: terms that must exist in title/body.
2. `exclude_terms`: terms that exclude documents.
3. `exclude_source`: source-level block list.

### Profile-aware behavior
`GET /search` also supports:
1. `profile_interests`: boosts documents containing profile terms.
2. `profile_preferred_sources`: boosts preferred publishers.
3. `profile_excluded_sources`: excludes disallowed publishers.

Response includes:
1. `filtering_summary` with dropped/kept counts.
2. `facets` recomputed after filtering.

## 2. Recommendation prototype (content-based)

Implemented in:
1. `app/api/src/filtering_recommendation.py`
2. `app/api/src/search_backend.py` (`get_document_by_id`)
3. `app/api/src/main.py` (`GET /recommendations`)

Endpoint:
`GET /recommendations?seed_doc_id=<id>&size=10`

Behavior:
1. Loads seed document by ID.
2. Fetches candidate documents from active backend.
3. Uses token-overlap similarity (Jaccard-like) for ranking.
4. Returns recommendations with explainability reason (`shared terms: ...`).

## 3. API examples

```bash
curl "http://localhost:8000/search?q=african%20fintech&must_include=funding&exclude_source=WeeTracker&profile_interests=payments&profile_preferred_sources=TechCabal"
curl "http://localhost:8000/recommendations?seed_doc_id=3&size=5"
```

## 4. Final hardening notes

1. Keep `.data/` and caches ignored in git.
2. Run Phase E scripts after major ranking/filter changes.
3. Keep roadmap/checklists updated per release branch.
