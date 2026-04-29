from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from app.services.analysis_service import run_analysis, get_result

router = APIRouter()

class AnalysisRequest(BaseModel):
    video_id: str

@router.post("/run")
async def analyze_video(request: AnalysisRequest):
    try:
        status = await run_analysis(request.video_id)
        return {"status": status}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/result/{video_id}")
async def analysis_result(video_id: str):
    try:
        result = await get_result(video_id)
        return result
    except Exception as e:
        raise HTTPException(status_code=404, detail=str(e))
