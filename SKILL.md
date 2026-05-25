---
name: extract-renpy-story
description: Use when working with Ren'Py .rpy visual novel scripts or .rpyc-only builds that need decompilation, story-flow/order analysis, speaker/name rendering, player-visible narrative extraction, per-story text outputs, and extraction-rule auditing.
---

# Extract Ren'Py Story

## Interaction Rule

When this skill is used, reply to the user in Chinese, even if the user invokes the skill with an English prompt such as "Use Ren'Py Story Extractor to decompile rpyc-only Ren'Py builds...".

## Core Rule

Use `.rpy` source files, not `.rpyc` compiled files. If only `.rpyc` exists, first decompile with `unrpyc` and then continue from the generated `.rpy` files. Use a global `unrpyc` command when it is available; otherwise use this skill's bundled fallback under `scripts/unrpyc/`. For example, run `unrpyc ./` from the project root to decompile `.rpyc` files in that directory and all subdirectories, or run `python <skill-dir>/scripts/unrpyc/unrpyc.py ./assets` when the Ren'Py payload is under `assets/` and no global command is available.

Do not assume filename or alphabetical order is game order. Determine order from Ren'Py `label`, `jump`, and `call` flow. Treat recap files, route files, text-message files, and translation files as label containers that may need to be split and inserted where the game jumps to them.

When project code defines the order of story files, chapters, episodes, routes, replay entries, or screen actions, that code-defined order takes precedence over physical file order, source-code order, natural sort, and guessed chapter numbering. Use source-code order only after proving there is no explicit ordering controller.

The default deliverable is separate ordered text files, not one monolithic merged story file. Name each extracted story output `storyxx_original-title.txt`, where `xx` is a zero-padded sequence number and `original-title` is the project-provided title when available, otherwise the source file stem plus label/range. Preserve the original title text; sanitize only characters that are invalid in filenames. A merged file may be generated as a convenience or trace artifact, but it must not replace the per-story outputs.

When extracting a multi-game series, preserve the user-stated chronology as a first-class ordering layer. Use prefixed output sections such as `01_mainline_title`, `02_mainline_title`, and high-numbered supplemental sections such as `90_supplement_demo` for side material that is not on the direct timeline. Keep per-game `storyxx_...txt` files inside those sections and write a series index explaining the timeline policy so later analysis does not mistake supplements for main continuity.

When users request a secondary merged deliverable after split extraction, write it to a new output folder and preserve the original per-story directory unchanged. Prefer relevance-based grouping over arbitrary fixed-size batches: group story units by project-visible relationships such as exact named-character sets, route/quest clusters, or other documented manifest evidence, and preserve the original manifest/story sequence order within each merged file. Include an index or manifest that proves every source story is covered exactly once unless the user explicitly asks for overlap.

Always normalize the protagonist/player name to `You` in extracted English text and speaker maps. Do not use fallback names such as Jack, MC, a persistent save value, or a default from the source project unless the user explicitly asks for that exact rendered name.

Always distinguish spoken dialogue from inner thoughts in extracted text and speaker maps. Do not flatten thought-character dialogue into ordinary speech. If a project encodes thoughts through `what_prefix="("` / `what_suffix=")"`, italic thought prefixes, no-name thought characters, or speaker keys such as `mct`, `mcT`, `thought`, or `intrusive thoughts`, mark them explicitly in the output, for example `You (thought): text`. Keep normal speech as `You: text`. Apply this distinction even when the protagonist name is normalized to `You`.

Each time this skill is used on a project, update this skill with reusable lessons, pitfalls, and user-stated requirements discovered during that work. Keep the update concise and general; avoid one-off plot spoilers or project-only clutter unless the issue is likely to recur. After updating the installed local skill, mirror the updated skill package one-way to the configured GitHub repository so the public/forked copy evolves with real use.

## Repository Sync Rule

When this skill package is a Git checkout, sync before and after skill work.

