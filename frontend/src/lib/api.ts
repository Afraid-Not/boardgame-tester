const API_BASE = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

export const api = {
  fetch: async (path: string, options?: RequestInit) => {
    const res = await fetch(`${API_BASE}${path}`, {
      headers: { "Content-Type": "application/json", ...options?.headers },
      ...options,
    });
    if (!res.ok) {
      const error = await res.json().catch(() => ({ detail: "Unknown error" }));
      throw new Error(error.detail || `HTTP ${res.status}`);
    }
    return res.json();
  },

  // Games
  getGames: () => api.fetch("/api/games"),
  getGame: (id: string) => api.fetch(`/api/games/${id}`),
  createGame: (data: { name: string; genre: string }) =>
    api.fetch("/api/games", { method: "POST", body: JSON.stringify(data) }),

  // Training
  createTrainingJob: (gameId: string, data: Record<string, unknown>) =>
    api.fetch(`/api/games/${gameId}/train`, {
      method: "POST",
      body: JSON.stringify(data),
    }),
  getTrainingJob: (jobId: string) => api.fetch(`/api/training/${jobId}`),

  // Reports
  getReport: (jobId: string) => api.fetch(`/api/reports/${jobId}`),
  getGuidelines: (jobId: string) =>
    api.fetch(`/api/reports/${jobId}/guidelines`),
};
