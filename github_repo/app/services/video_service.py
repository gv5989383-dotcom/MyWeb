import os
import uuid
from fastapi import UploadFile
from app.db.db import insert_video

VIDEO_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), '..', 'data', 'videos')
VIDEO_DIR = os.path.abspath(VIDEO_DIR)

async def save_video(file: UploadFile) -> str:
    os.makedirs(VIDEO_DIR, exist_ok=True)
    video_id = str(uuid.uuid4())
    filename = f"{video_id}_{file.filename}"
    file_path = os.path.join(VIDEO_DIR, filename)
    with open(file_path, "wb") as f:
        content = await file.read()
        f.write(content)
    insert_video(video_id, filename)
    return video_id
