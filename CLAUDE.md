# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Repository Overview

**Cheeky** is a lightweight, zero-setup internet radio system for Raspberry Pi with web-based Bluetooth management and QEMU testing support. The project emphasizes ease of use: users download pre-built images and start listening to 100,000+ radio stations (via TuneIn) within 2 minutes.

### Key Philosophy
- **Zero local compilation**: All builds happen in GitHub Actions
- **Zero configuration**: Flash image, boot, done
- **Zero hardware needed to test**: QEMU bundles for development
- **Playful but professional**: Quality code with personality

## Project Architecture

```
┌─────────────────────────────────────┐
│       User's Browser/Phone          │
│  Port 6680: Radio (Mopidy Iris)     │
│  Port 8080: Bluetooth Manager       │
└─────────────────────────────────────┘
                ↓
    ┌───────────────────────────┐
    │ Mopidy + FastAPI/Uvicorn  │
    │ (Python backends)         │
    └───────────────────────────┘
                ↓
    ┌───────────────────────────┐
    │ PulseAudio + BlueZ        │
    │ (Audio & Bluetooth)       │
    └───────────────────────────┘
                ↓
    ┌───────────────────────────┐
    │ DietPi Linux (~180MB)     │
    │ (Optimized Debian base)   │
    └───────────────────────────┘
                ↓
    ┌───────────────────────────┐
    │ Raspberry Pi OR QEMU      │
    └───────────────────────────┘
```

**Tech Stack:**
- **Base OS**: DietPi (optimized Debian)
- **Radio**: Mopidy + TuneIn extension + Iris web UI
- **Bluetooth Manager**: FastAPI + Uvicorn + Alpine.js + Tailwind CSS
- **Build System**: GitHub Actions (fully automated)
- **License**: MIT

## Repository Structure

```
cheeky/
├── .github/workflows/
│   └── build-release.yml              # Main CI/CD pipeline (see below)
├── config/
│   ├── mopidy.conf                    # Mopidy music server config
│   ├── dietpi.txt                     # DietPi first-boot settings
│   ├── Automation_Custom_Script.sh    # Post-boot customization script
│   ├── bluetooth-reconnect.sh         # BlueZ auto-reconnect logic
│   └── bluetooth-web-manager/         # FastAPI Bluetooth management
│       ├── main.py                    # REST API endpoints
│       ├── requirements.txt
│       ├── templates/index.html       # Web UI (Tailwind)
│       └── static/app.js              # Frontend logic (Alpine.js)
├── scripts/
│   ├── build.sh                       # Image customization script
│   └── versions.txt                   # DietPi version pinning
├── qemu/
│   ├── linux/
│   │   ├── start-qemu.sh.template     # Linux/macOS launcher
│   │   └── README.md
│   ├── macos/
│   │   ├── start-qemu.sh.template
│   │   └── README.md
│   └── windows/
│       ├── start-qemu.bat.template    # Windows launcher
│       └── README.txt
├── docs/
│   ├── INSTALLATION.md                # User installation guide
│   ├── WIFI-SETUP.md                  # Headless WiFi configuration
│   ├── QEMU.md                        # QEMU testing guide
│   ├── TROUBLESHOOTING.md             # Common issues & fixes
│   ├── API.md                         # FastAPI endpoint reference
│   └── CUSTOMIZATION.md               # Building on Cheeky
├── README.md                          # User-facing overview
├── CONTRIBUTING.md                    # Contribution guidelines
├── LICENSE                            # MIT license
├── PRD-RaspberryPi-Internet-Radio.md  # Complete product spec
├── CHEEKY-Brand-Guide.md              # Branding & voice guidelines
└── SUMMARY-COMPLETE-PACKAGE.md        # High-level overview

# Key files not in repo yet but documented:
# - .github/workflows/build-release.yml (see GITHUB-ACTIONS-COMPLETE.md)
```

## Build System & Automation

### How Builds Work

The project uses **GitHub Actions for complete automation**:

```
Developer: git tag -a v1.0.0 && git push origin v1.0.0
                              ↓
          GitHub Actions Triggered
                              ↓
    ┌─────────────────────────────────────┐
    │ Job 1: Build Pi Images (parallel)   │
    │ - ARMv8 (Pi 3/4/5)                  │
    │ - ARMv7 (Pi 2)                      │
    │ - ARMv6 (Pi Zero/1)                 │
    │ Each: Download DietPi → Customize   │
    │       → Compress (xz -9) → Checksum │
    └─────────────────────────────────────┘
                              ↓
    ┌─────────────────────────────────────┐
    │ Job 2: Build QEMU Bundles           │
    │ - Download QEMU kernel              │
    │ - Create launch scripts             │
    │ - Package for Linux/macOS/Windows   │
    └─────────────────────────────────────┘
                              ↓
    ┌─────────────────────────────────────┐
    │ Job 3: Create GitHub Release        │
    │ - Collect all artifacts             │
    │ - Generate release notes            │
    │ - Publish for users                 │
    └─────────────────────────────────────┘
                              ↓
         Users download ready-to-use files
```

