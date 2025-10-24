"""
Favorites Manager - Stores and retrieves favorite stations from JSON
"""

import json
from pathlib import Path
from typing import List, Dict, Optional
from datetime import datetime
import asyncio

class FavoritesManager:
    """Manages user's favorite radio stations"""

    def __init__(self, config_dir: Path):
        self.config_dir = Path(config_dir)
        self.favorites_file = self.config_dir / "favorites.json"
        self._favorites = []
        self._load()

    def _load(self):
        """Load favorites from disk"""
        if self.favorites_file.exists():
            try:
                with open(self.favorites_file, 'r') as f:
                    data = json.load(f)
                    self._favorites = data.get("favorites", [])
            except (json.JSONDecodeError, IOError) as e:
                print(f"[Cheeky] Error loading favorites: {e}")
                self._favorites = []
        else:
            self._favorites = []
            self._save()

    def _save(self):
        """Save favorites to disk"""
        try:
            with open(self.favorites_file, 'w') as f:
                json.dump({"favorites": self._favorites}, f, indent=2)
        except IOError as e:
            print(f"[Cheeky] Error saving favorites: {e}")

    async def get_all(self) -> List[Dict]:
        """Get all favorite stations"""
        await asyncio.sleep(0)  # Make it async
        return self._favorites.copy()

    async def add(self, station: Dict) -> None:
        """Add a station to favorites"""
        await asyncio.sleep(0)  # Make it async

        # Check if already exists
        if any(s.get("uuid") == station.get("uuid") for s in self._favorites):
            print(f"[Cheeky] Station already in favorites: {station.get('name')}")
            return

        # Add with timestamp
        favorite = station.copy()
        favorite["added_at"] = datetime.now().isoformat()

        self._favorites.append(favorite)
        self._save()
        print(f"[Cheeky] Added favorite: {station.get('name')}")

    async def remove(self, uuid: str) -> None:
        """Remove a station from favorites"""
        await asyncio.sleep(0)  # Make it async

        original_len = len(self._favorites)
        self._favorites = [s for s in self._favorites if s.get("uuid") != uuid]

        if len(self._favorites) < original_len:
            self._save()
            print(f"[Cheeky] Removed favorite: {uuid}")
        else:
            print(f"[Cheeky] Station not found in favorites: {uuid}")

    async def is_favorite(self, uuid: str) -> bool:
        """Check if a station is in favorites"""
        await asyncio.sleep(0)  # Make it async
        return any(s.get("uuid") == uuid for s in self._favorites)

    async def clear(self) -> None:
        """Clear all favorites"""
        await asyncio.sleep(0)  # Make it async
        self._favorites = []
        self._save()
        print("[Cheeky] Favorites cleared")
