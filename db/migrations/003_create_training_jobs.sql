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
