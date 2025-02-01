from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
import subprocess
import shlex
import shutil
import traceback
import os
import re
from api.config import logger, BASE_DIR, get_api_key

router = APIRouter()

class RunCommandRequest(BaseModel):
    command: str
    plan: str  # Yhteensopivuuden vuoksi, voi myöhemmin käyttää lokituksessa

SAFE_COMMANDS = {
    "sh", "bash", "adb", "flutter", "compile_and_run.sh", "./compile_and_run.sh",
    "tail", "cat", "mkdir", "rm", "ls", "pwd", "uname", "echo", "hostname", "git"
}

# Regex tunnistamaan shell-operaattorit (&&, ||, ;)
SHELL_OPERATORS_REGEX = re.compile(r'(&&|\|\||;)')

@router.post("/run-command", dependencies=[Depends(get_api_key)])
async def run_command(request: RunCommandRequest):
    """
    Suorittaa valkoistetut shell-komennot turvallisesti ja palauttaa tuloksen.
    Tukee ketjutettuja komentoja (esim. 'git add . && git commit -m "Viesti"').
    """
    logger.info(f"Received command request: {request.command}")
    command_str = request.command.strip()
    if not command_str:
        raise HTTPException(status_code=400, detail="No command provided.")

    # Tarkastetaan, sisältääkö komento shell-operaattoreita
    if SHELL_OPERATORS_REGEX.search(command_str):
        # Jaetaan komento alikomentoihin ja tarkastetaan jokainen
        subcommands = re.split(r'&&|\|\||;', command_str)
        for subcmd in subcommands:
            subcmd = subcmd.strip()
            if not subcmd:
                continue
            try:
                tokens = shlex.split(subcmd)
            except Exception as e:
                logger.error(f"Failed to parse subcommand '{subcmd}': {str(e)}")
                raise HTTPException(status_code=400, detail=f"Invalid subcommand format: {subcmd}")
            if not tokens:
                continue
            if tokens[0] not in SAFE_COMMANDS:
                logger.warning(f"Blocked unauthorized subcommand: {tokens[0]}")
                raise HTTPException(status_code=403, detail=f"Subcommand '{tokens[0]}' is not allowed.")
        use_shell = True
    else:
        # Ei shell-operaattoreita, käytetään tavallista tokenisoitua komentoa
        try:
            tokens = shlex.split(command_str)
        except Exception as e:
            logger.error(f"Failed to parse command: {str(e)}")
            raise HTTPException(status_code=400, detail="Invalid command format.")
        if not tokens:
            raise HTTPException(status_code=400, detail="No command provided.")
        if tokens[0] not in SAFE_COMMANDS:
            logger.warning(f"Blocked unauthorized command: {tokens[0]}")
            raise HTTPException(status_code=403, detail=f"Command '{tokens[0]}' is not allowed.")
        use_shell = False

    try:
        if use_shell:
            # Ajetaan koko komentorivi shell=True -tilassa
            result = subprocess.run(
                command_str,
                shell=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                cwd=BASE_DIR
            )
        else:
            # Jos komento on tiedostopolku, varmistetaan, ettei yritetä directory traversalia
            cmd = tokens[0]
            if '/' in cmd:
                full_path = os.path.abspath(os.path.join(BASE_DIR, cmd))
                base_dir_abs = os.path.abspath(BASE_DIR)
                if not (full_path == base_dir_abs or full_path.startswith(base_dir_abs + os.sep)):
                    logger.warning(f"Blocked path traversal attempt: {cmd}")
                    raise HTTPException(status_code=403, detail="Path traversal not allowed.")
                if not os.path.isfile(full_path):
                    logger.warning(f"Command not found: {cmd}")
                    raise HTTPException(status_code=404, detail=f"Command '{cmd}' not found on system.")
                if not os.access(full_path, os.X_OK):
                    logger.warning(f"Command not executable: {cmd}")
                    raise HTTPException(status_code=403, detail=f"Command '{cmd}' is not executable.")
                # Tarkistetaan shebang, jos kyseessä on .sh-tiedosto
                try:
                    with open(full_path, 'r', encoding='utf-8') as f:
                        first_line = f.readline().strip()
                except Exception as e:
                    logger.error(f"Failed to read file {full_path}: {str(e)}")
                    first_line = ""
                if not first_line.startswith("#!") and full_path.endswith(".sh"):
                    logger.info(f"No shebang found in {full_path}, prefixing command with 'bash'")
                    if tokens[0] != "bash":
                        tokens.insert(0, "bash")
            else:
                # Tarkistetaan järjestelmän PATH:sta
                cmd_path = shutil.which(cmd)
                if not cmd_path:
                    logger.warning(f"Command not found in system PATH: {cmd}")
                    raise HTTPException(status_code=404, detail=f"Command '{cmd}' not found on system.")
            result = subprocess.run(
                tokens,
                check=False,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                cwd=BASE_DIR
            )

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
