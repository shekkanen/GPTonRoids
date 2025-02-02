# /home/sami/sorsat/GPTonRoids/api/file_metadata_endpoint.py
from fastapi import APIRouter, HTTPException, Depends
from pathlib import Path
import os
from datetime import datetime
from api.config import WORK_DIR, get_api_key, logger

router = APIRouter()

@router.get("/file-metadata/{filename:path}", dependencies=[Depends(get_api_key)])
def get_file_metadata(filename: str):
    file_path = WORK_DIR / filename
    if not file_path.exists():
        logger.error(f"File not found: {filename}")
        raise HTTPException(status_code=404, detail="File not found")
    
    stat_info = os.stat(file_path)
    return {
        "filename": filename,
        "size": stat_info.st_size,
        "created": datetime.fromtimestamp(stat_info.st_ctime).isoformat(),
        "modified": datetime.fromtimestamp(stat_info.st_mtime).isoformat()
    }
