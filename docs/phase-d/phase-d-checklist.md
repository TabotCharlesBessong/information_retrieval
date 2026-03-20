# Phase D Checklist

## Roadmap Activity Coverage

- [x] Add query transformation, spell suggestions, and refinement.
- [x] Implement phrase queries, filters, and faceting.
- [x] Extend ranking with probabilistic mode and baseline comparison output.
- [ ] Build UI features for snippets and relevance-oriented interaction.

## Validation Steps

- [ ] `/search` returns refinement metadata (`normalized_query`, `suggested_query`, `expanded_terms`).
- [ ] `/search` supports `phrase`, `source`, and date filters.
- [ ] `/search` returns source facet counts when `facets=true`.
- [ ] `/search` supports `mode=probabilistic`.
- [ ] `/search/suggest` returns candidate spell/refinement suggestions.
- [ ] `benchmark_retrieval.py` produces both results and comparison JSON files.
