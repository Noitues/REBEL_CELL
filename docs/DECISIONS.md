# Decision Log

Append new entries at the top of the relevant section. Never delete entries; mark them
superseded instead.

## Locked design decisions (v0.9)
- Wheel is 30 ticks / 6 slices / 5 ticks per slice (was 24). Enables a true centre tick.
- No Miss precision tier; "Miss" means the Miss slice only.
- Enemy jitter replaced by spin resistance (passive trait or Hub-sourced). Flip and
  Respin are blocked while resistance > 0.
- Flip mirrors the wheel across the horizontal axis (opposite slice to the pointer).
- Triggering: every pointer triggers its slice on End Turn. Pointer attacks hit every
  pointer of the target wheel. Satellites act as bodyguards.
- Resolution order: defensive → offensive → statuses, simultaneous.
- Three-layer progression: netrun / campaign / profile. Class unlocks are profile-level.
- Rank (runs survived) replaces veterans/Trace: wheel upgrades, netrun tier access,
  station bonus scaling. Survivors keep everything; difficulty scales to match.
- Heat is one campaign meter. Threshold events fire once; modifiers apply while at/above.
- City Grid is one shared map for netruns, territory and raids; cleared Sites are used up
  and become claimable.
- Armory (cap 6) + persistent deployed assets resolves the audit's persistence question.
- Mainframe gate: minimum 3 Exploits (Intel, Breach, Virus); extras weaken the boss.
- Story paths: 5–6 per corporation, hidden and random; beats unlock in Exploit order.
- REBEL_CELL (the handler AI) is the final unlock corporation at ICE 10 on all others.
- ICE difficulty: 20 cumulative levels, ICE 5 is the average-player tuning target.
- Visual baseline: three worlds (cyberdeck / wireframe / zine), Cell colour hot pink.
- Full voice acting; fully solvable combat preview; rewind with checkpoints at random
  events.

## Implementation decisions
_(Claude Code: add entries here as you make them.)_

### 2026-09-24 — M3 Campaign & Raids
- **Grid runtime state** (`GridState`) records per Site: status (corporate / cleared /
  claimed / Seized), installed node id, integrity, condition (OK / Disabled), deployed
  assets and the stationed operative; plus home integrity and Intel-opened links. Layout
  stays in `CityGridData`. `NetworkNodeData` gained an `id` so nodes are content ids.
- **Heat thresholds** (`HeatRules`): events fire on upward crossings not yet in
  `thresholds_fired`; the MAJOR/PURGE raid goes to `pending_raids`, MINOR complications to
  `pending_complications` (consumed by the next netrun: shop stock −1, elite +25%).
  Modifiers are read live (`CampaignState.rule_modifier`), so they switch off by
  themselves below the threshold. ICE levels ≤ `ice_level` stack with them.
- **Raids resolve at HQ** (between runs). Threshold raids reached mid-run wait in the
  queue until the operative returns; the "mid-run interlude" of GDD §4.4 is deferred
  (open question). Setup projection and playout are the same pure `RaidResolver.resolve`
  on copies, so projection always equals the result.
- **Raid step rules** (TECH_SPEC §7 filled in): threats spawn wave *k* at step 1 + 5*k*
  at the entry Sites (corporate or Seized Sites adjacent to the territory; the boss Site
  as a last resort). Movement follows shortest paths (ties by Site id) toward the routing
  target: home, the highest-value node (`raid_priority`, then install cost) or the weakest
  node; a Decoy overrides the target. Entering a live claimed node (or home) ends the
  step's advance; Disabled and unclaimed Sites are passed through. A threat camps on its
  target node until it falls. ICE Locks hold each threat once per lock. Assets and
  built-in defenses fire per node in Site-id order (FIRST_IN_PATH = nearest to home,
  ties by content id then threat id). Node damage: 0 → Disabled, `floor(excess ×
  cascade_ratio)` to each adjacent claimed node (no chaining); a threat ending a step on a
  Disabled node Seizes it; a Seized Site loses its node, assets and station; damage at
  home reduces integrity, 0 = campaign lost; a threat that reaches home is done. Step cap
  30 then Seizes every node still occupied. Win = every threat destroyed → RaidData
  reward; otherwise +5 Heat. RAID_STRENGTH_PCT scales threat integrity and damage.
- **Claiming** needs a cleared Site adjacent to home or to a live Relay/Firewall Relay
  ("Relay lets you claim Sites beyond it"), costs the node's install cost, and provokes a
  TERRITORY_CLAIM raid when the Site touches a corporate or Seized Site (GDD §4.4).
