# Architecture

## Overview

```
┌─────────────────────────────────────┐
│  Mac (development + runtime)        │
│                                     │
│  bot/         Telegram bot          │
│  server/      FastAPI :8000         │
│               business logic        │
│               SQLite                │
│               job queue             │
└────────────┬────────────────────────┘
             │ HTTP  (MODEL_SERVER_URL / LLM_URL)
             ▼
┌─────────────────────────────────────┐
│  GPU box  (RTX 3090, 24 GB VRAM)    │
│                                     │
│  model_server/   FastAPI :8001      │
│    POST /whisper  → faster-whisper  │
│    POST /demucs   → demucs          │
│    GET  /health                     │
│                                     │
│  llama-swap      :8080 (existing)   │
│    translation + note summarization │
│                                     │
│  ACE-Step API    :8002 (standalone) │
│    music generation (not deployed)  │
└─────────────────────────────────────┘
```

## Machines

### Mac
- Runs: `server/` (FastAPI :8000), `bot/` (Telegram bot)
- Stores: SQLite (`data/studio.db`), audio files (`data/audio/`)
- No GPU required — all ML inference delegated to GPU box

### GPU box
- User: serbio, Python 3.10.6 (pyenv), torch 2.5.1+cu121
- Runs: `model_server/` (FastAPI :8001), llama-swap (:8080)
- Has: RTX 3090 24GB VRAM, ACE-Step weights, LLM GGUFs
- ComfyUI: manual experiments only, not used by our code

## Project Structure

```
sona-audio/
├── model_server/               ← runs on GPU box
│   ├── main.py                 # FastAPI: /whisper /demucs /health
│   └── config.py               # model paths, device settings
│
├── server/                     ← runs on Mac
│   ├── main.py                 # FastAPI app, job handlers, /health
│   ├── config.py               # MODEL_SERVER_URL, LLM_URL, paths
│   ├── core/
│   │   ├── database.py         # SQLite init, tables
│   │   └── job_queue.py        # async job queue (SQLite-backed)
│   ├── routes/
│   │   ├── transcribe.py       # POST /transcribe
│   │   ├── separate.py         # POST /separate (async)
│   │   ├── generate.py         # POST /generate (async)
│   │   ├── notes.py            # CRUD /notes
│   │   ├── jobs.py             # GET /jobs/{id}
│   │   └── translate.py        # POST /translate
│   └── services/               # HTTP clients → GPU box
│       ├── whisper_service.py  # calls model_server /whisper
│       ├── demucs_service.py   # calls model_server /demucs, extracts ZIP
│       ├── acestep_service.py  # HTTP client → standalone ACE-Step API server (:8002)
│       └── llm_service.py      # calls llama-swap /v1/chat/completions
│
├── bot/                        ← runs on Mac
│   ├── main.py
│   ├── config.py               # TELEGRAM_TOKEN, API_URL
│   └── handlers/
│       ├── audio.py            # voice → transcribe, /separate
│       ├── generate.py         # /generate wizard
│       └── notes.py            # /note, /notes
│
├── data/                       # Mac local (gitignored)
│   ├── studio.db
│   └── audio/
│
├── docs/
├── requirements.server.txt     # Mac: fastapi, httpx, aiosqlite...
├── requirements.model_server.txt  # GPU box: faster-whisper, demucs...
├── requirements.bot.txt        # Mac: python-telegram-bot...
└── .env.example
```

## Key Decisions

| Decision | Choice | Reason |
|---|---|---|
| Model server location | GPU box | Models need CUDA; Mac has no GPU |
| Business logic location | Mac | Keeps GPU box minimal and stateless |
| ACE-Step integration | Standalone ACE-Step API server (HTTP, :8002) | Reuses ACE-Step's own `api_server`; no ComfyUI dependency at runtime |
| Translation | llama-swap (qwen3) | Already running, no extra VRAM |
| Storage | SQLite on Mac | Simple, no server needed |
| Bot | Mac, stateless | Connects to server via API_URL env var |

## VRAM Budget (GPU box)

| Model | VRAM | Strategy |
|---|---|---|
| faster-whisper large-v3 | ~3 GB | loaded at startup |
| demucs htdemucs | ~1 GB | loaded at startup |
| ACE-Step (standalone :8002) | ~8-10 GB | runs in its own ACE-Step API server process; not deployed in this snapshot |
| llama-swap (qwen3) | ~6-8 GB | managed separately |

Whisper + Demucs + llama-swap ≈ 12 GB simultaneous → fits in 24 GB.

## How to Run

### GPU box
```bash
cd ~/sona-audio
source ~/venvs/alf-audio/bin/activate
python -m uvicorn model_server.main:app --host 0.0.0.0 --port 8001
```

### Mac
```bash
cd ~/work/sona-audio
# terminal 1 — API server
python -m uvicorn server.main:app --host 0.0.0.0 --port 8000
# terminal 2 — Telegram bot
python -m bot.main
```
