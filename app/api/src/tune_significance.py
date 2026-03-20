from __future__ import annotations

import json
import random
from datetime import UTC, datetime
from pathlib import Path

PHASE_E_DIR = Path(__file__).resolve().parents[3] / "docs" / "phase-e"


def _latest_effectiveness_report() -> Path:
    candidates = sorted(PHASE_E_DIR.glob("effectiveness_report_*.json"))
    if not candidates:
        raise FileNotFoundError(
            f"No effectiveness report found in {PHASE_E_DIR}. Run evaluate_metrics.py first."
        )
    return candidates[-1]


def randomization_test(metric_a: list[float], metric_b: list[float], iterations: int = 5000) -> float:
    if len(metric_a) != len(metric_b):
        raise ValueError("Metric vectors must have the same length for paired significance test")

    observed = abs(sum(a - b for a, b in zip(metric_a, metric_b)) / max(len(metric_a), 1))
    if observed == 0:
        return 1.0

    extreme = 0
    pairs = list(zip(metric_a, metric_b))
    for _ in range(iterations):
        sampled_diffs = []
        for a, b in pairs:
            if random.random() < 0.5:
                sampled_diffs.append(a - b)
            else:
                sampled_diffs.append(b - a)
        sampled = abs(sum(sampled_diffs) / max(len(sampled_diffs), 1))
        if sampled >= observed:
            extreme += 1

    return (extreme + 1) / float(iterations + 1)


def main() -> None:
    PHASE_E_DIR.mkdir(parents=True, exist_ok=True)
    report_path = _latest_effectiveness_report()
    with report_path.open("r", encoding="utf-8") as fp:
        report = json.load(fp)

    aggregate = report.get("aggregate", {})
    per_query = report.get("per_query", {})

    mode_ranking = sorted(
        (
            {
                "mode": mode,
                "ndcg@10": float(values.get("ndcg@10", 0.0)),
                "map@10": float(values.get("map@10", 0.0)),
            }
            for mode, values in aggregate.items()
        ),
        key=lambda row: (row["ndcg@10"], row["map@10"]),
        reverse=True,
    )

    bm25_by_query = per_query.get("bm25", {})
    probabilistic_by_query = per_query.get("probabilistic", {})
    common_qids = sorted(set(bm25_by_query.keys()) & set(probabilistic_by_query.keys()))

    bm25_scores = [float(bm25_by_query[qid].get("ndcg@10", 0.0)) for qid in common_qids]
    probabilistic_scores = [float(probabilistic_by_query[qid].get("ndcg@10", 0.0)) for qid in common_qids]

    p_value = randomization_test(probabilistic_scores, bm25_scores, iterations=5000) if common_qids else 1.0

    tuning_report = {
        "generated_at": datetime.now(UTC).isoformat(),
        "source_effectiveness_report": str(report_path),
        "best_mode_by_ndcg_map": mode_ranking[0] if mode_ranking else None,
        "mode_ranking": mode_ranking,
        "significance": {
            "comparison": "probabilistic vs bm25 on ndcg@10",
            "queries_compared": common_qids,
            "p_value": p_value,
            "alpha": 0.05,
            "is_significant": bool(p_value < 0.05),
            "method": "paired randomization test",
        },
    }

    ts = datetime.now(UTC).strftime("%Y%m%d_%H%M%S")
    out_path = PHASE_E_DIR / f"tuning_significance_{ts}.json"
    with out_path.open("w", encoding="utf-8") as fp:
        json.dump(tuning_report, fp, indent=2)

    print(f"Tuning/significance report written: {out_path}")


if __name__ == "__main__":
    main()
