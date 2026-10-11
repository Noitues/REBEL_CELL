## Implementation decisions (DECISIONS.md:10110)
### 2026-09-24 Vertical-slice fixes, batch 5
- RULING 2026-09-24 rank gating: `RunManager.launch_error` passes the operative's own ClassData; `CampaignRules.launch_error` refuses a mismatched class.
- RULING 2026-09-24 grid map click: selects a Site; its row is listed first under "SELECTED >" and the Site gets a cell_acid ring.
- RULING 2026-09-24 netrun panels: rewards and Modem stock are zine stickers (cards show RAM cost, stock shows Cycle price, Firmware/Daemon offers show none); street/corporate events on ZinePanel; DISPATCH events on a clean dark strip, never zined; run end is a stamp plus a torn note.
- RULING 2026-09-24 balance sim: `CombatBot` plays greedily from the End Turn preview and never plays random-outcome cards; `CampaignSimulator` uses fixed policies; `tools/simulate_campaign.gd -- <seeds> <ice> [verbose]`.
- DEFAULT sim results (8 seeds): ICE 0: 8/8 wins, 25.9 runs, 5.3 raids, Heat peak 78; ICE 5: 6/8 wins, 21.0 runs, 6.1 raids, Heat peak 84. GDD 11.8 targets ≈24 runs, ≈7 raids.
- RULING 2026-09-24 home server patch: HQ "Patch home" restores integrity at `home_repair_cost_per_point` (1) Schematics per point; partial patches allowed. GDD 3.3 annotated.
- RULING 2026-09-24 retaliation raids: only Exploit extraction at Heat ≥ `retaliation_min_heat` (50) provokes one; Heat objectives never do. SUPERSEDES batch 2a retaliation rule. GDD 4.4 annotated.
- RULING 2026-09-24 patrol runs: any cleared or claimed Site except home and boss can be rerun as a full netrun (normal loot, Heat, Rank; no objective); Grid unchanged afterwards (node passives still apply). Launch kind "patrol".
- RULING 2026-09-24 enemy damage scale: HP keeps `enemy_scale_per_tier` 1.6; slice outputs use `enemy_damage_scale_per_tier` = 1.2 (tuned by sim). Both scales hit normal enemies, mini-bosses and boss. `CombatantState.hp_scale` lets satellites inherit host HP scale. GDD 11.6 annotated.
- RULING 2026-09-24 the bot skips Burner Firmware (Heat per trigger).
- RULING 2026-09-24 M5 "Vertical completion" recorded in MILESTONES.md.
- DEFAULT schema additions: `CampaignConfigData.home_repair_cost_per_point / retaliation_min_heat / enemy_damage_scale_per_tier`, `CombatantState.hp_scale`.

### 2026-09-24 Batch 4: menus, platform, onboarding
- RULING 2026-09-24 title scene `scenes/menu/title_scene.tscn` is the main scene (Continue = latest saved numbered slot, Campaigns with three slots, Tutorial, Codex, Stats & achievements, Options, Quit with confirm). Saves carry `saved_at`; `SaveService.list_campaign_slots()`; test and demo slots never offered.
- RULING 2026-09-24 `PauseMenu` replaces the accessibility popup on Esc in every scene (Resume, Options, Codex, Save & quit to title, Quit to desktop); scene variable stays `_settings_panel`.
- RULING 2026-09-24 Options has five sections: Accessibility, Display, Audio, Controls (rebind twelve actions; card keys stay 1-9; Escape cancels; bindings in `Settings.keybinds`), Language. Display changes are no-ops headless.
- RULING 2026-09-24 autosave "SAVED" marker via Fx; fps counter in cell_acid top-right.
- RULING 2026-09-24 `TutorialOverlay`: seven zine steps in the first fight; Skip/Finish sets `Settings.tutorial_done`; auto-starts on a new profile's first fight (never headless); `RunManager.pending_tutorial`.
- RULING 2026-09-24 achievements in `Achievements.DEFS`, evaluated in `sync_profile_with_campaign`; Final Final defined but unreachable until REBEL_CELL; `ProfileState.stats` and `run_history` (20).
- RULING 2026-09-24 CI `.github/workflows/ci.yml` (import, GUT, schema smoke, content validation, strings.csv current, Windows/Linux export, Godot 4.7.2); `export_presets.cfg` committed; version 0.9.0.
- RULING 2026-09-24 controller support stays out of the vertical slice (P2 horizontal).
- OPEN performance: the TECH_SPEC 1080p target needs a human run (fps counter is the tool); core stays under 1 ms per turn.

