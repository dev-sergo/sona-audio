# sona-audio — Showcase Roadmap

> Forward-looking plan for turning sona-audio into a finished, honest showcase.
> Each **session** below is self-contained — pick one, finish it, ship it.
> Status legend: `[ ]` todo · `[~]` in progress · `[x]` done.
> Tags: **(no-GPU)** doable on the Mac · **(GPU)** needs the RTX 3090 GPU box.

Created 2026-06-24. **Frozen 2026-06-26** as a portfolio snapshot.

> **This project is frozen as a portfolio piece.** S0 (hygiene), S2 (spectrograms) and
> S3 (benchmark doc) are done; the ACE-Step code/docs were reconciled to one coherent
> design (the dead `model_server` stub was removed). **S1 (actually running generation) is
> intentionally deferred** — the model is already proven by the 13 demo tracks, so wiring the
> last HTTP hop adds little showcase value relative to the cost. The list below is kept as a
> record of what "fully finished" would mean if the project is ever resumed.

---

## Where this project stands

The architecture (Mac ↔ GPU-box split), transcription, separation, notes and translation
all work end-to-end. **Music generation** is wired on the Mac side (`/generate` → job queue →
`acestep_service` → standalone ACE-Step API server at `:8002`) but that server isn't deployed
in this snapshot; the 13 demo tracks were made via the ACE-Step ComfyUI node (same model).
Code and docs now tell one consistent story about this seam.

Audio is also harder to show off than images: GitHub won't play inline audio, and audio gen
has fewer "knobs" than image/video — the quality levers are mostly **model + lyrics/style
conditioning + post-mastering**, not a deep prompt/pipeline search. So the payoff order here
is: **finish the core feature first, then improve presentation.**

### Priority / impact at a glance

| Session | Effort | Needs GPU | Impact |
|---|---|---|---|
| S0 — Doc cleanup & hygiene | 30 min | no | High (removes the rough edges + a privacy leak) |
| S1 — Finish ACE-Step | 1 session | **yes** | **Highest** (unblocks the core promise) |
| S2 — Audio presentation | 1 session | partial | Medium–High (makes the demos legible) |
| S3 — Benchmark doc | short | optional | Medium (closes a dangling reference) |

Recommended order: **S0 → S1 → S2 → S3.**

---

## S0 — Doc cleanup & repo hygiene (no-GPU, ~30 min)

From the 2026-06-24 audit. Fixes a privacy leak, a broken link, stale URLs, and aligns the
internal docs with the now-honest README.

**Hygiene / blockers:**
- [x] `.env.example:28` — leaked personal username **and** hardcoded a ComfyUI-specific path. (S0 swapped it for a placeholder; the later freeze cleanup **removed `ACESTEP_MODEL_PATH` / `acestep_model_path` entirely** — they belonged to the deleted `model_server` ACE-Step stub, not the real `:8002` design.) Also: `Makefile` venv path → overridable `VENV ?=` var; stale `server/config.py` `llm_model` default → real gemma model.
- [x] Stale repo URL with trailing dash `sona-audio-` (canonical is now `sona-audio`): fixed README `:8` (CI badge), `:111`, `:119` and CONTRIBUTING `:19`. Ran `git remote set-url origin https://github.com/dev-sergo/sona-audio.git`.
- [x] `docs/BENCHMARKS.md` linked "coming soon" but doesn't exist → **dropped** the dangling links (README + CONTRIBUTING); S3 recreates the doc and re-adds them.

**Honesty alignment (docs still claim generation works):**
- [x] `docs/API.md` — `/generate` documented as functional → added a 501/WIP banner linking README `#status`.
- [x] `docs/FEATURES.md` — Music Generation marked WIP with a status banner (model proven, service integration pending).
- [x] `docs/ARCHITECTURE.md` — `(TODO)` markers in the diagram + VRAM table updated to reflect actual state (weights present, API WIP, 501).
- [x] `docs/PROGRESS.md` — stripped personal absolute paths (`/Users/admin/...`); also fixed the one in `ARCHITECTURE.md` "How to Run".

**Nits:**
- [x] README `:3` — "model benchmark **bench**" → "model benchmark **suite**".
- [x] `docs/API.md:3` — base URL clarified: server runs on the **Mac**, delegates to the GPU box.

---

## S1 — Run music generation end-to-end (GPU) — *deferred, out of scope for the freeze*

The Mac-side integration is already built: `/generate` → job queue → `acestep_service`
(HTTP client) → standalone **ACE-Step API server** (`ACESTEP_URL`, :8002, `/release_task`
+ `/query_result`). The only missing piece is **running that server** — no in-repo code
change is needed. (Earlier drafts of this plan described implementing `/acestep` inside
`model_server`; that was a superseded design and its dead stub has been removed.)

If resumed, the shortest path:
- [ ] On the GPU box, launch the ACE-Step API server on `:8002` from the ACE-Step-1.5 project. No `conda` here, so run it from an env with the deps (e.g. ComfyUI's, where ACE-Step already works) rather than the standalone `run_api_server.sh` (which assumes conda + binds :8001).
- [ ] Point `ACESTEP_URL` at it; run `/generate` end-to-end (curl + the Telegram wizard).
- [ ] Document seed/determinism (can a demo be regenerated exactly?).
- [ ] Only after a real run: flip the README **Status** + feature table to `✅ working`, add the generation row to [BENCHMARKS.md](BENCHMARKS.md), and update the frozen banner.

**Why deferred:** the model is already proven by the 13 demo tracks; running the last HTTP
hop is real-but-low-leverage work for a frozen showcase, and carries setup risk (port
conflict with `model_server`, VRAM juggling with resident Whisper/Demucs/llama-swap).

---

## S2 — Audio presentation (partial-GPU)

Make the demos legible on a platform that can't play them inline.

- [x] Generate **spectrograms** alongside the existing waveforms — they show frequency content, more informative than amplitude alone. Committed as PNGs under `result-test/spectrograms/`, wired into the README demo table. *(Used ffmpeg `showspectrumpic` via [`scripts/make_spectrograms.sh`](../scripts/make_spectrograms.sh) instead of librosa — the project installs nothing natively on the Mac, and ffmpeg is already a dep.)*
- [ ] Add a **generation-params table** per demo track (lyrics, style, seed, duration) for reproducibility — once S1 makes them reproducible. *(blocked on S1)*
- [ ] (optional) A minimal inline player: Gradio UI bolted onto FastAPI, or a GitHub Pages page with `<audio>` tags, linked from the README.
- [ ] (optional) A short A/B section: same lyrics, different styles — shows controllability.
- [ ] (optional) Add a generated-content license note (e.g. CC0) for the demo tracks.

**Payoff:** turns "13 download links" into a browsable, reproducible gallery.

---

## S3 — Benchmark methodology doc (no-GPU, short)

The README benchmark table (transcription ~4s, separation ~45s, translation ~2s,
generation ~10s) is currently asserted with no backing.

- [x] Create `docs/BENCHMARKS.md`: hardware, inputs, reproduction commands. Framed honestly as indicative single-run figures (not rigorous averages — a re-measurement TODO is listed in the doc). Generation row left as _pending S1_.
- [x] Link it from the README + CONTRIBUTING (replaces the dangling references dropped in S0).

**Payoff:** closes the loop on the "model benchmark bench" framing and makes the numbers credible.

---

## Out of scope (for now)

- TTS with voice cloning (XTTS v2) — already marked planned; revisit after generation ships.
- YouTube/SoundCloud features beyond current yt-dlp support.
- Multi-GPU / scaling — single 3090 is the target.