**Total time**: ~30-40 minutes for complete build.

### Build Artifacts

Each release generates:

**Pi Images** (3 variants):
- `cheeky-armv8-v1.0.0.img.xz` (~180 MB) - Pi Zero 2 W, 3, 4, 5
- `cheeky-armv7-v1.0.0.img.xz` (~170 MB) - Pi 2
- `cheeky-armv6-v1.0.0.img.xz` (~160 MB) - Pi Zero W, 1

**QEMU Bundles** (3 platforms):
- `cheeky-qemu-linux-v1.0.0.tar.gz` (~50 MB)
- `cheeky-qemu-macos-v1.0.0.tar.gz` (~50 MB)
- `cheeky-qemu-windows-v1.0.0.zip` (~120 MB)

**Checksums** (for integrity verification):
- SHA256 for all images
- MD5 for all images

### Hardware Support Matrix

| Model | Architecture | RAM | Status |
|-------|--------------|-----|--------|
| Pi Zero 2 W | ARMv8 | 512MB | ✅ Supported |
| Pi 3/3A+/3B+ | ARMv8 | 1GB | ✅ Supported |
| Pi 4 | ARMv8 | 2-8GB | ✅ Supported |
| Pi 5 | ARMv8 | 4-8GB | ✅ Supported |
| Pi 2 | ARMv7 | 1GB | ✅ Supported |
| Pi Zero W | ARMv6 | 512MB | ✅ Supported |
| Pi 1 B/B+ | ARMv6 | 256-512MB | ✅ Supported |

## Key Features & Implementation

### 1. Internet Radio (Port 6680)

**Frontend**: Mopidy Iris (pre-installed, React-based)
**Backend**: Mopidy music server + TuneIn extension
**Features**:
- Browse/search 100,000+ TuneIn stations
- Play/pause/volume control
- Favorites and playlists
- Mobile-responsive web UI

**Config**: `config/mopidy.conf` - Pre-configured for TuneIn (no API key needed)

### 2. Bluetooth Manager (Port 8080)

**Stack**: FastAPI (backend) + Alpine.js + Tailwind CSS (frontend)
**Location**: `config/bluetooth-web-manager/`

**Endpoints** (REST API):
- `GET /api/devices` - List paired devices
- `POST /api/devices/scan` - Scan for new devices
- `POST /api/devices/pair` - Pair new speaker
- `POST /api/devices/connect` - Connect to speaker
- `POST /api/devices/disconnect` - Disconnect from speaker
- `POST /api/devices/remove` - Remove paired device

**Features**:
- Real-time device status
- No SSH required (web-only management)
- Auto-reconnect on reboot via `config/bluetooth-reconnect.sh`

### 3. QEMU Testing (Development Feature)

Bundles in `qemu/` directory allow developers to test without hardware.

**What Works**:
- ✅ Web interface testing
- ✅ Radio browsing and playback (audio to host)
- ✅ UI development and debugging
- ✅ Network functionality
- ✅ SSH access for debugging

**What Doesn't Work**:
- ❌ Real Bluetooth audio (no hardware in VM)
- ❌ GPIO access
- ❌ Hardware-specific features

**Launch Methods**:
- Linux/macOS: `./start-qemu.sh`
- Windows: `start-qemu.bat`
- Auto-downloads Pi image on first run
- Port forwarding: 6680→6680, 8080→8080, 2222→SSH

### 4. Headless WiFi Configuration

Two methods for users:

**Method A: Before First Boot (Easiest)**
- After flashing image, edit `/boot/dietpi-wifi.txt`
- Add WiFi credentials
- Boot automatically connects

**Method B: Raspberry Pi Imager**
- Use built-in WiFi configuration in Advanced Options
- Flash with credentials pre-configured

**Config File**: `config/dietpi.txt` - Sets DietPi behavior on first boot

## Development Workflow

### Making Changes

1. **Edit configuration files** in `config/` directory
2. **Modify Bluetooth manager** in `config/bluetooth-web-manager/`
3. **Update build script** in `scripts/build.sh`
4. **Test in QEMU**:
   ```bash
   cd qemu/linux
   ./start-qemu.sh
   # Visit http://localhost:6680 and http://localhost:8080
   ```
5. **Commit and tag** when ready to release

### Testing Locally (QEMU)

