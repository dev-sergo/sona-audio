from fastapi import APIRouter, HTTPException

from server.core.job_queue import get_job

router = APIRouter()


@router.get("/jobs/{job_id}")
async def job_status(job_id: str):
    job = await get_job(job_id)
    if job is None:
        raise HTTPException(
            404,
            detail={"error": "job_not_found", "message": f"Job '{job_id}' not found"},
        )
    return job
