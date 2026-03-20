from __future__ import annotations

import hashlib
from datetime import datetime, timezone
from urllib.parse import urlparse

import requests
from requests import RequestException
from sqlalchemy import asc

from db import get_session
from models import CrawlEvent, CrawlQueue, RawDocument


def get_next_pending(limit: int = 20) -> list[tuple[int, str, int]]:
    with get_session() as session:
        rows = (
            session.query(CrawlQueue)
            .filter(CrawlQueue.status == "pending")
            .order_by(asc(CrawlQueue.priority), asc(CrawlQueue.created_at))
            .limit(limit)
            .all()
        )
        return [(row.id, row.url, row.source_id) for row in rows]


def low_value_url(url: str) -> bool:
    path = urlparse(url).path.lower()
    noise_tokens = ("/privacy", "/terms", "/login", "/signup", "/advert", "/about")
    return any(token in path for token in noise_tokens)


def fetch_and_store(queue_id: int, url: str, source_id: int) -> None:
    if low_value_url(url):
        status = "skipped_noise"
        message = "URL matched low-value noise rule"
        html = ""
        status_code = None
    else:
        try:
            resp = requests.get(url, timeout=20)
            status_code = resp.status_code
            html = resp.text if resp.ok else ""
            status = "fetched" if resp.ok else "fetch_failed"
            message = f"HTTP {status_code}"
        except RequestException as exc:
            status = "fetch_failed"
            message = f"request_error: {exc}"
            html = ""
            status_code = None

    content_hash = hashlib.sha256(html.encode("utf-8")).hexdigest() if html else None

    with get_session() as session:
        duplicate_of_id = None
        is_duplicate = False
        if content_hash:
            existing_hash_doc = (
                session.query(RawDocument)
                .filter(RawDocument.content_hash == content_hash)
                .order_by(asc(RawDocument.id))
                .first()
            )
            if existing_hash_doc is not None:
                is_duplicate = True
                duplicate_of_id = existing_hash_doc.id

        raw_doc = session.query(RawDocument).filter(RawDocument.url == url).one_or_none()
        if raw_doc is None:
            raw_doc = RawDocument(url=url, source_id=source_id)
            session.add(raw_doc)

        raw_doc.status_code = status_code
        raw_doc.content_hash = content_hash
        raw_doc.html = html
        raw_doc.is_duplicate = is_duplicate
        raw_doc.duplicate_of_id = duplicate_of_id
        raw_doc.fetched_at = datetime.now(timezone.utc)

        queue_item = session.query(CrawlQueue).filter(CrawlQueue.id == queue_id).one_or_none()
        if queue_item is not None:
            queue_item.status = status
            queue_item.updated_at = datetime.now(timezone.utc)

        session.add(CrawlEvent(url=url, status=status, message=message))


if __name__ == "__main__":
    rows = get_next_pending(limit=20)
    for queue_id, url, source_id in rows:
        fetch_and_store(queue_id, url, source_id)
        print(f"Processed queue item {queue_id}: {url}")
