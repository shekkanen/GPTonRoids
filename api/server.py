from fastapi import FastAPI, HTTPException, Depends, status, Request
from fastapi import UploadFile, File
from fastapi.staticfiles import StaticFiles
from fastapi.responses import JSONResponse
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
from github import Github
from api.config import logger, BASE_DIR, get_api_key

app = FastAPI()

# Mount static files directory for public access
app.mount("/static", StaticFiles(directory=BASE_DIR / "tmp"), name="static")

# Import new endpoint routers
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

# Mount included routers
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
