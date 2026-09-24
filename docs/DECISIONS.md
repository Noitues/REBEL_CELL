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

### 2026-09-24 — Vertical-slice fixes, batch 4: menus, platform and onboarding (GAP_ANALYSIS §2.5)
- **Title scene** (`scenes/menu/title_scene.tscn`) is the main scene: Continue (the most
  recently saved numbered slot), Campaigns (three slots with corporation / Heat / ICE /
  runs / state, New / Load / Delete with a confirm), Tutorial, Codex, Stats &
  achievements (profile numbers, achievement list, the last 20 runs), Options, Quit
  (confirm). Saves carry `saved_at`; `SaveService.list_campaign_slots()` scans the save
  directory; test and demo slots are never offered.
- **Pause menu** (`PauseMenu`) replaces the bare accessibility popup on Esc in every
  scene: Resume, Options (the full `SettingsPanel` inline), Codex, Save & quit to title,
  Quit to desktop (confirm). The scene variable keeps its `_settings_panel` name so the
  keyboard test still checks it toggles.
- **Options** in five sections: Accessibility (unchanged), Display (windowed /
  fullscreen / borderless, resolution presets, v-sync, fps counter), Audio (master, music,
  SFX), Controls (rebind the twelve combat/menu actions by pressing a key; card keys stay
  1-9; Escape cancels; Reset restores the project defaults; bindings persist in
  `Settings.keybinds` and are applied to the InputMap at start-up), Language (locales
  with a loaded translation). Display changes are no-ops headless.
- **Autosave indicator**: Fx shows a marker "SAVED" that fades whenever SignalBus reports
  a completed save; **fps counter** in cell_acid top-right when enabled.
- **Tutorial** (`TutorialOverlay`): seven zine steps over the first fight (wheel, precision,
  resistance, cards & preview, rewind, End Turn, Heat & banking); steps with a trigger
  advance on the matching engine event (nudge, card, rewind, turn_start), the rest on
  Next; Skip or Finish sets `Settings.tutorial_done`. Starts automatically on a new
  profile's first fight (never headless) and from the title's Tutorial button
  (`RunManager.pending_tutorial` → the combat scene).
- **Achievements** (`Achievements.DEFS`, evaluated in `sync_profile_with_campaign`): First
  Blood, Banked (10 Racks), Breach, Clean Hands, Average Is a Lie (ICE 5), Cold Storage
  (ICE 10), Purge Survivor, The Wall (20 raids), Perfectionist (500 Perfects), Final Final
  (defined, unreachable until REBEL_CELL). The narrator announces new ones through
  Dialogue. `ProfileState.stats` (perfects, racks, cycles, runs per tier) and
  `run_history` (20 entries) feed the stats screen.
- **CI and export**: `.github/workflows/ci.yml` runs import, GUT, the schema smoke test,
  content validation and checks that `assets/text/strings.csv` is current, then exports
  Windows and Linux builds as artifacts (Godot 4.7.2 via setup-godot). `export_presets.cfg`
  (Windows, Linux, macOS; no credentials) is committed, so it left `.gitignore`.
  `application/config/version` is 0.9.0 and the title shows it.
- **Controller support** stays out of the vertical slice (GDD 9.5: PC mouse + keyboard);
  it remains a P2 horizontal item.
- **Performance**: TECH_SPEC's 1080p target still needs a human run; the fps counter is
  the tool for it. The core stays under 1 ms per turn in the automated check.

### 2026-09-24 — Vertical-slice fixes, batch 3: narrative, dialogue, subtitles, codex, text export (GAP_ANALYSIS §2.4)
- **Line database** (`LineSetData` of `VoiceLineData`): lines are keyed by moment
  (`site:<id>`, `raid:<id>`, `threshold:<heat>`, `boss/win/loss`, `run_start/complete/died`,
  `rack`, `bark:<trigger>`, `dj`) and carry a `drift_stage` and `dispatch_clue`. The
  **Dialogue** autoload picks a line deterministically (hash of key + salt, ties by text)
  and never uses global RNG; **DISPATCH drift** (GDD 8.2) is a profile stage: 0 for the
  first two campaigns started, 1 from the third, 2 from the sixth; a higher stage replaces
  the human line and those lines are the clues (impossible timestamps, evenly spaced
  breaths, "the projection allowed for it").
