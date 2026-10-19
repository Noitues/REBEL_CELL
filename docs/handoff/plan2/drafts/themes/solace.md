<!-- THEMES draft via Message Batches, claude-sonnet-5-5, batch msgbatch_01Rzb4HxT5fiSKoNiHzd4i91, custom_id theme__solace; status ok; tokens in 21030 cache-write 33457 cache-read 0 out 11469; cost $0.120. DRAFT: designer picks. -->

# Solace: THE BLOOM

## 1. Rules

**One mechanic:** a virus front trails the operative. The player's real currency is delay, measured in whole route layers and combat turns, never in real time.

**Units.** Positions are layers: layer 0 is the start, and layer r is rung r in the HQ. `front_milli` and `layer_milli` are integers in thousandths of a layer, so there is no float drift. Gap = `layer_milli − front_milli`.

### Street netrun (LIGHT form)

1. At netrun start, `front_milli = −start_gap` and the operative is at layer 0. The state is DORMANT until the first node is entered, then CREEPING. Gap is the distance from the operative's layer to the front.
2. **Node entry.** Entering any node moves the operative to that layer and advances the front by `pace_node`.
3. **Combat turns.** When a combat ends, the front advances by `pace_turn` × the turns that fight took. The front is frozen during a fight, so the operative can never be caught mid-fight. Turns in the Server Rack and mini-boss fights count the same way.
4. **Caught.** If the gap is ≤ 0 after step 2 or step 3, the state is CAUGHT. This is an operative loss under Q24.1: the operative is lost with everything unbanked, the netrun is abandoned, the raid is unchanged, and the existing death consequences apply (10 + tier Heat). No new loss rules.
5. **State bands** by gap: CREEPING above `close_gap`; CLOSE up to `close_gap`; CATCHING up to `catch_gap`; CAUGHT at 0 or below.
6. **Antiviral dose.** This is the only counter. It pushes the front back by `dose_push`. It is sold at Mainframes and offered as a Terminal-event option, and the gap is clamped to `max_gap`.
7. **Rooms.** A node whose layer is ≤ floor(front) is INFECTED. This is display only, because the operative can't go back. Skipped branches behind the front count as INFECTED, including the same-layer node on the other branch.
8. **Tier order.** T1 starts with a wide gap and low pace. The pace table is by tier, so the Bloom teaches first and bites later. T1 netruns also grant `free_doses` doses at the start.

### HQ netrun (FULL form)

9. The same rules 1–5 run on the HQ ladder. The front is one number shared by both towers, so rung r on tower A and on tower B are infected at the same moment.
10. **ACROSS costs time.** Choosing ACROSS advances the front by `pace_cross` in addition to the node entry. This replaces the HQ draft's Co-pay, Referral, Audit and Quarantine tolls, which are retired under this theme. It is the toll that matters here, and its price is shown before commit.
11. **Ward rest.** The REST node (D4) in the HQ also calls `dose_push`. Rest therefore buys HP and delay, and costs a layer of pace.
12. **Exploit keys** change the pace:
    - **Intel:** reveals the exact gap after every candidate move for the whole ladder, not just within `read_horizon`.
    - **Virus ("open-source patch"):** `pace_node` and `pace_turn` are multiplied by `virus_pace_pct` (75 %).
    - **Breach:** no Bloom effect, so the theme stays one mechanic.
13. **Crown.** The caught check applies on entering the crown. The Genome Core fight is frozen like any fight, so the front never catches the player mid-boss. If the Genome Core draft wants an enrage cue, it uses R4 enrage and not the Bloom.
14. **Dropped from the HQ draft:** `tower_pressure`, which would double up on the porthole tint. The Waiting Room debts and the pink halo pips are also not part of this theme (see Q-DESIGNER).

### Raid (ONE hook)

