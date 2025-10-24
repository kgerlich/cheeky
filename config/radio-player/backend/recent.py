"""
Recent History Manager - Tracks recently played stations
"""

import json
from pathlib import Path
from typing import List, Dict
from datetime import datetime
import asyncio

class RecentManager:
    """Manages recently played radio stations (last 10)"""

    MAX_RECENT = 10

    def __init__(self, config_dir: Path):
        self.config_dir = Path(config_dir)
        self.recent_file = self.config_dir / "recent.json"
        self._recent = []
        self._load()

    def _load(self):
        """Load recent history from disk"""
        if self.recent_file.exists():
            try:
                with open(self.recent_file, 'r') as f:
                    data = json.load(f)
                    self._recent = data.get("recent", [])
            except (json.JSONDecodeError, IOError) as e:
                print(f"[Cheeky] Error loading recent: {e}")
                self._recent = []
        else:
            self._recent = []
            self._save()

    def _save(self):
        """Save recent history to disk"""
        try:
            with open(self.recent_file, 'w') as f:
                json.dump({"recent": self._recent}, f, indent=2)
        except IOError as e:
            print(f"[Cheeky] Error saving recent: {e}")

    async def get_all(self) -> List[Dict]:
        """Get all recently played stations"""
        await asyncio.sleep(0)  # Make it async
        return self._recent.copy()

    async def add(self, uuid: str, name: str) -> None:
        """Add a station to recent history"""
        await asyncio.sleep(0)  # Make it async

        # Remove duplicates (keep most recent)
        self._recent = [s for s in self._recent if s.get("uuid") != uuid]

        # Add to front
        entry = {
            "uuid": uuid,
            "name": name,
            "played_at": datetime.now().isoformat()
        }
        self._recent.insert(0, entry)

        # Keep only last MAX_RECENT entries
        self._recent = self._recent[:self.MAX_RECENT]

        self._save()
        print(f"[Cheeky] Added to recent: {name}")

    async def clear(self) -> None:
        """Clear all recent history"""
        await asyncio.sleep(0)  # Make it async
        self._recent = []
        self._save()
        print("[Cheeky] Recent history cleared")
