---
title: IteraMindAI
emoji: 🧠
colorFrom: purple
colorTo: indigo
sdk: docker
app_port: 7860
pinned: false
license: mit
---

# IteraMindAI

**Iterative, multi-provider reasoning engine.** Instead of trusting a single LLM
call, IteraMindAI refines a task across rounds with three cooperating agents —
**Generator → Critic → Integrator** — backed by a pluggable provider layer that
speaks to **Google Gemini, OpenAI, Anthropic, OpenRouter, Groq**, or a keyless
**offline Mock** so the demo runs with zero configuration.

![IteraMindAI](./assets/placeholder.jpg)

<p>
  <img alt="CI" src="https://github.com/Kaike-Vitorino/IteraMindAI/actions/workflows/ci.yml/badge.svg" />
  <img alt="Python" src="https://img.shields.io/badge/python-3.10%2B-blue" />
  <img alt="License" src="https://img.shields.io/badge/license-MIT-green" />
</p>

---

## Why it exists

A one-shot answer is rarely the best answer. IteraMindAI models the way people
actually improve work — draft, critique, revise — as an explicit loop you can
watch happen live:

1. **Generator** writes an initial solution.
2. **Critic** finds concrete issues (correctness, edge cases, robustness, clarity)
   and returns a verdict.
3. **Integrator** rewrites the solution addressing every point.
4. Repeat until the critic approves or the iteration budget runs out.

Every step streams to the browser over Server-Sent Events, so you see the
reasoning unfold round by round.

## Supported providers

| Provider   | Key env var             | Default model             |
|------------|-------------------------|---------------------------|
| **mock**   | *none* (offline)        | `mock-1`                  |
| gemini     | `GOOGLE_GEMINI_API_KEY` | `gemini-1.5-flash-latest` |
| openai     | `OPENAI_API_KEY`        | `gpt-4o-mini`             |
| anthropic  | `ANTHROPIC_API_KEY`     | `claude-3-5-haiku-latest` |
| openrouter | `OPENROUTER_API_KEY`    | `openai/gpt-4o-mini`      |
| groq       | `GROQ_API_KEY`          | `llama-3.3-70b-versatile` |

Keys can be set as environment variables **or** pasted per-request in the UI
(never stored server-side).

## Quickstart

```bash
python -m venv .venv
source .venv/bin/activate            # Windows: .venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload --port 7860
```

Open <http://localhost:7860>. Select **Mock** and run — no keys required. Full
setup notes: [docs/setup.md](docs/setup.md).

## Deploy

### Hugging Face Spaces (Docker) — easiest

1. Create a new Space → **SDK: Docker**.
2. Push this repository to it (the `Dockerfile` and the README front matter above
   are all HF needs; the app is served on port `7860`).
3. *(Optional)* add provider keys under **Settings → Variables and secrets**
   (`GROQ_API_KEY`, `OPENAI_API_KEY`, …). Without any keys the Mock provider
   keeps the Space fully functional.

### Vercel

The repo ships an `api/index.py` ASGI entry and `vercel.json`:

```bash
npm i -g vercel
vercel            # preview
vercel --prod     # production
```

Add provider keys in **Project → Settings → Environment Variables**.

### Docker / Railway / Render / Fly.io

```bash
docker compose up --build        # -> http://localhost:7860
```

or use the `Dockerfile` / `Procfile` directly on any container or PaaS host.

## API

| Method & path              | Description                                   |
|----------------------------|-----------------------------------------------|
| `GET  /api/health`         | Liveness probe                                |
| `GET  /api/providers`      | List providers and key status                 |
| `POST /api/iterate`        | Run the loop, return all steps                |
| `POST /api/iterate/stream` | Run the loop, stream steps as SSE             |
| `GET  /docs`               | Interactive Swagger UI                        |

```bash
curl -X POST http://localhost:7860/api/iterate \
  -H "Content-Type: application/json" \
  -d '{"task":"Write a function that returns the average of a list","provider":"mock","max_iterations":3}'
```

Full reference: [docs/api_reference.md](docs/api_reference.md).

## Architecture

The deployable MVP is the self-contained **FastAPI app** in `app/`. A pluggable
provider registry means adding a new vendor is a single small class. See
[docs/architecture.md](docs/architecture.md) for the full picture.

```
app/
├── main.py            # FastAPI: REST + SSE endpoints, serves the web UI
├── orchestrator.py    # generate → critique → integrate loop
├── providers/         # gemini · openai · anthropic · openrouter · groq · mock
└── web/               # zero-build single-page frontend
api/index.py           # Vercel serverless entry
Dockerfile             # Hugging Face Spaces / any container host
backend-go/            # optional Go orchestrator (polyglot local setup)
integration-python/    # optional legacy Flask agent microservice
core-rust/             # experimental Rust task-decomposition core
```

## Tests

```bash
pip install -r requirements-dev.txt
pytest -q
```

## License

MIT — see [LICENSE](LICENSE).