- **Subtitle bar** (GDD 9.6): bottom-centre CanvasLayer; speaker name; DISPATCH and Corpo
  on a dark strip in amber/corporate colour (clean system text, STYLE_GUIDE 3), everyone
  else on paper. Honours `Settings.subtitles`; `line_spoken` fires regardless for voice-over
  later; `history` feeds the codex's "lines heard". Queue of six, timed by text length.
- **Content**: 55 DISPATCH lines (a briefing for all 32 Solace Sites, boss/win/loss with
  drift variants, threshold lines, run lines), 8 Solace Collections raid warnings, 14
  Breaker barks (perfect, miss, hurt, victory, defeat, deploy, jack_in, boss; at most one
  per trigger per turn, never in headless/reduce-effects), 8 pirate-radio DJ lines at HQ
  (two carry stage-1/2 clues). Barks are per class (`LineSetData.class_id`), so each new
  class ships its own set.
- **Six written Solace story paths** replace the placeholders: Recall Notice, Clinical
  Trial, Terms of Service, The Cure, Ghost Patient (every beat a DISPATCH clue; beat II
  triggers the STORY raid; foreshadows `dispatch`) and Hostile Takeover (foreshadows
  `meridian`). Each has a premise, 3 beats in Exploit order, 2 bonus beats and a finale.
- **Corporations 2–4 named** (open question from the gap analysis, my call): **Meridian
  Freight Systems** (autonomous logistics; threats are fleet drones; Exploits: manifests,
  routing keys, fleet firmware), **Halcyon Civic** (municipal surveillance contractor;
  threats are wardens; Exploits: camera keys, warrant authority, the civic ledger) and
  **Orbital Commons** (satellite data commons gone private; threats are uplink hunters;
  Exploits: ephemeris, ground-station keys, the commons charter). Hostile Takeover points
  at Meridian. Horizontal work builds them.
- **Codex** (GDD 8.1): an HQ/start-screen panel built from `Codex.entries()` (slices,
  statuses and precision, cards, Firmware, Daemons, ring segments, enemies, nodes, assets,
  threats, lexicon) plus the last six lines heard.
- **Text externalisation** (GDD 10): `TextDb.key_for(res, field)` gives every content string
  a stable key (`CardData.jolt.description`); `tools/export_text.gd` writes
  `assets/text/strings.csv` (`keys,en`, 389 strings) keeping any locale columns already
  there; Godot's CSV importer produces the `.translation` files; `TextDb.t(res, field)`
  returns the loaded translation or the content text, so untranslated builds never show
  keys. `Settings.language` sets the locale. UI strings go through `TextDb.ui(key,
  fallback)` as they are touched. Voice recording stays out of scope for code (the
  `audio_path` field on lines is the hook).
- **Schema changes**: `VoiceLineData`, `LineSetData` (new), `Settings.language`, the
  `Dialogue` autoload (after Fx).

### 2026-09-24 — Vertical-slice fixes, batch 2b: Solace at size, events, map and raid presentation
- **Solace City Grid is 32 Sites** (GDD 4.1: 30-40), generated by a script and checked in:
  home → ten T1 Sites (all touch home, so the opening offers ten runs); eight T1 open one
  T2 each (Intel, Breach, Virus among them), every T2 opens a T3, every plain T3 reaches
  the Renewal Engine (minimum path stays T1 → T2 → T3 → boss); four Heat objectives
  (Scrub Records −5 off t1_a, Purge Camera Logs −5 off t1_i, Wipe Biometrics −8 at T2 off
  t1_j, Burn the Ledger −8 at T3 off t2_e, so ICE 2 switches off Wipe Biometrics first);
  eleven locked cross-links opened by the Intel Exploit or an Icebreaker. Slice ids
  (`t1_a`, `t2_intel`, `t3_core`, `scrub_records`, `renewal_engine_site`) are unchanged so
  saves and tests carry over. GDD A.6 is now historical.
