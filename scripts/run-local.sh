#!/bin/bash
# Run Cheeky Radio Player Locally for Development
# Activates venv and starts the FastAPI server
# Auto-runs setup if venv doesn't exist

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"

echo "=========================================="
echo "🍑 Cheeky - Local Development Server"
echo "=========================================="
echo ""

# Check if venv exists, if not run setup
if [ ! -d "$PROJECT_DIR/venv" ]; then
    echo "⚠️  Virtual environment not found!"
    echo "Running setup... this may take a few minutes."
    echo ""
    "$SCRIPT_DIR/setup-local.sh"
    echo ""
fi

echo "[Cheeky] Activating virtual environment..."
source "$PROJECT_DIR/venv/bin/activate"

echo "[Cheeky] Starting Radio Player..."
echo ""
echo "═════════════════════════════════════════════"
echo "Access the application:"
echo "  🌐 http://localhost:8000"
echo ""
echo "Press Ctrl+C to stop the server"
echo "═════════════════════════════════════════════"
echo ""

# Set config directory to user home
export CHEEKY_CONFIG="$HOME/.cheeky"

# Run the FastAPI app
cd "$PROJECT_DIR/config/radio-player"
python3 -m uvicorn main:app --host 0.0.0.0 --port 8000 --reload
