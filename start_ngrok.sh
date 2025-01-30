#!/bin/bash

# Exit immediately if a command exits with a non-zero status
set -e

# Load environment variables from .env
source .env

# Configuration
HOST="localhost"
PORT="4040"            # ngrok's API endpoint
TUNNEL_PORT="${PORT_TO_TUNNEL:-8000}"  # Port you want to tunnel (default: 8000)
TIMEOUT=30             # Total wait time in seconds
INTERVAL=1             # Interval between checks in seconds

# Function to clean up background processes on exit
cleanup() {
    echo "Cleaning up..."
    kill "$NGROK_PID" 2>/dev/null || true
    exit
}
trap cleanup SIGINT SIGTERM

echo "Starting ngrok to tunnel port $TUNNEL_PORT..."

# Start ngrok in the background
ngrok http "$TUNNEL_PORT" --log=stdout --log-format=logfmt > ngrok.log 2>&1 &
NGROK_PID=$!

# Wait for ngrok's API to become available
echo "Waiting for ngrok to start at http://$HOST:$PORT..."
start_time=$(date +%s)

while true; do
    if curl -s "http://$HOST:$PORT" > /dev/null; then
        echo "ngrok API is up and running."
        break
    fi

    current_time=$(date +%s)
    elapsed=$(( current_time - start_time ))

    if [ $elapsed -ge $TIMEOUT ]; then
        echo "Timeout after $TIMEOUT seconds waiting for ngrok to start."
        echo "Check ngrok logs at ngrok.log for details."
        kill "$NGROK_PID" 2>/dev/null || true
        exit 1
    fi

    sleep "$INTERVAL"
done

# Retrieve the public URL using ngrok's API
echo "Retrieving ngrok public URL..."
ngrok_url=$(curl -s http://localhost:4040/api/tunnels | jq -r '.tunnels[0].public_url')

if [ -z "$ngrok_url" ]; then
    echo "Failed to retrieve ngrok public URL."
    echo "Check ngrok logs at ngrok.log for details."
    kill "$NGROK_PID" 2>/dev/null || true
    exit 1
fi

echo "ngrok URL: $ngrok_url"

# Export the ngrok URL as an environment variable
export NGROK_URL="$ngrok_url"

# Optionally, save the ngrok URL to a file
echo "$ngrok_url" > /tmp/ngrok_url.txt

# Keep ngrok running in the foreground
wait "$NGROK_PID"