- Before using the skill for a project or editing the skill itself, fetch the configured remote. If the working tree is clean and the remote default branch is ahead, fast-forward or rebase onto it before continuing. If local uncommitted changes exist, do not overwrite them; inspect whether they are current user work, stash only when safe, then integrate remote changes without losing local edits.
- If the pre-use pull changes skill instructions or bundled scripts that matter for the current task, re-read the changed files before continuing so the current run follows the updated rules.
- After the task, update reusable lessons locally, validate the skill, fetch/pull again, resolve conflicts by preserving both remote improvements and newly learned local guidance, commit with a concise generated message, and push to the configured remote.
- If network or authentication blocks fetch/pull/push, finish the local task when possible, leave the repository in a clean or clearly documented state, and report exactly which sync step is still pending.

## Workflow

1. Locate the Ren'Py script root.
   - Desktop projects usually use `game/`.
   - Desktop builds may keep project scripts only inside `.rpa` archives such as `scripts.rpa`, `archive.rpa`, or DLC-specific archives while loose `game/` files contain only Ren'Py common/runtime scripts. Statically inspect archive indexes and extract `.rpy` entries before falling back to `.rpyc`; skip `tl/` translations unless the user asks for that language, and record archive provenance in the manifest.
   - Decompiled Android builds often use `assets/x-game/` and script folders such as `assets/x-game/x-scripts/`.
   - Android/YAC-crunched builds may prefix game files with `x-`, such as `assets/x-game/x-script.rpyc`, `x-game_vars.rpyc`, `x-script_exp_01.rpyc`, and `x-script_version.txt`.
   - Some Android builds keep runtime data tables under `assets/x-game/x-scripts/x-events.json`, `x-playlets.json`, `x-interactions.json`, and similar files even when decompiled code calls `renpy.file("scripts/events.json")`. Map the runtime `scripts/...` path back to the extracted `x-scripts/x-...json` path before concluding data files are missing.
   - Some Android builds separate character definitions into their own file (e.g. `x-characters.rpyc`) and store plain Python variable assignments inside `init python:` blocks in `x-variables.rpyc` rather than using `default`/`define` syntax. When config `variable_files` is used to include the character file, the bundled script can discover speaker mappings that would otherwise be missed.
   - Check exact extensions; PowerShell `-Filter *.rpy` can also match `.rpyc`, so prefer `Where-Object { $_.Extension -eq '.rpy' }`.
   - Do not stop at "some `.rpy` files exist" when a project has nested story folders. Check for `.rpyc` files without matching `.rpy` siblings in story subdirectories, and decompile only those missing files when needed.
   - If no `.rpy` files exist, first try a global `unrpyc ./` or a narrower path such as `unrpyc ./assets` or `unrpyc ./assets/x-game`, then inspect the generated `.rpy`.
   - If `unrpyc` is not found by `where.exe unrpyc` or `Get-Command unrpyc`, check for stale process environment before assuming it is unavailable. Codex/desktop shells may inherit an old `PATH` even after the user added a machine/user environment variable. Compare `$env:Path` with `[Environment]::GetEnvironmentVariable('Path','User')` and `('Path','Machine')`, check known dependency locations such as `D:\Dependency\unrpyc\unrpyc.cmd`, and temporarily append the missing directory to `$env:Path` when present.
   - If global `unrpyc` is genuinely not available after refreshing/checking `PATH`, do not assume the user has installed it and do not start with `pip install unrpyc`. Use the bundled fallback from this skill directory: `python <skill-dir>/scripts/unrpyc/unrpyc.py <script-root>`. On Windows, `scripts/unrpyc/unrpyc.cmd <script-root>` is also available when the `py -3` launcher exists.
   - Use absolute paths and quotes when either the skill directory or target project path contains spaces, for example `python "C:\Users\Name\.codex\skills\extract-renpy-story\scripts\unrpyc\unrpyc.py" ".\assets\x-game"`.
   - Only look for an external unrpyc checkout/release when both the global command and bundled fallback fail, or when the project requires an unsupported legacy Ren'Py bytecode path. Check files such as `x-script_version.txt` to understand the Ren'Py bytecode version and record why the bundled fallback was insufficient.
   - Some malicious or installer-style packages use Ren'Py only as a loading shell. If a small `.rpa` contains only `script.rpyc`, `options.rpyc`, `screens.rpyc`, and `gui.rpyc`, and the decompiled `script.rpy` reads hidden metadata, XOR-decrypts another file, opens it as a ZIP, or launches `.bat`, `.cmd`, `.exe`, `.msi`, or `.ps1` content with `subprocess`, treat it as a non-story payload. Do not execute it; statically document the finding, quarantine any extracted launcher by renaming it to a non-executable suffix, and do not create misleading `storyxx_*.txt` outputs.

