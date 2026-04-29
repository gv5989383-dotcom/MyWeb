from fastapi import APIRouter, UploadFile, File, HTTPException
from app.services.video_service import save_video

router = APIRouter()

@router.post("/upload")
async def upload_video(file: UploadFile = File(...)):
    try:
        video_id = await save_video(file)
        return {"video_id": video_id}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
