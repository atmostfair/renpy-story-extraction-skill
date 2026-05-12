# Ren'Py Story Extraction Skill

**Repository name:** `renpy-story-extraction-skill`

[简体中文](README.zh-CN.md)

Ren'Py Story Extraction Skill is a Codex skill for working with Ren'Py visual novel scripts and preparing ordered, readable story reference material. The extracted text can be used as source material for tools such as NotebookLM, private knowledge bases, retrieval-augmented generation systems, localization review, continuity checking, story summarization, or other workflows that need narrative material as reference.

This repository is a skill package and workflow reference, not a traditional standalone executable application. It is designed for personal research, documentation, and authorized content processing. Do not redistribute copyrighted story text unless you own it or have explicit permission.

## Adaptive Skill Behavior

This skill is intended to improve through use. After a real extraction task, reusable lessons, project patterns, audit checks, and user preferences can be added back into the local `SKILL.md`. The skill then mirrors those updates one-way to the configured GitHub repository with an automatic commit message, giving maintainers and fork owners a living copy that gradually reflects their own source formats, review habits, and narrative-analysis needs.

If you fork this repository, your fork can become a personalized Ren'Py extraction skill. It keeps the shared workflow structure, while your repeated use teaches it the conventions and edge cases that matter in your own projects.

## What This Is For

Ren'Py games often store narrative content across many `.rpy` files, labels, route files, recap files, message systems, and UI helpers. Reading files alphabetically is rarely the same as reading the story in game order.

This repository provides a repeatable approach for extracting player-visible narrative text while preserving the structure that matters:

- ordered story units instead of one unverified dump
- speaker names and narrator text
- dialogue, inner thoughts, choices, messages, and meaningful on-screen text
- chapter, episode, route, or label boundaries
- a manifest that records where each output file came from
- audit checks for unresolved variables, Ren'Py tags, asset paths, and leaked UI metadata

## Common Use Cases

- **NotebookLM source uploads:** convert a visual novel script into clean text files that can be uploaded as sources for summaries, Q&A, timeline reconstruction, character analysis, and theme review.
- **Private reference corpus:** prepare story material for local search, note-taking systems, RAG pipelines, or private assistants.
- **Writing and continuity support:** compare routes, trace character arcs, check callbacks, and find contradictions across episodes.
- **Localization and editing:** isolate player-visible lines from code, assets, menus, and debug text.
- **Dataset preparation:** build a structured reference set for authorized model fine-tuning, evaluation, or synthetic-data generation.

## Important Notes

- Use `.rpy` source files whenever possible.
- If only `.rpyc` files are available, decompile them first with a tool such as `unrpyc`, then inspect the generated `.rpy` files. If `unrpyc` is not installed globally or is missing from `PATH`, use the bundled fallback at `scripts/unrpyc/unrpyc.py`.
- Do not assume file name order is story order. Determine order from Ren'Py `label`, `jump`, `call`, route controllers, episode lists, gallery/replay entries, and screen actions.
- Keep extracted output split into per-story files by default. A single merged file can be useful, but it should not replace ordered per-story outputs.
- Respect copyright, platform terms, and the license of the source material. Uploading text to AI tools or training systems may have legal or contractual implications.

## Self-Evolving Skill Sync

This repository is intended to be both a reusable skill and a living record of extraction lessons learned from real projects. After each extraction task, Codex should fold broadly reusable lessons back into the installed `SKILL.md` or linked references, validate the updated skill package, commit the documentation changes with a concise generated message, and push them to the configured GitHub remote.

The sync direction is intentionally one-way for learned behavior: local skill improvements are mirrored into the active repository checkout and pushed to `origin`. Before committing, Codex should fetch or pull the remote default branch. If a fork has its own remote changes, Codex should preserve both sides where possible, remove duplicate wording, keep the new local guidance, and then push the reconciled result.

Forks are expected to diverge constructively. When you fork this repository and use the skill on your own Ren'Py projects, the workflow can accumulate your project patterns, preferred extraction rules, naming conventions, and audit expectations in your fork instead of being locked to the upstream maintainer's habits.

## Recommended Repository Layout

```text
renpy-story-extraction-skill/
├─ README.md
├─ README.zh-CN.md
├─ SKILL.md
├─ scripts/
│  ├─ renpy_story_extract.py
│  └─ unrpyc/
├─ configs/
│  └─ example.project.json
├─ input/
│  └─ .gitkeep
├─ work/
│  └─ .gitkeep
└─ output/
   └─ .gitkeep
```

Suggested directory roles:

- `SKILL.md`: the core Codex skill instructions.
- `scripts/`: extractor scripts, audit helpers, and the bundled `unrpyc` fallback.
- `configs/`: project-specific extraction plans, speaker maps, ordering rules, and inclusion/exclusion settings.
- `input/`: temporary local source files. Usually keep real game files out of git.
- `work/`: scan results, jump graphs, notes, and intermediate files.
- `output/`: extracted story text and manifests. Commit only content you are allowed to publish.

