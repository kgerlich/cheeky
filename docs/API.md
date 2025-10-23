# API Documentation

## Bluetooth Manager REST API

The Bluetooth Manager provides a REST API for managing Bluetooth speaker pairing and connections.

**Base URL**: `http://raspberrypi.local:8080/api` (or `http://localhost:8080/api` in QEMU)

### Authentication

Currently, no authentication is required. The API is intended for use on private networks only.

**Security Note**: Do not expose Cheeky to the public internet without adding authentication (planned for v1.1).

---

## Endpoints

### Get All Devices

```
GET /api/devices
```

Returns a list of all paired Bluetooth devices.

**Response** (200 OK):
```json
[
  {
    "mac": "AA:BB:CC:DD:EE:FF",
    "name": "JBL Speaker",
    "connected": true,
    "paired": true,
    "trusted": true
  },
  {
    "mac": "11:22:33:44:55:66",
    "name": "Sony Headphones",
    "connected": false,
    "paired": true,
    "trusted": true
  }
]
```

**Parameters**: None

---

### Scan for Devices

```
POST /api/devices/scan
```

Start scanning for nearby Bluetooth devices. Scan runs for 15 seconds.

**Request Body**: (empty)

**Response** (200 OK):
```json
{
  "status": "scanning",
  "message": "Scanning for 15 seconds...",
  "duration": 15
}
```

The discovered devices become available via `/api/devices/available` endpoint.

---

### Get Available Devices

```
GET /api/devices/available
```

Returns devices found during the last scan.

**Response** (200 OK):
```json
[
  {
    "mac": "AA:BB:CC:DD:EE:FF",
    "name": "Bose Speaker",
    "rssi": -45,
    "class": "Audio Device"
  }
]
```

**Note**: Results are from the most recent scan. Run `/scan` first to refresh.

---

### Pair Device

```
POST /api/devices/pair
```

Pair a new Bluetooth device.

**Request Body**:
```json
{
  "mac": "AA:BB:CC:DD:EE:FF"
}
```

**Response** (200 OK):
```json
{
  "status": "paired",
  "message": "Successfully paired with AA:BB:CC:DD:EE:FF",
  "device": {
    "mac": "AA:BB:CC:DD:EE:FF",
    "name": "JBL Speaker",
    "paired": true,
    "connected": true
  }
}
```

**Error** (400 Bad Request):
```json
{
  "error": "Already paired with this device"
}
```

---

### Connect Device

```
POST /api/devices/connect
```

Connect to a paired Bluetooth device (enable audio output).

**Request Body**:
```json
{
  "mac": "AA:BB:CC:DD:EE:FF"
}
```

**Response** (200 OK):
```json
{
  "status": "connected",
  "message": "Connected to AA:BB:CC:DD:EE:FF",
  "device": {
    "mac": "AA:BB:CC:DD:EE:FF",
    "name": "JBL Speaker",
    "connected": true
  }
}
```

**Error** (404 Not Found):
```json
{
  "error": "Device not found or not paired"
}
```

---

### Disconnect Device

```
POST /api/devices/disconnect
```

Disconnect from a Bluetooth device (disable audio output, but keep pairing).

**Request Body**:
```json
{
  "mac": "AA:BB:CC:DD:EE:FF"
}
```

**Response** (200 OK):
```json
{
  "status": "disconnected",
  "message": "Disconnected from AA:BB:CC:DD:EE:FF",
  "device": {
    "mac": "AA:BB:CC:DD:EE:FF",
    "name": "JBL Speaker",
    "connected": false,
    "paired": true
  }
}
```

---

### Remove Device

```
POST /api/devices/remove
```

Remove a paired Bluetooth device (un-pair).

**Request Body**:
```json
{
  "mac": "AA:BB:CC:DD:EE:FF"
}
```

**Response** (200 OK):
```json
{
  "status": "removed",
  "message": "Removed AA:BB:CC:DD:EE:FF",
  "device": {
    "mac": "AA:BB:CC:DD:EE:FF",
    "name": "JBL Speaker",
    "paired": false
  }
}
```

---

### Get Bluetooth Status

```
GET /api/status
```

Get the Bluetooth adapter status.

**Response** (200 OK):
```json
{
  "powered": true,
  "discoverable": false,
  "pairable": true,
  "version": "5.0",
  "class": "0x0c010c"
}
```

