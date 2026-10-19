<!-- THEMES2 draft via Message Batches, claude-sonnet-5-5, batch msgbatch_01BLNcf54zM6exqecvb8qLg7, custom_id themes2__meridian; status ok; tokens in 16274 cache-write 34418 cache-read 0 out 7510; cost $0.097. v2: designer answers 2026-10-19 applied. -->

# Meridian: MANIFEST (v2)

One identity: **freight in motion**. Everything is on the manifest. Cargo has weight, customs checks the manifest, every delivery has a window, and every Site is fed along a supply line. The four options are four faces of one object, the **manifest**, and they enter the game one at a time (§1.0).

## 0. What changed from v1
- **All four options merged (A, B, C, D):**
  - One theme, one entry order by tier (§1.0).
  - Each part lives in one layer: Window and Feed on the street, Payload and Customs in the HQ full form, Feed in the raid.
  - Parts interlock (§1.5).
  - Only one raid hook is kept (fed threats). v1's overcap, contraband hold and late-fee raid rules are dropped.
- **M1, the theme may cost power:**
  - Payload resistance on your own wheel and customs duty/surrender stay, with no softening.
  - The cap on Over resistance (3) is the only brake, and it is config.
- **M2, the faster-finish bonus is good:**
  - Express stays.
  - It also fuels customs (Cycles pay duty), so the bonus is load-bearing.
  - Bosses carry no Window, so long boss fights are untouched.
- **M3, surrendered items are lost permanently:**
  - v1 rule B5 (return next run) is deleted.
  - Surrender is a real sacrifice, and it also drops Load.
- **M4, the Grid clear order is a strategic choice:**
  - The Meridian tier chain is replaced by a "linked and cleared" unlock rule.
  - Feed makes the order matter.
- **Merging effects:**
  - Customs and Payload share one set of checkpoints (the HQ Weigh Stations are the Checkpoints).
  - The v1 Priority Meter is now fed by Express fights only.
  - The Customs Seal hub rule is merged into one (§1.4).
- **Code:** Meridian is not built, so there is no rework, only a new build. New code is (a) a player-wheel start resistance, (b) a CHECKPOINT node kind, (c) a feed derivation with a Grid overlay, (d) a Grid unlock rule per corporation.

## 1. Rules

### 1.0 Introduction order (the escalation)
`config: meridian.stage_by_tier[t]` gives the stage for a Site of tier t. A stage turns on its parts and keeps all earlier ones.

| Stage | Where | Parts live |
|---|---|---|
| 1 | T1 Sites | WINDOW (Express only, no Tariff) · FEED overlay on the Grid (feed cap 1) |
| 2 | T2 Sites | adds Tariff · PAYLOAD (capacity bonus +2) |
| 3 | T3 Sites | adds CUSTOMS: one Checkpoint, with declaration · feed cap 3 · capacity bonus +1 |
| 4 | T4 Sites and the HQ | all parts, full HQ form · capacity bonus 0 |

The player never meets more than one new system per tier.

