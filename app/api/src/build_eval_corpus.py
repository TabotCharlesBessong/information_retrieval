from __future__ import annotations

import csv
import json
from pathlib import Path

from eval_common import DEFAULT_QUERIES, retrieve_results

OUT_DIR = Path(__file__).resolve().parents[3] / "docs" / "phase-e"
QUERIES_PATH = OUT_DIR / "eval_queries.json"
QRELS_TEMPLATE_PATH = OUT_DIR / "qrels_template.csv"


def build_eval_corpus(top_k: int = 20) -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)

    with QUERIES_PATH.open("w", encoding="utf-8") as fp:
        json.dump(DEFAULT_QUERIES, fp, indent=2)

    header = [
        "query_id",
        "query_text",
        "mode",
        "rank",
        "doc_id",
        "url",
        "title",
        "source",
        "relevance",
    ]

    rows_written = 0
    with QRELS_TEMPLATE_PATH.open("w", encoding="utf-8", newline="") as fp:
        writer = csv.writer(fp)
        writer.writerow(header)

        for query_item in DEFAULT_QUERIES:
            qid = query_item["id"]
            qtext = query_item["text"]

            for mode in ("bm25", "boolean", "probabilistic"):
                results = retrieve_results(qtext, mode=mode, size=top_k)
                for rank, row in enumerate(results, start=1):
                    writer.writerow(
                        [
                            qid,
                            qtext,
                            mode,
                            rank,
                            row.get("id", ""),
                            row.get("url", ""),
                            row.get("title", ""),
                            row.get("source", ""),
                            "",  # Fill manually with integer relevance grades, e.g. 0/1/2.
                        ]
                    )
                    rows_written += 1

    print(f"Queries written: {QUERIES_PATH}")
    print(f"Qrels template written: {QRELS_TEMPLATE_PATH}")
    print(f"Candidate rows written: {rows_written}")


if __name__ == "__main__":
    build_eval_corpus(top_k=20)
