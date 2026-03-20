from __future__ import annotations

import json
from datetime import datetime

from search_backend import INDEX_NAME, build_extended_query, get_es

QUERIES = [
    "african fintech funding",
    "startup accelerator nigeria",
    "kenya ecommerce startup",
    "south africa ai startup",
]


def run() -> None:
    es = get_es()
    if not es.indices.exists(index=INDEX_NAME):
        print("Index does not exist. Run pipeline index_documents.py first.")
        return

    output: dict[str, dict[str, list[dict[str, str]]]] = {}
    comparison: dict[str, dict[str, float]] = {}
    for q in QUERIES:
        output[q] = {}
        for mode in ("bm25", "boolean", "probabilistic"):
            body = build_extended_query(
                q=q,
                mode=mode,
                phrase=None,
                sources=None,
                published_from=None,
                published_to=None,
                with_facets=False,
            )
            res = es.search(index=INDEX_NAME, body=body, size=10)
            hits = res.get("hits", {}).get("hits", [])
            output[q][mode] = [
                {
                    "id": h.get("_id", ""),
                    "score": str(h.get("_score", 0.0)),
                    "title": h.get("_source", {}).get("title", ""),
                    "url": h.get("_source", {}).get("url", ""),
                }
                for h in hits
            ]

        bm25_ids = {row["id"] for row in output[q]["bm25"]}
        boolean_ids = {row["id"] for row in output[q]["boolean"]}
        probabilistic_ids = {row["id"] for row in output[q]["probabilistic"]}
        comparison[q] = {
            "overlap_bm25_boolean": round(len(bm25_ids & boolean_ids) / 10.0, 3),
            "overlap_bm25_probabilistic": round(len(bm25_ids & probabilistic_ids) / 10.0, 3),
        }

    ts = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
    out_path = f"benchmark_results_{ts}.json"
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(output, f, indent=2)

    comparison_path = f"benchmark_comparison_{ts}.json"
    with open(comparison_path, "w", encoding="utf-8") as f:
        json.dump(comparison, f, indent=2)

    print(f"Benchmark written: {out_path}")
    print(f"Comparison written: {comparison_path}")


if __name__ == "__main__":
    run()
