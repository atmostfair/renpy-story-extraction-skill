from pathlib import Path
import argparse
import ast
import json
import re
import sys


SUPPORT_FILE_HINTS = {
    "variables", "screens", "myscreens", "images", "music", "music_data",
    "options", "gui", "other", "hamster", "gallery", "preferences"
}

RESOURCE_PREFIXES = ("audio/", "images/", "gui/", "phone_", "hamster_")

COMMAND_WORDS = {
    "scene", "show", "hide", "play", "queue", "add", "imagebutton",
    "textbutton", "text", "button", "label", "jump", "call", "if", "elif",
    "else", "menu", "return", "pause", "with", "stop", "window", "default",
    "define", "screen", "style", "transform", "init", "python", "for",
    "while", "old", "new", "translate"
}

DIALOGUE_RE = re.compile(
    r'^\s*(?:(?P<speaker>[A-Za-z_][\w.]*)\s+)?'
    r'"(?P<text>(?:[^"\\]|\\.)*)"'
    r'(?:\s+with\s+[A-Za-z_][\w.]*)?\s*$'
)
MENU_RE = re.compile(
    r'^\s*"(?P<text>(?:[^"\\]|\\.)*)"\s*'
    r'(?:\([^#]*\))?\s*'
    r'(?:if\s+.*?)?:?\s*$'
)
MESSAGE_CALL_RE = re.compile(
    r'^\s*call\s+(?P<func>message_img|reply_message)\s*'
    r'\((?P<args>.*)\)\s*(?:from\s+.*)?$'
)
CHARACTER_RE = re.compile(
    r'^define\s+(?P<key>[A-Za-z_]\w*)\s*=\s*Character\('
    r'(?:name\s*=\s*)?(?P<name>None|"(?:[^"\\]|\\.)*")'
)
DEFAULT_RE = re.compile(
    r'^default\s+(?P<key>[A-Za-z_]\w*)\s*=\s*'
    r'(?:\((?P<pquoted>"(?:[^"\\]|\\.)*")\)|(?P<quoted>"(?:[^"\\]|\\.)*"))'
)
DEFINE_STRING_RE = re.compile(
    r'^define\s+(?P<key>[A-Za-z_]\w*)\s*=\s*'
    r'(?:\((?P<pquoted>"(?:[^"\\]|\\.)*")\)|(?P<quoted>"(?:[^"\\]|\\.)*"))'
)
STRING_ASSIGN_RE = re.compile(
    r'^\s*\$\s*(?P<key>[A-Za-z_]\w*)\s*=\s*'
    r'(?P<value>"(?:[^"\\]|\\.)*")\s*$'
)
LIST_ASSIGN_RE = re.compile(
    r'^\s*\$\s*(?P<key>[A-Za-z_]\w*)\s*=\s*'
    r'(?P<value>\[(?:[^"\\\]]|"(?:[^"\\]|\\.)*"|\\.)*\])\s*$'
)
RANDOM_CHOICE_RE = re.compile(
    r'^\s*\$\s*(?P<key>[A-Za-z_]\w*)\s*=\s*'
    r'renpy\.random\.choice\((?P<source>[A-Za-z_]\w*)\)\s*$'
)
INPUT_ASSIGN_RE = re.compile(r'^\s*\$\s*(?P<key>[A-Za-z_]\w*)\s*=\s*renpy\.input\(')
IF_EMPTY_RE = re.compile(r'^\s*if\s+(?P<key>[A-Za-z_]\w*)\s*==\s*""\s*:\s*$')
LABEL_RE = re.compile(r'^\s*label\s+(?P<label>[A-Za-z_]\w*)\s*:\s*$')
JUMP_RE = re.compile(r'^\s*jump\s+(?P<label>[A-Za-z_]\w*)\s*$')
CALL_LABEL_RE = re.compile(r'^\s*call\s+(?P<label>[A-Za-z_]\w*)\b')

TAG_RE = re.compile(
    r'\{/?(?:i|b|u|s|font(?:=[^}]*)?|size(?:=[^}]*)?|color(?:=[^}]*)?|'
    r'outlinecolor(?:=[^}]*)?|alpha(?:=[^}]*)?|glitch(?:=[^}]*)?|cps(?:=[^}]*)?)\}'
)
CONTROL_TAG_RE = re.compile(r'\{(?:w(?:=[^}]*)?|p|nw|fast|clear)\}')
IMAGE_TAG_RE = re.compile(r'\{image=[^}]+\}')
PF_TAG_RE = re.compile(r'\{pf=([A-Za-z_]\w*)\}')
REMAINING_TAG_RE = re.compile(r'\{[^}]+\}')
RENPY_LINK_RE = re.compile(r'\[\[([^\]]+)\]\]?')
VAR_RE = re.compile(r'\[([A-Za-z_]\w*)(?P<method>\.upper\(\))?(?P<conversion>![^\]]+)?\]')


