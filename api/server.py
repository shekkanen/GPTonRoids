from fastapi import FastAPI, HTTPException, Depends, Request
from fastapi import UploadFile, File
from fastapi.staticfiles import StaticFiles
from fastapi.responses import JSONResponse, Response
from fastapi.security.api_key import APIKeyHeader
from pathlib import Path
from pydantic import BaseModel
import os
import subprocess
import re
import uuid
from gtts import gTTS
from pydub import AudioSegment
import simpleaudio as sa
import pyautogui
import base64
from io import BytesIO
import traceback
import json
import time
import logging
from github import Github, Auth
from api.config import logger, BASE_DIR, get_api_key

# Retrieve ngrok URL from environment variable
ngrok_url = os.getenv("NGROK_URL")

# Initialize FastAPI app with servers list including ngrok_url if set
if ngrok_url:
    app = FastAPI(
        title="GPTonRoids API",
        description="API for GPTonRoids application",
        version="1.0.0",
        servers=[{"url": ngrok_url, "description": "Public ngrok URL"}]
    )
else:
    app = FastAPI(
        title="GPTonRoids API",
        description="API for GPTonRoids application",
        version="1.0.0",
        servers=[{"url": "http://localhost:8000", "description": "Local server"}]
    )

# Middleware to set custom Server header
@app.middleware("http")
async def custom_server_header(request: Request, call_next):
    response: Response = await call_next(request)
    if ngrok_url:
        response.headers["Server"] = f"FastAPI {ngrok_url}"
    else:
        response.headers["Server"] = "FastAPI"
    return response

# Mount static files directory for public access
app.mount("/static", StaticFiles(directory=BASE_DIR / "tmp"), name="static")

# Import endpoint routers
from api.directories_endpoints import router as directories_router
from api.run_command_endpoint import router as run_command_router
from api.for_chat_gpt_endpoint import router as for_chat_gpt_router
from api.txt2wav_endpoint import router as txt2wav_router
from api.run_tests_endpoint import router as run_tests_router
from api.analyze_file_endpoint import router as analyze_file_router
from api.screenshot_endpoint import router as screenshot_router
from api.upload_file_endpoint import router as upload_file_router
from api.search_files_endpoint import router as search_files_router
from api.file_metadata_endpoint import router as file_metadata_router
from api.github_repo_endpoint import router as github_repo_router
from api.files_endpoint import router as files_router # ADDED

# Include routers in the app
app.include_router(directories_router)
app.include_router(run_command_router)
app.include_router(for_chat_gpt_router)
app.include_router(txt2wav_router)
app.include_router(run_tests_router)
app.include_router(analyze_file_router)
app.include_router(screenshot_router)
app.include_router(upload_file_router)
app.include_router(search_files_router)
app.include_router(file_metadata_router)
app.include_router(github_repo_router)
app.include_router(files_router) # ADDED

# Optional: Define root endpoint
@app.get("/")
def read_root():
    return {"message": "Welcome to GPTonRoids API"}

# Optional: Customize OpenAPI schema if needed
# For example, adding additional metadata or tags