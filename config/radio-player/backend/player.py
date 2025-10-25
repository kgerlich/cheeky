"""
MPV Player Controller - Handles audio playback and metadata
"""

import subprocess
import json
import asyncio
from pathlib import Path
from typing import Optional, Dict, Callable
import signal
import os
import socket
import tempfile

try:
    from backend.raop_stream_raop import RAOPStreamer
    AIRPLAY_AVAILABLE = True
except ImportError as e:
    AIRPLAY_AVAILABLE = False
    RAOPStreamer = None
    print(f"[Cheeky] raop_play binary not available - Airplay streaming disabled ({e})")

class PlayerController:
    """Controls MPV player instance for streaming radio"""

    def __init__(self, config_manager, metadata_callback: Optional[Callable[[Dict], None]] = None):
        self.config_mgr = config_manager
        self.mpv_process = None
        self.raop_streamer = RAOPStreamer() if AIRPLAY_AVAILABLE else None
        self.current_station = None
        self.current_status = "stopped"
        self.current_metadata = {}
        self.volume = 75
        self.output_device = {"type": "local"}  # Default to local speaker
        self.fade_in_duration = 0.5  # Fade-in duration in seconds (500ms)
        self.fade_out_duration = 2.0  # Fade-out duration in seconds (2s - conservative default)
        self.mpv_ipc_socket = None  # Path to MPV IPC socket
        self.metadata_callback = metadata_callback  # Callback for metadata updates
        self.metadata_task = None  # Background task for metadata polling

    async def _get_audio_buffer_duration(self) -> float:
        """Query MPV for audio buffer duration to determine safe fade-out time"""
        try:
            # Try to get demuxer cache duration (stream buffer)
            cache_duration = await self._query_mpv_property("demuxer-cache-duration")
            if cache_duration and cache_duration > 0:
                # Use cache duration, but cap at 5 seconds to avoid excessive fade times
                buffer_time = min(float(cache_duration), 5.0)
                print(f"[Cheeky] Detected buffer: {buffer_time:.1f}s")
                return buffer_time
        except Exception:
            pass

        # Fallback: conservative 2-second default
        return 2.0

    async def _fade_volume(self, from_vol: int, to_vol: int, duration: float = None, is_fade_out: bool = False):
        """Fade volume from one level to another over specified duration"""
        if duration is None:
            if is_fade_out:
                # For fade-out, query buffer and use longer duration
                duration = await self._get_audio_buffer_duration()
                # Update the fade_out_duration for future reference
                self.fade_out_duration = duration
            else:
                # For fade-in, use the fixed short duration
                duration = self.fade_in_duration

        steps = 20  # Number of steps in the fade
        step_duration = duration / steps
        vol_step = (to_vol - from_vol) / steps

        for i in range(steps):
            current_vol = int(from_vol + (vol_step * i))
            await self._set_volume_immediate(current_vol)
            await asyncio.sleep(step_duration)

        # Final volume
        await self._set_volume_immediate(to_vol)

    async def _set_volume_immediate(self, volume: int):
        """Set volume immediately without fading"""
        volume = max(0, min(100, volume))
        device_type = self.output_device.get("type", "local")

        if device_type == "airplay":
            # For Airplay, we can't change volume on the fly easily
            # Volume is set when starting the stream
            pass
        else:
            # MPV supports runtime volume changes
            if self.mpv_process:
                try:
                    cmd = f"set volume {volume}\n".encode()
                    self.mpv_process.stdin.write(cmd)
                    self.mpv_process.stdin.flush()
                except Exception as e:
                    print(f"[Cheeky] Error setting volume: {e}")

    async def _query_mpv_property(self, property_name: str) -> Optional[any]:
        """Query MPV property via IPC socket"""
        if not self.mpv_ipc_socket or not os.path.exists(self.mpv_ipc_socket):
            return None

        try:
            # Connect to MPV's IPC socket
            sock = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
            sock.settimeout(1.0)
            sock.connect(self.mpv_ipc_socket)

            # Send get_property command
            command = json.dumps({"command": ["get_property", property_name]}) + "\n"
            sock.sendall(command.encode('utf-8'))

            # Receive response
            response_data = b""
            while True:
                chunk = sock.recv(4096)
                if not chunk:
                    break
                response_data += chunk
                if b"\n" in response_data:
                    break

            sock.close()

            # Parse JSON response
            response = json.loads(response_data.decode('utf-8').strip())
            if response.get("error") == "success":
                return response.get("data")
            return None

        except Exception as e:
            # Socket errors are expected if MPV isn't ready yet
            return None

    async def _poll_metadata(self):
        """Background task to poll metadata from MPV"""
        while self.mpv_process and self.current_status in ("playing", "paused"):
            try:
                # Query ICY metadata properties from MPV
                metadata = {}

                # Try to get ICY title (contains "Artist - Song")
                icy_title = await self._query_mpv_property("icy-title")
                if icy_title:
                    metadata["icy_title"] = icy_title
                    # Try to split into artist/title
                    if " - " in icy_title:
                        parts = icy_title.split(" - ", 1)
                        metadata["artist"] = parts[0].strip()
                        metadata["title"] = parts[1].strip()
                    else:
                        metadata["title"] = icy_title

                # Get station name
                icy_name = await self._query_mpv_property("icy-name")
                if icy_name:
                    metadata["station_name"] = icy_name

                # Get genre
                icy_genre = await self._query_mpv_property("icy-genre")
                if icy_genre:
                    metadata["genre"] = icy_genre

                # Get bitrate
                icy_br = await self._query_mpv_property("icy-br")
                if icy_br:
                    metadata["bitrate"] = f"{icy_br} kbps"

                # Update if metadata changed
                if metadata and metadata != self.current_metadata:
                    self.current_metadata = metadata
                    print(f"[Cheeky] Metadata updated: {metadata}")

                    # Notify via callback if provided
                    if self.metadata_callback:
                        try:
                            self.metadata_callback(metadata)
                        except Exception as e:
                            print(f"[Cheeky] Error in metadata callback: {e}")

                # Poll every 3 seconds
                await asyncio.sleep(3)

            except asyncio.CancelledError:
                break
            except Exception as e:
                # Don't spam errors
                await asyncio.sleep(3)

    def _start_metadata_polling(self):
        """Start background metadata polling task"""
        if self.metadata_task:
            self.metadata_task.cancel()
        self.metadata_task = asyncio.create_task(self._poll_metadata())

    def _start_mpv_process(self, stream_url: str, start_volume: int = 0):
        """Start a new MPV process for streaming"""
        try:
            # Create IPC socket path for metadata querying
            socket_dir = tempfile.gettempdir()
            self.mpv_ipc_socket = os.path.join(socket_dir, f"mpv-ipc-{os.getpid()}.sock")

            # Clean up old socket if it exists
            if os.path.exists(self.mpv_ipc_socket):
                os.unlink(self.mpv_ipc_socket)

            # MPV arguments for optimal streaming performance
            # Start at 0 volume to avoid clicks, will fade in after
            mpv_args = [
                "mpv",
                "--no-audio-display",  # Don't show visualizer
                "--no-terminal",  # Don't show MPV terminal
                "--audio-device=pulse",  # Use PulseAudio for Bluetooth
                "--volume=" + str(start_volume),  # Start at 0 to avoid click
                "--force-window=no",  # No window
                "--ytdl=no",  # Disable YouTube-DL
                "--no-config",  # Don't load user config
                "--cache=yes",
                "--cache-secs=10",  # 10 second cache
                "--stream-lavf-o-append=headers=User-Agent: Cheeky",
                "--input-ipc-server=" + self.mpv_ipc_socket,  # Enable IPC for metadata
                stream_url
            ]

            self.mpv_process = subprocess.Popen(
                mpv_args,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                stdin=subprocess.PIPE
            )
            self.current_status = "playing"
            print(f"[Cheeky] Started playing: {stream_url} (volume will fade in)")

            # Start metadata polling
            self._start_metadata_polling()

        except FileNotFoundError:
            raise Exception("MPV not found. Install with: sudo apt install mpv")
        except Exception as e:
            self.current_status = "stopped"
            raise Exception(f"Failed to start playback: {str(e)}")

    def _stop_mpv_process(self):
        """Stop the current MPV process"""
        # Cancel metadata polling task
        if self.metadata_task:
            self.metadata_task.cancel()
            self.metadata_task = None

        if self.mpv_process:
            try:
                self.mpv_process.terminate()
                self.mpv_process.wait(timeout=3)
            except subprocess.TimeoutExpired:
                self.mpv_process.kill()
            except Exception as e:
                print(f"[Cheeky] Error stopping MPV: {e}")
            finally:
                self.mpv_process = None
                self.current_status = "stopped"

        # Clean up IPC socket
        if self.mpv_ipc_socket and os.path.exists(self.mpv_ipc_socket):
            try:
                os.unlink(self.mpv_ipc_socket)
            except Exception:
                pass
            self.mpv_ipc_socket = None

    async def _start_airplay_stream(self, stream_url: str):
        """Start streaming to an Airplay device using RAOP"""
        if not AIRPLAY_AVAILABLE or not self.raop_streamer:
            raise Exception("Airplay streaming not available")

        if self.output_device.get("type") != "airplay":
            raise Exception("No Airplay device selected")

        try:
            address = self.output_device.get("address")
            port = self.output_device.get("port", 5000)

            if not address:
                raise Exception("Airplay device address not set")

            print(f"[Cheeky] Connecting to Airplay receiver at {address}:{port}")

            # Connect to RAOP device
            connected = await self.raop_streamer.connect(address, port)
            if not connected:
                raise Exception("Failed to connect to Airplay receiver")

            # Start streaming
            started = await self.raop_streamer.start_stream(stream_url, self.volume)
            if not started:
                raise Exception("Failed to start Airplay stream")

            self.current_status = "playing"
            print(f"[Cheeky] ✓ Airplay streaming active")

        except Exception as e:
            self.current_status = "stopped"
            raise Exception(f"Failed to start Airplay playback: {str(e)}")

    async def _stop_airplay_stream(self):
        """Stop Airplay streaming"""
        if self.raop_streamer:
            try:
                await self.raop_streamer.stop_stream()
                print("[Cheeky] Stopped Airplay playback")
            except Exception as e:
                print(f"[Cheeky] Error stopping Airplay: {e}")
            finally:
                self.current_status = "stopped"

    def set_output_device(self, device: Dict) -> None:
        """Set the output device for playback"""
        self.output_device = device
        device_type = device.get("type", "local")
        device_name = device.get("name", "Unknown")
        print(f"[Cheeky] Output device set to: {device_type} - {device_name}")

    async def play(self, stream_url: str) -> None:
        """Start playing a stream"""
        # Stop any existing playback
        if self.mpv_process:
            self._stop_mpv_process()
        if self.raop_streamer and self.raop_streamer.is_streaming:
            await self._stop_airplay_stream()

        # Start new playback based on output device
        device_type = self.output_device.get("type", "local")

        if device_type == "airplay":
            await self._start_airplay_stream(stream_url)
        else:
            # Use MPV for local and Bluetooth (PulseAudio handles routing)
            # Start at 0 volume to avoid click
            self._start_mpv_process(stream_url, start_volume=0)

            # Wait a brief moment for MPV to start buffering
            await asyncio.sleep(0.1)

            # Fade in from 0 to target volume
            print(f"[Cheeky] Fading in volume from 0 to {self.volume}...")
            await self._fade_volume(0, self.volume)

    async def pause(self) -> None:
        """Pause playback"""
        device_type = self.output_device.get("type", "local")

        if device_type == "airplay":
            # Pause Airplay streaming
            if self.raop_streamer and self.raop_streamer.is_streaming:
                try:
                    await self.raop_streamer.pause_stream()
                    self.current_status = "paused"
                    print("[Cheeky] Paused Airplay playback")
                except Exception as e:
                    print(f"[Cheeky] Error pausing Airplay: {e}")
        else:
            # Pause MPV (local/Bluetooth)
            if self.mpv_process and self.current_status == "playing":
                try:
                    # Fade out volume before pausing to avoid click
                    print(f"[Cheeky] Fading out volume from {self.volume} to 0...")
                    await self._fade_volume(self.volume, 0, is_fade_out=True)

                    # Wait for hardware buffer to drain (200ms should be enough for most hardware)
                    print("[Cheeky] Draining hardware buffer...")
                    await asyncio.sleep(0.2)

                    # Send pause command to MPV via stdin
                    self.mpv_process.stdin.write(b"set pause yes\n")
                    self.mpv_process.stdin.flush()
                    self.current_status = "paused"
                    print("[Cheeky] Paused playback")
                except Exception as e:
                    print(f"[Cheeky] Error pausing: {e}")

    async def resume(self) -> None:
        """Resume playback"""
        device_type = self.output_device.get("type", "local")

        if device_type == "airplay":
            # Resume Airplay streaming
            if self.raop_streamer and self.raop_streamer.is_paused:
                try:
                    success = await self.raop_streamer.resume_stream()
                    if success:
                        self.current_status = "playing"
                        print("[Cheeky] Resumed Airplay playback")
                except Exception as e:
                    print(f"[Cheeky] Error resuming Airplay: {e}")
        else:
            # Resume MPV (local/Bluetooth)
            if self.mpv_process and self.current_status == "paused":
                try:
                    # Send resume command to MPV via stdin
                    self.mpv_process.stdin.write(b"set pause no\n")
                    self.mpv_process.stdin.flush()
                    self.current_status = "playing"

                    # Fade in volume from 0 to target to avoid click
                    print(f"[Cheeky] Fading in volume from 0 to {self.volume}...")
                    await self._fade_volume(0, self.volume)
                    print("[Cheeky] Resumed playback")
                except Exception as e:
                    print(f"[Cheeky] Error resuming: {e}")

    async def stop(self) -> None:
        """Stop playback"""
        device_type = self.output_device.get("type", "local")

        # Fade out volume before stopping to avoid click (MPV only)
        if device_type != "airplay" and self.mpv_process and self.current_status == "playing":
            try:
                print(f"[Cheeky] Fading out volume from {self.volume} to 0...")
                await self._fade_volume(self.volume, 0, is_fade_out=True)

                # Wait for hardware buffer to drain (200ms should be enough for most hardware)
                print("[Cheeky] Draining hardware buffer...")
                await asyncio.sleep(0.2)
            except Exception as e:
                print(f"[Cheeky] Error fading out: {e}")

        # Stop playback
        self._stop_mpv_process()
        if self.raop_streamer and self.raop_streamer.is_streaming:
            await self._stop_airplay_stream()
        self.current_station = None
        self.current_metadata = {}

    async def set_volume(self, volume: int) -> None:
        """Set volume (0-100)"""
        volume = max(0, min(100, volume))  # Clamp between 0-100
        self.volume = volume

        device_type = self.output_device.get("type", "local")

        if device_type == "airplay":
            # For Airplay, restart stream with new volume if currently streaming
            if self.raop_streamer and self.raop_streamer.is_streaming:
                try:
                    stream_url = self.raop_streamer.current_stream_url
                    if stream_url:
                        print(f"[Cheeky] Restarting Airplay stream with volume {volume}%")
                        await self.raop_streamer.stop_stream()
                        await self.raop_streamer.start_stream(stream_url, volume)
                except Exception as e:
                    print(f"[Cheeky] Error changing Airplay volume: {e}")
        else:
            # MPV supports runtime volume changes
            if self.mpv_process:
                try:
                    # Send volume command to MPV
                    cmd = f"set volume {volume}\n".encode()
                    self.mpv_process.stdin.write(cmd)
                    self.mpv_process.stdin.flush()
                    print(f"[Cheeky] Volume set to {volume}%")
                except Exception as e:
                    print(f"[Cheeky] Error setting volume: {e}")

    def get_volume(self) -> int:
        """Get current volume"""
        return self.volume

    def get_status(self) -> Dict:
        """Get current playback status"""
        # Check if process is still running
        if self.mpv_process:
            if self.mpv_process.poll() is not None:
                # Process has exited
                self.current_status = "stopped"
                self.mpv_process = None

        return {
            "status": self.current_status,
            "metadata": self.current_metadata
        }

    def is_playing(self) -> bool:
        """Check if currently playing"""
        return self.current_status == "playing"

    def __del__(self):
        """Cleanup on deletion"""
        if self.mpv_process:
            self._stop_mpv_process()
