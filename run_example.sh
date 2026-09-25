#!/usr/bin/env bash
set -euo pipefail
export PYTHONDONTWRITEBYTECODE=1
DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$DIR"
OUT="${1:-/tmp/simple_pulse_sid2midi.mid}"
python3 sid2midi.py examples/simple_pulse.sid --seconds 1 --report -o "$OUT"
echo "Wrote: $OUT"
