from fastapi import APIRouter, HTTPException, Depends
from pathlib import Path
import os
import time
from prod.config import BASE_DIR, get_api_key, logger

router = APIRouter()

@router.get("/file-metadata/{filename:path}", dependencies=[Depends(get_api_key)])
def get_file_metadata(filename: str):
    file_path = BASE_DIR / filename
    if not file_path.exists():
        raise HTTPException(status_code=404, detail="File not found")
    
    stat_info = os.stat(file_path)
    return {
        "filename": filename,
        "size": stat_info.st_size,
        "created": time.ctime(stat_info.st_ctime),
        "modified": time.ctime(stat_info.st_mtime)
    }