15. A raid carries `infection_bp` (basis points, 0 to 10000) alongside its other state. It starts at `start_bp` for the current Heat band.
16. **Each resolution step**, after assets fire and threats damage nodes, infection rises by `bp_base + bp_per_threat × threats still alive`. A threat is alive until it is destroyed or reaches home. A threat on a node counts the same as one in transit.
17. **Infection never decreases** during a raid. Destroying threats only stops the rise.
18. **CITY LOST.** If `infection_bp` reaches 10000 at any step, the raid ends as CITY LOST. The city is infected, only Solace has the cure, and Solace wins: this is a campaign loss, ended through the same path as BREACHED with its own end text. Operatives are never killed in raids, so nothing happens to them.
19. A raid that runs out the 30 steps, or ends with every threat gone, ends normally (CELL HOLDS). Infection resets with the raid; nothing is carried to the next raid.
20. **Setup.** There is no clock in setup. Delay is a function of the placed defense, so the setup preview is exact.

## 2. State and save fields

| Field | Type | Lives in | Notes |
|---|---|---|---|
| `bloom.front_milli` | int | `scripts/state/run_state.gd` (new `BloomState` sub-object) | Negative at start |
| `bloom.layer_milli` | int | `BloomState` | Set from the current node's layer × 1000 |
| `bloom.doses_taken` | int | `BloomState` | Telemetry and a price ramp |
| `bloom.caught` | bool | `BloomState` | Latched on CAUGHT |
| `bloom.enabled` | bool | `BloomState` | False when the pace table gives 0, or on non-Solace corporations |
| `raid.infection_bp` | int | the raid state object under `scripts/state/` (the existing raid state) | Resets per raid |
| `raid.steps_to_lost` | int (derived, not saved) | raid preview | −1 if never |

**Derived, never saved:** `bloom_front` = `front_milli`/1000.0, `bloom_gap`, `bloom_state` (enum computed from the gap bands), `raid_infection_pct` = `infection_bp`/100.

**Determinism:** there is no randomness. Nothing uses an RngService stream, and the HQ draft's `hq_graph` stream is not touched.

**Save impact:** additive. A missing `BloomState` loads as `enabled = false`, so old saves and non-Solace corporations are unaffected. If N8 takes the save to version 3, fold these fields into that bump; otherwise no bump is needed. Raid state is saved wherever it is today. Mid-fight quit and resume keeps the front frozen, because the front only changes at fight end and node entry.

## 3. Preview

**Route choice (street and HQ).** Every available next node shows:

- A `FRONT -n.n` chip: the exact gap after entering that node. In the HQ, ACROSS adds its `pace_cross` to the chip before commit.
- For fight nodes, `FRONT -n.n → ?`: the exact gap on entry, and the combat-turn cost as `?`. A tooltip says `−0.1 per turn`.
- A `CAUGHT` warning if the gap after entering is ≤ 0, so the player never walks into a certain loss unaware.
- Shop and Terminal nodes show a dose option with its price and its resulting gap (exact).

**Fight result.** The result screen shows `FRONT -a → -b` after the fight.

**HUD.** A TIDE gauge shows the layers, the operative marker and the front. `bloom_state` drives the art. Under Intel (HQ), the whole ladder shows exact gaps.

**Raid setup.** The projected outcome per the existing rule (HOLDS / DOWN / TAKEN) is joined by:

- `POPULATION INFECTED nn%` at the projected end of the raid;
- `CITY LOST at step n` or `holds at nn%`;
- a rate chip `+n%/step` (known).

Everything is deterministic, so there is no `?` in the raid preview. If a future raid has random elements, they show as `?` per Q19.

## 4. Numbers (all placeholders)

| Number | Value | Config key |
|---|---|---|
| Start gap, street T1–T4 | 4000 / 3500 / 3000 / 2500 | `campaign_config.bloom_start_gap_milli_by_tier` |
| Start gap, HQ | 3000 | `campaign_config.bloom_hq_start_gap_milli` |
| Pace per node entered, street T1–T4 | 500 / 600 / 650 / 700 | `campaign_config.bloom_pace_node_milli_by_tier` |
| Pace per node, HQ | 700 | `campaign_config.bloom_hq_pace_node_milli` |
| Pace per combat turn | 100 | `campaign_config.bloom_pace_turn_milli` |
| ACROSS cost (HQ) | 500 | `campaign_config.bloom_pace_cross_milli` |
| Dose push | 1000 | `campaign_config.bloom_dose_push_milli` |
| Dose price (Cycles) | 15 | `campaign_config.bloom_dose_price` |
| Max gap | 5000 | `campaign_config.bloom_max_gap_milli` |
| Free doses at T1 start | 1 | `campaign_config.bloom_free_doses_t1` |
| CLOSE gap | 2000 | `campaign_config.bloom_close_gap_milli` |
| CATCHING gap | 1000 | `campaign_config.bloom_catch_gap_milli` |
| Virus pace multiplier | 75 % | `campaign_config.bloom_virus_pace_pct` |
| Raid start by Heat band (COOL..HUNTED, PURGE) | 0 / 500 / 1000 / 1500 / 2000 bp | `campaign_config.raid_infection_start_bp_by_band` |
| Raid base rise per step | 50 bp | `campaign_config.raid_infection_bp_base` |
| Raid rise per living threat per step | 100 bp | `campaign_config.raid_infection_bp_per_threat` |

