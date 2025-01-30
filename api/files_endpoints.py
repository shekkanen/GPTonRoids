from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import JSONResponse
from pydantic import BaseModel
import os
from pathlib import Path
from prod.config import logger, BASE_DIR, get_api_key
from AIJudge.ai_judge import CreativeAgent, SecurityFirstAgent, BalancedAgent, get_consensus

router = APIRouter()

class FileData(BaseModel):
    filename: str
    content: str

# Endpoint to list all files in the base directory
@router.get("/files", dependencies=[Depends(get_api_key)])
def list_files():
    logger.info("Listing files")
    return [str(f.name) for f in BASE_DIR.iterdir() if f.is_file()]

# Endpoint to write a new file to the base directory
@router.post("/files", dependencies=[Depends(get_api_key)])
def write_file(file_data: FileData):
    logger.info(f"Attempting to write file: {file_data.filename}")
    file_path = BASE_DIR / file_data.filename

    if not file_path.exists():
        logger.info(f"File {file_data.filename} does not exist, creating a new file.")
        file_path.parent.mkdir(parents=True, exist_ok=True)
        file_path.write_text(file_data.content)
        return JSONResponse(
            content={"message": "New file created successfully."},
            status_code=status.HTTP_201_CREATED,
        )

    # Jos tiedosto jo on olemassa, ladataan sen nykyinen sisältö
    current_content = file_path.read_text()
    new_content = file_data.content

    logger.info(f"File {file_data.filename} exists, sending old+new content to AIJudge")

    # Kootaan "command"-kenttään molemmat sisällöt
    # Tällä tavalla AIJudge näkee kaiken – vanhan ja uuden tekstin
    plan_data = {
        "command": (
            f"Proposed overwrite for file '{file_data.filename}'.\n\n"
            f"--- OLD CONTENT START ---\n"
            f"{current_content}\n"
            f"--- OLD CONTENT END ---\n\n"
            f"--- NEW CONTENT START ---\n"
            f"{new_content}\n"
            f"--- NEW CONTENT END ---\n\n"
            f"Please decide if this change is acceptable or if it is too destructive."
        )
    }

    # Lähetetään plan_data jokaiselle agentille
    logger.info("Evaluating overwrite changes with AIJudge, old vs. new content.")
    agents = [CreativeAgent(), SecurityFirstAgent(), BalancedAgent()]
    votes = [agent.vote(plan_data) for agent in agents]
    consensus = get_consensus(votes)

    if not consensus["approved"]:
        logger.warning("Proposed overwrite changes rejected by AIJudge")
        return JSONResponse(
            content={
                "message": "Overwrite rejected by AIJudge",
                "reason": consensus["reason"],
                "votes": consensus["votes"],
            },
            status_code=status.HTTP_400_BAD_REQUEST,
        )

    logger.info("Overwrite approved by AIJudge, writing to file.")
    file_path.write_text(new_content)
    return JSONResponse(
        content={"message": "File overwritten successfully."},
        status_code=status.HTTP_200_OK,
    )

# Endpoint to list all files and directories recursively
@router.get("/files/all", dependencies=[Depends(get_api_key)])
def list_all_files(offset: int = 0, limit: int = 100):
    if offset < 0:
        offset = 0
    logger.info("Listing all files and directories recursively with pagination")
    try:
        items = []

        def process_path(path: Path):
            if path.is_dir():
                if path.name in [".venv", "venv", ".git", "__pycache__"]:
                    items.append({
                        "path": str(path.relative_to(BASE_DIR)), 
                        "type": "directory",
                        "file_count": sum(1 for _ in path.rglob('*') if _.is_file())
                    })
                else:
                    items.append({"path": str(path.relative_to(BASE_DIR)), "type": "directory"})
                    for sub in path.iterdir():
                        process_path(sub)
            else:
                items.append({"path": str(path.relative_to(BASE_DIR)), "type": "file"})

        process_path(BASE_DIR)
        paginated_items = items[offset:offset + limit]
        return {"items": paginated_items, "total": len(items)}
    except Exception as e:
        logger.error(f"Error listing files and directories: {e}")
        raise HTTPException(status_code=500, detail="Internal Server Error")

# Endpoint to read a file's content
@router.get("/files/{filename:path}", dependencies=[Depends(get_api_key)])
def read_file(filename: str):
    logger.info(f"Reading file: {filename}")
    file_path = BASE_DIR / filename
    if not file_path.exists():
        logger.error(f"File not found: {filename}")
        raise HTTPException(status_code=404, detail="File not found")
    return file_path.read_text()

# Endpoint to delete a file
@router.delete("/files/{filename:path}", dependencies=[Depends(get_api_key)])
def delete_file(filename: str):
    logger.info(f"Deleting file: {filename}")
    file_path = BASE_DIR / filename
    if not file_path.exists():
        logger.error(f"File not found: {filename}")
        raise HTTPException(status_code=404, detail="File not found")
    file_path.unlink()
    return {"message": "File deleted successfully"}

# Ensure the router is included in the main application
# In your main FastAPI application file (e.g., main.py or app.py)
from fastapi import FastAPI
from .files_endpoints import router as files_router

app = FastAPI()

app.include_router(files_router)
