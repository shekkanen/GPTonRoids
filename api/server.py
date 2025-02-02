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
from fastapi.openapi.utils import get_openapi
from api.config import logger, BASE_DIR, get_api_key

# Aseta FastAPI-sovellus oletusserveriksi localhost:8000.
# NGROK_URL päivitetään myöhemmin OpenAPI-skeemassa.
app = FastAPI(
    title="GPTonRoids API",
    description="API for GPTonRoids application",
    version="1.0.0",
    servers=[{"url": "http://localhost:8000", "description": "Local server"}]
)

# Middleware: asetetaan custom Server-header
@app.middleware("http")
async def custom_server_header(request: Request, call_next):
    response: Response = await call_next(request)
    # Jos haluttu, voidaan myös tarkastella NGROK_URL:a tässäkin,
    # mutta tässä käytetään sitä vain OpenAPI-skeemassa.
    response.headers["Server"] = "FastAPI"
    return response

# Mountataan static-tiedostojen hakemisto julkiseen käyttöön
app.mount("/static", StaticFiles(directory=BASE_DIR / "tmp"), name="static")

# Importoidaan endpoint-routerit
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
from api.files_endpoint import router as files_router  # ADDED

# Lisätään routerit sovellukseen
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
app.include_router(files_router)  # ADDED

# Perusreititys
@app.get("/")
def read_root():
    return {"message": "Welcome to GPTonRoids API"}

# Muokataan OpenAPI-skeemaa niin, että jokaisessa endpointissa on
# "x-openai-isConsequential": false ja päivitetään servers-dynamiikka.
def custom_openapi():
    if app.openapi_schema:
        return app.openapi_schema
    openapi_schema = get_openapi(
        title=app.title,
        version=app.version,
        description=app.description,
        routes=app.routes,
    )
    # Päivitetään servers-kenttä lukemalla NGROK_URL ympäristöstä juuri sillä hetkellä
    ngrok_url_dynamic = os.getenv("NGROK_URL")
    if ngrok_url_dynamic and ngrok_url_dynamic.lower() != "null":
        openapi_schema["servers"] = [{"url": ngrok_url_dynamic, "description": "Public ngrok URL"}]
    # Lisätään custom kenttä jokaiseen operaatioon
    for path, methods in openapi_schema.get("paths", {}).items():
        for operation in methods.values():
            operation["x-openai-isConsequential"] = False
    app.openapi_schema = openapi_schema
    return app.openapi_schema

app.openapi = custom_openapi