- **Terminal events: 19** (5 placeholders kept + 14 written): corporate memos (Continuum
  pricing, clause 44, the silent recall), street-merc trades, an auditor on break, the
  dosage cabinet, a honeypot, a Daemon broker and a Burner vendor, the Patient 0000-0000
  ghost record, **a rescue** (Locked Ward: 12 HP or 60 Cycles for a fresh Breaker) and the
  **DISPATCH clue chain** (Early Reply at T1, Escrow Receipt at T2, Voice Note at T3, all
  `dispatch_clue` + `foreshadows = dispatch`). Events honour `min_tier` (the pool filters
  on the run's tier). Original slang only (leash, subbie, bricked, ghosting).
- **Netrun map as a wireframe graph** (`NetrunMapView`): layers left to right, glyph per
  node type, current node cell_pink, reachable nodes cell_acid with a glow, visited nodes
  dimmed, Heat cost labelled; click a reachable node or press 1-9.
- **Raid playout** (`RaidPlayoutPanel`, GDD 7.2/9.3): the precomputed events are grouped
  by step (setup = link freezes/openings), shown at 0.9 s per step with 1×/2×/4× and Skip;
  threat markers move on the `GridMapView` (corporate dots + names), frozen links draw in
  resist_gold. Instant (straight to the summary) when headless or under reduce-effects,
  so the integration tests and the accessibility toggle both skip the wait. HQ and the
  mid-run interlude share the panel.
- **HQ screens**: start panel picks the ICE level (0..cap, with the cumulative ladder text)
  and the home-server variant; HQ sells next-run boosts and Profile unlocks and offers
  Rank 3 segment swaps per operative; the Grid lists every installable node type (locked
  ones disabled), an Upgrade button with its cost, switched-off objectives and ICE.
- Dense grids (> 16 Sites) draw smaller blocks with "T<n> <glyph>" labels.

### 2026-09-24 — Vertical-slice fixes, batch 2a: netrun and campaign rules (GAP_ANALYSIS §2.2-2.3)
- **Every remaining `RuleModifierType` is applied**: `HEAT_GAIN_PCT` scales positive Heat
  deltas and `HEAT_SINK_PCT` negative ones inside `HeatRules.add_heat` (a non-zero delta
  never rounds to zero); `PURGE_THRESHOLD` (ICE 17, value 90) makes the PURGE threshold
  fire at 90 (recorded as 100 in `thresholds_fired`); `HEAT_OBJECTIVE_SITES` (ICE 2, −1)
  switches off that many Heat-objective Sites at campaign start, the last by id
  (`CampaignState.disabled_objectives`, read through `CampaignRules.site_objective`);
  `DEATH_HEAT` and `EXPLOIT_HEAT` add to the base amounts before gain scaling;
  `CYCLE_PRICE_PCT` scales every Modem price including removals and overwrites;
  `REPAIR_COST_PCT` scales repairs; `SEIZED_RAID_STRENGTH_PCT` adds to raid strength when
  any entry Site is Seized; `RAID_EXTRA_WAVE` repeats the raid's last wave 5 steps later.
  Modifiers stack multiplicatively with ICE 1's gain (a death at ICE 8 is (10 + tier + 5)
  × 1.1), which is how a cumulative ladder should feel.
- **Node types complete** (GDD 3.2): Compiler Rack (a run launched next to an active one
  starts in the REWARD phase with one 1-of-3 card offer per adjacent Rack), Vault Terminal
  (+3 Schematics per completed run via `passive_effects`, +2 more next to a Firewall Relay
  via `adjacency_bonuses`, raid_priority 2, building it queues the NODE_BUILT raid) and
  Proxy Relay (−1 Heat per completed run; counts as a Relay for reach). Passives and
  adjacency bonuses with trigger ON_NETRUN_COMPLETE are evaluated in
  `CampaignRules.on_run_completed` for active nodes in id order; Disabled nodes give
  nothing. The three new nodes are **Profile unlocks** (30 Schematics each,
  `content/unlocks/`); `claim_error` refuses a locked node when a profile is passed.
- **Node upgrades** (GDD 11.4): `upgrade_node` costs `node_upgrade_costs[level]` (30, 60);
  each level adds `node_upgrade_integrity_pct` (50%) of the base integrity and
  `node_upgrade_asset_slots` (1) slots (`GridState` site `upgrade_level`). Home is not
  upgradable this way (variants cover it).
- **Home-server variants** (GDD 3.1): internal nodes fold into the home server's capacity
  (integrity, asset slots, built-in defenses in `GridState.home_asset_slots /
  home_built_in`) rather than becoming Grid sites; the Bunker variant (40 + 30 integrity,
  1 + 2 slots, built-in turret) is a 40-Schematic Profile unlock. `RunManager.new_campaign`
  takes the ICE level and the variant.
