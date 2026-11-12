-- Shared Request Log Contract (PRD Section 11 / AGENT.md Section 8)
-- Do not modify without agreeing together and updating the PRD.

CREATE TABLE IF NOT EXISTS requests (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    timestamp DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    query TEXT NOT NULL,
    tenant_id TEXT,
    cache_hit BOOLEAN NOT NULL DEFAULT 0,
    cache_score REAL,
    route TEXT NOT NULL CHECK (route IN ('simple', 'complex', 'cache')),
    router_signals TEXT,  -- JSON string of fired routing rules
    model_used TEXT NOT NULL,
    escalated BOOLEAN NOT NULL DEFAULT 0,
    input_tokens INTEGER NOT NULL DEFAULT 0,
    output_tokens INTEGER NOT NULL DEFAULT 0,
    cost_usd REAL NOT NULL DEFAULT 0.0,
    latency_ms INTEGER NOT NULL DEFAULT 0,
    quality_score REAL,
    corpus_version INTEGER NOT NULL,
    error TEXT
);

CREATE INDEX IF NOT EXISTS idx_requests_timestamp ON requests (timestamp);
CREATE INDEX IF NOT EXISTS idx_requests_route ON requests (route);
CREATE INDEX IF NOT EXISTS idx_requests_corpus_version ON requests (corpus_version);

