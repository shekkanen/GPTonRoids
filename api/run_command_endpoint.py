from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
import subprocess
import shlex
import shutil
import traceback
import os
from api.config import logger, BASE_DIR, get_api_key

router = APIRouter()

class RunCommandRequest(BaseModel):
    command: str
    plan: str  # Yhteensopivuuden vuoksi, voi myöhemmin käyttää lokituksessa

SAFE_COMMANDS = {
    "sh","grep","sleep", "bash", "adb", "flutter", "compile_and_run.sh", "./compile_and_run.sh",
    "tail", "cat", "mkdir", "rm", "ls", "pwd", "uname", "echo", "hostname", "git"
}

@router.post("/run-command", dependencies=[Depends(get_api_key)])
async def run_command(request: RunCommandRequest):
    """
    Suorittaa valkoistetut shell-komennot turvallisesti ja palauttaa tuloksen.
    """
    logger.info(f"Received command request: {request.command}")

    try:
        # Pilkotaan komento shell-tyylisesti
        command_parts = shlex.split(request.command)
        if not command_parts:
            raise HTTPException(status_code=400, detail="No command provided.")

        cmd = command_parts[0]
        if cmd not in SAFE_COMMANDS:
            logger.warning(f"Blocked unauthorized command: {cmd}")
            raise HTTPException(status_code=403, detail=f"Command '{cmd}' is not allowed.")

        base_dir_abs = os.path.abspath(BASE_DIR)
        cmd_path = None

        if '/' in cmd:
            # Käsitellään polkuna suhteessa BASE_DIR:iin
            full_path = os.path.abspath(os.path.join(BASE_DIR, cmd))
            # Estetään directory traversal BASE_DIR:n ulkopuolelle
            if not (full_path == base_dir_abs or full_path.startswith(base_dir_abs + os.sep)):
                logger.warning(f"Blocked path traversal attempt: {cmd}")
                raise HTTPException(status_code=403, detail="Path traversal not allowed.")
            if not os.path.isfile(full_path):
                logger.warning(f"Command not found: {cmd}")
                raise HTTPException(status_code=404, detail=f"Command '{cmd}' not found on system.")
            if not os.access(full_path, os.X_OK):
                logger.warning(f"Command not executable: {cmd}")
                raise HTTPException(status_code=403, detail=f"Command '{cmd}' is not executable.")

            cmd_path = full_path

            # Tarkistetaan, onko tiedostolla shebang. Jos ei ja kyseessä on .sh-tiedosto, lisätään "bash"
            try:
                with open(full_path, 'r', encoding='utf-8') as f:
                    first_line = f.readline().strip()
            except Exception as e:
                logger.error(f"Failed to read file {full_path}: {str(e)}")
                first_line = ""
            if not first_line.startswith("#!"):
                if full_path.endswith(".sh"):
                    logger.info(f"No shebang found in {full_path}, prefixing command with 'bash'")
                    if command_parts[0] != "bash":
                        command_parts.insert(0, "bash")
        else:
            # Tarkistetaan järjestelmän PATH:sta
            cmd_path = shutil.which(cmd)
            if not cmd_path:
                logger.warning(f"Command not found in system PATH: {cmd}")
                raise HTTPException(status_code=404, detail=f"Command '{cmd}' not found on system.")

        # Suoritetaan komento
        result = subprocess.run(
            command_parts,
            check=False,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            cwd=BASE_DIR,
            timeout=55
        )

        logger.info(f"Command executed: {request.command}, Exit code: {result.returncode}")

        return {
            "command": request.command,
            "stdout": result.stdout.strip(),
            "stderr": result.stderr.strip(),
            "exit_code": result.returncode
        }

    except HTTPException as he:
        raise he
    except Exception as e:
        logger.error(f"Command execution failed: {str(e)}\n{traceback.format_exc()}")
        raise HTTPException(status_code=500, detail="Command execution failed.")