- **Netrun boosts** (GDD 11.4): `NetrunBoostData` (cycles, run-only cards, max RAM bonus)
  listed in `config.netrun_boosts`; bought at HQ into `CampaignState.pending_boosts`, all
  consumed by the next run (`RunState.temp_cards` leave the deck on completion). Warm
  Cache 10 (+40 Cycles), Overclocked Deck 15 (two Jolts), Field Kit 20 (+2 max RAM).
- **Routers drop common Firmware** with `router_firmware_chance` (0.35), 1-of-2 from
  Firmware of rarity COMMON; elites keep 1-of-2 of any rarity.
- **Raid triggers** (GDD 4.4): RETALIATION raids follow every Exploit and Heat-objective
  run and enter from the Site just cleared; STORY raids fire from beats marked
  `StoryBeatData.triggers_raid` (Ghost Patient II); NODE_BUILT raids from nodes with
  `triggers_raid` (Vault Terminal), falling back to the claim raid when a corporation has
  no such template. Solace gained three raid templates and two threats: **Icebreaker**
  (`alters_edges`: opens the first locked link, by id, touching its entry; the route
  stays open) and **Lockdown Unit** (`freezes_edges`: freezes the link between home and
  the neighbour holding the most deployed assets for that raid only; nothing routes or
  shoots across a frozen link). Both resolve in setup so the projection shows them.
- **Stationed operatives** return unharmed from Disabled nodes too (cascade included).
- **Rank counts full netruns only**: Reclaim runs (one fight) no longer raise Rank; the
  breach ends the campaign. `runs_completed` still counts them.
- **ICE progression** (GDD 3.4): `ProfileState.ice_cap_for` = max(3, best on that
  corporation + 3, global best − `new_corp_ice_offset`), capped at 20. A fresh profile
  chooses ICE 0–3.
- **Schema changes**: `NetrunBoostData` (new), `CampaignConfigData.netrun_boosts /
  node_upgrade_integrity_pct / node_upgrade_asset_slots / router_firmware_chance /
  router_firmware_choices`, `StoryBeatData.triggers_raid`, `GridState.home_asset_slots /
  home_built_in / frozen_links / upgrade_level`, `CampaignState.pending_boosts /
  disabled_objectives / home_variant_id`, `RunState.temp_cards`. Smoke test batch 5.

