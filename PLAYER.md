# Product Requirements Document (PRD)
## TuneIn-Style Radio Player for Raspberry Pi Zero W 2

---

## 1. Product Overview

### 1.1 Product Vision
A lightweight, modern web-based radio player that runs on Raspberry Pi Zero W 2, streaming internet radio stations via Bluetooth speakers with a serene, edgy, and responsive single-page application interface.

### 1.2 Target User
Single user seeking a dedicated radio streaming device with a clean, modern web interface accessible from any device on the local network.

### 1.3 Success Metrics
- Page load time < 2 seconds on Pi Zero W 2
- Audio playback latency < 1 second
- CPU usage < 50% during playback
- Memory footprint < 200MB
- 99% uptime during operation

---

## 2. Technical Stack

| Component | Technology | Justification |
|-----------|-----------|---------------|
| Backend Framework | FastAPI | Async, lightweight, perfect for Pi Zero |
| Audio Engine | mpv | Low CPU usage, excellent codec support |
| Frontend Framework | Alpine.js | Minimal footprint (~15KB), reactive |
| Data Storage | JSON files | No database overhead, simple config |
| Station API | Radio Browser API | Free, comprehensive, community-driven |
| Real-time Communication | WebSocket | Live metadata and status updates |
| Audio Output | Bluetooth (PulseAudio/BlueZ) | Wireless speaker support |

---

## 3. Core Features

### 3.1 Radio Playback (P0 - Critical)

**Requirements:**
- Play/pause/stop radio streams
- Volume control (0-100%, persistent)
- Automatic reconnection on stream failure
- Buffer management for smooth playback
- Support for common formats (MP3, AAC, OGG)

**User Stories:**
- As a user, I can click play on any station and hear audio within 2 seconds
- As a user, I can adjust volume with a slider that reflects immediately
- As a user, the player remembers my last volume setting

### 3.2 Station Discovery (P0 - Critical)

**Requirements:**
- Search stations by name, genre, or country
- Browse by categories (Genre, Country, Language)
- Display station metadata (name, bitrate, codec, logo)
- Show currently playing track info (if available)
- Paginated results (20 stations per page)

**User Stories:**
- As a user, I can search for "jazz" and see relevant stations instantly
- As a user, I can browse by genre to discover new stations
- As a user, I can see what song is currently playing

### 3.3 Favorites Management (P0 - Critical)

**Requirements:**
- Add/remove stations to/from favorites
- Persist favorites to JSON file
- Display favorites list prominently
- Quick access to favorite stations

**User Stories:**
- As a user, I can save my favorite stations with one click
- As a user, my favorites persist across restarts
- As a user, I can quickly access my saved stations

### 3.4 Real-time Metadata Display (P1 - Important)

**Requirements:**
- Display current track title and artist
- Show station logo/artwork when available
- Update metadata in real-time via WebSocket
- Fallback to station name if no metadata

**User Stories:**
- As a user, I see what song is playing without refreshing
- As a user, I see the station's logo while listening

### 3.5 Recently Played (P2 - Nice to Have)

**Requirements:**
- Track last 10 played stations
- Display in sidebar or dedicated section
- Persist to JSON file

**User Stories:**
- As a user, I can quickly replay a station I listened to yesterday

---

## 4. User Interface

### 4.1 Design Principles
- **Modern**: Clean, contemporary aesthetic
- **Serene**: Calming color palette, smooth transitions
- **Edgy**: Bold accents, subtle shadows, contemporary typography
- **Responsive**: Works on mobile, tablet, and desktop
- **Minimalist**: No clutter, focus on content

### 4.2 Color Palette

```
Primary Background:   #0f0f1e (Deep Navy)
Secondary Background: #1a1a2e (Charcoal)
Accent Primary:       #00d4ff (Electric Cyan)
Accent Secondary:     #0f4c75 (Deep Blue)
Text Primary:         #e8e8e8 (Off-white)
Text Secondary:       #b0b0b0 (Light Gray)
Error:                #ff4757 (Soft Red)
Success:              #2ed573 (Soft Green)
```

### 4.3 Typography

```
Primary Font: 'Inter' or 'Poppins'
Headings: 600 weight
Body: 400 weight
Size Scale: 14px base, 1.25 ratio
```

### 4.4 Layout Structure

```
┌─────────────────────────────────────────────────┐
│ Header: Logo + Connection Status                │
├─────────────────────────────────────────────────┤
│                                                 │
│  ┌───────────────────────────────────────────┐ │
│  │         NOW PLAYING CARD                  │ │
│  │  [Album Art 200x200]  Station Name        │ │
│  │                       Track - Artist       │ │
│  │                       ███████░░░ Vol: 75%  │ │
│  │                       [◄] [▶/❚❚] [♡]     │ │
│  └───────────────────────────────────────────┘ │
│                                                 │
│  Search: [_________________________] [🔍]       │
│                                                 │
│  ┌─────────────┐  ┌──────────────────────────┐ │
│  │ SIDEBAR     │  │  MAIN CONTENT            │ │
│  │             │  │                          │ │
│  │ ★ Favorites │  │  Browse / Search Results │ │
│  │ • Station 1 │  │                          │ │
│  │ • Station 2 │  │  [Station Card]          │ │
│  │             │  │  [Station Card]          │ │
│  │ 🕐 Recent   │  │  [Station Card]          │ │
│  │ • Station A │  │  ...                     │ │
│  │             │  │  [Pagination]            │ │
│  │ 📂 Browse   │  │                          │ │
│  │ • By Genre  │  │                          │ │
│  │ • By Country│  │                          │ │
│  └─────────────┘  └──────────────────────────┘ │
└─────────────────────────────────────────────────┘
```

