# alf-audio-studio — Claude Context

Personal AI audio studio. Heavy models run on a GPU box (RTX 3090), Telegram bot and clients connect over HTTP.

## Docs (read first)
- [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md) — stack, schema, all key decisions
- [docs/FEATURES.md](docs/FEATURES.md) — what the project does, MVP vs later
- [docs/API.md](docs/API.md) — all endpoints with request/response formats
- [docs/PROGRESS.md](docs/PROGRESS.md) — current status, blockers, next steps ← update every session

## Quick Facts

**GPU box**: Linux, user `serbio`, Python 3.10.6 (pyenv), torch 2.5.1+cu121, RTX 3090 24GB
**Mac**: development machine, runs the Telegram bot locally for testing

**What's already on GPU box:**
- ACE-Step-1.5 weights: `~/Documents/ComfyUI/models/ace-step/`
- llama-swap: `:8080`, model `qwen3-32k` (used for translation + note summarization)
- ComfyUI: `~/Documents/ComfyUI` — for manual experiments only, NOT used by our API

**What needs to be installed on GPU box:**
- venv: `~/venvs/alf-audio` (python3 -m venv ... --system-site-packages)
- faster-whisper, demucs, fastapi, uvicorn, python-multipart
- ACE-Step Python package (check custom node source first)

## Stack
- **API server**: FastAPI, port 8000, on GPU box
- **STT**: faster-whisper large-v3 (CUDA, persistent in VRAM)
- **Stems**: demucs htdemucs (CUDA, persistent in VRAM)
- **Music gen**: ACE-Step-1.5 Python API direct (lazy VRAM, unload if free < 4GB)
- **LLM/translate**: llama-swap :8080 HTTP (already running)
- **Storage**: SQLite at `data/studio.db`, audio files at `data/audio/`
- **Bot**: python-telegram-bot, stateless, configured via env vars only

## Critical Decisions (don't revisit without good reason)
1. ACE-Step runs as direct Python API — not through ComfyUI workflow
2. Translation via llama-swap (qwen3) — no separate translation model
3. Whisper + Demucs persistent in VRAM; ACE-Step lazy-loaded
4. Bot is 100% stateless — all state in the API/SQLite

## Unknown at start of session?
Check [docs/PROGRESS.md](docs/PROGRESS.md) "Blockers" and "Known Unknowns" sections.
Update PROGRESS.md when something is resolved or a new blocker appears.
