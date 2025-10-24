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
  python3-gi \
  python3-dbus \
  build-essential \
  pulseaudio \
  pulseaudio-utils \
  bluez \
  alsa-utils \
  avahi-daemon \
  wget \
  curl \
  git \
  gstreamer1.0-tools \
  gstreamer1.0-plugins-good \
  gstreamer1.0-plugins-bad \
  gstreamer1.0-plugins-ugly \
  gir1.2-gstreamer-1.0 \
  gir1.2-gst-plugins-base-1.0

echo "[Cheeky] Installing Python packages..."
pip3 install --break-system-packages \
  mopidy \
  mopidy-iris \
  mopidy-tunein \
  fastapi==0.109.0 \
  uvicorn[standard]==0.27.0 \
  pydantic==2.5.0 \
  python-multipart==0.0.6

echo "[Cheeky] Creating Mopidy configuration..."
mkdir -p /etc/mopidy
cp /root/cheeky/config/mopidy.conf /etc/mopidy/mopidy.conf

# Create Mopidy system user
useradd -r -m -s /bin/false -d /var/lib/mopidy mopidy 2>/dev/null || true
mkdir -p /var/lib/mopidy/media
chown -R mopidy:mopidy /var/lib/mopidy

echo "[Cheeky] Creating Mopidy systemd service..."
cat > /etc/systemd/system/mopidy.service << 'EOF'
[Unit]
Description=Mopidy Music Server
After=network.target sound.target

[Service]
Type=simple
User=mopidy
ExecStart=/usr/local/bin/mopidy --config /etc/mopidy/mopidy.conf
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF

echo "[Cheeky] Installing Bluetooth Manager..."
mkdir -p /opt/cheeky/bluetooth-web-manager
cp -r /root/cheeky/config/bluetooth-web-manager/* /opt/cheeky/bluetooth-web-manager/

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
systemctl enable mopidy
systemctl enable cheeky-bluetooth-manager
systemctl enable cheeky-bluetooth-reconnect
systemctl enable bluetooth
systemctl enable avahi-daemon

echo "[Cheeky] Creating version marker..."
echo "CHEEKY_VERSION=VERSION_PLACEHOLDER" > /etc/cheeky-version
touch /root/.cheeky-installed

echo "[Cheeky] Installation complete!"
