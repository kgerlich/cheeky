#!/bin/bash
# Setup Cheeky Radio Player for Local Development
# Installs system dependencies and Python packages

set -e

echo "=========================================="
echo "🍑 Cheeky - Local Development Setup"
echo "=========================================="
echo ""

# Check Python version
echo "[Cheeky] Checking Python version..."
python3 --version

# Install system dependencies
echo "[Cheeky] Installing system dependencies..."
echo "You may be prompted for your password (sudo required)"
echo ""

# Check which package manager
if command -v apt-get &> /dev/null; then
    echo "Detected: Debian/Ubuntu (apt)"
    sudo apt-get update
    sudo apt-get install -y \
        python3-pip \
        python3-venv \
        python3-dev \
        build-essential \
        python3-dbus \
        pulseaudio \
        pulseaudio-utils \
        bluez \
        mpv \
        curl \
        wget
elif command -v brew &> /dev/null; then
    echo "Detected: macOS (homebrew)"
    brew install python3 mpv
else
    echo "❌ Could not detect package manager. Please install:"
    echo "   - Python 3.9+"
    echo "   - mpv"
    echo "   - libpulse (if using audio)"
    exit 1
fi

echo ""
echo "[Cheeky] Creating Python virtual environment..."
python3 -m venv venv

echo "[Cheeky] Activating virtual environment..."
source venv/bin/activate

echo "[Cheeky] Installing Python packages..."
pip install --upgrade pip
pip install \
    fastapi==0.104.1 \
    uvicorn[standard]==0.24.0 \
    aiohttp==3.9.0 \
    pydantic==2.5.0 \
    websockets==12.0 \
    python-multipart==0.0.6 \
    python-mpv==1.0.4

echo "[Cheeky] Creating config directory..."
mkdir -p ~/.cheeky

cat > ~/.cheeky/settings.json << 'EOF'
{
  "volume": 75,
  "last_station": null,
  "bluetooth_device": ""
}
EOF

cat > ~/.cheeky/favorites.json << 'EOF'
{
  "favorites": []
}
EOF

cat > ~/.cheeky/recent.json << 'EOF'
{
  "recent": []
}
EOF

echo ""
echo "=========================================="
echo "🍑 Setup Complete!"
echo "=========================================="
echo ""
echo "Next steps:"
echo "  1. Run the application:"
echo "     ./scripts/run-local.sh"
echo ""
echo "  2. Open in your browser:"
echo "     http://localhost:8000"
echo ""
echo "  3. Check the console for debug logs"
echo ""
