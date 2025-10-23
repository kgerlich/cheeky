# Product Requirements Document (PRD)
## Cheeky - Raspberry Pi Internet Radio

```
 ██████╗██╗  ██╗███████╗███████╗██╗  ██╗██╗   ██╗
██╔════╝██║  ██║██╔════╝██╔════╝██║ ██╔╝╚██╗ ██╔╝
██║     ███████║█████╗  █████╗  █████╔╝  ╚████╔╝ 
██║     ██╔══██║██╔══╝  ██╔══╝  ██╔═██╗   ╚██╔╝  
╚██████╗██║  ██║███████╗███████╗██║  ██╗   ██║   
 ╚═════╝╚═╝  ╚═╝╚══════╝╚══════╝╚═╝  ╚═╝   ╚═╝   

🍑 A cheeky little radio for your Pi
```

**Version:** 1.0.0  
**Date:** October 23, 2025  
**Status:** Ready for Development  
**Project Type:** Open Source GitHub Project  
**Project Name:** Cheeky

---

## Executive Summary

**Cheeky** is a lightweight, web-controlled internet radio system for Raspberry Pi that provides access to 100,000+ radio stations via TuneIn with Bluetooth speaker output. The system features automated image building via GitHub Actions, making it easy for users to flash and deploy on any Raspberry Pi model.

Don't take radio too seriously. Be cheeky.

### Key Differentiators
- **Zero configuration:** Flash and boot - ready in 2 minutes
- **Universal compatibility:** Single image works across Pi Zero 2 W, Pi 3, Pi 4, Pi 5
- **Minimal footprint:** ~180MB compressed image (DietPi-based)
- **Modern stack:** FastAPI + Tailwind CSS for clean, responsive UI
- **Automated releases:** GitHub Actions builds and publishes images automatically

---

## Table of Contents

