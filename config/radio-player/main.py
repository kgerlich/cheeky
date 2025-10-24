#!/usr/bin/env python3
"""
Cheeky Radio Player - FastAPI Backend
A lightweight, modern web-based radio player for Raspberry Pi Zero W 2
"""

import os
import json
import asyncio
from pathlib import Path
from typing import Optional
from fastapi import FastAPI, WebSocket, HTTPException, Query
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from backend.config import ConfigManager
from backend.player import PlayerController
from backend.stations import StationsClient
from backend.favorites import FavoritesManager
from backend.recent import RecentManager
from backend.websocket import WebSocketManager
from backend.bluetooth import BluetoothManager

# ============================================================================
# Configuration
# ============================================================================

CONFIG_DIR = Path(os.getenv("CHEEKY_CONFIG", "/etc/cheeky"))
CONFIG_DIR.mkdir(parents=True, exist_ok=True)

app = FastAPI(
    title="Cheeky Radio Player",
    description="TuneIn-style internet radio for Raspberry Pi",
    version="1.1.0"
)

# CORS middleware for local network access
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize core components
config_mgr = ConfigManager(CONFIG_DIR)
player = PlayerController(config_mgr)
stations_client = StationsClient()
favorites_mgr = FavoritesManager(CONFIG_DIR)
recent_mgr = RecentManager(CONFIG_DIR)
ws_manager = WebSocketManager()
bluetooth_mgr = BluetoothManager()

# ============================================================================
# Request/Response Models
# ============================================================================

class StationInfo(BaseModel):
    uuid: str
    name: str
    url: str
    favicon: Optional[str] = None
    country: Optional[str] = None
    language: Optional[str] = None
    tags: Optional[list] = []
    bitrate: Optional[int] = None
    codec: Optional[str] = None

class PlayRequest(BaseModel):
    station_uuid: str
    stream_url: str
    station_name: str
    station_favicon: Optional[str] = None

class VolumeRequest(BaseModel):
    volume: int  # 0-100

class PlayerStatus(BaseModel):
    status: str  # "playing", "paused", "stopped"
    station: Optional[dict] = None
    volume: int
    metadata: Optional[dict] = None

class SearchResponse(BaseModel):
    stations: list
    total: int

# ============================================================================
# Station Management Endpoints
# ============================================================================

@app.get("/api/stations/search")
async def search_stations(
    q: str = Query(..., min_length=1),
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0)
):
    """Search radio stations by name, genre, or country"""
    try:
        results = await stations_client.search(q, limit, offset)
        return SearchResponse(stations=results["stations"], total=results["total"])
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/stations/browse")
async def browse_stations(
    genre: Optional[str] = None,
    country: Optional[str] = None,
    language: Optional[str] = None,
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0)
):
    """Browse stations by category"""
    try:
        results = await stations_client.browse(
            genre=genre,
            country=country,
            language=language,
            limit=limit,
            offset=offset
        )
        return SearchResponse(stations=results["stations"], total=results["total"])
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/stations/popular")
async def popular_stations(
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0)
):
    """Get popular radio stations"""
    try:
        results = await stations_client.popular(limit, offset)
        return SearchResponse(stations=results["stations"], total=results["total"])
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/stations/{uuid}")
async def get_station(uuid: str):
    """Get detailed station information"""
    try:
        station = await stations_client.get_station(uuid)
        if not station:
            raise HTTPException(status_code=404, detail="Station not found")
        return station
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# ============================================================================
# Player Control Endpoints
# ============================================================================