def natural_key(value):
    return [int(part) if part.isdigit() else part.lower() for part in re.split(r"(\d+)", str(value))]


def load_config(path):
    if not path:
        return {}
    return json.loads(Path(path).read_text(encoding="utf-8"))


def all_rpy_files(source_dir):
    return sorted((p for p in Path(source_dir).rglob("*.rpy") if p.is_file()), key=lambda p: natural_key(p.as_posix()))


def rel_path(path, source_dir):
    return Path(path).resolve().relative_to(Path(source_dir).resolve()).as_posix()


def unescape_renpy_string(value):
    return (
        value.replace(r"\"", '"')
        .replace(r"\'", "'")
        .replace(r"\\", "\\")
        .replace(r"\n", "\n")
        .replace(r"\t", "\t")
    )


def strip_quotes(value):
    if value == "None":
        return None
    return unescape_renpy_string(value[1:-1])


def render_variables(text, substitutions):
    def replace_pf(match):
        key = match.group(1)
        value = substitutions.get(key, f"[{key}]")
        if value.endswith("s"):
            return value + "'"
        return value + "'s"

    def replace_var(match):
        key = match.group(1)
        value = substitutions.get(key, f"[{key}]")
        if match.group("method") == ".upper()" or match.group("conversion") == "!u":
            value = value.upper()
        return value

    text = PF_TAG_RE.sub(replace_pf, text)
    return VAR_RE.sub(replace_var, text)


def clean_text(text, substitutions):
    text = unescape_renpy_string(str(text))
    text = RENPY_LINK_RE.sub(r'\1', text)
    text = render_variables(text, substitutions)
    text = IMAGE_TAG_RE.sub("", text)
    text = TAG_RE.sub("", text)
    text = CONTROL_TAG_RE.sub("", text)
    text = REMAINING_TAG_RE.sub("", text)
    text = text.replace("%%", "%")
    text = re.sub(r"[ \t]+", " ", text)
    text = re.sub(r" *\n *", "\n", text)
    return text.strip()


def looks_like_resource(text):
    lowered = text.strip().lower()
    return lowered.startswith(RESOURCE_PREFIXES) or lowered.endswith(
        (".mp3", ".ogg", ".webm", ".png", ".jpg", ".jpeg", ".webp")
    )


def is_command_line(line):
    stripped = line.lstrip()
    if not stripped or stripped.startswith("#") or stripped.startswith("$"):
        return True
    first = re.split(r"\s+", stripped, 1)[0].rstrip(":")
    return first in COMMAND_WORDS


def label_pattern(label):
    return re.compile(rf"^\s*label\s+{re.escape(label)}\s*:\s*$")


def find_label(lines, label, start=0):
    pattern = label_pattern(label)
    for index in range(start, len(lines)):
        if pattern.match(lines[index]):
            return index
    raise ValueError(f"Label not found: {label}")


def first_jump_after_label(lines, start):
    for index in range(start + 1, len(lines)):
        if JUMP_RE.match(lines[index]):
            return index + 1
        stripped = lines[index].strip()
        if stripped and not stripped.startswith("#"):
            if not stripped.startswith(("scene ", "stop ", "pause", "$", "window ", "hide ", "show ")):
                # Keep scanning; some projects show splash setup before the first jump.
                pass
    raise ValueError(f"No jump found after label at line {start + 1}")


def unit_lines(path, unit):
    lines = Path(path).read_text(encoding="utf-8", errors="replace").splitlines()
    start = 0
    end = len(lines)
    if unit.get("start"):
        start = find_label(lines, unit["start"])
    if unit.get("end"):
        end = find_label(lines, unit["end"], start + 1)
    if unit.get("until_first_jump"):
        end = first_jump_after_label(lines, start)
    return lines[start:end]


def unit_name(unit):
    name = unit["file"]
    if unit.get("start"):
        name += f" :: {unit['start']}"
    if unit.get("end"):
        name += f" -> before {unit['end']}"
    if unit.get("until_first_jump"):
        name += " -> first jump"
    return name


