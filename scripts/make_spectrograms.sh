#!/usr/bin/env bash
# Generate log-frequency spectrograms for the demo tracks.
#
# Why ffmpeg and not librosa: the project deliberately installs nothing natively
# on the Mac (everything runs in Docker), and ffmpeg is already a dependency
# (torchaudio uses it for MP3). showspectrumpic gives a reproducible, single-panel
# mono spectrogram with frequency/time/dBFS axes — more informative than the
# amplitude-only waveforms.
#
# Usage: bash scripts/make_spectrograms.sh
# Output: result-test/spectrograms/<genre>.png  (one per demo track)
#
# The demo set is defined as the tracks that have a waveform PNG — this excludes
# the demucs separation stems (bass/drums/other) and first_ai_music.
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
SRC="$ROOT/result-test"
WAVEFORMS="$SRC/waveforms"
OUT="$SRC/spectrograms"
mkdir -p "$OUT"

for wf in "$WAVEFORMS"/*.png; do
    name="$(basename "$wf" .png)"
    mp3="$SRC/$name.mp3"
    if [[ ! -f "$mp3" ]]; then
        echo "skip $name (no mp3)" >&2
        continue
    fi
    ffmpeg -hide_banner -loglevel error -y -i "$mp3" \
        -lavfi "aformat=channel_layouts=mono,showspectrumpic=s=760x300:legend=1:color=viridis:scale=log" \
        "$OUT/$name.png"
    echo "spectrogram: $name"
done
