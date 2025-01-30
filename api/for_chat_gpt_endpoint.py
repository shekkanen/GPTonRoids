from fastapi import APIRouter, HTTPException, Depends, Query
from fastapi.responses import JSONResponse, Response
from pathlib import Path
import os
import gzip
import json
from prod.config import logger, BASE_DIR, get_api_key

router = APIRouter()

@router.get("/for-chat-gpt", dependencies=[Depends(get_api_key)])
def get_files_for_chat_gpt(
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(50, ge=1, le=500, description="Number of items per page")
):
    logger.info("Collecting files for chat gpt")
    files_data = []

    # Collect matching files
    try:
        for root, dirs, filenames in os.walk(BASE_DIR):
            # Exclude certain directories
            dirs[:] = [d for d in dirs if d not in {"__pycache__", ".pytest_cache__", "venv"}]
            for filename in filenames:
                # Filter by extension or other logic
                if filename.endswith((".py", ".txt", ".md", ".yaml", ".sh")):
                    file_path = os.path.join(root, filename)
                    try:
                        with open(file_path, "r", encoding="utf-8", errors="ignore") as file:
                            file_content = file.read()
                        files_data.append({
                            "path": os.path.relpath(file_path, BASE_DIR),
                            "content": file_content
                        })
                        logger.debug(f"Successfully processed file: {file_path}")
                    except Exception as file_error:
                        logger.warning(f"Skipping file due to error: {file_path}. Error: {file_error}")
    except Exception as e:
        logger.error(f"Failed to collect files: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Failed to collect files: {e}")

    total_files = len(files_data)
    if total_files == 0:
        logger.info("No files matched the criteria or directory is empty.")
        return JSONResponse(content={"message": "No files found"}, status_code=200)

    # Calculate pagination
    start_index = (page - 1) * page_size
    end_index = start_index + page_size

    # If the start is beyond the total number, return empty
    if start_index >= total_files:
        return JSONResponse(content={
            "page": page,
            "page_size": page_size,
            "total_files": total_files,
            "files": []
        }, status_code=200)

    # Slice the data for this page
    paged_data = files_data[start_index:end_index]

    # Wrap in a structure so the client knows how to request more
    response_body = {
        "page": page,
        "page_size": page_size,
        "total_files": total_files,
        "files": paged_data
    }

    # Serialize and compress
    serialized_data = json.dumps(response_body).encode("utf-8")
    compressed_data = gzip.compress(serialized_data)
    logger.info(f"Returning compressed data of size: {len(compressed_data)} bytes")

    return Response(
        content=compressed_data,
        media_type="application/gzip",
        headers={"Content-Encoding": "gzip"}
    )
