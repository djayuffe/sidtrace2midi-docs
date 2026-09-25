# Release Process

Use this when modifying the package and producing a clean zip.

## 1. Clean generated files

```bash
find . -type d -name __pycache__ -prune -exec rm -rf {} +
find . -type f -name '*.pyc' -delete
```

## 2. Run validation

```bash
./validate_release.sh
./validate_distribution.sh
./run_full_tests.sh
```

## 3. Regenerate SHA256SUMS

```bash
python3 - <<'PY'
from pathlib import Path
import hashlib
root = Path('.')
rows = []
for p in sorted(root.rglob('*')):
    if not p.is_file():
        continue
    if p.name == 'SHA256SUMS.txt':
        continue
    rel = p.relative_to(root).as_posix()
    rows.append(f"{hashlib.sha256(p.read_bytes()).hexdigest()}  {rel}\n")
Path('SHA256SUMS.txt').write_text(''.join(rows), encoding='utf-8')
PY
python3 tools/verify_sha256.py
```

## 4. Zip from parent directory

```bash
cd ..
zip -qr sid2midi_nmos6502_sid2midi_documentation_plus_release.zip sid2midi_superhuman_cpu_nmos \
  -x '*/__pycache__/*' '*.pyc'
unzip -t sid2midi_nmos6502_sid2midi_documentation_plus_release.zip
```

## 5. Release checklist

- `README.md` names the correct release.
- `PROJECT_MANIFEST.md` lists new docs/tools/tests.
- `RELEASE_NOTES_NMOS_CPU.md` has a dated note.
- `SHA256SUMS.txt` validates.
- `validate_distribution.sh` passes from a clean unzip.
- zip test reports no errors.

