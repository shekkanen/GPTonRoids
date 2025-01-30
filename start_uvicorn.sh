#!/bin/bash
source .env

# Export NGROK_URL if set
if [ -n "$NGROK_URL" ]; then
    export NGROK_URL
fi

source venv/bin/activate
uvicorn api.server:app \
    --reload \
    2>&1 | tee -a logs/uvicorn.log
