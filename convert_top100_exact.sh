#!/usr/bin/env bash
set -euo pipefail
HVSC="${1:-/Users/ulfbertilsson/Downloads/C64Music}"
OUT="${2:-$HOME/Downloads/c64_top100_midi}"
shift $(( $# >= 1 ? 1 : 0 )) || true
shift $(( $# >= 1 ? 1 : 0 )) || true
DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
exec python3 "$DIR/convert_top100_hvsc.py" \
  --hvsc "$HVSC" \
  --out "$OUT" \
  --seconds 600 \
  --auto \
  --timeout 300 \
  --skip-existing \
  --keep-going \
  --min-notes 100 \
  --subtune-good-notes 500 \
  --song-scan-limit 32 \
  --ppq 9600 \
  --auto-min-seconds 540 \
  --auto-confirm-windows 3 \
  --subtune-probe-seconds 45 \
  --subtune-probe-timeout 60 \
  --subtune-probe-min-notes 20 \
  --subtune-zero-streak-limit 4 \
  --subtune-bad-streak-limit 6 \
  --subtune-scan-time-budget 240 \
  --max-full-subtune-renders 4 \
  --scan-policy preferred-first \
  --debug \
  "$@"
