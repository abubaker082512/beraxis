"""
Beraxis AI Calling Platform — Centralized Configuration
All settings loaded from environment variables via pydantic-settings.
"""
from functools import lru_cache
from typing import List, Optional
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import AnyHttpUrl, field_validator


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # ── Application ──────────────────────────────────────────
    APP_NAME: str = "Beraxis"
    APP_ENV: str = "development"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = False
    LOG_LEVEL: str = "info"

    # ── API ──────────────────────────────────────────────────
    API_HOST: str = "0.0.0.0"
    API_PORT: int = 8000
    API_PREFIX: str = "/api/v1"
    ALLOWED_ORIGINS: str = "*" # Allow all in dev for network access

    @property
    def cors_origins(self) -> List[str]:
        return [o.strip() for o in self.ALLOWED_ORIGINS.split(",")]

    # ── Database ─────────────────────────────────────────────
    DATABASE_URL: str = "postgresql+asyncpg://beraxis_user:beraxis_pass@localhost:5432/beraxis_db"
    DATABASE_POOL_SIZE: int = 20
    DATABASE_MAX_OVERFLOW: int = 0

    # ── Redis ────────────────────────────────────────────────
    REDIS_URL: str = "redis://localhost:6379/0"
    REDIS_CELERY_URL: str = "redis://localhost:6379/1"
    REDIS_CACHE_URL: str = "redis://localhost:6379/2"
    CACHE_TTL: int = 3600

    # ── Security / JWT ───────────────────────────────────────
    JWT_SECRET_KEY: str = "change-me-in-production-use-256bit-secret"
    JWT_ALGORITHM: str = "HS256"
    JWT_ACCESS_TOKEN_EXPIRE_MINUTES: int = 60
    JWT_REFRESH_TOKEN_EXPIRE_DAYS: int = 30
    ENCRYPTION_KEY: str = "change-me-32-byte-fernet-key-here"

    # ── Admin ────────────────────────────────────────────────
    SUPERADMIN_EMAIL: str = "admin@beraxis.com"
    SUPERADMIN_PASSWORD: str = "changeme"

    # ── Rate Limiting ────────────────────────────────────────
    RATE_LIMIT_PER_MINUTE: int = 60
    RATE_LIMIT_BURST: int = 10

    # ── Stripe ───────────────────────────────────────────────
    STRIPE_SECRET_KEY: str = "sk_test_placeholder"
    STRIPE_PUBLISHABLE_KEY: str = "pk_test_placeholder"
    STRIPE_WEBHOOK_SECRET: str = "whsec_placeholder"
    STRIPE_STARTER_PRICE_ID: str = "price_starter"
    STRIPE_PROFESSIONAL_PRICE_ID: str = "price_professional"
    STRIPE_ENTERPRISE_PRICE_ID: str = "price_enterprise"

    # ── Telephony (Asterisk ARI) ─────────────────────────────
    ASTERISK_HOST: str = "127.0.0.1"

    @field_validator("ASTERISK_HOST", mode="before")
    @classmethod
    def strip_asterisk_host(cls, v: str) -> str:
        """Strip comments and whitespace from the host string."""
        if not v:
            return "127.0.0.1"
        # Remove anything after a '#' or ' '
        v = v.split("#")[0].split(";")[0].strip()
        return v

    ASTERISK_ARI_PORT: int = 8088
    ASTERISK_ARI_USER: str = "beraxis_ari"
    ASTERISK_ARI_PASS: str = "changeme"
    ASTERISK_ARI_APP: str = "beraxis_app"
    SIP_TRUNK_HOST: str = "sip.provider.com"
    SIP_TRUNK_USER: str = "sip_user"
    SIP_TRUNK_PASS: str = "sip_pass"
    OUTBOUND_CALLER_ID: str = "+10000000000"
    MAX_CONCURRENT_CALLS: int = 100

    # ── AI — STT (Faster-Whisper) ────────────────────────────
    WHISPER_MODEL_SIZE: str = "medium"
    WHISPER_DEVICE: str = "cpu"
    WHISPER_COMPUTE_TYPE: str = "int8"
    WHISPER_MODEL_PATH: str = "/models/whisper"
    WHISPER_LANGUAGE: str = "en"

    # ── AI — LLM (Llama.cpp) ─────────────────────────────────
    LLAMA_MODEL_PATH: str = "/models/llama/llama-3-8b-instruct.Q5_K_M.gguf"
    LLAMA_N_GPU_LAYERS: int = 0 # Default to CPU for stability
    LLAMA_N_CTX: int = 4096
    LLAMA_MAX_TOKENS: int = 512
    LLAMA_TEMPERATURE: float = 0.7
    LLAMA_N_THREADS: int = 8

    # ── AI — TTS (Piper) ─────────────────────────────────────
    PIPER_MODELS_DIR: str = "/models/piper"
    PIPER_DEFAULT_VOICE: str = "en_US-amy-medium"
    PIPER_SAMPLE_RATE: int = 22050

    # ── Storage ──────────────────────────────────────────────
    STORAGE_BACKEND: str = "local"
    STORAGE_LOCAL_PATH: str = "/recordings"
    AWS_ACCESS_KEY_ID: str = ""
    AWS_SECRET_ACCESS_KEY: str = ""
    AWS_BUCKET_NAME: str = "beraxis-recordings"
    AWS_REGION: str = "us-east-1"

    # ── Email ────────────────────────────────────────────────
    SMTP_HOST: str = "smtp.sendgrid.net"
    SMTP_PORT: int = 587
    SMTP_USER: str = "apikey"
    SMTP_PASS: str = ""
    EMAIL_FROM: str = "noreply@beraxis.com"
    EMAIL_FROM_NAME: str = "Beraxis"

    # ── OAuth ────────────────────────────────────────────────
    GOOGLE_CLIENT_ID: str = ""
    GOOGLE_CLIENT_SECRET: str = ""
    GITHUB_CLIENT_ID: str = ""
    GITHUB_CLIENT_SECRET: str = ""
    OAUTH_CALLBACK_URL: str = "http://localhost:8000/api/v1/auth/oauth/callback"

    # ── Monitoring ───────────────────────────────────────────
    SENTRY_DSN: Optional[str] = None
    PROMETHEUS_ENABLED: bool = True


@lru_cache()
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
