from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime
from enum import Enum


class Algorithm(str, Enum):
    PPO = "PPO"
    DQN = "DQN"
    A2C = "A2C"


class JobStatus(str, Enum):
    QUEUED = "queued"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"


class TrainingJobCreate(BaseModel):
    algorithm: Algorithm = Algorithm.PPO
    hyperparameters: dict = Field(default_factory=dict)
    total_episodes: int = Field(default=10000, ge=100, le=1000000)


class TrainingJobResponse(BaseModel):
    id: str
    game_id: str
    algorithm: Algorithm
    hyperparameters: dict
    status: JobStatus
    progress: int
    total_episodes: int
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    created_at: datetime
