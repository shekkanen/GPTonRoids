from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
import os
import logging

# Import logger, get_api_key from the main server file
from api.config import logger, get_api_key

router = APIRouter()

class AnalyzeFileRequest(BaseModel):
    filename: str
    analysis_type: str

@router.post("/analyze-file", dependencies=[Depends(get_api_key)])
def analyze_file(request: AnalyzeFileRequest):
    logger.info(f"Analyzing file: {request.filename}, type: {request.analysis_type}")
    try:
        file_path = WORK_DIR / request.filename
        if not file_path.exists():
            logger.error(f"File not found: {request.filename}")
            raise HTTPException(status_code=404, detail="File not found")

        # Simulated analysis logic
        if request.analysis_type == "summarize":
            analysis_result = f"Summary of {request.filename}"
        elif request.analysis_type == "classify":
            analysis_result = f"Classification of {request.filename}"
        elif request.analysis_type == "extract_keywords":
            analysis_result = f"Keywords from {request.filename}"
        else:
            raise HTTPException(status_code=400, detail="Invalid analysis type")

        return {"analysis_result": analysis_result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Analysis failed: {str(e)}")
