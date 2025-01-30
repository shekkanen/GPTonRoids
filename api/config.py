import os
import logging
from pathlib import Path
from pydantic import BaseModel
from fastapi import Depends, HTTPException, status
from fastapi.security.api_key import APIKeyHeader

# Base directory setup
BASE_DIR = Path(__file__).resolve().parent.parent
BASE_DIR = Path(BASE_DIR)

# Temporary directory setup
TMP_DIR = BASE_DIR / "tmp"
TMP_DIR.mkdir(parents=True, exist_ok=True)

# Logs directory setup
LOGS_DIR = BASE_DIR / "logs"
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

api_key_header = APIKeyHeader(name="x-api-key", auto_error=False)

# Function to get API key
def get_api_key(x_api_key: str = Depends(api_key_header)):
    expected_key = os.getenv("API_KEY")
    if not expected_key:
        # If the server itself doesn't have an API_KEY set
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="API_KEY environment variable is not set on the server"
        )

    # Check the client’s x-api-key vs the server’s
    if not x_api_key or x_api_key != expected_key:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Invalid or missing x-api-key"
        )

    return x_api_key
