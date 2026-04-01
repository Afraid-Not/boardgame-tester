from fastapi import APIRouter, HTTPException, BackgroundTasks
from app.models.training import TrainingJobCreate, TrainingJobResponse
from app.db.client import get_supabase
from app.services.train_service import start_training, get_progress, request_stop

router = APIRouter(prefix="/api", tags=["training"])


@router.post("/games/{game_id}/train", response_model=TrainingJobResponse)
async def create_training_job(
    game_id: str,
    job: TrainingJobCreate,
    background_tasks: BackgroundTasks,
):
    supabase = get_supabase()

    # 게임 존재 + 준비 상태 확인
    game = supabase.table("games").select("status").eq("id", game_id).execute()
    if not game.data:
        raise HTTPException(status_code=404, detail="Game not found")
    if game.data[0]["status"] not in ("ready", "completed"):
        raise HTTPException(status_code=400, detail="Game is not ready for training")

    # DB에 학습 작업 생성
    result = supabase.table("training_jobs").insert({
        "game_id": game_id,
        "algorithm": job.algorithm.value,
        "hyperparameters": job.hyperparameters,
        "total_episodes": job.total_episodes,
    }).execute()

    job_data = result.data[0]

    # 백그라운드에서 학습 실행
    background_tasks.add_task(
        start_training,
        job_id=job_data["id"],
        game_id=game_id,
        algorithm=job.algorithm.value,
        hyperparameters=job.hyperparameters,
        total_episodes=job.total_episodes,
    )

    return job_data


@router.get("/training/{job_id}", response_model=TrainingJobResponse)
async def get_training_job(job_id: str):
    supabase = get_supabase()
    result = supabase.table("training_jobs").select("*").eq("id", job_id).execute()
    if not result.data:
        raise HTTPException(status_code=404, detail="Training job not found")
    return result.data[0]


@router.get("/training/{job_id}/progress")
async def get_training_progress(job_id: str):
    # 먼저 in-memory에서 실시간 진행률 확인
    live = get_progress(job_id)
    if live["progress"] >= 0:
        return {"progress": live["progress"], "timesteps": live["timesteps"], "status": "running"}

    # 없으면 DB에서 조회
    supabase = get_supabase()
    result = supabase.table("training_jobs").select("progress, status").eq("id", job_id).execute()
    if not result.data:
        raise HTTPException(status_code=404, detail="Training job not found")
    return result.data[0]


@router.post("/training/{job_id}/stop")
async def stop_training(job_id: str):
    # in-memory에서 중지 요청
    if request_stop(job_id):
        return {"message": "Stop requested"}

    # 이미 끝난 경우 DB 업데이트
    supabase = get_supabase()
    result = supabase.table("training_jobs").update({
        "status": "failed"
    }).eq("id", job_id).eq("status", "running").execute()
    if not result.data:
        raise HTTPException(status_code=404, detail="Running training job not found")
    return {"message": "Training stopped"}