def candidate_story_files(source_dir):
    candidates = []
    for path in all_rpy_files(source_dir):
        stem = path.stem.lower()
        if any(hint in stem for hint in SUPPORT_FILE_HINTS):
            continue
        lines = path.read_text(encoding="utf-8", errors="replace").splitlines()
        if any(LABEL_RE.match(line) or (DIALOGUE_RE.match(line) and not is_command_line(line)) for line in lines):
            candidates.append(path)
    return candidates


def default_story_units(source_dir):
    return [{"file": rel_path(path, source_dir)} for path in candidate_story_files(source_dir)]


def parse_substitutions_and_speakers(source_dir, config):
    substitutions = {}
    speakers = {}

    variable_files = config.get("variable_files")
    if variable_files:
        files = [Path(source_dir) / name for name in variable_files]
    else:
        files = [p for p in all_rpy_files(source_dir) if "variable" in p.stem.lower()]

    for path in files:
        if not path.is_file():
            continue
        for line in path.read_text(encoding="utf-8", errors="replace").splitlines():
            stripped = line.strip()
            default_match = DEFAULT_RE.match(stripped) or DEFINE_STRING_RE.match(stripped)
            if default_match:
                raw = default_match.group("pquoted") or default_match.group("quoted")
                substitutions.setdefault(default_match.group("key"), strip_quotes(raw))

    substitutions.update(config.get("substitutions", {}))

    for path in files:
        if not path.is_file():
            continue
        for line in path.read_text(encoding="utf-8", errors="replace").splitlines():
            match = CHARACTER_RE.match(line.strip())
            if not match:
                continue
            name = strip_quotes(match.group("name"))
            if name is not None:
                name = clean_text(name, substitutions)
            speakers[match.group("key")] = name

    for key, name in speakers.items():
        if name and key not in substitutions:
            substitutions[key] = name

    for key, value in config.get("substitutions", {}).items():
        substitutions[key] = value

    return substitutions, speakers


def parse_call_args(args_text):
    try:
        return ast.literal_eval(f"({args_text},)")
    except (SyntaxError, ValueError):
        return None


def infer_message_sender(image_path, message_senders):
    filename = Path(image_path).name.lower()
    if filename.startswith("dmeme"):
        return None
    return message_senders.get(filename, Path(image_path).stem)


def update_substitutions_from_assignment(line, substitutions, input_defaults, list_values, skip_empty_fallback_key=None):
    match = LIST_ASSIGN_RE.match(line)
    if match:
        try:
            values = ast.literal_eval(match.group("value"))
        except (SyntaxError, ValueError):
            return False
        if isinstance(values, list):
            list_values[match.group("key")] = [str(value) for value in values]
            return True
        return False

    match = RANDOM_CHOICE_RE.match(line)
    if match:
        values = list_values.get(match.group("source"))
        if values:
            substitutions[match.group("key")] = " / ".join(values)
        return True

    match = INPUT_ASSIGN_RE.match(line)
    if match:
        key = match.group("key")
        substitutions[key] = input_defaults.get(key, substitutions.get(key, ""))
        return True

    match = STRING_ASSIGN_RE.match(line)
    if match:
        key = match.group("key")
        if key == skip_empty_fallback_key:
            return True
        substitutions[key] = strip_quotes(match.group("value"))
        return True

    return False


