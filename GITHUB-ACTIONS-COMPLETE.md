# Complete GitHub Actions Automation for Cheeky

This document describes the fully automated build system that requires **ZERO local setup**.

## Overview

Everything is built in GitHub Actions:
1. ✅ Pi images for all architectures (ARMv6, ARMv7, ARMv8)
2. ✅ QEMU bundles for Linux, macOS, Windows
3. ✅ Automatic compression and checksums
4. ✅ GitHub releases with all assets
5. ✅ Headless WiFi configuration built-in

**Users just download and use. No compilation, no setup, nothing.**

---

## How It Works

```
Developer pushes tag: v1.0.0
         ↓
GitHub Actions Triggered
         ↓
    ┌────────────────────────────┐
    │  Job 1: Build Pi Images    │
    │  - Download DietPi bases   │
    │  - Build ARMv6, 7, 8       │
    │  - Compress with xz -9     │
    │  - Generate checksums      │
    └────────────────────────────┘
         ↓
    ┌────────────────────────────┐
    │  Job 2: Build QEMU Bundles │
    │  - Download QEMU kernel    │
    │  - Create launch scripts   │
    │  - Package for Linux/Mac/Win│
    └────────────────────────────┘
         ↓
    ┌────────────────────────────┐
    │  Job 3: Create Release     │
    │  - Collect all artifacts   │
    │  - Generate release notes  │
    │  - Publish to GitHub       │
    └────────────────────────────┘
         ↓
    Release Published!
    Users download ready-to-use files
```

---

## User Experience

### For Physical Pi Users:

```bash
# 1. Download image from GitHub Releases
wget https://github.com/cheeky-radio/cheeky/releases/download/v1.0.0/cheeky-armv8-v1.0.0.img.xz

# 2. Flash to SD card
xz -d cheeky-armv8-v1.0.0.img.xz
sudo dd if=cheeky-armv8-v1.0.0.img of=/dev/sdX bs=4M

# 3. (Optional) Configure WiFi before first boot
#    Just add WiFi details to dietpi-wifi.txt on boot partition

# 4. Boot Pi
#    Everything installs automatically!

# 5. Access web interfaces
#    Radio: http://raspberrypi.local:6680
#    Bluetooth: http://raspberrypi.local:8080
```

### For QEMU Users:

```bash
# 1. Download QEMU bundle
wget https://github.com/cheeky-radio/cheeky/releases/download/v1.0.0/cheeky-qemu-linux-v1.0.0.tar.gz

# 2. Extract and run
tar xzf cheeky-qemu-linux-v1.0.0.tar.gz
cd linux
./start-qemu.sh

# The script automatically:
# - Downloads the Pi image (first time only)
# - Extracts and prepares it
# - Launches QEMU with port forwarding
# - Opens access to http://localhost:6680
```

---

## Complete Workflow Files

See the detailed workflow in the full document.

Key features:
- **Parallel builds** for speed
- **Caching** of base images
- **Automatic versioning** from git tags
- **Comprehensive release notes**
- **All platforms supported**

---

## Headless WiFi Configuration

Three methods for users:

### Method 1: Raspberry Pi Imager (Easiest)
- Use the built-in WiFi configuration
- Set SSID and password in Advanced Options
- Flash and boot - auto-connects!

### Method 2: Manual (Before First Boot)
- After flashing, before ejecting SD card
- Edit `/boot/dietpi-wifi.txt`
- Add WiFi credentials
- Boot - auto-connects!

### Method 3: After First Boot
- Connect via Ethernet
- SSH in and run `dietpi-config`
- Configure WiFi

---

## What Gets Built

### Pi Images (3 variants):
- `cheeky-armv8-v1.0.0.img.xz` (~180 MB) - Pi Zero 2 W, 3, 4, 5
- `cheeky-armv7-v1.0.0.img.xz` (~170 MB) - Pi 2
- `cheeky-armv6-v1.0.0.img.xz` (~160 MB) - Pi Zero W, Pi 1

### QEMU Bundles (3 platforms):
- `cheeky-qemu-linux-v1.0.0.tar.gz` (~50 MB)
- `cheeky-qemu-macos-v1.0.0.tar.gz` (~50 MB)  
- `cheeky-qemu-windows-v1.0.0.zip` (~50 MB)

### Checksums:
- SHA256 for each image
- MD5 for each image

---

## Triggering Builds

### Automatic (Production):
```bash
git tag -a v1.0.0 -m "Release v1.0.0"
git push origin v1.0.0
```

### Manual (Testing):
- Go to GitHub Actions tab
- Select "Build Cheeky Release"
- Click "Run workflow"
- Enter version (e.g., v1.0.0-beta)

---

## Zero Local Setup Required

**Users need:**
- Internet connection
- SD card (for Pi) OR QEMU (for testing)
- That's it!

**Users don't need:**
- Linux build environment
- Cross-compilation tools
- Python/Node.js
- Docker
- Any technical knowledge

**Everything is pre-built and ready to use!** 🍑

---

For complete workflow code, see the repository `.github/workflows/` directory.
