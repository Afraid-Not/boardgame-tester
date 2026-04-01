-- ============================================
-- Board Game Balance Tester - Full Migration
-- Supabase SQL Editor에서 실행
-- ============================================

-- 1. pgvector 활성화
CREATE EXTENSION IF NOT EXISTS vector;

-- 2. Games 테이블
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

ALTER TABLE games ENABLE ROW LEVEL SECURITY;

-- 3. Training Jobs 테이블
CREATE TABLE IF NOT EXISTS training_jobs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    game_id UUID NOT NULL REFERENCES games(id) ON DELETE CASCADE,
    algorithm TEXT NOT NULL DEFAULT 'PPO' CHECK (algorithm IN ('PPO', 'DQN', 'A2C')),
    hyperparameters JSONB NOT NULL DEFAULT '{}',
    status TEXT NOT NULL DEFAULT 'queued' CHECK (status IN ('queued', 'running', 'completed', 'failed')),
    progress INTEGER NOT NULL DEFAULT 0 CHECK (progress >= 0 AND progress <= 100),
    total_episodes INTEGER NOT NULL DEFAULT 10000,
    started_at TIMESTAMPTZ,
    completed_at TIMESTAMPTZ,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_training_jobs_game_id ON training_jobs(game_id);
CREATE INDEX idx_training_jobs_status ON training_jobs(status);
ALTER TABLE training_jobs ENABLE ROW LEVEL SECURITY;

-- 4. Balance Reports 테이블
CREATE TABLE IF NOT EXISTS balance_reports (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    training_job_id UUID NOT NULL REFERENCES training_jobs(id) ON DELETE CASCADE,
    win_rates JSONB NOT NULL DEFAULT '{}',
    balance_score NUMERIC(5, 2) NOT NULL DEFAULT 50.00 CHECK (balance_score >= 0 AND balance_score <= 100),
    dominant_strategies JSONB NOT NULL DEFAULT '[]',
    severity TEXT NOT NULL DEFAULT 'good' CHECK (severity IN ('good', 'warning', 'critical')),
    guidelines JSONB NOT NULL DEFAULT '[]',
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_balance_reports_training_job_id ON balance_reports(training_job_id);
ALTER TABLE balance_reports ENABLE ROW LEVEL SECURITY;

-- 5. Game References 테이블 (RAG용)
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

ALTER TABLE game_references ENABLE ROW LEVEL SECURITY;

-- 6. RLS 정책 (service_role은 모든 접근 허용)
CREATE POLICY "Service role full access on games" ON games FOR ALL USING (true) WITH CHECK (true);
CREATE POLICY "Service role full access on training_jobs" ON training_jobs FOR ALL USING (true) WITH CHECK (true);
CREATE POLICY "Service role full access on balance_reports" ON balance_reports FOR ALL USING (true) WITH CHECK (true);
CREATE POLICY "Service role full access on game_references" ON game_references FOR ALL USING (true) WITH CHECK (true);
