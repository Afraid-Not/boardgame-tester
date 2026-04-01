export type GameGenre = "economic_board" | "card_battle";
export type GameStatus = "parsing" | "ready" | "training" | "completed";
export type JobStatus = "queued" | "running" | "completed" | "failed";
export type Severity = "good" | "warning" | "critical";

export interface Game {
  id: string;
  name: string;
  genre: GameGenre;
  rules_text: string | null;
  rules_raw: string | null;
  parsed_structure: Record<string, unknown> | null;
  environment_code: string | null;
  status: GameStatus;
  created_at: string;
  updated_at: string;
}

export interface TrainingJob {
  id: string;
  game_id: string;
  algorithm: string;
  hyperparameters: Record<string, unknown>;
  status: JobStatus;
  progress: number;
  total_episodes: number;
  started_at: string | null;
  completed_at: string | null;
  created_at: string;
}

export interface BalanceReport {
  id: string;
  training_job_id: string;
  win_rates: Record<string, unknown>;
  balance_score: number;
  dominant_strategies: unknown[];
  severity: Severity;
  guidelines: unknown[];
  created_at: string;
}
