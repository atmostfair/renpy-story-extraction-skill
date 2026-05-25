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


def test_character_display_names_are_cleaned_for_story_and_speaker_map(tmp_path):
    source_dir = tmp_path / "game"
    source_dir.mkdir()
    (source_dir / "characters.rpy").write_text(
        (
            'define combo = Character("{color=#0059a7}[PlayerName]{/color} & '
            '{color=#1b7519}Lily{/color}")\n'
        ),
        encoding="utf-8",
    )
    (source_dir / "story.rpy").write_text(
        'label start:\n    combo "Together."\n',
        encoding="utf-8",
    )
    config = tmp_path / "config.json"
    config.write_text(
        (
            '{"story_units":[{"file":"story.rpy"}],'
            '"variable_files":["characters.rpy"],'
            '"substitutions":{"PlayerName":"You"}}'
        ),
        encoding="utf-8",
    )
    speaker_map = tmp_path / "speaker_map.txt"
    story_text = tmp_path / "story_text.txt"

    extractor.command_extract(
        SimpleNamespace(
            source_dir=source_dir,
            config=config,
            output=story_text,
            speaker_map=speaker_map,
            include_skipped=False,
            with_headers=False,
        )
    )

    assert "You & Lily: Together." in story_text.read_text(encoding="utf-8")
    assert "combo = You & Lily" in speaker_map.read_text(encoding="utf-8")
    assert "{color=" not in story_text.read_text(encoding="utf-8")
    assert "{color=" not in speaker_map.read_text(encoding="utf-8")


def test_python_phone_messages_and_choices_are_extracted_without_resource_paths():
    items, stats = extractor.extract_items(
        [
            '$ send_phone_message("Aine", "Hey, [mc].", "aine_dm", do_pause=False)',
            '$ send_phone_message(phone_config["phone_player_name"], "I am here.", "aine_dm")',
            '$ send_phone_message("Aine", "images/ch2ep1_18.jpg", "aine_dm", 2)',
            '$ present_phone_choices([("I miss you", "I miss you.", Jump("true")), ("Give me something", "Come on... give me something.", Jump("false"))], "aine_dm")',
        ],
        {},
        {"mc": "You", "phone_player_name": "You"},
        {},
    )

    assert items == [
        "Aine [text]: Hey, You.",
        "You [text]: I am here.",
        "[Choice] I miss you",
        "[Choice] Give me something",
    ]
    assert stats["message"] == 2
    assert stats["choice"] == 2


def test_speaker_overrides_and_whole_line_italics_render_as_thoughts(tmp_path):
    source_dir = tmp_path / "game"
    source_dir.mkdir()
    (source_dir / "characters.rpy").write_text(
        '\n'.join(
            [
                'define yt = Character("Your Thoughts")',
                'define s = Character("Sky")',
            ]
        ),
        encoding="utf-8",
    )

    substitutions, speakers = extractor.parse_substitutions_and_speakers(
        source_dir,
        {
            "variable_files": ["characters.rpy"],
            "speaker_overrides": {"yt": "You"},
        },
    )
    items, stats = extractor.extract_items(
        [
            'yt "I need to stay calm."',
            's "{i}I hope he is okay.{/i}"',
            's "{color=#808080}{i}Wrapped thought.{/i}{/color}"',
            's "This is {i}still{/i} spoken."',
        ],
        speakers,
        substitutions,
        {"speaker_mode": {"yt": "thought"}},
    )

    assert items == [
        "You (thought): I need to stay calm.",
        "Sky (thought): I hope he is okay.",
        "Sky (thought): Wrapped thought.",
        "Sky: This is still spoken.",
    ]
    assert stats["dialogue"] == 4


def test_character_with_space_and_multiple_dialogue_arguments_are_extracted(tmp_path):
    source_dir = tmp_path / "game"
    source_dir.mkdir()
    (source_dir / "characters.rpy").write_text(
        'define nic = Character ("Nicole")\n',
        encoding="utf-8",
    )

    substitutions, speakers = extractor.parse_substitutions_and_speakers(
        source_dir,
        {"variable_files": ["characters.rpy"]},
    )
    items, stats = extractor.extract_items(
        [
            'nic "I am here." (multiple=2)',
            'nic "Still here." (multiple=2) with hpunch',
        ],
        speakers,
        substitutions,
        {},
    )

    assert items == [
        "Nicole: I am here.",
        "Nicole: Still here.",
    ]
    assert stats["dialogue"] == 2


