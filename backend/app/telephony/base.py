from abc import ABC, abstractmethod
from typing import Callable, Any, Dict, Optional
import logging

logger = logging.getLogger(__name__)

class BaseTelephonyProvider(ABC):
    """
    Abstract Base Class for Telephony Providers.
    Allows Beraxis to swap between Asterisk, Twilio, or Custom Dialers.
    """

    def __init__(self):
        self.on_audio_cb: Optional[Callable[[bytes], Any]] = None
        self.on_event_cb: Optional[Callable[[str, Dict[str, Any]], Any]] = None

    @abstractmethod
    async def make_call(self, to_number: str, lead_id: str, campaign_id: str) -> str:
        """
        Initiates an outbound call.
        Returns a unique call_id (Provider-specific).
        """
        pass

    @abstractmethod
    async def hangup(self, call_id: str):
        """Terminates an active call."""
        pass

    @abstractmethod
    async def send_audio(self, call_id: str, audio_bytes: bytes):
        """Streams audio to the caller."""
        pass

    def set_on_audio_received(self, callback: Callable[[bytes], Any]):
        """Callback for when user audio is received from the provider."""
        self.on_audio_cb = callback

    def set_on_event(self, callback: Callable[[str, Dict[str, Any]], Any]):
        """Callback for call events (ringing, answered, hangup, dtmf)."""
        self.on_event_cb = callback

    async def _handle_incoming_audio(self, audio_bytes: bytes):
        if self.on_audio_cb:
            await self.on_audio_cb(audio_bytes)

    async def _handle_event(self, event_type: str, data: Dict[str, Any]):
        if self.on_event_cb:
            await self.on_event_cb(event_type, data)
