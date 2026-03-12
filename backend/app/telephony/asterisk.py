import asyncio
import json
import logging
import uuid
import socket
import struct
from typing import Dict, Any, Optional, Callable
import httpx
import websockets
from .base import BaseTelephonyProvider
from app.config import settings

logger = logging.getLogger(__name__)

# AudioSocket Header: 3 bytes
# Type (1 byte): 0x01 (Signed Linear 16-bit, 8kHz, mono)
# Length (2 bytes, big-endian)
AUDIOSOCKET_TYPE_PCM = 0x01
AUDIOSOCKET_HANGUP = 0x00

class AsteriskProvider(BaseTelephonyProvider):
    """
    Asterisk implementation using ARI + AudioSocket.
    - ARI: Call control (Dial, Hangup, Events)
    - AudioSocket: Low-latency raw audio streaming (TCP)
    """

    def __init__(self):
        super().__init__()
        self.base_url = f"http://{settings.ASTERISK_HOST}:{settings.ASTERISK_ARI_PORT}/ari"
        self.ws_url = f"ws://{settings.ASTERISK_HOST}:{settings.ASTERISK_ARI_PORT}/ari/events"
        self.auth = (settings.ASTERISK_ARI_USER, settings.ASTERISK_ARI_PASS)
        self.app_name = settings.ASTERISK_ARI_APP
        
        self.active_channels: Dict[str, str] = {} # call_id -> channel_id
        self.audio_connections: Dict[str, asyncio.StreamWriter] = {} # channel_id -> writer
        self._ws_task: Optional[asyncio.Task] = None
        self._server: Optional[asyncio.Server] = None

    async def connect(self):
        """Starts the WebSocket event listener and AudioSocket server."""
        if self._ws_task:
            return
        
        # 1. Start ARI Event Listener
        logger.info(f"Connecting to Asterisk ARI at {self.base_url} (WS: {self.ws_url})")
        self._ws_task = asyncio.create_task(self._listen_events())
        
        # 2. Start AudioSocket TCP Server (Listeners for incoming audio from Asterisk)
        # Port 9092 is standard for AudioSocket
        self._server = await asyncio.start_server(
            self._handle_audiosocket_connection, '0.0.0.0', 9092
        )
        logger.info(f"AudioSocket server listening on 0.0.0.0:9092")
        logger.info(f"Connected to Asterisk ARI events (App: {self.app_name})")

    async def _handle_audiosocket_connection(self, reader: asyncio.StreamReader, writer: asyncio.StreamWriter):
        """Processes a new TCP connection from an Asterisk AudioSocket."""
        peer = writer.get_extra_info('peername')
        logger.info(f"New AudioSocket connection from {peer}")
        
        try:
            # First 16 bytes is the UUID from Asterisk
            # Use a timeout to avoid hanging if Asterisk sends less than 16 bytes
            raw_id = await asyncio.wait_for(reader.read(16), timeout=5.0)
            
            # Try to parse as UUID, if not use as raw string key
            try:
                channel_id = str(uuid.UUID(bytes=raw_id))
            except:
                channel_id = raw_id.decode('ascii', errors='ignore').strip()
            
            logger.info(f"AudioSocket matched to channel: {channel_id}")
            
            self.audio_connections[channel_id] = writer
            
            # Read loop
            while True:
                header = await reader.readexactly(3)
                msg_type = int(header[0])
                msg_len = struct.unpack('>H', header[1:3])[0]
                
                if msg_type == AUDIOSOCKET_HANGUP:
                    break
                
                payload = await reader.readexactly(msg_len)
                if msg_type == AUDIOSOCKET_TYPE_PCM:
                    # Pass raw PCM to AI Pipeline
                    if self.on_audio_cb:
                        res = self.on_audio_cb(payload)
                        if asyncio.iscoroutine(res):
                            await res
                        
        except Exception as e:
            logger.debug(f"AudioSocket session ended for {peer}: {e}")
        finally:
            writer.close()
            try:
                await writer.wait_closed()
            except:
                pass

    async def _listen_events(self):
        """Websocket listener for ARI events."""
        params = f"api_key={self.auth[0]}:{self.auth[1]}&app={self.app_name}"
        url = f"{self.ws_url}?{params}"
        while True:
            try:
                async with websockets.connect(url) as ws:
                    logger.info("Asterisk ARI WebSocket connected")
                    async for message in ws:
                        await self._process_event(json.loads(message))
            except Exception as e:
                logger.error(f"Asterisk WS connection lost: {e}. Retrying in 5s...")
                await asyncio.sleep(5)

    async def _process_event(self, event: Dict[str, Any]):
        event_type = event.get("type")
        channel = event.get("channel", {})
        channel_id = channel.get("id")

        if event_type == "StasisStart":
            logger.info(f"Channel {channel_id} entered Stasis. Logic: {event.get('args')}")
            
            # If this is an outbound call we initiated via ARI, 
            # we need to redirect it to the AudioSocket dialplan (default,100,1)
            # to start the audio flow.
            # StasisStart args usually contains our custom identifier if we passed it.
            
            await self._redirect_to_audiosocket(channel_id)
            await self._handle_event("answered", {"channel_id": channel_id})
        
        elif event_type == "StasisEnd":
            self.audio_connections.pop(channel_id, None)
            await self._handle_event("hangup", {"channel_id": channel_id})

    async def _handle_event(self, event_type: str, data: Dict[str, Any]):
        if self.on_event_cb:
            res = self.on_event_cb(event_type, data)
            if asyncio.iscoroutine(res):
                await res

    async def make_call(self, to_number: str, lead_id: str, campaign_id: str) -> str:
        url = f"{self.base_url}/channels"
        # For outbound, we can use the AudioSocket as the endpoint bridge
        # But usually we dial the SIP endpoint first, then bridge to AudioSocket in dialplan or ARI
        data = {
            "endpoint": f"PJSIP/{to_number}@{settings.SIP_TRUNK_HOST}",
            "app": self.app_name,
            "callerId": settings.OUTBOUND_CALLER_ID
        }
        async with httpx.AsyncClient() as client:
            resp = await client.post(url, auth=self.auth, json=data)
            resp.raise_for_status()
            cid = resp.json()["id"]
            return str(cid)

    async def hangup(self, call_id: str):
        url = f"{self.base_url}/channels/{call_id}"
        async with httpx.AsyncClient() as client:
            await client.delete(url, auth=self.auth)

    async def _redirect_to_audiosocket(self, channel_id: str):
        """Redirects a channel to the dialplan that starts AudioSocket."""
        url = f"{self.base_url}/channels/{channel_id}/continue"
        data = {
            "context": "default",
            "extension": "100",
            "priority": 1
        }
        async with httpx.AsyncClient() as client:
            try:
                resp = await client.post(url, auth=self.auth, json=data)
                resp.raise_for_status()
                logger.info(f"Redirected channel {channel_id} to AudioSocket dialplan.")
            except Exception as e:
                logger.error(f"Failed to redirect channel {channel_id}: {e}")

    async def send_audio(self, call_id: str, audio_bytes: bytes):
        """Sends audio to Asterisk via the TCP socket."""
        writer = self.audio_connections.get(call_id)
        if writer:
            # Wrap in AudioSocket header
            header = struct.pack('>BH', AUDIOSOCKET_TYPE_PCM, len(audio_bytes))
            writer.write(header + audio_bytes)
            await writer.drain()
