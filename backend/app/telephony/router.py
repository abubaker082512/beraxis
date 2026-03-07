import logging
from typing import Dict, Optional, Type
from .base import BaseTelephonyProvider
from .asterisk import AsteriskProvider

logger = logging.getLogger(__name__)

class TelephonyRouter:
    """
    Dynamically routes calls to the appropriate Telephony Provider.
    Supports Asterisk by default, with extensibility for Twilio, VAPI, etc.
    """

    def __init__(self):
        self._providers: Dict[str, BaseTelephonyProvider] = {}
        # Register default native provider
        self.register_provider("asterisk", AsteriskProvider())

    def register_provider(self, name: str, provider: BaseTelephonyProvider):
        self._providers[name.lower()] = provider
        logger.info(f"Telephony Provider Registered: {name}")

    def get_provider(self, name: str = "asterisk") -> BaseTelephonyProvider:
        """Retrieves a provider by name, defaults to Asterisk."""
        provider = self._providers.get(name.lower())
        if not provider:
            logger.warning(f"Provider {name} not found, falling back to Asterisk")
            return self._providers["asterisk"]
        return provider

# Global instance
telephony_router = TelephonyRouter()
