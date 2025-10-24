"""
Radio Browser API Client - Fetches station data from Radio Browser
"""

import aiohttp
import asyncio
from typing import Optional, List, Dict
from datetime import datetime, timedelta

class StationsClient:
    """Client for Radio Browser API"""

    BASE_URL = "https://de1.api.radio-browser.info/json"

    def __init__(self):
        self.session: Optional[aiohttp.ClientSession] = None
        self.cache = {}
        self.cache_ttl = 300  # 5 minutes

    async def _get_session(self) -> aiohttp.ClientSession:
        """Get or create aiohttp session"""
        if self.session is None:
            self.session = aiohttp.ClientSession()
        return self.session

    async def _cache_get(self, key: str) -> Optional[Dict]:
        """Get cached result if still valid"""
        if key in self.cache:
            data, timestamp = self.cache[key]
            if datetime.now() - timestamp < timedelta(seconds=self.cache_ttl):
                return data
            else:
                del self.cache[key]
        return None

    async def _cache_set(self, key: str, data: Dict) -> None:
        """Cache a result with timestamp"""
        self.cache[key] = (data, datetime.now())

    async def search(
        self,
        query: str,
        limit: int = 20,
        offset: int = 0
    ) -> Dict:
        """Search stations by name, genre, or country"""
        cache_key = f"search:{query}:{limit}:{offset}"
        cached = await self._cache_get(cache_key)
        if cached:
            return cached

        try:
            session = await self._get_session()

            # Try search by name first
            url = f"{self.BASE_URL}/stations/search"
            params = {
                "name": query,
                "limit": limit,
                "offset": offset,
                "hidebroken": "true"
            }

            async with session.get(url, params=params) as resp:
                if resp.status == 200:
                    stations = await resp.json()
                    result = {
                        "stations": self._normalize_stations(stations),
                        "total": len(stations)
                    }
                    await self._cache_set(cache_key, result)
                    return result
                else:
                    raise Exception(f"API returned {resp.status}")

        except Exception as e:
            print(f"[Cheeky] Search error: {e}")
            return {"stations": [], "total": 0}

    async def browse(
        self,
        genre: Optional[str] = None,
        country: Optional[str] = None,
        language: Optional[str] = None,
        limit: int = 20,
        offset: int = 0
    ) -> Dict:
        """Browse stations by category"""
        cache_key = f"browse:{genre}:{country}:{language}:{limit}:{offset}"
        cached = await self._cache_get(cache_key)
        if cached:
            return cached

        try:
            session = await self._get_session()
            url = f"{self.BASE_URL}/stations/search"

            params = {
                "limit": limit,
                "offset": offset,
                "hidebroken": "true"
            }

            if genre:
                params["tag"] = genre
            if country:
                params["country"] = country
            if language:
                params["language"] = language

            async with session.get(url, params=params) as resp:
                if resp.status == 200:
                    stations = await resp.json()
                    result = {
                        "stations": self._normalize_stations(stations),
                        "total": len(stations)
                    }
                    await self._cache_set(cache_key, result)
                    return result
                else:
                    raise Exception(f"API returned {resp.status}")

        except Exception as e:
            print(f"[Cheeky] Browse error: {e}")
            return {"stations": [], "total": 0}

    async def popular(
        self,
        limit: int = 20,
        offset: int = 0
    ) -> Dict:
        """Get popular/top-rated stations"""
        cache_key = f"popular:{limit}:{offset}"
        cached = await self._cache_get(cache_key)
        if cached:
            return cached

        try:
            session = await self._get_session()
            url = f"{self.BASE_URL}/stations/topclick"

            params = {
                "limit": limit,
                "offset": offset,
                "hidebroken": "true"
            }

            async with session.get(url, params=params) as resp:
                if resp.status == 200:
                    stations = await resp.json()
                    result = {
                        "stations": self._normalize_stations(stations),
                        "total": len(stations)
                    }
                    await self._cache_set(cache_key, result)
                    return result
                else:
                    raise Exception(f"API returned {resp.status}")

        except Exception as e:
            print(f"[Cheeky] Popular stations error: {e}")
            return {"stations": [], "total": 0}

    async def get_station(self, uuid: str) -> Optional[Dict]:
        """Get detailed station information"""
        try:
            session = await self._get_session()
            url = f"{self.BASE_URL}/stations/byuuid"

            params = {"uuids": uuid}

            async with session.get(url, params=params) as resp:
                if resp.status == 200:
                    stations = await resp.json()
                    if stations:
                        return self._normalize_station(stations[0])
                    return None
                else:
                    raise Exception(f"API returned {resp.status}")

        except Exception as e:
            print(f"[Cheeky] Get station error: {e}")
            return None

    def _normalize_station(self, station: Dict) -> Dict:
        """Normalize station data to our format"""
        return {
            "uuid": station.get("stationuuid", ""),
            "name": station.get("name", "Unknown"),
            "url": station.get("url_resolved", station.get("url", "")),
            "favicon": station.get("favicon", ""),
            "country": station.get("country", ""),
            "language": station.get("language", ""),
            "tags": station.get("tags", "").split(",") if station.get("tags") else [],
            "bitrate": station.get("bitrate", 0),
            "codec": station.get("codec", ""),
        }

    def _normalize_stations(self, stations: List[Dict]) -> List[Dict]:
        """Normalize multiple stations"""
        return [self._normalize_station(s) for s in stations]

    async def close(self):
        """Close the aiohttp session"""
        if self.session:
            await self.session.close()
            self.session = None

    def __del__(self):
        """Cleanup on deletion"""
        # Note: Proper async cleanup should be done via shutdown event
        pass
