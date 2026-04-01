import { create } from "zustand";
import { api } from "@/lib/api";
import type { Game, TrainingJob, BalanceReport } from "@/types";

interface GameStore {
  games: Game[];
  currentGame: Game | null;
  currentJob: TrainingJob | null;
  currentReport: BalanceReport | null;
  loading: boolean;
  error: string | null;

  fetchGames: () => Promise<void>;
  fetchGame: (id: string) => Promise<void>;
  createGame: (name: string, genre: string) => Promise<Game>;
  parseGame: (id: string, rulesText?: string, file?: File) => Promise<void>;
  startTraining: (
    gameId: string,
    options?: { algorithm?: string; total_episodes?: number },
  ) => Promise<TrainingJob>;
  fetchTrainingJob: (jobId: string) => Promise<void>;
  fetchReport: (jobId: string) => Promise<void>;
  clearError: () => void;
}

export const useGameStore = create<GameStore>((set) => ({
  games: [],
  currentGame: null,
  currentJob: null,
  currentReport: null,
  loading: false,
  error: null,

  fetchGames: async () => {
    set({ loading: true, error: null });
    try {
      const games = await api.getGames();
      set({ games, loading: false });
    } catch (e) {
      set({ error: (e as Error).message, loading: false });
    }
  },

  fetchGame: async (id: string) => {
    set({ loading: true, error: null });
    try {
      const game = await api.getGame(id);
      set({ currentGame: game, loading: false });
    } catch (e) {
      set({ error: (e as Error).message, loading: false });
    }
  },

  createGame: async (name: string, genre: string) => {
    set({ loading: true, error: null });
    try {
      const game = await api.createGame({ name, genre });
      set((state) => ({
        games: [game, ...state.games],
        loading: false,
      }));
      return game;
    } catch (e) {
      set({ error: (e as Error).message, loading: false });
      throw e;
    }
  },

  parseGame: async (id: string, rulesText?: string, file?: File) => {
    set({ loading: true, error: null });
    try {
      const formData = new FormData();
      if (rulesText) formData.append("rules_text", rulesText);
      if (file) formData.append("file", file);

      const API_BASE =
        process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";
      await fetch(`${API_BASE}/api/games/${id}/parse`, {
        method: "POST",
        body: formData,
      });
      set({ loading: false });
    } catch (e) {
      set({ error: (e as Error).message, loading: false });
    }
  },

  startTraining: async (gameId: string, options = {}) => {
    set({ loading: true, error: null });
    try {
      const job = await api.createTrainingJob(gameId, {
        algorithm: options.algorithm || "PPO",
        total_episodes: options.total_episodes || 10000,
        hyperparameters: {},
      });
      set({ currentJob: job, loading: false });
      return job;
    } catch (e) {
      set({ error: (e as Error).message, loading: false });
      throw e;
    }
  },

  fetchTrainingJob: async (jobId: string) => {
    try {
      const job = await api.getTrainingJob(jobId);
      set({ currentJob: job });
    } catch (e) {
      set({ error: (e as Error).message });
    }
  },

  fetchReport: async (jobId: string) => {
    set({ loading: true, error: null });
    try {
      const report = await api.getReport(jobId);
      set({ currentReport: report, loading: false });
    } catch (e) {
      set({ error: (e as Error).message, loading: false });
    }
  },

  clearError: () => set({ error: null }),
}));
