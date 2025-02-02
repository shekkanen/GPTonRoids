from fastapi import APIRouter, HTTPException, Depends
import subprocess
import logging
from pathlib import Path
from api.config import logger, WORK_DIR, get_api_key

BASE_DIR = Path(__file__).resolve().parent.parent


router = APIRouter()

@router.get("/run-tests", dependencies=[Depends(get_api_key)])
def run_api_tests():
    """Runs the API test script."""
    logger.info("Running API tests")
    script_path = BASE_DIR / "run_api_tests.sh"
    if not script_path.exists():
        logger.error("Test script not found")
        raise HTTPException(status_code=404, detail="Test script not found")
    try:
        result = subprocess.run(["bash", str(script_path)], capture_output=True, text=True)
        return {
            "stdout": result.stdout,
            "stderr": result.stderr,
            "returncode": result.returncode
        }
    except Exception as e:
        logger.error(f"Failed to execute test script: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Failed to execute test script: {str(e)}")
