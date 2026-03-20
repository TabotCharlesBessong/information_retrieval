from __future__ import annotations

import re
from collections import Counter

WORD_RE = re.compile(r"[a-zA-Z][a-zA-Z0-9'-]+")

STOPWORDS = {
    "a",
    "an",
    "and",
    "are",
    "as",
    "at",
    "be",
    "by",
    "for",
    "from",
    "has",
    "he",
    "in",
    "is",
    "it",
    "its",
    "of",
    "on",
    "that",
    "the",
    "to",
    "was",
    "were",
    "will",
    "with",
}


def tokenize(text: str) -> list[str]:
    return [w.lower() for w in WORD_RE.findall(text)]


def remove_stopwords(tokens: list[str]) -> list[str]:
    return [t for t in tokens if t not in STOPWORDS]


def stem_token(token: str) -> str:
    # Lightweight stemming heuristic to avoid heavy runtime dependencies.
    for suffix in ("ingly", "edly", "ing", "ed", "ies", "s"):
        if token.endswith(suffix) and len(token) > len(suffix) + 2:
            if suffix == "ies":
                return token[: -len(suffix)] + "y"
            return token[: -len(suffix)]
    return token


def stem_tokens(tokens: list[str]) -> list[str]:
    return [stem_token(t) for t in tokens]


def ngrams(tokens: list[str], n: int) -> list[str]:
    if n <= 1:
        return tokens
    return [" ".join(tokens[i : i + n]) for i in range(len(tokens) - n + 1)]


def zipf_table(tokens: list[str], top_n: int = 50) -> list[tuple[str, int]]:
    return Counter(tokens).most_common(top_n)
