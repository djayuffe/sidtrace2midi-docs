# SIDTrace2MIDI ASCII-art logo

Use this logo in terminal output, README headers, release notes or demo screenshots.

```text
  _____ _____ _____ _______                  ___ __  __ _____ _____ _____  _____ 
 / ____|_   _|  __ \__   __|                |__ \  \/  |_   _|  __ \_   _|/ ____|
| (___   | | | |  | | | |_ __ __ _  ___ ___   ) | \  / | | | | |  | || | | (___  
 \___ \  | | | |  | | | | '__/ _` |/ __/ _ \ / /| |\/| | | | | |  | || |  \___ \ 
 ____) |_| |_| |__| | | | | | (_| | (_|  __// /_| |  | |_| |_| |__| || |_ ____) |
|_____/|_____|_____/  |_|_|  \__,_|\___\___|____|_|  |_|_____|_____/_____|_____/ 

          SID / PSID / RSID  ->  C64 player execution  ->  SID register trace  ->  MIDI
```

## Short terminal banner

```text
SIDTrace2MIDI :: SID/PSID/RSID -> SID register trace -> MIDI
```

## Naming rule

Do **not** call this project `midi2sid`. The data direction is the opposite: the tool runs SID player code, captures SID register writes, and exports MIDI.