@app.post("/api/player/play")
async def play_station(request: PlayRequest):
    """Start playing a station"""
    try:
        player.play(request.stream_url)

        # Update recent history
        await recent_mgr.add(
            request.station_uuid,
            request.station_name
        )

        # Save last station
        await config_mgr.set("last_station", {
            "uuid": request.station_uuid,
            "name": request.station_name,
            "url": request.stream_url,
            "favicon": request.station_favicon
        })

        # Broadcast to WebSocket clients
        await ws_manager.broadcast({
            "type": "playback_status",
            "status": "playing",
            "station": {
                "uuid": request.station_uuid,
                "name": request.station_name,
                "favicon": request.station_favicon
            }
        })

        return {"status": "playing"}
    except Exception as e:
        await ws_manager.broadcast({
            "type": "error",
            "message": f"Playback error: {str(e)}"
        })
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/player/pause")
async def pause_playback():
    """Pause playback"""
    try:
        player.pause()
        await ws_manager.broadcast({
            "type": "playback_status",
            "status": "paused"
        })
        return {"status": "paused"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/player/stop")
async def stop_playback():
    """Stop playback"""
    try:
        player.stop()
        await ws_manager.broadcast({
            "type": "playback_status",
            "status": "stopped"
        })
        return {"status": "stopped"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/player/volume")
async def set_volume(request: VolumeRequest):
    """Set player volume (0-100)"""
    if not 0 <= request.volume <= 100:
        raise HTTPException(status_code=400, detail="Volume must be 0-100")
    try:
        player.set_volume(request.volume)
        await config_mgr.set("volume", request.volume)

        await ws_manager.broadcast({
            "type": "volume_change",
            "volume": request.volume
        })

        return {"volume": request.volume}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/player/status")
async def get_player_status():
    """Get current player status"""
    try:
        status = player.get_status()
        volume = await config_mgr.get("volume", 75)
        last_station = await config_mgr.get("last_station")

        return PlayerStatus(
            status=status["status"],
            station=last_station,
            volume=volume,
            metadata=status.get("metadata")
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# ============================================================================
# Favorites Management Endpoints
# ============================================================================

@app.get("/api/favorites")
async def get_favorites():
    """Get all favorite stations"""
    try:
        favorites = await favorites_mgr.get_all()
        return {"favorites": favorites}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/favorites")
async def add_favorite(station: StationInfo):
    """Add station to favorites"""
    try:
        await favorites_mgr.add(station.dict())

        await ws_manager.broadcast({
            "type": "favorites_updated",
            "station_uuid": station.uuid
        })

        return {"success": True, "message": "Station added to favorites"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.delete("/api/favorites/{uuid}")
async def remove_favorite(uuid: str):
    """Remove station from favorites"""
    try:
        await favorites_mgr.remove(uuid)

        await ws_manager.broadcast({
            "type": "favorites_updated",
            "station_uuid": uuid
        })

        return {"success": True, "message": "Station removed from favorites"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# ============================================================================
# Recent History Endpoint
# ============================================================================

@app.get("/api/recent")
async def get_recent():
    """Get recently played stations"""
    try:
        recent = await recent_mgr.get_all()
        return {"recent": recent}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# ============================================================================
# Bluetooth Management Endpoints
# ============================================================================

@app.get("/api/bluetooth/devices")
async def get_bluetooth_devices():
    """Get list of paired Bluetooth devices"""
    try:
        devices = await bluetooth_mgr.get_devices()
        return {"devices": devices}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/bluetooth/status")
async def get_bluetooth_status():
    """Get Bluetooth adapter status"""
    try:
        status = await bluetooth_mgr.get_adapter_status()
        if status:
            return status
        else:
            raise HTTPException(status_code=500, detail="Could not get Bluetooth status")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/bluetooth/scan")
async def scan_bluetooth_devices():
    """Start scanning for new Bluetooth devices"""
    try:
        result = await bluetooth_mgr.scan_devices()
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/bluetooth/pair")
async def pair_bluetooth_device(request: dict):
    """Pair a new Bluetooth device"""
    mac = request.get("mac")
    if not mac:
        raise HTTPException(status_code=400, detail="MAC address required")
    try:
        result = await bluetooth_mgr.pair_device(mac)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/bluetooth/connect")
async def connect_bluetooth_device(request: dict):
    """Connect to a paired Bluetooth device"""
    mac = request.get("mac")
    if not mac:
        raise HTTPException(status_code=400, detail="MAC address required")
    try:
        result = await bluetooth_mgr.connect_device(mac)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/bluetooth/disconnect")
async def disconnect_bluetooth_device(request: dict):
    """Disconnect from a Bluetooth device"""
    mac = request.get("mac")
    if not mac:
        raise HTTPException(status_code=400, detail="MAC address required")
    try:
        result = await bluetooth_mgr.disconnect_device(mac)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/bluetooth/remove")
async def remove_bluetooth_device(request: dict):
    """Remove a paired Bluetooth device"""
    mac = request.get("mac")
    if not mac:
        raise HTTPException(status_code=400, detail="MAC address required")
    try:
        result = await bluetooth_mgr.remove_device(mac)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# ============================================================================
# WebSocket Endpoint
# ============================================================================

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """WebSocket endpoint for real-time updates"""
    await ws_manager.connect(websocket)
    try:
        while True:
            # Keep connection alive
            data = await websocket.receive_text()
            # Echo back or handle client messages
            await websocket.send_text(json.dumps({"type": "pong"}))
    except Exception as e:
        print(f"WebSocket error: {e}")
    finally:
        await ws_manager.disconnect(websocket)

# ============================================================================
# Static Files & SPA
# ============================================================================

# Mount static files
static_dir = Path(__file__).parent / "static"
templates_dir = Path(__file__).parent / "templates"

if static_dir.exists():
    app.mount("/static", StaticFiles(directory=static_dir), name="static")

@app.get("/")
async def index():
    """Serve the main SPA"""
    index_file = templates_dir / "index.html"
    if index_file.exists():
        return FileResponse(index_file, media_type="text/html")
    else:
        return {"error": "Frontend not found"}

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "ok",
        "app": "Cheeky Radio Player",
        "version": "1.1.0"
    }

# ============================================================================
# Startup & Shutdown
# ============================================================================

@app.on_event("startup")
async def startup():
    """Initialize on startup"""
    print("[Cheeky] Radio Player starting...")
    print(f"[Cheeky] Config directory: {CONFIG_DIR}")

    # Load saved volume
    volume = await config_mgr.get("volume", 75)
    player.set_volume(volume)

    print("[Cheeky] Radio Player ready!")

@app.on_event("shutdown")
async def shutdown():
    """Cleanup on shutdown"""
    print("[Cheeky] Radio Player shutting down...")
    player.stop()

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=80,
        log_level="info"
    )