- **Node slots** (content): Relay 1 asset slot, Firewall Relay 2 (+ built-in 3-damage
  turret), Safehouse 1 (+1 station slot), home 2. Station bonuses are recorded but not
  yet applied in raids (open question on scaling).
- **Special runs:** the final breach and Reclaim runs are one-node `NetrunSession`s
  (`kind` boss / reclaim) so save/resume and the netrun scene work unchanged. Reclaim pays
  the 10–20 "Combat" Cycles and offers nothing else.
- **Boss phases** (`CombatResolver._check_boss_phases`) enter after deaths each turn;
  MULTIPLY/MIGRATE set the pointer layout, ORBIT sets `pointer_orbit`, phase spawns dock,
  hub overrides swap the Hub. Breach removes pointers in every layout but never below one;
  Virus corrupts two random non-Miss boss slices at the start; Intel only flags
  `reveal_phases` for the HUD.
- **Story:** one path is picked at campaign start from the corporation's weighted list
  using the `events` stream of the campaign seed; each Exploit reveals the next beat; the
  finale is shown on the win. Solace ships five placeholder paths of 3 beats + finale.
- **Profile** (`ProfileState`, `profile.json`): campaigns started/won/lost, runs completed,
  operatives lost, raids won/lost, best ICE overall and per corporation.
- **State dictionaries are JSON-normalised on `to_dict()`** (`RunState`, `CampaignState`)
  so a saved-and-reloaded state hashes identically (ints become floats either way).
- **Breaker Rank 2/3 rewards** exist only for tier gating (T3 / T4); the Rank 2 Hub
  upgrade and Rank 3 segment options are content for later (CONTENT_SLICES.md).
- **Scenes:** the HQ scene is the main scene (start → HQ → City Grid → launch → netrun
  scene → back to HQ; raids from HQ). RunManager owns profile, campaign, corporation and
  run; scene switching can be disabled for tests.

### 2026-09-24 — M2 Netrun Loop
- **Run randomness** comes from the run's own `RngStreams` (pure core class; `RngService`
  now wraps it) seeded from a run seed drawn from the campaign `map` stream: `map` builds
  the map, `combat` picks enemies and seeds each fight, `rewards` rolls Cycles, asset drops,
  offers and shop stock, `events` picks Terminal events. Stream states are saved with the
  run, so a resumed run continues identically.
- **Map generator** follows TECH_SPEC §6 with non-crossing edges built as monotone chains
  (each node 1–2 forward edges; every next-layer node covered; provably reachable both
  ways). New config: `map_modem_layers` (3–5), `map_elite_layers` (3–6),
  `map_elites_per_layer` (1), `map_terminal_ratio` (0.25). Elite Heat (+1) is charged on
  entering the node; Server Rack Heat is charged on *capture* (11.5 says "capture", and
  Scrubber needs to replace it).
- **Cycles per node:** Router 15–25 (`cycles_router_range`), Elite Router and Server Rack
  30–40 (`cycles_elite_range`); "Combat 10–20" is reserved for non-node fights (Reclaim,
  events). Rewards scale ×1.7^(tier−1); enemy HP and slice outputs ×1.6^(tier−1) via
  `CombatantState.output_scale`.
- **Rewards:** every won fight offers 1-of-3 cards from the shared pool plus the class's
  exclusives (no duplicate within an offer; skip allowed); elite Routers add 1-of-2
  Firmware (the player picks the socket; must fit the slice type); Server Racks add 1-of-3
  Daemons not yet owned, bank `rack_schematics_by_tier` and any unbanked assets. Asset drop
  chance 0.4 per fight from the A.5 assets; assets are unbanked until a Rack.
- **Modem stock:** 3 cards, 2 Firmware, 1 Daemon (prices rolled in the §11.2 ranges), card
  removal at 50 (+25 per removal), slice overwrite 100 (150 for the Miss slot). The
  overwrite options are the distinct non-Miss slices already on the operative's wheel
  (open question: a real slice catalogue).
- **Enemy pools** are derived from content, not a CorporationData (arrives with the City
  Grid in M3): EnemyData with `corporation_id == "solace"`, 6-slice wheel, not boss;
  `is_elite` splits normal/elite. Terminal events: `TerminalEventData` with matching or
  empty corporation, weighted pick.
- **Operative state** (`OperativeState`) carries the current wheel layout (slice ids +
  Firmware sockets), deck, Daemons, HP and Rank; a run works on a copy written back to the
  roster only on completion (death: permadeath, the roster entry is marked dead).
