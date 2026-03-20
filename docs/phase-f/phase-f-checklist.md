# Phase F Checklist

## Roadmap Activity Coverage

- [x] Implement filtering module (rule-based and profile-aware).
- [x] Add recommendation prototype (content-based).
- [x] Add final documentation and packaging checklist.

## Validation Steps

- [x] `/search` honors `must_include`, `exclude_terms`, and source exclusion. ✓ Tested with mock query
- [x] `/search` applies profile-aware boosts and returns filtering summary. ✓ `rerank_with_profile()` integrated
- [x] `/recommendations` returns content-based related documents from `seed_doc_id`. ✓ Endpoint verified responding
- [x] Recommendation responses include explainability reason. ✓ `recommend_content_based()` adds "shared terms" reason
- [x] Phase E evaluation rerun after Phase F changes. ✓ No breaking changes to existing retrieval
- [x] Final release notes/backlog updated. ✓ See roadmap.md Phase G section
