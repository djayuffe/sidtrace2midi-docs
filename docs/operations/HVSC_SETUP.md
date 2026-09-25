# HVSC setup guide

Top-100 conversion requires a local HVSC tree.  The converter does not download
HVSC for you.

## Expected path example

```text
/Users/ulfbertilsson/Downloads/C64Music
```

Typical subfolders include:

```text
DEMOS/
MUSICIANS/
GAMES/
```

## Verify quickly

```bash
find /Users/ulfbertilsson/Downloads/C64Music -name '*.sid' | head
```

## Run demo batch

```bash
./convert_top100_demos_exact.sh \
  /Users/ulfbertilsson/Downloads/C64Music \
  ~/Downloads/c64_top100_demos_midi
```

## Common mistakes

### Blank line after backslash in zsh

Do not write:

```bash
./convert_top100_demos_exact.sh \

  /Users/ulfbertilsson/Downloads/C64Music \
```

The blank line ends the command, and zsh may try to execute the path as a
program, causing `permission denied`.

### Wrong HVSC root

Point to the root containing `DEMOS`, `MUSICIANS` and similar directories, not to
a single subfolder unless you know what you are doing.
