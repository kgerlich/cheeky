#!/bin/bash
# Cheeky First-Boot Automation Script
# Runs once on first boot to install and configure all services
# See https://dietpi.com for DietPi documentation

set -e

echo "=========================================="
echo "🍑 Cheeky - First Boot Automation Starting"
echo "=========================================="

# Update system
echo "[Cheeky] Updating system packages..."
apt-get update
apt-get upgrade -y

# Install dependencies
echo "[Cheeky] Installing core dependencies..."
apt-get install -y \
    python3-pip \
    python3-dev \
    build-essential \
    python3-dbus \
    pulseaudio \
    pulseaudio-utils \
    bluez \
    mpv \
    avahi-daemon \
    wget \
    curl \
    git

# Install Python packages
echo "[Cheeky] Installing Python packages..."
pip3 install --break-system-packages \
    fastapi==0.104.1 \
    uvicorn[standard]==0.24.0 \
    aiohttp==3.9.0 \
    pydantic==2.5.0 \
    websockets==12.0 \
    python-multipart==0.0.6 \
    python-mpv==1.0.4

# Install Radio Player
echo "[Cheeky] Installing Radio Player..."
mkdir -p /opt/cheeky/radio-player
cp -r config/radio-player/* /opt/cheeky/radio-player/

# Create config directory
mkdir -p /etc/cheeky
cat > /etc/cheeky/settings.json << 'EOF'
{
  "volume": 75,
  "last_station": null,
  "bluetooth_device": ""
}
EOF

cat > /etc/cheeky/favorites.json << 'EOF'
{
  "favorites": []
}
EOF

cat > /etc/cheeky/recent.json << 'EOF'
{
  "recent": []
}
EOF

# Create systemd service for Radio Player
echo "[Cheeky] Creating Radio Player systemd service..."
cat > /etc/systemd/system/cheeky-radio-player.service << 'EOF'
[Unit]
Description=Cheeky Radio Player
After=network.target sound.target pulseaudio.service

[Service]
Type=simple
User=root
WorkingDirectory=/opt/cheeky/radio-player
ExecStart=/usr/bin/python3 -m uvicorn main:app --host 0.0.0.0 --port 80
Restart=always
RestartSec=10
Environment="CHEEKY_CONFIG=/etc/cheeky"

[Install]
WantedBy=multi-user.target
EOF

# Install Bluetooth auto-reconnect service
echo "[Cheeky] Installing Bluetooth auto-reconnect..."
cp config/bluetooth-reconnect.sh /usr/local/bin/cheeky-bluetooth-reconnect.sh
chmod +x /usr/local/bin/cheeky-bluetooth-reconnect.sh

cat > /etc/systemd/system/cheeky-bluetooth-reconnect.service << 'EOF'
[Unit]
Description=Cheeky Bluetooth Auto-Reconnect
After=bluetooth.service

[Service]
Type=oneshot
ExecStart=/usr/local/bin/cheeky-bluetooth-reconnect.sh
RemainAfterExit=yes

[Install]
WantedBy=multi-user.target
EOF

# Enable and start services
echo "[Cheeky] Enabling services..."
systemctl daemon-reload
systemctl enable cheeky-radio-player
systemctl enable cheeky-bluetooth-reconnect
systemctl enable bluetooth
systemctl enable avahi-daemon

# Start services
echo "[Cheeky] Starting services..."
systemctl start bluetooth
systemctl start avahi-daemon
systemctl start cheeky-radio-player
systemctl start cheeky-bluetooth-reconnect

# Verify services are running
echo ""
echo "[Cheeky] Verifying services..."
sleep 2

if systemctl is-active --quiet cheeky-radio-player; then
    echo "✓ Radio Player is running (port 80)"
else
    echo "✗ Radio Player failed to start"
fi

if systemctl is-active --quiet bluetooth; then
    echo "✓ Bluetooth service is running"
else
    echo "✗ Bluetooth service failed to start"
fi

echo ""
echo "=========================================="
echo "🍑 Cheeky Setup Complete!"
echo "=========================================="
echo ""
echo "Access your radio player and Bluetooth manager:"
echo "  http://raspberrypi.local"
echo ""
echo "SSH access (if needed):"
echo "  ssh root@raspberrypi.local"
echo "  password: raspberry"
echo ""
echo "Don't take radio too seriously. Be cheeky! 🍑"
echo ""