**Arithmetic check (street, T3).**
- A node entry adds +1000 layer and +650 front, so the gap grows by 350.
- A 4-turn fight costs 400, so the net per fight node is about −50.
- An 8-turn elite costs 800, so the net is −450.
- With 6 fights, 1 elite and a shop at T3, the gap goes 3000 → about 1900, which stays CREEPING to CLOSE. Slow play (rests and long fights) reaches CATCHING.

**HQ.** Start gap 3000, with 9 fights, 2 elites and 2 ACROSS crossings, comes to about 1400 at the crown. That is CATCHING territory with no doses and no Virus. A Virus key restores about 700 of margin.

**Raid.** With 3 threats alive for 10 steps: 10 × (50 + 300) = 3500 bp, so 35 %. For a lingering threat to reach CITY LOST it takes about 28 steps with 1 threat plus extras, which matches the 30-step cap.

## 5. Tests to write

| Name | Tier | Asserts |
|---|---|---|
| `test_bloom_gap_after_node_entry` | fast | Gap changes by `layer_milli_step − pace_node` |
| `test_bloom_combat_turns_advance_front_at_fight_end` | fast | Front is frozen during a fight, and advances turns × `pace_turn` at the end |
| `test_bloom_caught_at_gap_zero` | fast | Gap ≤ 0 latches CAUGHT and routes to the Q24.1 loss flow |
| `test_bloom_never_catches_mid_fight` | fast | No CAUGHT between a fight's first and last turn |
| `test_bloom_state_bands` | fast | The gap-to-state mapping is exact at each boundary |
| `test_bloom_dose_push_and_clamp` | fast | Push adds `dose_push`, clamped to `max_gap` |
| `test_bloom_hq_across_cost_preview_equals_result` | fast | The ACROSS chip equals the real front change |
| `test_bloom_virus_scales_pace` | fast | The pace multiplier is applied once, without a rounding drift (rounded down, minimum 1) |
| `test_bloom_infected_rooms_both_towers` | fast | Rooms with layer ≤ floor(front) are INFECTED on both towers, including skipped branches |
| `test_bloom_save_roundtrip_midnetrun` | full | Save and load mid-netrun gives an identical `BloomState`; an old save loads DORMANT, disabled |
| `test_bloom_disabled_on_other_corporations` | fast | `enabled` is false for non-Solace corporations |
| `test_bloom_t1_free_dose_and_wide_gap` | fast | T1 starts with the gap and doses from config |
| `test_raid_infection_rises_per_step_and_threat` | fast | Per-step rise equals base + per-threat × living threats |
| `test_raid_infection_never_decreases` | fast | Monotonic across 30 steps |
| `test_raid_city_lost_ends_campaign` | full | 10000 bp ends the raid CITY LOST, the campaign as lost, with the Solace text |
| `test_raid_infection_preview_equals_result` | fast | The setup projection equals the played-out end value and loss step |
| `test_raid_infection_resets_per_raid` | fast | A new raid starts at its Heat-band value |
| `test_operatives_never_killed_in_raid_infection` | fast | CITY LOST changes no operative state |
| `test_bloom_config_has_no_magic_numbers` | fast | The Bloom code reads only the config keys above |

## 6. Art answers

### Names confirmed or renamed

