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
