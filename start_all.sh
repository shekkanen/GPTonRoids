#!/bin/bash
set -e

# Load environment variables
source .env

# Start ngrok in the background
./start_ngrok.sh &
NGROK_PID=$!

# Allow some time for ngrok to initialize and set NGROK_URL
sleep 5

# Retrieve NGROK_URL from the shared file
if [ -f "/tmp/ngrok_url.txt" ]; then
    NGROK_URL=$(cat /tmp/ngrok_url.txt)
    export NGROK_URL
    echo "NGROK_URL successfully retrieved: $NGROK_URL"
else
    echo "NGROK_URL file not found. Exiting."
    kill "$NGROK_PID" 2>/dev/null || true
    exit 1
fi

echo "*******************************************************************************"
echo "Paste this to GPT Actions import URL field: $NGROK_URL/openapi.json"
echo "*******************************************************************************"

echo "Starting FastAPI application with Uvicorn..."
# Start FastAPI using Uvicorn
./start_uvicorn.sh

# Wait for ngrok to exit
wait "$NGROK_PID"
