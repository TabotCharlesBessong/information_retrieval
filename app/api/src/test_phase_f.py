from __future__ import annotations

import unittest
from unittest.mock import patch

from fastapi import HTTPException

from app.api.src.filtering_recommendation import (
    apply_filters,
    recommend_content_based,
    rerank_with_profile,
)
from app.api.src.main import recommendations, search


class FilteringRecommendationTests(unittest.TestCase):
    def test_apply_filters_tracks_drop_reason_counts(self) -> None:
        rows = [
            {"id": "1", "title": "Fintech Funding", "body": "Series A in Lagos", "source": "TechCabal"},
            {"id": "2", "title": "Gaming News", "body": "Esports update", "source": "GamesHub"},
            {"id": "3", "title": "Startup Funding", "body": "Kenya round", "source": "BlockedSource"},
            {"id": "4", "title": "Fintech Expansion", "body": "Payments and banking", "source": "Techpoint"},
        ]

        kept, summary = apply_filters(
            rows=rows,
            must_terms=["fintech"],
            exclude_terms=["esports"],
            blocked_sources=["blockedsource"],
        )

        self.assertEqual([r["id"] for r in kept], ["1", "4"])
        self.assertEqual(summary["input_count"], 4)
        self.assertEqual(summary["kept_count"], 2)
        self.assertEqual(summary["dropped_source"], 1)
        self.assertEqual(summary["dropped_excluded_terms"], 1)
        self.assertEqual(summary["dropped_missing_must_terms"], 0)

    def test_rerank_with_profile_boosts_interest_and_source(self) -> None:
        rows = [
            {"id": "1", "title": "General News", "body": "Market update", "source": "Alpha", "score": 1.0},
            {"id": "2", "title": "Payments Deep Dive", "body": "Fintech and banking", "source": "Beta", "score": 0.9},
            {"id": "3", "title": "Funding Watch", "body": "Seed stage fintech", "source": "Alpha", "score": 0.95},
        ]

        reranked = rerank_with_profile(
            rows=rows,
            interests=["fintech", "payments"],
            preferred_sources=["alpha"],
        )

        self.assertEqual(reranked[0]["id"], "3")
        self.assertGreater(reranked[0]["score"], rows[2]["score"])

    def test_recommend_content_based_returns_reason(self) -> None:
        seed = {"id": "10", "title": "African fintech funding", "body": "payments banking nigeria"}
        candidates = [
            {
                "id": "11",
                "title": "Banking startup raises funding",
                "body": "nigeria payments expansion",
                "source": "TechCabal",
                "published_at": "2026-03-01",
                "url": "https://example.com/11",
                "score": 0.0,
            },
            {
                "id": "12",
                "title": "Agriculture roundup",
                "body": "crop yields and weather",
                "source": "AgriNews",
                "published_at": "2026-03-02",
                "url": "https://example.com/12",
                "score": 0.0,
            },
        ]

        out = recommend_content_based(seed_doc=seed, candidates=candidates, top_k=5)

        self.assertEqual(len(out), 1)
        self.assertEqual(out[0]["id"], "11")
        self.assertIn("shared terms:", out[0]["reason"])


class PhaseFEndpointTests(unittest.TestCase):
    @patch("app.api.src.main.local_search_extended")
    @patch("app.api.src.main.get_search_backend")
    def test_search_applies_filtering_and_profile_summary(self, backend_mock, local_search_mock) -> None:
        backend_mock.return_value = "sqlite"
        local_search_mock.return_value = (
            4,
            [
                {
                    "id": "1",
                    "title": "Payments growth",
                    "body": "fintech in kenya",
                    "source": "TechCabal",
                    "published_at": "2026-03-01",
                    "score": 1.0,
                    "url": "https://example.com/1",
                },
                {
                    "id": "2",
                    "title": "Other update",
                    "body": "random topic",
                    "source": "Blocked",
                    "published_at": "2026-03-01",
                    "score": 2.0,
                    "url": "https://example.com/2",
                },
                {
                    "id": "3",
                    "title": "Esports feature",
                    "body": "gaming only",
                    "source": "Techpoint",
                    "published_at": "2026-03-01",
                    "score": 2.0,
                    "url": "https://example.com/3",
                },
            ],
            {"sources": []},
        )

        response = search(
            q="fintech",
            mode="bm25",
            must_include=["fintech"],
            exclude_terms=["gaming"],
            exclude_source=["Blocked"],
            profile_interests=["payments"],
            profile_preferred_sources=["TechCabal"],
            profile_excluded_sources=None,
            source=None,
            phrase=None,
            published_from=None,
            published_to=None,
            facets=True,
            page=1,
            size=10,
        )

        self.assertEqual(response.total, 1)
        self.assertEqual(response.items[0].id, "1")
        self.assertEqual(response.filtering_summary["dropped_source"], 1)
        self.assertEqual(response.filtering_summary["dropped_excluded_terms"], 1)

    @patch("app.api.src.main.get_document_by_id")
    @patch("app.api.src.main.local_search_extended")
    @patch("app.api.src.main.get_search_backend")
    def test_recommendations_returns_explainable_items(self, backend_mock, local_search_mock, get_doc_mock) -> None:
        backend_mock.return_value = "sqlite"
        get_doc_mock.return_value = {
            "id": "3",
            "title": "African fintech funding",
            "body": "payments growth in nigeria",
            "source": "TechCabal",
            "published_at": "2026-03-01",
            "url": "https://example.com/3",
            "score": 0.0,
        }
        local_search_mock.return_value = (
            3,
            [
                {
                    "id": "4",
                    "title": "Funding expands",
                    "body": "nigeria payments and fintech",
                    "source": "Techpoint",
                    "published_at": "2026-03-02",
                    "score": 3.0,
                    "url": "https://example.com/4",
                },
                {
                    "id": "5",
                    "title": "Sports update",
                    "body": "football results",
                    "source": "SportsDaily",
                    "published_at": "2026-03-02",
                    "score": 2.0,
                    "url": "https://example.com/5",
                },
            ],
            {"sources": []},
        )

        response = recommendations(seed_doc_id="3", q=None, profile_excluded_sources=None, size=5)

        self.assertEqual(response.seed_doc_id, "3")
        self.assertGreaterEqual(response.total, 1)
        self.assertIn("shared terms:", response.items[0].reason)

    @patch("app.api.src.main.get_document_by_id")
    def test_recommendations_404_when_seed_missing(self, get_doc_mock) -> None:
        get_doc_mock.return_value = None

        with self.assertRaises(HTTPException) as raised:
            recommendations(seed_doc_id="missing", q=None, profile_excluded_sources=None, size=5)

        self.assertEqual(raised.exception.status_code, 404)


if __name__ == "__main__":
    unittest.main()
