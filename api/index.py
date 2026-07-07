"""Vercel serverless entry point.

Vercel's @vercel/python runtime auto-detects an ASGI application exported as
``app``, so we simply re-export the FastAPI instance.
"""
from app.main import app  # noqa: F401
