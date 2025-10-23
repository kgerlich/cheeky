# Cheeky QEMU Bundle - Linux/macOS

Test Cheeky without a Raspberry Pi!

## Requirements

- **QEMU**: `sudo apt install qemu-system-arm` (Linux) or `brew install qemu` (macOS)
- **Disk space**: 10GB free
- **RAM**: 4GB available
- **Internet**: For first-run image download

## Quick Start

1. **Ensure QEMU is installed**:
   ```bash
   which qemu-system-aarch64
   ```

2. **Make script executable**:
   ```bash
   chmod +x start-qemu.sh
   ```

3. **Run the launcher**:
   ```bash
   ./start-qemu.sh
   ```

4. **Wait for boot** (30-60 seconds on first run):
   ```
   Booting Cheeky Linux...
   ...
   Cheeky Setup Complete!
   ```

5. **Open in browser**:
   - **Radio**: http://localhost:6680
   - **Bluetooth Manager**: http://localhost:8080
   - **SSH** (optional): `ssh -p 2222 root@localhost` (password: `raspberry`)

## What Happens

**First run**:
- Downloads the Pi image (~180MB) - only happens once
- Extracts image
- Resizes for QEMU
- Boots in QEMU (~60 seconds)

**Subsequent runs**:
- Uses cached image
- Boots quickly (~20 seconds)

## Exiting QEMU

- **Linux/macOS**: Press `Ctrl+A` then `X`
- Or in another terminal: `pkill qemu`

## Troubleshooting

### QEMU not found
```bash
# Linux (Ubuntu/Debian)
sudo apt-get install qemu-system-arm

# macOS
brew install qemu
```

### Port already in use
```bash
# Find process on port 6680
lsof -i :6680
# Kill it
kill -9 <PID>
```

### Not enough disk space
```bash
# Check available space
df -h
# Need at least 10GB free
```

### Download fails
```bash
# Check internet connection
ping github.com

# Download manually if needed
wget https://github.com/cheeky-radio/cheeky/releases/download/VERSION_PLACEHOLDER/cheeky-armv8-VERSION_PLACEHOLDER.img.xz
xz -d cheeky-armv8-VERSION_PLACEHOLDER.img.xz
./start-qemu.sh
```

## Advanced Options

Edit `start-qemu.sh` to customize:

```bash
# Allocate more RAM (in MB)
-m 4096  # Instead of 2048

# Change port forwarding
-hostfwd=tcp::6680-:6680  # Forward port 6680
```

## What Works

✅ Web interfaces (radio + Bluetooth manager)
✅ Radio station browsing and playback
✅ Network access
✅ SSH to the emulated Pi

## What Doesn't Work

❌ Real Bluetooth audio (no hardware in VM)
❌ GPIO access
❌ Hardware-specific features

For full Bluetooth testing, use a real Raspberry Pi!

---

For help, see [Cheeky Documentation](../../docs/QEMU.md) or [report an issue](https://github.com/cheeky-radio/cheeky/issues)

🍑 Be cheeky with your testing!
