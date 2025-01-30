from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
import subprocess
import logging
import shlex
from api.config import logger, BASE_DIR, get_api_key

router = APIRouter()

class RunCommandRequest(BaseModel):
    command: str
    plan: str

# Define allowed commands (whitelist)
safe_commands = {"ls", "pwd", "uname", "echo", "cat", "hostname", "git"}

# Define disallowed commands (blacklist) – forcibly denied
disallowed_commands = {"nano", "vi", "vim", "bash", "sh", "python", "perl"}  

@router.post("/run-command", dependencies=[Depends(get_api_key)])
async def run_command(request: RunCommandRequest):
    logger.info(f"Processing command: {request.command}")

    try:
        command_parts = shlex.split(request.command)
    except ValueError as e:
        logger.warning(f"Invalid command format: {request.command}")
        raise HTTPException(status_code=400, detail=f"Invalid command format: {str(e)}")

    # 1) Jos komentoa ei voi edes ajaa, kielletään se suoraan
    if not command_parts:
        raise HTTPException(status_code=400, detail="No command provided.")

    # 2) Katso ensin musta lista
    if command_parts[0] in disallowed_commands:
        logger.warning(f"Command forcibly disallowed: {request.command}")
        raise HTTPException(
            status_code=400,
            detail=f"Command '{command_parts[0]}' is disallowed."
        )

    # 3) Salli whitelistan komennot suoraan
    logger.info(f"Running ANY command without AIJudge: {request.command}")
    try:
        command_parts = shlex.split(request.command)
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
            "logs": "AIJudge removed. No checks performed."
        }
    except subprocess.CalledProcessError as e:
        logger.error(f"Command failed: {request.command}\nStderr: {e.stderr}")
        raise HTTPException(status_code=500, detail=f"Command failed: {e.stderr}")

    # 4) Kaikki muu laitetaan AIJudgen arvioitavaksi
    aijudge_response = await run_aijudge_signal_flow(request)
    if not aijudge_response.get("approved"):
        logger.warning(f"Command denied by AIJudge: {request.command}")
        raise HTTPException(
            status_code=400,
            detail={
                "reason": aijudge_response.get("reason"),
                "votes": aijudge_response.get("votes"),
                "logs": aijudge_response.get("logs")
            }
        )

    # 5) Jos AIJudge hyväksyy, suoritetaan komento varovaisesti
    try:
        process = subprocess.Popen(
            request.command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, cwd=BASE_DIR
        )
        stdout, stderr = process.communicate()

        if process.returncode != 0:
            logger.error(f"Command failed: {request.command}\nStderr: {stderr}")
            raise HTTPException(status_code=500, detail=f"Command failed: {stderr.strip()}")

        return {
            "stdout": stdout.strip(),
            "stderr": stderr.strip(),
            "logs": aijudge_response.get("logs")
        }

    except Exception as e:
        logger.error(f"Command execution failed: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Command execution failed: {str(e)}")
