from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api import games, training, reports

app = FastAPI(
    title="Board Game Balance Tester",
    description="AI-powered board game balance analysis platform",
    version="0.1.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(games.router)
app.include_router(training.router)
app.include_router(reports.router)


@app.get("/health")
async def health_check():
    return {"status": "ok"}
