# REBEL_CELL — Instructions for Claude Code

Cyberpunk roguelite deckbuilder in **Godot 4.7 / GDScript**. Combat resolves through
spinning 30-tick wheels; a campaign layer adds a City Grid map, Heat, and raid defense.

## Read before working
- `docs/MILESTONES.md` — what to build now and how it's accepted. Work on the current
  milestone only.
- `docs/GDD.md` — the rules. It is the source of truth for game behaviour.
- `docs/TECH_SPEC.md` — architecture, determinism, RNG, saving, testing.
- `docs/STYLE_GUIDE.md` — visuals (needed from M4; placeholders before that).
- `docs/DECISIONS.md` — decision log. Append to it; never silently change the GDD.

## Commands
- Tests: `godot --headless -s addons/gut/gut_cmdln.gd -gdir=res://tests -gexit`
- Tests in parallel (same scripts, shards balanced by measured time, each shard its own
  user://; exits non-zero on any failure, crash or skipped script):
  `python tools/run_tests.py` (4 shards; `-j N` for N). Fast tier for iteration (a
  couple of minutes): `python tools/run_tests.py --tier fast`. See `docs/TEST_SUITE.md`.
- Schema smoke test: `godot --headless --path . -s tools/schema_smoke_test.gd`
- Content validation (from M0): `godot --headless --path . -s tools/validate_content.gd`
- Anything that must render in a real window (Movie Maker captures, storyboard, motion
  lab, profiling): `python tools/run_windowed.py --log <file> -- <godot args>`, from a
  worktree or a copy. Never launch a windowed `godot` directly: it can take the user's
  keyboard and mouse focus and play sound. See `docs/TEST_SUITE.md` "Windowed checks".
- Run all three before declaring any task done, with the **full** suite (single process or
  the parallel runner; the fast tier alone never counts). A new test script goes into
  `tests/test_manifest.json` with its tier (`test_suite_integrity.gd` checks it).

## Non-negotiable rules
1. **Deterministic core.** Game rules live in pure `RefCounted` classes under
   `scripts/core/` with no Node or scene dependencies. Same seed + inputs = same result.
2. **Randomness only via `RngService` streams**, passed in as parameters. Never call
   global `randi()`, `randf()` or `randomize()`.
3. **Never modify a loaded Resource at runtime.** Content (`scripts/data/` schemas,
   `content/*.tres`) is read-only; runtime values live in `scripts/state/` objects.
4. **Signal Up, Call Down.** Views emit signals upward and never change game state.
5. **No magic numbers.** Tuning comes from `content/config/campaign_config.tres` or
   content `.tres` files.
6. **Every rule gets a test.** Preview must equal the real result; rewind must not cross a
   checkpoint; seeded replays must match.
7. Break ties deterministically (content id, then node id), never by dictionary order.
8. Keep `scripts/data/` schema changes minimal; add its check to `tools/schema_smoke_checks.gd` and
   log the change in `docs/DECISIONS.md`.

## When the docs don't answer something
Pick the simplest option consistent with the GDD pillars, implement it behind config if
it's a number, and add an entry to `docs/DECISIONS.md` under "Open questions for the
designer". Don't invent new mechanics or content beyond the current milestone.

## Style
- GDScript: static typing everywhere, `snake_case`, `class_name` for shared classes,
  `##` doc comments on public functions.
- One class per file; file name = snake_case of the class name.
- Small commits per acceptance criterion, with the criterion in the message.
