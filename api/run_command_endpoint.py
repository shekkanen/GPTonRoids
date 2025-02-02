from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
import subprocess
import shlex
import shutil
import traceback
import os
from api.config import logger, WORK_DIR, get_api_key, SAFE_COMMANDS

router = APIRouter()

class RunCommandRequest(BaseModel):
    command: str
    plan: str  # Yhteensopivuuden vuoksi, lokitusta varten tulevaisuudessa

def split_commands(command_str: str):
    """
    Pilkkoo annetun komentorivin useisiin osakomentoihin puolipisteen avulla.
    Jos shlex tukee punctuation_chars-attribuuttia, käytetään sitä. Muussa tapauksessa
    jaetaan ensin puolipisteittäin ja sitten shlex.splitillä, jotta lainausmerkit huomioidaan.
    """
    # Jos punctuation_chars on tuettu, käytetään sitä.
    if hasattr(shlex, 'punctuation_chars'):
        try:
            lexer = shlex.shlex(command_str, posix=True)
            lexer.whitespace_split = True
            lexer.punctuation_chars = ';'
            tokens = list(lexer)
            commands = []
            current_cmd = []
            for token in tokens:
                if token == ';':
                    if current_cmd:
                        commands.append(current_cmd)
                        current_cmd = []
                else:
                    current_cmd.append(token)
            if current_cmd:
                commands.append(current_cmd)
            return commands
        except Exception as e:
            logger.warning(f"punctuation_chars -attribuutin käyttö epäonnistui: {e}")
            # Fall back to manual split alla.
    
    # Fallback: jaetaan merkkijono puolipisteittäin, sitten shlex.split kullekin osalle.
    commands = []
    for part in command_str.split(';'):
        part = part.strip()
        if part:
            try:
                commands.append(shlex.split(part))
            except Exception as e:
                logger.error(f"Failed to split part '{part}': {e}")
                raise HTTPException(status_code=400, detail="Command parsing failed.")
    return commands

def process_command_tokens(command_tokens):
    """
    Tarkistaa ja valmistaa yhden käskyn tokenit:
      - Varmistetaan, että käskyn ensimmäinen komento on SAFE_COMMANDS-listassa.
      - Jos komennossa on polku, varmistetaan, ettei yritetä directory traversalia ja että tiedosto on suoritettava.
      - Jos kyseessä on .sh-tiedosto ilman shebangia, lisätään 'bash' suoritukseen.
    """
    if not command_tokens:
        raise HTTPException(status_code=400, detail="Tyhjä komento.")
    
    cmd = command_tokens[0]
    if cmd not in SAFE_COMMANDS:
        logger.warning(f"Blocked unauthorized command: {cmd}")
        raise HTTPException(status_code=403, detail=f"Command '{cmd}' is not allowed.")

    WORK_DIR_abs = os.path.abspath(WORK_DIR)

    # Jos komennossa on polku, ratkotaan se WORK_DIR:iin nähden
    if '/' in cmd:
        full_path = os.path.abspath(os.path.join(WORK_DIR, cmd))
        if not (full_path == WORK_DIR_abs or full_path.startswith(WORK_DIR_abs + os.sep)):
            logger.warning(f"Blocked path traversal attempt: {cmd}")
            raise HTTPException(status_code=403, detail="Path traversal not allowed.")
        if not os.path.isfile(full_path):
            logger.warning(f"Command not found: {cmd}")
            raise HTTPException(status_code=404, detail=f"Command '{cmd}' not found on system.")
        if not os.access(full_path, os.X_OK):
            logger.warning(f"Command not executable: {cmd}")
            raise HTTPException(status_code=403, detail=f"Command '{cmd}' is not executable.")

        # Korvataan komennon nimi täyteen polkuun
        command_tokens[0] = full_path

        # Tarkistetaan, onko .sh-tiedosto ilman shebangia
        try:
            with open(full_path, 'r', encoding='utf-8') as f:
                first_line = f.readline().strip()
        except Exception as e:
            logger.error(f"Failed to read file {full_path}: {str(e)}")
            first_line = ""
        if not first_line.startswith("#!"):
            if full_path.endswith(".sh"):
                logger.info(f"No shebang found in {full_path}, prefixing command with 'bash'")
                # Lisätään 'bash' alkuun, jos sitä ei jo ole
                if command_tokens[0] != "bash":
                    command_tokens.insert(0, "bash")
    else:
        # Haetaan komennon polku järjestelmän PATH:sta
        cmd_path = shutil.which(cmd)
        if not cmd_path:
            logger.warning(f"Command not found in system PATH: {cmd}")
            raise HTTPException(status_code=404, detail=f"Command '{cmd}' not found on system.")
        command_tokens[0] = cmd_path

    return command_tokens

@router.post("/run-command", dependencies=[Depends(get_api_key)])
async def run_command(request: RunCommandRequest):
    """
    Suorittaa valkoistetut shell-komennot turvallisesti ja palauttaa tuloksen.
    Tukee komentojen ketjuttamista puolipisteellä (;), esim.
      "sleep 30; cat flutter.log -n 50"
    """
    logger.info(f"Received command request: {request.command}")

    try:
        # Jaetaan komentorivi yksittäisiksi komennoiksi
        commands_list = split_commands(request.command)
        if not commands_list:
            raise HTTPException(status_code=400, detail="No command provided.")

        combined_stdout = []
        combined_stderr = []
        exit_code = 0

        # Suoritetaan käskyt yksi kerrallaan
        for cmd_tokens in commands_list:
            processed_tokens = process_command_tokens(cmd_tokens)
            logger.info(f"Executing command: {' '.join(processed_tokens)}")
            result = subprocess.run(
                processed_tokens,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                cwd=WORK_DIR,
                timeout=55
            )
            combined_stdout.append(result.stdout.strip())
            combined_stderr.append(result.stderr.strip())
            exit_code = result.returncode

            # Jos käsky epäonnistuu, keskeytetään ketjun suoritus
            if result.returncode != 0:
                logger.warning(f"Command failed with exit code {result.returncode}. Halting further execution.")
                break

        return {
            "command": request.command,
            "stdout": "\n".join(combined_stdout).strip(),
            "stderr": "\n".join(combined_stderr).strip(),
            "exit_code": exit_code
        }

    except HTTPException as he:
        raise he
    except subprocess.TimeoutExpired as te:
        logger.error(f"Command timeout: {str(te)}")
        raise HTTPException(status_code=504, detail="Command execution timed out.")
    except Exception as e:
        logger.error(f"Command execution failed: {str(e)}\n{traceback.format_exc()}")
        raise HTTPException(status_code=500, detail="Command execution failed.")