2. Classify files.
   - Story candidates: files containing many `label`, dialogue, `menu`, `jump`, `call message_img`, or scene labels such as `e1s1`, `ep4sc1`, `episode9`.
   - Support files: `variables`, `screens`, `images`, `music`, `options`, `gui`, `other`, `hamster`, etc.
   - In large Android builds, common story files include a main `script` file plus expansion/route files such as `script_exp_01`, while `phone`, `karma`, `gallery`, `screens`, `startup`, `town_map`, and `hud` are usually support files unless flow analysis proves otherwise.
   - Some Android builds keep all character definitions and player-name defaults inside the first main story file rather than a `variables` file, and may use single-quoted `Character(...)` plus `DynamicCharacter(...)`. Parse participating story files for speaker maps when no variables file exists.
   - Translation files under `tl/` may contain localized dialogue; use them only if the user asks for that language.
   - Some desktop builds keep original-language story flow in `game/chapters/*.rpy` or `game/script.rpy` and localized dialogue under `game/tl/<language>/` as many `translate <language> label_hash:` blocks. Use the original story files for label order and branching evidence, then treat the `tl/` files as a language overlay keyed by the label prefix. Also parse `translate <language> strings` blocks for localized menu choices instead of leaving source-language menu text in translated outputs.

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
   - In small linear desktop builds, `start` may contain only warnings plus a menu whose every branch jumps to the same first story label. Treat that menu as gate text, not a branching story unit, and record the shared jump target as the first real story unit.
   - Search for ordering controllers before relying on jump traversal alone: chapter/episode lists, route arrays, replay/gallery definitions, screen `Jump("label")` and `Start("label")` actions, map/menu screens, update selectors, and files whose only purpose is to choose or sequence other files.
   - Android builds may put story chapters under misspelled or prefixed paths such as `assets/x-game/x-script/x-dialouge/...` while a separate ending/continue screen (for example `x-ending_scene/x-Ending.rpy`) controls the next chapter through `episode`-conditioned `Jump("label")` buttons. Treat that screen as primary ordering evidence when the `start` label only shows an age gate or jumps into the first real chapter.
   - If replay/gallery data registers labels that are not reachable from the main jump chain but are player-visible scenes, include them as explicitly marked replay-only story units rather than silently dropping them or pretending they are part of the main route. Preserve their `replay_scenes` order and record that ordering evidence in the manifest.
   - Some Android builds define Story Map order as `define gal = [repGallery(title, image, check, label, ...)]`, with a `StoryMap` screen iterating `gal` and calling `renpy.call_replay(i.label, ...)`. Treat the `repGallery` list as explicit ordered story evidence, then confirm it against the main label/jump chain before splitting per act.
   - Android galleries may register entries as triples such as `(seen_label, thumbnail_path, replay_label)` and then call `Replay(replay_label, locked=False)`. Use the replay label order, fold duplicate replay labels into one output, keep non-registered helper labels inside the surrounding replay range, and do not copy thumbnail/asset paths into story headers or index evidence.
   - In sandbox games, replay/gallery order can still be incomplete. After extracting replay entries, reverse-audit all uncovered top-level labels for visible text and append legitimate map-triggered events, readable emails/documents, repeatable scenes, or post-route endings as supplemental story units with explicit evidence instead of treating the replay gallery as full coverage.
   - Desktop projects may define day/chapter order in Python UI data classes such as `ChapterItem(..., content=[["label", "date"], ...])`, plus separate `New Game` and `Latest Update` `Jump(...)` buttons. Treat the content list as the primary ordered story index, and record the selector file as ordering evidence.
   - Desktop projects may also expose a `chapter_selection` or similar screen whose `textbutton` actions call `Start("DayN_Start")` for every chapter. Treat that screen as explicit chapter order, then confirm it against the `start` label and end-of-chapter jump chain.
   - Some linear desktop games use menu-driven POV selectors with boolean flags and a final `Present`/continue option after all POV branches have been seen. Preserve each POV branch as its own ordered story unit, then insert the post-selector continuation where the selector jumps after the completion counter/flags are satisfied.
   - For sandbox/event-framework games, JSON or Python data tables may be the real ordering controller. Treat event registration tables such as `events.json` as the primary order for event units; include playlet/random-ambient tables separately when they represent player-visible scenes rather than UI. When `run_interaction` dynamically jumps to relation-specific labels, expand the registered base label into existing suffix labels such as `_general`, `_girlfriend`, `_sexpartner`, `_fiancee`, `_lover`, or `_maid`.
   - Android open-map builds may use Ren'Py Python tables rather than JSON for ordering. Treat tables such as `TB_Quest`, `TB_Mission`, `TB_Card`, `TB_Stream`, `TB_Memory`, `TB_Action`, `TB_Room`, and `TB_ActorGrp` collectively as ordering evidence; then append remaining visible story/event labels by source order and record the fallback reason.
   - For open-map relationship games with no single chapter route, relation/contact screens, event-list screens, replay galleries, and map-trigger conditions may collectively define the closest project-authored order. Use the entry prologue first, then the project UI's character/event grouping and source-code event order, and record that evidence in the manifest instead of pretending there is a linear jump chain.
   - In open sandbox relationship games, per-character event-delay arrays, stats completion checks, gallery/replay screens, room/lobby/bar controllers, and map-trigger conditions may each expose part of the order. Keep a curated ordered-story directory for readable sequence, and write a separate all-visible-label trace directory so coverage auditing does not force every hub/support label into the narrative order.
   - If a specific file constrains which story file comes before another, use that file as the primary ordering source and record the evidence in a manifest or notes.
   - Follow unconditional transitions between files.
   - Split files by labels when a file holds multiple flow entry points.
   - Final episode files may combine the main route, ending-choice labels, and all route endings in one source file. Keep the ending-choice menu text with the main route up to the first actual route label, then split ending routes by the player-visible menu order. Include alias and chained labels reached by a route jump, such as a menu jumping to an intermediate ending label or one ending label continuing into a dependent follow-up label.
   - When building label ranges, use `end` only when the next boundary label is in the same source file. If the next ordered story unit starts in another file, let the current file end naturally or split with an explicit same-file label; otherwise the extractor may fail looking for a cross-file label.
   - When the main script jumps out to a side file and the side file jumps back to a return label, split the main script before the return label, insert the side file, then resume at the return label.
   - For a label whose first executable statement is an unconditional `jump`, include only the label and first jump when extracting player-visible text, because later text in that label block is unreachable.
   - Recap files are common traps: do not append the whole recap file at the end. Insert each recap label where the game jumps to it.