- **Daemon hooks.** Data-driven Daemons are plain listeners in TECH_SPEC order after the
  Hub. Rule-breakers use `custom_handler` scripts with
  `handle(context, state, rng) -> Array[Dictionary]`; combat handlers get every trigger with
  `context.trigger`, run-level handlers get ON_SERVER_RACK_CAPTURE / ON_NETRUN_COMPLETE with
  the RunState. Kernel Sync's +1 applies from the *next* attack after the Perfect.
  Zero Day = 3 × the wheel's best Crit output (else best Attack) at the pointer target.
- **Custom card effects** (`EffectType.CUSTOM` + handler): Ring Lock, Momentum, Calibrate,
  Steady Hand, Undock. Per-combat markers live in `CombatState.flags` / `ring_locked` /
  `ram_bonus_next_turn` / `damage_bonus` so they save, preview and replay like everything
  else.
- **Firmware neighbour rules** add derived resolutions before the passes: Mirror copies the
  neighbour on the landed side (both on Perfect) at the landing's tier; Shunt resolves that
  neighbour instead at ×1.5 and does nothing special on Perfect. Positive offset = landed
  clockwise = neighbour slot +1.
- **Billing Daemon** drains RAM through DRAIN_RAM slice effects (`atk_7_drain`,
  `crit_12_drain`); **Recall Unit** orbit is a new `WheelData.pointer_orbit_per_turn` (+2,
  applied from turn 2 on); **Care Swarm** drones dock on random free slots.
- **Save file:** one JSON per campaign slot (`user://saves/campaign_<slot>.json`) holding
  the campaign, the run (with its live combat session, checkpoint and streams) and the
  campaign RNG. Autosave on entering a node, after each combat, after every reward/event/
  shop step and on quit. A combat's `setup` is JSON-normalised on creation so a resumed
  session hashes identically.
- **Scenes:** the netrun scene is the main scene (start screen → map → embedded combat →
  reward/event/shop → summary). The combat scene keeps its standalone picker for M1-style
  testing (`auto_start`).

