#!/bin/bash
# Cheeky Installation Script
# Runs inside chroot to install all Cheeky components

set -e
export DEBIAN_FRONTEND=noninteractive

echo "[Cheeky] Updating package lists..."
apt-get update -qq

echo "[Cheeky] Installing core dependencies..."
apt-get install -y -qq \
  python3-pip \
  python3-dev \
  build-essential \
  python3-dbus \
  pulseaudio \
  pulseaudio-utils \
  bluez \
  mpv \
  libmpv1 \
  avahi-daemon \
  wget \
  curl \
  git

echo "[Cheeky] Installing Python packages..."
pip3 install --break-system-packages \
  fastapi==0.104.1 \
  uvicorn[standard]==0.24.0 \
  aiohttp==3.9.0 \
  pydantic==2.5.0 \
  websockets==12.0 \
  python-multipart==0.0.6 \
  python-mpv==1.0.4

echo "[Cheeky] Installing Radio Player..."
mkdir -p /opt/cheeky/radio-player
cp -r /root/cheeky/config/radio-player/* /opt/cheeky/radio-player/

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

echo "[Cheeky] Installing Bluetooth auto-reconnect..."
cp /root/cheeky/config/bluetooth-reconnect.sh /usr/local/bin/cheeky-bluetooth-reconnect.sh
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

echo "[Cheeky] Enabling services..."
systemctl daemon-reload
systemctl enable cheeky-radio-player
systemctl enable cheeky-bluetooth-reconnect
systemctl enable bluetooth
systemctl enable avahi-daemon

echo "[Cheeky] Creating version marker..."
echo "CHEEKY_VERSION=VERSION_PLACEHOLDER" > /etc/cheeky-version
touch /root/.cheeky-installed

echo "[Cheeky] Installation complete!"