def extract_items(lines, speakers, substitutions, config):
    items = []
    stats = {"dialogue": 0, "narration": 0, "choice": 0, "message": 0, "unknown_speakers": set()}
    input_defaults = dict(substitutions)
    list_values = {}
    last_if_empty_key = None
    include_choices = not config.get("no_choices", False)
    include_centered = not config.get("exclude_centered", False)
    exclude_ui_texts = set(config.get("exclude_ui_texts", []))
    message_senders = {k.lower(): v for k, v in config.get("message_senders", {}).items()}
    speaker_mode = config.get("speaker_mode", {})

    for line in lines:
        stripped = line.strip()
        if not stripped or stripped.startswith("#"):
            continue

        empty_match = IF_EMPTY_RE.match(line)
        if empty_match:
            last_if_empty_key = empty_match.group("key")
            continue

        if update_substitutions_from_assignment(line, substitutions, input_defaults, list_values, last_if_empty_key):
            last_if_empty_key = None
            continue
        last_if_empty_key = None

        message_call = MESSAGE_CALL_RE.match(line)
        if message_call:
            args = parse_call_args(message_call.group("args"))
            if not args:
                continue
            if message_call.group("func") == "reply_message":
                raw_text = args[0] if args else ""
                speaker = substitutions.get("playerName", "Player")
            else:
                raw_text = args[1] if len(args) > 1 else ""
                image_path = args[2] if len(args) > 2 else ""
                explicit_sender = args[0].strip() if args and isinstance(args[0], str) else ""
                speaker = explicit_sender or infer_message_sender(image_path, message_senders)
            text = clean_text(raw_text, substitutions)
            if text and speaker and text not in exclude_ui_texts:
                items.append(f"{speaker} [text]: {text}")
                stats["message"] += 1
            continue

        dialogue = DIALOGUE_RE.match(line)
        if dialogue and not is_command_line(line):
            speaker_key = dialogue.group("speaker")
            if speaker_key in {"centered", "my_centered"} and not include_centered:
                continue
            raw_text = dialogue.group("text")
            if looks_like_resource(raw_text):
                continue
            text = clean_text(raw_text, substitutions)
            if not text or text in exclude_ui_texts:
                continue
            speaker = speakers.get(speaker_key, speaker_key) if speaker_key else None
            if speaker_key in {"centered", "my_centered"}:
                speaker = None
            if speaker_key and speaker_key not in speakers:
                stats["unknown_speakers"].add(speaker_key)
            if speaker_key and speaker_mode.get(speaker_key):
                speaker = f"{speaker} ({speaker_mode[speaker_key]})"
            if speaker:
                items.append(f"{speaker}: {text}")
                stats["dialogue"] += 1
            else:
                items.append(text)
                stats["narration"] += 1
            continue

        if include_choices:
            menu = MENU_RE.match(line)
            if menu:
                raw_text = menu.group("text")
                if looks_like_resource(raw_text):
                    continue
                text = clean_text(raw_text, substitutions)
                if text and text not in exclude_ui_texts:
                    items.append(f"[Choice] {text}")
                    stats["choice"] += 1

    return items, stats


