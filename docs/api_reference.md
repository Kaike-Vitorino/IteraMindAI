# API reference

Base URL: `/` · Interactive docs (Swagger UI): `/docs` · OpenAPI: `/openapi.json`

## `GET /api/health`

Liveness probe.

```json
{ "status": "ok", "app": "IteraMindAI", "version": "1.0.0" }
```

## `GET /api/providers`

List available providers and whether a server-side key is configured.

```json
[
  { "name": "mock", "label": "Mock (offline demo)", "default_model": "mock-1",
    "requires_key": false, "key_configured": false },
  { "name": "gemini", "label": "Google Gemini", "default_model": "gemini-1.5-flash-latest",
    "requires_key": true, "key_configured": false }
]
```

## `POST /api/iterate`

Run the full loop and return every step at once.

**Request body**

| Field            | Type   | Default | Notes                                        |
|------------------|--------|---------|----------------------------------------------|
| `task`           | string | —       | Required. The task/prompt to solve.          |
| `provider`       | string | `mock`  | One of the provider slugs.                   |
| `model`          | string | null    | Optional model override.                     |
| `api_key`        | string | null    | Optional per-request key (falls back to env).|
| `max_iterations` | int    | 3       | 1–8. Refinement rounds.                      |
| `temperature`    | float  | 0.7     | 0.0–2.0.                                      |

```bash
curl -X POST http://localhost:7860/api/iterate \
  -H "Content-Type: application/json" \
  -d '{"task":"Write a function that returns the average of a list","provider":"mock","max_iterations":3}'
```

**Response**

```json
{
  "task": "…",
  "provider": "mock",
  "model": "mock-1",
  "iterations": 3,
  "steps": [
    { "iteration": 1, "role": "generator",  "content": "…", "provider": "mock", "model": "mock-1" },
    { "iteration": 2, "role": "critic",      "content": "…", "provider": "mock", "model": "mock-1" },
    { "iteration": 2, "role": "integrator",  "content": "…", "provider": "mock", "model": "mock-1" }
  ],
  "final_solution": "…",
  "stopped_early": false
}
```

## `POST /api/iterate/stream`

Same request body, but streams the loop live as **Server-Sent Events**
(`text/event-stream`). Each event is a JSON object:

```
data: {"type": "step", "step": { "iteration": 1, "role": "generator", ... }}

data: {"type": "step", "step": { "iteration": 2, "role": "critic", ... }}

data: {"type": "done", "result": { ...full result... }}
```

An `{"type": "error", "message": "…"}` event is emitted if a provider call fails.

## Errors

| Status | Meaning                                             |
|--------|-----------------------------------------------------|
| 400    | Unknown provider or missing required key            |
| 422    | Request validation failed (e.g. empty `task`)       |
| 502    | Upstream provider call failed                       |
