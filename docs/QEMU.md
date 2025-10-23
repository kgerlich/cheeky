# QEMU Testing Guide

Test Cheeky without a Raspberry Pi using QEMU emulation!

## Quick Start

### 1. Download QEMU Bundle

From the [GitHub Releases page](https://github.com/cheeky-radio/cheeky/releases), download the bundle for your OS:

- **Linux**: `cheeky-qemu-linux-v*.tar.gz`
- **macOS**: `cheeky-qemu-macos-v*.tar.gz`
- **Windows**: `cheeky-qemu-windows-v*.zip`

### 2. Extract

**Linux/macOS**:
```bash
tar xzf cheeky-qemu-linux-v1.0.0.tar.gz
cd linux
```

**Windows**:
```
Extract cheeky-qemu-windows-v1.0.0.zip
Open the extracted folder
```

### 3. Run

**Linux/macOS**:
```bash
./start-qemu.sh
```

**Windows**:
```
Double-click start-qemu.bat
```

### 4. Access

Open your browser and visit:

- **Radio Interface**: http://localhost:6680
- **Bluetooth Manager**: http://localhost:8080
- **SSH** (optional): `ssh -p 2222 root@localhost` (password: `raspberry`)

First run will download the Pi image (~180MB). Subsequent runs use the cached image and start instantly.

## What Works in QEMU

✅ **Web Interfaces**
- Load and interact with radio control (port 6680)
- Load and interact with Bluetooth manager (port 8080)

✅ **Radio Functionality**
- Browse TuneIn stations
- Search for stations by genre/location
- Play stations (audio goes to host, not emulated speakers)
- Test UI responsiveness

✅ **Networking**
- Full network access
- Port forwarding preconfigured
- SSH access to the emulated Pi

✅ **UI Development**
- Test web interface changes
- Debug JavaScript/CSS
- Test on different screen sizes

## What Doesn't Work in QEMU

❌ **Bluetooth Audio**
- No real Bluetooth hardware in VM
- The web interface works, but you can't pair real speakers
- Use for testing the UI only

❌ **GPIO Access**
- GPIO pins are emulated only
- Hardware-specific features won't work

❌ **Real Audio Playback**
- Can't output audio to speakers in QEMU
- Can play for testing, but no audio device

## Common Workflows

### Testing Web Interface Changes

```bash
# Start QEMU
./start-qemu.sh

# In another terminal, SSH in and edit files
ssh -p 2222 root@localhost

# Make changes to /opt/cheeky/bluetooth-web-manager/
# Changes will be live (Alpine.js reacts immediately)

# Refresh browser to see changes
```

### Testing Radio Functionality

1. Start QEMU
2. Visit http://localhost:6680
3. Browse TuneIn stations
4. Test search functionality
5. Verify UI responsiveness on different screen sizes

### Testing Bluetooth Manager UI

1. Start QEMU
2. Visit http://localhost:8080
3. Test layout and responsiveness
4. Verify form validation
5. Check error handling

## Troubleshooting QEMU

### QEMU Won't Start

**Error**: "qemu-system-aarch64: command not found"

**Solution**: Install QEMU
```bash
# Linux (Ubuntu/Debian)
sudo apt-get install qemu-system-arm

# macOS
brew install qemu

# Windows
Download from https://qemu.weilnetz.de/
```

### Port Already in Use

**Error**: "Address already in use: 6680"

**Solution**: Stop the conflicting process
```bash
# Find process using port 6680
lsof -i :6680

# Kill it
kill -9 <PID>

# Or use different port in start script
```

### Not Enough Disk Space

**Error**: Image download or boot fails

**Solution**: Free up space
```bash
# Check available space
df -h

# Need at least 10GB free
```

### QEMU is Slow

**Note**: Emulation is slower than real hardware. This is normal.

**Tips**:
- Close other applications
- Increase available RAM
- QEMU on Linux is faster than on Windows/Mac

### Can't Connect to localhost

**Issue**: Browser can't reach http://localhost:6680

**Solution**:
- Ensure QEMU started successfully (check terminal output)
- Wait 30 seconds for Pi to boot in QEMU
- Try refreshing (Ctrl+R)
- Try http://127.0.0.1:6680 instead

## SSH into QEMU

Access the emulated Pi via SSH:

```bash
ssh -p 2222 root@localhost
# Password: raspberry
```

Once connected, you can:
- Edit configuration files
- View logs: `journalctl -u mopidy`
- Restart services: `systemctl restart mopidy`
- Install additional software

## Exiting QEMU

To stop QEMU:

**Linux/macOS**:
- Press `Ctrl+A` then `X` in the terminal

**Windows**:
- Press `Ctrl+Alt+Delete` (exits the terminal window)

Alternatively, from another terminal:
```bash
# Find QEMU process
ps aux | grep qemu

# Kill it
kill -9 <PID>
```

## Advanced: Custom QEMU Configuration

Edit the `start-qemu.sh` (or `.bat`) file to customize:

- **Memory**: `-m 2048` (MB of RAM)
- **CPU cores**: `-smp 2` (number of cores)
- **Ports**: `-hostfwd=tcp::6680-:6680` (port mapping)

Example: Allocate 4GB RAM to QEMU
```bash
# In start-qemu.sh, change:
-m 2048 \
# to:
-m 4096 \
```

## Performance Expectations

- **First boot**: 30-60 seconds (downloads image)
- **Subsequent boots**: 10-20 seconds
- **Web page load**: 1-3 seconds
- **Station search**: 2-5 seconds
- **Overall**: Slower than real hardware, but adequate for testing UI

## Using QEMU in CI/CD

You can integrate QEMU testing into your GitHub Actions:

```yaml
- name: Test in QEMU
  run: |
    tar xzf cheeky-qemu-linux-v1.0.0.tar.gz
    cd linux
    timeout 120 ./start-qemu.sh &
    sleep 30
    curl -f http://localhost:6680 || exit 1
    curl -f http://localhost:8080 || exit 1
```

## Limitations

- **No Bluetooth testing**: Real speakers won't pair
- **No GPIO testing**: Hardware features unavailable
- **Performance**: Emulation is slower than real hardware
- **Audio**: Can't test real audio output to speakers

## What's Next?

After testing in QEMU:

1. **Try on real Pi**: See [Installation Guide](INSTALLATION.md)
2. **Pair Bluetooth speaker**: Only works on real Pi
3. **Contribute changes**: See [Contributing Guide](../CONTRIBUTING.md)

---

💡 **Pro Tip**: Use QEMU for rapid UI development. Boot in seconds, make changes, see results immediately!

Questions? [Open an issue on GitHub](https://github.com/cheeky-radio/cheeky/issues)

🍑 Be cheeky with your testing!
