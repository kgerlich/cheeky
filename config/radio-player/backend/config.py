"""
Configuration Manager - Handles settings persistence via JSON files
"""

import json
from pathlib import Path
from typing import Any, Optional
import asyncio

class ConfigManager:
    """Manages application settings and configuration"""

    def __init__(self, config_dir: Path):
        self.config_dir = Path(config_dir)
        self.config_dir.mkdir(parents=True, exist_ok=True)
        self.settings_file = self.config_dir / "settings.json"
        self._cache = {}
        self._load_defaults()

    def _load_defaults(self):
        """Initialize default settings"""
        defaults = {
            "volume": 75,
            "last_station": None,
            "bluetooth_device": ""
        }

        # Load from file if it exists
        if self.settings_file.exists():
            try:
                with open(self.settings_file, 'r') as f:
                    self._cache = json.load(f)
            except (json.JSONDecodeError, IOError):
                self._cache = defaults
        else:
            self._cache = defaults
            self._save()

    def _save(self):
        """Save settings to disk"""
        try:
            with open(self.settings_file, 'w') as f:
                json.dump(self._cache, f, indent=2)
        except IOError as e:
            print(f"[Cheeky] Error saving config: {e}")

    async def get(self, key: str, default: Any = None) -> Any:
        """Get a configuration value"""
        await asyncio.sleep(0)  # Make it async
        return self._cache.get(key, default)

    async def set(self, key: str, value: Any) -> None:
        """Set a configuration value"""
        await asyncio.sleep(0)  # Make it async
        self._cache[key] = value
        self._save()

    async def get_all(self) -> dict:
        """Get all configuration"""
        await asyncio.sleep(0)  # Make it async
        return self._cache.copy()