1. [Product Vision](#product-vision)
2. [Target Audience](#target-audience)
3. [Core Features](#core-features)
4. [Technical Architecture](#technical-architecture)
5. [QEMU Emulation for Development](#qemu-emulation-for-development)
6. [Hardware Support](#hardware-support)
7. [User Stories](#user-stories)
8. [System Requirements](#system-requirements)
9. [Build Pipeline](#build-pipeline)
10. [Web Interfaces](#web-interfaces)
11. [API Specifications](#api-specifications)
12. [Security Considerations](#security-considerations)
13. [Testing Strategy](#testing-strategy)
14. [Deployment & Distribution](#deployment-distribution)
15. [Success Metrics](#success-metrics)
16. [Roadmap](#roadmap)
17. [Open Questions](#open-questions)

---

## 1. Product Vision

### Mission Statement
Democratize internet radio by providing a simple, open-source solution that anyone can deploy on a Raspberry Pi in minutes - without taking ourselves too seriously. **Cheeky** makes radio fun again.

### Tagline
**"A cheeky approach to internet radio"**

### Problem Statement
- Existing internet radio solutions are complex to set up and too serious
- Commercial solutions are expensive or ad-supported
- Developers need physical Raspberry Pi hardware to test
- Managing Bluetooth connections typically requires SSH access
- No unified solution for all Raspberry Pi models
- Radio projects lack personality

### Solution
**Cheeky** provides a pre-built, optimized Linux image with:
- TuneIn integration for 100,000+ radio stations
- Modern web interfaces for radio control and Bluetooth management
- QEMU emulation support for development and testing without hardware
- Automated CI/CD pipeline for multi-architecture builds
- Bluetooth speaker control via web browser
- A playful attitude that makes tech approachable

---

## 2. Target Audience

### Primary Users
1. **Hobbyists & Makers**
   - Want a DIY internet radio solution
   - Comfortable with basic tech (flashing SD cards)
   - May not own Raspberry Pi hardware yet

2. **Developers**
   - Building custom radio/audio projects
   - Need to test before buying hardware
   - Want to contribute to open source

3. **Non-Technical Users**
   - Want simple internet radio
   - Don't want to deal with command line
   - Need everything "just work"

### Secondary Users
1. **Home Automation Enthusiasts**
   - Integrating into smart home setups
   - Multi-room audio systems

2. **Educational Institutions**
   - Teaching Linux/IoT concepts
   - Student projects

---

## 3. Core Features

### 3.1 Internet Radio (Priority: P0 - MVP)
- **TuneIn Integration**
  - Access to 100,000+ stations worldwide
  - Browse by location, genre, language
  - Search functionality
  - No API key required

### 3.1 Internet Radio (Priority: P0 - MVP)
- **TuneIn Integration**
  - Access to 100,000+ stations worldwide
  - Browse by location, genre, language
  - Search functionality
  - No API key required

- **Web Interface (Mopidy Iris)**
  - Port: 6680
  - Play/pause/stop controls
  - Volume control
  - Station favorites
  - Search and browse
  - Mobile-responsive design

### 3.2 Bluetooth Management (Priority: P0 - MVP)
- **Web Interface (FastAPI + Tailwind)**
  - Port: 8080
  - List paired devices
  - Connect/disconnect speakers
  - Scan for new devices
  - Pair new speakers
  - Remove devices
  - Real-time connection status

### 3.3 QEMU Emulation (Priority: P0 - MVP)
- **Pre-configured QEMU Environment**
  - Complete VM bundle with networking
  - Port forwarding pre-configured
  - Works on Linux, macOS, Windows
  - No manual kernel/DTB configuration needed
  - One-click start scripts

- **GitHub Release Assets**
  - QEMU wrapper scripts for all platforms
  - Pre-configured for ARM emulation
  - Automatic port mapping (6680, 8080, 22)
  - Network configuration included

### 3.4 Multi-Architecture Support (Priority: P0 - MVP)
- ARMv8 (Pi Zero 2 W, Pi 3, Pi 4, Pi 5)
- ARMv7 (Pi 2)
- ARMv6 (Pi Zero W, Pi 1)

### 3.5 Auto-Configuration (Priority: P0 - MVP)
- First-boot automation via DietPi
- Service auto-start on boot
- Bluetooth auto-reconnect
- WiFi configuration helper

---

## 4. Technical Architecture

### 4.1 System Stack

```
┌─────────────────────────────────────────┐
│         User's Browser/QEMU             │
│  ┌──────────┐          ┌─────────────┐ │
│  │ Radio UI │          │ BT Manager  │ │
│  │ :6680    │          │ :8080       │ │
│  └──────────┘          └─────────────┘ │
└─────────────────────────────────────────┘
         │                      │
         ↓                      ↓
    ┌─────────┐          ┌─────────────┐
    │ Mopidy  │          │  FastAPI    │
    │ + Iris  │          │  + Uvicorn  │
    └─────────┘          └─────────────┘
         │                      │
         ↓                      ↓
    ┌─────────────────────────────────┐
    │      PulseAudio + BlueZ         │
    └─────────────────────────────────┘
         │
         ↓
    ┌─────────────────────────────────┐
    │     DietPi (Debian-based)       │
    └─────────────────────────────────┘
         │
         ↓
    ┌─────────────────────────────────┐
    │  Physical Pi OR QEMU Emulation  │
    └─────────────────────────────────┘
```

### 4.2 Component Details

**Base OS: DietPi**
- Optimized Debian-based distribution
- ~150MB compressed
- Automated first-boot configuration
- Built-in software installer

**Audio Stack:**
- PulseAudio: Audio server
- BlueZ: Bluetooth stack
- ALSA: Low-level audio drivers

**Radio Backend:**
- Mopidy: Music server daemon
- Mopidy-TuneIn: TuneIn extension
- Mopidy-Iris: Web interface

**Bluetooth Manager:**
- FastAPI: Web framework
- Uvicorn: ASGI server
- Alpine.js: Frontend reactivity
- Tailwind CSS: UI styling

---

## 5. QEMU Emulation for Development

### 5.1 Overview

**Purpose:** Allow developers to test the internet radio system without physical Raspberry Pi hardware.

**Approach:** Provide pre-packaged QEMU bundles with all configurations included in GitHub releases.

### 5.2 QEMU Architecture Options

#### Option A: Full System Emulation (Recommended)
```
┌──────────────────────────────────────┐
│   Host Machine (Linux/Mac/Windows)   │
│                                      │
│  ┌────────────────────────────────┐ │
│  │  QEMU VM (ARM64 emulation)     │ │
│  │                                │ │
│  │  ┌──────────────────────────┐ │ │
│  │  │  DietPi Radio Image      │ │ │
│  │  │  - Mopidy :6680          │ │ │
│  │  │  - BT Manager :8080      │ │ │
│  │  │  - SSH :22               │ │ │
│  │  └──────────────────────────┘ │ │
│  │                                │ │
│  │  Port Forwarding:              │ │
│  │  Host:6680 → VM:6680          │ │
│  │  Host:8080 → VM:8080          │ │
│  │  Host:2222 → VM:22            │ │
│  └────────────────────────────────┘ │
└──────────────────────────────────────┘
```

### 5.3 QEMU Bundle Contents

Each release will include:

**For Linux/macOS:**
```
raspi-radio-qemu-linux-v1.0.0.tar.gz
├── start-qemu.sh              # Launch script
├── kernel-qemu                # ARM kernel for QEMU
├── versatile-pb.dtb           # Device tree blob
├── README.md                  # Quick start guide
└── config/
    └── qemu-config.txt        # QEMU parameters
```

**For Windows:**
```
raspi-radio-qemu-windows-v1.0.0.zip
├── start-qemu.bat             # Launch script
├── qemu/                      # QEMU binaries (portable)
├── kernel-qemu                # ARM kernel
├── versatile-pb.dtb           # Device tree blob
└── README.txt                 # Quick start guide
```

### 5.4 QEMU Start Scripts

**Linux/macOS: `start-qemu.sh`**
```bash
#!/bin/bash

# Download image if not present
IMAGE_URL="https://github.com/user/repo/releases/download/v1.0.0/raspi-radio-armv8-v1.0.0.img.xz"
IMAGE_FILE="raspi-radio.img"

if [ ! -f "$IMAGE_FILE" ]; then
    echo "Downloading image..."
    wget "$IMAGE_URL"
    unxz raspi-radio-armv8-v1.0.0.img.xz
    mv raspi-radio-armv8-v1.0.0.img "$IMAGE_FILE"
fi

# Resize image for QEMU (add space for data)
qemu-img resize "$IMAGE_FILE" +2G

# Launch QEMU
qemu-system-aarch64 \
    -machine virt \
    -cpu cortex-a72 \
    -m 2048 \
    -kernel kernel-qemu \
    -append "root=/dev/vda2 rootfstype=ext4 rw console=ttyAMA0" \
    -drive file="$IMAGE_FILE",if=none,format=raw,id=hd \
    -device virtio-blk-device,drive=hd \
    -netdev user,id=net0,hostfwd=tcp::6680-:6680,hostfwd=tcp::8080-:8080,hostfwd=tcp::2222-:22 \
    -device virtio-net-device,netdev=net0 \
    -nographic \
    -serial mon:stdio

echo ""
echo "================================"
echo "Radio Interface: http://localhost:6680"
echo "Bluetooth Manager: http://localhost:8080"
echo "SSH Access: ssh -p 2222 root@localhost"
echo "Default password: raspberry"
echo "================================"
```

**Windows: `start-qemu.bat`**
```batch
@echo off
setlocal

set IMAGE_URL=https://github.com/user/repo/releases/download/v1.0.0/raspi-radio-armv8-v1.0.0.img.xz
set IMAGE_FILE=raspi-radio.img

if not exist "%IMAGE_FILE%" (
    echo Downloading image...
    curl -L -o raspi-radio.img.xz "%IMAGE_URL%"
    7z x raspi-radio.img.xz
    del raspi-radio.img.xz
)

echo Resizing image...
qemu\qemu-img.exe resize "%IMAGE_FILE%" +2G

echo Starting QEMU...
qemu\qemu-system-aarch64.exe ^
    -machine virt ^
    -cpu cortex-a72 ^
    -m 2048 ^
    -kernel kernel-qemu ^
    -append "root=/dev/vda2 rootfstype=ext4 rw console=ttyAMA0" ^
    -drive file=%IMAGE_FILE%,if=none,format=raw,id=hd ^
    -device virtio-blk-device,drive=hd ^
    -netdev user,id=net0,hostfwd=tcp::6680-:6680,hostfwd=tcp::8080-:8080,hostfwd=tcp::2222-:22 ^
    -device virtio-net-device,netdev=net0 ^
    -serial mon:stdio

echo.
echo ================================
echo Radio Interface: http://localhost:6680
echo Bluetooth Manager: http://localhost:8080  
echo SSH Access: ssh -p 2222 root@localhost
echo Default password: raspberry
echo ================================
pause
```

### 5.5 QEMU Bundle Build Pipeline

**GitHub Actions Workflow: `.github/workflows/build-qemu-bundle.yml`**

```yaml
name: Build QEMU Bundle

on:
  push:
    tags:
      - 'v*.*.*'
  workflow_dispatch:

jobs:
  build-qemu-bundle:
    runs-on: ubuntu-latest
    
    steps:
      - uses: actions/checkout@v4
      
      - name: Install dependencies
        run: |
          sudo apt-get update
          sudo apt-get install -y qemu-system-arm qemu-utils wget
      
      - name: Download QEMU kernel
        run: |
          mkdir -p qemu-bundle/linux qemu-bundle/macos
          
          # Download pre-built ARM64 kernel for QEMU
          wget https://github.com/dhruvvyas90/qemu-rpi-kernel/raw/master/kernel-qemu-5.10.63-bullseye
          mv kernel-qemu-5.10.63-bullseye qemu-bundle/linux/kernel-qemu
          cp qemu-bundle/linux/kernel-qemu qemu-bundle/macos/
          
          # Download device tree blob
          wget https://github.com/dhruvvyas90/qemu-rpi-kernel/raw/master/versatile-pb.dtb
          cp versatile-pb.dtb qemu-bundle/linux/
          cp versatile-pb.dtb qemu-bundle/macos/
      
      - name: Create start scripts
        run: |
          # Linux/macOS script
          cat > qemu-bundle/linux/start-qemu.sh << 'EOF'
#!/bin/bash
IMAGE_URL="https://github.com/${{ github.repository }}/releases/download/${{ github.ref_name }}/raspi-radio-armv8-${{ github.ref_name }}.img.xz"
IMAGE_FILE="raspi-radio.img"

if [ ! -f "$IMAGE_FILE" ]; then
    echo "Downloading image..."
    wget "$IMAGE_URL"
    unxz raspi-radio-armv8-${{ github.ref_name }}.img.xz
    mv raspi-radio-armv8-${{ github.ref_name }}.img "$IMAGE_FILE"
fi

qemu-img resize "$IMAGE_FILE" +2G

qemu-system-aarch64 \
    -machine virt \
    -cpu cortex-a72 \
    -m 2048 \
    -kernel kernel-qemu \
    -append "root=/dev/vda2 rootfstype=ext4 rw console=ttyAMA0" \
    -drive file="$IMAGE_FILE",if=none,format=raw,id=hd \
    -device virtio-blk-device,drive=hd \
    -netdev user,id=net0,hostfwd=tcp::6680-:6680,hostfwd=tcp::8080-:8080,hostfwd=tcp::2222-:22 \
    -device virtio-net-device,netdev=net0 \
    -nographic \
    -serial mon:stdio

echo ""
echo "================================"
echo "Radio: http://localhost:6680"
echo "Bluetooth: http://localhost:8080"
echo "SSH: ssh -p 2222 root@localhost"
echo "Password: raspberry"
echo "================================"
EOF
          chmod +x qemu-bundle/linux/start-qemu.sh
          cp qemu-bundle/linux/start-qemu.sh qemu-bundle/macos/
      
      - name: Create README
        run: |
          cat > qemu-bundle/linux/README.md << 'EOF'
# Raspberry Pi Internet Radio - QEMU Emulator

## Requirements
- QEMU installed (`sudo apt install qemu-system-arm` on Linux)
- 4GB free disk space
- Internet connection (first run)

## Quick Start

1. Run the start script:
   ```bash
   ./start-qemu.sh
   ```

2. Wait for boot (30-60 seconds)

3. Access web interfaces:
   - Radio: http://localhost:6680
   - Bluetooth Manager: http://localhost:8080

4. SSH access (optional):
   ```bash
   ssh -p 2222 root@localhost
   # Password: raspberry
   ```

## Notes
- First boot downloads the image (~180MB)
- Bluetooth audio won't work in QEMU (no real hardware)
- Use for testing web interfaces and radio playback
- Press Ctrl+A then X to exit QEMU

## Troubleshooting
- **Port already in use**: Close other applications using ports 6680, 8080, or 2222
- **QEMU not found**: Install with `sudo apt install qemu-system-arm`
- **Download fails**: Check internet connection and GitHub release page
EOF
          cp qemu-bundle/linux/README.md qemu-bundle/macos/
      
      - name: Download Windows QEMU binaries
        run: |
          mkdir -p qemu-bundle/windows/qemu
          
          # Download portable QEMU for Windows
          wget https://qemu.weilnetz.de/w64/2024/qemu-w64-setup-20241014.exe
          
          # Extract QEMU (simplified - in reality would use proper extraction)
          # For production, use pre-packaged QEMU binaries
          echo "Note: Windows bundle requires manual QEMU binary packaging"
      
      - name: Create Windows batch script
        run: |
          cat > qemu-bundle/windows/start-qemu.bat << 'EOF'
@echo off
set IMAGE_URL=https://github.com/${{ github.repository }}/releases/download/${{ github.ref_name }}/raspi-radio-armv8-${{ github.ref_name }}.img.xz
set IMAGE_FILE=raspi-radio.img

if not exist "%IMAGE_FILE%" (
    echo Downloading image...
    curl -L -o raspi-radio.img.xz "%IMAGE_URL%"
    7z x raspi-radio.img.xz
    del raspi-radio.img.xz
)

qemu\qemu-img.exe resize "%IMAGE_FILE%" +2G

qemu\qemu-system-aarch64.exe ^
    -machine virt ^
    -cpu cortex-a72 ^
    -m 2048 ^
    -kernel kernel-qemu ^
    -append "root=/dev/vda2 rootfstype=ext4 rw console=ttyAMA0" ^
    -drive file=%IMAGE_FILE%,if=none,format=raw,id=hd ^
    -device virtio-blk-device,drive=hd ^
    -netdev user,id=net0,hostfwd=tcp::6680-:6680,hostfwd=tcp::8080-:8080,hostfwd=tcp::2222-:22 ^
    -device virtio-net-device,netdev=net0 ^
    -serial mon:stdio

echo.
echo ================================
echo Radio: http://localhost:6680
echo Bluetooth: http://localhost:8080
echo SSH: ssh -p 2222 root@localhost
echo Password: raspberry
echo ================================
pause
EOF
      
      - name: Package bundles
        run: |
          cd qemu-bundle
          
          # Linux bundle
          tar czf raspi-radio-qemu-linux-${{ github.ref_name }}.tar.gz linux/
          
          # macOS bundle (same as Linux)
          tar czf raspi-radio-qemu-macos-${{ github.ref_name }}.tar.gz macos/
          
          # Windows bundle
          cd windows && zip -r ../raspi-radio-qemu-windows-${{ github.ref_name }}.zip . && cd ..
      
      - name: Upload artifacts
        uses: actions/upload-artifact@v3
        with:
          name: qemu-bundles
          path: |
            qemu-bundle/*.tar.gz
            qemu-bundle/*.zip
  
  add-to-release:
    needs: build-qemu-bundle
    runs-on: ubuntu-latest
    if: startsWith(github.ref, 'refs/tags/')
    
    steps:
      - name: Download artifacts
        uses: actions/download-artifact@v3
        with:
          name: qemu-bundles
      
      - name: Add to GitHub Release
        uses: softprops/action-gh-release@v1
        with:
          files: |
            raspi-radio-qemu-linux-*.tar.gz
            raspi-radio-qemu-macos-*.tar.gz
            raspi-radio-qemu-windows-*.zip
          append_body: true
          body: |
            
            ---
            
            ## 🖥️ QEMU Emulation (Test Without Hardware)
            
            **Don't have a Raspberry Pi? Test in QEMU!**
            
            Download the QEMU bundle for your operating system:
            
            | Platform | Download | Size |
            |----------|----------|------|
            | 🐧 Linux | [raspi-radio-qemu-linux-${{ github.ref_name }}.tar.gz](link) | ~50 MB |
            | 🍎 macOS | [raspi-radio-qemu-macos-${{ github.ref_name }}.tar.gz](link) | ~50 MB |
            | 🪟 Windows | [raspi-radio-qemu-windows-${{ github.ref_name }}.zip](link) | ~120 MB |
            
            ### Quick Start:
            ```bash
            # Linux/macOS
            tar xzf raspi-radio-qemu-linux-*.tar.gz
            cd linux
            ./start-qemu.sh
            
            # Windows
            # Extract ZIP, double-click start-qemu.bat
            ```
            
            ### Access:
            - Radio Interface: http://localhost:6680
            - Bluetooth Manager: http://localhost:8080
            - SSH: `ssh -p 2222 root@localhost` (password: raspberry)
            
            ### Notes:
            - ⚠️ Bluetooth audio won't work (no real hardware in QEMU)
            - ✅ Perfect for testing web interfaces
            - ✅ Test radio station browsing and playback
            - ✅ No SD card flashing required
        env:
          GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
```

### 5.6 QEMU Testing Workflow

**Developer Workflow:**
1. Download QEMU bundle from GitHub releases
2. Extract and run start script
3. Wait 30-60 seconds for boot
4. Access web interfaces in browser
5. Test radio functionality
6. Test UI changes
7. SSH in for debugging if needed

**CI/CD Testing:**
```yaml
# .github/workflows/test-in-qemu.yml
name: Test in QEMU

on: [pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    
    steps:
      - name: Start QEMU instance
        run: |
          # Download and boot image in QEMU
          # Run automated tests
          # Check web interfaces respond
          # Validate services running
```

### 5.7 QEMU Limitations

**What Works:**
- ✅ Web interface testing
- ✅ Radio station playback (to host audio)
- ✅ UI development
- ✅ Network functionality
- ✅ SSH access
- ✅ Software testing

**What Doesn't Work:**
- ❌ Bluetooth audio (no real Bluetooth hardware)
- ❌ GPIO access
- ❌ Hardware-specific features
- ❌ Performance testing (emulated CPU slower)

**Workarounds:**
- Bluetooth UI can be tested, just can't pair real devices
- Use "mock" devices for UI testing
- SSH into QEMU and use bluetoothctl to simulate pairing

---

## 6. Hardware Support

### 6.1 Supported Models

| Model | Architecture | RAM | Status | Priority |
|-------|--------------|-----|--------|----------|
| Pi Zero 2 W | ARMv8 | 512MB | ✅ Supported | High |
| Pi 3 B/B+/A+ | ARMv8 | 1GB | ✅ Supported | High |
| Pi 4 B | ARMv8 | 2-8GB | ✅ Supported | High |
| Pi 5 | ARMv8 | 4-8GB | ✅ Supported | Medium |
| Pi 2 B | ARMv7 | 1GB | ✅ Supported | Medium |
| Pi Zero W | ARMv6 | 512MB | ✅ Supported | Low |
| Pi 1 B/B+ | ARMv6 | 256-512MB | ✅ Supported | Low |

### 6.2 Minimum Requirements

**Physical Hardware:**
- Raspberry Pi (any model above)
- MicroSD card (8GB minimum, 16GB recommended)
- 5V power supply (appropriate for model)
- Bluetooth speaker
- Internet connection (WiFi or Ethernet)

**QEMU Emulation:**
- 4GB RAM on host machine
- 10GB free disk space
- QEMU 5.0+ installed
- Internet connection

---

## 7. User Stories

### 7.1 End User Stories

**US-1: Flash and Play**
- As a user, I want to flash an SD card and boot my Pi so that I can start listening to radio within 2 minutes
- Acceptance: Boot to working radio in under 120 seconds

**US-2: Browse Stations**
- As a user, I want to browse TuneIn stations by genre and location so that I can find music I like
- Acceptance: Can navigate TuneIn categories in web UI

**US-3: Control via Web**
- As a user, I want to control playback from my phone's browser so that I don't need to install an app
- Acceptance: Responsive UI works on mobile browsers

**US-4: Pair Bluetooth Speaker**
- As a user, I want to pair my Bluetooth speaker via web interface so that I don't need to use SSH
- Acceptance: Can scan, pair, and connect speakers without command line

**US-5: Auto-Reconnect**
- As a user, I want my Bluetooth speaker to reconnect automatically when I turn it on so that I don't have to manually reconnect
- Acceptance: Speaker reconnects within 30 seconds of power-on

### 7.2 Developer Stories

**US-6: Test Without Hardware**
- As a developer, I want to test the system in QEMU so that I don't need to buy a Raspberry Pi
- Acceptance: Can download and run QEMU bundle in under 5 minutes

**US-7: Contribute Code**
- As a developer, I want to fork the repo and submit PRs so that I can add features
- Acceptance: Clear contribution guidelines, CI/CD validates PRs

**US-8: Custom Builds**
- As a developer, I want to modify the image build so that I can add my own software
- Acceptance: Documented build process, modular scripts

---

## 8. System Requirements

### 8.1 Runtime Requirements

**For Raspberry Pi:**
- DietPi OS (provided in image)
- 512MB RAM minimum
- 4GB storage minimum
- Internet connection
- Bluetooth 4.0+ (for audio)

**For QEMU:**
- Host OS: Linux, macOS 10.14+, Windows 10+
- Host RAM: 4GB minimum
- Host Storage: 10GB free
- QEMU 5.0+
- Internet connection

### 8.2 Build Requirements

**For GitHub Actions (automatic):**
- Nothing - builds automatically on tag push

**For Local Builds:**
- Ubuntu 20.04+ or Debian 11+
- 20GB free disk space
- sudo access
- Packages: qemu-user-static, kpartx, p7zip

---

## 9. Build Pipeline

### 9.1 GitHub Actions Workflows

**Primary Workflows:**
1. `build-release.yml` - Build images for all architectures
2. `build-qemu-bundle.yml` - Package QEMU emulator bundles
3. `build-dev.yml` - PR validation and testing
4. `test-scripts.yml` - Shell script linting

### 9.2 Build Matrix

```yaml
matrix:
  include:
    - arch: armv8
      models: "Pi Zero 2 W, Pi 3, Pi 4, Pi 5"
      base: DietPi_RPi-ARMv8-Bookworm.7z
      
    - arch: armv7
      models: "Pi 2"
      base: DietPi_RPi-ARMv7-Bookworm.7z
      
    - arch: armv6
      models: "Pi Zero W, Pi 1"
      base: DietPi_RPi-ARMv6-Bookworm.7z
```

### 9.3 Release Process

**Trigger:**
```bash
git tag -a v1.0.0 -m "Release version 1.0.0"
git push origin v1.0.0
```

**Automated Steps:**
1. Download DietPi base images (cached)
2. Build custom images (parallel, 3 architectures)
3. Compress with xz -9
4. Generate SHA256 checksums
5. Build QEMU bundles (3 platforms)
6. Create GitHub Release
7. Upload all assets
8. Generate release notes

**Total Time:** ~30-40 minutes

### 9.4 Release Assets

```
v1.0.0 Release Assets:
├── raspi-radio-armv8-v1.0.0.img.xz (180 MB)
├── raspi-radio-armv8-v1.0.0.img.xz.sha256
├── raspi-radio-armv7-v1.0.0.img.xz (170 MB)
├── raspi-radio-armv7-v1.0.0.img.xz.sha256
├── raspi-radio-armv6-v1.0.0.img.xz (160 MB)
├── raspi-radio-armv6-v1.0.0.img.xz.sha256
├── raspi-radio-qemu-linux-v1.0.0.tar.gz (50 MB)
├── raspi-radio-qemu-macos-v1.0.0.tar.gz (50 MB)
├── raspi-radio-qemu-windows-v1.0.0.zip (120 MB)
└── Source code (zip)
└── Source code (tar.gz)
```

---

## 10. Web Interfaces

### 10.1 Radio Interface (Mopidy Iris)

**URL:** `http://raspberrypi.local:6680`

**Features:**
- Browse TuneIn stations
- Search functionality
- Playback controls
- Volume control
- Queue management
- Favorites/playlists
- Mobile-responsive

**Technology:**
- Backend: Mopidy (Python)
- Frontend: Iris (React-based)
- Protocol: HTTP + WebSocket

### 10.2 Bluetooth Manager Interface

**URL:** `http://raspberrypi.local:8080`

**Pages:**

**Main Dashboard:**
- List of paired devices
- Connection status indicators
- Connect/disconnect buttons
- Scan button
- Real-time status updates

**Device Card Components:**
- Device name
- MAC address
- Connection status (connected/disconnected)
- Action buttons (connect/disconnect/remove)

**Technology:**
- Backend: FastAPI (Python) + Uvicorn
- Frontend: Alpine.js + Tailwind CSS
- API: REST + async

### 10.3 UI/UX Design Principles

**Consistency:**
- Tailwind utility classes
- Mobile-first responsive design
- Consistent color scheme
- Clear typography hierarchy

**Simplicity:**
- Minimal clicks to perform actions
- Clear labels and feedback
- No technical jargon
- Progressive disclosure

**Performance:**
- Fast load times
- Optimistic UI updates
- Real-time status without polling
- Cached assets

---

## 11. API Specifications

### 11.1 Bluetooth Manager REST API

**Base URL:** `http://raspberrypi.local:8080/api`

**Endpoints:**

```
GET /devices
Description: List all paired Bluetooth devices
Response: [
  {
    "mac": "AA:BB:CC:DD:EE:FF",
    "name": "JBL Speaker",
    "connected": true,
    "paired": true
  }
]

GET /devices/scan
Description: Start scanning for new devices
Response: {
  "status": "scanning",
  "message": "Scanning for 15 seconds..."
}

GET /devices/available
Description: List devices found during scan
Response: [Device array]

POST /devices/connect
Body: {"mac": "AA:BB:CC:DD:EE:FF"}
Response: {
  "status": "connected",
  "message": "Connected to AA:BB:CC:DD:EE:FF"
}

POST /devices/disconnect
Body: {"mac": "AA:BB:CC:DD:EE:FF"}
Response: {
  "status": "disconnected",
  "message": "Disconnected from AA:BB:CC:DD:EE:FF"
}

POST /devices/pair
Body: {"mac": "AA:BB:CC:DD:EE:FF"}
Response: {
  "status": "paired",
  "message": "Paired and connected to AA:BB:CC:DD:EE:FF"
}

POST /devices/remove
Body: {"mac": "AA:BB:CC:DD:EE:FF"}
Response: {
  "status": "removed",
  "message": "Removed AA:BB:CC:DD:EE:FF"
}

GET /status
Description: Get Bluetooth adapter status
Response: {
  "powered": true,
  "discoverable": false,
  "pairable": true
}
```

### 11.2 Mopidy API

**Base URL:** `http://raspberrypi.local:6680/mopidy/rpc`

Uses JSON-RPC 2.0 protocol. Pre-configured, no changes needed.

---

## 12. Security Considerations

### 12.1 Authentication

**MVP (v1.0):**
- No authentication required
- Intended for home network use only
- **Warning in documentation:** Not for public networks

**Future (v1.1+):**
- Optional HTTP Basic Auth
- Password protection for web interfaces
- JWT tokens for API access

### 12.2 Network Security

**Default Configuration:**
- Services bind to 0.0.0.0 (all interfaces)
- No firewall rules (user's network provides security)
- SSH enabled with default password

**Recommendations:**
- Change default password on first boot
- Use on private WiFi networks only
- Consider VPN for remote access
- Update regularly

### 12.3 Data Privacy

**No Data Collection:**
- No analytics
- No telemetry
- No user tracking
- TuneIn usage governed by their ToS

---

## 13. Testing Strategy

### 13.1 Automated Testing

**GitHub Actions CI:**
```
On Pull Request:
├── Lint shell scripts (shellcheck)
├── Validate Python code (flake8, black)
├── Test build process (dry-run)
└── Validate configuration files

On Tag Push:
├── Full image builds (3 architectures)
├── QEMU bundle creation
├── Checksum validation
└── Release creation
```

### 13.2 Manual Testing

**Pre-Release Checklist:**
- [ ] Flash image to real Pi
- [ ] Boot and verify timing (<120s)
- [ ] Access web interfaces
- [ ] Pair Bluetooth speaker
- [ ] Play TuneIn station
- [ ] Test auto-reconnect
- [ ] Test in QEMU
- [ ] Verify all release assets

### 13.3 Community Testing

**Beta Program:**
- Pre-release builds for testers
- GitHub Discussions for feedback
- Issue templates for bug reports
- Testing guidelines in docs

---

## 14. Deployment & Distribution

### 14.1 Distribution Channels

**Primary:**
- GitHub Releases (free, unlimited)
- Direct download links
- Repository: `github.com/cheeky-radio/cheeky`

**Secondary (Future):**
- Docker Hub (container version)
- Pi App Store (if available)

**Release Asset Naming:**
```
Cheeky v1.0.0 Assets:
├── cheeky-armv8-v1.0.0.img.xz (180 MB)
├── cheeky-armv8-v1.0.0.img.xz.sha256
├── cheeky-armv7-v1.0.0.img.xz (170 MB)
├── cheeky-armv7-v1.0.0.img.xz.sha256
├── cheeky-armv6-v1.0.0.img.xz (160 MB)
├── cheeky-armv6-v1.0.0.img.xz.sha256
├── cheeky-qemu-linux-v1.0.0.tar.gz (50 MB)
├── cheeky-qemu-macos-v1.0.0.tar.gz (50 MB)
├── cheeky-qemu-windows-v1.0.0.zip (120 MB)
└── Source code (zip/tar.gz)
```

### 14.2 Documentation Structure

```
Repository:
├── README.md (overview, quick start)
├── docs/
│   ├── INSTALLATION.md (detailed setup)
│   ├── QEMU.md (emulation guide)
│   ├── TROUBLESHOOTING.md (common issues)
│   ├── CONTRIBUTING.md (development guide)
│   ├── API.md (API documentation)
│   └── CHANGELOG.md (version history)
```

### 14.3 User Support

**Channels:**
- GitHub Issues (bug reports)
- GitHub Discussions (Q&A, features)
- README badges (build status, version)
- Inline documentation in code

---

## 15. Success Metrics

### 15.1 Key Performance Indicators (KPIs)

**Adoption:**
- GitHub stars (target: 100 in first month)
- Release downloads (target: 500 in first month)
- Forks (target: 20 in first month)

**Quality:**
- Boot time (<120 seconds)
- Image size (<200MB compressed)
- Build success rate (>95%)
- Issue resolution time (<7 days)

**Engagement:**
- Active contributors (target: 5+)
- Pull requests per month (target: 3+)
- Community discussions (target: 10+)

### 15.2 User Satisfaction

**Metrics:**
- Net Promoter Score (via GitHub Discussions)
- Issue-to-feature ratio (<3:1)
- Documentation clarity (feedback-based)

---

## 16. Roadmap

### 16.1 Version 1.0 (MVP) - Week 1-2

**Core Features:**
- [x] TuneIn integration
- [x] Bluetooth web management
- [x] Multi-architecture builds
- [x] QEMU bundles
- [x] Automated CI/CD
- [x] Basic documentation

**Deliverables:**
- 3 Pi image variants
- 3 QEMU bundles
- GitHub repository with full CI/CD
- Complete documentation

### 16.2 Version 1.1 - Month 2

**Enhancements:**
- [ ] HTTP Basic Auth (optional)
- [ ] Custom station presets
- [ ] Sleep timer
- [ ] Alarm clock functionality
- [ ] WiFi configuration via web
- [ ] Multiple Bluetooth device profiles

### 16.3 Version 1.2 - Month 3

**Advanced Features:**
- [ ] Spotify Connect integration
- [ ] Podcast support (via Mopidy extensions)
- [ ] Multi-room sync (Snapcast)
- [ ] Voice control (Alexa/Google Home)
- [ ] Mobile app (React Native)

### 16.4 Version 2.0 - Month 6

**Major Upgrades:**
- [ ] Docker container version
- [ ] Kubernetes support
- [ ] Home Assistant integration
- [ ] Custom web UI (replace Iris)
- [ ] Advanced audio processing (EQ, etc.)

---

## 17. Open Questions

### 17.1 Technical Decisions

**Q: Should we support 32-bit vs 64-bit?**
- A: Both - use DietPi's architecture-specific images
- ARMv8 models get 64-bit
- ARMv6/v7 get 32-bit

**Q: Audio quality settings?**
- A: Default to high quality (256kbps+)
- Consider adding quality selector in v1.1

**Q: Caching strategy for base images?**
- A: Use GitHub Actions cache
- Cache key based on DietPi version
- Invalidate monthly or on version change

### 17.2 Product Decisions

**Q: Should we support local file playback?**
- A: Not in MVP (TuneIn only)
- Consider for v1.1 based on feedback

**Q: Monetization strategy?**
- A: None - fully open source
- Accept donations via GitHub Sponsors (optional)

**Q: Commercial support?**
- A: Not initially
- Community support only
- Re-evaluate after 1,000 users

### 17.3 Licensing

**Q: What license?**
- A: MIT License (permissive, open source)
- Allows commercial use
- No warranty/liability

---

## 18. Risks & Mitigation

### 18.1 Technical Risks

**Risk: QEMU emulation too slow**
- Mitigation: Document performance expectations
- Workaround: Use lightweight browser, reduce concurrent streams

**Risk: Bluetooth compatibility issues**
- Mitigation: Test with multiple speaker brands
- Workaround: Provide troubleshooting guide

**Risk: DietPi upstream changes break build**
- Mitigation: Pin to specific DietPi version
- Monitor DietPi releases for breaking changes

### 18.2 Product Risks

**Risk: Low adoption**
- Mitigation: Market via Reddit (r/raspberry_pi), HackerNews
- Create demo video
- Write blog post

**Risk: TuneIn API changes**
- Mitigation: Use Mopidy-TuneIn (maintained project)
- Monitor TuneIn ToS
- Have backup stream sources ready

**Risk: Burnout (single maintainer)**
- Mitigation: Document everything
- Make contribution easy
- Recruit co-maintainers early

---

## 19. Success Criteria

### 19.1 Launch Criteria (v1.0)

**Must Have:**
- ✅ Working image for all 3 architectures
- ✅ QEMU bundles for 3 platforms
- ✅ Automated GitHub Actions builds
- ✅ Complete README with quick start
- ✅ Working radio playback
- ✅ Working Bluetooth management
- ✅ Boot time <120 seconds
- ✅ Image size <200MB

**Should Have:**
- ✅ Troubleshooting guide
- ✅ API documentation
- ✅ Contribution guidelines
- ✅ Automated tests

**Nice to Have:**
- Demo video
- Blog post announcement
- Reddit/HN submission

### 19.2 Post-Launch Success (30 days)

**Minimum Viable Success:**
- 50+ GitHub stars
- 200+ downloads
- 5+ GitHub issues filed (showing usage)
- 0 critical bugs

**Target Success:**
- 100+ GitHub stars
- 500+ downloads
- 2+ contributors
- Featured on Pi Weekly newsletter

**Stretch Success:**
- 500+ GitHub stars
- 2000+ downloads
- 10+ contributors
- Front page of Hacker News

---

## 20. Appendix

### 20.1 Glossary

- **DietPi**: Lightweight Debian-based Linux distribution for single-board computers
- **Mopidy**: Extensible music server with web API
- **TuneIn**: Internet radio aggregator with 100,000+ stations
- **BlueZ**: Official Linux Bluetooth protocol stack
- **QEMU**: Open source emulator for running ARM software on x86 machines
- **FastAPI**: Modern Python web framework
- **Tailwind CSS**: Utility-first CSS framework

### 20.2 References

- [DietPi Documentation](https://dietpi.com/docs/)
- [Mopidy Documentation](https://docs.mopidy.com/)
- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [QEMU Documentation](https://www.qemu.org/docs/master/)
- [BlueZ Documentation](http://www.bluez.org/)
- [Raspberry Pi Documentation](https://www.raspberrypi.com/documentation/)

### 20.3 Contact & Links

- **GitHub Repository**: [github.com/username/raspi-internet-radio](https://github.com)
- **Documentation Site**: TBD
- **Discussion Forum**: GitHub Discussions
- **Issue Tracker**: GitHub Issues
- **License**: MIT

---

**Document Version:** 1.0  
**Last Updated:** October 23, 2025  
**Author:** Product Team  
**Status:** Approved for Development

---

## Change Log

| Version | Date | Changes | Author |
|---------|------|---------|--------|
| 1.0 | 2025-10-23 | Initial PRD with QEMU support | Product Team |

