# Benchmarks

Conditions and methodology behind the timing table in the [README](../README.md#benchmarks-rtx-3090-24-gb-vram).

> **Honesty note.** These are **indicative, single-run wall-clock** figures observed
> during manual end-to-end testing (session 4, see [PROGRESS.md](PROGRESS.md)), with models
> already resident in VRAM. They are **not** rigorous averaged benchmarks — no warmup
> sweep, no repeated runs, no percentiles. Treat them as "order of magnitude on a 3090",
> not as reproducible-to-the-millisecond claims. A proper re-measurement (N runs, warmup,
> p50/p95) is a TODO — see [below](#todo-rigorous-re-measurement).

---

## Hardware

| Component | Spec |
|---|---|
| GPU | NVIDIA RTX 3090, 24 GB VRAM |
| CUDA | 12.1 |
| PyTorch | 2.5.1+cu121 |
| Python | 3.10.6 (pyenv) |
| Inference server | `model_server/` FastAPI on `:8001` (native on the GPU box) |
| LLM runtime | llama-swap on `:8080`, model `gemma-4-26b-a4b-it-mxfp4-moe-ctx-32k-q8-0-kv-t07` |

The orchestration server (`server/`) runs on the Mac and calls the GPU box over HTTP, so
the figures below are **inference time on the GPU box** and exclude Mac↔box network latency
(both machines on the same LAN; latency is negligible relative to the inference times).

---

## Results

| Operation | Model | Input | Time |
|---|---|---|---|
| Transcription | faster-whisper large-v3 | 60 s voice message (OGG) | ~4 s |
| Stem separation | demucs htdemucs (4-stem) | 3 min track (MP3) | ~45 s |
| Translation (RU→EN) | gemma-4-26b MoE via llama-swap | ~200 tokens | ~2 s |
| Music generation | ACE-Step-1.5 turbo | 30–45 s track | _pending S1_ |

<sub>**Generation:** the ~10 s figure quoted historically was measured via the ACE-Step
**ComfyUI node**, not the in-repo `/generate` endpoint (which is still a 501 stub — see
[README → Status](../README.md#status)). It will be measured here once the endpoint is
wired up (roadmap S1).</sub>

Notes:
- **Whisper** and **demucs** are loaded persistently at startup, so the times above are
  steady-state (no model-load cost). Cold start adds a one-time load of a few seconds.
- **Translation** latency depends on llama-swap having the model already loaded; a cold
  model swap is slower and not reflected here.

---

## How to reproduce

Preconditions: `model_server` up on the GPU box, `make up` on the Mac (see
[TESTING.md](TESTING.md)). Time the round-trip from the Mac with `curl -w`:

```bash
# Transcription — 60 s OGG voice message
curl -s -o /dev/null -w "%{time_total}s\n" \
  -X POST http://localhost:8000/transcribe -F "file=@voice.ogg" -F "language=auto"

# Translation — short phrase
curl -s -o /dev/null -w "%{time_total}s\n" \
  -X POST http://localhost:8000/translate \
  -H "Content-Type: application/json" -d '{"text":"dark beat","target_lang":"en"}'
```

Stem separation and generation are async (return a `job_id`); time them by polling
`GET /jobs/{id}` until `status: done` and diffing `created_at` / `updated_at`.

---

## TODO: rigorous re-measurement

To turn these into credible benchmarks:
1. Fixed input fixtures committed to the repo (a reference 60 s OGG, a 3 min MP3).
2. A warmup run, then N≥10 timed runs; report p50 and p95, not a single sample.
3. Separate **model-load** time from **steady-state inference** time.
4. Add the generation row once S1 lands (seed fixed, so the timing is reproducible).
