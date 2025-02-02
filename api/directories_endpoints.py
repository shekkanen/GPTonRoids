from fastapi import APIRouter, HTTPException, Depends
from fastapi.responses import JSONResponse
from pathlib import Path
from pydantic import BaseModel
from api.config import logger, WORK_DIR, get_api_key

router = APIRouter()

# Endpoint to list directories
@router.get("/directories", dependencies=[Depends(get_api_key)])
def list_directories():
    logger.info("Listing directories")
    dirs = [d.name for d in WORK_DIR.iterdir() if d.is_dir()]
    if not dirs:
        raise HTTPException(status_code=404, detail="No directories found")
    return {"directories": dirs}

# Endpoint to list contents of a specific directory or file
@router.get("/directories/{dir_name:path}", dependencies=[Depends(get_api_key)])
def list_directory_content(dir_name: str):
    logger.info(f"Listing contents of directory: {dir_name}")
    dir_path = WORK_DIR / dir_name

    if not dir_path.exists():
        raise HTTPException(status_code=404, detail=f"Directory '{dir_name}' not found")

    if dir_path.is_dir():
        # List files in the directory
        files = [f.name for f in dir_path.iterdir()]
        return {"files": files}
    else:
        # If it's a file, return file metadata or content
        return {"message": f"'{dir_name}' is a file, not a directory."}

# Endpoint to create a directory
@router.post("/directories/{dir_name}", dependencies=[Depends(get_api_key)])
def create_directory(dir_name: str):
    logger.info(f"Creating directory: {dir_name}")
    dir_path = WORK_DIR / dir_name
    if dir_path.exists():
        logger.error(f"Directory already exists: {dir_name}")
        raise HTTPException(status_code=400, detail="Directory already exists")
    dir_path.mkdir(parents=True, exist_ok=True)
    return {"message": f"Directory '{dir_name}' created successfully"}

# Endpoint to delete a directory
@router.delete("/directories/{dir_name}", dependencies=[Depends(get_api_key)])
def delete_directory(dir_name: str):
    logger.info(f"Deleting directory: {dir_name}")
    dir_path = WORK_DIR / dir_name
    if not dir_path.exists():
        logger.error(f"Directory not found: {dir_name}")
        raise HTTPException(status_code=404, detail="Directory not found")
    dir_path.rmdir()
    return {"message": f"Directory '{dir_name}' deleted successfully"}
