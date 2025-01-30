from fastapi import APIRouter, HTTPException, Depends
from pathlib import Path
import pyautogui
import uuid
import os
from api.config import TMP_DIR, get_api_key, logger

router = APIRouter()

@router.get("/screenshot", dependencies=[Depends(get_api_key)])
def get_screenshot():
    try:
        # Check if running in a headless environment
        if not os.getenv('DISPLAY'):
            os.environ['DISPLAY'] = ':0'  # Set DISPLAY for headless environments

        screenshot = pyautogui.screenshot()
        screenshot_path = TMP_DIR / f"{uuid.uuid4()}.png"
        screenshot.save(screenshot_path)
        return {"message": "Screenshot captured successfully", "file_path": str(screenshot_path)}
    except Exception as e:
        logger.error(f"Failed to capture screenshot: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Failed to capture screenshot: {str(e)}")