## Workflow

### 1. Prepare the Script Source

Locate the Ren'Py script directory. Desktop builds commonly use `game/`. Android builds may place scripts under paths such as `assets/x-game/`.

If you already have `.rpy` files, use those. If you only have `.rpyc` files, decompile first:

```bash
unrpyc ./game
```

If `unrpyc` is not available globally, use the bundled fallback from this skill checkout:

```bash
python path/to/renpy-story-extraction-skill/scripts/unrpyc/unrpyc.py ./game
```

or, for an Android-style payload:

```bash
unrpyc ./assets
```

After decompilation, verify that real `.rpy` files exist before continuing.

### 2. Scan the Project

Identify story files, support files, labels, jumps, calls, character definitions, dynamic name variables, and custom visible-text helpers.

Example command if this repository includes `scripts/renpy_story_extract.py`:

```bash
python scripts/renpy_story_extract.py scan \
  --source-dir /path/to/game \
  --output-dir work/my-project-scan
```

The scan is only a starting point. Review the output manually before extracting.

### 3. Build an Extraction Config

Create a project-specific config in `configs/`. The config should describe:

- the ordered story units to extract
- source file and label ranges for each unit
- speaker mappings
- player-name normalization rules
- thought/speech distinctions
- custom message or phone-chat helpers
- text to include and text to ignore

Recommended output naming:

```text
story01_original-title.txt
story02_original-title.txt
story03_original-title.txt
```

Use project-provided chapter, episode, or route titles when available. Otherwise use a source file or label-based title.

### 4. Extract Ordered Text

Run the extractor with the reviewed config:

```bash
python scripts/renpy_story_extract.py extract \
  --source-dir /path/to/game \
  --config configs/my-project.json \
  --output-dir output/my-project
```

Recommended output:

```text
output/my-project/
├─ story01_prologue.txt
├─ story02_chapter-1.txt
├─ story03_chapter-2.txt
├─ story_index.txt
├─ story_manifest.json
└─ speaker_map.txt
```

### 5. Audit the Output

Before using the extracted text in NotebookLM or another system, audit it for leakage and unresolved markup.

Useful checks:

```bash
rg -n "audio/|images/|\\.png|\\.jpg|\\.webp|\\.mp3|\\.ogg|\\.webm" output/my-project
rg -n "\\[[^\\]\\n]+\\]" output/my-project
rg -n "\\{[^}\\n]+\\}" output/my-project
rg -n "^extend:|^label |^screen " output/my-project
```

Common issues to fix:

- resource paths accidentally extracted as story text
- unresolved Ren'Py variables such as `[player_name]`
- formatting tags such as `{i}`, `{w}`, `{p}`, or `{size=...}`
- thought lines rendered as ordinary spoken dialogue
- debug, gallery, settings, or menu text mixed into the narrative

### 6. Use the Text as Reference Material

For NotebookLM:

1. Upload the ordered `storyxx_*.txt` files.
2. Upload `story_index.txt` or `story_manifest.json` if the platform accepts it.
3. Ask questions against specific chapters, routes, characters, or themes.
4. Keep outputs split by story unit so the source order remains understandable.

For RAG or training workflows:

1. Chunk by story unit, label, scene, or chapter instead of arbitrary byte size.
2. Store source metadata such as file name, label, speaker, route, and sequence number.
3. Keep a manifest so generated answers can cite or trace back to source units.
4. Verify that your use is permitted by the content owner and the platform terms.

## Output Guidelines

Good extracted text should be readable without Ren'Py code knowledge:

```text
You: I should check the old station before sunset.
You (thought): Something about this place still feels wrong.

[Choice]
- Go to the platform.
- Call Maya first.

Maya: You heard it too, didn't you?
```

Avoid output like this:

```text
show maya neutral at left with dissolve
audio/bgm/station_theme.ogg
extend: "didn't you?"
mc "[player_name!u], are you listening?"
```

## Legal and Ethical Use

This workflow can process large amounts of narrative text. Use it responsibly:

- Process only games, mods, scripts, or translations you own or have permission to analyze.
- Do not publish extracted proprietary story text unless the license allows it.
- Do not use extracted text for model training, fine-tuning, or public datasets unless you have the required rights.
- Review the terms of platforms such as NotebookLM before uploading third-party content.

## Suggested GitHub Topics

```text
renpy
visual-novel
story-extraction
narrative-analysis
notebooklm
rag
dataset-preparation
localization
```

## License

Choose a license that matches what the repository contains.

- For extraction scripts only, an open-source license such as MIT or Apache-2.0 may be appropriate.
- For documentation and examples, consider a documentation-friendly license such as CC BY 4.0.
- Do not apply an open-source license to extracted story text unless you have the rights to do so.
