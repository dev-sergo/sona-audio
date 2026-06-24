# Progress

Living document. Update at the start and end of every dev session.

---

## Current Status

**Phase**: 2 — Core stack deployed and tested end-to-end; ACE-Step generation is next
**Date**: 2026-06-17
**Next action**: Implement ACE-Step music generation (study ComfyUI node source → wire up model_server endpoint)

---

## Environment Checklist

### GPU Box (serbio@admin, RTX 3090)
- [x] GPU visible, CUDA 12.1
- [x] Python 3.10.6 (pyenv), torch 2.5.1+cu121
- [x] ACE-Step weights present at `~/Documents/ComfyUI/models/ace-step/`
- [x] llama-swap running at :8080 (gemma-4-26b-a4b-it-mxfp4-moe used for translation/notes)
- [x] venv `~/venvs/alf-audio` created
- [x] faster-whisper installed and working
- [x] demucs installed and working (ffmpeg added for MP3 support)
- [ ] ACE-Step Python package installed and verified
- [x] FastAPI server runs and /health responds

### Mac (development)
- [x] Project dir: `~/work/sona-audio`
- [x] Scaffold complete, repo pushed to GitHub
- [x] .env configured (MODEL_SERVER_URL, LLM_URL, LLM_MODEL)
- [ ] Bot dependencies installed
- [ ] Bot connects to API and responds to /start

---

## Iteration Log

### 2026-06-16/17 — Session 4
**Done:**
- Deployed model_server on GPU box (Whisper + Demucs loaded, /health ✅)
- Fixed Makefile gpu-start (`source` → `bash -c "source ..."`)
- Identified working LLM: gemma-4-26b-a4b-it-mxfp4-moe (qwen3-32k not available)
- Fixed LLM service for thinking models: system prompt + max_tokens=4000 + reasoning_content fallback
- Fixed /notes curl example (form-data, not JSON)
- Installed ffmpeg on GPU box (required by torchaudio for MP3)
- End-to-end test results: /translate ✅ /notes ✅ /transcribe ✅ /separate ✅

**Blockers hit and resolved:**
- llama-swap model OOM → use MoE model with small active params
- torchaudio can't decode MP3 → install ffmpeg
- Thinking model returns empty content → system prompt + reasoning_content fallback
- model_server OOM on restart → stop llama-swap first, then start model_server

**Still open:**
- ACE-Step music generation (stub, returns 501)
- Telegram bot not configured (no token yet)
- model_server starts manually — no systemd service yet

### 2026-06-12 — Session 3
**Done:**
- Renamed project to `sona`; dir is `~/work/sona-audio`
- Added test suite (`tests/`: health, jobs, notes, transcribe, translate) + `pytest.ini` + `conftest.py`
- Added GitHub Actions CI (`.github/workflows/ci.yml`) — runs pytest on every push/PR
- Added Docker: `Dockerfile.server`, `Dockerfile.bot`, `docker-compose.yml`, `Makefile`
- Added `docs/TESTING.md`, rewrote `README.md`, `setup_gpu.sh`

**Open:**
- Repo not yet `git init`-ed — pending first commit
- ACE-Step still a stub (501) — see Known Unknowns
- Nothing deployed to GPU box yet (model_server unverified with real models)

### 2026-06-11 — Session 2
**Done:**
- Full scaffold: all files (server + bot + model_server)
- Architecture reworked: GPU box = models only, Mac = all logic + bot
- model_server/ — minimal FastAPI :8001 for the GPU box (Whisper, Demucs, ACE-Step stub)
- server/services/ — became HTTP clients (httpx → model_server)
- model_manager removed from the Mac (not needed — the GPU box manages models)
- Fixed bug: StaticFiles directory must exist before mount

**Runs on the Mac (no GPU):**
- python -m uvicorn server.main:app → /health, /notes, /translate, /jobs
- python -m bot.main → bot

**Runs on the GPU box:**
- python -m uvicorn model_server.main:app → /whisper, /demucs

**Still to verify in tests:**
- demucs Python API on a real file (apply_model + torchaudio)
- ACE-Step Python API (study ~/Documents/ComfyUI/custom_nodes/ACE-Step-1.5/)

### 2026-06-10 — Session 1
**Done:**
- Inventoried GPU box: GPU, Python, existing models (ACE-Step weights, LLM GGUFs, ComfyUI image stack)
- Confirmed no audio packages installed (no whisper, demucs, TTS)
- Finalized all architecture decisions (see ARCHITECTURE.md)
- Created all docs: ARCHITECTURE, FEATURES, API, PROGRESS

**Decisions made:**
- ACE-Step: direct Python API (not ComfyUI workflow) — more reliable, no dependency on ComfyUI running
- Translation: via llama-swap/qwen3 — already running, no extra VRAM
- Storage: SQLite
- VRAM: Whisper+Demucs persistent, ACE-Step lazy load with 4GB free threshold
- Bot: stateless, all state in API, fully env-var driven

---

## Blockers

_None currently. First blocker likely: ACE-Step Python package API — need to verify it works standalone (outside ComfyUI). The ComfyUI node code at `~/Documents/ComfyUI/custom_nodes/ACE-Step-1.5/` is the reference._

---

## Known Unknowns

1. **ACE-Step standalone API** — need to check if `pip install acestep` exists or if we need to adapt the ComfyUI node code directly. Check: `~/Documents/ComfyUI/custom_nodes/ACE-Step-1.5/`
2. **ACE-Step input format** — exact parameters (lyrics format, style tags, model loading) to be confirmed from node source
3. **Demucs output format** — stems as separate files, need to confirm naming convention
4. **llama-swap translate latency** — unknown, may be too slow for inline use; if >5s, cache translations

---

## Next Steps (ordered)

1. Create venv on GPU box: `python3 -m venv ~/venvs/alf-audio --system-site-packages`
2. Install: `pip install faster-whisper demucs fastapi uvicorn python-multipart`
3. Inspect ACE-Step node source to understand Python API
4. Scaffold `server/` directory structure
5. Implement `/health` and `/transcribe` first (simplest, no async)
6. Test transcription with a real voice message
7. Implement job queue + `/separate`
8. Implement `/generate` (ACE-Step)
9. Scaffold Telegram bot, connect to API
10. Implement `/notes`
