#!/bin/bash
# ============================================================
# HDDS Clinical Intelligence Platform - Quick Start Script
# ============================================================
# This script runs the AI agent pipeline, starts the FastAPI
# backend, and launches the React frontend in one go.
#
# Usage (from the hdds_clinical_intelligence/ directory):
#   bash start.sh
# ============================================================

set -e

echo ""
echo "============================================================"
echo "  HDDS Agentic Clinical Intelligence Platform"
echo "  Quick Start"
echo "============================================================"
echo ""

# Step 1: Install Python dependencies
echo "[1/4] Installing Python dependencies..."
pip install -r requirements.txt --quiet 2>/dev/null || pip install fastapi uvicorn --quiet

# Step 2: Install frontend dependencies
echo "[2/4] Installing frontend dependencies..."
cd frontend
npm install --silent 2>/dev/null
cd ..

# Step 3: Run the AI agent pipeline to generate insights
echo "[3/4] Running AI agent pipeline (all patients)..."
python run_hdds_prototype.py --all

# Step 4: Start both servers
echo "[4/4] Starting servers..."
echo ""
echo "  Backend API  -> http://127.0.0.1:8000"
echo "  Frontend UI  -> http://localhost:5173"
echo ""
echo "  Press Ctrl+C to stop both servers."
echo "------------------------------------------------------------"

# Start FastAPI in background, React in foreground
uvicorn api:app --reload --host 127.0.0.1 --port 8000 &
BACKEND_PID=$!

cd frontend
npm run dev &
FRONTEND_PID=$!
cd ..

# Trap Ctrl+C to kill both
trap "kill $BACKEND_PID $FRONTEND_PID 2>/dev/null; exit 0" INT TERM

# Wait for either to exit
wait
