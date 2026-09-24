# REBEL_CELL — Technical Specification

Godot **4.7** (pinned since M1, was 4.3; schemas verified on 4.3 and 4.7.2). GDScript only. PC, mouse + keyboard.

## 1. Principles
1. **Deterministic core.** All game rules live in pure-logic `RefCounted` classes with no
   Node, scene-tree or rendering dependencies. Same seed + same inputs = same result.
2. **Signal Up, Call Down.** Child nodes emit signals upward; parents call methods
   downward. Visual nodes never change game state; they animate what the core reports.
3. **Data vs state.** Content is `Resource` data (`scripts/data/`, authored as `.tres` in
   `content/`). Runtime values live in state objects. **Never modify a loaded Resource at
   runtime** — Godot shares loaded Resources, so an edit changes every user.
4. **No magic numbers.** Tuning values come from `CampaignConfigData`
   (`content/config/campaign_config.tres`) or content `.tres`, never literals in code.
5. **Every rule has a test.**

## 2. Project Layout
```
project.godot
CLAUDE.md, README.md
docs/                   GDD, TECH_SPEC, MILESTONES, STYLE_GUIDE, DECISIONS
scripts/
  data/                 Resource schemas (provided; 39 classes + RC enums)
  core/                 Pure logic: wheel_math, combat_state, combat_resolver,
                        effect_interpreter, preview, rewind, map_generator, raid_resolver
  state/                Runtime state: wheel_state, combatant_state, operative_state,
                        run_state, campaign_state, profile_state
  autoload/             signal_bus, content_registry, rng_service, save_service, run_manager
  ui/                   Scene scripts (views only)
scenes/                 hq/, grid/, netrun_map/, combat/, raid/, ui_kit/
content/                .tres by type: classes/, cards/, slices/, firmware/, daemons/,
                        enemies/, corporations/, nodes/, assets/, threats/, config/
shaders/                glow, scanline, zine_paper, distortion
audio/                  placeholders
tests/                  GUT tests mirroring scripts/ (unit/, integration/)
tools/                  schema_smoke_test.gd, validate_content.gd
addons/gut/             GUT 9.x (installed in M0)
```

## 3. Autoloads
| Autoload | Role |
|---|---|
| `SignalBus` | Global event bridge only (no state) |
| `ContentRegistry` | Scans `content/`, maps `id → Resource`, validates on load in debug builds |
| `RngService` | Named, seeded RNG streams (4.) |
| `SaveService` | Versioned JSON save/load (8.) |
| `RunManager` | Owns `ProfileState`, `CampaignState`, active `RunState`; scene transitions |

## 4. Randomness
- One campaign seed. `RngService` derives **independent streams**: `map`, `combat`,
  `rewards`, `events`, `raids`, each a `RandomNumberGenerator` seeded from
  `hash([campaign_seed, stream_name])`.
- Stream state (`rng.state`) is saved. Core code receives the RNG it needs as a parameter;
  it never calls global `randi()`/`randf()`.
- Rewinding combat restores the `combat` stream state; it never touches other streams, so
  rewinds cannot change maps or rewards.

## 5. Combat Core

### 5.1 Wheel math (`wheel_math.gd`, static functions)
```
TICKS = 30
tick_at(rotation, pointer_tick) = posmod(rotation + pointer_tick, 30)
mirror_tick(t, p)             : posmod(2p + 15 − t, 30)   # Flip rearranges slots (i → −i mod n) and sets rotation = −rotation − 15
slice_at(tick, slice_count)   : c = round(tick / (30/slice_count)); return posmod(c, slice_count)
offset_at(tick, slice_count)  : tick − (30/slice_count) × round(tick / (30/slice_count))
tier(offset)                  : 0 → PERFECT, ±1 → GOOD, ±2 → PARTIAL   (6-slice wheels)
ring_segment(tick)            : floor(posmod(tick + 5, 30) / 10)        (3 × 10-tick ring)
```
Satellite wheels (2–3 slices) use the same functions with `slice_count`; their tier is
not used (they resolve at full output) unless a card says otherwise.

### 5.2 State
`CombatState` (duplicable, pure data): turn number, phase, player `CombatantState`,
enemy `CombatantState[]`, draw/hand/discard/exhaust piles (card ids), RAM, free-nudge
flag, per-combat counters (consecutive Perfects, once-per-combat uses).
`CombatantState`: HP, block, shield, statuses per slice, `WheelState`, satellites, hub
breached flag, resistance remaining.
`WheelState`: rotation (int, unbounded; visuals use it for spin direction), inner rotation,
pointer ticks, frozen flag (a Flip rearranges the slot arrays; there is no flipped flag).
All state classes implement `duplicate_state()` (deep copy) and `to_dict()/from_dict()`.

### 5.3 Turn state machine
`START_TURN → PLAYER_PHASE → RESOLVE → (END_COMBAT | START_TURN)`
- `START_TURN`: respin each non-frozen wheel via `combat` RNG → **checkpoint** → draw →
  RAM +regen (cap) → refresh free nudge → expire block → restore passive resistance.
