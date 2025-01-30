from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
import traceback
import logging

# Import logger, get_api_key from the main server file
from api.config import logger, get_api_key

router = APIRouter()

class GroqChatRequest(BaseModel):
    prompt: str
    model: str

@router.post("/groq-chat", dependencies=[Depends(get_api_key)])
def groq_chat(request: GroqChatRequest):
    logger.info(f"Groq chat request: {request.prompt}, model: {request.model}")
    try:
        # Simulated Groq API functionality for local testing
        if not request.prompt or not request.model:
            logger.error("Prompt and model must be provided.")
            raise HTTPException(status_code=400, detail="Prompt and model must be provided.")
        return {"message": f"Processed prompt '{request.prompt}' with model '{request.model}'"}
    except Exception as e:
        error_details = traceback.format_exc()
        logger.error(f"Groq API call failed: {str(e)}\n{error_details}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Groq API call failed: {str(e)}\n{error_details}")
