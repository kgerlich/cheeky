"""
RAOP Streaming - Handles Airplay audio streaming using pyatv
Optimized for modern Airplay 2 devices (tested with Yamaha receivers)
"""

import asyncio
import pyatv
from pyatv.const import Protocol
import subprocess
import tempfile
import os
from typing import Optional

class RAOPStreamer:
    """Handles RAOP/Airplay audio streaming"""

    def __init__(self):
        self.atv = None
        self.stream_task = None
        self.buffer_process = None
        self.temp_file_path = None
        self.is_streaming = False
        self.current_address = None
        self.current_port = None

    async def connect(self, address: str, port: int = 5000) -> bool:
        """Connect to Airplay receiver via RAOP protocol (modern Airplay 2 devices)"""
        try:
            print(f"[Cheeky RAOP] Connecting to device at {address}:{port}...")
            loop = asyncio.get_event_loop()

            # Scan for Airplay devices on the network
            print(f"[Cheeky RAOP] Scanning for device at {address}...")
            atvs = await pyatv.scan(loop, timeout=15)
            print(f"[Cheeky RAOP] pyatv scan completed, found {len(atvs)} devices")

            # Debug: print all found devices
            for dev in atvs:
                print(f"[Cheeky RAOP]   - Device: name='{dev.name}' address='{dev.address}'")

            # Find the target device by address (convert IPv4Address to string for comparison)
            target = next((c for c in atvs if str(c.address) == address), None)
            if not target:
                print(f"[Cheeky RAOP] Device not found at {address}")
                print(f"[Cheeky RAOP] Available devices:")
                for dev in atvs:
                    print(f"[Cheeky RAOP]   - {dev.name} at {dev.address}")
                return False

            print(f"[Cheeky RAOP] Found: {target.name} at {target.address}")
            print(f"[Cheeky RAOP] Connecting via RAOP...")

            # Connect using RAOP protocol
            self.atv = await pyatv.connect(target, Protocol.RAOP)
            self.current_address = address
            self.current_port = port

            print(f"[Cheeky RAOP] ✓ Connected to {target.name}")
            return True

        except Exception as e:
            print(f"[Cheeky RAOP] Connection failed: {e}")
            import traceback
            traceback.print_exc()
            return False

    async def start_stream(self, stream_url: str, volume: int = 60) -> bool:
        """Start streaming audio to Airplay receiver"""
        if not self.atv:
            print("[Cheeky RAOP] Not connected to any device")
            return False

        try:
            # Set volume
            print(f"[Cheeky RAOP] Setting volume to {volume}...")
            try:
                await self.atv.audio.set_volume(volume)
            except Exception as e:
                print(f"[Cheeky RAOP] Volume control not supported: {e}")

            print(f"[Cheeky RAOP] Starting direct stream: {stream_url}")

            # Stream directly from ffmpeg stdout to pyatv
            # No buffering - just like the working test scripts!
            ffmpeg_cmd = [
                'ffmpeg',
                '-re',           # Real-time
                '-i', stream_url,
                '-c:a', 'aac',   # AAC codec
                '-b:a', '256k',
                '-ar', '44100',
                '-ac', '2',
                '-f', 'adts',    # ADTS container for AAC
                '-'              # Output to stdout
            ]

            print(f"[Cheeky RAOP] Starting ffmpeg: {' '.join(ffmpeg_cmd[:6])} ...")
            self.buffer_process = subprocess.Popen(
                ffmpeg_cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.DEVNULL
            )

            print(f"[Cheeky RAOP] Starting direct stream to receiver...")
            # Stream ffmpeg stdout directly to Airplay receiver
            self.stream_task = asyncio.create_task(
                self.atv.stream.stream_file(self.buffer_process.stdout)
            )

            self.is_streaming = True
            print(f"[Cheeky RAOP] ✓ Streaming to Airplay receiver")
            return True

        except Exception as e:
            print(f"[Cheeky RAOP] Streaming failed: {e}")
            import traceback
            traceback.print_exc()
            self._cleanup()
            return False

    async def stop_stream(self):
        """Stop streaming"""
        print("[Cheeky RAOP] Stopping stream...")

        try:
            # Cancel streaming task
            if self.stream_task and not self.stream_task.done():
                self.stream_task.cancel()
                try:
                    await self.stream_task
                except asyncio.CancelledError:
                    pass

            # Stop buffer process
            if self.buffer_process:
                self.buffer_process.terminate()
                try:
                    self.buffer_process.wait(timeout=2)
                except subprocess.TimeoutExpired:
                    self.buffer_process.kill()

            self._cleanup()
            self.is_streaming = False
            print("[Cheeky RAOP] ✓ Stream stopped")

        except Exception as e:
            print(f"[Cheeky RAOP] Error stopping stream: {e}")

    def _cleanup(self):
        """Clean up temporary files"""
        if self.temp_file_path and os.path.exists(self.temp_file_path):
            try:
                os.unlink(self.temp_file_path)
                print(f"[Cheeky RAOP] Cleaned up temp file")
            except Exception as e:
                print(f"[Cheeky RAOP] Failed to cleanup temp file: {e}")

        self.temp_file_path = None
        self.buffer_process = None
        self.stream_task = None

    async def disconnect(self):
        """Disconnect from Airplay receiver"""
        try:
            await self.stop_stream()

            if self.atv:
                self.atv.close()
                self.atv = None

            self.current_address = None
            self.current_port = None
            print("[Cheeky RAOP] ✓ Disconnected")

        except Exception as e:
            print(f"[Cheeky RAOP] Error disconnecting: {e}")

    def get_status(self) -> dict:
        """Get current streaming status"""
        return {
            "connected": self.atv is not None,
            "streaming": self.is_streaming,
            "address": self.current_address,
            "port": self.current_port
        }
