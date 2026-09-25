# How to make a release

Run all commands from the project root.

```bash
./validate_release.sh
./validate_distribution.sh
./run_full_tests.sh
python3 tools/verify_sha256.py
```

Before zipping:

```bash
find . -name '__pycache__' -type d -prune -exec rm -rf {} +
find . -name '*.pyc' -delete
```

Regenerate `SHA256SUMS.txt` after every documentation or code change:

```bash
python3 - <<'SHA_REGEN'
from pathlib import Path
import hashlib
root = Path('.')
paths = sorted(p for p in root.rglob('*') if p.is_file() and p.name != 'SHA256SUMS.txt')
with open('SHA256SUMS.txt', 'w', encoding='utf-8') as out:
    for p in paths:
        h = hashlib.sha256(p.read_bytes()).hexdigest()
        out.write(f'{h}  {p.as_posix()}\n')
SHA_REGEN
```

Package with a stable root folder:

```bash
cd ..
zip -qr sidtrace2midi_<release_name>.zip sidtrace2midi   -x '*/__pycache__/*' '*.pyc' '.DS_Store'
unzip -t sidtrace2midi_<release_name>.zip
```
