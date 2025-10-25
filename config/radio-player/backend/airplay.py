"""
Airplay Manager - Discovers and controls Airplay receiver devices
"""

import subprocess
import asyncio
from typing import List, Dict, Optional
import socket
import struct

class AirplayManager:
    """Manages Airplay receiver discovery and connection"""

    def __init__(self):
        self.timeout = 30  # Timeout for device discovery (increased for slow networks)
        self.connected_device = None
        self.last_discovered_devices = []  # Cache of last discovered devices

    def _get_local_ip(self) -> str:
        """Get local IP address for mDNS queries"""
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.connect(("8.8.8.8", 80))
            ip = s.getsockname()[0]
            s.close()
            return ip
        except:
            return "127.0.0.1"

    def _run_avahi_browse(self) -> Optional[str]:
        """Browse for Airplay devices using Avahi"""
        try:
            # Use -p (parsable) and -t (terminate) for fast, reliable parsing
            print(f"[Cheeky] Running avahi-browse with timeout={self.timeout}s")
            result = subprocess.run(
                ['avahi-browse', '-p', '-t', '-r', '_raop._tcp'],
                capture_output=True,
                text=True,
                timeout=self.timeout
            )
            print(f"[Cheeky] avahi-browse returned: rc={result.returncode}, stdout_len={len(result.stdout)}")
            return result.stdout.strip() if result.returncode == 0 else None
        except FileNotFoundError:
            print("[Cheeky] avahi-browse not found - Airplay discovery unavailable")
            return None
        except subprocess.TimeoutExpired as e:
            # Even on timeout, we might have partial output - use it!
            print(f"[Cheeky] Airplay discovery timeout after {self.timeout}s, checking partial output")
            if e.stdout:
                output = e.stdout.decode('utf-8') if isinstance(e.stdout, bytes) else e.stdout
                if output and output.strip():
                    print(f"[Cheeky] Using partial output from timeout: {len(output)} chars")
                    return output.strip()
            print("[Cheeky] No partial output available from timeout")
            return None
        except Exception as e:
            print(f"[Cheeky] Airplay browse error: {type(e).__name__}: {e}")
            import traceback
            traceback.print_exc()
            return None

    async def discover_airplay_devices(self) -> List[Dict]:
        """Discover available Airplay receiver devices"""
        await asyncio.sleep(0)  # Make it async

        try:
            output = self._run_avahi_browse()
            if not output:
                print("[Cheeky] No Airplay devices found (avahi not available)")
                return []

            devices = []
            seen_addresses = set()

            for line in output.split('\n'):
                line = line.strip()
                if not line:
                    continue

                # Parse semicolon-separated fields
                # Format: =;ens33;IPv4;Name;Type;Domain;Hostname;Address;Port;TXT...
                parts = line.split(';')

                # Only process resolved IPv4 entries (ignore IPv6 duplicates)
                if len(parts) >= 9 and parts[0] == '=' and parts[2] == 'IPv4':
                    try:
                        # Decode name (replace \032 with space, \064 with @)
                        raw_name = parts[3]
                        device_name = raw_name.replace('\\032', ' ').replace('\\064', '@')

                        # Remove MAC address prefix if present (e.g., "ABC123@DeviceName" -> "DeviceName")
                        if '@' in device_name:
                            device_name = device_name.split('@', 1)[1]

                        hostname = parts[6]
                        address = parts[7]
                        port = int(parts[8])

                        # Avoid duplicates
                        if address not in seen_addresses:
                            seen_addresses.add(address)
                            device = {
                                "name": device_name,
                                "hostname": hostname,
                                "address": address,
                                "port": port,
                                "type": "airplay"
                            }
                            devices.append(device)
                            print(f"[Cheeky] Found Airplay: {device_name} at {address}:{port}")

                    except (IndexError, ValueError) as e:
                        print(f"[Cheeky] Failed to parse Airplay line: {e}")
                        continue

            print(f"[Cheeky] Discovered {len(devices)} Airplay device(s)")

            # Cache the discovered devices
            self.last_discovered_devices = devices

            return devices

        except Exception as e:
            print(f"[Cheeky] Error discovering Airplay devices: {e}")
            # Return cached devices on error
            return self.last_discovered_devices

    async def connect_airplay(self, address: str, port: int = 5000) -> Dict:
        """Connect to an Airplay receiver device"""
        await asyncio.sleep(0)  # Make it async

        try:
            # Test connection to Airplay device
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(5)

            result = sock.connect_ex((address, port))
            sock.close()

            if result == 0:
                self.connected_device = {
                    "address": address,
                    "port": port,
                    "type": "airplay"
                }
                print(f"[Cheeky] Connected to Airplay receiver at {address}:{port}")
                return {
                    "status": "connected",
                    "message": f"Connected to Airplay receiver at {address}",
                    "device": self.connected_device
                }
            else:
                return {
                    "status": "failed",
                    "message": f"Could not connect to {address}:{port}",
                    "address": address,
                    "port": port
                }

        except Exception as e:
            print(f"[Cheeky] Airplay connection error: {e}")
            return {
                "status": "error",
                "message": str(e),
                "address": address
            }

    async def disconnect_airplay(self) -> Dict:
        """Disconnect from Airplay receiver"""
        await asyncio.sleep(0)  # Make it async

        try:
            if self.connected_device:
                addr = self.connected_device.get("address", "Unknown")
                self.connected_device = None
                print(f"[Cheeky] Disconnected from Airplay receiver at {addr}")
                return {
                    "status": "disconnected",
                    "message": f"Disconnected from Airplay receiver"
                }
            else:
                return {
                    "status": "not_connected",
                    "message": "No Airplay device currently connected"
                }

        except Exception as e:
            print(f"[Cheeky] Airplay disconnect error: {e}")
            return {
                "status": "error",
                "message": str(e)
            }

    async def get_connected_device(self) -> Optional[Dict]:
        """Get currently connected Airplay device"""
        await asyncio.sleep(0)  # Make it async
        return self.connected_device

    async def get_status(self) -> Dict:
        """Get Airplay manager status"""
        await asyncio.sleep(0)  # Make it async

        return {
            "type": "airplay",
            "connected": self.connected_device is not None,
            "device": self.connected_device,
            "available": True  # Airplay is always available
        }