5. Build the per-story output plan.
   - Create ordered story units from the code-defined order. A unit can be an entire file, a label range, or a side-file insertion point.
   - If a project config was edited by Windows tools and starts with a UTF-8 BOM, read it with `utf-8-sig` or normalize it before loading JSON so a valid config is not rejected.
   - Assign filenames before extraction: `story01_<title>.txt`, `story02_<title>.txt`, etc. Use at least two digits; increase padding if there are 100+ units.
   - Derive `<title>` from project-visible chapter/episode/replay titles when available. If no title exists, use the source stem and start label, for example `story03_script_exp_01_expansion_01_start.txt`.
   - Preserve route status in titles or metadata when the source states it explicitly, such as `canon`, `non-canon`, `bad end`, `optional`, or `shared continuation`. Do not flatten those routes into an implied single canon line.
   - Produce an index or manifest such as `story_index.txt` or `story_manifest.json` listing sequence number, output filename, source file, label/range, and ordering evidence.
   - Produce a coverage note when practical: list source labels covered by story files, replay-only labels included separately, and skipped labels that contain no standalone player-visible text, such as animation/manual interaction helpers, branch dispatch labels, or chapter-end screens.
   - When supplemental units are appended after the primary project-defined order, keep them clearly marked by section/reason, for example `supplemental_event`, `supplemental_map_event`, or `supplemental_email`, and record skipped visible labels with reasons such as map/navigation/shop UI or support selector text.
   - Do not collapse future-update-sensitive units into one final text file. Keep separate story outputs so later game updates can be diffed and re-extracted incrementally.
   - If a later merge is requested for readability, keep it as an additional artifact. Avoid fixed-count chunking unless requested; instead group by cast, route, quest, or another clear relevance key, then sort each merged group by the existing story sequence and document the grouping rule.
   - When player-visible history is initialized inside a support Python function rather than a Ren'Py label, define the unit by exact source markers such as `start_marker` / `end_marker` around that function. Do not extract an entire phone/UI support file just because it contains visible history calls; screen code and helper definitions can leak fake speakers and placeholder strings.

