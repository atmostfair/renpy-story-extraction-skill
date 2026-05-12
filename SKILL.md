---
name: extract-renpy-story
description: Use when working with Ren'Py .rpy visual novel scripts or .rpyc-only builds that need decompilation, story-flow/order analysis, speaker/name rendering, player-visible narrative extraction, per-story text outputs, and extraction-rule auditing.
---

# Extract Ren'Py Story

## Interaction Rule

When this skill is used, reply to the user in Chinese, even if the user invokes the skill with an English prompt such as "Use Ren'Py Story Extractor to decompile rpyc-only Ren'Py builds...".

## Core Rule

Use `.rpy` source files, not `.rpyc` compiled files. If only `.rpyc` exists, first decompile with `unrpyc` and then continue from the generated `.rpy` files. For example, run `unrpyc ./` from the project root to decompile `.rpyc` files in that directory and all subdirectories, or run `unrpyc ./assets` when the Ren'Py payload is under `assets/`.

Do not assume filename or alphabetical order is game order. Determine order from Ren'Py `label`, `jump`, and `call` flow. Treat recap files, route files, text-message files, and translation files as label containers that may need to be split and inserted where the game jumps to them.

When project code defines the order of story files, chapters, episodes, routes, replay entries, or screen actions, that code-defined order takes precedence over physical file order, source-code order, natural sort, and guessed chapter numbering. Use source-code order only after proving there is no explicit ordering controller.

The default deliverable is separate ordered text files, not one monolithic merged story file. Name each extracted story output `storyxx_original-title.txt`, where `xx` is a zero-padded sequence number and `original-title` is the project-provided title when available, otherwise the source file stem plus label/range. Preserve the original title text; sanitize only characters that are invalid in filenames. A merged file may be generated as a convenience or trace artifact, but it must not replace the per-story outputs.

Always normalize the protagonist/player name to `You` in extracted English text and speaker maps. Do not use fallback names such as Jack, MC, a persistent save value, or a default from the source project unless the user explicitly asks for that exact rendered name.

Always distinguish spoken dialogue from inner thoughts in extracted text and speaker maps. Do not flatten thought-character dialogue into ordinary speech. If a project encodes thoughts through `what_prefix="("` / `what_suffix=")"`, italic thought prefixes, no-name thought characters, or speaker keys such as `mct`, `mcT`, `thought`, or `intrusive thoughts`, mark them explicitly in the output, for example `You (thought): text`. Keep normal speech as `You: text`. Apply this distinction even when the protagonist name is normalized to `You`.

Each time this skill is used on a project, update this skill with reusable lessons, pitfalls, and user-stated requirements discovered during that work. Keep the update concise and general; avoid one-off plot spoilers or project-only clutter unless the issue is likely to recur.

## Workflow

1. Locate the Ren'Py script root.
   - Desktop projects usually use `game/`.
   - Decompiled Android builds often use `assets/x-game/` and script folders such as `assets/x-game/x-scripts/`.
   - Android/YAC-crunched builds may prefix game files with `x-`, such as `assets/x-game/x-script.rpyc`, `x-game_vars.rpyc`, `x-script_exp_01.rpyc`, and `x-script_version.txt`.
   - Check exact extensions; PowerShell `-Filter *.rpy` can also match `.rpyc`, so prefer `Where-Object { $_.Extension -eq '.rpy' }`.
   - If no `.rpy` files exist, run `unrpyc ./` or a narrower path such as `unrpyc ./assets` or `unrpyc ./assets/x-game`, then inspect the generated `.rpy`.
   - If `unrpyc` is not found by `where.exe unrpyc` or `Get-Command unrpyc`, check for stale process environment before assuming it is unavailable. Codex/desktop shells may inherit an old `PATH` even after the user added a machine/user environment variable. Compare `$env:Path` with `[Environment]::GetEnvironmentVariable('Path','User')` and `('Path','Machine')`, check known dependency locations such as `D:\Dependency\unrpyc\unrpyc.cmd`, and temporarily append the missing directory to `$env:Path` when present.
   - If `unrpyc` is genuinely not available after refreshing/checking `PATH`, do not assume `pip install unrpyc` works. Use a known unrpyc source checkout/release, then run `python unrpyc.py <script-root>`. Check files such as `x-script_version.txt` to understand the Ren'Py bytecode version.

2. Classify files.
   - Story candidates: files containing many `label`, dialogue, `menu`, `jump`, `call message_img`, or scene labels such as `e1s1`, `ep4sc1`, `episode9`.
   - Support files: `variables`, `screens`, `images`, `music`, `options`, `gui`, `other`, `hamster`, etc.
   - In large Android builds, common story files include a main `script` file plus expansion/route files such as `script_exp_01`, while `phone`, `karma`, `gallery`, `screens`, `startup`, `town_map`, and `hud` are usually support files unless flow analysis proves otherwise.
   - Some Android builds keep all character definitions and player-name defaults inside the first main story file rather than a `variables` file, and may use single-quoted `Character(...)` plus `DynamicCharacter(...)`. Parse participating story files for speaker maps when no variables file exists.
   - Translation files under `tl/` may contain localized dialogue; use them only if the user asks for that language.

