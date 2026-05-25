import sys
from types import SimpleNamespace
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import renpy_story_extract as extractor  # noqa: E402


def test_named_none_character_speaker_renders_as_narration(tmp_path):
    source_dir = tmp_path / "game"
    source_dir.mkdir()
    (source_dir / "characters.rpy").write_text(
        'define sys = Character(name=None)\n',
        encoding="utf-8",
    )

    substitutions, speakers = extractor.parse_substitutions_and_speakers(
        source_dir,
        {"variable_files": ["characters.rpy"]},
    )
    items, stats = extractor.extract_items(
        ['sys "Before we begin."'],
        speakers,
        substitutions,
        {},
    )

    assert items == ["Before we begin."]
    assert stats["unknown_speakers"] == set()


def test_speaker_map_text_variables_are_cleaned(tmp_path):
    source_dir = tmp_path / "game"
    source_dir.mkdir()
    (source_dir / "variables.rpy").write_text(
        'default history_lucy = "Lucy {i}wasn\\\'t{/i} wrong."\n',
        encoding="utf-8",
    )
    (source_dir / "story.rpy").write_text(
        'label start:\n    "Visible."\n',
        encoding="utf-8",
    )
    config = tmp_path / "config.json"
    config.write_text(
        '{"story_units":[{"file":"story.rpy"}],"variable_files":["variables.rpy"]}',
        encoding="utf-8",
    )
    speaker_map = tmp_path / "speaker_map.txt"

    extractor.command_extract(
        SimpleNamespace(
            source_dir=source_dir,
            config=config,
            output=tmp_path / "story_text.txt",
            speaker_map=speaker_map,
            include_skipped=False,
            with_headers=False,
        )
    )

    assert "[history_lucy] = Lucy wasn't wrong." in speaker_map.read_text(encoding="utf-8")
    assert "{i}" not in speaker_map.read_text(encoding="utf-8")
