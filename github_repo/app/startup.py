import os
from app.db.db import init_db

DATA_VIDEO_DIR = os.path.abspath(
    os.path.join(os.path.dirname(os.path.dirname(__file__)), '..', 'data', 'videos')
)


def on_startup():
    os.makedirs(DATA_VIDEO_DIR, exist_ok=True)
    init_db()
