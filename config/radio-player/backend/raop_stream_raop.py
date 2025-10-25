"""
RAOP Streaming using raop_play binary
Works with both native Airplay 2 devices AND MASHBOX/AirServer
"""

import os
import platform
import subprocess
import asyncio
from typing import Optional
from pathlib import Path

class RAOPStreamer:
    """Handles RAOP/Airplay audio streaming using raop_play binary"""

    def __init__(self):
        self.ffmpeg_process = None
        self.raop_process = None
        self.is_streaming = False
        self.is_paused = False
        self.current_address = None
        self.current_port = None
        self.current_stream_url = None
        self.current_volume = 60
        self.bin_dir = Path(__file__).parent.parent / "bin"

    def _get_raop_binary(self) -> str:
        """Get the correct raop_play binary for current architecture"""
        machine = platform.machine().lower()

        # Map architecture to binary name
        if machine in ('aarch64', 'arm64'):
            binary = self.bin_dir / "raop_play-aarch64"
        elif machine in ('armv7l', 'armv7'):
            binary = self.bin_dir / "raop_play-armv7"
        elif machine in ('armv6l', 'armv6'):
            binary = self.bin_dir / "raop_play-armv6"
        elif machine in ('x86_64', 'amd64'):
            binary = self.bin_dir / "raop_play"
        else:
            raise RuntimeError(f"Unsupported architecture: {machine}")

        if not binary.exists():
            raise RuntimeError(f"raop_play binary not found: {binary}")

        return str(binary)

    async def connect(self, address: str, port: int = 5000) -> bool:
        """
        Test connection to Airplay receiver
        For raop_play, we don't need a persistent connection - just verify the binary exists
        """
        try:
            print(f"[Cheeky RAOP] Preparing to connect to {address}:{port}")

            # Verify binary exists
            binary = self._get_raop_binary()
            print(f"[Cheeky RAOP] Using binary: {binary}")

            self.current_address = address
            self.current_port = port

            print(f"[Cheeky RAOP] ✓ Ready to stream to {address}")
            return True

        except Exception as e:
            print(f"[Cheeky RAOP] Connection setup failed: {e}")
            import traceback
            traceback.print_exc()
            return False

    async def start_stream(self, stream_url: str, volume: int = 60) -> bool:
        """Start streaming audio to Airplay receiver"""
        if not self.current_address:
            print("[Cheeky RAOP] Not connected to any device")
            return False

        try:
            binary = self._get_raop_binary()

            print(f"[Cheeky RAOP] Starting stream: {stream_url}")
            print(f"[Cheeky RAOP] Target: {self.current_address}:{self.current_port}")
            print(f"[Cheeky RAOP] Volume: {volume}%")

            # Start ffmpeg to transcode stream to 44.1kHz stereo s16le
            # This is critical to avoid "mickey mouse" pitch issues
            ffmpeg_cmd = [
                'ffmpeg',
                '-re',              # Real-time playback
                '-i', stream_url,   # Input stream
                '-ar', '44100',     # Resample to 44.1kHz (critical!)
                '-ac', '2',         # Stereo (critical!)
                '-f', 's16le',      # Signed 16-bit little-endian PCM
                '-'                 # Output to stdout
            ]

            print(f"[Cheeky RAOP] Starting ffmpeg transcoder...")
            self.ffmpeg_process = subprocess.Popen(
                ffmpeg_cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.DEVNULL
            )

            # Start raop_play to stream to Airplay device
            # -v: volume (0-100)
            # -d: debug level
            # -a: use ALAC codec (critical for MASHBOX/AirServer!)
            # -p: port
            raop_cmd = [
                binary,
                '-v', str(volume),
                '-d', '0',                    # No debug output
                '-a',                         # ALAC codec (critical!)
                '-p', str(self.current_port),
                self.current_address,
                '-'                           # Read from stdin
            ]

            print(f"[Cheeky RAOP] Starting raop_play streamer...")
            self.raop_process = subprocess.Popen(
                raop_cmd,
                stdin=self.ffmpeg_process.stdout,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL
            )

            # Allow ffmpeg to receive SIGPIPE if raop_play exits
            self.ffmpeg_process.stdout.close()

            self.is_streaming = True
            self.is_paused = False
            self.current_stream_url = stream_url
            self.current_volume = volume
            print(f"[Cheeky RAOP] ✓ Streaming to {self.current_address}")
            return True

        except Exception as e:
            print(f"[Cheeky RAOP] Streaming failed: {e}")
            import traceback
            traceback.print_exc()
            await self.stop_stream()
            return False

    async def stop_stream(self):
        """Stop streaming"""
        print("[Cheeky RAOP] Stopping stream...")

        try:
            # Terminate raop_play first
            if self.raop_process:
                self.raop_process.terminate()
                try:
                    self.raop_process.wait(timeout=2)
                except subprocess.TimeoutExpired:
                    self.raop_process.kill()
                self.raop_process = None

            # Then terminate ffmpeg
            if self.ffmpeg_process:
                self.ffmpeg_process.terminate()
                try:
                    self.ffmpeg_process.wait(timeout=2)
                except subprocess.TimeoutExpired:
                    self.ffmpeg_process.kill()
                self.ffmpeg_process = None

            self.is_streaming = False
            self.is_paused = False
            print("[Cheeky RAOP] ✓ Stream stopped")

        except Exception as e:
            print(f"[Cheeky RAOP] Error stopping stream: {e}")

    async def pause_stream(self):
        """Pause streaming (stops stream, saves state for resume)"""
        if not self.is_streaming or self.is_paused:
            print("[Cheeky RAOP] Not streaming or already paused")
            return

        print("[Cheeky RAOP] Pausing stream...")
        await self.stop_stream()
        self.is_paused = True
        print("[Cheeky RAOP] ✓ Stream paused")

    async def resume_stream(self):
        """Resume streaming (restarts stream from saved URL)"""
        if not self.is_paused or not self.current_stream_url:
            print("[Cheeky RAOP] Not paused or no stream to resume")
            return

        print("[Cheeky RAOP] Resuming stream...")
        success = await self.start_stream(self.current_stream_url, self.current_volume)
        if success:
            print("[Cheeky RAOP] ✓ Stream resumed")
        return success

    async def disconnect(self):
        """Disconnect from Airplay receiver"""
        try:
            await self.stop_stream()

            self.current_address = None
            self.current_port = None
            print("[Cheeky RAOP] ✓ Disconnected")

        except Exception as e:
            print(f"[Cheeky RAOP] Error disconnecting: {e}")

    def get_status(self) -> dict:
        """Get current streaming status"""
        return {
            "connected": self.current_address is not None,
            "streaming": self.is_streaming,
            "address": self.current_address,
            "port": self.current_port
        }