### 2026-09-24 — Vertical-slice fixes, batch 1: combat rules (GAP_ANALYSIS §2.1)
Designer instruction: "make calls on every decision". Every call below is logged here
and annotated in the GDD where it changes a rule.
- **ICE/Heat combat modifiers are applied through `NetrunSession.rule_overrides()`**:
  `ENEMY_RESISTANCE` adds passive resistance to every non-satellite enemy (satellites are
  nudged individually and stay at 0); `BOSS_STRENGTH_PCT` multiplies HP and output of the
  final boss **and mini-bosses** (the designer's "up the boss numbers"); `BOSS_EXTRA_POINTER`
  adds pointers to the final boss only, evenly spaced (offsets 15, 10, 20, 5, 25 from
  pointer 0, first free wins) and survives phase changes via the trim/add rules;
  `NO_FIRST_TURN_FREE_NUDGE` zeroes the free nudge on turn 1 only; `STARTING_BUG_CARD`
  puts N **Bug** cards (0 RAM, drains 1 RAM, exhaust, `CardData.offered = false` so it is
  never a reward or Modem stock) into the working deck at run start — a Modem removal
  is the counterplay, and the roster copy only inherits them on completion.
- **HeatGatedEffectData is live**: an enemy's `heat_effects` join its listeners while the
  Heat at combat start (`CombatState.campaign_heat`) is at or above `min_heat`. Content:
  Compliance Officer at Heat 50+ drains 1 RAM per attack ("Audit"); Account Manager at
  Heat 75+ heals 5 per turn ("Retainer").
- **Satellite spawns**: `ON_TURN_START` spawns count every start of turn (turn 1
  included), fire every `every_n`, and only while fewer than `max_active` satellites of
  that template are alive on the host.
- **MIGRATE is telegraphed**: entering a MIGRATE phase stores the layout in
  `WheelState.pending_pointer_ticks` (event `boss_migrate_telegraph`); the pointers move at
  that wheel's next start of turn (event `boss_migrate`). The view draws the pending
  pointers dashed in cell_acid with a "next" tag and flickers the current ones. Account
  Manager gained a 25% MIGRATE phase (pointers 5 and 20).
- **`BossPhaseData.wheel_override`** swaps slices, Firmware, statuses (reset) and passive
  resistance; rotation, pointers and pending migrations are kept; the override's hub
  applies unless `hub_override` is set. The Renewal Engine's ORBIT phase now swaps its
  second Atk 14 for a Crit 24.
- **Player drones (GDD 5.2)** live in `CombatState.drones` as satellites with
  `is_player = true`, host `player`. A DEPLOY slice docks the Hub's `drone` template
  (new `HubCoreData.drone`) on the Deploy slice itself or the next free slice clockwise,
  up to `max_drones`; `DEPLOY_DRONE` effects may pick the slice (`slice_pick`). A drone
  resolves only in a turn where the slice it docks on resolves (any player pointer), at
  full output, against the player's target; enemy attacks aimed at a guarded slice hit
  the drone (same bodyguard rule as enemy satellites). Drones respin with the wheel, do
  not get Kernel Sync or Daemon listeners, and die like satellites (deaths of combatants
  spawned mid-resolve are reported the same turn). Drones persisting between combats
  (Botnet passive) is left to the Botnet class work.
- **Rule-breaking Daemons**: Linked Bus echoes nudge *actions* (not nudge cards) on
  enemy wheels to your wheel, free, ignoring resistance; Stolen Intent fires automatically
  once per combat when your first pointer would resolve Miss and the target's first
  pointer would not, swapping the two slices (own tiers kept) through the new
  `ON_RESOLVE` trigger that hands handlers the collected resolutions; Twin Pointer adds a
  pointer 15 ticks from yours at combat start (`ON_COMBAT_START` Daemon hooks now run in
  `begin_combat`) and halves max RAM rounding up (`CombatState.max_ram`, 12 → 6); Botnet
  Seed docks a 1-HP `seed_drone` on the Perfect slice, max 2 seed drones alive.
- **Ring segments** Corrupt (ON_SLICE_TRIGGER → CORRUPTED on the target's slice under the
  matching pointer, clamped to its last pointer), Anchor (ON_PERFECT → FREEZE own wheel),
  Accelerator (ON_SLICE_TRIGGER → `DOUBLE_NUDGE_CARDS`: nudge cards resolve twice next
  turn, `CombatState.double_nudge_cards[_next]`), Echo (RETRIGGER ×0.5) are data. **Rank 3
  swap flow**: `RankRewardData.ring_segment_options` (Breaker: all four),
  `OperativeState.ring_segment_ids`, `CampaignRules.swap_ring_segment()` (free, any time
  between runs, empty id restores the default), passed to combat as the
  `ring_segment_ids` override.
- **RAM Respin action** (GDD 2.5 lists Respin as a card, 11.3 prices it at 4 RAM; the card
  pool has none): `CombatAction.RESPIN` respins your own wheel for `respin_ram_cost`, is a
  random event (checkpoint) and previews exactly. Key X.
- **Combat UI**: chosen-slice picker (F cycles, auto = none) and card direction picker (D)
  feed `CombatAction.slot_index` / `direction`; random effects (Respin, random slice picks)
  show **odds** as the slice-type mix of the wheel instead of the roll; right-click
  **inspect** describes the slice, Firmware, status and guard under the cursor (or the
  hub/segments at the centre) via the new `Codex` helper, in the left-column note that
  otherwise lists the installed Daemons; revealed boss phases (Intel) print on the enemy
  wheel; the log strip plays the three passes with a 0.35 s beat between them (instant
  under headless or reduce-effects; the wheels always show the final state at once).
- **Schema changes** (rule 8): `CardData.offered`, `HubCoreData.drone`,
  `RC.Trigger.ON_RESOLVE` (appended), `CombatAction.Type.RESPIN` (appended),
  `WheelState.pending_pointer_ticks`, `CombatState.drones/max_ram/campaign_heat/
  double_nudge_cards[_next]`, `OperativeState.ring_segment_ids`. Smoke test batch 4.
- **Timeline captures** (`docs/timeline/`): the designer asked for screen captures per
  system over time; each batch adds dated frames.

### 2026-09-24 — M4 Look, Feel & Accessibility
- **No approved mockups are in the repo** (STYLE_GUIDE points at a private canvas), so the
  screens follow the style guide's component rules literally: three worlds per screen,
  colour tokens in `Palette`, the three fonts, zine kit elements by name (Polaroid,
  ransom-note Heat, marker RAM tally, torn-paper log strip, SEND IT stamp, card stickers,
  graffiti tag, wanted poster, pirate radio, JACK IN, THE PLAN sidebar). Automated
  layout rules: zine elements never intersect a wheel's disc; player wheel `cell_pink`,
  enemy wheels `corp_*`; each screen shows its world background.
- **Fonts** (Permanent Marker — Apache 2.0, Anton and Share Tech Mono — OFL 1.1) are
  vendored from github.com/google/fonts with their licences in `assets/fonts/`.
- **Effects architecture:** one `Fx` autoload (CanvasLayer) owns the scanline / flicker /
  chromatic overlay (all three are shader uniforms), the Heat distortion pulse, screen
  flashes and the jack-in / jack-out transition. `Settings.reduce_effects` hides the
  overlay, zeroes the distortion, freezes background animation and skips freeze frames and
  stutter shakes. The glow and paper shaders are static and stay on.
- **Flash limiter** is a pure sliding-window class (`FlashLimiter`, 3 per rolling second)
  used by `Fx.flash()` and by the automated event-stream check, which maps the flash-worthy
  combat event types (Perfect retrigger, boss phase, Heat threshold, combat end, Zero Day)
  onto a timeline and asserts no one-second window holds more than three.
- **Without-colour readability:** a distinct glyph per slice type (▲ ✦ ■ ◇ ⬢ ⬡ ✚ ◈ ✕) and
  per status (☠ ⚡ ⌗) plus text tags; the Miss slice has a dashed outline; resistance is
  labelled, not only gold.
- **Keyboard play:** 1–9 play cards, Q/E nudge, W nudge wheel toggle, R ring toggle, T card
  target toggle, Tab target, Space end turn, Z / Ctrl+Z rewind, Esc settings; cards and the
  stamp are focusable.
- **Placeholder audio is generated in code** (`AudioDirector`): ratchet ticks, spins as
  decelerating click runs, flip clack, latch/click/stutter/static precision feedback, and
  4-second loops per music context with a Heat layer for combat. Real assets swap in behind
  the same API.
- **Performance:** fps at 1080p cannot be measured headless; the core budget is enforced
  by test (< 1 ms per resolved turn including state duplication) and every effect is a
  cheap 2D shader or `_draw` call that reduce-effects can disable.

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

### From M3 (2026-09-24) — resolved by the designer on 2026-09-24
- **Tier scaling hits everything**, including the final boss (T4 ×4.1) and the new
  **mini-bosses**: every netrun's final Server Rack is guarded by a corporation mini-boss
  (`EnemyData.is_mini_boss`, may have phases). Solace: *Account Manager* (120 HP, Atk 10,
  Def 8, Crit 16, Dose, Shield 5, Miss; resistance 1; at 50% multiplies to two pointers).
  Playtest risk noted: a T4 Renewal Engine Crit is 98 damage against 60 HP operatives.
- **Mid-run raid interludes** are in: whenever a run would return to the map with a raid
  queued, `RunState.Phase.RAID` opens the setup inside the netrun scene (projection, the
  run's own assets and the Armory both deployable, playout). Losing the home server there
  ends the run as ABORTED. Runs that launch with a raid already queued fight it first.
- **Station bonus scaling** (made up): the class `station_bonus` is a DEAL_DAMAGE effect
  whose `multiplier` is the asset damage factor (Breaker 1.5); Rank scales the bonus part
  by `RankRewardData.station_bonus_multiplier` = 1.25 / 1.5 / 2.0 at Ranks 1 / 2 / 3, so a
  Rank 3 Breaker doubles asset damage. It applies to the stationed node and to adjacent
  Firewall Relays.
- **Raid movement details** confirmed as a starting point.
- **Breaker Core Mk2** (Rank 2 Hub upgrade, made up): +2 spin on all cards; Perfect
  resolves the slice twice and refunds 1 RAM per resolution. Operatives fight with the
  highest hub upgrade their Rank has earned (`OperativeState.hub_id`).

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
