from fastapi import APIRouter, HTTPException, BackgroundTasks
from app.models.report import BalanceReportResponse
from app.db.client import get_supabase
from app.services.report_service import revalidate as run_revalidation

router = APIRouter(prefix="/api/reports", tags=["reports"])


@router.get("/{job_id}", response_model=BalanceReportResponse)
async def get_report(job_id: str):
    supabase = get_supabase()
    result = supabase.table("balance_reports").select("*").eq("training_job_id", job_id).execute()
    if not result.data:
        raise HTTPException(status_code=404, detail="Report not found")
    return result.data[0]


@router.get("/{job_id}/guidelines")
async def get_guidelines(job_id: str):
    supabase = get_supabase()
    result = supabase.table("balance_reports").select("guidelines, severity, balance_score").eq("training_job_id", job_id).execute()
    if not result.data:
        raise HTTPException(status_code=404, detail="Report not found")
    return result.data[0]


@router.post("/{job_id}/revalidate")
async def revalidate(job_id: str, background_tasks: BackgroundTasks):
    # 리포트 존재 확인
    supabase = get_supabase()
    result = supabase.table("balance_reports").select("guidelines").eq("training_job_id", job_id).execute()
    if not result.data:
        raise HTTPException(status_code=404, detail="Report not found")
    if not result.data[0].get("guidelines"):
        raise HTTPException(status_code=400, detail="No guidelines to apply")

    background_tasks.add_task(run_revalidation, job_id=job_id)
    return {"message": "Revalidation started", "job_id": job_id}
