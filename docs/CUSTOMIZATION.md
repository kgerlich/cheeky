# Customization Guide

Learn how to customize Cheeky for your needs!

## For End Users

### Change Mopidy Configuration

You can customize the music server behavior:

```bash
# SSH into your Pi
ssh root@raspberrypi.local

# Edit Mopidy config
nano /etc/mopidy/mopidy.conf

# Restart Mopidy to apply changes
systemctl restart mopidy
```

**Common configurations**:

**Change audio output quality**:
```ini
[tunein]
max_bitrate = 320  # 96, 128, 192, 256, 320 kbps
```

**Change HTTP port**:
```ini
[http]
port = 6681
```

**Enable logging**:
```ini
[logging]
level = debug
```

### Customize Web Interface

The web interfaces are served by Mopidy (port 6680) and FastAPI (port 8080).

**For radio interface** (Mopidy Iris), you can:
- Customize theme colors
- Change layout
- See [Iris documentation](https://github.com/jaedb/Iris)

**For Bluetooth manager** (port 8080), edit:
```bash
nano /opt/cheeky/bluetooth-web-manager/templates/index.html  # HTML
nano /opt/cheeky/bluetooth-web-manager/static/app.js         # JavaScript
```

Changes take effect immediately (refresh browser).

### Add Custom Radio Stations

Add stations to your Mopidy playlists:

```bash
# SSH in
ssh root@raspberrypi.local

# Edit playlist file
nano /var/lib/mopidy/playlists/custom.m3u

# Add station URLs:
# #EXTINF:-1,Station Name
# http://station-url:port
```

Reload the web interface to see new playlists.

### Change System Timezone

```bash
ssh root@raspberrypi.local
timedatectl set-timezone America/New_York
```

### Change Hostname

Change how your Pi appears on the network:

```bash
ssh root@raspberrypi.local
hostnamectl set-hostname my-radio
reboot
```

After reboot, access via `http://my-radio.local:6680`

---

## For Developers

### Building Custom Images

You can create your own Cheeky images with custom software.

**Requirements**:
- Linux machine (Ubuntu 20.04+ recommended)
- 20GB free disk space
- Tools: `p7zip-full`, `kpartx`, `qemu-user-static`, `xz-utils`

**Steps**:

1. **Clone the repository**:
   ```bash
   git clone https://github.com/cheeky-radio/cheeky.git
   cd cheeky
   ```

2. **Download DietPi base image**:
   ```bash
   mkdir -p base-images
   cd base-images
   wget https://dietpi.com/downloads/images/DietPi_RPi-ARMv8-Bookworm.7z
   7z x DietPi_RPi-ARMv8-Bookworm.7z
   ```

3. **Customize build script** (`scripts/build.sh`):
   Add your custom software installation commands

4. **Run build**:
   ```bash
   chmod +x scripts/build.sh
   sudo scripts/build.sh \
     --arch armv8 \
     --base-image base-images/armv8.img \
     --output my-cheeky-custom.img \
     --version 1.0.0-custom
   ```

5. **Test in QEMU**:
   ```bash
   xz my-cheeky-custom.img
   # Follow QEMU guide to test
   ```

### Adding Custom Services

Add your own services to start on boot:

1. **Create a systemd service file**:
   ```bash
   nano /etc/systemd/system/my-service.service
   ```

2. **Add service definition**:
   ```ini
   [Unit]
   Description=My Custom Service
   After=network.target

   [Service]
   Type=simple
   User=root
   ExecStart=/usr/local/bin/my-service.py
   Restart=always

   [Install]
   WantedBy=multi-user.target
   ```

3. **Enable and start**:
   ```bash
   systemctl daemon-reload
   systemctl enable my-service
   systemctl start my-service
   ```

### Extending the Bluetooth Manager

Add features to the web interface:

**Add new API endpoint** (`config/bluetooth-web-manager/main.py`):
```python
from fastapi import FastAPI

app = FastAPI()

@app.get("/api/my-feature")
async def my_feature():
    return {"result": "Hello from Cheeky!"}
```

**Add web UI** (`config/bluetooth-web-manager/templates/index.html`):
```html
<button @click="loadFeature()" class="btn btn-primary">
  Click me!
</button>
```

**Add JavaScript** (`config/bluetooth-web-manager/static/app.js`):
```javascript
async function loadFeature() {
  const response = await fetch('/api/my-feature');
  const data = await response.json();
  console.log(data.result);
}
```

### Adding Mopidy Extensions

Install additional Mopidy extensions:

```bash
ssh root@raspberrypi.local

# Install extension
pip install mopidy-spotify  # Example: Spotify support

# Edit config
nano /etc/mopidy/mopidy.conf
# Add:
# [spotify]
# username = your-spotify-email
# password = your-spotify-password

# Restart
systemctl restart mopidy
```

Popular extensions:
- `mopidy-spotify` - Spotify support
- `mopidy-youtube` - YouTube Music
- `mopidy-podcast` - Podcast support
- `mopidy-jellyfin` - Jellyfin music server

### Modifying First Boot Behavior

Edit the first-boot automation script:

```bash
nano config/Automation_Custom_Script.sh
```

This script runs on first boot and installs all software. Add your custom commands here.

**Example**: Auto-update DNS servers
```bash
# Add at the end of Automation_Custom_Script.sh
echo "nameserver 1.1.1.1" > /etc/resolv.conf
echo "nameserver 8.8.8.8" >> /etc/resolv.conf
```

---

## Docker-based Customization (Advanced)

You can run Cheeky in Docker instead of on physical hardware:

**Dockerfile** (example):
```dockerfile
FROM arm32v7/debian:bookworm

# Install dependencies
RUN apt-get update && apt-get install -y \
    mopidy \
    pulseaudio \
    bluez \
    python3-pip

# Copy config
COPY config/mopidy.conf /etc/mopidy/mopidy.conf

# Expose ports
EXPOSE 6680 8080

# Start services
CMD ["bash", "-c", "mopidy & python3 -m bluetooth_manager"]
```

**Build and run**:
```bash
docker build -t my-cheeky .
docker run -d \
  -p 6680:6680 \
  -p 8080:8080 \
  --device /dev/snd \
  my-cheeky
```

---

## Configuration Files Reference

### Mopidy Config (`/etc/mopidy/mopidy.conf`)

```ini
[http]
port = 6680
hostname = 0.0.0.0

[mpd]
port = 6600

[tunein]
timeout = 10

[local]
media_dir = /var/lib/mopidy/media
```

### DietPi Config (`/boot/dietpi.txt`)

```
AUTO_UNMASK_LOGIND=1
BOOT_WAIT_FOR_NETWORK=1
DIETPI_SURVEY_OPTED_OUT=1
```

### Bluetooth Manager Config

The FastAPI app looks for these environment variables:

```bash
DEVICE_TIMEOUT=10        # Seconds to wait for device operations
LOG_LEVEL=INFO           # DEBUG, INFO, WARNING, ERROR
PORT=8080                # HTTP port
```

---

## Version Customization

If you're building a custom variant:

1. **Update version in tag**:
   ```bash
   git tag -a v1.0.0-custom -m "My custom build"
   ```

2. **Update release notes** in `.github/workflows/build-release.yml`

3. **Document changes** in a new document:
   ```bash
   touch CUSTOM-CHANGES.md
   ```

---

## Performance Tuning

### For Older Raspberry Pi Models (Pi Zero, Pi 1)

Reduce resource usage:

```bash
ssh root@raspberrypi.local

# Disable logging
nano /etc/mopidy/mopidy.conf
# Change to:
# [logging]
# level = info

# Reduce UI complexity (use older browser or simpler UI)

# Monitor resources
top
free -h
df -h
```

### For Newer Models (Pi 4, Pi 5)

Increase performance:

```bash
nano /etc/mopidy/mopidy.conf
# Add:
# [tunein]
# max_bitrate = 320

# Allocate more CPU
nano /etc/security/limits.conf
# Add:
# * soft nofile 4096
# * hard nofile 65536
```

---

## Backup & Recovery

### Backup Your Configuration

```bash
ssh root@raspberrypi.local

# Backup key files
tar czf ~/cheeky-backup.tar.gz \
  /etc/mopidy/mopidy.conf \
  /opt/cheeky/ \
  /var/lib/mopidy/playlists/

# Download backup
# On your computer:
scp root@raspberrypi.local:~/cheeky-backup.tar.gz .
```

### Restore from Backup

```bash
# On your computer:
scp cheeky-backup.tar.gz root@raspberrypi.local:~/

# On Pi:
ssh root@raspberrypi.local
tar xzf ~/cheeky-backup.tar.gz -C /
systemctl restart mopidy
systemctl restart cheeky-bluetooth-manager
```

---

## Troubleshooting Custom Changes

**Service won't start**:
```bash
# Check logs
journalctl -u service-name -n 50

# Check syntax (for config files)
# Test the application manually
```

**Port conflicts**:
```bash
# Find what's using a port
lsof -i :8080

# Use a different port
nano /etc/mopidy/mopidy.conf
# Change: port = 6681
```

**High CPU/Memory usage**:
```bash
# Monitor
top
ps aux | sort -nrk 3,3 | head -n 5

# Disable unnecessary features
```

---

## Contributing Custom Features Back

If you build something cool, consider contributing it back:

1. Fork the [Cheeky repository](https://github.com/cheeky-radio/cheeky)
2. Make your changes
3. Test thoroughly
4. Submit a pull request
5. Engage with the community!

See [CONTRIBUTING.md](../CONTRIBUTING.md) for guidelines.

---

Questions about customization?
- 📖 Check [CLAUDE.md](../CLAUDE.md) for architecture details
- 💬 [Ask on GitHub Discussions](https://github.com/cheeky-radio/cheeky/discussions)
- 🐛 [Report issues](https://github.com/cheeky-radio/cheeky/issues)

🍑 Make Cheeky your own!
