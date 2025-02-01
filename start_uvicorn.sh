#!/bin/bash
source .env

# Export NGROK_URL if set
if [ -n "$NGROK_URL" ]; then
    export NGROK_URL
fi

source venv/bin/activate

# Example with workers, without reload for production (example for production-like use)
#  uvicorn api.server:app --workers 4 2>&1 | tee -a logs/uvicorn.log

# Example with workers and reload for development
uvicorn api.server:app --reload --workers 2 2>&1 | tee -a logs/uvicorn.log