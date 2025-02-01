from fastapi import APIRouter, HTTPException, Depends, status
from pydantic import BaseModel
from pathlib import Path
from api.config import logger, BASE_DIR, get_api_key
import aiofiles

router = APIRouter()

class FileContent(BaseModel):
    content: str

class FileLines(BaseModel):
    lines: list[str]

@router.post("/files/{filename:path}/append", dependencies=[Depends(get_api_key)])
async def append_to_file(filename: str, file_content: FileContent):
    file_path = BASE_DIR / filename
    try:
        async with aiofiles.open(file_path, "a") as f:
            await f.write(file_content.content)
        return {"message": f"Content appended to '{filename}' successfully"}
    except Exception as e:
        logger.error(f"Failed to append to file: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Failed to append to file: {str(e)}")

@router.put("/files/{filename:path}", dependencies=[Depends(get_api_key)])
async def write_file(filename: str, file_content: FileContent):
    file_path = BASE_DIR / filename
    try:
        async with aiofiles.open(file_path, "w") as f:
            await f.write(file_content.content)
        return {"message": "File written successfully"}
    except Exception as e:
        logger.error(f"Failed to write to file: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Failed to write to file: {str(e)}")

@router.get("/files/{filename:path}", dependencies=[Depends(get_api_key)])
async def read_file(filename: str):
    file_path = BASE_DIR / filename
    if not file_path.exists():
        logger.error(f"File not found: {filename}")
        raise HTTPException(status_code=404, detail="File not found")
    try:
        async with aiofiles.open(file_path, "r") as f:
            content = await f.read()
        return content
    except Exception as e:
        logger.error(f"Failed to read file: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Failed to read file: {str(e)}")

@router.delete("/files/{filename:path}", dependencies=[Depends(get_api_key)])
def delete_file(filename: str):
    file_path = BASE_DIR / filename
    if not file_path.exists():
        logger.error(f"File not found: {filename}")
        raise HTTPException(status_code=404, detail="File not found")
    try:
        file_path.unlink()
        return {"message": "File deleted successfully"}
    except Exception as e:
        logger.error(f"Failed to delete file: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Failed to delete file: {str(e)}")

@router.post("/files/{filename:path}/lines", dependencies=[Depends(get_api_key)])
async def append_lines_to_file(filename: str, file_lines: FileLines):
    file_path = BASE_DIR / filename
    try:
        async with aiofiles.open(file_path, "a") as f:
            for line in file_lines.lines:
                await f.write(line + "\n")
        return {"message": f"Lines appended to '{filename}' successfully"}
    except Exception as e:
        logger.error(f"Failed to append lines to file: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Failed to append lines to file: {str(e)}")
