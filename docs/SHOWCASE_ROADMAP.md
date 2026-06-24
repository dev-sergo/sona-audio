# sona-audio — Showcase Roadmap

> Forward-looking plan for turning sona-audio into a finished, honest showcase.
> Each **session** below is self-contained — pick one, finish it, ship it.
> Status legend: `[ ]` todo · `[~]` in progress · `[x]` done.
> Tags: **(no-GPU)** doable on the Mac · **(GPU)** needs the RTX 3090 GPU box.

Created 2026-06-24.

---

## Where this project stands

The architecture (Mac ↔ GPU-box split), transcription, separation, notes and translation
all work end-to-end. The **music-generation pipeline does not** — `/acestep` is a 501 stub;
the 13 demo tracks were made directly in ComfyUI. The README is now honest about this, but
**internal docs still contradict it**, and there's repo hygiene to clean up.

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
- [x] `.env.example:28` — leaked personal username **and** hardcoded a ComfyUI-specific path → replaced with `<path-to-ace-step-models>` placeholder; `model_server/config.py:12` default emptied (must be set via `ACESTEP_MODEL_PATH`; no `~` expansion in pydantic). Also: `Makefile` venv path → overridable `VENV ?=` var; stale `server/config.py` `llm_model` default → real gemma model.
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

## S1 — Finish ACE-Step integration (GPU) — *the core blocker*

Until this works, the project is a benchmark stand, not a music studio. This is the one
session that changes the project's identity.

- [ ] Study the kijai ACE-Step node / Python API (reference in `model_server/main.py:168-170`).
- [ ] Implement `/acestep` in `model_server/main.py` (replace the 501 stub): load weights from `settings.acestep_model_path`, lazy-load when VRAM > threshold, return audio.
- [ ] Confirm `server/services/acestep_service.py` → `/acestep` round-trips, and `/generate` → job queue → result works end-to-end.
- [ ] Test via curl and via the Telegram `/generate` wizard.
- [ ] Document seed/determinism behaviour (can a demo be regenerated exactly?).
- [ ] Flip the README **Status** table + feature table from `🧪 API WIP` to `✅ working`, and update the benchmark footnote.

**Payoff:** delivers on the headline promise; turns sona into a real third showcase pillar.

---

## S2 — Audio presentation (partial-GPU)

Make the demos legible on a platform that can't play them inline.

- [ ] Generate **spectrograms** alongside the existing waveforms (librosa + matplotlib) — they show frequency content, more informative than amplitude alone. Commit small PNGs next to `result-test/waveforms/`.
- [ ] Add a **generation-params table** per demo track (lyrics, style, seed, duration) for reproducibility — once S1 makes them reproducible.
- [ ] (optional) A minimal inline player: Gradio UI bolted onto FastAPI, or a GitHub Pages page with `<audio>` tags, linked from the README.
- [ ] (optional) A short A/B section: same lyrics, different styles — shows controllability.
- [ ] (optional) Add a generated-content license note (e.g. CC0) for the demo tracks.

**Payoff:** turns "13 download links" into a browsable, reproducible gallery.

---

## S3 — Benchmark methodology doc (no-GPU, short)

The README benchmark table (transcription ~4s, separation ~45s, translation ~2s,
generation ~10s) is currently asserted with no backing.

- [ ] Create `docs/BENCHMARKS.md`: hardware, exact inputs, how each number was measured, and (after S1) the generation timing.
- [ ] Link it from the README (replaces the "coming soon" dangling reference from S0).

**Payoff:** closes the loop on the "model benchmark bench" framing and makes the numbers credible.

---

## Out of scope (for now)

- TTS with voice cloning (XTTS v2) — already marked planned; revisit after generation ships.
- YouTube/SoundCloud features beyond current yt-dlp support.
- Multi-GPU / scaling — single 3090 is the target.