| Art plan name | Decision | Type / values |
|---|---|---|
| `bloom_front` | Keep | Float derived from `front_milli`/1000, in route-layer units |
| `bloom_gap` | Keep | Float: operative layer minus front; at 0 or below, CAUGHT |
| `bloom_state` | Keep | DORMANT, CREEPING, CLOSE, CATCHING, CAUGHT, set by the gap bands (CLOSE at ≤ 2.0, CATCHING at ≤ 1.0) |
| `raid_infection_pct` | Keep | Int 0–100, derived from `infection_bp`/100 |
| `bloom_room_infected` (new, derived) | Add | Per node: layer ≤ floor(front) |
| `raid_infection_rate_pct` (new, derived) | Add | Chip value for `+n%/step` |
| `bloom_doses` (new) | Add | Dose count, optional gauge tick |

### Answers

1. **Advance:** by node entry and by combat turns, applied at fight end. Never real time.
2. **Layer or path:** a layer number, the same on both HQ towers.
3. **Thresholds:** CLOSE at gap ≤ 2.0 layers, CATCHING at gap ≤ 1.0, CAUGHT at 0 or below (config).
4. **Frost and Bloom:** the operative is always at or ahead of the front, and the read horizon (current rung + 2) is ahead of the operative. They never overlap in the same room. In the HQ overview they can appear at once, in separate regions: Bloom low, frost high.
5. **Skipped branches:** yes. A skipped branch and the other tower's same-layer room are INFECTED once layer ≤ floor(front).
6. **ACROSS:** yes. It costs `pace_cross` = 0.5 layer of front, so it changes the gap. The route preview shows it before commit.
7. **Raid rate:** yes, a rising value with a known rate. The art may show a `+n%/step` chip.
8. **Raid view:** it is the existing 2D raid / City Grid graph map (GDD 7, Grid view). The Grid median is for the art session to measure.
9. **`tower_pressure` and `debts`:** neither is part of this theme. Pressure is dropped. The HQ draft's tolls other than the front cost are retired, which frees the porthole tint for the Bloom. The debt pips are not needed.
10. **Lost raid:** CITY LOST ends the campaign as lost. There is no permanent Grid scar, so Part D stays minimal.
11. **CAUGHT and end text:** CAUGHT hands off to the existing operative-loss flow (Q24.1). The `CITY LOST` text is "THE CITY IS INFECTED. ONLY SOLACE HAS THE CURE."
12. **Tempo:** art can pick it. The gameplay values do not depend on loop timing. Audio follows the art.

## 7. Reuse and dependencies

| Item | Source | Notes |
|---|---|---|
| N2 tier tables | N2 | Per-tier arrays above |
| N18 data-driven rewards | N18 | The Antiviral dose as a shop and event row; fallback is a hard-coded shop slot |
| REST node (D4) | D4 | HQ Ward rest calls the dose push; fallback is a plain event |
| N16 | not needed | |
| Exploits (N5) | N5 | Intel and Virus modifiers are data fields on `ExploitData` |
| Raid resolver | existing | Add an accumulator to the step loop |
| Parasite ring, rim gates, enrage, resistance | not used | One mechanic per corporation |
| Heat | existing | Read only, for the raid start value |

**NEW code:**
- `BloomState` with node-entry and fight-end hooks in `netrun_session`;
- the caught check and its handoff to the loss flow;
- the route preview chips;
- the raid infection accumulator and the CITY LOST ending.

**Data-only fallback:** none for the front itself. It needs the state and the hooks.

## 8. Q-DESIGNER

Q-DESIGNER: Should the raid infection carry over between raids as a campaign figure (stakes build up), or reset per raid as I chose?
Q-DESIGNER: Does the Heat band also speed the street Bloom pace, or does Heat only affect raids?
Q-DESIGNER: Is a mini-boss or elite fight's turn cost at 0.1 layer per turn too punishing for the long fights the R1 design wants, or should boss and mini-boss fights be exempt?
Q-DESIGNER: Do you want the HQ Waiting Room debts kept, with a new visual channel, or cut with the pressure counter?
Q-DESIGNER: Should the T1 free dose stay, or should the first netrun teach the Bloom with no safety net?
Q-DESIGNER: Is Virus the right Exploit to slow the Bloom, or should Intel or Breach own it?
