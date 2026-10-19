<!-- THEMES draft via Message Batches, claude-sonnet-5-5, batch msgbatch_01Rzb4HxT5fiSKoNiHzd4i91, custom_id theme__rebel_cell; status ok; tokens in 25970 cache-write 0 cache-read 33457 out 13003; cost $0.094. DRAFT: designer picks. -->

# REBEL_CELL: THREE LINES, ONE CLOCK

Working names: lanes ROOF / STREET / SEWER; the finale is "Sync Strike"; the boss is `dispatch_core`.

**Reconciliation with Q34 (decided).** The three lanes are the route phase of the HQ run. Each lane is a full operative route. Its end-room fight is that operative's "small fight" from the Sync Strike direction. The Sync Strike is the finale: one combat in the Q34 view (three operative wheels orbiting the DISPATCH wheel). There is no separate mini-fight phase.

**Where the phases meet.**
- The route phase ends at the instant every living lane's switch is ARMED. This means each living operative has won its end-room fight.
- The player then confirms THROW, a single non-random action.
- The Sync Strike begins with the first turn of the `dispatch_core` combat.

**What carries across the THROW** (details in 1.4):
- each surviving operative's HP, deck, Firmware, Daemons and class;
- the shared Cycles pool;
- one lane effect per ARMED lane.

**What does not carry:**
- route position and node state;
- RAM (each operative starts the finale with its normal combat RAM);
- statuses;
- the lead limit.

## 1. Rules

### Street netruns (LIGHT form: the lane tag)

1. A street Site carries a `lane_tag` in {ROOF, STREET, SEWER}, assigned at Grid generation from the `grid` stream. It biases the netrun's node mix per `hq_lane_node_weights` (see §4). ROOF leans toward elites, SEWER toward events, STREET is neutral.
2. The tag changes only node-type weights. It adds no new rule, and the netrun still has one operative.
3. Capturing the final Rack of a street netrun adds its `lane_tag` to the campaign's `lanes_scouted` set.
4. In the HQ run, a lane whose tag is scouted gives its operative +`scout_ram` starting RAM in that lane's first fight.
5. Scouting also reveals that lane's end-room enemy on the plan view before launch. This is information only.

### HQ netrun (FULL form: three simultaneous lanes)

**1.1 Setup.**
1. The Grid's HQ launch screen requires `lanes_required` (3) operatives, one assigned per lane. Any class may take any lane; accent colors belong to lanes, not classes.
2. Each lane has its own route graph, `hq_lane_layers` (7) layers. Every layer has 2-3 nodes. The last layer is the end room, a single elite-strength fight that holds the lane's kill switch.
3. Each operative uses its own HP, RAM, deck, Firmware and Daemons. Cycles are one shared pool.
4. Lane graphs are built once at launch from the `map` stream and checkpointed. Nothing in the route phase uses randomness except ordinary combat streams.

**1.2 Route phase: one clock.**
5. The player may take any lane's next node at any time. Only one node resolves at a time. A fight is the normal combat, and other lanes wait.
6. **Step** = the lowest layer among living lanes. **Lead limit:** a lane may not enter a node more than `lead_limit` (2) layers above the lowest living lane's layer. The action is refused with the reason "AHEAD OF CLOCK: advance <lane>".
7. A lane with nothing left to take (waiting at the end room or ARMED) is excluded from the lowest-layer calculation.
8. `sync_state` is IN_STEP when all living, unARMED lanes are on the same layer. Otherwise it is OUT_OF_STEP. This is information only; it never penalizes.
9. Rest nodes heal that operative `rest_heal_pct` max HP. Shops and events behave as in a street run but spend the shared Cycles pool. Events are tagged to a lane.
10. A lane's end-room win sets that lane's switch to ARMED. The operative is parked at the switch (inactive, safe).

**1.3 Death (Q24.1).**
11. An operative at 0 HP, from any cause, is lost for good. Its lane becomes DARK (no further nodes, no switch, no lane effect). The run continues for the remaining lanes. Heat for the death follows GDD 4.2.
12. If all three lanes are DARK, the run fails (§1.5).

**1.4 THROW and the Sync Strike boundary.**
13. When every living lane is ARMED, the THROW button enables. It is a single deterministic action. Pressing it checkpoints the save.
14. On THROW:
    1. each surviving operative heals `throw_heal_pct` max HP;
    2. `seq` goes to 3 and `pulse` fires;
    3. each ARMED lane applies its `lane_effect` (see §4) to the `dispatch_core` combat as a start-of-fight modifier;
    4. the finale combat is created.