6. Map rendered names.
   - Parse `define key = Character("Name", ...)` in variables files. Allow optional whitespace such as `Character ("Name", ...)`.
   - Also parse single-quoted character definitions such as `define MC = Character('Hiroki', ...)`; small desktop projects often use them in the main script instead of a variables file.
   - Also parse translation-wrapped display names such as `Character(_("Name"), ...)` when building speaker maps; strip the `_()` wrapper before applying substitutions and text cleaning.
   - Parse `Character(...)` and `DynamicCharacter(...)` display metadata, especially `what_prefix`, `what_suffix`, `who_prefix`, and `who_suffix`, before generating the speaker map. Use this metadata to classify each speaker as spoken dialogue, inner thought, narration/no-name text, styled speech, or another project-specific visible-text type.
   - If the same speaker key has different meanings in separate story files or supplemental modules, keep speaker mappings scoped per project, file, or story unit. Per-unit speaker overrides are safer than one global map when keys such as `M`, `Y`, or `MC` are reused.
   - Clean rendered `Character(...)` display names with the same tag/link/resource rules as story text. Combination speakers often embed Ren'Py color tags in the name, such as `{color=#...}[PlayerName]{/color} & {color=#...}Lily{/color}`, and those tags must not leak into story text or speaker maps.
   - Treat `Character(None, ...)`, `Character(name=None, ...)`, and equivalent no-name character definitions as narrator/no-name text. If keys such as `sys` appear as literal speakers in output, re-check no-name `Character(...)` parsing before accepting them as real speakers.
   - Parse `default var = "value"` for dynamic text variables such as `[playerName]`, `[playerNameA]`, `[jnNick]`, `[scarNick]`, `[heart]`.
   - When variables are defined inside `init python:` blocks as plain Python assignments (not `default`/`define`), the bundled script may not discover them. Add essential missing variables to the config `substitutions` map directly, or set `variable_files` to include both the variables file and the character-definition file when they are separate.
   - Add speaker keys themselves as substitutions when needed, e.g. `[mc]` should render through `mc = Character("[playerName]")`.
   - Support Ren'Py interpolation forms such as `[playerName]`, `[playerName!u]`, and `[playerName.upper()]`.
   - Support object-name interpolation forms such as `[P.name]`, `[B.name]`, and other `[CharacterObject.name]` strings when character objects implement `__str__` or expose a `.name` property. If source text uses lowercase aliases or typos such as `[p]` for the protagonist, resolve them deliberately instead of leaving them as bracket residue.
   - When relationship objects render placeholders such as `[rel.m]`, `[rel.MUP]`, `[rel.si]`, or `[rel.au]`, build an explicit substitution map from the relationship class defaults, setup UI prompts, and project context. If runtime defaults are obfuscated placeholders like `M__` or `S_____`, replace them with readable extraction values instead of leaking placeholder tokens.
   - Override protagonist variables and speakers to `You`: examples include `[player_name]`, `[playerName]`, `[mc]`, `[p]`, and `define p = Character("[player_name]")`. Apply this override before generating the story text and speaker map.
   - Keep protagonist overrides pinned after runtime assignments as well as defaults. Some projects prompt for a name, then assign fallback values such as `MC`, `Jack`, or `Isac`, or load `persistent` save names inside later labels; do not let those assignments pollute the extracted protagonist name unless explicitly requested.
   - When the protagonist has separate speech and thought speakers, keep both mapped to `You` but record the mode separately, for example `mc = You (speech)` and `mct = You (thought)`. Use config `speaker_mode` to attach display suffixes to speaker keys without mutating the base name, e.g. `"speaker_mode": {"mct": "thought"}` produces `You (thought): text`. Do not set `speaker_mode` for keys whose Character name already includes the mode text (e.g. `define mctxt = Character("[mcf] (Text)")` already renders as `You (Text)`).

