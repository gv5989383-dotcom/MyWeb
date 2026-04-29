from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routes import video, analysis
from app.startup import on_startup


app = FastAPI(on_startup=[on_startup])

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Routers
app.include_router(video.router, prefix="/videos", tags=["videos"])
app.include_router(analysis.router, prefix="/analysis", tags=["analysis"])
