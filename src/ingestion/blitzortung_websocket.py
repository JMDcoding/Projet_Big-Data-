"""
Real-time WebSocket client for Blitzortung lightning data.
Connects to Blitzortung WebSocket server for live strike streaming.
"""
import asyncio
import json
import logging
import threading
from datetime import datetime
from typing import Dict, List, Any, Callable, Optional
from queue import Queue

try:
    import websocket
    HAS_WEBSOCKET = True
except ImportError:
    HAS_WEBSOCKET = False
    websocket = None


class BlitzortungWebSocketClient:
    """Real-time WebSocket client for Blitzortung lightning data."""
    
    def __init__(self, 
                 ws_url: str = "wss://ws.blitzortung.org/ws",
                 buffer_size: int = 100):
        """Initialize Blitzortung WebSocket client.
        
        Args:
            ws_url: WebSocket server URL (Blitzortung endpoint)
            buffer_size: Maximum buffer size for strikes
        """
        if not HAS_WEBSOCKET:
            raise ImportError("websocket-client not installed. Install with: pip install websocket-client")
        
        self.ws_url = ws_url
        self.buffer_size = buffer_size
        self.logger = logging.getLogger(self.__class__.__name__)
        
        # Connection state
        self.is_connected = False
        self.ws = None
        self.thread = None
        self.stop_flag = False
        
        # Data buffer
        self.strike_queue = Queue(maxsize=buffer_size)
        self.strikes_buffer: List[Dict] = []
        
        # Statistics
        self.strikes_received = 0
        self.last_strike_time = None
        self.connection_time = None
    
    def connect(self):
        """Connect to Blitzortung WebSocket server."""
        if self.is_connected:
            self.logger.warning("Already connected")
            return
        
        try:
            self.logger.info(f"Connecting to Blitzortung WebSocket: {self.ws_url}")
            
            # Create WebSocket connection with handlers
            self.ws = websocket.WebSocketApp(
                self.ws_url,
                on_open=self._on_open,
                on_message=self._on_message,
                on_error=self._on_error,
                on_close=self._on_close
            )
            
            # Start WebSocket in separate thread
            self.stop_flag = False
            self.thread = threading.Thread(
                target=self.ws.run_forever,
                kwargs={"ping_interval": 30, "ping_timeout": 10},
                daemon=True
            )
            self.thread.start()
            
            # Wait for connection to establish
            import time
            max_wait = 5
            while not self.is_connected and max_wait > 0:
                time.sleep(0.5)
                max_wait -= 0.5
            
            if self.is_connected:
                self.logger.info("✅ Connected to Blitzortung WebSocket")
                self.connection_time = datetime.now()
            else:
                self.logger.error("❌ Failed to connect to Blitzortung WebSocket")
        
        except Exception as e:
            self.logger.error(f"Connection error: {str(e)}")
            self.is_connected = False
    
    def disconnect(self):
        """Disconnect from WebSocket server."""
        if not self.is_connected:
            return
        
        try:
            self.logger.info("Disconnecting from Blitzortung WebSocket...")
            self.stop_flag = True
            
            if self.ws:
                self.ws.close()
            
            if self.thread:
                self.thread.join(timeout=5)
            
            self.is_connected = False
            self.logger.info("✅ Disconnected from Blitzortung WebSocket")
        
        except Exception as e:
            self.logger.error(f"Disconnection error: {str(e)}")
    
    def get_strikes(self, clear: bool = True) -> List[Dict]:
        """Get accumulated lightning strikes from buffer.
        
        Args:
            clear: Whether to clear buffer after retrieval
            
        Returns:
            List of lightning strikes
        """
        strikes = list(self.strikes_buffer)
        
        if clear:
            self.strikes_buffer.clear()
        
        return strikes
    
    def get_latest_strike(self) -> Optional[Dict]:
        """Get the most recent lightning strike.
        
        Returns:
            Latest strike dictionary or None
        """
        return self.strikes_buffer[-1] if self.strikes_buffer else None
    
    def get_status(self) -> Dict[str, Any]:
        """Get WebSocket client status.
        
        Returns:
            Status dictionary
        """
        uptime = None
        if self.connection_time:
            uptime = (datetime.now() - self.connection_time).total_seconds()
        
        return {
            "is_connected": self.is_connected,
            "strikes_received": self.strikes_received,
            "buffer_size": len(self.strikes_buffer),
            "last_strike": self.last_strike_time,
            "uptime_seconds": uptime
        }
    
    # Private WebSocket handlers
    def _on_open(self, ws):
        """Handler for WebSocket connection opened."""
        self.is_connected = True
        self.logger.info("WebSocket connection opened")
    
    def _on_message(self, ws, message: str):
        """Handler for incoming WebSocket messages.
        
        Args:
            ws: WebSocket instance
            message: Message data
        """
        try:
            # Parse JSON message from Blitzortung
            data = json.loads(message)
            
            # Extract strike data (format may vary)
            if "strike" in data:
                strike = data["strike"]
            elif isinstance(data, dict) and "lat" in data and "lon" in data:
                strike = data
            else:
                strike = data
            
            # Normalize strike data
            normalized_strike = {
                "latitude": strike.get("lat", strike.get("latitude", 0)),
                "longitude": strike.get("lon", strike.get("longitude", 0)),
                "altitude": strike.get("altitude", strike.get("alt", 0)),
                "intensity": strike.get("intensity", strike.get("power", 0)),
                "timestamp": strike.get("timestamp", datetime.now().isoformat()),
                "source": "blitzortung_websocket"
            }
            
            # Add to buffer
            if len(self.strikes_buffer) >= self.buffer_size:
                self.strikes_buffer.pop(0)  # Remove oldest
            
            self.strikes_buffer.append(normalized_strike)
            self.strikes_received += 1
            self.last_strike_time = datetime.now()
            
            # Log every 10 strikes
            if self.strikes_received % 10 == 0:
                self.logger.debug(
                    f"Received {self.strikes_received} strikes | "
                    f"Buffer: {len(self.strikes_buffer)}/{self.buffer_size}"
                )
        
        except json.JSONDecodeError:
            self.logger.warning(f"Invalid JSON message: {message[:100]}")
        except Exception as e:
            self.logger.error(f"Error processing message: {str(e)}")
    
    def _on_error(self, ws, error: Exception):
        """Handler for WebSocket errors.
        
        Args:
            ws: WebSocket instance
            error: Error exception
        """
        self.logger.error(f"WebSocket error: {str(error)}")
    
    def _on_close(self, ws, close_status_code, close_msg):
        """Handler for WebSocket connection closed.
        
        Args:
            ws: WebSocket instance
            close_status_code: Close code
            close_msg: Close message
        """
        self.is_connected = False
        self.logger.info(
            f"WebSocket connection closed "
            f"(code: {close_status_code}, msg: {close_msg})"
        )


