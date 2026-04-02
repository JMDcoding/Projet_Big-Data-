# Blitzortung WebSocket Real-Time Lightning Data

## Overview

This implementation enables **real-time lightning strike data** from Blitzortung using WebSocket connections instead of periodic HTTP polling.

## Features

✅ **Real-time Data**: Receive lightning strikes as they happen (not polling)  
✅ **Low Latency**: Instant updates via WebSocket  
✅ **Automatic Sync**: Strikes automatically saved to PostgreSQL  
✅ **Fallback Support**: Falls back to HTTP if WebSocket unavailable  
✅ **Background Thread**: Runs independently of main pipeline  

## Architecture

```
Blitzortung WebSocket Server (wss://ws.blitzortung.org/ws)
            ↓
    WebSocket Client
            ↓
    Strike Buffer (Queue)
            ↓
    Database Sync Thread
            ↓
PostgreSQL lightning table
```

## Installation

Install the required WebSocket client:

```bash
pip install websocket-client>=1.0.0
```

Or update dependencies:

```bash
pip install -r requirements.txt
```

## Usage

### 1. **WebSocket Lightning Monitor** (Real-time Listener)

```bash
python blitzortung_websocket_demo.py
```

Output:
```
⚡ BLITZORTUNG WEBSOCKET REAL-TIME LIGHTNING MONITOR
✅ WebSocket connected!

📊 Real-time lightning strike stream:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
⚡ NEW STRIKES RECEIVED: 3
   🧲 Strike @ (48.42, 7.89) | Intensity: 45.2 | Time: 2026-04-02T15:30:45
   🧲 Strike @ (49.12, 8.56) | Intensity: 52.1 | Time: 2026-04-02T15:30:46
   🧲 Strike @ (47.98, 6.34) | Intensity: 38.9 | Time: 2026-04-02T15:30:47
```

### 2. **Enhanced Refresh Service** (WebSocket + Periodic Polling)

```bash
python enhanced_refresh_demo.py
```

Output:
```
⚡ ENHANCED REFRESH SERVICE - WebSocket Lightning + Polling Flights

📊 DATA SOURCES:
   • Lightning: Blitzortung WebSocket (real-time)
   • Flights: AviationStack API (every 5 minutes)

✅ Service started successfully!

📈 SERVICE STATUS:
   ✓ Running: True
   ✓ WebSocket Lightning: True
   ✓ WebSocket Connected: True
   ✓ Strikes Received: 156
   ✓ Strikes Processed: 156
```

### 3. **Dashboard with WebSocket** (Streamlit)

```bash
streamlit run app.py
```

The dashboard automatically initializes the refresh service.

## Code Examples

### Basic Usage

```python
from src.ingestion.blitzortung_websocket import BlitzortungWebSocketDataSource

# Create data source
ws_source = BlitzortungWebSocketDataSource()

# Start listening
ws_source.start()

# Get accumulated strikes
data = ws_source.fetch()
strikes = data['strikes']

# Stop when done
ws_source.stop()
```

### With Database Integration

```python
from src.utils.enhanced_refresh_service import get_enhanced_refresh_service

# Initialize service
service = get_enhanced_refresh_service(use_websocket=True)

# Start (connects WebSocket + schedules flight polling)
service.start()

# Get status
status = service.get_status()
print(f"Strikes processed: {status['websocket_strikes_processed']}")

# Stop service
service.stop()
```

### Advanced: Custom Handler

```python
from src.ingestion.blitzortung_websocket import BlitzortungWebSocketClient

client = BlitzortungWebSocketClient()
client.connect()

# Strikes are automatically buffered and accessible
while client.is_connected:
    strikes = client.get_strikes(clear=True)
    if strikes:
        print(f"Received {len(strikes)} strikes")
    
    time.sleep(1)

client.disconnect()
```

## Configuration

### WebSocket Server URL

Default: `wss://ws.blitzortung.org/ws`

