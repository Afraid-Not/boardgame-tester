CREATE TABLE IF NOT EXISTS game_references (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name TEXT NOT NULL,
    genre TEXT NOT NULL DEFAULT 'economic_board' CHECK (genre IN ('economic_board', 'card_battle')),
    rules_summary TEXT,
    balance_data JSONB NOT NULL DEFAULT '{}',
    strategies JSONB NOT NULL DEFAULT '[]',
    embedding VECTOR(384),
    source TEXT,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- Vector similarity search index
CREATE INDEX idx_game_references_embedding ON game_references
    USING ivfflat (embedding vector_cosine_ops)
    WITH (lists = 10);

ALTER TABLE game_references ENABLE ROW LEVEL SECURITY;
