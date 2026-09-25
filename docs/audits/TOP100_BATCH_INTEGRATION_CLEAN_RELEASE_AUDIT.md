# Top-100 Batch Integration Clean Release Audit

## Integrated files

- `TOP100_AUTO_README.md`
- `TOP100_DEMOS_README.md`
- `TOP100_CRACKTROS_README.md`
- `validate_top100_manifest.py`
- `validate_top100_demos_manifest.py`
- `validate_top100_cracktros_manifest.py`
- `convert_top100_demos_exact.sh`
- `convert_top100_cracktros_exact.sh`
- `convert_top100_cracktros_hvsc.sh`
- `convert_top100_cracktros_hvsc.py`

## Added support files

- `convert_top25_hvsc.py`
- `convert_top100_hvsc.py`
- `convert_top100_exact.sh`
- `convert_top100_demos_hvsc.py`
- `convert_top100_demos_hvsc.sh`
- `tests/test_top100_batch_integration.py`

## Runtime policy

The Top-100 wrappers reuse the final SID2MIDI runtime and final-perfect NMOS CPU core. The exact wrappers use:

```text
--auto --seconds 600 --auto-min-seconds 540 --auto-confirm-windows 3 --ppq 9600
```

This preserves high-resolution timing, avoids very short false loop detections and caps conversion at five minutes per SID/subtune.

## Resolver policy

- Classic Top-100 uses strict candidate path/name/stem matching, then deterministic local HVSC auto-fill.
- Demo Top-100 rejects generic `Demo_Tune.sid` collapse unless the exact seeded path exists.
- Cracktro Top-100 rejects generic `Intro.sid`, `Loader.sid`, `Music.sid`, `Cracktro.sid` collapse unless exact seeded path exists.
- Validators flag failed/weak/missing/duplicate/suspicious rows.

## Validation

The release validation now compiles the Top-100 scripts and runs a fake-HVSC dry-run test for classic, demo and cracktro flows.