### 2026-09-24 — M1 Combat Core
- **Designer rulings applied (from the M0 review):** Godot pin moved to **4.7** (GUT
  9.7.1); elite frequency placeholder 25% confirmed; `BOSS_PHASE_EARLY` dropped in favour
  of a new `RuleModifierType.BOSS_STRENGTH_PCT` (boss HP and damage +25% at ICE 9; the
  old enum value stays so stored numbers keep meaning; GDD §11.9 "bosses change pointers
  earlier" is superseded); minor Heat complications alternate shop stock −1 (10/30/60/80)
  and elite frequency +25% (20/40/70/90); RAM cap is **12** as GDD §2.2/§5.2 already state,
  carried by `ClassData.max_ram` (`ram_regen_per_turn` removed from the config so RAM has
  one source of truth).
- **Flip math.** GDD §2.3's code block and TECH_SPEC §5.1 both say
  `tick = (rotation + pointer + 15 if flipped) mod 30`; the prose ("mirrors… slice order
  reverses") would be `pointer + 15 − rotation`. The code block is implemented; the
  discrepancy is logged as an open question.
- **State references content by id.** `WheelState` stores slice / Firmware / Hub / ring
  segment ids and resolves them through a `ContentLookup` handed to the resolver, so the
  core never touches the ContentRegistry autoload and tests can inject in-memory content.
- **One status per slice.** ENCRYPTED absorbs the next status and clears; OVERCLOCKED
  becomes CORRUPTED after its trigger; permanent Firmware statuses (Hardened, Burner) come
  from the Firmware, not the status slot. CORRUPTED self-damage ignores block/shield and is
  applied in the status pass for every corrupted slice that resolved this turn.
- **Simultaneity.** All pointers are collected before any pass; a combatant reduced to 0 HP
  still resolves the rest of the turn; deaths and the outcome apply after the status pass.
  A dead host takes its satellites with it.
- **Pointer rule.** Every attack instance hits once per pointer of the target wheel; the
  bodyguard check uses the target's slice under *that* pointer. Pierce ignores satellites
  and block but not shield (shield is a separate resource; open question).
- **Retrigger.** RETRIGGER effects (Breaker Perfect hook, Echo) are counted before the
  slice resolves; each extra instance repeats the base action and the slice's listeners.
- **Output rounding:** `roundi(base × multipliers)` (Partial 0.5, Overclock 1.5, ring ×2).
- **Breaker "+1 spin on all cards"** is data: a PASSIVE-trigger SPIN effect on the Hub
  Core; the interpreter adds its amount to every SPIN a card performs.
- **Slice selection for slice-level effects** is a new `EffectData.slice_pick`
  (UNDER_POINTER / RANDOM_NON_MISS / CHOSEN). DOSE = RANDOM_NON_MISS, never an
  already-corrupted slice. Convention: a NUDGE effect with `multiplier 0.0` ignores
  resistance (Jam). Fine Tune's ring and direction come from the action.
- **Enemy targeting:** enemies and satellites always attack the operative; the operative's
  pointer attacks and cards aim at `CombatState.target_id` (Tab / target list), which may
  be a satellite.
- **Checkpoints are detected, not declared:** `CombatSession.apply()` compares the RNG
  state before and after; any action that consumed RNG (End Turn respins, DOSE's random
  slice, Respin, a reshuffle on draw) becomes the new checkpoint. Rewind restores the
  checkpoint and replays the rest. Preview clones the RNG, so the preview of a random
  effect is exact in the engine; the scene deliberately shows DOSE as "random non-Miss
  slice" rather than the exact slot (GDD §2.10 says random effects show odds).
- **Respin** adds `2×30 + rand(0..29)` ticks so views can animate direction and distance;
  the inner ring respins independently; a Respin clears `flipped`.
- **Hub Breach** removes the hub's resistance from the pool at once and disables hub
  passives; the breach counter decrements at the next start of turn (one full turn).
- **Combat scene starts the Breaker at Rank 1** (ring installed) so every M1 mechanic is
  visible; the rank-0 path is covered by tests.
- **Breaker slice values** are placeholders (Crit 12 / Atk 6 / Def 5, matching the schema
  smoke test) because GDD §5.2 lists types only.

### 2026-09-24 — M0 Foundation
- **Engine used for verification: Godot 4.7.2** (only 4.6.2 / 4.7.x are installed on the
  dev machine). M0 kept the 4.3 pin; _superseded in M1_: the designer moved the pin to 4.7,
  so `*.uid` sidecars are now committed.
- **GUT 9.4.0** was vendored in M0; _superseded in M1_ by GUT 9.7.1 (the Godot 4.7 tag).
  `.gutconfig.json` enables `include_subdirs` so `-gdir=res://tests` picks up `unit/`,
  `integration/` and the non-test `helpers/`.
- **Fresh clone needs one import** before the `-s` tools work:
  `godot --headless --path . --import` builds the global script-class cache.
- **`-s` tool scripts compile before autoloads exist.** `tools/validate_content.gd`
  preloads `content_registry.gd`, so the registry looks SignalBus up by node path instead
  of naming the singleton. Other autoloads may name singletons directly.
- **ContentRegistry:** ids are collected from every `.tres/.res` under `res://content`
  *and* from resources nested inside them (Hub Cores, cards, slices…). The same instance
  reached twice is fine; two different instances with the same id is a duplicate and fails
  validation. Files are visited in sorted path order (rule 7: no dictionary-order ties).
  `validate()` runs every resource's `validate()` and prefixes problems with class + id.
- **RngService:** stream seed = `hash([campaign_seed, stream_name])` (TECH_SPEC §4). Save
  representation stores seeds and states as decimal strings because JSON round-trips
  integers exactly only up to 2^53 and `RandomNumberGenerator.state` is 64-bit.
- **SaveService skeleton:** every file gets a top-level `"version"`; `migrate()` walks a
  table of `from_version -> Callable` steps. JSON numbers come back as floats, so loaders
  must `int()` what they read; 64-bit values travel as strings (see RngService).
- **CampaignConfigData schema additions** so every GDD §11 number lives in
  `content/config/campaign_config.tres` (rule 5): `exploit_heat`; Cycle reward ranges
  (`cycles_combat_range`, `cycles_elite_range`, `cycles_router_range`); new group
  **Shop** (card/firmware/daemon price ranges, card removal price + increment, slice and
  Miss-slice overwrite prices); new group **Schematic costs** (rookie, node base, node
  upgrade costs, netrun boost range, Heat purchase amount/cost/increment, class unlock);
  Combat `ram_regen_per_turn` and `respin_ram_cost`. Ranges use `Vector2i(min, max)`.
  `validate()` checks min ≤ max and non-empty upgrade costs. Smoke test batch 3 covers it.
- **Heat thresholds in data (GDD §4.3):** MINOR at 10/20/30/40/60/70/80/90, MAJOR at
  25/50/75, PURGE at 100. MAJOR ongoing modifiers: 25 → ELITE_FREQUENCY_PCT, 50 →
  ENEMY_RESISTANCE +1, 75 → RAID_STRENGTH_PCT +25. MINOR one-time complications alternate
  the two examples the GDD gives (shop stock −1 / extra elite). `event_raid` stays null
  until M3 authors RaidData.
- **ICE ladder in data (GDD §11.9):** one change per level, in the order the GDD lists them
  within each band (ICE 1 = Heat gain +10% … ICE 6 = Heat sinks −15%, matching the schema
  README example). Bands 6–10, 11–15 and 16–20 list four changes each, so levels 10, 15 and
  20 carry no modifier and are marked "Reserved" in their description.
- **Input map (GDD §9.5):** actions `nudge_left` (Q), `nudge_right` (E), `cycle_target`
  (Tab), `end_turn` (Space), `rewind` (Z and Ctrl+Z), `inspect` (right mouse). Physical
  keycodes, so layouts other than QWERTY keep the key positions.
- **Display:** 1280×720 viewport, `canvas_items` stretch, `keep` aspect (TECH_SPEC §10).

## Open questions for the designer
_(Claude Code: add questions here instead of guessing on design.)_

### From M1 (2026-09-24) — resolved by the designer on 2026-09-24
- **Flip** is a true mirror, implemented as a rearrangement: slot i's slice (with its
  status and Firmware) moves to slot −i mod n on both rings, docked satellites move with
  their slice, and the rotation is remapped (`r' = −r − 15`) so the tick under the top
  pointer becomes `15 − t` as GDD §2.3 states. Orientation stays clockwise, so nudges and
  spins need no special case; flipping twice restores the wheel. The `flipped` flag is gone
  from WheelState and the GDD code block no longer carries a `+15` term.
- **Breaker slice numbers** Crit 12 / Atk 6 / Def 5 confirmed.
- **Pierce ignores block and shield, not satellites** (GDD §2.7 and §6.4 updated). The
  bodyguard rule applies to piercing hits; the drone takes them.
- **Corrupted self-damage** straight to HP confirmed.
- **DOSE preview** stays hidden from the player (the engine still predicts it exactly).

### From M3 (2026-09-24)
- **Boss scaling.** A.3 lists the Renewal Engine at 300 HP / Atk 14 / Crit 24 with "Tier 1
  base values; scale per 11.6", but the boss Site is T4 (×4.1 → 1,229 HP, 98-damage Crit,
  one-shots a 60 HP operative). M3 uses the authored values unscaled. Confirm, or give the
  boss its own scaling.
