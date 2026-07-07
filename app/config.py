"""Runtime configuration, loaded from environment (and a local .env if present)."""
from __future__ import annotations

import os

try:  # optional: load .env for local development
    from dotenv import load_dotenv

    load_dotenv()
except Exception:  # pragma: no cover - dotenv is optional
    pass


class Settings:
    """Small settings holder read from environment variables."""

    APP_NAME = "IteraMindAI"
    # Host/port used when running standalone (HF Spaces expects 7860).
    HOST = os.getenv("HOST", "0.0.0.0")
    PORT = int(os.getenv("PORT", "7860"))

    # Hard limits to keep the public demo cheap and safe.
    MAX_ITERATIONS = int(os.getenv("MAX_ITERATIONS", "8"))
    MAX_TOKENS = int(os.getenv("MAX_TOKENS", "1024"))
    REQUEST_TIMEOUT = float(os.getenv("REQUEST_TIMEOUT", "60"))

    # Comma separated origins for CORS ("*" to allow all).
    CORS_ORIGINS = os.getenv("CORS_ORIGINS", "*")


settings = Settings()
