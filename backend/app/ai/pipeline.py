"""
AI Pipeline Orchestrator.
Connects STT -> LLM -> TTS in a streaming chain.
Handles conversation memory, interruptions, and websocket emission.
"""
import asyncio
from typing import AsyncGenerator, Dict, List
from app.ai.stt import transcribe_stream
from app.ai.llm import stream_response
from app.ai.tts import generate_speech_stream
from app.routers.websocket import emit_call_event
from app.models.agent import AIAgent

class CallSession:
    """Manages state for a single active call."""
    def __init__(self, call_id: str, agent: AIAgent):
        self.call_id = call_id
        self.agent = agent
        self.history: List[Dict[str, str]] = []
        # Push initial greeting if defined
        if agent.flow_steps and len(agent.flow_steps) > 0:
            greeting = agent.flow_steps[0].get("content", "Hello?")
            # Format variables
            # in real app, replace {{first_name}} with lead data here
            self.initial_greeting = greeting
        else:
            self.initial_greeting = "Hello?"

        self.audio_out_queue = asyncio.Queue()
        self.interrupted = False

    async def handle_user_audio(self, audio_chunks: AsyncGenerator[bytes, None]):
        """Consumes raw audio chunks from Asterisk -> STT -> LLM -> TTS"""
        
        # 1. Pipe audio to Faster-Whisper
        async for user_text in transcribe_stream(audio_chunks):
            # STT gave us a piece of text
            
            # Emit to dashboard/frontend
            await emit_call_event(self.call_id, "transcript_final", {"speaker": "user", "text": user_text})
            
            # Interrupt any playing agent audio
            self.interrupted = True
            
            # 2. Get LLM response stream
            llm_text_stream = stream_response(
                system_prompt=self.agent.system_prompt or "",
                conversation_history=self.history,
                user_message=user_text,
                temperature=self.agent.llm_temperature
            )
            
            # Reset interrupt flag for the new generation
            self.interrupted = False
            full_ai_response_chunks = []
            
            # Wrapper to intercept text chunks, save them, and emit ws events
            async def intercepted_text_stream():
                async for text_chunk in llm_text_stream:
                    if self.interrupted:
                        break
                    full_ai_response_chunks.append(text_chunk)
                    await emit_call_event(self.call_id, "transcript_partial", {"speaker": "ai", "text": text_chunk})
                    yield text_chunk

            # 3. Pipe LLM text stream to Piper TTS
            audio_out_stream = generate_speech_stream(
                intercepted_text_stream(),
                voice_id=self.agent.voice_id
            )
            
            # 4. Push generated audio chunks to out-queue for Asterisk
            async for audio_chunk in audio_out_stream:
                if self.interrupted:
                    break
                await self.audio_out_queue.put(audio_chunk)
                
            # Finalize transcript in history
            self.history.append({"speaker": "user", "text": user_text})
            full_ai_response = "".join(full_ai_response_chunks)
            if full_ai_response:
                self.history.append({"speaker": "ai", "text": full_ai_response})
                await emit_call_event(self.call_id, "transcript_final", {"speaker": "ai", "text": full_ai_response})

    async def get_audio_out_stream(self) -> AsyncGenerator[bytes, None]:
        """Asterisk pulls from this to play audio to caller."""
        # Yield the initial greeting synthesized audio first
        # (Mocking simple string to stream conversion here)
        async def initial_text():
            yield self.initial_greeting
            
        initial_audio = generate_speech_stream(initial_text(), self.agent.voice_id)
        async for chunk in initial_audio:
            yield chunk
            
        self.history.append({"speaker": "ai", "text": self.initial_greeting})
        await emit_call_event(self.call_id, "transcript_final", {"speaker": "ai", "text": self.initial_greeting})

        # Then loop forever pulling from the queue (interactive part)
        while True:
            chunk = await self.audio_out_queue.get()
            if chunk is None:  # Sentinel to close
                break
            if isinstance(chunk, bytes):
                yield chunk


class AIPipeline:
    """
    Orchestrates multiple CallSessions.
    This is the main entry point for the Telephony Provider to interact with AI.
    """
    def __init__(self):
        self.sessions: Dict[str, CallSession] = {}
        self._output_callbacks: Dict[str, Callable] = {}
        self._input_queues: Dict[str, asyncio.Queue] = {}

    async def create_session(self, call_id: str, agent: AIAgent):
        session = CallSession(call_id, agent)
        self.sessions[call_id] = session
        
        # Create an input queue for this session's STT
        queue = asyncio.Queue()
        self._input_queues[call_id] = queue

        # Start the processing loop in the background
        async def input_gen():
            while True:
                chunk = await queue.get()
                if chunk is None: break
                yield chunk

        # Run the AI logic (STT -> LLM -> TTS)
        asyncio.create_task(session.handle_user_audio(input_gen()))
        
        # Run the output loop (AI -> Provider)
        async def output_loop():
            async for audio_chunk in session.get_audio_out_stream():
                callback = self._output_callbacks.get(call_id)
                if callback:
                    if asyncio.iscoroutinefunction(callback):
                        await callback(audio_chunk)
                    else:
                        callback(audio_chunk)
        
        asyncio.create_task(output_loop())

    async def process_audio_input(self, call_id: str, audio_chunk: bytes):
        """Called by Telephony Provider when new user audio arrives."""
        queue = self._input_queues.get(call_id)
        if queue:
            await queue.put(audio_chunk)

    def set_on_output(self, call_id: str, callback: Callable):
        """Called by CallSessionManager to hook back to Telephony Provider."""
        self._output_callbacks[call_id] = callback

    async def end_session(self, call_id: str):
        queue = self._input_queues.pop(call_id, None)
        if queue:
            await queue.put(None) # Signal end
        self.sessions.pop(call_id, None)
        self._output_callbacks.pop(call_id, None)

# Global Instance
ai_pipeline = AIPipeline()
from typing import Callable
