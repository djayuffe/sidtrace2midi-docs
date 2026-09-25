# Step 04: Manifest triage and reruns

After a batch run, inspect the manifest.

## Analyze manifest

```bash
python3 tools/analyze_top100_manifest.py ~/Downloads/c64_top100_demos_midi/top100_demos_manifest.json --emit-rerun
```

This summarizes failed/weak rows and prints targeted rerun commands.

## Validate manifest

```bash
python3 validate_top100_demos_manifest.py ~/Downloads/c64_top100_demos_midi/top100_demos_manifest.json --min-notes 100
```

## Common statuses

- `ok`: accepted conversion.
- `failed`: no acceptable MIDI produced.
- `weak`: low-note result, usually only kept if explicitly allowed for debugging.

## Common reasons

- `notes-below-min`
- `subtune-zero-streak-*`
- `subtune-bad-streak-*`
- `subtune-probe-budget-*`
- `max-full-subtune-renders-*`
- `timeout`
- `init-budget`