### 2026-09-24 Batch 3: narrative, dialogue, codex, text
- RULING 2026-09-24 line database `LineSetData`/`VoiceLineData` keyed by moment; the Dialogue autoload picks deterministically (hash of key + salt, ties by text), no global RNG.
- RULING 2026-09-24 DISPATCH drift (GDD 8.2) is a profile stage: 0 for the first two campaigns, 1 from the third, 2 from the sixth; higher stage replaces the human line (lines are the clues).
- RULING 2026-09-24 subtitle bar (GDD 9.6): honours `Settings.subtitles`; `line_spoken` fires regardless; DISPATCH and Corpo on dark strip; queue of six.
- DEFAULT content: 55 DISPATCH lines, 8 raid warnings, 14 Breaker barks (per class via `LineSetData.class_id`; max one per trigger per turn; none headless/reduce-effects), 8 DJ lines.
- RULING 2026-09-24 six written Solace story paths replace placeholders (Recall Notice, Clinical Trial, Terms of Service, The Cure, Ghost Patient with beat II triggering the STORY raid, Hostile Takeover foreshadowing `meridian`).
- RULING 2026-09-24 corporations 2-4 named (designer's call): Meridian Freight Systems, Halcyon Civic, Orbital Commons.
- RULING 2026-09-24 Codex (GDD 8.1) from `Codex.entries()` plus last six lines heard.
- RULING 2026-09-24 text externalisation (GDD 10): `TextDb.key_for`, `tools/export_text.gd` writes `assets/text/strings.csv`; `TextDb.t(res, field)` falls back to content text; `Settings.language`; UI strings via `TextDb.ui(key, fallback)`. Voice recording out of scope (`audio_path` hook).
- DEFAULT schema: `VoiceLineData`, `LineSetData`, `Settings.language`, `Dialogue` autoload after Fx.

### 2026-09-24 Batch 2b: Solace at size, events, map, raid presentation
- RULING 2026-09-24 Solace Grid is 32 Sites (GDD 4.1), 10 T1 touching home, four Heat objectives (Scrub Records −5, Purge Camera Logs −5, Wipe Biometrics −8, Burn the Ledger −8; ICE 2 switches off Wipe Biometrics first), eleven locked cross-links opened by Intel Exploit or Icebreaker. Slice ids unchanged. GDD A.6 historical.
- RULING 2026-09-24 terminal events: 19, include rescue and DISPATCH clue chain (T1/T2/T3); events honour `min_tier`; original slang only.
- RULING 2026-09-24 `NetrunMapView` wireframe graph: click reachable node or keys 1-9.
- RULING 2026-09-24 `RaidPlayoutPanel` (GDD 7.2/9.3): 0.9 s per step, 1×/2×/4×, Skip; instant when headless or reduce-effects; shared by HQ and interlude.
- RULING 2026-09-24 HQ screens: ICE picker 0..cap with ladder text, home variant, boosts, unlocks, Rank 3 swaps; Grid lists installable nodes. Dense grids (>16 Sites) draw smaller blocks.

### 2026-09-24 Batch 2a: netrun and campaign rules
- RULING 2026-09-24 every `RuleModifierType` applied: HEAT_GAIN_PCT/HEAT_SINK_PCT in `HeatRules.add_heat` (non-zero never rounds to zero); PURGE_THRESHOLD (ICE 17, 90); HEAT_OBJECTIVE_SITES (ICE 2, −1; last by id; `CampaignState.disabled_objectives`); DEATH_HEAT/EXPLOIT_HEAT add before gain scaling; CYCLE_PRICE_PCT all Modem prices; REPAIR_COST_PCT; SEIZED_RAID_STRENGTH_PCT; RAID_EXTRA_WAVE repeats last wave 5 steps later. Modifiers stack multiplicatively.
- RULING 2026-09-24 node types: Compiler Rack, Vault Terminal (+3 Schematics per run, +2 next to Firewall Relay, raid_priority 2, queues NODE_BUILT raid), Proxy Relay (−1 Heat per run; counts as Relay). Evaluated in `CampaignRules.on_run_completed` in id order; Disabled nodes give nothing. The three are Profile unlocks (30 Schematics).
- RULING 2026-09-24 node upgrades (GDD 11.4): `node_upgrade_costs` (30, 60); +`node_upgrade_integrity_pct` 50% and +`node_upgrade_asset_slots` 1 per level; home not upgradable (variants).
- RULING 2026-09-24 home variants (GDD 3.1): internal nodes fold into home capacity; Bunker (40+30 integrity, 1+2 slots, built-in turret) is a 40-Schematic unlock.
- RULING 2026-09-24 netrun boosts (GDD 11.4): Warm Cache 10 (+40 Cycles), Overclocked Deck 15 (two Jolts), Field Kit 20 (+2 max RAM); all consumed by the next run.
- DEFAULT `router_firmware_chance` 0.35, 1-of-2 COMMON Firmware; elites 1-of-2 any rarity.
- RULING 2026-09-24 raid triggers (GDD 4.4): RETALIATION after every Exploit and Heat-objective run (SUPERSEDED by batch 5); STORY from `triggers_raid` beats; NODE_BUILT from nodes with `triggers_raid`. Icebreaker (opens first locked link) and Lockdown Unit (freezes link) resolve in setup.
- RULING 2026-09-24 stationed operatives return unharmed from Disabled nodes.
- RULING 2026-09-24 Rank counts full netruns only; Reclaim runs do not raise Rank (still count in `runs_completed`).
- RULING 2026-09-24 ICE progression (GDD 3.4): `ice_cap_for` = max(3, best on corporation + 3, global best − `new_corp_ice_offset`), capped 20; fresh profile ICE 0-3.

### 2026-09-24 Batch 1: combat rules
- RULING 2026-09-24 designer instruction: "make calls on every decision"; all calls logged.
- RULING 2026-09-24 ICE/Heat combat modifiers via `NetrunSession.rule_overrides()`: ENEMY_RESISTANCE (non-satellites); BOSS_STRENGTH_PCT (final boss and mini-bosses); BOSS_EXTRA_POINTER (final boss only, offsets 15, 10, 20, 5, 25); NO_FIRST_TURN_FREE_NUDGE; STARTING_BUG_CARD (Bug: 0 RAM, drains 1 RAM, exhaust, `offered = false`).
- RULING 2026-09-24 HeatGatedEffectData live from `CombatState.campaign_heat`: Compliance Officer Heat 50+ "Audit"; Account Manager Heat 75+ "Retainer" (heal 5).
- RULING 2026-09-24 satellite spawns ON_TURN_START count every turn start, every `every_n`, only while fewer than `max_active` alive.
- RULING 2026-09-24 MIGRATE telegraphed via `WheelState.pending_pointer_ticks`; pointers move at the wheel's next start of turn. Account Manager has 25% MIGRATE phase.
- RULING 2026-09-24 `BossPhaseData.wheel_override` semantics (keeps rotation, pointers, pending migrations); Renewal Engine ORBIT swaps an Atk 14 for Crit 24.
- RULING 2026-09-24 player drones (GDD 5.2) in `CombatState.drones`; resolve only when their slice resolves; no Kernel Sync/Daemon listeners; persistence between combats left to Botnet class work.
- RULING 2026-09-24 rule-breaking Daemons: Linked Bus, Stolen Intent (ON_RESOLVE), Twin Pointer (halves max RAM 12 → 6), Botnet Seed (max 2 seed drones).
- RULING 2026-09-24 ring segments Corrupt, Anchor, Accelerator, Echo are data; Rank 3 swap via `CampaignRules.swap_ring_segment()` (free between runs; empty id restores default).
- RULING 2026-09-24 RAM Respin action: `respin_ram_cost` 4 RAM, key X, random event (checkpoint), previews exactly.
- RULING 2026-09-24 combat UI: slice picker (F), card direction (D), odds shown for random effects, right-click inspect via `Codex`, log strip 0.35 s beat (instant headless/reduce-effects).
- DEFAULT timeline captures per batch in `docs/timeline/`.

### 2026-09-24 M4 Look, Feel & Accessibility
- RULING 2026-09-24 no approved mockups in repo; screens follow STYLE_GUIDE literally; zine elements never intersect a wheel's disc; player wheel `cell_pink`, enemy wheels `corp_*`.
- RULING 2026-09-24 fonts vendored (Permanent Marker, Anton, Share Tech Mono) with licences.
- RULING 2026-09-24 one `Fx` autoload owns overlays; `Settings.reduce_effects` hides overlay, zeroes distortion, freezes background, skips freeze frames and shakes.
- RULING 2026-09-24 `FlashLimiter`: max 3 flashes per rolling second, also asserted on the event stream.
- RULING 2026-09-24 without-colour readability: glyph per slice type and status plus text tags; Miss dashed; resistance labelled.
- RULING 2026-09-24 keyboard: 1-9 cards, Q/E nudge, W, R, T, Tab, Space, Z/Ctrl+Z, Esc.
- RULING 2026-09-24 placeholder audio generated in `AudioDirector`.
- RULING 2026-09-24 core budget < 1 ms per resolved turn enforced by test; 1080p fps not measurable headless.

### 2026-09-24 M3 Campaign & Raids
- RULING 2026-09-24 `GridState` holds per-Site runtime state; layout stays in `CityGridData`; `NetworkNodeData.id` added.
- RULING 2026-09-24 Heat thresholds (`HeatRules`): fire on upward crossings not in `thresholds_fired`; MAJOR/PURGE → `pending_raids`, MINOR → `pending_complications`; modifiers read live.
- RULING 2026-09-24 raids resolve at HQ; threshold raids mid-run wait. Projection and playout are the same pure `RaidResolver.resolve`.
- OPEN mid-run interlude (GDD 4.4) deferred (later built as shared panel in batch 2b).
- RULING 2026-09-24 raid step rules (TECH_SPEC §7): wave k spawns at step 1+5k; shortest paths, ties by Site id; ICE Locks hold once per lock; node damage 0 → Disabled, cascade `floor(excess × cascade_ratio)` no chaining; step cap 30; win = all threats destroyed → RaidData reward, otherwise +5 Heat; RAID_STRENGTH_PCT scales threats.
- RULING 2026-09-24 claiming needs a cleared Site adjacent to home or live Relay/Firewall Relay, costs install cost, TERRITORY_CLAIM raid if touching corporate or Seized Site.
- RULING 2026-09-24 node slots: Relay 1, Firewall Relay 2 (+3-damage turret), Safehouse 1 (+1 station), home 2.
- OPEN station bonuses recorded but not applied in raids (scaling question).
- RULING 2026-09-24 boss and Reclaim runs are one-node `NetrunSession`s; Reclaim pays 10-20 Cycles.
- RULING 2026-09-24 boss phases in `CombatResolver._check_boss_phases`; Breach never below one pointer; Virus corrupts two random boss slices; Intel flags `reveal_phases`.
- RULING 2026-09-24 story path picked from `events` stream; each Exploit reveals next beat.
- RULING 2026-09-24 `ProfileState` in `profile.json`; `to_dict()` JSON-normalised.
- RULING 2026-09-24 Breaker Rank 2/3 rewards gate tiers only (T3/T4).
- RULING 2026-09-24 HQ scene is the main scene (later superseded by title scene, batch 4).

### 2026-09-24 M2 Netrun Loop
- RULING 2026-09-24 run randomness from run `RngStreams` (`map`, `combat`, `rewards`, `events`), saved with the run.
- RULING 2026-09-24 map generator per TECH_SPEC §6; config `map_modem_layers` (3-5), `map_elite_layers` (3-6), `map_elites_per_layer` (1), `map_terminal_ratio` (0.25); Elite Heat charged on entering, Server Rack Heat on capture.
- DEFAULT Cycles: Router 15-25 (`cycles_router_range`), Elite/Rack 30-40 (`cycles_elite_range`); ×1.7^(tier−1); HP and outputs ×1.6^(tier−1).
- RULING 2026-09-24 rewards: 1-of-3 cards (skip allowed); elite 1-of-2 Firmware; Rack 1-of-3 unowned Daemons, banks `rack_schematics_by_tier`; asset drop 0.4 per fight, unbanked until a Rack.
- RULING 2026-09-24 Modem: 3 cards, 2 Firmware, 1 Daemon; removal 50 (+25 each); overwrite 100 (150 Miss slot).
- OPEN slice overwrite options are distinct non-Miss slices on the wheel (real slice catalogue needed).
- RULING 2026-09-24 enemy pools derived from content (corporation_id "solace", 6-slice, not boss; `is_elite` splits).
- RULING 2026-09-24 `OperativeState` runs on a copy written back only on completion; death is permadeath.
- RULING 2026-09-24 Daemon hooks in TECH_SPEC order; custom handlers `handle(context, state, rng)`; Kernel Sync +1 from next attack; Zero Day = 3 × best Crit (else Attack).
- RULING 2026-09-24 custom card effects (Ring Lock, Momentum, Calibrate, Steady Hand, Undock) keep markers in `CombatState`.
- RULING 2026-09-24 Firmware: Mirror copies neighbour on landed side; Shunt resolves neighbour at ×1.5; positive offset = clockwise.
- RULING 2026-09-24 save: one JSON per slot `user://saves/campaign_<slot>.json`; autosave on node entry, after combats, steps, and quit.

### 2026-09-24 M1 Combat Core
- RULING 2026-09-24 Godot pin 4.7 (GUT 9.7.1); elite frequency 25%; `BOSS_PHASE_EARLY` dropped for BOSS_STRENGTH_PCT (+25% at ICE 9; GDD 11.9 "bosses change pointers earlier" superseded); minor Heat complications alternate shop −1 (10/30/60/80) and elite +25% (20/40/70/90); RAM cap 12 via `ClassData.max_ram`.
- OPEN flip math: code block `tick = (rotation + pointer + 15 if flipped) mod 30` implemented; prose would be `pointer + 15 − rotation`; discrepancy unresolved.
- RULING 2026-09-24 state references content by id through `ContentLookup`.
- RULING 2026-09-24 one status per slice; ENCRYPTED absorbs next status; OVERCLOCKED → CORRUPTED; CORRUPTED self-damage ignores block/shield.
- RULING 2026-09-24 simultaneity: all pointers collected before passes; deaths apply after status pass; dead host takes satellites.
- OPEN pierce ignores satellites and block but not shield (shield is a separate resource).
- RULING 2026-09-24 output rounding `roundi(base × multipliers)`; Breaker "+1 spin" is a PASSIVE SPIN effect on Hub Core.
- RULING 2026-09-24 `EffectData.slice_pick` (UNDER_POINTER / RANDOM_NON_MISS / CHOSEN); NUDGE multiplier 0.0 ignores resistance (Jam).
- RULING 2026-09-24 enemies always attack the operative; player attacks aim at `CombatState.target_id`.
- RULING 2026-09-24 checkpoints detected by RNG state change; rewind restores checkpoint; preview clones RNG; DOSE shown as "random non-Miss slice".
- RULING 2026-09-24 Respin adds 2×30 + rand(0..29) ticks, clears `flipped`; Hub Breach lasts one full turn.
- DEFAULT combat scene starts the Breaker at Rank 1; Breaker slice values placeholders (Crit 12 / Atk 6 / Def 5).

### 2026-09-24 M0 Foundation
- SUPERSEDED Godot 4.3 pin by 4.7 (M1); GUT 9.4.0 by 9.7.1; `*.uid` sidecars committed.
- RULING 2026-09-24 fresh clone needs `godot --headless --path . --import` before `-s` tools; `-s` tools compile before autoloads, so the registry looks SignalBus up by node path.
- RULING 2026-09-24 ContentRegistry: ids from all `.tres/.res` incl. nested; duplicate different instances fail; sorted path order.
- RULING 2026-09-24 RngService stream seed = `hash([campaign_seed, stream_name])`; 64-bit values saved as decimal strings.
- RULING 2026-09-24 SaveService: top-level `"version"`, `migrate()` table; loaders `int()` JSON numbers.
- DEFAULT every GDD §11 number lives in `content/config/campaign_config.tres` (ranges as `Vector2i`).
- DEFAULT Heat thresholds (GDD 4.3): MINOR 10/20/30/40/60/70/80/90, MAJOR 25/50/75, PURGE 100; MAJOR modifiers 25 ELITE_FREQUENCY_PCT, 50 ENEMY_RESISTANCE +1, 75 RAID_STRENGTH_PCT +25; `event_raid` null until M3.
- DEFAULT ICE ladder (GDD 11.9): one change per level; levels 10, 15, 20 reserved with no modifier.
- DEFAULT input map (GDD 9.5): nudge_left Q, nudge_right E, cycle_target Tab, end_turn Space, rewind Z/Ctrl+Z, inspect right mouse; physical keycodes.
- DEFAULT display 1280×720, `canvas_items`, `keep`.

## Open questions for the designer
- OPEN CP-001 (2026-10-10): answered 2026-10-11 (1A 2A-never-×3 3A 4A); only the API key still open. Defaults in force A / A / B (reports only) / A (`docs/handoff/CHECKPOINT_PENDING.md`).
- OPEN B4 b perf (2026-10-06): HQ idle at City Grid look ~10 ms/frame vs 8 ms budget. Keep City Grid look and cut city cost at RAID band, or use RAID band at HQ idle? Designer. Default: City Grid look.
- OPEN B4 HQ to round 44 (2026-10-06): (1) drop minimap terminal and MAP KEY strip? (2) keep ON AIR on the HQ or title only? (3) CORE verb stays PATCH (UPGRADE needs a home-upgrade rule GDD lacks). Defaults: all kept as built.
- OPEN B2 combat composition (2026-10-06): lime target brackets kept outside aiming (alt: none); hub passive name tooltip-only (alt: chip); low Site close-ups frame small until per-fight backdrops; hub tiny name under 12 px floor, built as review asks.
- SUPERSEDED/ANSWERED B1b pencil audit (2026-10-06): all three pencil notes stay (art director); raid verdict slice goes to B3 (re-home `raid_result_banner` as CELL HOLDS sticker).
- ANSWERED parity fix route map (2026-10-06): ROUTE-04 stickers are focus stops, rows removed. OPEN ROUTE-01: hidden nodes show as small grey discs; keep or hide fully (round 37)? Default: grey discs.
- OPEN parity fix codex, stats, options (2026-10-06): (1) RESET TO DEFAULTS per open tab or all tabs (ask first)? (2) Codex page paper or terminal glass? Defaults: per tab; paper.
- OPEN HQRUN-02 (2026-10-05, held): should the HQ run become a multi-node netrun on the compound (length, node mix, Heat/death/banking per GDD 4.2)? Default: breach run, one node; page title "<CORPORATION>: HQ RUN" until G12.
- OPEN HQ redesign B raid setup at big text (2026-10-06): keep map following target at text ≥1.3, or move YOUR NETWORK under THREAT INTEL? RAID-05: keep no RAID SETUP title sticker? Defaults: as built.
- OPEN parity card aiming/combat HUD (2026-10-05): key hints tooltip-only on TURN strip; keep, or add small key caption under nudge pair?
- OPEN S-MAPVIEW (2026-10-05): (1) raid map shows only Cell network plus raid entry/crossed Sites; should HQ show every launchable Site? (2) netrun route lies on one link; should it follow several links (needs rule change)? (3) map-mode numbers (saturation 0.7, veil 0.22, bloom 0.45) to tune on sheet.
- OPEN parity combat backdrop (2026-10-05): (4) a Site shot cannot keep far HQ in frame; default Site large; per-fight backdrop slice would fix. Round 2 rulings: each Site fight frames its own lot, landmark only on its own Site, no inset; concept's low angle now (perf overage owed in ART-12/perf.md); raid and netrun views grey city on purpose. Finding: 3D city ViewportTexture reads ~4× darker in canvas shaders; proposed slice to measure and decode; designer to rule if Grid's darker look is intended.
- OPEN parity endings (2026-10-05): (1) CORP DOWN beat inside won dossier; (2) pink spray X became red grease pencil X; (3) won/abandoned network prints stay stand-ins. Defaults implemented.
- OPEN ART-12 12p Steam Deck run (owed): Deck tier measured on dev PC only; real run of `tools/visual_qa/perf_pack.tscn --tiers=1 --size=1280x800` owed; estimate ~10-12 ms.
- ANSWERED S-CARDFACE (2026-10-05): lower floor at rest plus bigger grown card built; flights to piles queued for animation pass; RECYCLE BIN confirmed.
- ANSWERED SLOTS-01/02 (2026-10-05): manila folders stay; DELETE is a sticker too.
- ANSWERED overlap defects RAID-08 by "Parity fix — raid". OPEN GRID-12: Meridian map shows 12-19% fog past city edge; default no zoom.
- OPEN parity raid (2026-10-05): (1) defence card 105 × 120 at 1.0, keep? (2) HONEYPOT card VAULT glyph in PINK, keep? (3) RAID-10 result call-out: pencil at DISPLAY step with leader, or red label sticker? Default unchanged. (4) playout opens on CORE at closest zoom; open with step framing instead?
- OPEN Parity NEWC (2026-10-05): (1) locked REBEL_CELL shown as CLASSIFIED fifth tile ("OPENS AT ICE 10 EVERYWHERE"); keep? (2) pickers start on game defaults (Solace, standard home server, Breaker); keep? Defaults implemented.
- OPEN ART-3 6w raid on city (2026-10-05): (1) raid widest zoom ortho 640 vs bible clamp 220-380; shrink network spread? (2) sockets float over roofs; keep?
- OPEN ART-8 8w keycard words: Exploit keycards have English words baked in; export a text-free card later for translation? Default: kept as made.
- OPEN ART-8 8w combat close-up framing: one ortho (140) and height (30 BU) for all HQs; Solace helix cut at top; per-corp framing a follow-up if wanted.
- OPEN asset parity card kinds (2026-10-05): violet "other" family drawn as SYSTEM (cyan); is a fourth face wanted?
- OPEN ART-12 12s skins (2026-10-05): (1) skins free in Options > Display, or Profile unlocks (UnlockKind.SKIN)? (2) set is v2 + cobalt + graphite; others or corp-kit skins? Default: free.
- ANSWERED ART-5 5c city motion: transit shows CLOSE-tier cars at netrun close-up below ortho 150 (ART-7 7w); reduce motion and `CityView3D.set_night_share` built in 5e.
- OPEN ART-5 5e city integration (2026-10-05): (1) Site landmarks: Solace `t1_c`, Halcyon `lose_the_case_file`, Orbital `o1_d` (`CityConfig.site_landmarks`); Meridian and Cell none. (2) x2 spread aimed into each territory vs smaller spread. (3) Grid always night. (4) DISPATCH's fist on Cell district in REBEL_CELL only. (5) Cell blackout reveal once per session. Defaults as built.
- OPEN ART-6 3A raid: "Remove to hand = click the node" (ART_BIBLE v2 §4.8) would change click behaviour on a claimed node in raid setup, and whether pad keeps separate target pick. Default: click picks target; Withdraw button or drag returns a defence.