7. Extract player-visible story text.
   - Keep dialogue, narrator lines, meaningful centered transition text, choices, and in-game text messages.
   - Treat transition-card statements such as `show text "Later"`, `show text"Next day"`, and `centered "Hours later"` as player-visible story text when reached from story flow. Generic dialogue regexes often miss these because `show` and `centered` are command-like tokens.
   - Format inner thoughts distinctly from spoken dialogue. Prefer `Speaker (thought): text` for thought-character lines and `Speaker: text` for ordinary spoken lines. If the game visibly renders thoughts with parentheses, either preserve those parentheses or use the explicit `(thought)` marker, but do not lose the distinction.
   - Some projects encode thoughts as ordinary character dialogue whose entire visible text is wrapped in plain markers such as `*...*` rather than Ren'Py style tags. Use a project config such as `thought_wrappers` to mark only whole-line wrapped dialogue as thought, and treat inline `*emphasis*` inside a spoken sentence as speech.
   - If a project uses plain thought markers and some source lines are malformed, such as starting with `*` but missing the closing `*`, configure an explicit thought prefix and audit for leftover ordinary dialogue like `^.+: \*` before delivery.
   - Short star-wrapped beats such as `*gasp*`, `*slurp*`, or `*Message notification*` should be marked as actions, for example `Speaker (action): gasp` or `[Action] Message notification`, not as thoughts or unresolved bracket markers.
   - If a whole dialogue line starts with a thought marker such as `(` but the source has a missing closing marker, classify it as thought during audit rather than leaving it as ordinary `Speaker: (` text. Search final outputs for patterns such as `^[A-Za-z][^:]+: \(` to catch missed thought lines.
   - When thoughts are encoded with italics on ordinary dialogue speakers, mark only whole-line italic dialogue such as `mc "{i}...{/i}"` as thought. Treat inline italics inside a larger spoken sentence as emphasis/formatting, not a thought boundary. Detect this before stripping tags, and allow style wrappers such as `{color=#808080}{i}...{/i}{/color}`.
   - Extract phone/message calls such as `call message_img("", "text", "other/darcitxt.png")` and `call reply_message("text")`.
   - Extract Python phone helpers when the project uses them, for example `$ send_phone_message(...)`, `$ npc_type_and_send(...)`, `$ npc_type_and_send_hesitate(...)`, and `$ present_phone_choices(...)`. Treat media-message arguments as resources to filter, render `phone_config["phone_player_name"]` as `You`, and keep player replies as choices or text-message lines according to how the UI displays them.
   - For phone history initializers such as `reset_phone_data()`, extract only the initializer body as a support-visible story unit when it populates prior chats shown to the player. Stop before later helpers or screens such as typing-name resolvers and message-list viewports, then audit for leaked placeholders like `message_text` and UI keys such as `scrollbars`, `hover_color`, or `layout`.
   - Some projects implement phone chats as dictionaries of custom `Msg(who, text, replies=...)` objects and insert them with `call chat(chat_name)`. Treat the chat file as a message container: traverse from step `"0"`, include all reachable reply branches once, render `"mc"` as `You`, and insert the chat at the call site.
   - Story-visible `screen text` may live in support screens and be triggered by `show screen` or unlock variables rather than normal dialogue, such as time cards, email/readable documents, poems, news captions, death messages, or audio logs. Include only screens reached from story flow or unlocked at that point; exclude menu, gallery, preference, score, and minigame UI text.
   - Infer message sender from image filenames when the call does not specify one.
   - Remove Ren'Py style/control tags such as `{i}`, `{size=...}`, `{font=...}`, `{w}`, `{p}`, `{nw}`, `{fast}`, `{image=...}`.
   - Remove Ren'Py hyperlink syntax `[[link text]]` (rendering just the inner text), which may survive tag stripping as `[[text]` when decompilation splits the closing `]]` across tag boundaries.
   - After removing known tags, strip any remaining `{...}` patterns (decompilation may produce malformed tag closers such as `{/p}`, `{/!}`, `{/f}`, `{/}` which are not standard Ren'Py tags).
   - Filter command-word quoted strings before speaker parsing. Lines such as `textbutton "View current mission" action Jump(...)`, `tooltip "..."`, `imagebutton`, and other screen/menu command text should not become fake speakers like `textbutton: ...` unless the surrounding code proves the player reads them as story text.
   - Treat `extend "..."` as a continuation of the previous visible line, not as a speaker named `extend`.
   - Some scripts split a single quoted Ren'Py dialogue statement across physical lines. Collapse continued quoted strings into one logical line before applying dialogue/menu regexes so lines such as `Jack "I received a message 10 min` followed by `ago."` are not dropped or misparsed.
   - Repair mojibake caused by decompilation/terminal encoding when visible text shows misdecoded curly quotes, apostrophes, symbols, or name punctuation; use a Unicode repair pass such as `ftfy` when appropriate, then re-audit.
   - Exclude asset paths, UI labels, input prompts, age gates, gallery/music data, and contact-list menu entries.

8. Audit and iterate.
   - Search the output for resource paths: `audio/`, `images/`, `.png`, `.mp3`, `.ogg`, `.webm`, `.webp`.
   - Search unresolved variables: `\[[^\]\n]+\]`; only intentional markers such as `[Choice]` or `[text]` should remain.
   - Do a stricter unresolved-variable search for lowercase identifier brackets such as `\[player_name\]`, `\[temp_str\]`, `\[loaded_d20roll\]`, or `\[some_var!u\]`. Resolve them to concrete defaults, readable ranges, or intentional markers.
   - For dynamic gameplay counters in player-visible text, replace unresolved variables with readable ranges or descriptions when the exact runtime value is branch/state dependent, for example `0-2`, `current bet`, or `the winning` instead of leaving `[sw_counter]` residue.
   - When unresolved variables are interpolated with currency or counters, remove misleading syntax after substitution if needed: `$[money]` can become `current money`, not `$current money`, and `[lottery_day]` can become `lottery draw day` when the runtime value is state-dependent.
   - Handle method-style interpolation that the generic variable regex may miss, such as `[actor.Name()!t]`; replace it with a readable runtime description or a resolved table/default value rather than leaving bracket residue.
   - Handle indexed/runtime result interpolation that simple variable regexes miss, such as `[result[1]!t]` or `[inventory_result[0]]`. Resolve it to a concrete nearby value when obvious, or replace it with a readable runtime description such as `current result message`.
   - On Windows/PowerShell, terminal output can make valid UTF-8 dialogue appear mojibaked. Set `PYTHONIOENCODING=utf-8` and verify file decoding before treating Korean, Chinese, or other non-ASCII text as corrupt source data.
   - UTF-8 emoji can appear as CJK/Kana mojibake such as `鉂わ笍` when interpreted through GBK/CP936. Verify actual file codepoints before "repairing" it; intended heart emoji should remain as `U+2764 U+FE0F` with zero replacement characters and no CJK/Kana leftovers in final outputs.
   - Search leftover tags: `\{[^}\n]+\}`.
   - Search for fake speakers or leakage: `^extend:`, `^label `, `^screen `, and resource-like file names.
   - Audit speaker maps as well as story text. Text-variable values in a speaker map should be unescaped and cleaned with the same tag/link/resource rules as extracted story text.
   - Filter resource-like substitution values from speaker maps and variable tables. Values such as `Hotel.webp`, `images/...`, or audio filenames are asset data, not rendered names or readable story variables.
   - Audit known thought speaker keys and thought-style `Character(...)` definitions against the output. Confirm thought lines are marked as thoughts and are not emitted as ordinary speech.
   - If audit output contains many bracket expressions, distinguish player-visible captions like `[!!Ding-dong!!]`, TV/phone subtitles, and `[Choice]` from unresolved Ren'Py variables before changing them.
   - If the extractor uses explicit markers such as `[Choice]`, exclude those intentional markers from unresolved-variable totals after confirming every remaining bracket expression has been classified.
   - Reverse-audit source quoted strings that the extractor did not consume; classify each as story text, UI text, resource data, or unreachable text.
   - When extraction files include metadata headers, keep ordering evidence readable without Python-list bracket syntax, or audit only the story body. Otherwise header strings like `pre_event=['foo']` can mask real unresolved interpolation variables.
   - Reverse-audit support labels with visible text, but do not automatically promote all of them into story outputs. Map/action labels, shop and wallpaper menus, tutorial hints, save/escape screens, repeatable housekeeping, wage/pay, and location descriptions are often UI or ambient support even when they contain quoted strings.
   - If reverse-audit finds a small number of player-visible support labels outside the normal story/event folders, append them as explicitly marked supplemental support units and write a coverage report showing uncovered visible labels are zero.
   - Fix the script/config and regenerate until the output matches player-visible narrative content.
   - Run audits per output file and across the output directory. A single clean merged file is not enough if any `storyxx_*.txt` file still has leakage.

9. Update the skill and sync it.
   - Before final response, identify reusable lessons from the current project: new archive layouts, ordering controllers, custom visible-text helpers, dynamic variable forms, encoding issues, or user constraints.
   - Update `SKILL.md` or a directly linked reference with those lessons if they generalize beyond one plot event.
   - Treat the installed local skill as the source of newly learned behavior, then mirror the same change into the active repository checkout. For the official upstream, use `https://github.com/atmostfair/renpy-story-extraction-skill.git`; for forks, push to that checkout's `origin` unless the user explicitly configures another remote.
   - Before committing, fetch or pull the remote default branch again, even if the pre-use sync already ran. If conflicts appear, resolve them intelligently: preserve the newly learned local guidance, keep unrelated remote improvements, remove duplicate wording, and leave `SKILL.md`, `README.md`, `README.zh-CN.md`, and bundled references internally consistent.
   - Validate the skill after editing when possible. At minimum, inspect frontmatter, search for stale repository names, check Markdown links, and run available script/help or syntax checks for changed bundled scripts.
   - Commit the repository sync with an automatically generated concise message, usually `docs(skill): sync learned extraction workflow updates` or a more specific `docs(skill): <summary>`.
   - Push to the configured GitHub remote. If push is rejected, pull/rebase, resolve conflicts using the same preservation rules, re-run validation, commit if needed, and push again.
   - Mention the skill update and repository sync status in the final response.

## Bundled Resources

- `scripts/renpy_story_extract.py`: reusable extractor/merger. Prefer using it with a project-specific JSON config for reliable ordering.
- `scripts/unrpyc/`: bundled Unrpyc command-line fallback for users who do not have `unrpyc` installed globally or exposed through `PATH`. Keep this folder trimmed to runtime files: `unrpyc.py`, `unrpyc.cmd`, `deobfuscate.py`, `decompiler/*.py`, and `LICENSE`.
- `references/workflow.md`: detailed notes, regex patterns, audit commands, and Ren'Py pitfalls learned from prior extraction work.

## Documentation Notes

- When packaging or documenting this workflow as a public repository, present it as a Codex skill/workflow rather than a standalone executable application. Use the repository name `renpy-story-extraction-skill`, and keep short repository descriptions focused on intended use cases rather than implementation steps.
- Public documentation should explain that forks can evolve independently: as the skill is used, reusable lessons from each user's projects and preferences are added to their local skill and can be pushed back to their own repository fork through that checkout's configured remote.

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
