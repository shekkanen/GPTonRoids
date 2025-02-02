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

def fallback_split(command_str: str):
    """
    Jos shlexin punctuation_chars ei ole käytettävissä, pilkotaan komentojono manuaalisesti
    tukien erotusoperaattoreita "&&" ja ";" huomioiden lainausmerkit.
    """
    commands = []
    current = ""
    in_single = False
    in_double = False
    i = 0
    while i < len(command_str):
        ch = command_str[i]
        if ch == "'" and not in_double:
            in_single = not in_single
            current += ch
        elif ch == '"' and not in_single:
            in_double = not in_double
            current += ch
        elif not in_single and not in_double:
            # Tarkistetaan "&&"
            if command_str[i:i+2] == "&&":
                if current.strip():
                    commands.append(current.strip())
                current = ""
                i += 2
                continue
            elif ch == ';':
                if current.strip():
                    commands.append(current.strip())
                current = ""
            else:
                current += ch
        else:
            current += ch
        i += 1
    if current.strip():
        commands.append(current.strip())
    # Käytetään shlex.split jokaiselle osakomennolle, jotta lainaukset otetaan huomioon oikein
    return [shlex.split(cmd) for cmd in commands]

def split_commands(command_str: str):
    """
    Pilkkoo annetun komentojonon listaksi komentoja. Tukee sekä ";" että "&&" erotuksina.
    Yritetään ensin shlexin punctuation_chars -attribuuttia, ja jos se epäonnistuu,
    käytetään fallback_split-funktiota.
    """
    if hasattr(shlex, 'punctuation_chars'):
        try:
            lexer = shlex.shlex(command_str, posix=True)
            lexer.whitespace_split = True
            # Määritellään erotinmerkkeinä puolipiste ja ampersandi (jolloin "&&" tulee erikseen kahta '&'-merkkiä)
            lexer.punctuation_chars = ";&"
            tokens = list(lexer)
            commands = []
            current_cmd = []
            i = 0
            while i < len(tokens):
                token = tokens[i]
                if token == ';':
                    if current_cmd:
                        commands.append(current_cmd)
                        current_cmd = []
                    i += 1
                    continue
                elif token == '&':
                    # Jos seuraava token on myös "&", käsitellään niitä erotinmerkkinä
                    if i + 1 < len(tokens) and tokens[i + 1] == '&':
                        if current_cmd:
                            commands.append(current_cmd)
                            current_cmd = []
                        i += 2
                        continue
                    else:
                        # Yksittäinen '&' – lisätään se osaksi komentoa
                        current_cmd.append(token)
                        i += 1
                        continue
                else:
                    current_cmd.append(token)
                    i += 1
            if current_cmd:
                commands.append(current_cmd)
            return commands
        except Exception as e:
            logger.warning(f"punctuation_chars -attribuutin käyttö epäonnistui: {e}")
            return fallback_split(command_str)
    else:
        return fallback_split(command_str)

def process_command_tokens(command_tokens):
    """
    Tarkistaa ja valmistaa yhden käskyn tokenit:
      - Varmistetaan, että käskyn ensimmäinen sana (komento) on SAFE_COMMANDS-listassa.
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
            logger.error(f"Tiedoston {full_path} lukeminen epäonnistui: {str(e)}")
            first_line = ""
        if not first_line.startswith("#!"):
            if full_path.endswith(".sh"):
                logger.info(f"Tiedostosta {full_path} puuttuu shebang, lisätään 'bash' komentoon")
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
    Tukee komentojen ketjuttamista erotinoperaattoreilla ";" ja "&&", esim.
      "sleep 30; cat flutter.log -n 50"
      "git add . && git commit -m \"Added dynamic animations (bounce & glow) to letter cards.\""
    """
    logger.info(f"Received command request: {request.command}")

    try:
        # Jaetaan komentojono yksittäisiksi komennoiksi
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
                logger.warning(f"Command failed with exit code {result.returncode}. Keskeytetään ketjun suoritus.")
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