3. Learn project-specific content rules before extraction.
   - Inspect every `.rpy` file that will participate in extraction before deciding final keep/delete rules.
   - Identify how this project encodes visible text: dialogue lines, narrator lines, `extend`, menus, centered text, phone messages, TV/news captions, screen `text`, imagebutton tooltips, custom call helpers, gallery/replay labels, and debug/developer menus.
   - Identify what this project treats as non-story: asset paths, transforms, screen layout labels, variable/default data, gallery metadata, replay setup, contact lists, system prompts, age gates, debug menus, and unreachable leftovers.
   - Write or mentally maintain a project-specific inclusion/exclusion table before running the final extraction. If a quoted string is ambiguous, inspect surrounding code and how the player reaches it.
   - Revisit these rules after the first audit; do not blindly apply a generic extractor output without adapting it to the project's actual script conventions.

4. Determine game order.
   - Search labels and jumps: `rg -n "^\s*label\s+|^\s*jump\s+|^\s*call\s+" <scripts> --glob "*.rpy"`.
   - Start from `start`, `intro`, or the first explicit story entry.
   - If `start` is only an age gate, disclaimer, splash, or update-intro selector, begin extraction at the first real story label such as `gamestart`, and exclude unreachable intro/update branches unless the user asks for them.
   - Search for ordering controllers before relying on jump traversal alone: chapter/episode lists, route arrays, replay/gallery definitions, screen `Jump("label")` actions, map/menu screens, update selectors, and files whose only purpose is to choose or sequence other files.
   - If a specific file constrains which story file comes before another, use that file as the primary ordering source and record the evidence in a manifest or notes.
   - Follow unconditional transitions between files.
   - Split files by labels when a file holds multiple flow entry points.
   - When the main script jumps out to a side file and the side file jumps back to a return label, split the main script before the return label, insert the side file, then resume at the return label.
   - For a label whose first executable statement is an unconditional `jump`, include only the label and first jump when extracting player-visible text, because later text in that label block is unreachable.
   - Recap files are common traps: do not append the whole recap file at the end. Insert each recap label where the game jumps to it.

5. Build the per-story output plan.
   - Create ordered story units from the code-defined order. A unit can be an entire file, a label range, or a side-file insertion point.
   - Assign filenames before extraction: `story01_<title>.txt`, `story02_<title>.txt`, etc. Use at least two digits; increase padding if there are 100+ units.
   - Derive `<title>` from project-visible chapter/episode/replay titles when available. If no title exists, use the source stem and start label, for example `story03_script_exp_01_expansion_01_start.txt`.
   - Produce an index or manifest such as `story_index.txt` or `story_manifest.json` listing sequence number, output filename, source file, label/range, and ordering evidence.
   - Do not collapse future-update-sensitive units into one final text file. Keep separate story outputs so later game updates can be diffed and re-extracted incrementally.

6. Map rendered names.
   - Parse `define key = Character("Name", ...)` in variables files. Allow optional whitespace such as `Character ("Name", ...)`.
   - Parse `Character(...)` and `DynamicCharacter(...)` display metadata, especially `what_prefix`, `what_suffix`, `who_prefix`, and `who_suffix`, before generating the speaker map. Use this metadata to classify each speaker as spoken dialogue, inner thought, narration/no-name text, styled speech, or another project-specific visible-text type.
   - Parse `default var = "value"` for dynamic text variables such as `[playerName]`, `[playerNameA]`, `[jnNick]`, `[scarNick]`, `[heart]`.
   - Add speaker keys themselves as substitutions when needed, e.g. `[mc]` should render through `mc = Character("[playerName]")`.
   - Support Ren'Py interpolation forms such as `[playerName]`, `[playerName!u]`, and `[playerName.upper()]`.
   - Override protagonist variables and speakers to `You`: examples include `[player_name]`, `[playerName]`, `[mc]`, `[p]`, and `define p = Character("[player_name]")`. Apply this override before generating the story text and speaker map.
   - When the protagonist has separate speech and thought speakers, keep both mapped to `You` but record the mode separately, for example `mc = You (speech)` and `mct = You (thought)`.

