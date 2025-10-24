"""
MPV Player Controller - Handles audio playback and metadata
"""

import subprocess
import json
import asyncio
from pathlib import Path
from typing import Optional, Dict
import signal
import os

class PlayerController:
    """Controls MPV player instance for streaming radio"""

    def __init__(self, config_manager):
        self.config_mgr = config_manager
        self.mpv_process = None
        self.current_station = None
        self.current_status = "stopped"
        self.current_metadata = {}
        self.volume = 75

    def _start_mpv_process(self, stream_url: str):
        """Start a new MPV process for streaming"""
        try:
            # MPV arguments for optimal streaming performance
            mpv_args = [
                "mpv",
                "--no-audio-display",  # Don't show visualizer
                "--no-terminal",  # Don't show MPV terminal
                "--audio-device=pulse",  # Use PulseAudio for Bluetooth
                "--volume=" + str(self.volume),  # Set initial volume
                "--force-window=no",  # No window
                "--ytdl=no",  # Disable YouTube-DL
                "--no-config",  # Don't load user config
                "--cache=yes",
                "--cache-secs=10",  # 10 second cache
                "--stream-lavf-o-append=headers=User-Agent: Cheeky",
                stream_url
            ]

            self.mpv_process = subprocess.Popen(
                mpv_args,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                stdin=subprocess.PIPE
            )
            self.current_status = "playing"
            print(f"[Cheeky] Started playing: {stream_url}")

        except FileNotFoundError:
            raise Exception("MPV not found. Install with: sudo apt install mpv")
        except Exception as e:
            self.current_status = "stopped"
            raise Exception(f"Failed to start playback: {str(e)}")

    def _stop_mpv_process(self):
        """Stop the current MPV process"""
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

    def play(self, stream_url: str) -> None:
        """Start playing a stream"""
        # Stop any existing playback
        if self.mpv_process:
            self._stop_mpv_process()

        # Start new playback
        self._start_mpv_process(stream_url)

    def pause(self) -> None:
        """Pause playback"""
        if self.mpv_process and self.current_status == "playing":
            try:
                # Send pause command to MPV via stdin
                self.mpv_process.stdin.write(b"set pause yes\n")
                self.mpv_process.stdin.flush()
                self.current_status = "paused"
                print("[Cheeky] Paused playback")
            except Exception as e:
                print(f"[Cheeky] Error pausing: {e}")

    def resume(self) -> None:
        """Resume playback"""
        if self.mpv_process and self.current_status == "paused":
            try:
                # Send resume command to MPV via stdin
                self.mpv_process.stdin.write(b"set pause no\n")
                self.mpv_process.stdin.flush()
                self.current_status = "playing"
                print("[Cheeky] Resumed playback")
            except Exception as e:
                print(f"[Cheeky] Error resuming: {e}")

    def stop(self) -> None:
        """Stop playback"""
        self._stop_mpv_process()
        self.current_station = None
        self.current_metadata = {}

    def set_volume(self, volume: int) -> None:
        """Set volume (0-100)"""
        volume = max(0, min(100, volume))  # Clamp between 0-100
        self.volume = volume

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
