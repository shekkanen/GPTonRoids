from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
import subprocess
import logging
import shlex
from api.config import logger, BASE_DIR, get_api_key

router = APIRouter()

class RunCommandRequest(BaseModel):
    command: str
    plan: str  # Ensure 'plan' is included and required

# Define allowed commands (whitelist)
safe_commands = {"ls", "pwd", "uname", "echo", "cat", "hostname", "git"}

@router.post("/run-command", dependencies=[Depends(get_api_key)])
async def run_command(request: RunCommandRequest):
    logger.info(f"Processing command: {request.command}")
    try:
        command_parts = shlex.split(request.command)
    except ValueError as e:
        logger.warning(f"Invalid command format: {request.command}")
        raise HTTPException(status_code=400, detail=f"Invalid command format: {str(e)}")
    
    if not command_parts:
        raise HTTPException(status_code=400, detail="No command provided.")
    
    # Only use the whitelist for security and remove the need for AIJudge
    if command_parts[0] not in safe_commands:
        logger.warning(f"Command not in whitelist: {command_parts[0]}")
        raise HTTPException(
            status_code=400,
            detail=f"Command '{command_parts[0]}' is not allowed."
        )
    
    try:
        result = subprocess.run(
            command_parts,
            check=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            cwd=BASE_DIR
        )
        stdout = result.stdout.strip()
        stderr = result.stderr.strip()
        return {
            "stdout": stdout,
            "stderr": stderr,
            "logs": "AIJudge removed. Whitelist in use."
        }
    except subprocess.CalledProcessError as e:
        logger.error(f"Command failed: {request.command}\nStderr: {e.stderr}")
        raise HTTPException(status_code=500, detail=f"Command failed: {e.stderr}")
    except Exception as e:
        logger.error(f"Command execution failed: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Command execution failed: {str(e)}")
