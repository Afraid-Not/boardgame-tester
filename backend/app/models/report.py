from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime
from enum import Enum


class Severity(str, Enum):
    GOOD = "good"
    WARNING = "warning"
    CRITICAL = "critical"


class BalanceReportResponse(BaseModel):
    id: str
    training_job_id: str
    win_rates: dict
    balance_score: float = Field(..., ge=0, le=100)
    dominant_strategies: list
    severity: Severity
    guidelines: list
    created_at: datetime