15. **Finale (Q34).**
    - Survivors form the operative set; DARK lanes are absent.
    - Within a turn the player moves focus freely between operative wheels.
    - SEND IT resolves the focused wheel, then the next in order (fixed order ROOF, STREET, SEWER), then the next. Focus then returns to the first living wheel.
    - Killed operatives are skipped and leave the focus set.
    - Operatives share no HP; each takes hits at its own wheel's pointers.
    - The boss's phases, buffs and enrage belong to the DISPATCH boss pass; this theme only supplies the start modifiers.
16. Win = campaign win per GDD 1.3. The HQ run ends.

**1.5 Failure.**
17. Run fails when all operatives are lost (route or finale). Survivors at that point do not exist by definition. The HQ netrun stays available; a new launch needs new operatives and a fresh seeded graph.
18. Abandon run kills every operative on it (GDD 4.5).

### Raid (ONE hook: converging arrival)

19. A REBEL_CELL raid always has 3 first-wave threats. Their start steps are delayed so all three would reach the target node on the same step: start delay = the longest path length among the three minus the threat's own path length.
20. Raids never kill operatives (Q24.1). All other raid rules are unchanged.

## 2. State and save fields

| Field | Type | Lives in | Notes |
|---|---|---|---|
| `lane_tag` | StringName | `SiteState` (scripts/state/) | Grid generation, `grid` stream; default `&"STREET"` on load |
| `lanes_scouted` | Array[StringName] | `CampaignState` | default [] |
| `hq_strike` | `HqStrikeState` (new object) | `RunState` | null outside HQ runs |
| `HqStrikeState.lanes` | Array[3] of `{lane_id, operative_id, layer, node_id, status}` | in `hq_strike` | status in ALIVE, ARMED, DARK |
| `HqStrikeState.graphs` | Array[3] of map graphs | in `hq_strike` | built at launch |
| `HqStrikeState.phase` | enum ROUTE, THROWN, FINALE | in `hq_strike` | |
| `HqStrikeState.focus_lane` | int | in `hq_strike` | finale only |
| `raid_arrival_step` | int | raid state | derived; saved so the preview survives reload |

- **Derived, never saved:** `step`, `sync_state`, `seq`.
- **Save:** additive fields with defaults, so the save version bumps by 1 with a trivial migration (old saves are dropped anyway per D3).
- **RNG:** lane graphs use the `map` stream, checkpointed; `lane_tag` uses `grid`; there is no other randomness.

## 3. Preview

- **Plan view (DISPATCH view):**
  - three lane graphs, each node's type, and the step ruler;
  - for each lane: layer, HP and RAM gauges, status;
  - scouted lanes show the end-room enemy.
- **Hover a refused node:** the reason "AHEAD OF CLOCK" plus the lane that must advance. This is exact.
- **Fight outcomes** in the route are "?" until fought; they follow the normal combat preview.
- **THROW preview:**
  - the survivors list;
  - each operative's HP after `throw_heal_pct`;
  - the lane effects that will apply;
  - the DARK lanes whose effects are lost.
  
  All of this is exact, with no "?" parts.
- **Finale:** the Q34 preview. The focused wheel's result is exact; the other wheels show their known results. A random respin shows "?" per Q19.
- **Raid:** each threat's arrival step and its start delay, exact.

## 4. Numbers (placeholders)

| Value | Placeholder | config |
|---|---|---|
| `lanes_required` | 3 | `campaign_config.hq_lanes_required` |
| `hq_lane_layers` | 7 | `campaign_config.hq_lane_layers` |
| `lead_limit` | 2 | `campaign_config.hq_lead_limit` |
| `rest_heal_pct` | 30 | `campaign_config.hq_rest_heal_pct` |
| `throw_heal_pct` | 20 | `campaign_config.hq_throw_heal_pct` |
| `scout_ram` | 2 | `campaign_config.lane_scout_ram` |
| seq thresholds: seq 1 at step ≥ | 3 | `campaign_config.hq_seq_steps` |
| seq 2 at step ≥ | 5 | `campaign_config.hq_seq_steps` |
| Lane node weights (elite / event / shop) | ROOF 30/15/10, STREET 20/25/15, SEWER 15/40/15 | `campaign_config.hq_lane_node_weights` |
| Street tag tilt (same rows, scaled) | 50 % of the HQ tilt | `campaign_config.street_lane_tilt_pct` |
| Lane effects on `dispatch_core` | ROOF: enemy resistance −2 (min 0); STREET: first-phase hub heal off; SEWER: each operative +2 RAM at fight start | `campaign_config.hq_lane_effects` |
| Raid first-wave threat count | 3 | `raid_config.rebel_first_wave` |

