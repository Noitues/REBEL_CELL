# REBEL_CELL

Cyberpunk tactical dual-spinner deckbuilder with a network-defense campaign.
Godot 4.7 · GDScript · PC.

- Design: `docs/GDD.md`
- Architecture: `docs/TECH_SPEC.md`
- Build plan: `docs/MILESTONES.md` (vertical slice, M0–M4)
- Visual baseline: `docs/STYLE_GUIDE.md`
- Decisions: `docs/DECISIONS.md`
- Instructions for Claude Code: `CLAUDE.md`

## Quick start
1. Install Godot 4.7 (verified on 4.7.2).
2. On a fresh clone, build the script class cache once:
   `godot --headless --path . --import`
3. Run the three checks; all must exit 0:
   - Tests: `godot --headless -s addons/gut/gut_cmdln.gd -gdir=res://tests -gexit`
   - Schema: `godot --headless --path . -s tools/schema_smoke_test.gd` → `SCHEMA SMOKE TEST: PASS`
   - Content: `godot --headless --path . -s tools/validate_content.gd` → `CONTENT VALIDATION: PASS`
4. Current milestone: see `docs/MILESTONES.md`.

## Layout (M0–M2)
- `scripts/autoload/` — `SignalBus`, `ContentRegistry`, `RngService`, `SaveService`, `RunManager`
- `scripts/core/` — `WheelMath`, `CombatResolver`, `EffectInterpreter`, `CombatSession` (checkpoints, rewind, replay), `MapGenerator`, `NetrunSession` (map, rewards, shop, events, banking), `handlers/` (rule-breaking cards and Daemons)
- `scripts/state/` — `WheelState`, `CombatantState`, `CombatState`, `OperativeState`, `RunState`, `CampaignState` · `scripts/ui/` — `CombatEngine`, `WheelView`, combat and netrun scenes
- `scenes/netrun_map/netrun_scene.tscn` — the main scene: campaign start, map, embedded combat, rewards, Modem, Terminals, save/resume · `scenes/combat/combat_scene.tscn` — standalone fight picker
- `scripts/data/` — Resource schemas · `content/` — authored `.tres` (config, Breaker, 25 cards, Firmware, Daemons, slices, Solace enemies, assets, threats, Terminal events)
- `tests/unit`, `tests/integration` — GUT 9.x tests · `tools/` — headless checks
- `addons/gut/` — GUT 9.7.1