- **Mid-run raid interludes.** Threshold raids reached during a netrun wait until the
  operative is back at HQ. GDD §4.4 allows an interlude between map nodes; do you want it
  (it needs the raid setup inside the netrun scene)?
- **Station bonuses** (Breaker: node assets +50% damage) are stored but not applied by the
  raid resolver yet; rank scaling for them is unspecified.
- **Raid movement details** filled in (see M3 decisions: waves every 5 steps, camping on
  the target node, live nodes stop the advance). Any of these you want different?
- **Rank 2 Hub Core upgrade** for the Breaker has no content (only tier gating exists).

### From M2 (2026-09-24) — resolved by the designer on 2026-09-24
- **Shop slice catalogue:** `CampaignConfigData.shop_slices` (Atk 6/8, Crit 12, Def 5/8,
  Shield 5, Evade) with `shop_slice_choices = 3` per Modem; new slices go in the catalogue
  rather than repeating the wheel. Tracked as a horizontal slice in
  `docs/CONTENT_SLICES.md` (new running list: vertical first, horizontal later).
- **Cycles ranges:** implementer's call stands (Router nodes 15–25, elites/Racks 30–40,
  10–20 reserved for non-node fights). Revisit in human playtest.
- **Elite frequency:** node combat type is always known before entering. ELITE_FREQUENCY_PCT
  adds a fraction of an elite per band layer at map generation; when the fraction reaches a
  whole node, one more Router in that layer is flipped to elite (never in place, never after
  the map is shown; each layer keeps a non-elite route). Elite Terminals are a horizontal
  backlog item.
- **Rescued operatives** become a free fresh rookie in the roster (as implemented).

### From M0 (2026-09-24) — resolved by the designer on 2026-09-24
- Godot version → 4.7 pin, GUT 9.7.1. "More elites" → 25% confirmed. ICE 9 → boss
  strength (+25% HP/damage) instead of BOSS_PHASE_EARLY. Minor Heat complications →
  alternate shop stock −1 / elite +25% (implementer's call). RAM cap → 12 (GDD §2.2).
- Still open: **ICE levels 10, 15 and 20** have no listed change; `REPAIR_COST_PCT = 25`
  (ICE 13) and `SEIZED_RAID_STRENGTH_PCT = 25` (ICE 14) are placeholders ("when in doubt,
  up elite and boss numbers" applied); MAJOR-threshold RaidData arrives in M3.