## 5. Tests to write

| Test | Tier | Asserts |
|---|---|---|
| `test_lane_tag_biases_node_weights` | fast | the tag changes weights only; the same seed gives the same graph |
| `test_lanes_scouted_set_on_rack_capture` | fast | the tag is added once, never duplicated |
| `test_hq_launch_requires_three_operatives` | fast | fewer than `lanes_required` is refused with a reason |
| `test_lane_graphs_checkpointed_deterministic` | fast | same seed gives the same three graphs; reload does not reroll |
| `test_lead_limit_refuses_third_layer_ahead` | fast | the refusal and its text; a parked or DARK lane is excluded from the minimum |
| `test_sync_state_in_vs_out_of_step` | fast | derived values for a table of lane layers |
| `test_end_room_win_arms_switch` | fast | the status becomes ARMED and the operative is parked |
| `test_operative_death_darkens_lane_run_continues` | fast | DARK status and Heat per GDD 4.2; the other lanes keep playing |
| `test_all_lanes_dark_fails_run_keeps_hq_open` | fast | the run fails; the HQ netrun stays launchable |
| `test_throw_requires_all_living_armed` | fast | THROW is disabled until the last ARMED |
| `test_throw_heals_and_applies_lane_effects` | fast | heal pct, one effect per ARMED lane, none for DARK |
| `test_throw_checkpoint_roundtrip` | full | save at THROW, reload, and the same finale state results |
| `test_finale_focus_order_skips_dead` | full | Q34 order and skipping |
| `test_abandon_kills_all_operatives` | fast | GDD 4.5 applied to all three |
| `test_raid_converging_arrival` | fast | three threats share one arrival step; delay arithmetic |
| `test_raid_never_kills_operatives` | fast | Q24.1 |
| `test_seq_mapping_from_step` | fast | 0/1/2 by step, 3 at THROW |
| `test_hq_save_load_roundtrip` | full | `hq_strike` survives a mid-route reload |

## 6. Art answers

**Q1.** Sync Strike is the HQ rule, and the theme in street netruns is the lane tag only. Three operatives run, and the HQ launch requires exactly three. Street netruns show no operative tokens.

**Q2.** "DISPATCH view" is the plan view's final name. The boss id is `dispatch_core`; the display name is the boss pass's call and is low priority.

**Q3.** Lane R is the approved service tunnel with the Undercroft. SEWER is only the gameplay and glyph name. Use B14(a).

**Q4.** Step = the lowest living lane's layer. There is no real time anywhere. The beat is cosmetic and need not sync to a game event.
- `seq`: 0 below step 3, 1 from step 3, 2 from step 5, 3 on THROW.
- `pulse`: a short envelope when a lane is ARMED, a full one on THROW.
- `lane_pos[3]`: the lane's layer and node.
- `switch_state[3]`: NOT_ARMED / ARMED / THROWN / DARK.
- `sync_state`: IN_STEP / OUT_OF_STEP.

**Q5.**
- **Out:** STALL, COUNTERED, detour cost, parked support, lone throw. Draw no hooks for them.
- **In:** operative death (LANE DARK).
- **Gauges:** HP and RAM are per operative (three gauge slots). Cycles are shared.

**Q6.** The street netrun passes `room_active`, `node_cleared`, tier, Heat and `lane_tag`. The light form changes only with `lane_tag` (which pattern leads) and with room_active (QUIET / ENGAGED) and node_cleared (CLEARED). It does not change with Heat or tier.

**Q7.** The theme adds no landmark in street netruns. The 9.4× MAINFRAME exception applies in the HQ netrun, but I rule nothing on the DISPATCH view, so the art keeps its own rule there.

**Q8.** REBEL_CELL raids exist (Heat thresholds and story). The raid states are the existing planning, playout and outcome phases:

