CREATE TABLE IF NOT EXISTS games (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name TEXT NOT NULL,
    genre TEXT NOT NULL DEFAULT 'economic_board' CHECK (genre IN ('economic_board', 'card_battle')),
    rules_text TEXT,
    rules_raw TEXT,
    parsed_structure JSONB,
    environment_code TEXT,
    status TEXT NOT NULL DEFAULT 'parsing' CHECK (status IN ('parsing', 'ready', 'training', 'completed')),
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- Auto-update updated_at
CREATE OR REPLACE FUNCTION update_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER games_updated_at
    BEFORE UPDATE ON games
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at();

-- RLS
ALTER TABLE games ENABLE ROW LEVEL SECURITY;
