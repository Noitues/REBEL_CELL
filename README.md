# REBEL_CELL

Cyberpunk tactical dual-spinner deckbuilder with a network-defense campaign.
Godot 4.7 · GDScript · PC.

- Design: `docs/GDD.md`
- Architecture: `docs/TECH_SPEC.md`
- Build plan: `docs/MILESTONES.md` (vertical slice, M0–M4)
- Visual baseline: `docs/STYLE_GUIDE.md`
- Decisions: `docs/DECISIONS.md`
- Gap analysis and horizontal plan: `docs/GAP_ANALYSIS.md`
- Instructions for Claude Code: `CLAUDE.md`

## Quick start
1. Install Godot 4.7 (verified on 4.7.2).
2. On a fresh clone, build the script class cache once:
   `godot --headless --path . --import`
3. Run the three checks; all must exit 0:
   - Tests: `godot --headless -s addons/gut/gut_cmdln.gd -gdir=res://tests -gexit`
   - Schema: `godot --headless --path . -s tools/schema_smoke_test.gd` → `SCHEMA SMOKE TEST: PASS`
   - Content: `godot --headless --path . -s tools/validate_content.gd` → `CONTENT VALIDATION: PASS`
   - Text export (localisation): `godot --headless --path . -s tools/export_text.gd` → `assets/text/strings.csv`
   - Screenshots: `godot --path . --resolution 1280x720 --write-movie out.png --fixed-fps 10 --quit-after 12 [scene] -- --demo-<hq|grid|raid|run|combat|tutorial|options|slots>`
   - Exports: `godot --headless --path . --export-release "Windows Desktop" build/windows/rebel_cell.exe` (presets in `export_presets.cfg`; CI does this on every push)
4. Current milestone: see `docs/MILESTONES.md`.

## Layout (M0–M4)
- `scripts/autoload/` — `SignalBus`, `ContentRegistry`, `RngService`, `SaveService`, `RunManager`
- `scripts/core/` — `WheelMath`, `CombatResolver`, `EffectInterpreter`, `CombatSession` (checkpoints, rewind, replay), `MapGenerator`, `NetrunSession` (map, rewards, shop, events, banking), `HeatRules`, `RaidResolver`, `CampaignRules` (Grid, claiming, raids, Exploits, story, win/loss), `handlers/`
- `scripts/state/` — `WheelState`, `CombatantState`, `CombatState`, `OperativeState`, `RunState`, `CampaignState`, `GridState`, `ProfileState` · `scripts/ui/` — `CombatEngine`, `WheelView`, combat, netrun and HQ scenes, `kit/` (zine kit, backgrounds, palette, theme), `fx/` (flash limiter)
- `scenes/hq/hq_scene.tscn` — the main scene: start, HQ (roster, recruit, station, Heat, Armory, story), City Grid, raid setup/projection/playout, campaign end · `scenes/netrun_map/netrun_scene.tscn` — map, embedded combat, rewards, Modem, Terminals · `scenes/combat/combat_scene.tscn` — standalone fight picker
- `scripts/data/` — Resource schemas · `content/` — authored `.tres` (config, Breaker, 25 cards, Firmware, Daemons, slices, Solace corporation with its City Grid, boss, Exploits, story paths, raids, nodes, assets, threats, Terminal events)
- `tests/unit`, `tests/integration` — GUT 9.x tests · `tools/` — headless checks
- `assets/fonts/` — Permanent Marker, Anton, Share Tech Mono (licences alongside) · `shaders/` — scanline, distortion, glow, zine paper
- `addons/gut/` — GUT 9.7.1