| Art state | Game |
|---|---|
| WARNING | threats revealed, setup |
| INCOMING | playout, steps before the arrival step |
| ACTIVE | threats on the target node |
| REPELLED | CELL HOLDS |
| BREACHED | node DOWN or TAKEN |

The gauge `arrival` = current step ÷ `raid_arrival_step` (0-1). There are three threats but one outcome. Traces originate from the raid's source Site.

**Q9.** Grid HQ states:
- HIDDEN before the first Exploit;
- LOCATED with 1-2 Exploits;
- OPEN at `min_exploits_for_breach` or more.

Selecting the HQ opens the DISPATCH view as the pre-launch screen. There is no layer toggle. I rule no median luma for the Grid or raid map.

**Q10.** Entry is from the Grid (pre-launch, interactive: assign operatives to lanes) and mid-run via the D6 zoom (read-only plus lane or node selection).

**Q11.** Pink, cyan and green are **lane** accents (ROOF pink, STREET cyan, SEWER green), not class accents. The art plan's BREAKER / GHOST / RIGGER names for the lanes are renamed: tokens show the class glyph inside a lane-colored frame. The route colors are untouched by this theme.

**Q12.** There is no reduce-motion setting in the spec. Propose: loops pause on a still frame. This is outside this theme.

**Q13.** The HQ netrun's seq follows Q4's mapping (0 to 3), not a fixed 2. The DISPATCH view takes the same seq. The 0.14 target for the DISPATCH view is the art session's call.

**State-name table (art plan → build):**

| Art plan name | Build name | Status |
|---|---|---|
| `seq` | `seq` | confirmed, derived |
| `pulse` | `pulse` | confirmed |
| `lane_pos[3]` | `lane_layer[3]`, `lane_node[3]` | renamed |
| `lane_nodes[3][layer]` | `lane_graphs` | renamed |
| `countered_room` | none | dropped |
| `sign_target` | fixed DISPATCH lot | no state |
| `step` | `step` | confirmed, derived |
| `stall_tokens` | none | dropped |
| `sync_state` | `sync_state` (IN_STEP / OUT_OF_STEP) | confirmed |
| `relay_events[]` | none | dropped |
| `switch_state[3]` | `switch_state[3]` (NOT_ARMED / ARMED / THROWN / DARK) | renamed values |
| `parked[3]` | `focus_lane`, `orbit_order` (finale) | renamed |
| `dark_lane[3]` | folded into `switch_state` DARK | merged |
| `camera_beat` | camera, not game state | unchanged |
| intel / breach / virus flags | none | dropped (D5 buildings belong to the Exploit pass) |

## 7. Reuse and dependencies

- **Reuses:**
  - the existing `map_graph` generator (one call per lane);
  - the normal combat for lane fights;
  - N3 phases and N4 enrage for the elite end rooms and the boss;
  - the `lanes_scouted` set (data only);
  - the raid threat start-delay field (data only).
- **Depends on:**
  - the Sync Strike combat (Q34), which comes from the DISPATCH boss pass; the boss fight is built on N3 and N6;
  - N5 for boss buffs and Exploits, passed into the run state;
  - N18 for reward rows if the HQ win drops anything.
- **NEW code:**
  1. **NEW: multi-operative netrun session.** It holds three operative states and routes input to the current lane. This is the largest item. Reduced fallback: one operative walking all three lanes in sequence, which loses simultaneity but keeps the lead limit.
  2. **NEW: HqStrikeState** (plain state) and the lead-limit validator.
  3. **NEW: multi-operative finale view** (three wheels orbiting). It is the Q34 view and is covered by the boss pass.
- **Dropped from the earlier HQ draft:** relay, Counter, STALL, Hack puzzle, per-Exploit lane effects, parked-support passives. They are mechanics beyond the stated direction. Anything the designer wants back goes through a new ruling.

## 8. Q-DESIGNER

Q-DESIGNER: Should the HQ run require exactly three operatives (my default, behind config), or may a smaller crew run fewer lanes?
Q-DESIGNER: When one operative dies in the route phase, should the whole run be abandoned (a strict reading of Q24.1), or do the other lanes continue (my default)?
Q-DESIGNER: Should the lead limit be 2 layers (my default) or tighter or looser?
Q-DESIGNER: Should lane effects on `dispatch_core` be the three proposed starts, or should an ARMED lane instead carry nothing into the finale?
Q-DESIGNER: Should an operative's route HP carry into the finale with only a 20 % heal, or should the THROW fully heal everyone?
