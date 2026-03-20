from __future__ import annotations

import json
from datetime import datetime

from search_backend import INDEX_NAME, build_query, get_es

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
    for q in QUERIES:
        output[q] = {}
        for mode in ("bm25", "boolean"):
            res = es.search(index=INDEX_NAME, body=build_query(q, mode), size=10)
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

    ts = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
    out_path = f"benchmark_results_{ts}.json"
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(output, f, indent=2)

    print(f"Benchmark written: {out_path}")


if __name__ == "__main__":
    run()
