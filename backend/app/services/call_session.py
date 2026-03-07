import logging
import asyncio
from typing import Dict, Any, Optional
from app.telephony.router import telephony_router
from app.ai.pipeline import ai_pipeline  # Assuming this exists from previous setups
from app.telephony.base import BaseTelephonyProvider

logger = logging.getLogger(__name__)

class CallSessionManager:
    """
    Orchestrates the lifecycle of a call session.
    Links the Telephony Provider (Audio In/Out) to the AI Pipeline.
    """

    def __init__(self):
        self.active_sessions: Dict[str, Dict[str, Any]] = {}

    async def start_session(self, call_id: str, provider_name: str, lead_id: str):
        """
        Initializes a new AI call session.
        Sets up audio callbacks to feed the AI pipeline.
        """
        provider = telephony_router.get_provider(provider_name)
        
        # 1. Setup session state
        self.active_sessions[call_id] = {
            "provider": provider,
            "lead_id": lead_id,
            "status": "active"
        }

        # 2. Define Audio Callback (Telephony -> AI)
        async def on_audio_received(audio_chunk: bytes):
            # Send telephony audio into AI STT
            await ai_pipeline.process_audio_input(call_id, audio_chunk)

        provider.set_on_audio_received(on_audio_received)

        # 3. Define AI Output Callback (AI -> Telephony)
        async def on_ai_response(response_audio: bytes):
            # Send AI generated audio back to Telephony
            await provider.send_audio(call_id, response_audio)

        # Hook into AI pipeline events
        ai_pipeline.set_on_output(call_id, on_ai_response)
        
        logger.info(f"AI Call Session Started: {call_id} using {provider_name}")

    async def end_session(self, call_id: str):
        """Clean up session resources."""
        if call_id in self.active_sessions:
            session = self.active_sessions[call_id]
            provider = session["provider"]
            await provider.hangup(call_id)
            del self.active_sessions[call_id]
            logger.info(f"AI Call Session Ended: {call_id}")

# Global instance
call_session_manager = CallSessionManager()
