#!/usr/bin/env python3
"""
Cheeky Bluetooth Manager API
FastAPI server for managing Bluetooth devices via REST API
"""

import subprocess
import json
import logging
from typing import Optional
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pathlib import Path

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI(
    title="Cheeky Bluetooth Manager",
    version="1.0.0",
    description="Manage Bluetooth speakers for Cheeky Radio"
)

# Enable CORS for web UI
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static files
try:
    app.mount("/static", StaticFiles(directory="static"), name="static")
except Exception as e:
    logger.warning(f"Could not mount static files: {e}")


# ==================== Bluetooth Manager Functions ====================

def run_bluetoothctl(commands):
    """Run bluetoothctl with provided commands"""
    try:
        result = subprocess.run(
            ['bluetoothctl'],
            input=commands,
            capture_output=True,
            text=True,
            timeout=10
        )
        return result.stdout.strip()
    except Exception as e:
        logger.error(f"bluetoothctl error: {e}")
        return None


def get_devices():
    """Get list of paired Bluetooth devices"""
    try:
        output = run_bluetoothctl("devices\nquit\n")
        if not output:
            return []

        devices = []
        for line in output.split('\n'):
            if line.startswith('Device'):
                parts = line.split(None, 2)
                if len(parts) >= 3:
                    mac = parts[1]
                    name = parts[2] if len(parts) > 2 else "Unknown"

                    # Get device info
                    info_output = run_bluetoothctl(f"info {mac}\nquit\n")
                    connected = "Connected: yes" in (info_output or "")
                    paired = "Paired: yes" in (info_output or "")

                    devices.append({
                        "mac": mac,
                        "name": name,
                        "connected": connected,
                        "paired": paired,
                        "trusted": paired
                    })

        return devices
    except Exception as e:
        logger.error(f"Error getting devices: {e}")
        return []


def get_adapter_status():
    """Get Bluetooth adapter status"""
    try:
        output = run_bluetoothctl("show\nquit\n")
        if not output:
            return None

        status = {
            "powered": "Powered: yes" in output,
            "discoverable": "Discoverable: yes" in output,
            "pairable": "Pairable: yes" in output,
            "version": "Unknown",
            "class": "Unknown"
        }

        for line in output.split('\n'):
            if line.startswith("\tVersion:"):
                status["version"] = line.split('\t')[1].split(': ')[1]
            elif line.startswith("\tClass:"):
                status["class"] = line.split(': ')[1]

        return status
    except Exception as e:
        logger.error(f"Error getting adapter status: {e}")
        return None


# ==================== REST API Endpoints ====================

@app.get("/")
async def root():
    """Serve the web UI"""
    html_file = Path(__file__).parent / "templates" / "index.html"
    if html_file.exists():
        return FileResponse(html_file)
    return {"message": "Cheeky Bluetooth Manager"}


@app.get("/api/devices")
async def list_devices():
    """Get all paired Bluetooth devices"""
    devices = get_devices()
    return devices


@app.post("/api/devices/scan")
async def scan_devices():
    """Start scanning for new Bluetooth devices"""
    try:
        # Start scan for 15 seconds
        commands = "scan on\nquit\n"
        run_bluetoothctl(commands)

        return {
            "status": "scanning",
            "message": "Scanning for 15 seconds...",
            "duration": 15
        }
    except Exception as e:
        logger.error(f"Scan error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/devices/available")
async def available_devices():
    """Get devices found during last scan"""
    # For now, return paired devices
    # In a full implementation, would track scan results separately
    devices = get_devices()
    return devices


@app.post("/api/devices/pair")
async def pair_device(request: dict):
    """Pair a new Bluetooth device"""
    mac = request.get("mac")
    if not mac:
        raise HTTPException(status_code=400, detail="MAC address required")

    try:
        commands = f"pair {mac}\nquit\n"
        output = run_bluetoothctl(commands)

        if "Pairing successful" in (output or ""):
            # Also connect after pairing
            run_bluetoothctl(f"connect {mac}\nquit\n")

            device = {
                "mac": mac,
                "name": "Unknown",
                "paired": True,
                "connected": True
            }

            return {
                "status": "paired",
                "message": f"Successfully paired with {mac}",
                "device": device
            }
        else:
            raise HTTPException(status_code=400, detail="Pairing failed")
    except Exception as e:
        logger.error(f"Pair error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/devices/connect")
async def connect_device(request: dict):
    """Connect to a paired Bluetooth device"""
    mac = request.get("mac")
    if not mac:
        raise HTTPException(status_code=400, detail="MAC address required")

    try:
        commands = f"connect {mac}\nquit\n"
        output = run_bluetoothctl(commands)

        device_info = get_devices()
        device = next((d for d in device_info if d["mac"] == mac), None)

        if device:
            return {
                "status": "connected",
                "message": f"Connected to {mac}",
                "device": device
            }
        else:
            raise HTTPException(status_code=404, detail="Device not found")
    except Exception as e:
        logger.error(f"Connect error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/devices/disconnect")
async def disconnect_device(request: dict):
    """Disconnect from a Bluetooth device"""
    mac = request.get("mac")
    if not mac:
        raise HTTPException(status_code=400, detail="MAC address required")

    try:
        commands = f"disconnect {mac}\nquit\n"
        run_bluetoothctl(commands)

        device_info = get_devices()
        device = next((d for d in device_info if d["mac"] == mac), None)

        if device:
            return {
                "status": "disconnected",
                "message": f"Disconnected from {mac}",
                "device": device
            }
        else:
            raise HTTPException(status_code=404, detail="Device not found")
    except Exception as e:
        logger.error(f"Disconnect error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/devices/remove")
async def remove_device(request: dict):
    """Remove a paired Bluetooth device"""
    mac = request.get("mac")
    if not mac:
        raise HTTPException(status_code=400, detail="MAC address required")

    try:
        commands = f"remove {mac}\nquit\n"
        run_bluetoothctl(commands)

        return {
            "status": "removed",
            "message": f"Removed {mac}",
            "device": {"mac": mac, "paired": False}
        }
    except Exception as e:
        logger.error(f"Remove error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/status")
async def bluetooth_status():
    """Get Bluetooth adapter status"""
    status = get_adapter_status()
    if status:
        return status
    raise HTTPException(status_code=500, detail="Could not get Bluetooth status")


@app.get("/api/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "ok",
        "service": "cheeky-bluetooth-manager",
        "version": "1.0.0"
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8080)
