from __future__ import annotations

import json
import statistics
import time
from datetime import UTC, datetime
from pathlib import Path

from eval_common import DEFAULT_QUERIES, retrieve_results
from search_backend import get_search_backend

PHASE_E_DIR = Path(__file__).resolve().parents[3] / "docs" / "phase-e"


def _percentile(sorted_values: list[float], q: float) -> float:
    if not sorted_values:
        return 0.0
    idx = int(round((len(sorted_values) - 1) * q))
    return sorted_values[idx]


def run_query_latency_benchmark(repetitions: int = 5, top_k: int = 10) -> dict:
    timings_by_mode: dict[str, list[float]] = {"bm25": [], "boolean": [], "probabilistic": []}

    total_queries = 0
    total_seconds = 0.0
    for _ in range(repetitions):
        for query in DEFAULT_QUERIES:
            qtext = query["text"]
            for mode in ("bm25", "boolean", "probabilistic"):
                t0 = time.perf_counter()
                _ = retrieve_results(qtext, mode=mode, size=top_k)
                elapsed = time.perf_counter() - t0
                timings_by_mode[mode].append(elapsed)
                total_queries += 1
                total_seconds += elapsed

    summary: dict[str, dict[str, float]] = {}
    for mode, values in timings_by_mode.items():
        sorted_values = sorted(values)
        summary[mode] = {
            "count": float(len(values)),
            "avg_ms": statistics.mean(values) * 1000 if values else 0.0,
            "p95_ms": _percentile(sorted_values, 0.95) * 1000 if values else 0.0,
            "min_ms": (sorted_values[0] * 1000) if values else 0.0,
            "max_ms": (sorted_values[-1] * 1000) if values else 0.0,
        }

    throughput_qps = (total_queries / total_seconds) if total_seconds > 0 else 0.0
    return {
        "latency": summary,
        "throughput_qps": throughput_qps,
        "total_queries": total_queries,
        "total_seconds": total_seconds,
    }


def run_indexing_time_check(limit: int = 1000) -> dict:
    backend = get_search_backend()
    if backend != "elasticsearch":
        return {
            "backend": backend,
            "indexing_time_seconds": None,
            "status": "skipped (indexing benchmark currently implemented for Elasticsearch mode)",
        }

    from app.pipeline.src.index_documents import bulk_index, ensure_index, get_es, load_documents

    t0 = time.perf_counter()
    es = get_es()
    ensure_index(es)
    docs = load_documents(limit=limit)
    indexed = bulk_index(es, docs)
    elapsed = time.perf_counter() - t0
    return {
        "backend": backend,
        "documents_loaded": len(docs),
        "documents_indexed": indexed,
        "indexing_time_seconds": elapsed,
        "docs_per_second": (indexed / elapsed) if elapsed > 0 else 0.0,
        "status": "ok",
    }


def main() -> None:
    PHASE_E_DIR.mkdir(parents=True, exist_ok=True)

    efficiency = {
        "generated_at": datetime.now(UTC).isoformat(),
        "query_performance": run_query_latency_benchmark(repetitions=5, top_k=10),
        "indexing_performance": run_indexing_time_check(limit=1000),
    }

    ts = datetime.now(UTC).strftime("%Y%m%d_%H%M%S")
    out_path = PHASE_E_DIR / f"efficiency_report_{ts}.json"
    with out_path.open("w", encoding="utf-8") as fp:
        json.dump(efficiency, fp, indent=2)

    print(f"Efficiency report written: {out_path}")


if __name__ == "__main__":
    main()
