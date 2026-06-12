# sona

Personal AI audio studio and a test bench for audio models.
Heavy models run on a GPU box (RTX 3090); logic and the bot run on a Mac.

## What it does

| Feature | Model | Status |
|---|---|---|
| Speech transcription | faster-whisper large-v3 | ✅ |
| Stem separation | demucs htdemucs | ✅ |
| Smart notes | qwen3 (llama-swap) | ✅ |
| RU↔EN translation | qwen3 (llama-swap) | ✅ |
| YouTube/SoundCloud download | yt-dlp | ✅ |
| Music generation | ACE-Step-1.5 | 🚧 stub (501) |
| TTS with your own voice | XTTS v2 | 📋 planned |

## Architecture

```
Mac (Docker)                         GPU box (native)
├── server  :8000  logic, SQLite ──HTTP──▶ model_server :8001  Whisper, Demucs
└── bot            Telegram                  llama-swap   :8080  qwen3 (ready)
```

- `model_server/` — model inference only (needs CUDA)
- `server/` — business logic: routes, job queue, DB, HTTP clients to the models
- `bot/` — Telegram UI (optional; everything is available over the HTTP API)

More: [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md) · [docs/API.md](docs/API.md) · [docs/FEATURES.md](docs/FEATURES.md) · [docs/PROGRESS.md](docs/PROGRESS.md)

## Running

### GPU box (one-time)
```bash
git clone <repo-url> ~/sona && cd ~/sona
bash setup_gpu.sh
make gpu-start          # uvicorn model_server :8001
```

### Mac
```bash
cp .env.example .env    # set MODEL_SERVER_URL / LLM_URL = http://<gpu-ip>:port
make up                 # docker compose up -d (server + bot)
make logs
```

Nothing is installed natively on the Mac — everything runs in Docker. Wipe it clean: `make clean`.

## Testing

```bash
make test               # automated tests in a python:3.11 container (no GPU, no bot)
```

Manual API checks without Telegram — see [docs/TESTING.md](docs/TESTING.md).

## How to add a new audio model

Repeatable recipe (example — adding a model called `foo`):

1. **GPU** — in `model_server/main.py`: loader `_load_foo()` + endpoint `POST /foo`
2. **Mac** — `server/services/foo_service.py`: HTTP client for `/foo`
3. **Mac** — route:
   - fast operation → `server/routes/foo.py` + `include_router` in `server/main.py`
   - long operation → `register_handler("foo", ...)` in `server/main.py` (job queue)
4. **Dependencies** — in `requirements.model_server.txt`
5. **Test** — `tests/test_foo.py` (mock the service, check the route)
6. _(optional)_ **Bot** — `bot/handlers/foo.py`

Existing models stay untouched — each one is isolated.

## Makefile

| Command | Action |
|---|---|
| `make test` | automated tests in Docker |
| `make build` / `make up` / `make down` | Docker images / start / stop |
| `make logs` | container logs |
| `make clean` | remove containers, images and `data/` |
| `make gpu-setup` / `make gpu-start` | install / run model_server (on the GPU box) |
