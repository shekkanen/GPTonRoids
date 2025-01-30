from fastapi import APIRouter, HTTPException, Depends
from pathlib import Path
from prod.config import BASE_DIR, get_api_key, logger
import os
from prod.config import BaseModel

class FileSearchRequest(BaseModel):
    query: str

router = APIRouter()

@router.post("/search-files", dependencies=[Depends(get_api_key)])
def search_files(request: FileSearchRequest):
    """
    Search for files by name or content.
    """
    query = request.query.lower()
    if not query:
        raise HTTPException(status_code=400, detail="Query parameter is required.")
    
    matches = []
    try:
        for root, _, filenames in os.walk(BASE_DIR):
            for filename in filenames:
                file_path = os.path.join(root, filename)
                if query in filename.lower():
                    matches.append(file_path)
                else:
                    try:
                        with open(file_path, "r", encoding="utf-8", errors="ignore") as file:
                            content = file.read()
                            if query in content.lower():
                                matches.append(file_path)
                    except Exception:
                        continue
        return {"matches": matches}
    except Exception as e:
        logger.error(f"Failed to search files: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Failed to search files: {str(e)}")
