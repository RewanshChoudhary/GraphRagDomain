CREATE EXTENSION IF NOT EXISTS vector;

CREATE TABLE IF NOT EXISTS document (
    id BIGSERIAL PRIMARY KEY,
    title TEXT NOT NULL,
    content TEXT NOT NULL,
    metadata JSONB,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS chunk (
    id BIGSERIAL PRIMARY KEY,

    document_id BIGINT NOT NULL
        REFERENCES document(id) ON DELETE CASCADE,

    chunk_index INT NOT NULL,

    content TEXT NOT NULL,

    token_count INT,

    start_sentence INT,

    end_sentence INT,

    embedding vector(384),

    UNIQUE(document_id, chunk_index)
);

CREATE TABLE IF NOT EXISTS entity (
    id TEXT PRIMARY KEY DEFAULT gen_random_uuid()::text,
    name TEXT NOT NULL,
    type TEXT NOT NULL CHECK (
        type IN (
            'FILM',
            'ACTOR',
            'DIRECTOR',
            'WRITER',
            'CHARACTER',
            'GENRE',
            'STUDIO',
            'CRITIC',
            'PUBLICATION'
        )
    ),
    description TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS entity_mention (
    entity_id TEXT NOT NULL REFERENCES entity(id) ON DELETE CASCADE,
    chunk_id BIGINT NOT NULL REFERENCES chunk(id) ON DELETE CASCADE,
    raw_description TEXT NOT NULL,
    PRIMARY KEY (entity_id, chunk_id)
);

CREATE TABLE IF NOT EXISTS relationship (
    id TEXT PRIMARY KEY DEFAULT gen_random_uuid()::text,
    source_entity_id TEXT NOT NULL REFERENCES entity(id) ON DELETE CASCADE,
    target_entity_id TEXT NOT NULL REFERENCES entity(id) ON DELETE CASCADE,
    description TEXT NOT NULL,
    weight DOUBLE PRECISION NOT NULL DEFAULT 1.0 CHECK (weight BETWEEN 0.0 AND 1.0),
    type TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS claim (
    id TEXT PRIMARY KEY DEFAULT gen_random_uuid()::text,
    entity_id TEXT NOT NULL REFERENCES entity(id) ON DELETE CASCADE,
    description TEXT NOT NULL,
    source_chunk_id BIGINT NOT NULL REFERENCES chunk(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS community (
    id TEXT PRIMARY KEY DEFAULT gen_random_uuid()::text,
    level INTEGER NOT NULL CHECK (level >= 0),
    parent_community_id TEXT REFERENCES community(id) ON DELETE SET NULL
);

CREATE TABLE IF NOT EXISTS community_entity (
    community_id TEXT NOT NULL REFERENCES community(id) ON DELETE CASCADE,
    entity_id TEXT NOT NULL REFERENCES entity(id) ON DELETE CASCADE,
    PRIMARY KEY (community_id, entity_id)
);

CREATE TABLE IF NOT EXISTS community_summary (
    community_id TEXT PRIMARY KEY REFERENCES community(id) ON DELETE CASCADE,
    title TEXT NOT NULL,
    summary TEXT NOT NULL,
    rating DOUBLE PRECISION NOT NULL,
    findings_json JSONB NOT NULL DEFAULT '{}'::jsonb
);

CREATE TABLE IF NOT EXISTS query (
    id TEXT PRIMARY KEY DEFAULT gen_random_uuid()::text,
    question TEXT NOT NULL,
    answer TEXT NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS query_community_answer (
    query_id TEXT NOT NULL REFERENCES query(id) ON DELETE CASCADE,
    community_id TEXT NOT NULL REFERENCES community(id) ON DELETE CASCADE,
    partial_answer TEXT NOT NULL,
    helpfulness_score DOUBLE PRECISION NOT NULL
        CHECK (helpfulness_score BETWEEN 0.0 AND 1.0),
    PRIMARY KEY (query_id, community_id)
);
