# Features

## MVP (first working version)

### 1. Transcription
Convert any audio to text. Primary use: Telegram voice messages.

- Input: audio file (ogg, mp3, wav, m4a)
- Languages: RU + EN, auto-detect
- Output: text, detected language, duration
- Model: faster-whisper large-v3 (CUDA)
- Bot command: send voice message or audio file → get text back

### 2. Music Generation
Text + style → full song with vocals.

- Input: lyrics (text), style/genre tags (e.g. "hip-hop, russian, dark beat"), duration
- Language: EN or RU. If RU detected → auto-translate to EN before generation
- Output: audio file (mp3/wav)
- Model: ACE-Step-1.5 turbo (direct Python API)
- Async: returns job_id, result polled via /jobs/{id}
- Bot command: /generate → bot asks for lyrics → asks for style → generates → sends file

### 3. Stem Separation
Split any track into 4 stems: vocals / drums / bass / other.

- Input: audio file
- Output: 4 audio files as zip or individual files
- Model: demucs htdemucs (4-stem)
- Async: job-based (takes 30-120s depending on track length)
- Use cases: extract vocal from recording, get instrumental for karaoke, remix components
- Bot command: /separate → send audio → receive stems

### 4. Smart Notes
Voice or text → structured note stored in SQLite.

- Input: voice message OR typed text
- Processing: if voice → Whisper transcribes → LLM (llama-swap/qwen3) extracts title, summary, tags
- Output: note with title, summary, full text, tags, timestamp
- Bot commands:
  - Send voice/text in /note mode → saves note
  - /notes → list recent notes
  - /notes search <query> → search by text/tags

### 5. Auto-Translation
Transparent translation layer used internally and exposed as endpoint.

- RU → EN: before sending lyrics to ACE-Step
- EN → RU: optionally translate transcription result
- Via llama-swap (qwen3), simple prompt, no extra model
- Also exposed as /translate endpoint for direct use

---

## Later (post-MVP)

### Voice Transfer (RVC)
Record your rap/singing → transfer to different voice timbre or clean up your own.
Requires: RVC model + training on voice samples.

### Lyrics Workshop
LLM-assisted lyrics writing: suggest rhymes, fix rhythm, generate alternative lines.
Input: partial lyrics or idea. Output: improved/expanded lyrics ready for /generate.

### Around-Authorial Pipeline
Full creative pipeline:
1. Record your live vocal/rap
2. Whisper extracts text + word timings
3. librosa detects BPM/key
4. ACE-Step generates instrumental matching BPM
5. time-stretch vocal to grid
6. Mix: live vocal + AI instrumental → final track

### Track Version History
Keep all /generate runs with parameters (lyrics, style, seed).
Compare versions, reuse seeds, mark favorites.

### Auto-Cleanup Cron
Delete audio files older than N days. Configurable threshold.
Design: separate script, run via cron or systemd timer.

### Gradio Web UI
Quick browser UI for non-bot access. Useful for longer sessions or file management.

---

## Telegram Bot Command Map

| Command | Action |
|---|---|
| (voice message) | Auto-transcribe and show text |
| /generate | Wizard: ask lyrics → ask style → generate track |
| /separate | Ask for audio file → separate stems → send zip |
| /note | Save next voice/text message as smart note |
| /notes | List last 10 notes |
| /translate | Translate next message RU↔EN |
| /status `<job_id>` | Check async job status |
| /help | Show all commands |
