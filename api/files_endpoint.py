from fastapi import APIRouter, HTTPException, Depends, status
from pydantic import BaseModel
from pathlib import Path
from api.config import logger, BASE_DIR, get_api_key

router = APIRouter()

class FileContent(BaseModel):
    content: str

class FileLines(BaseModel):
    lines: list[str]

@router.post("/files/{filename:path}/append", dependencies=[Depends(get_api_key)])
def append_to_file(filename: str, file_content: FileContent):
    """Appends content to the end of an existing file or creates a new one."""
    file_path = BASE_DIR / filename
    try:
        with open(file_path, "a") as f:
            f.write(file_content.content)
        return {"message": f"Content appended to '{filename}' successfully"}
    except Exception as e:
        logger.error(f"Failed to append to file: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Failed to append to file: {str(e)}")

@router.put("/files/{filename:path}", dependencies=[Depends(get_api_key)])
def write_file(filename: str, file_content: FileContent):
    """Writes the given content to the file, overwriting existing content or creating new file."""
    file_path = BASE_DIR / filename
    try:
         with open(file_path, "w") as f:
             f.write(file_content.content)
         return {"message": f"File written successfully"}
    except Exception as e:
        logger.error(f"Failed to write to file: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Failed to write to file: {str(e)}")

@router.get("/files/{filename:path}", dependencies=[Depends(get_api_key)])
def read_file(filename: str):
    """Reads the content of a file"""
    file_path = BASE_DIR / filename
    if not file_path.exists():
        logger.error(f"File not found: {filename}")
        raise HTTPException(status_code=404, detail="File not found")
    try:
        with open(file_path, "r") as f:
            content = f.read()
        return content
    except Exception as e:
        logger.error(f"Failed to read file: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Failed to read file: {str(e)}")

@router.delete("/files/{filename:path}", dependencies=[Depends(get_api_key)])
def delete_file(filename: str):
    """Deletes a file."""
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
def append_lines_to_file(filename: str, file_lines: FileLines):
    """Appends lines to the end of an existing file, creating a new one if necessary."""
    file_path = BASE_DIR / filename
    try:
        with open(file_path, "a") as f:
            for line in file_lines.lines:
                f.write(line + "\n")
        return {"message": f"Lines appended to '{filename}' successfully"}
    except Exception as e:
        logger.error(f"Failed to append lines to file: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Failed to append lines to file: {str(e)}")