---

## Radio API (Mopidy)

The radio backend uses Mopidy's JSON-RPC API on port 6680.

**Base URL**: `http://raspberrypi.local:6680/mopidy/rpc`

### Using the Mopidy API

The Mopidy API uses JSON-RPC 2.0 protocol. It's pre-configured and doesn't require any setup.

**Example Request** (Get current playback state):
```bash
curl -X POST http://raspberrypi.local:6680/mopidy/rpc \
  -H "Content-Type: application/json" \
  -d '{
    "jsonrpc": "2.0",
    "id": 1,
    "method": "core.playback.get_state",
    "params": {}
  }'
```

**Response**:
```json
{
  "jsonrpc": "2.0",
  "id": 1,
  "result": "playing"
}
```

### Common Mopidy Methods

- `core.library.browse()` - Browse music library
- `core.playback.play()` - Start playback
- `core.playback.pause()` - Pause playback
- `core.playback.stop()` - Stop playback
- `core.tracklist.add()` - Add tracks to queue
- `core.playback.set_volume()` - Set volume (0-100)

See [Mopidy Documentation](https://docs.mopidy.com/) for complete API reference.

---

## Example Usage

### Python

```python
import requests
import json

BASE_URL = "http://raspberrypi.local:8080/api"

# Get all devices
response = requests.get(f"{BASE_URL}/devices")
devices = response.json()
print(f"Found {len(devices)} paired devices")

# Scan for new devices
requests.post(f"{BASE_URL}/devices/scan")

# Pair a device
pair_response = requests.post(
    f"{BASE_URL}/devices/pair",
    json={"mac": "AA:BB:CC:DD:EE:FF"}
)
print(pair_response.json())

# Connect to device
connect_response = requests.post(
    f"{BASE_URL}/devices/connect",
    json={"mac": "AA:BB:CC:DD:EE:FF"}
)
print(connect_response.json())
```

### JavaScript

```javascript
const BASE_URL = "http://raspberrypi.local:8080/api";

// Get all devices
async function getDevices() {
  const response = await fetch(`${BASE_URL}/devices`);
  const devices = await response.json();
  console.log("Devices:", devices);
  return devices;
}

// Connect to device
async function connectDevice(mac) {
  const response = await fetch(`${BASE_URL}/devices/connect`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ mac: mac })
  });
  return await response.json();
}

// Example
getDevices().then(devices => {
  if (devices.length > 0) {
    connectDevice(devices[0].mac);
  }
});
```

### cURL

```bash
# Get devices
curl http://raspberrypi.local:8080/api/devices

# Scan
curl -X POST http://raspberrypi.local:8080/api/devices/scan

# Pair device
curl -X POST http://raspberrypi.local:8080/api/devices/pair \
  -H "Content-Type: application/json" \
  -d '{"mac":"AA:BB:CC:DD:EE:FF"}'

# Connect
curl -X POST http://raspberrypi.local:8080/api/devices/connect \
  -H "Content-Type: application/json" \
  -d '{"mac":"AA:BB:CC:DD:EE:FF"}'
```

---

## Error Handling

All errors return JSON responses with appropriate HTTP status codes:

- **400 Bad Request**: Invalid parameters or malformed JSON
- **404 Not Found**: Device or resource not found
- **500 Internal Server Error**: Server-side error

**Error Response Format**:
```json
{
  "error": "Device not found",
  "details": "No device with MAC AA:BB:CC:DD:EE:FF"
}
```

---

## Rate Limiting

No rate limiting is currently implemented. For v1.1, consider implementing rate limiting to prevent abuse.

---

## CORS

CORS is enabled to allow requests from web pages served on different ports.

---

## Versioning

The API doesn't currently use versioning (all requests go to `/api/`). Future versions may use `/api/v1/`, `/api/v2/`, etc.

---

## Future Enhancements (v1.1+)

- [ ] Authentication via API tokens
- [ ] WebSocket support for real-time updates
- [ ] Rate limiting
- [ ] API versioning
- [ ] More granular device information
- [ ] Volume control per device

---

Questions about the API? [Open an issue](https://github.com/cheeky-radio/cheeky/issues)

🍑 Enjoy building with Cheeky!
