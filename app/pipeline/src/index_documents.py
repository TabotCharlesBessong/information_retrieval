from __future__ import annotations

import os
from datetime import datetime

from elasticsearch import Elasticsearch, helpers
from sqlalchemy import asc

from db import get_session
from models import ParsedDocument, RawDocument, Source

INDEX_NAME = os.getenv("ELASTICSEARCH_INDEX", "documents")


MAPPING = {
    "settings": {
        "analysis": {
            "analyzer": {
                "default": {"type": "standard"}
            }
        }
    },
    "mappings": {
        "properties": {
            "id": {"type": "keyword"},
            "title": {"type": "text"},
            "body": {"type": "text"},
            "cleaned_text": {"type": "text"},
            "source": {"type": "keyword"},
            "url": {"type": "keyword"},
            "published_at": {"type": "date", "format": "strict_date_optional_time||epoch_millis"},
            "tags": {"type": "keyword"},
        }
    },
}


def get_es() -> Elasticsearch:
    es_url = os.getenv("ELASTICSEARCH_URL", "http://localhost:9200")
    return Elasticsearch(es_url)


def ensure_index(es: Elasticsearch) -> None:
    if not es.indices.exists(index=INDEX_NAME):
        es.indices.create(index=INDEX_NAME, body=MAPPING)


def load_documents(limit: int = 1000) -> list[dict[str, str]]:
    with get_session() as session:
        rows = (
            session.query(ParsedDocument, RawDocument, Source)
            .join(RawDocument, ParsedDocument.raw_document_id == RawDocument.id)
            .join(Source, RawDocument.source_id == Source.id)
            .order_by(asc(ParsedDocument.id))
            .limit(limit)
            .all()
        )

        docs: list[dict[str, str]] = []
        for parsed, _raw, source in rows:
            docs.append(
                {
                    "id": str(parsed.id),
                    "title": parsed.title or "",
                    "body": parsed.body_text or "",
                    "cleaned_text": parsed.cleaned_text or "",
                    "source": source.name,
                    "url": parsed.url,
                    # We do not have publish date yet; use processing timestamp for baseline indexing.
                    "published_at": (parsed.processed_at or datetime.utcnow()).isoformat(),
                    "tags": [],
                }
            )
        return docs


def bulk_index(es: Elasticsearch, docs: list[dict[str, str]]) -> int:
    actions = [
        {
            "_index": INDEX_NAME,
            "_id": doc["id"],
            "_source": doc,
        }
        for doc in docs
    ]

    if not actions:
        return 0

    success, _ = helpers.bulk(es, actions, refresh=True)
    return success


if __name__ == "__main__":
    es = get_es()
    ensure_index(es)
    documents = load_documents(limit=5000)
    count = bulk_index(es, documents)
    print(f"Indexed documents: {count}")
