CREATE EXTENSION IF NOT EXISTS vector;

CREATE TABLE IF NOT EXISTS pokemon (
    id          INT PRIMARY KEY,
    name        TEXT NOT NULL,
    generation  INT NOT NULL,
    types       TEXT[] NOT NULL,
    tier        TEXT,
    stats       JSONB NOT NULL,
    metadata    JSONB NOT NULL DEFAULT '{}'::jsonb,
    text_v1     TEXT, text_v2 TEXT, text_v3 TEXT, text_v4 TEXT,
    emb_v1_titan  vector(1024), emb_v2_titan  vector(1024),
    emb_v3_titan  vector(1024), emb_v4_titan  vector(1024),
    emb_v1_minilm vector(384),  emb_v2_minilm vector(384),
    emb_v3_minilm vector(384),  emb_v4_minilm vector(384)
);

CREATE INDEX IF NOT EXISTS pokemon_types_gin ON pokemon USING GIN (types);
CREATE INDEX IF NOT EXISTS pokemon_tier_idx  ON pokemon (tier);
CREATE INDEX IF NOT EXISTS pokemon_gen_idx   ON pokemon (generation);

CREATE INDEX IF NOT EXISTS hnsw_v1_titan  ON pokemon USING hnsw (emb_v1_titan  vector_cosine_ops) WITH (m = 16, ef_construction = 64);
CREATE INDEX IF NOT EXISTS hnsw_v2_titan  ON pokemon USING hnsw (emb_v2_titan  vector_cosine_ops) WITH (m = 16, ef_construction = 64);
CREATE INDEX IF NOT EXISTS hnsw_v3_titan  ON pokemon USING hnsw (emb_v3_titan  vector_cosine_ops) WITH (m = 16, ef_construction = 64);
CREATE INDEX IF NOT EXISTS hnsw_v4_titan  ON pokemon USING hnsw (emb_v4_titan  vector_cosine_ops) WITH (m = 16, ef_construction = 64);
CREATE INDEX IF NOT EXISTS hnsw_v1_minilm ON pokemon USING hnsw (emb_v1_minilm vector_cosine_ops) WITH (m = 16, ef_construction = 64);
CREATE INDEX IF NOT EXISTS hnsw_v2_minilm ON pokemon USING hnsw (emb_v2_minilm vector_cosine_ops) WITH (m = 16, ef_construction = 64);
CREATE INDEX IF NOT EXISTS hnsw_v3_minilm ON pokemon USING hnsw (emb_v3_minilm vector_cosine_ops) WITH (m = 16, ef_construction = 64);
CREATE INDEX IF NOT EXISTS hnsw_v4_minilm ON pokemon USING hnsw (emb_v4_minilm vector_cosine_ops) WITH (m = 16, ef_construction = 64);