```bash
# Extract QEMU bundle
tar xzf cheeky-qemu-linux-v1.0.0.tar.gz
cd linux

# First run: Downloads the Pi image (~180MB)
./start-qemu.sh

# Subsequent runs: Starts existing image immediately
# Ctrl+A then X to exit QEMU
```

### Code Organization Rules

**Backend Code** (Python):
- Location: `config/bluetooth-web-manager/`
- Framework: FastAPI
- Dependencies: Listed in `requirements.txt`
- Entry point: `main.py` creates FastAPI app with REST endpoints

**Frontend Code** (Web):
- HTML: `config/bluetooth-web-manager/templates/index.html` (Tailwind CSS)
- JavaScript: `config/bluetooth-web-manager/static/app.js` (Alpine.js)
- No Node build step required (Alpine.js is lightweight)

**Configuration**:
- Mopidy: `config/mopidy.conf` (INI format)
- DietPi: `config/dietpi.txt` (KEY=VALUE format)
- Bluetooth: `config/bluetooth-reconnect.sh` (Bash script)

**Scripts**:
- Build: `scripts/build.sh` - Customizes DietPi image
- Automation: `config/Automation_Custom_Script.sh` - Runs on first boot

## Customization & Extension Points

### Adding Features

**For Bluetooth Manager**:
1. Add FastAPI endpoint in `config/bluetooth-web-manager/main.py`
2. Add UI component in `templates/index.html`
3. Add frontend logic in `static/app.js`
4. Test in QEMU

**For Radio/Audio**:
1. Modify `config/mopidy.conf` to add extensions
2. Update `scripts/build.sh` to install dependencies
3. Test in QEMU
4. Document in `docs/CUSTOMIZATION.md`

**For First-Boot Behavior**:
1. Edit `config/dietpi.txt` for DietPi settings
2. Edit `config/Automation_Custom_Script.sh` for custom setup
3. These run automatically on first boot

### DietPi Automation

The `config/Automation_Custom_Script.sh` script runs on first boot and:
- Installs required packages (Mopidy, FastAPI, etc.)
- Starts services (Mopidy on 6680, FastAPI on 8080)
- Configures Bluetooth auto-reconnect
- Sets up any custom software

Edit this file to add first-boot customizations.

## Release Process

### Creating a Release

```bash
# Make your changes
git add config/ scripts/ docs/

# Commit
git commit -m "Update: Add new feature"
git push origin master

# Create release tag (semantic versioning)
git tag -a v1.1.0 -m "Release v1.1.0: Add new feature"
git push origin v1.1.0

# GitHub Actions automatically:
# 1. Builds all 3 Pi images
# 2. Builds all 3 QEMU bundles
# 3. Generates checksums
# 4. Creates GitHub Release with all assets
# 5. Publishes release notes
```

**Total time**: ~30-40 minutes

### Version Numbering

Use semantic versioning: `v1.0.0`, `v1.1.0`, `v2.0.0`

- **Major** (v2.0.0): Breaking changes or major features
- **Minor** (v1.1.0): New features (backward compatible)
- **Patch** (v1.0.1): Bug fixes only

## Testing Strategy

### Automated (GitHub Actions)
- Runs on every PR
- Validates shell scripts (`shellcheck`)
- Validates build process (dry-run)
- Checks configuration files

### Manual Testing Checklist (Before Release)

```
Hardware Test:
- [ ] Flash ARMv8 image to Pi 4/5
- [ ] Flash ARMv7 image to Pi 2
- [ ] Flash ARMv6 image to Pi Zero W
- [ ] Boot time under 120 seconds
- [ ] Web interfaces load (ports 6680, 8080)
- [ ] Play a TuneIn station
- [ ] Pair Bluetooth speaker
- [ ] Auto-reconnect on reboot

QEMU Test:
- [ ] Extract QEMU bundle on Linux
- [ ] Extract QEMU bundle on macOS
- [ ] Extract QEMU bundle on Windows
- [ ] Run start scripts on all platforms
- [ ] Access web interfaces
- [ ] Browse radio stations (playback to host)

Release:
- [ ] All checksums match
- [ ] Download sizes within expected range
- [ ] Release notes clear and complete
- [ ] No broken links in documentation
```

## Common Development Tasks

### Add a Python Dependency

1. Update `config/bluetooth-web-manager/requirements.txt`
2. Update `config/Automation_Custom_Script.sh` to install from pip
3. Test in QEMU
4. Tag release

### Modify Mopidy Configuration

1. Edit `config/mopidy.conf`
2. Add any extensions needed
3. Update `config/Automation_Custom_Script.sh` to install them
4. Test in QEMU

### Change Boot Behavior

1. Edit `config/dietpi.txt` for DietPi settings
2. Edit `config/Automation_Custom_Script.sh` for custom behavior
3. Re-build and test in QEMU

