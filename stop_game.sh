#!/bin/bash

# Reverse Turing Game Stop Script
# This script stops all game services

echo "🛑 Stopping Reverse Turing Game..."

# Kill backend if running
if [ -f .backend_pid ]; then
    BACKEND_PID=$(cat .backend_pid)
    if ps -p $BACKEND_PID > /dev/null; then
        echo "Stopping backend (PID: $BACKEND_PID)..."
        kill $BACKEND_PID
        sleep 2
        if ps -p $BACKEND_PID > /dev/null; then
            echo "Force stopping backend..."
            kill -9 $BACKEND_PID
        fi
    fi
    rm .backend_pid
fi

# Kill frontend if running
if [ -f .frontend_pid ]; then
    FRONTEND_PID=$(cat .frontend_pid)
    if ps -p $FRONTEND_PID > /dev/null; then
        echo "Stopping frontend (PID: $FRONTEND_PID)..."
        kill $FRONTEND_PID
        sleep 2
        if ps -p $FRONTEND_PID > /dev/null; then
            echo "Force stopping frontend..."
            kill -9 $FRONTEND_PID
        fi
    fi
    rm .frontend_pid
fi

# Stop Docker services
echo "Stopping Docker services..."
docker-compose down

# Kill any remaining processes
pkill -f "python.*app.py" 2>/dev/null || true
pkill -f "npm.*start" 2>/dev/null || true

echo "✅ All services stopped!"