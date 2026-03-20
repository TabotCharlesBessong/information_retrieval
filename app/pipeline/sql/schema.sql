CREATE TABLE IF NOT EXISTS sources (
    id SERIAL PRIMARY KEY,
    name TEXT NOT NULL UNIQUE,
    base_url TEXT NOT NULL UNIQUE,
    enabled BOOLEAN NOT NULL DEFAULT TRUE,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS crawl_queue (
    id BIGSERIAL PRIMARY KEY,
    url TEXT NOT NULL,
    source_id INTEGER NOT NULL REFERENCES sources(id) ON DELETE CASCADE,
    status TEXT NOT NULL DEFAULT 'pending',
    priority INTEGER NOT NULL DEFAULT 100,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    UNIQUE (url)
);

CREATE TABLE IF NOT EXISTS raw_documents (
    id BIGSERIAL PRIMARY KEY,
    url TEXT NOT NULL UNIQUE,
    source_id INTEGER NOT NULL REFERENCES sources(id) ON DELETE CASCADE,
    status_code INTEGER,
    content_hash TEXT,
    html TEXT,
    fetched_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    is_duplicate BOOLEAN NOT NULL DEFAULT FALSE,
    duplicate_of_id BIGINT REFERENCES raw_documents(id)
);

CREATE INDEX IF NOT EXISTS idx_raw_documents_content_hash ON raw_documents(content_hash);

CREATE TABLE IF NOT EXISTS parsed_documents (
    id BIGSERIAL PRIMARY KEY,
    raw_document_id BIGINT NOT NULL UNIQUE REFERENCES raw_documents(id) ON DELETE CASCADE,
    url TEXT NOT NULL,
    title TEXT,
    body_text TEXT,
    cleaned_text TEXT,
    tokens TEXT,
    stems TEXT,
    bigrams TEXT,
    trigrams TEXT,
    processed_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS crawl_events (
    id BIGSERIAL PRIMARY KEY,
    url TEXT NOT NULL,
    status TEXT NOT NULL,
    message TEXT,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