7. Extract player-visible story text.
   - Keep dialogue, narrator lines, meaningful centered transition text, choices, and in-game text messages.
   - Format inner thoughts distinctly from spoken dialogue. Prefer `Speaker (thought): text` for thought-character lines and `Speaker: text` for ordinary spoken lines. If the game visibly renders thoughts with parentheses, either preserve those parentheses or use the explicit `(thought)` marker, but do not lose the distinction.
   - Extract phone/message calls such as `call message_img("", "text", "other/darcitxt.png")` and `call reply_message("text")`.
   - Some projects implement phone chats as dictionaries of custom `Msg(who, text, replies=...)` objects and insert them with `call chat(chat_name)`. Treat the chat file as a message container: traverse from step `"0"`, include all reachable reply branches once, render `"mc"` as `You`, and insert the chat at the call site.
   - Story-visible `screen text` may live in support screens and be triggered by `show screen` or unlock variables rather than normal dialogue, such as time cards, email/readable documents, poems, news captions, death messages, or audio logs. Include only screens reached from story flow or unlocked at that point; exclude menu, gallery, preference, score, and minigame UI text.
   - Infer message sender from image filenames when the call does not specify one.
   - Remove Ren'Py style/control tags such as `{i}`, `{size=...}`, `{font=...}`, `{w}`, `{p}`, `{nw}`, `{fast}`, `{image=...}`.
   - Treat `extend "..."` as a continuation of the previous visible line, not as a speaker named `extend`.
   - Repair mojibake caused by decompilation/terminal encoding when visible text shows misdecoded curly quotes, apostrophes, symbols, or name punctuation; use a Unicode repair pass such as `ftfy` when appropriate, then re-audit.
   - Exclude asset paths, UI labels, input prompts, age gates, gallery/music data, and contact-list menu entries.

8. Audit and iterate.
   - Search the output for resource paths: `audio/`, `images/`, `.png`, `.mp3`, `.ogg`, `.webm`, `.webp`.
   - Search unresolved variables: `\[[^\]\n]+\]`; only intentional markers such as `[Choice]` or `[text]` should remain.
   - Do a stricter unresolved-variable search for lowercase identifier brackets such as `\[player_name\]`, `\[temp_str\]`, `\[loaded_d20roll\]`, or `\[some_var!u\]`. Resolve them to concrete defaults, readable ranges, or intentional markers.
   - Search leftover tags: `\{[^}\n]+\}`.
   - Search for fake speakers or leakage: `^extend:`, `^label `, `^screen `, and resource-like file names.
   - Audit known thought speaker keys and thought-style `Character(...)` definitions against the output. Confirm thought lines are marked as thoughts and are not emitted as ordinary speech.
   - If audit output contains many bracket expressions, distinguish player-visible captions like `[!!Ding-dong!!]`, TV/phone subtitles, and `[Choice]` from unresolved Ren'Py variables before changing them.
   - Reverse-audit source quoted strings that the extractor did not consume; classify each as story text, UI text, resource data, or unreachable text.
   - Fix the script/config and regenerate until the output matches player-visible narrative content.
   - Run audits per output file and across the output directory. A single clean merged file is not enough if any `storyxx_*.txt` file still has leakage.

9. Update the skill.
   - Before final response, identify reusable lessons from the current project: new archive layouts, ordering controllers, custom visible-text helpers, dynamic variable forms, encoding issues, or user constraints.
   - Update `SKILL.md` or a directly linked reference with those lessons if they generalize beyond one plot event.
   - Validate the skill after editing when possible, then mention the skill update in the final response.

## Bundled Resources

- `scripts/renpy_story_extract.py`: reusable extractor/merger. Prefer using it with a project-specific JSON config for reliable ordering.
- `references/workflow.md`: detailed notes, regex patterns, audit commands, and Ren'Py pitfalls learned from prior extraction work.

## Documentation Notes

- When packaging or documenting this workflow as a public repository, present it as a Codex skill/workflow rather than a standalone executable application. Prefer a repository name that makes the skill nature clear, such as `renpy-story-extract-skill`, and keep short repository descriptions focused on intended use cases rather than implementation steps.

## Practical Use

First run a scan:

```bash
python <skill>/scripts/renpy_story_extract.py scan --source-dir <script-dir> --output-dir <work-dir>
```

Then create or edit a config from the scan output, especially `story_units`, and run:

```bash
python <skill>/scripts/renpy_story_extract.py merge --source-dir <script-dir> --config <config.json> --output <merged.txt>
python <skill>/scripts/renpy_story_extract.py extract --source-dir <script-dir> --config <config.json> --output <story_text.txt> --speaker-map <speaker_map.txt>
```

For final delivery, split extraction by ordered story unit and write `storyxx_original-title.txt` files plus an index/manifest. If the bundled script does not directly support split outputs, run it with per-unit configs or split a headered extraction deterministically; do not leave only `story_text.txt` as the final artifact.

If no config is available, the script can use a natural-sort heuristic, but treat that as a draft only. Verify it against the jump graph before delivery.
