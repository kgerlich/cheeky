"""
Bluetooth Manager - Controls Bluetooth device pairing and connection
"""

import subprocess
import asyncio
from typing import List, Dict, Optional

class BluetoothManager:
    """Manages Bluetooth device pairing and connection"""

    def __init__(self):
        self.timeout = 10

    def _run_bluetoothctl(self, commands: str) -> Optional[str]:
        """Run bluetoothctl with provided commands"""
        try:
            result = subprocess.run(
                ['bluetoothctl'],
                input=commands,
                capture_output=True,
                text=True,
                timeout=self.timeout
            )
            return result.stdout.strip()
        except FileNotFoundError:
            print("[Cheeky] bluetoothctl not found")
            return None
        except Exception as e:
            print(f"[Cheeky] bluetoothctl error: {e}")
            return None

    async def get_devices(self) -> List[Dict]:
        """Get list of paired Bluetooth devices"""
        await asyncio.sleep(0)  # Make it async

        try:
            output = self._run_bluetoothctl("devices\nquit\n")
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
                        info_output = self._run_bluetoothctl(f"info {mac}\nquit\n")
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
            print(f"[Cheeky] Error getting devices: {e}")
            return []

    async def get_adapter_status(self) -> Optional[Dict]:
        """Get Bluetooth adapter status"""
        await asyncio.sleep(0)  # Make it async

        try:
            output = self._run_bluetoothctl("show\nquit\n")
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
                    try:
                        status["version"] = line.split(': ')[1]
                    except:
                        pass
                elif line.startswith("\tClass:"):
                    try:
                        status["class"] = line.split(': ')[1]
                    except:
                        pass

            return status
        except Exception as e:
            print(f"[Cheeky] Error getting adapter status: {e}")
            return None

    async def pair_device(self, mac: str) -> Dict:
        """Pair a new Bluetooth device"""
        await asyncio.sleep(0)  # Make it async

        try:
            commands = f"pair {mac}\nquit\n"
            output = self._run_bluetoothctl(commands)

            if "Pairing successful" in (output or ""):
                # Also connect after pairing
                self._run_bluetoothctl(f"connect {mac}\nquit\n")
                print(f"[Cheeky] Paired with {mac}")

                return {
                    "status": "paired",
                    "message": f"Successfully paired with {mac}",
                    "mac": mac
                }
            else:
                return {
                    "status": "failed",
                    "message": "Pairing failed",
                    "mac": mac
                }
        except Exception as e:
            print(f"[Cheeky] Pair error: {e}")
            return {
                "status": "error",
                "message": str(e),
                "mac": mac
            }

    async def connect_device(self, mac: str) -> Dict:
        """Connect to a paired Bluetooth device"""
        await asyncio.sleep(0)  # Make it async

        try:
            commands = f"connect {mac}\nquit\n"
            output = self._run_bluetoothctl(commands)

            devices = await self.get_devices()
            device = next((d for d in devices if d["mac"] == mac), None)

            if device:
                print(f"[Cheeky] Connected to {mac}")
                return {
                    "status": "connected",
                    "message": f"Connected to {mac}",
                    "device": device
                }
            else:
                return {
                    "status": "error",
                    "message": "Device not found",
                    "mac": mac
                }
        except Exception as e:
            print(f"[Cheeky] Connect error: {e}")
            return {
                "status": "error",
                "message": str(e),
                "mac": mac
            }

    async def disconnect_device(self, mac: str) -> Dict:
        """Disconnect from a Bluetooth device"""
        await asyncio.sleep(0)  # Make it async

        try:
            commands = f"disconnect {mac}\nquit\n"
            self._run_bluetoothctl(commands)

            devices = await self.get_devices()
            device = next((d for d in devices if d["mac"] == mac), None)

            if device:
                print(f"[Cheeky] Disconnected from {mac}")
                return {
                    "status": "disconnected",
                    "message": f"Disconnected from {mac}",
                    "device": device
                }
            else:
                return {
                    "status": "error",
                    "message": "Device not found",
                    "mac": mac
                }
        except Exception as e:
            print(f"[Cheeky] Disconnect error: {e}")
            return {
                "status": "error",
                "message": str(e),
                "mac": mac
            }

    async def remove_device(self, mac: str) -> Dict:
        """Remove a paired Bluetooth device"""
        await asyncio.sleep(0)  # Make it async

        try:
            commands = f"remove {mac}\nquit\n"
            self._run_bluetoothctl(commands)

            print(f"[Cheeky] Removed {mac}")
            return {
                "status": "removed",
                "message": f"Removed {mac}",
                "mac": mac
            }
        except Exception as e:
            print(f"[Cheeky] Remove error: {e}")
            return {
                "status": "error",
                "message": str(e),
                "mac": mac
            }

    async def scan_devices(self) -> Dict:
        """Start scanning for new Bluetooth devices"""
        await asyncio.sleep(0)  # Make it async

        try:
            commands = "scan on\nquit\n"
            self._run_bluetoothctl(commands)

            print("[Cheeky] Started Bluetooth scan")
            return {
                "status": "scanning",
                "message": "Scanning for devices..."
            }
        except Exception as e:
            print(f"[Cheeky] Scan error: {e}")
            return {
                "status": "error",
                "message": str(e)
            }
