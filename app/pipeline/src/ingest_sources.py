from __future__ import annotations

from pathlib import Path

from db import get_session, init_schema
from models import CrawlQueue, Source
from source_allowlist import parse_allowlist


def seed_sources(allowlist_path: str) -> None:
    entries = parse_allowlist(allowlist_path)
    if not entries:
        raise RuntimeError("No source entries found in allowlist")

    with get_session() as session:
        for entry in entries:
            source = session.query(Source).filter(Source.name == entry["name"]).one_or_none()
            if source is None:
                source = Source(name=entry["name"], base_url=entry["base_url"], enabled=True)
                session.add(source)
                session.flush()
            else:
                source.base_url = entry["base_url"]

            queue_item = session.query(CrawlQueue).filter(CrawlQueue.url == entry["base_url"]).one_or_none()
            if queue_item is None:
                session.add(
                    CrawlQueue(
                        url=entry["base_url"],
                        source_id=source.id,
                        status="pending",
                        priority=100,
                    )
                )


if __name__ == "__main__":
    init_schema()
    allowlist = (
        Path(__file__).resolve().parents[3] / "docs" / "phase-a" / "source-allowlist.md"
    )
    seed_sources(str(allowlist))
    print("Sources seeded and crawl queue initialized.")
