from __future__ import annotations

import csv
import json
import math
from datetime import UTC, datetime
from pathlib import Path

from eval_common import QueryMode, retrieve_results

PHASE_E_DIR = Path(__file__).resolve().parents[3] / "docs" / "phase-e"
QUERIES_PATH = PHASE_E_DIR / "eval_queries.json"
QRELS_PATH = PHASE_E_DIR / "qrels.csv"


def precision_at_k(relevances: list[int], k: int) -> float:
    if k <= 0:
        return 0.0
    rel = relevances[:k]
    return sum(1 for r in rel if r > 0) / float(k)


def recall_at_k(relevances: list[int], total_relevant: int, k: int) -> float:
    if total_relevant <= 0:
        return 0.0
    rel = relevances[:k]
    return sum(1 for r in rel if r > 0) / float(total_relevant)


def ap_at_k(relevances: list[int], total_relevant: int, k: int) -> float:
    if total_relevant <= 0:
        return 0.0
    rel = relevances[:k]
    hit_count = 0
    precision_sum = 0.0
    for idx, r in enumerate(rel, start=1):
        if r > 0:
            hit_count += 1
            precision_sum += hit_count / float(idx)
    return precision_sum / float(total_relevant)


def dcg_at_k(relevances: list[int], k: int) -> float:
    score = 0.0
    for idx, rel in enumerate(relevances[:k], start=1):
        gain = (2**rel - 1)
        score += gain / math.log2(idx + 1)
    return score


def ndcg_at_k(relevances: list[int], ideal_relevances: list[int], k: int) -> float:
    dcg = dcg_at_k(relevances, k)
    idcg = dcg_at_k(ideal_relevances, k)
    if idcg <= 0:
        return 0.0
    return dcg / idcg


def mrr_at_k(relevances: list[int], k: int) -> float:
    for idx, r in enumerate(relevances[:k], start=1):
        if r > 0:
            return 1.0 / float(idx)
    return 0.0


def load_queries() -> list[dict[str, str]]:
    with QUERIES_PATH.open("r", encoding="utf-8") as fp:
        return json.load(fp)


def load_qrels() -> tuple[dict[tuple[str, str], int], dict[str, dict[str, int]]]:
    if not QRELS_PATH.exists():
        raise FileNotFoundError(
            f"Missing qrels file: {QRELS_PATH}. Run build_eval_corpus.py and fill qrels.csv first."
        )

    qrels_mode_agnostic: dict[tuple[str, str], int] = {}
    judged_counts: dict[str, dict[str, int]] = {}
    with QRELS_PATH.open("r", encoding="utf-8", newline="") as fp:
        reader = csv.DictReader(fp)
        for row in reader:
            qid = (row.get("query_id") or "").strip()
            doc_id = (row.get("doc_id") or "").strip()
            relevance_str = (row.get("relevance") or "").strip()
            if not qid or not doc_id or relevance_str == "":
                continue

            relevance = int(relevance_str)
            key = (qid, doc_id)
            qrels_mode_agnostic[key] = max(relevance, qrels_mode_agnostic.get(key, 0))

            bucket = judged_counts.setdefault(qid, {"judged": 0, "relevant": 0})
            bucket["judged"] += 1
            if relevance > 0:
                bucket["relevant"] += 1

    return qrels_mode_agnostic, judged_counts


def evaluate(k_values: list[int] | None = None) -> dict:
    if not k_values:
        k_values = [5, 10]

    queries = load_queries()
    qrels, judged_counts = load_qrels()

    per_query: dict[str, dict[str, dict[str, float]]] = {}
    aggregate: dict[str, dict[str, float]] = {}

    for mode in ("bm25", "boolean", "probabilistic"):
        mode_metrics: dict[str, list[float]] = {
            "p@5": [],
            "p@10": [],
            "r@5": [],
            "r@10": [],
            "map@10": [],
            "ndcg@10": [],
            "mrr@10": [],
            "hits@10": [],
        }

        for query_item in queries:
            qid = query_item["id"]
            qtext = query_item["text"]
            results = retrieve_results(qtext, mode=mode, size=max(k_values))

            rel_lookup = {doc_id: rel for (rqid, doc_id), rel in qrels.items() if rqid == qid}
            total_relevant = sum(1 for rel in rel_lookup.values() if rel > 0)

            ranked_rels = [rel_lookup.get(str(row.get("id", "")), 0) for row in results]
            ideal_rels = sorted(rel_lookup.values(), reverse=True)

            p5 = precision_at_k(ranked_rels, 5)
            p10 = precision_at_k(ranked_rels, 10)
            r5 = recall_at_k(ranked_rels, total_relevant, 5)
            r10 = recall_at_k(ranked_rels, total_relevant, 10)
            map10 = ap_at_k(ranked_rels, total_relevant, 10)
            ndcg10 = ndcg_at_k(ranked_rels, ideal_rels, 10)
            mrr10 = mrr_at_k(ranked_rels, 10)
            hits10 = 1.0 if any(rel > 0 for rel in ranked_rels[:10]) else 0.0

            per_query.setdefault(mode, {})[qid] = {
                "p@5": p5,
                "p@10": p10,
                "r@5": r5,
                "r@10": r10,
                "map@10": map10,
                "ndcg@10": ndcg10,
                "mrr@10": mrr10,
                "hits@10": hits10,
            }

            mode_metrics["p@5"].append(p5)
            mode_metrics["p@10"].append(p10)
            mode_metrics["r@5"].append(r5)
            mode_metrics["r@10"].append(r10)
            mode_metrics["map@10"].append(map10)
            mode_metrics["ndcg@10"].append(ndcg10)
            mode_metrics["mrr@10"].append(mrr10)
            mode_metrics["hits@10"].append(hits10)

        aggregate[mode] = {
            metric: (sum(values) / len(values) if values else 0.0)
            for metric, values in mode_metrics.items()
        }

    report = {
        "generated_at": datetime.now(UTC).isoformat(),
        "queries_file": str(QUERIES_PATH),
        "qrels_file": str(QRELS_PATH),
        "judged_counts": judged_counts,
        "aggregate": aggregate,
        "per_query": per_query,
    }
    return report


def main() -> None:
    report = evaluate(k_values=[5, 10])
    PHASE_E_DIR.mkdir(parents=True, exist_ok=True)

    ts = datetime.now(UTC).strftime("%Y%m%d_%H%M%S")
    out_path = PHASE_E_DIR / f"effectiveness_report_{ts}.json"
    with out_path.open("w", encoding="utf-8") as fp:
        json.dump(report, fp, indent=2)

    print(f"Effectiveness report written: {out_path}")


if __name__ == "__main__":
    main()
