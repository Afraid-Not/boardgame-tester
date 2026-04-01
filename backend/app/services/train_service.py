"""학습 작업 서비스. 로컬 GPU에서 학습 실행 + 상태 추적."""

import sys
import os
import traceback
from datetime import datetime, timezone

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "..")))

from app.config import get_settings
from app.db.client import get_supabase
from rl_engine.agents.trainer import train
from rl_engine.agents.evaluator import evaluate
from ai_pipeline.analysis.balance_analyzer import analyze_balance
from ai_pipeline.analysis.strategy_detector import detect_dominant_strategies
from ai_pipeline.analysis.guideline_agent import generate_guidelines

# 진행 중인 학습 작업의 진행률 저장 (in-memory)
# key: job_id, value: {"progress": int, "timesteps": int, "stop_requested": bool}
active_jobs: dict[str, dict] = {}


async def start_training(
    job_id: str,
    game_id: str,
    algorithm: str = "PPO",
    hyperparameters: dict | None = None,
    total_episodes: int = 10000,
):
    """
    학습 작업 실행 (BackgroundTasks에서 호출).

    1. DB 상태 → running
    2. 게임 JSON 로드
    3. RL 학습 실행
    4. 평가 실행
    5. DB에 결과 저장
    """
    supabase = get_supabase()

    # 진행률 스토어 초기화
    progress_store = {"progress": 0, "timesteps": 0, "stop_requested": False}
    active_jobs[job_id] = progress_store

    try:
        # 상태 → running
        supabase.table("training_jobs").update({
            "status": "running",
            "started_at": datetime.now(timezone.utc).isoformat(),
        }).eq("id", job_id).execute()

        supabase.table("games").update({
            "status": "training",
        }).eq("id", game_id).execute()

        # 게임 JSON 로드
        game = supabase.table("games").select("parsed_structure").eq("id", game_id).execute()
        if not game.data or not game.data[0].get("parsed_structure"):
            raise ValueError("Game has no parsed structure")

        parsed_json = game.data[0]["parsed_structure"]

        # 에피소드 → 타임스텝 변환 (대략 에피소드당 100스텝)
        total_timesteps = total_episodes * 100

        # 학습 실행
        train_result = train(
            parsed_json=parsed_json,
            algorithm=algorithm,
            hyperparameters=hyperparameters,
            total_timesteps=total_timesteps,
            job_id=job_id,
            progress_store=progress_store,
        )

        # DB 진행률 업데이트
        supabase.table("training_jobs").update({
            "progress": 100,
            "status": "completed",
            "completed_at": datetime.now(timezone.utc).isoformat(),
        }).eq("id", job_id).execute()

        supabase.table("games").update({
            "status": "completed",
        }).eq("id", game_id).execute()

        # 평가 실행
        eval_result = evaluate(
            parsed_json=parsed_json,
            model_path=train_result["model_path"],
            algorithm=algorithm,
            num_games=500,
        )

        # 밸런스 분석
        balance_result = analyze_balance(eval_result, parsed_json)
        dominant = detect_dominant_strategies(eval_result, parsed_json)

        # 가이드라인 생성 (API 키가 있는 경우만)
        settings = get_settings()
        guidelines = []
        if settings.openai_api_key:
            try:
                guidelines = generate_guidelines(
                    parsed_json=parsed_json,
                    balance_result=balance_result,
                    eval_result=eval_result,
                    dominant_strategies=dominant,
                    api_key=settings.openai_api_key,
                )
            except Exception:
                traceback.print_exc()

        # 밸런스 리포트 저장
        supabase.table("balance_reports").insert({
            "training_job_id": job_id,
            "win_rates": eval_result["win_rates"],
            "balance_score": balance_result["balance_score"],
            "dominant_strategies": dominant,
            "severity": balance_result["severity"],
            "guidelines": guidelines,
        }).execute()

    except Exception as e:
        # 실패 처리
        supabase.table("training_jobs").update({
            "status": "failed",
            "completed_at": datetime.now(timezone.utc).isoformat(),
        }).eq("id", job_id).execute()

        supabase.table("games").update({
            "status": "ready",
        }).eq("id", game_id).execute()

        traceback.print_exc()

    finally:
        active_jobs.pop(job_id, None)


def get_progress(job_id: str) -> dict:
    """진행 중인 학습 작업의 진행률 조회."""
    if job_id in active_jobs:
        return active_jobs[job_id]
    return {"progress": -1, "timesteps": 0}


def request_stop(job_id: str) -> bool:
    """학습 중지 요청."""
    if job_id in active_jobs:
        active_jobs[job_id]["stop_requested"] = True
        return True
    return False
