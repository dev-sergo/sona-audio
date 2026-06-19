# Testing

Two levels: automated tests (logic, no GPU) and manual API checks (real models).

## Automated tests

```bash
make test
```
Run in a python:3.11 container. Real calls to Whisper/LLM are mocked —
route logic, validation, and the DB are checked. Also run in CI on every push.

## Manual checks (no Telegram, via curl)

Precondition: `model_server` is up on the GPU box, `make up` on the Mac.

### 1. Everything alive
```bash
curl http://localhost:8000/health
```
Expect `"status":"ok"` with the loaded models inside `model_server`.

### 2. Transcription
```bash
curl -X POST http://localhost:8000/transcribe \
  -F "file=@voice.ogg" -F "language=auto"
```

### 3. Translation
```bash
curl -X POST http://localhost:8000/translate \
  -H "Content-Type: application/json" \
  -d '{"text":"dark beat","target_lang":"en"}'
```

### 4. Notes
```bash
curl -X POST http://localhost:8000/notes \
  -F "text=track idea: trap, 90 bpm"
curl http://localhost:8000/notes
curl "http://localhost:8000/notes?search=trap"
```

### 5. Stem separation (async)
```bash
curl -X POST http://localhost:8000/separate -F "file=@track.mp3"
# → {"job_id":"sep_xxxx"}
curl http://localhost:8000/jobs/sep_xxxx        # wait for status: done
curl -O http://localhost:8000/audio/sep_xxxx/vocals.wav
```

### 6. Music generation
```bash
curl -X POST http://localhost:8000/generate \
  -H "Content-Type: application/json" \
  -d '{"lyrics":"[verse]\nDark skies, empty streets","style":"dark trap, 90 bpm","duration_seconds":30}'
# → {"job_id":"gen_xxxx"}
curl http://localhost:8000/jobs/gen_xxxx        # wait for status: done
curl -O http://localhost:8000/audio/gen_xxxx/output.wav
```
Precondition: ACE-Step API running on GPU box at port 8002.

## Readiness checklist

| Check | Expected |
|---|---|
| health | ✅ |
| transcribe | ✅ |
| translate | ✅ (depends on llama-swap) |
| notes | ✅ |
| separate | ✅ |
| generate | ⏳ ACE-Step API server needed on GPU box |