class BlitzortungWebSocketDataSource:
    """Asynchronous data source wrapper for Blitzortung WebSocket."""
    
    def __init__(self, ws_url: str = "wss://ws.blitzortung.org/ws"):
        """Initialize data source.
        
        Args:
            ws_url: WebSocket server URL
        """
        self.logger = logging.getLogger(self.__class__.__name__)
        self.client = BlitzortungWebSocketClient(ws_url=ws_url)
        self.auto_reconnect = True
    
    def start(self):
        """Start the WebSocket client and listening."""
        try:
            self.client.connect()
            self.logger.info("Blitzortung WebSocket data source started")
        except Exception as e:
            self.logger.error(f"Failed to start WebSocket: {str(e)}")
    
    def stop(self):
        """Stop the WebSocket client."""
        self.client.disconnect()
        self.logger.info("Blitzortung WebSocket data source stopped")
    
    def fetch(self) -> Dict[str, Any]:
        """Get accumulated lightning strikes.
        
        Returns:
            Dictionary with strikes data
        """
        strikes = self.client.get_strikes(clear=True)
        
        return {
            "strikes": strikes,
            "source": "blitzortung_websocket",
            "timestamp": datetime.now().isoformat(),
            "count": len(strikes),
            "status": self.client.get_status()
        }
    
    def is_connected(self) -> bool:
        """Check if WebSocket is connected.
        
        Returns:
            True if connected
        """
        return self.client.is_connected
