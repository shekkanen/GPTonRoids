import os
import logging
from pathlib import Path
from pydantic import BaseModel
from fastapi import Depends, HTTPException, status
from fastapi.security.api_key import APIKeyHeader

from dotenv import load_dotenv
load_dotenv()

# Work directory setup
work_dir_env = os.getenv("WORK_DIR")
if work_dir_env and work_dir_env.strip():
    WORK_DIR = Path(work_dir_env)
else:
    WORK_DIR = Path(__file__).resolve().parent.parent / "work"

# Temporary directory setup
BASE_DIR = Path(__file__).resolve().parent.parent
TMP_DIR = BASE_DIR / "tmp"
TMP_DIR.mkdir(parents=True, exist_ok=True)

# Logs directory setup
LOGS_DIR = WORK_DIR / "logs"
LOGS_DIR.mkdir(parents=True, exist_ok=True)

# Logger setup
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler(LOGS_DIR / "server.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("server")

# Safe commands configuration from environment variable
safe_commands_str = os.getenv("SAFE_COMMANDS", "ls,pwd,uname,echo,cat,hostname,git")
SAFE_COMMANDS = set(cmd.strip() for cmd in safe_commands_str.split(',') if cmd.strip())
if not SAFE_COMMANDS:
    SAFE_COMMANDS = {"ls", "pwd", "uname", "echo", "cat", "hostname", "git"}  # Default safe commands if empty or not set

logger.info(f"SAFE_COMMANDS loaded from env: {SAFE_COMMANDS}")

GPTONROIDS_API_KEY_header = APIKeyHeader(name="GPTONROIDS_API_KEY", auto_error=False)

# Function to get API key
def get_api_key(x_GPTONROIDS_API_KEY: str = Depends(GPTONROIDS_API_KEY_header)):
    expected_key = os.getenv("GPTONROIDS_API_KEY")
    if not expected_key:
        # If the server itself doesn't have an GPTONROIDS_API_KEY set
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="GPTONROIDS_API_KEY environment variable is not set on the server"
        )

    # Check the client’s GPTONROIDS_API_KEY vs the server’s
    if not x_GPTONROIDS_API_KEY or x_GPTONROIDS_API_KEY != expected_key:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Invalid or missing GPTONROIDS_API_KEY"
        )

    return x_GPTONROIDS_API_KEY
