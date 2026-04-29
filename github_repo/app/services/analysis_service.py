import os
import cv2
from app.db.db import update_analysis, get_analysis_result, get_video_filename
from app.services.mcp_tool import analyze_video_tool

VIDEO_DATA_DIR = os.path.abspath(os.path.join(os.path.dirname(os.path.dirname(__file__)), '..', 'data', 'videos'))

def extract_video_frames(video_path: str, max_frames: int = 8):
    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        raise Exception("Cannot open video file for frame extraction")

    frames = []
    while len(frames) < max_frames:
        ret, frame = cap.read()
        if not ret:
            break
        frames.append(frame)

    cap.release()
    return frames

async def run_analysis(video_id: str) -> str:
    filename = get_video_filename(video_id)
    if not filename:
        raise Exception("Video not found")

    video_path = os.path.join(VIDEO_DATA_DIR, filename)
    if not os.path.exists(video_path):
        raise Exception("Video file missing")

    frames = extract_video_frames(video_path)
    # Future model integration can consume extracted frames.
    result, confidence = analyze_video_tool(video_path)

    update_analysis(video_id, result, confidence, status="COMPLETED")
    return "COMPLETED"

async def get_result(video_id: str):
    data = get_analysis_result(video_id)
    if not data:
        raise Exception("Result not found")
    result, confidence, status = data
    if status != "COMPLETED":
        return {"status": "processing"}
    return {"result": result, "confidence": confidence}
