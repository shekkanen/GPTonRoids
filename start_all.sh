#!/bin/bash
set -e

# Load environment variables
source .env

# Start ngrok in the background
./start_ngrok.sh &
NGROK_PID=$!

# Allow some time for ngrok to initialize and set NGROK_URL
sleep 5

# Check if NGROK_URL is set
if [ -z "$NGROK_URL" ]; then
    echo "NGROK_URL is not set. Exiting."
    kill "$NGROK_PID" 2>/dev/null || true
    exit 1
fi

echo "Starting FastAPI application with Uvicorn..."
# Start FastAPI using Uvicorn
./start_uvicorn.sh

# Wait for ngrok to exit
wait "$NGROK_PID"