def test_single_quoted_character_names_and_compact_dialogue_are_extracted(tmp_path):
    source_dir = tmp_path / "game"
    source_dir.mkdir()
    (source_dir / "characters.rpy").write_text(
        "\n".join(
            [
                "define yu = Character('Yukine')",
                "define wi = Character ('Wild')",
            ]
        ),
        encoding="utf-8",
    )

    substitutions, speakers = extractor.parse_substitutions_and_speakers(
        source_dir,
        {"variable_files": ["characters.rpy"], "speaker_overrides": {"mc": "You"}},
    )
    items, stats = extractor.extract_items(
        [
            'yu"Fu-Uhn!"',
            'wi" That works too."',
            'mc"I should still be normalized."',
        ],
        speakers,
        substitutions,
        {},
    )

    assert items == [
        "Yukine: Fu-Uhn!",
        "Wild: That works too.",
        "You: I should still be normalized.",
    ]
    assert stats["dialogue"] == 3


def test_configured_plain_wrapped_dialogue_renders_as_thoughts(tmp_path):
    source_dir = tmp_path / "game"
    source_dir.mkdir()
    (source_dir / "characters.rpy").write_text(
        'define m = Character("Moon")\n',
        encoding="utf-8",
    )

    substitutions, speakers = extractor.parse_substitutions_and_speakers(
        source_dir,
        {"variable_files": ["characters.rpy"]},
    )
    items, stats = extractor.extract_items(
        [
            'm "*I should not say this out loud.*"',
            'm " (I should stay calm.) "',
            'm "A regular line with *emphasis* stays spoken."',
            'm "A regular line with (aside) stays spoken."',
        ],
        speakers,
        substitutions,
        {"thought_wrappers": [["*", "*"], ["(", ")"]]},
    )

    assert items == [
        "Moon (thought): I should not say this out loud.",
        "Moon (thought): I should stay calm.",
        "Moon: A regular line with *emphasis* stays spoken.",
        "Moon: A regular line with (aside) stays spoken.",
    ]
    assert stats["dialogue"] == 4


def test_configured_plain_thought_prefix_handles_missing_closing_marker(tmp_path):
    source_dir = tmp_path / "game"
    source_dir.mkdir()
    (source_dir / "characters.rpy").write_text(
        'define m = Character("Moon")\n',
        encoding="utf-8",
    )

    substitutions, speakers = extractor.parse_substitutions_and_speakers(
        source_dir,
        {"variable_files": ["characters.rpy"]},
    )
    items, stats = extractor.extract_items(
        [
            'm "*This source line is missing the close marker"',
            'm "A regular line with *emphasis* stays spoken."',
        ],
        speakers,
        substitutions,
        {"thought_prefixes": ["*"]},
    )

    assert items == [
        "Moon (thought): This source line is missing the close marker",
        "Moon: A regular line with *emphasis* stays spoken.",
    ]
    assert stats["dialogue"] == 2


def test_unit_lines_can_extract_marker_ranges(tmp_path):
    story = tmp_path / "phone.rpy"
    story.write_text(
        "\n".join(
            [
                "init python:",
                "    def setup_phone():",
                '        text "UI only"',
                "    def reset_phone_data():",
                '        send_phone_message("Aine", "Visible history.", "aine_dm")',
                "    def phone_screen_helper():",
                '        text "UI chrome"',
            ]
        ),
        encoding="utf-8",
    )

    lines = extractor.unit_lines(
        story,
        {
            "file": "phone.rpy",
            "start_marker": "    def reset_phone_data(",
            "end_marker": "    def phone_screen_helper(",
        },
    )

    assert lines == [
        "    def reset_phone_data():",
        '        send_phone_message("Aine", "Visible history.", "aine_dm")',
    ]


def test_dotted_interpolation_variables_are_rendered_from_substitutions():
    items, stats = extractor.extract_items(
        [
            'mc "Morning [rel.m]."',
            'mc "[rel.MUP]!"',
            'mom "Where is [MC]?"',
        ],
        {"mc": "You", "mom": "Tasha"},
        {"rel.m": "mom", "rel.MUP": "MOM", "MC": "You"},
        {},
    )

    assert items == [
        "You: Morning mom.",
        "You: MOM!",
        "Tasha: Where is You?",
    ]
    assert stats["dialogue"] == 3
