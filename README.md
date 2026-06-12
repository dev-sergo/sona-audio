```
███████  ██████  ███    ██  █████
██      ██    ██ ████   ██ ██   ██
███████ ██    ██ ██ ██  ██ ███████
     ██ ██    ██ ██  ██ ██ ██   ██
███████  ██████  ██   ████ ██   ██
```

**Personal AI audio studio and model benchmark bench.**  
Transcription · Stem separation · Smart notes · Translation · Music generation.  
Heavy models run on a GPU box (RTX 3090); logic and the Telegram bot run on a Mac.

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![CI](https://github.com/dev-sergo/sona-audio-/actions/workflows/ci.yml/badge.svg)](https://github.com/dev-sergo/sona-audio-/actions)
[![Python 3.10+](https://img.shields.io/badge/python-3.10%2B-blue.svg)](https://www.python.org/)
[![Open Source](https://img.shields.io/badge/Open%20Source-%E2%9D%A4-red.svg)](https://opensource.org/)

---

## What it does

| Feature | Model | Status |
|---|---|---|
| Speech transcription | faster-whisper large-v3 | ✅ ready |
| Stem separation | demucs htdemucs | ✅ ready |
| Smart notes | qwen3 via llama-swap | ✅ ready |
| RU ↔ EN translation | qwen3 via llama-swap | ✅ ready |
| YouTube / SoundCloud download | yt-dlp | ✅ ready |
| Music generation | ACE-Step-1.5 | 🚧 stub (501) |
| TTS with your own voice | XTTS v2 | 📋 planned |

---

## Architecture

```
Mac (Docker)                          GPU box (native, RTX 3090)
┌──────────────────┐                 ┌──────────────────────────┐
│  server  :8000   │ ─── HTTP ──▶   │  model_server  :8001     │
│  business logic  │                 │  Whisper · Demucs        │
│  SQLite · jobs   │ ─── HTTP ──▶   │  llama-swap    :8080     │
│  bot (Telegram)  │                 │  qwen3-32k               │
└──────────────────┘                 └──────────────────────────┘
```

- `model_server/` — inference only, needs CUDA
- `server/` — routes, job queue, SQLite, HTTP clients to the models
- `bot/` — Telegram UI (optional; everything is available over HTTP)

Full details: [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md) · [docs/API.md](docs/API.md)

---

## Benchmarks (RTX 3090, 24 GB VRAM)

All numbers measured on the GPU box. Lower is better.

| Operation | Input | Time |
|---|---|---|
| Whisper large-v3 transcription | 60 s voice (OGG) | ~4 s |
| Demucs htdemucs stem split | 3 min track (MP3) | ~45 s |
| qwen3-32k translation | ~200 tokens | ~2 s |
| ACE-Step music generation | 30 s, 4 stems | TBD |

> Benchmark conditions and methodology: [docs/BENCHMARKS.md](docs/BENCHMARKS.md) _(coming soon)_

---

## Quick start

### GPU box (one-time setup)
```bash
git clone https://github.com/dev-sergo/sona-audio-.git ~/sona-audio
cd ~/sona-audio
bash setup_gpu.sh          # creates venv, installs faster-whisper + demucs
make gpu-start             # starts model_server on :8001
```

### Mac
```bash
git clone https://github.com/dev-sergo/sona-audio-.git
cd sona-audio
cp .env.example .env       # set MODEL_SERVER_URL and LLM_URL
make up                    # docker compose up -d  (server + bot)
make logs
```

Nothing is installed natively on the Mac — everything runs in Docker.  
To wipe it all: `make clean`.

---

## Testing

```bash
make test                  # automated tests in a python:3.11 container (no GPU needed)
```

Manual API checks without Telegram — see [docs/TESTING.md](docs/TESTING.md).

---

## How to add a new audio model

Repeatable recipe — example: adding a model called `foo`.

1. **GPU box** — `model_server/main.py`: loader `_load_foo()` + endpoint `POST /foo`
2. **Mac** — `server/services/foo_service.py`: HTTP client for `/foo`
3. **Mac** — route:
   - fast op → `server/routes/foo.py` + `include_router` in `server/main.py`
   - slow op → `register_handler("foo", ...)` in `server/main.py` (job queue)
4. **Deps** — `requirements.model_server.txt`
5. **Test** — `tests/test_foo.py` (mock the service, test the route)
6. _(optional)_ **Bot** — `bot/handlers/foo.py`

Existing models are untouched — each one is isolated.

---

## Makefile reference

| Command | Action |
|---|---|
| `make test` | run automated tests in Docker |
| `make build` / `make up` / `make down` | build images / start / stop |
| `make logs` | stream container logs |
| `make clean` | remove containers, images and `data/` |
| `make gpu-setup` / `make gpu-start` | install / run model_server (GPU box) |

---

## Contributing

Contributions, issues and pull requests are welcome.  
Please read [CONTRIBUTING.md](CONTRIBUTING.md) before opening a PR.

---

## License

MIT © 2026 [dev-sergo](https://github.com/dev-sergo)  
See [LICENSE](LICENSE) for the full text.
