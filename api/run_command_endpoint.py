from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
import subprocess
import logging
import shlex
import shutil
import traceback
from api.config import logger, BASE_DIR, get_api_key

router = APIRouter()

class RunCommandRequest(BaseModel):
    command: str
    plan: str  # Kept for compatibility, can be used for logging future actions

# Define allowed commands (whitelist)
SAFE_COMMANDS = {"ls", "pwd", "uname", "echo", "cat", "hostname", "git"}

@router.post("/run-command", dependencies=[Depends(get_api_key)])
async def run_command(request: RunCommandRequest):
    """
    Securely executes whitelisted shell commands and returns the result.
    """
    logger.info(f"Received command request: {request.command}")

    try:
        # Parse the command safely
        command_parts = shlex.split(request.command)

        if not command_parts:
            raise HTTPException(status_code=400, detail="No command provided.")

        # Validate the command against the whitelist
        cmd = command_parts[0]
        if cmd not in SAFE_COMMANDS:
            logger.warning(f"Blocked unauthorized command: {cmd}")
            raise HTTPException(status_code=403, detail=f"Command '{cmd}' is not allowed.")

        # Validate if the command exists in the system path
        cmd_path = shutil.which(cmd)
        if not cmd_path:
            logger.warning(f"Command not found: {cmd}")
            raise HTTPException(status_code=404, detail=f"Command '{cmd}' not found on system.")

        # Execute the command securely
        result = subprocess.run(
            command_parts,
            check=False,  # Avoid automatic exceptions; handle errors manually
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            cwd=BASE_DIR
        )

        # Log execution result
        logger.info(f"Command executed: {request.command}, Exit code: {result.returncode}")

        return {
            "command": request.command,
            "stdout": result.stdout.strip(),
            "stderr": result.stderr.strip(),
            "exit_code": result.returncode
        }

    except Exception as e:
        logger.error(f"Command execution failed: {str(e)}\n{traceback.format_exc()}")
        raise HTTPException(status_code=500, detail="Command execution failed.")