"""
Main FastAPI entry point.
"""
import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
import sys
import os
# Ensure the backend directory is in the path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.config import settings

# Routers
from app.routers import (
    auth, dashboard, campaigns, calls, agents, billing, admin,
    contacts, settings as settings_router, marketing, websocket, test_voice
)

logging.basicConfig(level=getattr(logging, settings.LOG_LEVEL.upper()))
logger = logging.getLogger(settings.APP_NAME)


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: Connect to DB, Redis, etc.
    logger.info("Starting Beraxis API...")
    
    # Connect to Telephony (Asterisk ARI)
    try:
        from app.telephony.router import telephony_router
        asterisk = telephony_router.get_provider("asterisk")
        # Connect is an async task that runs in the background
        await asterisk.connect()
        logger.info("Connected to Asterisk ARI (Telephony Ready)")
        
        # Log network access info
        import socket
        hostname = socket.gethostname()
        local_ip = socket.gethostbyname(hostname)
        logger.info(f"API is accessible on local network via: http://{local_ip}:8000")
        logger.info(f"Documentation: http://{local_ip}:8000/docs")
        
    except Exception as e:
        logger.error(f"Failed to connect to Asterisk ARI: {e}")

    yield
    # Shutdown: Cleanup connections
    logger.info("Shutting down Beraxis API...")


app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url=None,
)

# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount Routers
# NOTE: Using consistent `/api/v1` prefix for REST routes
api_prefix = settings.API_PREFIX
app.include_router(auth.router, prefix=api_prefix)
app.include_router(dashboard.router, prefix=api_prefix)
app.include_router(campaigns.router, prefix=api_prefix)
# leads routes are handled within campaigns or contacts, but we can mount explicit leads router if needed
app.include_router(calls.router, prefix=api_prefix)
app.include_router(agents.router, prefix=api_prefix)
app.include_router(contacts.router, prefix=api_prefix)
app.include_router(billing.router, prefix=api_prefix)
app.include_router(admin.router, prefix=api_prefix)
app.include_router(settings_router.router, prefix=api_prefix)
app.include_router(marketing.router, prefix=api_prefix)

# Mount WebSocket router without API prefix since it uses /ws/...
app.include_router(websocket.router)

# Voice test (browser-based AI voice demo)
app.include_router(test_voice.router)


@app.get("/health", tags=["Health"])
async def health_check():
    """Basic health check endpoint."""
    return {"success": True, "data": {"status": "healthy", "version": settings.APP_VERSION}}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=settings.DEBUG)
