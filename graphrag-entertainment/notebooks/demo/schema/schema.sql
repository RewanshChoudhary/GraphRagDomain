CREATE TABLE document IF NOT EXISTS(
    id BIGSERIAL PRIMARY KEY,
    title TEXT NOT NULL,
    content TEXT NOT NULL,
    metadata JSONB,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE chunk (
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