def command_scan(args):
    source_dir = Path(args.source_dir).resolve()
    output_dir = Path(args.output_dir).resolve()
    output_dir.mkdir(parents=True, exist_ok=True)

    labels = []
    jumps = []
    calls = []
    for path in all_rpy_files(source_dir):
        rel = rel_path(path, source_dir)
        for line_no, line in enumerate(path.read_text(encoding="utf-8", errors="replace").splitlines(), 1):
            label = LABEL_RE.match(line)
            if label:
                labels.append({"file": rel, "line": line_no, "label": label.group("label")})
            jump = JUMP_RE.match(line)
            if jump:
                jumps.append({"file": rel, "line": line_no, "target": jump.group("label")})
            call = CALL_LABEL_RE.match(line)
            if call and call.group("label") not in {"message_img", "reply_message"}:
                calls.append({"file": rel, "line": line_no, "target": call.group("label")})

    suggested = {
        "story_units": default_story_units(source_dir),
        "skip_files_by_default": [],
        "substitutions": {},
        "exclude_ui_texts": [],
        "message_senders": {}
    }
    scan = {"labels": labels, "jumps": jumps, "calls": calls, "suggested_config": suggested}
    (output_dir / "renpy_story_scan.json").write_text(json.dumps(scan, indent=2, ensure_ascii=False), encoding="utf-8")
    (output_dir / "renpy_story_suggested_config.json").write_text(json.dumps(suggested, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"Labels: {len(labels)}")
    print(f"Jumps: {len(jumps)}")
    print(f"Calls: {len(calls)}")
    print(f"Scan: {output_dir / 'renpy_story_scan.json'}")
    print(f"Suggested config draft: {output_dir / 'renpy_story_suggested_config.json'}")
    return 0


def command_merge(args):
    source_dir = Path(args.source_dir).resolve()
    config = load_config(args.config)
    story_units = config.get("story_units") or default_story_units(source_dir)
    skip = set(config.get("skip_files_by_default", []))
    parts = []
    merged = 0

    for unit in story_units:
        if unit["file"] in skip and not args.include_skipped:
            continue
        path = source_dir / unit["file"]
        if not path.is_file():
            print(f"Missing file: {path}", file=sys.stderr)
            return 1
        lines = unit_lines(path, unit)
        if not lines:
            continue
        merged += 1
        if not args.no_headers:
            parts.append(f"\n{'=' * 80}\n{unit_name(unit)}\n{'=' * 80}\n\n")
        parts.append("\n".join(lines).rstrip())
        parts.append("\n")

    output = Path(args.output).resolve()
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text("\n".join(parts).lstrip(), encoding="utf-8")
    print(f"Merged {merged} story units into: {output}")
    return 0


def command_extract(args):
    source_dir = Path(args.source_dir).resolve()
    config = load_config(args.config)
    story_units = config.get("story_units") or default_story_units(source_dir)
    skip = set(config.get("skip_files_by_default", []))
    substitutions, speakers = parse_substitutions_and_speakers(source_dir, config)

    output_items = []
    total = {"dialogue": 0, "narration": 0, "choice": 0, "message": 0, "unknown_speakers": set()}
    processed = 0

    for unit in story_units:
        if unit["file"] in skip and not args.include_skipped:
            continue
        path = source_dir / unit["file"]
        if not path.is_file():
            print(f"Missing file: {path}", file=sys.stderr)
            return 1
        items, stats = extract_items(unit_lines(path, unit), speakers, substitutions, config)
        if not items:
            continue
        processed += 1
        if args.with_headers:
            output_items.append(f"\n===== {unit_name(unit)} =====\n")
        output_items.extend(items)
        output_items.append("")
        for key in ("dialogue", "narration", "choice", "message"):
            total[key] += stats[key]
        total["unknown_speakers"].update(stats["unknown_speakers"])

    output = Path(args.output).resolve()
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text("\n".join(output_items).strip() + "\n", encoding="utf-8")

    if args.speaker_map:
        speaker_mode = config.get("speaker_mode", {})
        lines = ["# Character speaker keys"]
        for key in sorted(speakers):
            name = speakers[key] if speakers[key] is not None else '(narrator / no namebox)'
            if mode := speaker_mode.get(key):
                name = f"{name} ({mode})"
            lines.append(f"{key} = {name}")
        lines.append("")
        lines.append("# Text variables")
        for key in sorted(substitutions):
            if isinstance(substitutions[key], str):
                value = clean_text(substitutions[key], substitutions)
                lines.append(f"[{key}] = {value}")
        Path(args.speaker_map).resolve().write_text("\n".join(lines) + "\n", encoding="utf-8")

    print(f"Processed story units with visible text: {processed}")
    print(f"Dialogue lines: {total['dialogue']}")
    print(f"Narration lines: {total['narration']}")
    print(f"Choice lines: {total['choice']}")
    print(f"Phone/message lines: {total['message']}")
    print(f"Output: {output}")
    if total["unknown_speakers"]:
        print("Unknown speaker keys left as-is: " + ", ".join(sorted(total["unknown_speakers"])))
    return 0


def command_audit(args):
    text = Path(args.output).read_text(encoding="utf-8", errors="replace")
    bracket = sorted(set(re.findall(r"\[[^\]\n]+\]", text)))
    tags = sorted(set(re.findall(r"\{[^}\n]+\}", text)))
    resources = re.findall(r"(?:audio|images|gui)/|\.(?:png|jpg|jpeg|webp|mp3|ogg|webm)\b", text, flags=re.I)
    print("Bracket expressions:", bracket[:100])
    print("Tag expressions:", tags[:100])
    print("Resource-like matches:", len(resources))
    return 0


def main():
    parser = argparse.ArgumentParser(description="Scan, merge, and extract player-visible text from Ren'Py .rpy scripts.")
    sub = parser.add_subparsers(dest="command", required=True)

    scan = sub.add_parser("scan")
    scan.add_argument("--source-dir", required=True)
    scan.add_argument("--output-dir", required=True)
    scan.set_defaults(func=command_scan)

    merge = sub.add_parser("merge")
    merge.add_argument("--source-dir", required=True)
    merge.add_argument("--config")
    merge.add_argument("--output", required=True)
    merge.add_argument("--include-skipped", action="store_true")
    merge.add_argument("--no-headers", action="store_true")
    merge.set_defaults(func=command_merge)

    extract = sub.add_parser("extract")
    extract.add_argument("--source-dir", required=True)
    extract.add_argument("--config")
    extract.add_argument("--output", required=True)
    extract.add_argument("--speaker-map")
    extract.add_argument("--include-skipped", action="store_true")
    extract.add_argument("--with-headers", action="store_true")
    extract.set_defaults(func=command_extract)

    audit = sub.add_parser("audit")
    audit.add_argument("--output", required=True)
    audit.set_defaults(func=command_audit)

    args = parser.parse_args()
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