### 4.5 UI Components

**Station Card:**
```
┌─────────────────────────────┐
│ [Logo]  Station Name        │
│         Genre • Country     │
│         128kbps MP3         │
│         [▶ Play] [♡ Fav]   │
└─────────────────────────────┘
```

**Volume Slider:**
- Modern range slider with gradient fill
- Real-time visual feedback
- Percentage display

**Loading States:**
- Skeleton screens for station cards
- Pulsing animation for buffering
- Smooth fade-in for loaded content

---

## 5. Backend Architecture

### 5.1 API Endpoints

#### Station Management
```
GET  /api/stations/search
     Query params: q (search term), limit, offset
     Returns: { stations: [], total: int }

GET  /api/stations/browse
     Query params: genre, country, language, limit, offset
     Returns: { stations: [], total: int }

GET  /api/stations/popular
     Query params: limit, offset
     Returns: { stations: [] }

GET  /api/stations/{uuid}
     Returns: { station: {} }
```

#### Player Control
```
POST /api/player/play
     Body: { station_uuid: string, stream_url: string }
     Returns: { status: "playing" }

POST /api/player/pause
     Returns: { status: "paused" }

POST /api/player/stop
     Returns: { status: "stopped" }

POST /api/player/volume
     Body: { volume: int (0-100) }
     Returns: { volume: int }

GET  /api/player/status
     Returns: {
       status: "playing|paused|stopped",
       station: {},
       volume: int,
       metadata: {}
     }
```

#### Favorites Management
```
GET  /api/favorites
     Returns: { favorites: [] }

POST /api/favorites
     Body: { station: {} }
     Returns: { success: bool }

DELETE /api/favorites/{uuid}
     Returns: { success: bool }
```

#### Recent History
```
GET  /api/recent
     Returns: { recent: [] }
```

#### WebSocket
```
WS   /ws
     Events sent to client:
     - playback_status: { status, station, metadata }
     - metadata_update: { title, artist, album }
     - volume_change: { volume }
     - error: { message }
```

### 5.2 Data Storage (JSON Files)

**config/settings.json**
```json
{
  "volume": 75,
  "last_station": null,
  "bluetooth_device": "xx:xx:xx:xx:xx:xx"
}
```

**config/favorites.json**
```json
{
  "favorites": [
    {
      "uuid": "station-uuid",
      "name": "Station Name",
      "url": "stream-url",
      "favicon": "logo-url",
      "country": "US",
      "language": "english",
      "tags": ["rock", "classic"],
      "bitrate": 128,
      "codec": "MP3",
      "added_at": "2025-10-24T10:30:00Z"
    }
  ]
}
```

**config/recent.json**
```json
{
  "recent": [
    {
      "uuid": "station-uuid",
      "name": "Station Name",
      "played_at": "2025-10-24T10:30:00Z"
    }
  ]
}
```

### 5.3 Core Modules

**player.py** - MPV Player Controller
- Initialize mpv with Bluetooth audio routing
- Control playback (play/pause/stop)
- Set volume
- Extract ICY metadata from streams
- Handle errors and reconnections

**stations.py** - Radio Browser API Client
- Search stations
- Browse by category
- Fetch popular stations
- Cache results (in-memory, 5 min TTL)
- Handle API rate limits

**favorites.py** - Favorites Manager
- Load/save favorites from/to JSON
- Add/remove favorites
- Validate station data

**recent.py** - Recent History Manager
- Track last 10 played stations
- Load/save from/to JSON
- Remove duplicates

**websocket.py** - WebSocket Manager
- Maintain active connections
- Broadcast player status updates
- Broadcast metadata changes
- Handle client disconnections

**config.py** - Configuration Manager
- Load/save settings from/to JSON
- Default configuration
- Validation

---

## 6. Performance Requirements

### 6.1 Resource Constraints (Pi Zero W 2)
- **CPU**: Single-core ARM Cortex-A53 @ 1GHz
- **RAM**: 512MB
- **Network**: 2.4GHz WiFi

### 6.2 Performance Targets
| Metric | Target | Critical Threshold |
|--------|--------|-------------------|
| Page Load Time | < 2s | < 3s |
| Stream Start Time | < 1s | < 2s |
| CPU Usage (idle) | < 10% | < 20% |
| CPU Usage (playing) | < 40% | < 60% |
| Memory Usage | < 150MB | < 200MB |
| WebSocket Latency | < 100ms | < 300ms |

