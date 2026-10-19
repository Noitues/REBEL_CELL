<!-- THEMES draft via Message Batches, claude-sonnet-5-5, batch msgbatch_01Rzb4HxT5fiSKoNiHzd4i91, custom_id theme__meridian; status ok; tokens in 15371 cache-write 0 cache-read 33457 out 9729; cost $0.067. DRAFT: designer picks. -->

# Meridian: theme options (status: options)

Four distinct themes, each on a different axis, so the choice is real:

| Option | Axis | One-line pitch |
|---|---|---|
| A. PAYLOAD | what you carry | Everything you pick up has weight. Overload makes your own wheel heavy. |
| B. CUSTOMS | what you declare | Declare your gear at the border or have it seized at the gate. |
| C. DELIVERY WINDOW | tempo | Every fight is a parcel with a delivery deadline. Early pays, late is taxed. |
| D. SUPPLY LINE | geography | Meridian Sites feed each other. Cut the chain and the boss starves. |

All numbers are placeholders. None of the options uses randomness at play time.

---

## Option A: PAYLOAD

Pitch: loot has weight, and WEIGHT (Meridian's spin resistance) is turned on you.

Cost: small new code (a Load counter, plus player-wheel resistance if WheelState does not already allow it). Everything else is data.

Risk: it may read as an inventory tax on top of Heat. The "drop items" decision could feel like punishment for good play.

### 1. Rules
**Street (light)**
1. Load = Σ item weights: Firmware 1, Daemon 2, unbanked Armory asset 2. `config: meridian.weight_firmware / weight_daemon / weight_asset`.
2. Capacity = 5 + Rank. `config: meridian.capacity_base`, `meridian.capacity_per_rank`.
3. Over = max(0, Load − Capacity). At combat start your wheel gets resistance = min(Over, 3). `config: meridian.over_resistance_cap`.
4. Player resistance behaves like enemy resistance: it is zeroed at end of turn and regained at start of turn, and shows as "+N" (Q16 / Q31 lifecycle).
5. Mainframes and Terminals offer a free **Jettison**: drop an item and get 50 % of its Cycles value. `config: meridian.jettison_refund_pct`.

**HQ (full)**
6. Three Weigh Stations (L4, L7, L10 of the HQ route). Each lowers Capacity by 2 for the rest of the run.
7. At each station you may Jettison for free (rule 5 still applies).
8. The boss hub, the Customs Seal, gains resistance equal to your Load ÷ 3 (rounded down). Drop weight and the boss is easier to move.

**Raid (one hook)**
9. A defense node holds `node_capacity` = 2 assets. Each asset beyond that fires one step later. `config: meridian.raid_node_capacity`.

### 2. State and save
- `RunState.load: int` (derived, not stored, from the item lists) and `RunState.capacity_bonus: int` (stored; the HQ station penalty is applied here).
- `WheelState.resistance` is reused for the player wheel. Add `CombatantState.start_resistance_from_load` as a combat-start hook.
- `NodeState.raid_assets_overcap` is derived in the raid code.
- Save: +1 int field in RunState, a minor save-version bump (v+1, default 0). No RNG.

### 3. Preview
- A Load chip reads `LOAD 7/6`, turning amber when Over > 0.
- At combat start the player wheel shows "+1" resistance.
- Jettison shows the refund exactly.
- Weigh Stations show the new capacity before you enter.
- The raid overcap marker is drawn on the asset (the "fires late" step is already in the exact projection).

### 4. Numbers
- Weights 1 / 2 / 2; capacity 5 + Rank; Over cap 3; station penalty 2 (`config: meridian.station_capacity_penalty`); boss hub divisor 3 (`config: meridian.hub_load_divisor`); refund 50 %.
- Intro order: Capacity is generous at T1 (+2 `config: meridian.capacity_tier_bonus[t]`, tapering to 0 at T4).

### 5. Tests
- `test_load_sums_item_weights` (fast): the weight table gives the expected Load.
- `test_over_capacity_sets_resistance_capped` (fast): Over 5 → resistance 3.
- `test_player_resistance_refreshes_and_zeroes` (fast): follows the Q31 lifecycle.
- `test_jettison_refund_and_load_drop` (fast).
- `test_weigh_station_penalty_persists_in_save` (full): save and reload keeps `capacity_bonus`.
- `test_raid_overcap_fires_one_step_late` (full): the exact raid projection.

### 6. Art answers
No art plan exists. State names for the art session:
- `load`, `capacity`, `over` (ints), `weigh_station_state` {pending, passed}, `jettison_available` (bool).
- On the wheel: `player_resistance` (int).
- On raid nodes: `asset_overcap_count` (int).
- Visual cues: a weigh-bridge platform under the weigh node, a load gauge at the HUD edge, and container stacking on the operative portrait.

### 7. Reuse and dependencies
- Reuses N21 (resistance refresh and the "+N" mark) and the N16 map edits for stations.
- NEW: player-side resistance wiring if the WheelState field is enemy-only. This is data-only otherwise.
- No dependency on N10, rim gates or enrage.

---

## Option B: CUSTOMS

Pitch: at the start of every netrun you declare what you are carrying. Anything undeclared is contraband and gets seized at a checkpoint.

Cost: medium. It needs a pre-run declaration UI and a checkpoint node type, and the HQ form needs more. The rest is reuse.

Risk: a declare-or-lose-your-build choice before the run may feel unfair (hidden-information fear). It also fights the "no punishing shortcuts" ruling unless seizure is gentle.

### 1. Rules
**Street (light)**
1. Before JACK IN you declare up to `meridian.declare_slots` = 3 Firmware or Daemons. Declared items are safe.
2. Each netrun has exactly one **Checkpoint** node at layer 4 (replacing a Router). It is visible on the map from the start.
3. At the Checkpoint, the first **undeclared** item (in acquisition order) is flagged. You choose: pay a duty of 15 Cycles, or surrender it. `config: meridian.duty_cycles`.
4. You can still declare an item you pick up mid-run at any Mainframe for 10 Cycles. `config: meridian.late_declare_cycles`.
5. A surrendered item is returned at run completion (it goes into the Armory shop of the next run), never lost forever.

**HQ (full)**
6. Three Checkpoints (L3, L6, L9), each inspecting one more item: 1, 2, 3 in total per pass.
7. The HQ also has a **Bonded Warehouse** node where you may re-declare slots (swap up to 2).
8. The boss hub, the Customs Seal, gains one resistance per item you carried through all checkpoints declared (a reward for planning).

**Raid (one hook)**
9. Meridian threats arrive with a declared cargo. The raid setup shows "Contraband: yes/no". A node with an ICE Lock inspects, and holds the threat for 2 extra steps if contraband. `config: meridian.raid_inspect_hold`.

### 2. State and save
- `RunState.declared_ids: Array[StringName]`, `RunState.seized_ids: Array[StringName]`.
- `NodeData.kind = CHECKPOINT` (extends the node-kind enum; append-only).
- `RaidThreatState.contraband: bool`.
- Save: three new arrays/bools, one version bump. Deterministic: the "first undeclared" is acquisition order, no RNG.

### 3. Preview
- The Checkpoint node shows: "Would flag: <item>" (the exact item, since order is known).
- The declare screen shows each item's state: declared / undeclared.
- A raid threat chip shows a contraband flag.
- Nothing is random, so there is no "?".

### 4. Numbers
- Declare slots 3 (+1 per 2 Ranks); duty 15; late declare 10; HQ checkpoints 3; inspect hold 2.
- Intro order: T1 has no Checkpoint. T2 introduces it, T3 and T4 add the Warehouse.

### 5. Tests
- `test_checkpoint_flags_first_undeclared` (fast).
- `test_duty_vs_surrender_outcomes` (fast).
- `test_surrendered_item_returns_next_run` (full).
- `test_late_declare_cost` (fast).
- `test_hq_checkpoints_inspect_increasing_counts` (full).
- `test_raid_contraband_hold_steps` (full).
- `test_declaration_round_trips_in_save` (full).

### 6. Art answers
State names for the art session:
- `declared_ids` (list), `checkpoint_state` {upcoming, inspecting, cleared}, `flagged_item_id`, `bonded_warehouse_open` (bool).
- On raids: `threat.contraband` (bool), and a hold marker on ICE Lock nodes.
- Visual cues: a customs gate with a scanner arch, stamped "DECLARED" on item cards, and a conveyor scanner passing items.

### 7. Reuse and dependencies
- Reuses N16 (map edits for the Checkpoint), the existing ICE Lock asset, and the Customs Seal hub identity.
- NEW: the declaration screen and `CHECKPOINT` node kind. No data-only fallback for the declaration UI; a Terminal-event fallback exists for the Checkpoint (two-choice event).

---

## Option C: DELIVERY WINDOW

Pitch: every fight is a parcel with a delivery window. Finish inside it for a bonus; run late and pay a tariff.

Cost: smallest. It adds a per-fight turn threshold, a reward modifier and an enemy enrage reuse. It is mostly data.

Risk: it pushes players to burst down enemies, which cuts against the ruling that boss fights are the longest fights ("do not shorten phases"). It must stay a soft bonus.

### 1. Rules
**Street (light)**
1. Each normal and elite fight shows a **Window** of N turns, N = the class target (normal 4, elite 8). `config: meridian.window_turns[class]`.
2. Finish in N turns or fewer: +25 % Cycles (**Express**). `config: meridian.express_cycles_pct`.
3. Finish later: no penalty up to N + 3; beyond that, −10 % Cycles (**Tariff**). `config: meridian.tariff_cycles_pct`.
4. The window never changes enemy behavior and never ends a fight.

**HQ (full)**
5. Each HQ fight also has a Window. Express fights fill a **Priority Meter** (0-5).
6. Priority Meter ≥ 3 at the boss gives the player +1 starting RAM; at 5 gives +2 RAM and the boss starts with enrage delayed by 3 turns. `config: meridian.priority_ram_bonus[]`.
7. A Tariff fight resets the meter by 1.

**Raid (one hook)**
8. A raid has a **Delivery Window** of 12 steps. Threats still on a node after step 12 deal +25 % damage ("late fee") until the raid ends (30-step cap unchanged). `config: meridian.raid_window_steps`, `meridian.raid_late_damage_pct`.

### 2. State and save
- `CombatState.window_turns: int` (read from config at create).
- `RunState.priority_meter: int` (0-5).
- `RaidState.window_steps: int` (derived from config).
- Save: one int in RunState, a minor bump. No RNG.

### 3. Preview
- A **WINDOW 3/4** chip beside the turn counter; it flips to "TARIFF" at N + 4.
- Rewards show "Express: +25 %" before the fight starts.
- The raid projection already shows the final state, so the late fee shows exactly.

### 4. Numbers
- Windows: normal 4, elite 8, mini-boss 10. Express 25 %; tariff 10 %; grace 3 turns (`config: meridian.tariff_grace_turns`).
- Priority meter max 5; RAM bonus 1 at 3, 2 at 5; raid window 12 steps; late fee 25 %.
- Intro: the Window starts at T2 (T1 has no tariff).

### 5. Tests
- `test_express_bonus_when_within_window` (fast).
- `test_tariff_only_after_grace` (fast).
- `test_priority_meter_increments_and_resets` (fast).
- `test_boss_start_ram_from_meter` (full).
- `test_window_never_alters_combat_result` (fast): the same seeds give identical outcomes with the Window on or off.
- `test_raid_late_fee_after_window` (full).

### 6. Art answers
State names for the art session:
- `window_turns`, `turns_elapsed`, `window_state` {inside, grace, tariff}, `priority_meter` (0-5).
- Raid: `raid_window_step`, `late_fee_active` (bool).
- Visual cues: a shipping label with a stamped "EXPRESS" or "LATE", a parcel clock on the HUD, and a priority tag on the boss entry.

### 7. Reuse and dependencies
- Reuses N4 enrage (the delayed enrage at 5 priority) and N18 (reward rows, via a modifier).
- NEW: none beyond a counter. Fully data plus tiny HUD code.

---

## Option D: SUPPLY LINE

Pitch: Meridian Sites feed each other along the Grid. Cut the chain at a Site and every enemy fed through it gets weaker, all the way up to the boss.

Cost: largest. It needs a campaign-level supply graph, per-Site state and the HQ depots. The Grid graph already exists, so the reuse is high but the integration is wide.

Risk: it overlaps the campaign map's Site-ordering logic (tier chains) and could confuse the clear order. It needs a clear map overlay.

### 1. Rules
**Street (light)**
1. Every Meridian Site has a `feed` value = the number of uncleared Meridian Sites linked to it that are of equal or higher tier ("feeders"), capped at 3. `config: meridian.feed_cap`.
2. The fight's enemies start with +`feed` × 8 % HP (percent mode, N1) and `feed` × 1 starting shield percent of 5 %. `config: meridian.feed_hp_pct`, `meridian.feed_shield_pct`.
3. Clearing a Site removes it as a feeder for its neighbors (cut). It shows on the Grid right away.

**HQ (full)**
4. The HQ route contains three **Depot** nodes (Intel, Breach, Virus buildings). Each one visited cuts one of the boss's feed lines.
5. Boss feed lines: heal, shield, second needle. A cut disables that boss mechanic for the fight (this is the existing boss Exploit buff counter, N5).
6. Visiting a Depot costs one fight (it is a fight-or-puzzle node).

**Raid (one hook)**
7. A Meridian threat that spawns from a Site with feed ≥ 2 moves +1 edge on its first step ("fed"). `config: meridian.raid_fed_edges`.

### 2. State and save
- `CampaignState.site_feed: Dictionary[site_id → int]` (derived on load, cached; stored only for cleared flags already saved).
- `RunState.cut_lines: Array[StringName]` (HQ).
- `RaidThreatState.fed: bool`.
- Save: one array, one bump. Deterministic: derived from the Grid graph.

### 3. Preview
- The Grid overlay draws feed lines between Sites with a number badge.
- Selecting a Site shows "Feed 2: enemies +16 % HP, +10 % shield".
- Raid threats show a "fed" chip.
- No random elements.

### 4. Numbers
- Feed cap 3; HP +8 % per feed; shield +5 % per feed; three boss lines; raid extra edge 1.
- Intro: feed is capped at 1 at T1 and T2 (`config: meridian.feed_cap_by_tier[]`), full at T3 and T4.

### 5. Tests
- `test_feed_counts_uncleared_higher_tier_neighbors` (fast).
- `test_feed_drops_when_neighbor_cleared` (fast).
- `test_feed_hp_percent_applied_once` (fast): never rescaled (R2).
- `test_depot_cuts_boss_line` (full).
- `test_raid_fed_threat_extra_edge` (full).
- `test_feed_derived_after_load_matches` (full).

### 6. Art answers
State names for the art session:
- `site_feed` (int per Site), `feed_edges` (list of {from, to, active}), `cut_lines` (list).
- On HQ: `depot_state` {intact, cut} per building.
- On raids: `threat.fed` (bool).
- Visual cues: a belt line between Sites that goes dark when cut, and a conveyor spur from the boss to each depot.

### 7. Reuse and dependencies
- Reuses N1 (percent amounts), N5 (boss buffs and Exploit counters, mapped to depots), N16 (map edits) and the Grid graph.
- NEW: the feed derivation function and the Grid overlay (no pure data fallback; an authored per-Site feed value is a partial one).

---

## 8. Q-DESIGNER (shared)
Q-DESIGNER: Which option do you want, or which two should I merge (for example A for street plus D for the raid hook)?
Q-DESIGNER: Should the theme be allowed to cost the player power (A, B) or only reward good play (C), given your "games should be fun, not always punishing" ruling?
Q-DESIGNER: For option C, is a faster-finish bonus acceptable next to your "do not shorten phases" ruling, or should the Window only apply to normal fights?
Q-DESIGNER: For option B, should a surrendered item return after the run (proposed) or be lost?
Q-DESIGNER: For option D, may the Grid clear order become a strategic choice (cut feeders first), or must the existing tier chain stay the only order?

## Ranked recommendation (advice only)
1. **A, PAYLOAD.** It is the cheapest option that plays on the corporation's identity (WEIGHT), and it is readable at a glance. It also matches the Q16 intent that per-turn manipulation choices matter.
2. **D, SUPPLY LINE.** It has the strongest identity and a natural fit for the boss's Exploit buffs, but the cost and Grid-overlay work are the largest. Pick it if you want Meridian to change how the campaign is played.
3. **B, CUSTOMS.** It is distinctive and thematic, but it risks pre-run friction and a punishing feel.
4. **C, DELIVERY WINDOW.** It is the lightest and safest, but the weakest as an identity, and it leans against the long-boss-fight ruling.
