from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime
from enum import Enum


class GameGenre(str, Enum):
    ECONOMIC_BOARD = "economic_board"
    CARD_BATTLE = "card_battle"


class GameStatus(str, Enum):
    PARSING = "parsing"
    READY = "ready"
    TRAINING = "training"
    COMPLETED = "completed"


class GameCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=200)
    genre: GameGenre = GameGenre.ECONOMIC_BOARD


class GameResponse(BaseModel):
    id: str
    name: str
    genre: GameGenre
    rules_text: Optional[str] = None
    rules_raw: Optional[str] = None
    parsed_structure: Optional[dict] = None
    environment_code: Optional[str] = None
    status: GameStatus
    created_at: datetime
    updated_at: datetime
