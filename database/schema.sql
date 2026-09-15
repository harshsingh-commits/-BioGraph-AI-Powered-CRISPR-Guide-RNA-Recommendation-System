CREATE TABLE IF NOT EXISTS genes (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    sequence_length INTEGER NOT NULL,
    gc_content DOUBLE PRECISION NOT NULL,
    sequence_hash VARCHAR(64) NOT NULL
);

CREATE TABLE IF NOT EXISTS guides (
    id SERIAL PRIMARY KEY,
    gene_id INTEGER NOT NULL REFERENCES genes(id),
    sequence VARCHAR(64) NOT NULL,
    efficiency DOUBLE PRECISION NOT NULL,
    final_score DOUBLE PRECISION NOT NULL,
    risk VARCHAR(32) NOT NULL
);

CREATE TABLE IF NOT EXISTS off_targets (
    id SERIAL PRIMARY KEY,
    guide_id INTEGER NOT NULL REFERENCES guides(id),
    reference VARCHAR(255) NOT NULL,
    position INTEGER NOT NULL,
    mismatches INTEGER NOT NULL
);

CREATE TABLE IF NOT EXISTS experiments (
    id SERIAL PRIMARY KEY,
    external_id VARCHAR(64) UNIQUE NOT NULL,
    gene VARCHAR(255) NOT NULL,
    selected_guide VARCHAR(64) NOT NULL,
    model_version VARCHAR(128) NOT NULL,
    efficiency DOUBLE PRECISION NOT NULL,
    risk_score DOUBLE PRECISION NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS reports (
    id SERIAL PRIMARY KEY,
    experiment_id VARCHAR(64) NOT NULL,
    text_path TEXT NOT NULL,
    pdf_path TEXT NOT NULL,
    metadata JSONB NOT NULL DEFAULT '{}'::jsonb
);
