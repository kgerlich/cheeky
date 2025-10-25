# 🍑 Cheeky - Local Development Guide

This guide helps you set up and run Cheeky locally for development and debugging.

## Quick Start

### 1. Initial Setup (One-time)

```bash
./scripts/setup-local.sh
```

This script will:
- ✓ Check for Python 3.9+
- ✓ Install system dependencies (apt or homebrew)
- ✓ Create Python virtual environment (`venv/`)
- ✓ Install Python packages
- ✓ Create config directory at `~/.cheeky/`

**Requires**: `sudo` access for system package installation

### 2. Run the Application

```bash
./scripts/run-local.sh
```

This will:
- ✓ Activate the virtual environment
- ✓ Start FastAPI development server on port 8000
- ✓ Enable auto-reload on code changes
- ✓ Print logs to console

**Access**: http://localhost:8000

## Project Structure

```
config/
├── radio-player/              # Main application
│   ├── main.py                # FastAPI entry point
│   ├── backend/               # Backend modules
│   │   ├── player.py          # MPV player controller
│   │   ├── stations.py        # Radio Browser API client
│   │   ├── favorites.py       # Favorites manager
│   │   ├── recent.py          # Recent history
│   │   ├── bluetooth.py       # Bluetooth manager
│   │   ├── websocket.py       # WebSocket manager
│   │   └── config.py          # Configuration manager
│   └── templates/
│       └── index.html         # Frontend SPA
├── Automation_Custom_Script.sh # DietPi first-boot script
└── bluetooth-reconnect.sh      # Bluetooth auto-reconnect

scripts/
├── setup-local.sh             # Setup dev environment
├── run-local.sh               # Run app locally
├── install-cheeky.sh          # Build system installation
└── build.sh                   # Image customization
```

## Configuration

Local development uses `~/.cheeky/` for configuration:

```
~/.cheeky/
├── settings.json     # Volume, last station
├── favorites.json    # Saved stations
└── recent.json       # Recently played
```

These are created automatically by `setup-local.sh`.

## Development Workflow

### Making Changes

1. **Edit code** in `config/radio-player/backend/` or `config/radio-player/templates/index.html`
2. **Auto-reload** happens automatically when you save (thanks to `--reload`)
3. **Check console** for errors and debug logs
4. **Browser DevTools** (`F12`) for frontend debugging

### Testing API Endpoints

Use browser console or curl:

```bash
# Get popular stations (with debug logging)
curl http://localhost:8000/api/stations/popular

# Get test endpoint (hardcoded data)
curl http://localhost:8000/api/stations/test

# Get Bluetooth devices
curl http://localhost:8000/api/bluetooth/devices
```

### Browser DevTools

Press `F12` to open developer tools and check the **Console** tab for:
- `[Cheeky]` log messages
- API request/response logging
- WebSocket connection status

## Troubleshooting

### "venv not found"
```bash
./scripts/setup-local.sh
```

### "Port 8000 already in use"
```bash
# Kill existing process
lsof -i :8000
kill -9 <PID>

# Or use different port:
cd config/radio-player
python3 -m uvicorn main:app --port 8001
```

### "No stations loading"
Check browser console (`F12`) for error messages. The test endpoint is useful:
```javascript
fetch('/api/stations/test').then(r => r.json()).then(d => console.log(d))
```

### "Bluetooth not working"
Bluetooth features require `bluez` and `python3-dbus` to be installed. On Linux:
```bash
sudo apt install python3-dbus bluez
```

## Debugging Tips

### Enable Verbose Logging

The app already logs extensively to console. Key patterns to look for:
- `[Cheeky]` - Application logs
- Check terminal output and browser console for full trace

### Add Your Own Logs

```python
# In backend code
print(f"[Cheeky] Debug message: {variable}")

# In frontend (JavaScript)
console.log('[Cheeky] Debug message:', variable);
```

### Check Config Files

```bash
cat ~/.cheeky/settings.json
cat ~/.cheeky/favorites.json
cat ~/.cheeky/recent.json
```

### Test API Directly

```bash
# Pretty-print API responses
curl -s http://localhost:8000/api/stations/test | python3 -m json.tool
```

## Environment Variables

For local development:

```bash
# Use custom config directory
export CHEEKY_CONFIG=/path/to/config

# Then run
./scripts/run-local.sh
```

The `run-local.sh` script already sets:
```bash
export CHEEKY_CONFIG="$HOME/.cheeky"
```

## Building for Release

Once you're happy with your changes:

1. **Test thoroughly** locally with `./scripts/run-local.sh`
2. **Commit your changes**
```bash
git add -A
git commit -m "Your change description"
git push origin main
```
3. **Create a tag** to trigger GitHub Actions build
```bash
git tag -a v1.1.1 -m "Release v1.1.1: Description"
git push origin v1.1.1
```
4. **GitHub Actions** automatically builds QEMU images and creates release

## Dependencies

### System Level
- Python 3.9+
- mpv (audio playback)
- libpulse (audio output)
- bluez (Bluetooth - Linux only)
- python3-dbus (Bluetooth - Linux only)

### Python Packages
- fastapi==0.104.1
- uvicorn[standard]==0.24.0
- aiohttp==3.9.0
- pydantic==2.5.0
- websockets==12.0
- python-multipart==0.0.6
- python-mpv==1.0.4

All installed automatically by `setup-local.sh`.

## Performance Notes

Local development:
- **Fast reload** thanks to Uvicorn `--reload` flag
- **Full debug output** in console
- **No build overhead** - run directly from source

For production (QEMU/Pi):
- Uses optimized startup without reload
- Limited console output
- Built from customized Debian image

## Architecture

### Backend (FastAPI)

```
main.py                 # FastAPI app + REST endpoints
│
├── player.py           # MPV audio controller
├── stations.py         # Radio Browser API client
├── favorites.py        # JSON favorites storage
├── recent.py           # JSON history storage
├── bluetooth.py        # BlueZ device management
├── websocket.py        # Real-time updates
└── config.py           # Settings persistence
```

### Frontend (Single-Page App)

```
templates/index.html    # HTML + Tailwind CSS + Alpine.js
│
├── Radio controls      # Search, browse, play, volume
├── Bluetooth manager   # Device scan, pair, connect
├── Favorites sidebar   # Quick access to saved stations
└── WebSocket client    # Real-time updates
```

## Tips & Tricks

### Faster development
Don't stop/start the server - just edit and save. Uvicorn auto-reloads.

### Clear cache
Delete `~/.cheeky/` to reset all local data:
```bash
rm -rf ~/.cheeky/
./scripts/run-local.sh
```

### Monitor logs in real-time
Keep the terminal running and watch logs as you interact with the app.

### Test WebSocket
Browser console:
```javascript
ws = new WebSocket('ws://localhost:8000/ws');
ws.onmessage = e => console.log(JSON.parse(e.data));
```

## Contributing

1. Create feature branch: `git checkout -b feature/my-feature`
2. Run locally: `./scripts/run-local.sh`
3. Test thoroughly and check console logs
4. Commit: `git commit -m "Add my feature"`
5. Push: `git push origin feature/my-feature`
6. Create pull request

## Questions?

- Check console logs first (`F12` in browser, terminal output)
- Look at existing API endpoints in `main.py` for examples
- Check frontend code in `templates/index.html` for patterns
- Test with `/api/stations/test` endpoint if Radio Browser API doesn't work

Happy coding! 🍑
