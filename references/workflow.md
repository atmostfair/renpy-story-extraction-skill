# Ren'Py Story Extraction Workflow

## Common Script Locations

- Normal Ren'Py project: `game/**/*.rpy`
- Decompiled Android package: `assets/x-game/**/*.rpy`
- Ripples-like Android build: `assets/x-game/x-scripts/*.rpy`
- Localization: `game/tl/<language>/*.rpy` or `assets/x-game/tl/<language>/*.rpy`

Always ignore `.rpyc` when `.rpy` exists. `.rpyc` is compiled bytecode and is not the reliable source for text extraction.

If exact-extension checks find no `.rpy` files but `.rpyc` files are present, decompile first:

```powershell
unrpyc ./
```

`unrpyc` recurses into subdirectories, so running it at the project root covers unpacked desktop projects and many Android unpack directories. Use a narrower path when appropriate:

```powershell
unrpyc ./assets
unrpyc ./assets/x-game
```

After decompilation, rerun the exact-extension check and continue with the generated `.rpy` files. Do not extract directly from `.rpyc`.

## File Roles

Likely story files:

- Episode/chapter names: `e1s1`, `ep2sc3`, `episode9`, `script`, `chapter`, `story`
- Files with many labels, dialogue lines, menus, and jumps

Likely support files:

- `variables.rpy`: Character definitions and defaults
- `screens.rpy`, `myscreens.rpy`: UI
- `images.rpy`: image definitions
- `music_data.rpy`: music metadata
- `options.rpy`, `gui.rpy`: settings
- `other.rpy`: helper code, transforms, minigames, custom text tags
- `textmessages.rpy`: may be UI helpers or actual message content; inspect before including/excluding

## Determine Order

Use jump/call flow, not filenames:

```powershell
rg -n "^\s*label\s+|^\s*jump\s+|^\s*call\s+" <scripts> --glob "*.rpy"
```

Look for:

- Entry labels: `start`, `intro`, `introStory`, `episodeN`, `epNsc1`
- End-of-file jumps to the next episode
- Recap jumps: `jump ep7recap`, `jump ep8recap`, etc.
- Files that contain many independent labels

When a recap or helper file contains labels that are jumped into by different chapters, split it by label. Do not append the entire file at the end.

Important pattern:

```renpy
label ep8recap:
    jump e8s1
    centered "Previously on Ripples"
    ...
```

Only the label and first jump are reachable. The visible recap text after the jump is not shown in normal flow. Do not extract that text unless the user explicitly asks for unreachable/dead script content.

## JSON Config Pattern

Prefer a project-specific config:

```json
{
  "story_units": [
    {"file": "x-intro.rpy"},
    {"file": "x-e1s1.rpy"},
    {"file": "x-e6s1.rpy", "start": "episode6", "end": "ep6recap"},
    {"file": "x-e6s1.rpy", "start": "ep6recap", "until_first_jump": true},
    {"file": "x-e6s1.rpy", "start": "e6s1"},
    {"file": "x-e7s1.rpy", "start": "episode7", "end": "e7s1"},
    {"file": "x-recap.rpy", "start": "ep7recap", "until_first_jump": true},
    {"file": "x-e7s1.rpy", "start": "e7s1"}
  ],
  "skip_files_by_default": ["x-intro.rpy"],
  "substitutions": {
    "playerName": "Jack",
    "playerNameL": "Wilson",
    "playerNameA": "Donnie"
  },
  "exclude_ui_texts": [
    "Pick a contact.",
    "Done Reading Text",
    "Are you at least 18 years old?"
  ],
  "message_senders": {
    "darcitxt.png": "Darci",
    "jessicatxt.png": "Jessica",
    "skylartxt.png": "Skylar",
    "skylartxt1.png": "Skylar",
    "tiffanytxt.png": "Tiffany"
  }
}
```

## Extraction Patterns

Dialogue:

```regex
^\s*(?:(?P<speaker>[A-Za-z_][\w.]*)\s+)?"(?P<text>(?:[^"\\]|\\.)*)"(?:\s+with\s+[A-Za-z_][\w.]*)?\s*$
```

Menu option:

```regex
^\s*"(?P<text>(?:[^"\\]|\\.)*)"\s*(?:\([^#]*\))?\s*(?:if\s+.*?)?:?\s*$
```

Phone messages:

```regex
^\s*call\s+(?P<func>message_img|reply_message)\s*\((?P<args>.*)\)\s*(?:from\s+.*)?$
```

Character definitions:

```regex
^define\s+(?P<key>[A-Za-z_]\w*)\s*=\s*Character\((?P<name>None|"(?:[^"\\]|\\.)*")
```

Default string variables:

```regex
^default\s+(?P<key>[A-Za-z_]\w*)\s*=\s*(?:\((?P<pquoted>"(?:[^"\\]|\\.)*")\)|(?P<quoted>"(?:[^"\\]|\\.)*"))
```

Variable rendering:

- `[playerName]` -> default/substitution value
- `[playerName!u]` -> uppercase value
- `[playerName.upper()]` -> uppercase value
- `{pf=playerName}` -> possessive/simple substitution if relevant

## Keep vs Exclude

Keep:

- Character dialogue
- Narration
- Thought-character dialogue such as `mcT`
- Story choices
- Story-centered transition/action summaries
- Phone/message text calls
- Branch alternatives if the user wants all possible player-visible story text

Exclude:

- Asset paths and file names
- `play`, `scene`, `show`, `hide`, `imagebutton`, `textbutton`, `screen`, `style`, transform code
- Age gates and platform prompts unless requested
- Text input prompts such as "Please enter your name"
- Phone contact-list menu labels if they only navigate message reading
- Music/gallery metadata
- Unreachable text after an unconditional jump

## Audit Commands

Search for unresolved variables:

```powershell
$env:PYTHONIOENCODING='utf-8'
@'
from pathlib import Path
import re
text = Path("story_text.txt").read_text(encoding="utf-8")
print(sorted(set(re.findall(r"\[[^\]\n]+\]", text))))
'@ | python -
```

Search for tags/resources:

```powershell
rg -n "\{[^}\n]+\}|audio/|images/|gui/|\.(png|jpg|jpeg|webp|mp3|ogg|webm)\b" story_text.txt
```

Reverse-audit missed quoted strings:

```powershell
$env:PYTHONIOENCODING='utf-8'
@'
from pathlib import Path
import re
root = Path("assets/x-game/x-scripts")
miss = []
for p in root.glob("*.rpy"):
    if p.suffix == ".rpyc":
        continue
    for i, line in enumerate(p.read_text(encoding="utf-8", errors="replace").splitlines(), 1):
        s = line.strip()
        if '"' not in s or s.startswith(("#", "$")):
            continue
        first = s.split(None, 1)[0].rstrip(":") if s.split(None, 1) else ""
        if first in {"play","queue","scene","show","hide","add","imagebutton","textbutton","text","define","default","style","screen","transform","image","if","elif"}:
            continue
        miss.append((p.name, i, s[:220]))
print("miss count", len(miss))
for row in miss[:120]:
    print(row)
'@ | python -
```

Classify misses manually. Only add new extraction rules for text a player can actually read in normal gameplay.

## Delivery Checks

Before final delivery, report:

- Which files/units were included and skipped
- Whether `.rpyc` was ignored
- How order was determined
- Output paths
- Counts for dialogue, narration, choices, messages if available
- Residual limitations, especially user-selected names, branch alternatives, localization, and unreachable/dead script content