### 6.3 Optimization Strategies
- Minify CSS and JS
- Enable gzip compression
- Lazy load images
- Paginate station lists (20 per page)
- Cache Radio Browser API responses (5 min)
- Use CDN for Alpine.js
- Optimize mpv buffer settings
- Limit concurrent WebSocket connections (max 5)

---

## 7. Error Handling

### 7.1 Network Errors
- Display friendly error message
- Auto-retry stream connection (3 attempts, exponential backoff)
- Fallback to cached station list if API unavailable

### 7.2 Playback Errors
- Log error details
- Show toast notification
- Auto-stop on fatal errors
- Offer "Try Again" option

### 7.3 Bluetooth Connection
- Detect disconnection
- Display warning banner
- Auto-reconnect when available

### 7.4 System Errors
- Graceful degradation
- Log to file for debugging
- Restart services if critical failure

---

## 8. Installation & Deployment

### 8.1 System Requirements
- Raspberry Pi Zero W 2
- Raspbian OS (Bookworm or later)
- Python 3.11+
- Bluetooth speaker paired

### 8.2 Installation Steps
```bash
# Install system dependencies
sudo apt update
sudo apt install -y python3-pip mpv pulseaudio bluez

# Clone repository
git clone <repo-url>
cd tunein-player

# Install Python dependencies
pip3 install -r requirements.txt

# Configure Bluetooth
# (Manual pairing steps)

# Run application
python3 backend/main.py
```

### 8.3 Auto-start Configuration
- Create systemd service
- Enable on boot
- Restart on failure

---

## 9. Security Considerations

### 9.1 Network Security
- Local network access only (no external exposure)
- No authentication required (single-user, trusted network)
- Rate limiting on API endpoints (100 req/min per IP)

### 9.2 Input Validation
- Sanitize all user inputs
- Validate station URLs
- Limit file sizes (favorites, recent)

### 9.3 Data Privacy
- No telemetry or analytics
- No external logging
- Local data storage only

---

## 10. Testing Strategy

### 10.1 Unit Tests
- Player control functions
- JSON file operations
- API client methods

### 10.2 Integration Tests
- End-to-end playback flow
- WebSocket communication
- Favorite management

### 10.3 Performance Tests
- Load testing (simulated user interactions)
- Memory leak detection
- CPU profiling

### 10.4 User Acceptance Tests
- Manual testing on Pi Zero W 2
- Different browsers (Chrome, Firefox, Safari)
- Mobile responsiveness

---

## 11. Future Enhancements (Out of Scope)

- Multi-user support with authentication
- Playlist creation
- Sleep timer
- Alarm/wake-up radio
- Podcast support
- Recording functionality
- EQ/audio effects
- Multi-room audio
- Voice control integration
- Chromecast support

---

## 12. Project Milestones

### Milestone 1: Core Backend (Week 1)
- ✓ FastAPI server setup
- ✓ MPV player integration
- ✓ Radio Browser API client
- ✓ JSON storage implementation

### Milestone 2: API & WebSocket (Week 2)
- ✓ All REST endpoints
- ✓ WebSocket real-time updates
- ✓ Favorites & recent history

### Milestone 3: Frontend UI (Week 3)
- ✓ HTML structure
- ✓ CSS styling (responsive)
- ✓ Alpine.js integration
- ✓ WebSocket client

### Milestone 4: Integration & Testing (Week 4)
- ✓ End-to-end testing
- ✓ Performance optimization
- ✓ Bug fixes
- ✓ Documentation

### Milestone 5: Deployment (Week 5)
- ✓ Pi Zero W 2 setup
- ✓ Bluetooth configuration
- ✓ Auto-start configuration
- ✓ User guide

---

## 13. Dependencies

### 13.1 Python Packages
```
fastapi==0.104.1
uvicorn[standard]==0.24.0
python-mpv==1.0.4
aiohttp==3.9.0
pydantic==2.5.0
websockets==12.0
python-multipart==0.0.6
```

### 13.2 System Packages
```
mpv
pulseaudio
bluez
python3-pip
python3-venv
```

### 13.3 Frontend Libraries
```
Alpine.js 3.x (CDN)
```

---

## 14. Documentation Deliverables

- README.md (Quick start guide)
- API documentation (OpenAPI/Swagger)
- Installation guide (Pi Zero W 2 specific)
- User manual (UI walkthrough)
- Developer guide (code structure)
- Troubleshooting guide

---

## 15. Success Criteria

**Launch Criteria:**
- [ ] All P0 features implemented
- [ ] All API endpoints functional
- [ ] UI responsive on mobile/desktop
- [ ] Successfully runs on Pi Zero W 2
- [ ] Bluetooth audio works reliably
- [ ] Performance targets met
- [ ] Zero critical bugs

**Post-Launch:**
- 30-day uptime > 95%
- Average CPU < 50% during playback
- User satisfaction > 4/5 (if surveyed)

---

**Document Version:** 1.0
**Last Updated:** October 24, 2025
**Status:** Approved for Development
