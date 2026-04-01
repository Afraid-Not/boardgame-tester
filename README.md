# Board Game Balance Tester

AI-powered platform that parses board game rulebooks, generates game environments, runs RL simulations, and provides balance analysis with improvement guidelines.

## Features

- **Rulebook Parsing** — Upload text or images of game rules; OpenAI API extracts structured game data
- **RAG-based Reference** — Finds similar existing games via pgvector embeddings for context-aware analysis
- **RL Environment Generation** — Auto-generates Gymnasium environments from parsed rules
- **Self-play Training** — Trains agents using Stable-Baselines3 with local GPU acceleration
- **Balance Analysis** — Produces win rates, dominant strategy detection, balance scores (0–100), and actionable guidelines
- **Revalidation Loop** — Applies suggested improvements and re-runs simulations to verify changes

## Tech Stack

| Layer    | Technology                                              |
| -------- | ------------------------------------------------------- |
| Frontend | Next.js 16, TypeScript, Tailwind CSS, Zustand, Recharts |
| Backend  | FastAPI, Supabase (PostgreSQL + pgvector)               |
| RL       | Stable-Baselines3, Gymnasium, PyTorch (CUDA)            |
| AI       | OpenAI API (parsing, code generation, analysis)         |
| Infra    | Vercel (frontend), ngrok (backend dev), GitHub Actions  |

## Project Structure

```
boardgame-tester/
├── frontend/          # Next.js dashboard (App Router)
├── backend/           # FastAPI server
│   └── app/
│       ├── api/       # Route handlers (games, training, reports)
│       ├── models/    # Pydantic schemas
│       ├── services/  # Business logic
│       └── db/        # Supabase client
├── rl_engine/         # RL simulation engine
│   ├── agents/        # Trainer, evaluator, self-play
│   ├── environments/  # Gymnasium envs (economic board template)
│   └── codegen/       # Environment code generator
├── ai_pipeline/       # AI processing pipeline
│   ├── parsing/       # Text & image rule parsing
│   ├── rag/           # Embedding & retrieval (pgvector)
│   └── analysis/      # Balance analysis & guideline generation
├── data/              # Reference data for RAG
├── db/                # SQL migrations & seeds
└── tests/             # Test suites per module
```

## Getting Started

### Prerequisites

- Python 3.10+
- Node.js 22+
- Conda (virtual environment)
- NVIDIA GPU with CUDA (for RL training)

### Backend

```bash
cd backend
conda activate boardgame-tester
uv pip install -r requirements.txt
uvicorn app.main:app --reload
```

### Frontend

```bash
cd frontend
npm install
npm run dev
```

### RL Engine / AI Pipeline

```bash
cd rl_engine   # or ai_pipeline
uv pip install -r requirements.txt
```

## Environment Variables

Copy `.env.example` to `.env` and fill in:

| Variable                    | Description               |
| --------------------------- | ------------------------- |
| `SUPABASE_URL`              | Supabase project URL      |
| `SUPABASE_ANON_KEY`         | Supabase anonymous key    |
| `SUPABASE_SERVICE_ROLE_KEY` | Supabase service role key |
| `OPENAI_API_KEY`            | OpenAI API key            |
| `NGROK_AUTH_TOKEN`          | ngrok auth token          |

## API Endpoints

| Method | Path                           | Description                    |
| ------ | ------------------------------ | ------------------------------ |
| GET    | `/health`                      | Health check                   |
| POST   | `/api/games`                   | Create a new game              |
| GET    | `/api/games`                   | List all games                 |
| GET    | `/api/games/{id}`              | Get game details               |
| POST   | `/api/games/{id}/parse`        | Parse rulebook (text/image)    |
| GET    | `/api/games/{id}/environment`  | Get generated environment code |
| POST   | `/api/games/{id}/train`        | Start RL training job          |
| GET    | `/api/training/{id}`           | Get training job status        |
| GET    | `/api/training/{id}/progress`  | Get live training progress     |
| POST   | `/api/training/{id}/stop`      | Stop a running training job    |
| GET    | `/api/reports/{id}`            | Get balance report             |
| GET    | `/api/reports/{id}/guidelines` | Get improvement guidelines     |
| POST   | `/api/reports/{id}/revalidate` | Re-run with applied guidelines |

## Testing

```bash
pytest tests/backend/
pytest tests/rl_engine/
pytest tests/ai_pipeline/
```

## CI

GitHub Actions runs on push/PR to `main`:

- **Frontend** — lint + build
- **Backend** — pytest
