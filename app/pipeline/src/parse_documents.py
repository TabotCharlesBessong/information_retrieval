from __future__ import annotations

from bs4 import BeautifulSoup
from sqlalchemy import asc

from db import get_session
from models import ParsedDocument, RawDocument
from text_processing import ngrams, remove_stopwords, stem_tokens, tokenize


def normalize_whitespace(text: str) -> str:
    return " ".join(text.split())


def parse_html(html: str) -> tuple[str, str]:
    soup = BeautifulSoup(html, "lxml")

    for tag in soup(["script", "style", "noscript", "nav", "footer", "header"]):
        tag.decompose()

    title = normalize_whitespace(soup.title.get_text()) if soup.title else ""
    body = normalize_whitespace(soup.get_text(" "))
    return title, body


def parse_unprocessed(limit: int = 100) -> int:
    processed = 0
    with get_session() as session:
        rows = (
            session.query(RawDocument)
            .outerjoin(ParsedDocument, ParsedDocument.raw_document_id == RawDocument.id)
            .filter(ParsedDocument.id.is_(None))
            .filter(RawDocument.is_duplicate.is_(False))
            .filter(RawDocument.html.is_not(None))
            .filter(RawDocument.html != "")
            .order_by(asc(RawDocument.id))
            .limit(limit)
            .all()
        )

        for raw_doc in rows:
            title, body = parse_html(raw_doc.html or "")
            tokens = remove_stopwords(tokenize(body))
            stems = stem_tokens(tokens)
            bigrams = ngrams(tokens, 2)
            trigrams = ngrams(tokens, 3)

            session.add(
                ParsedDocument(
                    raw_document_id=raw_doc.id,
                    url=raw_doc.url,
                    title=title,
                    body_text=body,
                    cleaned_text=" ".join(tokens),
                    tokens=" ".join(tokens),
                    stems=" ".join(stems),
                    bigrams=" | ".join(bigrams),
                    trigrams=" | ".join(trigrams),
                )
            )
            processed += 1

    return processed


if __name__ == "__main__":
    count = parse_unprocessed(limit=200)
    print(f"Parsed documents: {count}")