- `PLAYER_PHASE`: accepts `Action` objects (PlayCard, Nudge, Target, EndTurn, Rewind).
- `RESOLVE`: three passes (defensive, offensive, status/effects) over all pointers of all
  wheels, both sides simultaneously, per GDD 2.2.

### 5.4 Actions, preview and rewind
- Every player input is an `Action` (plain data). `CombatResolver.apply(state, action,
  rng) -> Result{state, events}` is **pure**: it returns a new state and a list of events.
- **Preview** = `apply()` on `state.duplicate_state()` (including a full simulated
  `RESOLVE` for the End Turn preview). Preview must equal the real result — enforced by
  tests.
- **Rewind**: the engine keeps `checkpoint_state` plus `actions_since_checkpoint[]`.
  Undo = restore checkpoint, replay all actions except the last. Any action that consumes
  `combat` RNG creates a new checkpoint after resolving. The checkpoint and action list
  are saved.

### 5.5 Effect interpreter
- Content describes behaviour as `TriggeredEffectData → EffectData[]`.
- The interpreter keeps a registry of listeners (slice extras, Firmware, ring segment,
  Hub, Daemons, statuses) keyed by `RC.Trigger`. When the resolver raises a trigger it
  passes a context `{source, owner, pointer, tier, slice_index, target}`; listeners whose
  `min_tier`, `consecutive_required` and `limit_per_combat` conditions pass run their
  effects in a deterministic order: **slice → Firmware → ring segment → Hub → Daemons →
  statuses**, then by content id.
- `EffectType.CUSTOM` and `DaemonData.custom_handler` point to scripts implementing
  `func handle(context: Dictionary, state: CombatState, rng: RandomNumberGenerator) -> Array`
  (returns events). Custom handlers must be pure like the resolver.

### 5.6 Node layer
`CombatScene` (Node) owns a `CombatEngine` (Node) which holds the current `CombatState`,
calls the core, and emits `state_changed(state, events)`. Views (wheel, hand, HUD, log)
subscribe and animate events with Tweens. Views emit intent signals up
(`card_hovered`, `card_played`, `nudge_requested`, `target_selected`, `end_turn_pressed`,
`rewind_pressed`).

## 6. Netrun Map Generation (`map_generator.gd`)
Input: tier, Site data, config, `map` RNG. Output: `MapGraph` (layers of nodes + edges).
1. Layer count = `config.map_layers` (7). Each layer gets `randi_range(min, max)` nodes;
   layer 7 has exactly one node (final Server Rack).
2. Assign types: layer 1 all Routers; one Server Rack in layer 4; at least one Modem in
   layers 3–5; about one Elite per layer in 3–6; Terminals ≈ 25% of the rest; remainder
   Routers.
3. Edges: each node connects to 1–2 nodes in the next layer; no crossing edges; every
   node reachable from layer 1 and able to reach layer 7.
4. Validate (reachability, guarantees); regenerate with the next RNG value on failure.
Tests: 1,000 seeds produce valid maps; same seed = identical map.

## 7. Raid Resolver (`raid_resolver.gd`)
Pure function: `resolve(grid_state, placements, threats, config) -> RaidResult` with a
per-step event log for the playout. Setup-phase projection calls the same function.
```
for step in 1..config.raid_step_cap:
    move threats (edges_per_step, by routing rule; decoys add pull to routing score)
    apply ICE Lock holds
    assets + built-in defenses fire (range in hops, targeting priority, shots_per_step)
    threats damage the node they occupy
        node integrity ≤ 0 → DISABLED; excess × cascade_ratio → adjacent claimed nodes
        threat at home → home integrity −= damage; if ≤ 0 → CAMPAIGN_LOST
    stop if no threats remain
threats still on nodes at the end → SEIZED
```
Ties are broken by content id, then node id — never by dictionary order.

## 8. Saving
- JSON via `FileAccess`, one file per profile plus one per campaign, with a top-level
  `"version"` and a migrations table.
- State references content **by id** (`ContentRegistry` resolves ids on load). Never
  serialize Resource paths or objects.
- Autosave: entering each map node, after each combat, returning to HQ, and after raids.
  Combat saves include `checkpoint_state`, `actions_since_checkpoint` and RNG stream
  states.

## 9. Testing
- **GUT 9.x** (Godot 4 compatible). Tests in `tests/unit` and `tests/integration`.
- Run headless: `godot --headless -s addons/gut/gut_cmdln.gd -gdir=res://tests -gexit`
- Schema check: `godot --headless --path . -s tools/schema_smoke_test.gd`
- Content check (M0): `godot --headless --path . -s tools/validate_content.gd` runs every
  Resource's `validate()`.
- Required test types: wheel math tables; each GDD rule (resistance, flip blocking,
  resolution order, pointer rule, satellites, statuses); **preview == actual**; **rewind
  cannot cross a checkpoint**; **seeded replay determinism** (record inputs, replay, compare
  final state hash); save → load round-trip equality; map generator properties; raid
  resolver golden-file tests.

## 10. Performance & Platform
Target 60 fps at 1920×1080, 16:9 layout scaled from a 1280×720 design canvas. Resolution
logic must run well under 1 ms per turn. Keep shaders optional so the reduce-effects
setting can disable them.
