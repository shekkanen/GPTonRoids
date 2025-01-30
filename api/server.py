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
from prod.config import logger, BASE_DIR, get_api_key

app = FastAPI()

# Mount static files directory for public access
app.mount("/static", StaticFiles(directory=BASE_DIR / "tmp"), name="static")

# Import new endpoint routers
from prod.files_endpoints import router as files_router
from prod.directories_endpoints import router as directories_router
from prod.run_command_endpoint import router as run_command_router
from prod.for_chat_gpt_endpoint import router as for_chat_gpt_router
from prod.txt2wav_endpoint import router as txt2wav_router
from prod.run_tests_endpoint import router as run_tests_router
from prod.groq_chat_endpoint import router as groq_chat_router
from prod.groq_tool_endpoint import router as groq_tool_router
from prod.analyze_file_endpoint import router as analyze_file_router
from prod.screenshot_endpoint import router as screenshot_router
from prod.upload_file_endpoint import router as upload_file_router
from prod.search_files_endpoint import router as search_files_router
from prod.file_metadata_endpoint import router as file_metadata_router
from prod.github_repo_endpoint import router as github_repo_router
from prod.run_aijudge_signal_flow_endpoint import router as run_aijudge_signal_flow_router

# Mount included routers
app.include_router(files_router)
app.include_router(directories_router)
app.include_router(run_command_router)
app.include_router(for_chat_gpt_router)
app.include_router(txt2wav_router)
app.include_router(run_tests_router)
app.include_router(groq_chat_router)
app.include_router(groq_tool_router)
app.include_router(analyze_file_router)
app.include_router(screenshot_router)
app.include_router(upload_file_router)
app.include_router(search_files_router)
app.include_router(file_metadata_router)
app.include_router(github_repo_router)
app.include_router(run_aijudge_signal_flow_router)
