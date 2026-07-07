# Architecture

IteraMindAI turns a single task into a **multi-round refinement loop**. Instead
of trusting one LLM call, the task passes through three cooperating roles — all
backed by the same pluggable provider — until the critic is satisfied or the
iteration budget is exhausted.

```
                ┌─────────────────────────────────────────────┐
                │                Orchestrator                  │
                │  (app/orchestrator.py — async generator)     │
                └─────────────────────────────────────────────┘
                     │            │              │
             round 0 │    round i │      round i │
                     ▼            ▼              ▼
              ┌───────────┐ ┌───────────┐ ┌────────────┐
              │ Generator │ │  Critic   │ │ Integrator │
              └───────────┘ └───────────┘ └────────────┘
                     │            │              │
                     └────────────┴──────────────┘
                                  ▼
                    ┌────────────────────────────┐
                    │   Provider layer (registry) │
                    ├────────────────────────────┤
                    │ gemini · openai · anthropic │
                    │ openrouter · groq · mock    │
                    └────────────────────────────┘
```

## The loop

1. **Generator** produces an initial solution to the task.
2. **Critic** reviews the current solution and lists concrete, actionable issues,
   ending with a verdict (`APPROVED` / `NEEDS_WORK`).
3. **Integrator** rewrites the solution addressing every point from the critic.
4. Steps 2–3 repeat until `max_iterations` is reached, or the critic returns
   `APPROVED` (early stop).

Each step is emitted as an event, so the API can stream the reasoning live over
Server-Sent Events and the web UI renders it round by round.

## Provider layer

Every provider implements a single async method:

```python
async def complete(self, messages, *, temperature, max_tokens) -> LLMResult
```

`app/providers/registry.py` resolves a provider slug to a configured instance
and injects the API key (request override → environment variable → none). The
keyless **Mock** provider makes the app fully runnable with zero configuration,
which is what powers the public demo.

| Provider    | Key env var              | Default model                 |
|-------------|--------------------------|-------------------------------|
| mock        | — (none)                 | mock-1                        |
| gemini      | `GOOGLE_GEMINI_API_KEY`  | gemini-1.5-flash-latest       |
| openai      | `OPENAI_API_KEY`         | gpt-4o-mini                   |
| anthropic   | `ANTHROPIC_API_KEY`      | claude-3-5-haiku-latest       |
| openrouter  | `OPENROUTER_API_KEY`     | openai/gpt-4o-mini            |
| groq        | `GROQ_API_KEY`           | llama-3.3-70b-versatile       |

OpenAI, Groq and OpenRouter share one implementation (`openai_compat.py`) since
they all speak the OpenAI Chat Completions schema.

## Components

| Path                         | Role                                                        |
|------------------------------|-------------------------------------------------------------|
| `app/main.py`                | FastAPI app: REST + SSE endpoints, serves the web UI        |
| `app/orchestrator.py`        | The iterative generate → critique → integrate engine        |
| `app/providers/`             | Pluggable multi-provider LLM layer                          |
| `app/web/`                   | Zero-build single-page frontend (HTML/CSS/JS)               |
| `api/index.py` + `vercel.json` | Vercel serverless entry                                   |
| `Dockerfile`                 | Container image (Hugging Face Spaces, Railway, Render, …)    |
| `backend-go/`                | Optional Go orchestrator for the polyglot local setup       |
| `integration-python/`        | Optional legacy Flask agent microservice (Go talks to this) |
| `core-rust/`                 | Experimental Rust task-decomposition core                   |

The **deployable MVP is the FastAPI app** in `app/`. The Go and Rust pieces are
the original polyglot vision kept for local experimentation.
