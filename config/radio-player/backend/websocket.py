"""
WebSocket Manager - Handles real-time connections and broadcasts
"""

import json
from typing import List, Dict
from fastapi import WebSocket
from datetime import datetime

class WebSocketManager:
    """Manages WebSocket connections for real-time updates"""

    def __init__(self):
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        """Accept and register a new WebSocket connection"""
        await websocket.accept()
        self.active_connections.append(websocket)
        print(f"[Cheeky] Client connected. Active: {len(self.active_connections)}")

    async def disconnect(self, websocket: WebSocket):
        """Disconnect and unregister a WebSocket"""
        self.active_connections.remove(websocket)
        print(f"[Cheeky] Client disconnected. Active: {len(self.active_connections)}")

    async def broadcast(self, message: Dict):
        """Broadcast a message to all connected clients"""
        # Add timestamp to message
        message["timestamp"] = datetime.now().isoformat()

        disconnected = []
        for connection in self.active_connections:
            try:
                await connection.send_json(message)
            except RuntimeError:
                # Connection was closed
                disconnected.append(connection)
            except Exception as e:
                print(f"[Cheeky] Error sending message: {e}")
                disconnected.append(connection)

        # Remove disconnected clients
        for conn in disconnected:
            self.active_connections.remove(conn)

    async def send_personal(self, websocket: WebSocket, message: Dict):
        """Send a message to a specific client"""
        try:
            message["timestamp"] = datetime.now().isoformat()
            await websocket.send_json(message)
        except Exception as e:
            print(f"[Cheeky] Error sending personal message: {e}")

    def get_connection_count(self) -> int:
        """Get number of active connections"""
        return len(self.active_connections)
