CREATE EXTENSION IF NOT EXISTS vector;
CREATE EXTENSION IF NOT EXISTS pg_trgm;

DROP TABLE IF EXISTS embedding_eval_chunks;

CREATE TABLE embedding_eval_chunks (
    meeting_chunk_id text PRIMARY KEY,
    meeting_id text NOT NULL,
    meeting_title text NOT NULL,
    meeting_date date NOT NULL,
    participant_user_ids text[] NOT NULL DEFAULT '{}',
    content text NOT NULL,
    search_text text NOT NULL,
    content_tsv tsvector GENERATED ALWAYS AS (to_tsvector('simple', content)) STORED,
    embedding vector(1536) NOT NULL
);

CREATE INDEX embedding_eval_chunks_tsv_idx
    ON embedding_eval_chunks USING gin (content_tsv);

CREATE INDEX embedding_eval_chunks_trgm_idx
    ON embedding_eval_chunks USING gist (search_text gist_trgm_ops(siglen=32));
