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
    python3-glib \
    build-essential \
    pulseaudio \
    pulseaudio-utils \
    bluez \
    bluez-tools \
    alsa-utils \
    avahi-daemon \
    wget \
    curl \
    git

# Install Mopidy
echo "[Cheeky] Installing Mopidy music server..."
pip3 install --upgrade pip
pip3 install mopidy mopidy-iris mopidy-tunein

# Install FastAPI for Bluetooth Manager
echo "[Cheeky] Installing FastAPI for Bluetooth Manager..."
pip3 install fastapi uvicorn python-multipart

# Create Mopidy configuration directory
mkdir -p /etc/mopidy
cp config/mopidy.conf /etc/mopidy/mopidy.conf

# Create Mopidy system user and directories
useradd -r -m -s /bin/false -d /var/lib/mopidy mopidy 2>/dev/null || true
mkdir -p /var/lib/mopidy
chown -R mopidy:mopidy /var/lib/mopidy

# Create systemd service for Mopidy
echo "[Cheeky] Creating Mopidy systemd service..."
cat > /etc/systemd/system/mopidy.service << 'EOF'
[Unit]
Description=Mopidy Music Server
After=network.target sound.target pulseaudio.service

[Service]
Type=simple
User=mopidy
ExecStart=/usr/local/bin/mopidy --config /etc/mopidy/mopidy.conf
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF

# Install Bluetooth Manager (FastAPI app)
echo "[Cheeky] Installing Bluetooth Manager..."
mkdir -p /opt/cheeky/bluetooth-web-manager
cp -r config/bluetooth-web-manager/* /opt/cheeky/bluetooth-web-manager/

# Create Bluetooth Manager systemd service
echo "[Cheeky] Creating Bluetooth Manager systemd service..."
cat > /etc/systemd/system/cheeky-bluetooth-manager.service << 'EOF'
[Unit]
Description=Cheeky Bluetooth Manager
After=network.target bluetooth.service

[Service]
Type=simple
User=root
WorkingDirectory=/opt/cheeky/bluetooth-web-manager
ExecStart=/usr/bin/python3 -m uvicorn main:app --host 0.0.0.0 --port 8080
Restart=always
RestartSec=10

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

# Enable BlueZ for background pairing
echo "[Cheeky] Configuring BlueZ for automatic pairing..."
mkdir -p /var/lib/bluetooth
chmod 755 /var/lib/bluetooth

# Enable and start services
echo "[Cheeky] Enabling services..."
systemctl daemon-reload
systemctl enable mopidy
systemctl enable cheeky-bluetooth-manager
systemctl enable cheeky-bluetooth-reconnect
systemctl enable bluetooth
systemctl enable pulseaudio

# Configure PulseAudio
echo "[Cheeky] Configuring PulseAudio..."
mkdir -p /var/lib/mopidy/.config/pulse
cat >> /var/lib/mopidy/.config/pulse/client.conf << 'EOF'
autospawn = yes
daemon-binary = /usr/bin/pulseaudio
EOF

# Start services
echo "[Cheeky] Starting services..."
systemctl start pulseaudio
systemctl start bluetooth
systemctl start mopidy
systemctl start cheeky-bluetooth-manager
systemctl start cheeky-bluetooth-reconnect

# Verify services are running
echo ""
echo "[Cheeky] Verifying services..."
sleep 2

if systemctl is-active --quiet mopidy; then
    echo "✓ Mopidy is running (port 6680)"
else
    echo "✗ Mopidy failed to start"
fi

if systemctl is-active --quiet cheeky-bluetooth-manager; then
    echo "✓ Bluetooth Manager is running (port 8080)"
else
    echo "✗ Bluetooth Manager failed to start"
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
echo "Access your radio:"
echo "  http://raspberrypi.local:6680"
echo ""
echo "Manage Bluetooth speakers:"
echo "  http://raspberrypi.local:8080"
echo ""
echo "SSH access (if needed):"
echo "  ssh root@raspberrypi.local"
echo "  password: raspberry"
echo ""
echo "Don't take radio too seriously. Be cheeky! 🍑"
echo ""
