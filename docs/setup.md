# Local setup

## Requirements

- Python 3.10+ (3.12 recommended)
- Optional: Go 1.21+ and Rust (only for the polyglot local services)
- Optional: Docker (for the container workflow)

## Run the web app (recommended)

```bash
# 1. create a virtual environment
python -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate

# 2. install dependencies
pip install -r requirements.txt

# 3. (optional) configure provider keys — the app runs without any
cp .env.example .env             # then edit .env

# 4. start the server
uvicorn app.main:app --reload --port 7860
```

Open http://localhost:7860. With no keys set, pick the **Mock** provider and it
works offline. To use a real model, select a provider and either set its key in
`.env` or paste a key directly in the UI (sent per-request, never stored).

## Run with Docker

```bash
docker compose up --build
# open http://localhost:7860
```

## Run the tests

```bash
pip install -r requirements-dev.txt
pytest -q
```

## Optional: the polyglot local architecture

```bash
# terminal 1 — Python agent microservice (multi-provider)
cd integration-python
pip install -r requirements.txt
python gemini_integration.py      # serves on :5000

# terminal 2 — Go orchestrator drives the loop
cd backend-go/cmd
go run main.go
```

The Rust core is a standalone experiment:

```bash
cd core-rust
cargo run
```
