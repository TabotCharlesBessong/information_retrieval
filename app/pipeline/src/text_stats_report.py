from __future__ import annotations

from collections import Counter
from sqlalchemy import asc

from db import get_session
from models import ParsedDocument
from text_processing import tokenize


def get_corpus_tokens(limit_docs: int = 5000) -> list[str]:
    with get_session() as session:
        rows = (
            session.query(ParsedDocument.cleaned_text)
            .order_by(asc(ParsedDocument.id))
            .limit(limit_docs)
            .all()
        )

    tokens: list[str] = []
    for (text,) in rows:
        if text:
            tokens.extend(tokenize(text))
    return tokens


def heaps_points(tokens: list[str], step: int = 200) -> list[tuple[int, int]]:
    points: list[tuple[int, int]] = []
    seen: set[str] = set()
    for i, token in enumerate(tokens, start=1):
        seen.add(token)
        if i % step == 0:
            points.append((i, len(seen)))
    if not points and tokens:
        points.append((len(tokens), len(seen)))
    return points


def main() -> None:
    tokens = get_corpus_tokens()
    if not tokens:
        print("No parsed tokens available. Run parse_documents.py first.")
        return

    total = len(tokens)
    vocab = len(set(tokens))
    freq = Counter(tokens)

    print("=== Text Statistics ===")
    print(f"Total tokens: {total}")
    print(f"Vocabulary size: {vocab}")
    print("Top 20 tokens (Zipf head):")
    for token, count in freq.most_common(20):
        print(f"  {token}: {count}")

    print("Heaps growth points (n_tokens, vocab_size):")
    for n, v in heaps_points(tokens, step=500):
        print(f"  ({n}, {v})")


if __name__ == "__main__":
    main()
