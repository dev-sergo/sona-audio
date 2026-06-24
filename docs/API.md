# API Reference

Base URL: `http://<mac-host>:8000` — the API server runs on the Mac; it delegates
inference to the GPU box over HTTP (see [ARCHITECTURE.md](ARCHITECTURE.md)).

All endpoints accept and return JSON unless noted (file uploads use multipart/form-data).
Async endpoints return `job_id` immediately. Poll `GET /jobs/{id}` for result.

---

## POST /transcribe

Transcribe audio to text.

**Request** — multipart/form-data
```
file: <audio file>  (ogg, mp3, wav, m4a)
language: "ru" | "en" | "auto"  (default: "auto")
```

**Response**
```json
{
  "text": "transcribed text",
  "language": "en",
  "duration_seconds": 12.4
}
```

**Notes**
- Synchronous (fast: ~1-3s for a 30s voice message on 3090)
- Whisper large-v3 loaded persistently in VRAM

---

## POST /separate

Split audio into stems: vocals / drums / bass / other.

**Request** — multipart/form-data
```
file: <audio file>  (mp3, wav, flac)
```

**Response** — async
```json
{
  "job_id": "sep_a1b2c3"
}
```

Poll `GET /jobs/sep_a1b2c3` for result:
```json
{
  "status": "done",
  "result": {
    "vocals": "/audio/sep_a1b2c3_vocals.wav",
    "drums":  "/audio/sep_a1b2c3_drums.wav",
    "bass":   "/audio/sep_a1b2c3_bass.wav",
    "other":  "/audio/sep_a1b2c3_other.wav"
  }
}
```

---

## POST /generate

Generate a song from lyrics + style.

> ⚠️ **Status: WIP.** This endpoint currently returns **501 Not Implemented** — the
> downstream `model_server:/acestep` is still a stub. The demo tracks in the README were
> produced via the ACE-Step ComfyUI node, not this endpoint. See
> [README → Status](../README.md#status). The request/response shape below is the target
> contract once the integration lands.

**Request** — JSON
```json
{
  "lyrics": "song or rap lyrics",
  "style": "hip-hop, dark, 90 bpm",
  "language": "en",
  "duration_seconds": 30
}
```

**Notes on fields**
- `language`: if `"ru"`, lyrics are auto-translated to EN before generation
- `style`: free-form tags, ACE-Step style. Examples: `"pop, upbeat"`, `"lo-fi, chill, instrumental"`
- `duration_seconds`: 15–120, default 30

**Response** — async
```json
{
  "job_id": "gen_x9y8z7"
}
```

Poll `GET /jobs/gen_x9y8z7` for result:
```json
{
  "status": "done",
  "result": {
    "audio": "/audio/gen_x9y8z7.wav",
    "lyrics_translated": "translated lyrics used for generation"
  }
}
```

---

## GET /jobs/{job_id}

Check status of any async job.

**Response**
```json
{
  "job_id": "gen_x9y8z7",
  "type": "generate",
  "status": "pending | running | done | error",
  "progress": 0.6,
  "result": { ... },
  "error": null,
  "created_at": "2026-06-10T12:00:00Z",
  "updated_at": "2026-06-10T12:00:45Z"
}
```

---

## GET /audio/{filename}

Serve generated audio file.

**Response** — audio/wav or audio/mpeg stream

---

## POST /notes

Save a smart note. If audio is provided — transcribe first, then summarize. If text — summarize directly.

**Request** — multipart/form-data OR JSON

With audio:
```
file: <audio file>
```

With text:
```json
{
  "text": "raw text or transcription"
}
```

**Response**
```json
{
  "id": 42,
  "title": "Auto-extracted title",
  "summary": "3-4 sentence summary",
  "tags": ["music", "idea", "beat"],
  "full_text": "original transcribed/input text",
  "created_at": "2026-06-10T12:00:00Z"
}
```

---

## GET /notes

List notes, newest first.

**Query params**
```
limit: int  (default 10)
offset: int (default 0)
search: str (optional, searches title + full_text + tags)
```

**Response**
```json
{
  "notes": [
    {
      "id": 42,
      "title": "Track idea",
      "tags": ["music", "rap"],
      "created_at": "2026-06-10T12:00:00Z"
    }
  ],
  "total": 15
}
```

---

## GET /notes/{id}

Get full note.

**Response** — same as POST /notes response

---

## POST /translate

Translate text between RU and EN.

**Request** — JSON
```json
{
  "text": "text to translate",
  "target_lang": "en"
}
```

**Response**
```json
{
  "text": "text for translation",
  "source_lang": "ru",
  "target_lang": "en"
}
```

---

## GET /health

Health check.

```json
{
  "status": "ok",
  "models": {
    "whisper": "loaded",
    "demucs": "loaded",
    "acestep": "unloaded"
  },
  "vram_free_gb": 11.2
}
```

---

## Error Format

All errors return HTTP 4xx/5xx with:
```json
{
  "error": "short_code",
  "message": "Human readable description"
}
```

Common errors:
- `unsupported_format` — audio format not accepted
- `file_too_large` — file exceeds limit
- `job_not_found` — unknown job_id
- `model_loading` — model is loading, retry in a few seconds
- `vram_unavailable` — not enough VRAM to load model
