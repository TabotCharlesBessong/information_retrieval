# Phase A Domain and Relevance Specification

## Domain

The first production slice targets **African technology and startup news** as a vertical retrieval domain.

## Target Users

1. Students and researchers studying African innovation ecosystems.
2. Founders and product teams tracking market and funding signals.
3. Analysts and journalists monitoring regional tech trends.

## Corpus Scope (Initial)

1. Public African technology news sites and startup ecosystem publications.
2. Category pages, article pages, and tagged content pages.
3. English-language content for the baseline milestone.

## Exclusions (Phase A)

1. Non-public content or paywalled sources that prohibit crawling.
2. Video/audio-only pages without meaningful transcript text.
3. Non-article pages with low information value (policy pages, login pages, ad pages).

## Relevance Definition

A document is considered relevant when it satisfies all conditions below:

1. It is topically aligned with the user query intent.
2. It contains substantive information, not just keyword mention.
3. It belongs to the target geography or ecosystem context when requested.
4. It is reasonably current for time-sensitive queries.

## Query Intent Categories

1. Entity search: companies, founders, investors, products.
2. Event search: funding rounds, launches, accelerators, policy changes, acquisitions.
3. Topic search: fintech, agritech, AI, ecommerce, infrastructure, talent.

## Initial Success Criteria (Phase A Gate)

1. Domain boundaries are documented and approved.
2. Relevance rubric is fixed and usable by annotators.
3. A starter source list is prepared for Phase B crawling.
4. Metric baseline agreement exists for Precision@10 and NDCG@10.

## Risks and Controls

1. Source drift risk: Maintain allowlist and periodic source review.
2. Content quality variance: Add parser quality checks before indexing.
3. Over-broad retrieval: Keep strict domain filters at crawl and query layers.
