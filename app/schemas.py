"""Pydantic request/response models for the HTTP API."""
from __future__ import annotations

from pydantic import BaseModel, Field

from .config import settings


class IterateRequest(BaseModel):
    task: str = Field(..., min_length=1, description="The task/prompt to solve.")
    provider: str = Field("mock", description="Provider slug, e.g. 'gemini'.")
    model: str | None = Field(None, description="Optional model override.")
    api_key: str | None = Field(
        None, description="Optional per-request key; falls back to server env."
    )
    max_iterations: int = Field(
        3, ge=1, le=settings.MAX_ITERATIONS, description="Refinement rounds."
    )
    temperature: float = Field(0.7, ge=0.0, le=2.0)

    model_config = {
        "json_schema_extra": {
            "example": {
                "task": "Write a Python function that returns the average of a list.",
                "provider": "mock",
                "max_iterations": 3,
            }
        }
    }


class Step(BaseModel):
    iteration: int
    role: str  # generator | critic | integrator
    content: str
    provider: str
    model: str


class IterateResponse(BaseModel):
    task: str
    provider: str
    model: str
    iterations: int
    steps: list[Step]
    final_solution: str
    stopped_early: bool = False


class ProviderInfo(BaseModel):
    name: str
    label: str
    default_model: str
    requires_key: bool
    key_configured: bool