To use a different endpoint:

```python
ws_source = BlitzortungWebSocketDataSource(
    ws_url="wss://custom.endpoint.org/ws"
)
```

### Buffer Size

Default: 100 strikes

```python
client = BlitzortungWebSocketClient(
    buffer_size=500  # Increase for more buffering
)
```

### Refresh Intervals

Enhanced service defaults:
- **Lightning**: Real-time (WebSocket)
- **Flights**: Every 5 minutes
- **Database Sync**: Every 2 seconds

To modify in `enhanced_refresh_service.py`:

```python
# Change flights polling interval
self.scheduler.add_job(
    self._refresh_flights_data,
    IntervalTrigger(minutes=10),  # Change to 10 minutes
    ...
)
```

## WebSocket Messages

Messages from Blitzortung contain lightning strike data:

```json
{
  "strike": {
    "lat": 48.42,
    "lon": 7.89,
    "altitude": 8500,
    "intensity": 45.2,
    "timestamp": "2026-04-02T15:30:45Z"
  }
}
```

Supported message formats:
- `{"strike": {...}}` - Full strike object
- `{"lat": ..., "lon": ..., ...}` - Inline coordinates
- Any format with `lat`/`lon`/`latitude`/`longitude` keys

## Status Monitoring

Check WebSocket health:

```python
client = BlitzortungWebSocketClient()
client.connect()

status = client.get_status()
# {
#   'is_connected': True,
#   'strikes_received': 156,
#   'buffer_size': 42,
#   'last_strike': datetime(...),
#   'uptime_seconds': 1234.5
# }
```

## Troubleshooting

### WebSocket Connection Failed

```
❌ Failed to connect to Blitzortung WebSocket
```

**Solutions:**
- Check internet connection
- Verify firewall allows WebSocket (port 443)
- Check if Blitzortung servers are online: https://www.blitzortung.org
- Try the HTTP fallback (disables WebSocket)

### No Strikes Received

- Wait for actual lightning in your region
- Check if Blitzortung has coverage in your area: https://www.blitzortung.org/fr/cover_your_area.php
- Monitor the buffer size in status

### Memory Usage High

Reduce buffer size:

```python
client = BlitzortungWebSocketClient(buffer_size=50)
```

## Performance

**Expected Throughput:**
- 10-50 strikes/minute during storms
- 1-5 strikes/minute during fair weather
- Network bandwidth: ~1 KB per strike

**Latency:**
- WebSocket: <100ms (real-time)
- HTTP polling: 5-60 seconds (interval-based)

## Database Schema

Strikes are stored in `lightning` table:

```sql
CREATE TABLE lightning (
    id SERIAL PRIMARY KEY,
    latitude FLOAT,
    longitude FLOAT,
    altitude FLOAT,
    intensity FLOAT,
    timestamp TIMESTAMP,
    source VARCHAR(50),
    created_at TIMESTAMP DEFAULT NOW()
);
```

## Integration with Pipeline

The enhanced refresh service automatically:
1. ✓ Connects to Blitzortung WebSocket
2. ✓ Buffers incoming strikes
3. ✓ Syncs every 2 seconds to PostgreSQL
4. ✓ Polls flights every 5 minutes
5. ✓ Calculates disruptions
6. ✓ Stores in MinIO + PostgreSQL

## Files

- `src/ingestion/blitzortung_websocket.py` - WebSocket client implementation
- `src/utils/enhanced_refresh_service.py` - Enhanced refresh service with WebSocket
- `blitzortung_websocket_demo.py` - Real-time strike monitor demo
- `enhanced_refresh_demo.py` - Full service demo

## References

- Blitzortung Website: https://www.blitzortung.org
- Coverage Map: https://www.blitzortung.org/fr/cover_your_area.php
- WebSocket Documentation: https://websocket-client-py.readthedocs.io

---

**Version:** 1.0  
**Last Updated:** April 2, 2026
