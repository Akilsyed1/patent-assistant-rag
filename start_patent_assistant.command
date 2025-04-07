#!/bin/bash

# Display startup message
echo "Starting Patent Assistant RAG..."

# Set base directory
BASE_DIR="$(dirname "$0")/enterprise-rag-ui"

# Start the backend service first
echo "Starting backend service..."
cd "$BASE_DIR/backend"

# Check if uvicorn is installed
if ! command -v uvicorn &> /dev/null; then
    echo "Installing uvicorn..."
    pip install uvicorn fastapi
fi

# Run the FastAPI backend on port 8003
uvicorn main:app --host 0.0.0.0 --port 8003 &
BACKEND_PID=$!

# Wait for backend to start
echo "Waiting for backend to start..."
sleep 5

# Start the frontend service
echo "Starting frontend service..."
cd "$BASE_DIR/frontend"

# Run the Flask application
python app.py &
FRONTEND_PID=$!

# Wait for the frontend to start
sleep 2

# Open the web browser to the application
open http://127.0.0.1:5002

echo "Patent Assistant is now running!"
echo "Backend PID: $BACKEND_PID"
echo "Frontend PID: $FRONTEND_PID"
echo "Press CTRL+C to stop both services"

# Wait for user to press CTRL+C
wait $FRONTEND_PID

# Clean up when user presses CTRL+C
kill $BACKEND_PID 2>/dev/null
kill $FRONTEND_PID 2>/dev/null
echo "Patent Assistant has been stopped."
