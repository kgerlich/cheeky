"""
Radio Browser API Client - Fetches station data from Radio Browser
"""

import aiohttp
import asyncio
import socket
from typing import Optional, List, Dict
from datetime import datetime, timedelta

class StationsClient:
    """Client for Radio Browser API"""

    API_SERVERS = [
        "https://de1.api.radio-browser.info",
        "https://de2.api.radio-browser.info",
        "https://fr1.api.radio-browser.info",
        "https://fi1.api.radio-browser.info",
        "https://at1.api.radio-browser.info",
        "https://nl1.api.radio-browser.info",
    ]

    # User-Agent for API requests (required by Radio Browser)
    USER_AGENT = "CheekyRadio/1.1.0"

    def __init__(self):
        self.session: Optional[aiohttp.ClientSession] = None
        self.cache = {}
        self.cache_ttl = 300  # 5 minutes
        self.current_server_index = 0
        print(f"[Cheeky] Stations client initialized. Using {len(self.API_SERVERS)} radio browser servers")

    def _get_next_server(self) -> str:
        """Get next API server URL and rotate index"""
        url = self.API_SERVERS[self.current_server_index % len(self.API_SERVERS)]
        self.current_server_index += 1
        return url

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

        session = await self._get_session()
        headers = {"User-Agent": self.USER_AGENT}

        # Try each server in rotation until one succeeds
        for attempt in range(len(self.API_SERVERS)):
            try:
                server = self._get_next_server()
                url = f"{server}/json/stations/search"
                params = {
                    "name": query,
                    "limit": limit,
                    "offset": offset,
                    "hidebroken": "true"
                }

                print(f"[Cheeky] Searching for '{query}' from {server}")
                async with session.get(url, params=params, headers=headers, timeout=aiohttp.ClientTimeout(total=10)) as resp:
                    if resp.status == 200:
                        stations = await resp.json()
                        print(f"[Cheeky] Got {len(stations)} results for '{query}'")
                        result = {
                            "stations": self._normalize_stations(stations),
                            "total": len(stations)
                        }
                        await self._cache_set(cache_key, result)
                        return result
                    else:
                        print(f"[Cheeky] Search API error {resp.status} from {server}, trying next...")
                        continue

            except asyncio.TimeoutError:
                print(f"[Cheeky] Search timeout from {server}, trying next...")
                continue
            except Exception as e:
                print(f"[Cheeky] Search error from {server}: {type(e).__name__}: {e}")
                continue

        print(f"[Cheeky] Search failed on all servers for '{query}'")
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

        session = await self._get_session()
        headers = {"User-Agent": self.USER_AGENT}

        # Try each server in rotation until one succeeds
        for attempt in range(len(self.API_SERVERS)):
            try:
                server = self._get_next_server()
                url = f"{server}/json/stations/search"

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

                async with session.get(url, params=params, headers=headers, timeout=aiohttp.ClientTimeout(total=10)) as resp:
                    if resp.status == 200:
                        stations = await resp.json()
                        result = {
                            "stations": self._normalize_stations(stations),
                            "total": len(stations)
                        }
                        await self._cache_set(cache_key, result)
                        return result
                    else:
                        print(f"[Cheeky] Browse API error {resp.status} from {server}, trying next...")
                        continue

            except asyncio.TimeoutError:
                print(f"[Cheeky] Browse timeout from {server}, trying next...")
                continue
            except Exception as e:
                print(f"[Cheeky] Browse error from {server}: {type(e).__name__}: {e}")
                continue

        print(f"[Cheeky] Browse failed on all servers")
        return {"stations": [], "total": 0}

    async def popular(
        self,
        limit: int = 20,
        offset: int = 0
    ) -> Dict:
        """Get popular/top-rated stations"""
        cache_key = f"popular:{limit}:{offset}"
        cached = await self._cache_get(cache_key)
        if cached and cached.get("stations"):  # Only use cache if it has stations
            return cached

        session = await self._get_session()
        headers = {"User-Agent": self.USER_AGENT}

        # Try each server in rotation until one succeeds
        for attempt in range(len(self.API_SERVERS)):
            try:
                server = self._get_next_server()
                url = f"{server}/json/stations/topclick"

                params = {
                    "limit": limit,
                    "offset": offset,
                    "hidebroken": "true"
                }

                print(f"[Cheeky] Fetching popular stations from {server}")
                async with session.get(url, params=params, headers=headers, timeout=aiohttp.ClientTimeout(total=10)) as resp:
                    if resp.status == 200:
                        stations = await resp.json()
                        print(f"[Cheeky] Got {len(stations)} popular stations from {server}")
                        result = {
                            "stations": self._normalize_stations(stations),
                            "total": len(stations)
                        }
                        if result["stations"]:  # Only cache if we got results
                            await self._cache_set(cache_key, result)
                        return result
                    else:
                        print(f"[Cheeky] Popular API error {resp.status} from {server}, trying next...")
                        continue

            except asyncio.TimeoutError:
                print(f"[Cheeky] Popular timeout from {server}, trying next...")
                continue
            except Exception as e:
                print(f"[Cheeky] Popular stations error from {server}: {type(e).__name__}: {e}")
                continue

        print(f"[Cheeky] Popular stations failed on all servers")
        return {"stations": [], "total": 0}

    async def get_station(self, uuid: str) -> Optional[Dict]:
        """Get detailed station information"""
        session = await self._get_session()
        headers = {"User-Agent": self.USER_AGENT}

        # Try each server in rotation until one succeeds
        for attempt in range(len(self.API_SERVERS)):
            try:
                server = self._get_next_server()
                url = f"{server}/json/stations/byuuid"

                params = {"uuids": uuid}

                async with session.get(url, params=params, headers=headers, timeout=aiohttp.ClientTimeout(total=10)) as resp:
                    if resp.status == 200:
                        stations = await resp.json()
                        if stations:
                            return self._normalize_station(stations[0])
                        return None
                    else:
                        print(f"[Cheeky] Get station API error {resp.status} from {server}, trying next...")
                        continue

            except asyncio.TimeoutError:
                print(f"[Cheeky] Get station timeout from {server}, trying next...")
                continue
            except Exception as e:
                print(f"[Cheeky] Get station error from {server}: {type(e).__name__}: {e}")
                continue

        print(f"[Cheeky] Get station failed on all servers for uuid: {uuid}")
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
