"""밸런스 리포트 + 재검증 서비스."""

import sys
import os
import traceback

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "..")))

from app.config import get_settings
from app.db.client import get_supabase
from ai_pipeline.analysis.comparator import apply_guidelines, compare_reports
from ai_pipeline.analysis.balance_analyzer import analyze_balance
from ai_pipeline.analysis.strategy_detector import detect_dominant_strategies
from rl_engine.agents.trainer import train
from rl_engine.agents.evaluator import evaluate


async def revalidate(job_id: str):
    """
    가이드라인을 적용하고 재학습/재분석하여 Before/After 비교.

    1. 기존 리포트에서 가이드라인 가져오기
    2. 가이드라인을 게임 JSON에 적용
    3. 수정된 게임으로 재학습
    4. 재평가 + 재분석
    5. Before/After 비교 결과 저장
    """
    supabase = get_supabase()

    # 기존 리포트 조회
    report = supabase.table("balance_reports").select("*").eq("training_job_id", job_id).execute()
    if not report.data:
        raise ValueError("Report not found")
    original_report = report.data[0]

    # 기존 학습 작업 + 게임 조회
    job = supabase.table("training_jobs").select("*").eq("id", job_id).execute()
    if not job.data:
        raise ValueError("Training job not found")
    job_data = job.data[0]

    game = supabase.table("games").select("parsed_structure").eq("id", job_data["game_id"]).execute()
    if not game.data or not game.data[0].get("parsed_structure"):
        raise ValueError("Game parsed structure not found")

    parsed_json = game.data[0]["parsed_structure"]
    guidelines = original_report.get("guidelines", [])

    if not guidelines:
        raise ValueError("No guidelines to apply")

    # 가이드라인 적용
    modified_json = apply_guidelines(parsed_json, guidelines)

    # 수정된 게임으로 재학습
    reval_job_id = f"{job_id}_reval"
    total_timesteps = job_data.get("total_episodes", 10000) * 100

    train_result = train(
        parsed_json=modified_json,
        algorithm=job_data.get("algorithm", "PPO"),
        total_timesteps=total_timesteps,
        job_id=reval_job_id,
    )

    # 재평가
    eval_result = evaluate(
        parsed_json=modified_json,
        model_path=train_result["model_path"],
        algorithm=job_data.get("algorithm", "PPO"),
        num_games=500,
    )

    # 재분석
    new_balance = analyze_balance(eval_result, modified_json)
    new_dominant = detect_dominant_strategies(eval_result, modified_json)

    # Before/After 비교
    original_balance = {
        "balance_score": original_report["balance_score"],
        "severity": original_report["severity"],
        "metrics": original_report.get("metrics", {}),
    }
    comparison = compare_reports(original_balance, new_balance)

    # 새 리포트 저장 (기존 리포트 업데이트에 비교 결과 추가)
    new_guidelines_data = {
        "revalidation": {
            "comparison": comparison,
            "new_balance_score": new_balance["balance_score"],
            "new_severity": new_balance["severity"],
            "new_win_rates": eval_result["win_rates"],
            "applied_guidelines": len(guidelines),
            "new_issues": new_balance.get("issues", []),
            "new_dominant_strategies": new_dominant,
        }
    }

    # 기존 가이드라인에 재검증 결과 추가
    updated_guidelines = guidelines + [new_guidelines_data]

    supabase.table("balance_reports").update({
        "guidelines": updated_guidelines,
    }).eq("id", original_report["id"]).execute()

    return {
        "comparison": comparison,
        "new_balance_score": new_balance["balance_score"],
        "new_severity": new_balance["severity"],
        "improved": comparison["score_change"] > 0,
    }