### Update Documentation

Docs are in `docs/` directory:
- `INSTALLATION.md` - User setup guide
- `WIFI-SETUP.md` - WiFi configuration methods
- `QEMU.md` - QEMU testing guide
- `TROUBLESHOOTING.md` - Common issues
- `API.md` - FastAPI endpoint reference
- `CUSTOMIZATION.md` - Building on Cheeky

## Important Patterns & Conventions

### Service Management

All services are configured to auto-start on boot:

- **Mopidy** (radio backend): Runs on port 6680
  - Config: `config/mopidy.conf`
  - Start: Automatic via systemd (set in Automation_Custom_Script.sh)

- **FastAPI** (Bluetooth manager): Runs on port 8080
  - Code: `config/bluetooth-web-manager/main.py`
  - Start: Automatic via systemd (set in Automation_Custom_Script.sh)

- **BlueZ** (Bluetooth stack): System daemon
  - Auto-reconnect: `config/bluetooth-reconnect.sh`
  - Runs on boot to reconnect previous devices

### Port Usage

- **6680**: Mopidy Iris (radio web UI)
- **8080**: FastAPI Bluetooth manager
- **2222**: SSH (QEMU only) → host port 2222
- **22**: SSH (physical Pi)

### Configuration Order

Files are applied in this order on first boot:
1. `config/dietpi.txt` - DietPi base configuration
2. `config/Automation_Custom_Script.sh` - Custom setup script
3. `config/mopidy.conf` - Mopidy music server config
4. `config/bluetooth-reconnect.sh` - Auto-reconnect setup
5. FastAPI app loaded from `config/bluetooth-web-manager/`

## Troubleshooting Development Issues

### QEMU Boot Issues

**Problem**: QEMU hangs or exits immediately
**Solution**:
```bash
# Ensure QEMU is installed
which qemu-system-aarch64

# Check disk space (needs ~10GB free)
df -h

# Check image file exists
ls -lh *.img
```

### Port Conflicts

**Problem**: "Address already in use" when starting services
**Solution**:
```bash
# Kill existing process
sudo lsof -i :6680  # Find process on port 6680
sudo kill -9 <PID>  # Kill it

# Or use different ports in config/Automation_Custom_Script.sh
```

### Image Build Failures

**Problem**: GitHub Actions build fails
**Check**:
- DietPi base image still available at URL
- GitHub Actions has sufficient storage quota
- Build script permissions are correct (`chmod +x scripts/build.sh`)
- No syntax errors in `config/dietpi.txt` or shell scripts

## Key Dependencies

**On Host (For Building)**:
- `p7zip-full` - Extract DietPi base images
- `qemu-user-static` - ARM emulation during build
- `kpartx` - Mount disk image partitions
- `xz-utils` - Compress images
- `parted` - Partition manipulation
- `dosfstools` - FAT filesystem tools

**On Raspberry Pi (Auto-installed)**:
- DietPi base OS
- Mopidy + Mopidy-TuneIn
- Mopidy-Iris web UI
- FastAPI + Uvicorn
- PulseAudio
- BlueZ
- Python 3
- systemd (service management)

## References & Links

**Project Documentation**:
- `README.md` - User-facing overview
- `PRD-RaspberryPi-Internet-Radio.md` - Complete product spec
- `CHEEKY-Brand-Guide.md` - Brand voice and guidelines
- `GITHUB-ACTIONS-COMPLETE.md` - CI/CD details
- `docs/` - User guides

**External Documentation**:
- [DietPi Docs](https://dietpi.com/docs/)
- [Mopidy Docs](https://docs.mopidy.com/)
- [FastAPI Docs](https://fastapi.tiangolo.com/)
- [QEMU Docs](https://www.qemu.org/docs/master/)
- [BlueZ Docs](http://www.bluez.org/)
- [Raspberry Pi Docs](https://www.raspberrypi.com/documentation/)

**Tools**:
- GitHub Actions for CI/CD
- Semantic versioning for releases
- MIT License (permissive, commercial-friendly)

## Brand & Communication

**Voice**: Playful but professional. The "cheeky" personality should come through in:
- Documentation tone (friendly, not stuffy)
- Error messages (helpful with personality)
- Community interactions (fun but respectful)
- Feature announcements (exciting but honest)

See `CHEEKY-Brand-Guide.md` for complete branding guidelines.

## Community & Contributing

Contributors should:
1. Read `CONTRIBUTING.md` for guidelines
2. Test changes in QEMU before submitting PR
3. Include documentation updates
4. Follow the cheeky brand voice
5. Be respectful and inclusive

See issues labeled "good-first-issue" for ways to get started.
