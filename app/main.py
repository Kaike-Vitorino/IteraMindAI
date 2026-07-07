"""FastAPI application: iterative multi-provider reasoning API + web UI."""
from __future__ import annotations

import json
from pathlib import Path

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, StreamingResponse
from fastapi.staticfiles import StaticFiles

from .config import settings
from .orchestrator import run_iterations, stream_iterations
from .providers import ProviderError, available_providers, get_provider
from .schemas import IterateRequest, IterateResponse, ProviderInfo

WEB_DIR = Path(__file__).parent / "web"

app = FastAPI(
    title=settings.APP_NAME,
    description=(
        "Iterative reasoning engine that refines a task across generator / critic "
        "/ integrator rounds, backed by a pluggable multi-provider LLM layer "
        "(Gemini, OpenAI, Anthropic, OpenRouter, Groq, or an offline Mock)."
    ),
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[o.strip() for o in settings.CORS_ORIGINS.split(",")],
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/api/health")
async def health() -> dict:
    return {"status": "ok", "app": settings.APP_NAME, "version": app.version}


@app.get("/api/providers", response_model=list[ProviderInfo])
async def providers() -> list[dict]:
    return available_providers()


def _build_provider(req: IterateRequest):
    try:
        return get_provider(
            req.provider,
            api_key=req.api_key,
            model=req.model,
            timeout=settings.REQUEST_TIMEOUT,
        )
    except ProviderError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@app.post("/api/iterate", response_model=IterateResponse)
async def iterate(req: IterateRequest) -> dict:
    provider = _build_provider(req)
    try:
        return await run_iterations(
            req.task,
            provider,
            max_iterations=req.max_iterations,
            temperature=req.temperature,
            max_tokens=settings.MAX_TOKENS,
        )
    except ProviderError as exc:
        raise HTTPException(status_code=502, detail=str(exc)) from exc


@app.post("/api/iterate/stream")
async def iterate_stream(req: IterateRequest) -> StreamingResponse:
    provider = _build_provider(req)

    async def event_gen():
        try:
            async for event in stream_iterations(
                req.task,
                provider,
                max_iterations=req.max_iterations,
                temperature=req.temperature,
                max_tokens=settings.MAX_TOKENS,
            ):
                yield f"data: {json.dumps(event)}\n\n"
        except ProviderError as exc:
            yield f"data: {json.dumps({'type': 'error', 'message': str(exc)})}\n\n"

    return StreamingResponse(
        event_gen(),
        media_type="text/event-stream",
        headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"},
    )


# --- Web UI ---------------------------------------------------------------
if (WEB_DIR / "static").exists():
    app.mount("/static", StaticFiles(directory=WEB_DIR / "static"), name="static")


@app.get("/")
async def index() -> FileResponse:
    return FileResponse(WEB_DIR / "index.html")