### 1.1 Street (light form)
1. **Window.** Normal fights show a Window of 4 turns, elites 8, mini-bosses 10. The Window never changes combat, ends a fight, or applies to HQ bosses.
2. **Express.** Finishing in N turns or fewer gives +25 % Cycles from that fight.
3. **Tariff** (stage 2+). Finishing after turn N + 3 gives −10 % Cycles from that fight (bounded: the fight's Cycles are never below 0).
4. **Feed.** A Site's `feed` is the number of uncleared Meridian Sites linked to it of equal or higher tier, capped (1 at stage 1, 3 from stage 3).
5. **Feed effect.** Enemies in a fight at that Site start with +8 % × feed max HP and a shield of 5 % × feed of max HP (percent mode, N1, never rescaled).
6. **Cutting feeders.** Clearing a Site lowers the feed of every linked neighbor immediately (shown on the Grid overlay).
7. **Payload** (stage 2+). Load = Firmware ×1 + Daemons ×2 + unbanked Armory assets ×2. Capacity = 5 + Rank + the stage bonus. At combat start your wheel gets resistance = min(Over, 3). Player resistance follows the enemy lifecycle (zeroed at end of turn, regained at start, "+N" mark).
8. **Jettison.** Any Mainframe offers a free Jettison: drop an item and get 50 % of its Cycles value.
9. **Customs, Checkpoint** (stage 3+). The run map has exactly one Checkpoint at layer 4, replacing a Router and visible from the start. At it, the first **undeclared** item in acquisition order is flagged. You pay a 15-Cycle duty or surrender it. A surrendered item is **lost permanently**. If every item you hold is declared, the Checkpoint is a free pass.
10. **Declaration** (stage 3+). Before JACK IN you declare up to 3 Firmware/Daemons (+1 per 2 Ranks). A mid-run pickup is undeclared until you declare it at a Mainframe for 10 Cycles.

### 1.2 Grid order (M4)
11. **Meridian Sites unlock when any linked Site is cleared.** The tier chain no longer gates the order. Rank gates the tier of Site you may launch, as everywhere. `config: meridian.free_clear_order`.
12. The minimum winning path stays at least as long as today's (8 runs). The Grid builder must keep a connected path from every T1 Site to the boss.

### 1.3 HQ (full form)
13. The HQ route has 3 **Weigh-and-Inspect gates** (L3, L6, L9). Each is a Checkpoint (rule 9) that also weighs you: your Capacity drops by 2 for the rest of the run, and it inspects 1, 2, then 3 undeclared items.
14. A **Bonded Warehouse** node (L5) lets you re-declare up to 2 slots for free.
15. The route has 3 **Depot** nodes (the Intel, Breach and Virus buildings). Each is a fight. Winning one cuts one boss feed line: heal, shield, or second needle. It disables that boss mechanic for the final fight (the N5 Exploit counter).
16. Every HQ fight (not the boss) has a Window. Each Express fight adds 1 to the **Priority Meter** (0-5); each Tariff fight removes 1.
17. At the boss, Priority ≥ 3 gives +1 starting RAM, and Priority 5 gives +2 RAM and delays the boss enrage by 3 turns.
18. **Customs Seal hub** (the boss). Resistance = floor(Load ÷ 3) + 1 per item you passed through every Checkpoint declared. Planning raises the resistance; weight raises it too.

### 1.4 Raid (one hook)
19. A Meridian threat that spawns from a Site with feed ≥ 2 is **fed**: it moves +1 edge on its first step. The feed value is the one frozen when the raid starts.

### 1.5 How the parts interact
- **Feed vs Window:** a high feed means tougher enemies and a harder Express. Cutting feeders first makes both Express and Tariff easier. This is the M4 choice.
- **Express vs Customs:** Express Cycles pay duty. A greedy player keeps items and pays; a fast player affords more.
- **Payload vs Customs:** surrendering is the only way to shed Load, and a Jettison is the other.
- **Depot vs Priority:** a Depot fight is an Express chance, so cutting a line also pays into the meter.

## 2. State and save fields
- `RunState.capacity_bonus: int` (stored; HQ gate penalty applied here). Load, Over and Capacity are derived.
- `RunState.declared_ids: Array[StringName]`.
- `RunState.surrendered_ids: Array[StringName]` (log only, for the Codex and tests).
- `RunState.priority_meter: int` (0-5, HQ only).
- `RunState.cut_lines: Array[StringName]` (HQ).
- `CombatState.window_turns: int` (read from config at create); turns elapsed already exists.
- `CampaignState`: `site_feed` is derived on load from the Grid and cleared flags, not stored.
- `NodeData.kind = CHECKPOINT` (append-only).
- `RaidThreatState.fed: bool` (frozen at raid start).
- **Save impact:** one version bump (v+1); all new fields default empty/0. Old campaigns are dropped anyway (D3).
- **RNG:** none. "First undeclared" is acquisition order, and feed comes from the graph.

## 3. Preview
- A **WINDOW 3/4** chip beside the turn counter; it turns to TARIFF after N + 3. The reward panel shows "Express +25 %" and "Tariff −10 %" before the fight.
- A **LOAD 7/6** chip (amber when Over > 0). At combat start the player wheel shows its "+N" resistance. Jettison shows its refund.
- A Checkpoint on the map shows "Would flag: <item>" and the duty. The declaration screen marks each item declared/undeclared.
- The Grid overlay draws feed lines with number badges. The Site card reads "Feed 2: enemies +16 % HP, +10 % shield".
- Raid threats show a "fed" chip.
- Everything is exact. No "?" is shown anywhere (no stream is read).

## 4. Numbers (placeholders)
- `config: meridian.stage_by_tier` = [1, 2, 3, 4].
- `config: meridian.window_turns[class]` = normal 4, elite 8, mini-boss 10.
- `config: meridian.express_cycles_pct` = 25.
- `config: meridian.tariff_cycles_pct` = 10.
- `config: meridian.tariff_grace_turns` = 3.
- `config: meridian.weight_firmware` = 1.
- `config: meridian.weight_daemon` = 2.
- `config: meridian.weight_asset` = 2.
- `config: meridian.capacity_base` = 5.
- `config: meridian.capacity_per_rank` = 1.
- `config: meridian.capacity_stage_bonus[]` = [0, 2, 1, 0].
- `config: meridian.over_resistance_cap` = 3.
- `config: meridian.jettison_refund_pct` = 50.
- `config: meridian.declare_slots` = 3.
- `config: meridian.duty_cycles` = 15.
- `config: meridian.late_declare_cycles` = 10.
- `config: meridian.feed_cap_by_stage[]` = [1, 1, 3, 3].
- `config: meridian.feed_hp_pct` = 8.
- `config: meridian.feed_shield_pct` = 5.
- `config: meridian.station_capacity_penalty` = 2.
- `config: meridian.hq_gate_inspect_counts[]` = [1, 2, 3].
- `config: meridian.priority_ram_bonus[]` = [0, 1, 2] at Priority 0-2, 3-4, 5.
- `config: meridian.priority_enrage_delay` = 3.
- `config: meridian.hub_load_divisor` = 3.
- `config: meridian.raid_fed_edges` = 1.
- `config: meridian.raid_fed_min_feed` = 2.
- `config: meridian.free_clear_order` = true.

## 5. Tests to write
- `test_window_express_and_tariff_cycles` (fast): Express at ≤ N, no change at N+1..N+3, Tariff after.
- `test_window_never_alters_combat_result` (fast): identical outcome with the Window on or off.
- `test_boss_has_no_window` (fast).
- `test_feed_counts_uncleared_higher_tier_neighbors` (fast).
- `test_feed_drops_when_neighbor_cleared` (fast).
- `test_feed_hp_percent_applied_once` (fast): never rescaled (R2).
- `test_stage_gates_parts_by_tier` (fast): T1 has no Tariff, Payload or Checkpoint; T3 has the Checkpoint.
- `test_load_sums_item_weights` (fast).
- `test_over_capacity_sets_resistance_capped` (fast).
- `test_player_resistance_lifecycle` (fast).
- `test_jettison_refund_and_load_drop` (fast).
- `test_checkpoint_flags_first_undeclared` (fast).
- `test_duty_vs_surrender` (fast): surrender removes the item permanently and lowers Load.
- `test_surrendered_item_never_returns` (full): save, reload, next run.
- `test_late_declare_cost` (fast).
- `test_free_clear_order_unlocks_linked_site` (fast).
- `test_grid_keeps_path_to_boss` (full): every seed has a connected path from each T1 Site to the boss.
- `test_hq_gate_penalty_and_inspect_counts` (full).
- `test_depot_cuts_boss_line` (full).
- `test_priority_meter_effects_at_boss` (full).
- `test_seal_hub_resistance_formula` (fast).
- `test_raid_fed_threat_extra_edge` (full).
- `test_manifest_state_round_trips_in_save` (full).

## 6. Build slices
1. **Window and Express/Tariff** (S): the turn counter, reward modifier and WINDOW chip. Depends on the stage table and N18 (or the existing Cycles reward code).
2. **Stage table and config block** (S): `meridian.*` keys and `stage_by_tier`.
3. **Feed derivation and Grid overlay** (M): feed badges, the Site card text and the enemy start-HP/shield hookup (N1, N2). Depends on 2.
4. **Free clear order** (M): the unlock rule per corporation and the path-to-boss check. Depends on 3. NEW: Grid unlock rule.
5. **Payload: Load, Capacity, player start resistance, Jettison** (M): NEW: player-wheel start resistance (data-only fallback: none). Depends on 2.
6. **Customs: Checkpoint node, declaration screen, duty/surrender** (L): NEW: CHECKPOINT node kind and declaration UI. Fallback for the node: a two-choice Terminal event (N16). Depends on 5.
7. **HQ gates, Bonded Warehouse, Depots, Priority Meter, Seal hub** (L): depends on 1, 5, 6, N5.
8. **Raid fed hook** (S): depends on 3.
9. **Save version bump and migration** (S): in step with each slice.
10. **Art-pass owns the 3D look:** weigh-bridge platforms, customs arch, shipping labels, belt lines between Sites that go dark when cut, depot spurs.

## 7. Q-DESIGNER
Q-DESIGNER: Does the free Grid clear order (rule 11) apply to all Meridian tiers, or only from T2 up, with T1 Sites still opened by the chain? (all tiers, with Rank still gating the tier you may launch)
Q-DESIGNER: When you hold nothing undeclared at a Checkpoint, should it be a free pass or still cost a flat toll? (free pass, so declaring in advance is rewarded)
Q-DESIGNER: May the Over resistance (up to 3) land on a boss fight at full strength, since M1 allows power loss? (yes; its cap is already config)
Q-DESIGNER: Should Express/Tariff change Heat as well as Cycles? (no, Cycles only, to avoid a second economy)
Q-DESIGNER: Should a Depot fight count as a normal fight for the Window and the Priority Meter? (yes, it is the intended tie-in)
