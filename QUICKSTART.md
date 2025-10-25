# 🍑 Cheeky - Quick Start Guide

## Local Development (5 minutes)

### 1. First Time Setup
```bash
cd ~/dev/cheeky
./scripts/setup-local.sh
```

This installs everything you need. Takes ~5-10 minutes depending on internet speed.

### 2. Run the App
```bash
./scripts/run-local.sh
```

You'll see:
```
═════════════════════════════════════════════
Access the application:
  🌐 http://localhost:8000

Press Ctrl+C to stop the server
═════════════════════════════════════════════

[Cheeky] Radio Player ready!
```

### 3. Open in Browser
- **Main App**: http://localhost:8000
- **Browser Console** (F12): Check for `[Cheeky]` log messages
- **API Test**: http://localhost:8000/api/stations/test

That's it! The app auto-reloads when you edit code.

## What You Get

✅ **Radio Player** on port 8000
- Search 100,000+ radio stations
- Play/pause/stop controls
- Volume control (persistent)
- Save favorite stations
- Recently played tracking

✅ **Bluetooth Manager** integrated
- Scan for Bluetooth devices
- Pair/connect/disconnect speakers
- Device status monitoring

✅ **Auto-reload** on code changes
- Edit Python files → saves instantly
- Edit HTML/CSS → refresh browser
- Check console for errors

✅ **Detailed Logging**
- Look for `[Cheeky]` messages in console
- All API calls logged
- WebSocket connection status shown

## File Structure

```
config/radio-player/
├── main.py              ← FastAPI entry point
├── backend/
│   ├── player.py        ← Audio playback
│   ├── stations.py      ← Radio API
│   ├── bluetooth.py     ← Bluetooth control
│   └── ...other modules
└── templates/
    └── index.html       ← Web UI
```

## Editing Code

### Backend (Python)
Edit files in `config/radio-player/backend/` then refresh the browser. Uvicorn auto-reloads.

### Frontend (HTML/CSS/JavaScript)
Edit `config/radio-player/templates/index.html` then refresh browser (F5).

### Debug with Logs
```javascript
// In browser console (F12)
// All API calls are logged as [Cheeky]
fetch('/api/stations/test').then(r => r.json()).then(d => console.log(d))
```

## Common Tasks

### Stop the Server
Press `Ctrl+C` in the terminal running `./scripts/run-local.sh`

### Clear Local Data
```bash
rm -rf ~/.cheeky/
```
This resets favorites and settings to defaults.

### Use Different Port
```bash
cd config/radio-player
python3 -m uvicorn main:app --port 8001
```

### Check What's Running
```bash
curl http://localhost:8000/health
```

## Troubleshooting

### "Module not found" error
Run setup again:
```bash
./scripts/setup-local.sh
```

### "Port 8000 already in use"
Kill existing process:
```bash
lsof -i :8000
kill -9 <PID>
```

### "No stations loading"
1. Check browser console (F12) for errors
2. Try test endpoint: `http://localhost:8000/api/stations/test`
3. Check internet connection

### "Bluetooth not working"
Bluetooth is simulated via API. Full support requires BlueZ on Linux.

## Building for Release

Once you're happy:

```bash
# 1. Commit your changes
git add -A
git commit -m "Your change description"
git push origin main

# 2. Create a release tag
git tag -a v1.2.0 -m "Release v1.2.0"
git push origin v1.2.0

# 3. GitHub Actions automatically builds everything!
```

Then download from: https://github.com/kgerlich/cheeky/releases

## Next Steps

- 📖 Read `DEVELOPMENT.md` for detailed guide
- 🐛 Check `DEVELOPMENT.md` Troubleshooting section
- 🔍 Look at existing code in `backend/` for patterns
- 💬 Check logs with `[Cheeky]` prefix

## Running Both Locally AND on QEMU

You can have both running:

1. **Local**: `./scripts/run-local.sh` (port 8000)
2. **QEMU**: Download from releases, extract and run `./start-qemu.sh` (port 80)

Perfect for comparing behavior!

---

**Happy coding!** 🍑

Questions? Check the logs first - they tell you everything!
