<!-- THEMES2 draft via Message Batches, claude-sonnet-5-5, batch msgbatch_01BLNcf54zM6exqecvb8qLg7, custom_id themes2__solace; status ok; tokens in 16104 cache-write 0 cache-read 34418 out 6176; cost $0.050. v2: designer answers 2026-10-19 applied. -->

# Solace: THE BLOOM (v2)

## 0. What changed from v1

- **S1 (raid infection is a campaign figure that may diminish to zero):** the per-raid `infection_bp` that reset each raid (v1 rules 15–19) is replaced by a persistent `campaign.infection_bp`. It decays after a raid that CELL HOLDS, and by Heat-sink actions, per the rules below. CITY LOST at 10000 bp stays. v1 `raid_infection_start_bp_by_band` is retired.
  - **Code to change:** move the field from the raid state to the campaign state, remove the reset in raid creation, add the post-raid decay hook, and add the save field.
- **S2 (Heat also speeds the street Bloom):** a new `pace_heat_pct` multiplier by Heat band applies to `pace_node` and `pace_turn`. v1 read Heat only for the raid start value.
  - **Code to change:** pace computation reads the Heat band.
- **S3 (no exemption for elites, mini-bosses and bosses):** v1 rule 3 already charged every fight the same, but the v1 arithmetic and Q-DESIGNER implied an exemption might exist. Rule 3 now says explicitly that none exists. The HQ crown fight is still frozen mid-fight, but its turns are charged when it ends (this affects the post-fight result only).
  - **Code to change:** none if the built branch charges every fight; add a test asserting it. Remove any class exemption flag if one was added.
- **S4 (Waiting Room debts cut):** v1 rule 14 and Art answer 9 already drop them. They are now final, with no new visual channel. Delete any debt-pip code.
- **S5 (no T1 free dose):** delete `bloom_free_doses_t1` and the start-of-netrun dose grant (v1 rule 8, last sentence).
  - **Code to change:** remove the grant and the test `test_bloom_t1_free_dose_and_wide_gap`. Replace it with a test that T1 starts with zero doses and the wide gap.
- **S6 (every Exploit slows the Bloom):** v1 gave Virus a 75 % pace multiplier, Intel a visibility effect and Breach nothing. Each Exploit now gets its own form (rule 12 below). Intel and Breach gain Bloom effects.
  - **Code to change:** `ExploitData` gets three Bloom effect fields; the pace code reads the held Exploits.
  - **Interaction:** the three effects stack (see rule 12).

## 1. Rules

**One mechanic:** a virus front trails the operative. The player's currency is delay, in whole route layers and combat turns, never real time.

**Units.** Positions are layers. `front_milli` and `layer_milli` are integers in thousandths of a layer. Gap = `layer_milli − front_milli`.

### Street netrun (light form)

1. At netrun start, `front_milli = −start_gap` and the operative is at layer 0. The state is DORMANT until the first node is entered, then CREEPING.
2. **Node entry.** The operative moves to the node's layer and the front advances by `pace_node_eff`.
3. **Combat turns.** When any fight ends, the front advances by `pace_turn_eff` × the turns that fight took. There is no exemption: normal fights, elites, mini-bosses and Server Rack fights all pay. The front is frozen during a fight, so the operative is never caught mid-fight.
4. **Effective pace.** `pace_node_eff = pace_node × heat_pct × exploit_pct / 100²` and `pace_turn_eff` likewise, floored, with a minimum of 1. `heat_pct` comes from the Heat band (S2). `exploit_pct` is the product of the held Exploits' pace multipliers (rule 12). It is computed once per entry, so there is no drift.
5. **Caught.** A gap ≤ 0 after rule 2 or 3 latches CAUGHT. Per Q24.1 the operative is lost with everything unbanked, the netrun is abandoned, the raid is unchanged, and the existing death consequences apply (10 + tier Heat).
6. **State bands** by gap: CREEPING above `close_gap`; CLOSE up to `close_gap`; CATCHING up to `catch_gap`; CAUGHT at 0 or below.
7. **Antiviral dose.** Pushes the front back by `dose_push`. Sold at Mainframes and offered as a Terminal option; the gap is clamped to `max_gap`. No dose is granted free at any tier (S5).
8. **Rooms.** A node whose layer is ≤ floor(front) is INFECTED (display only). Skipped branches behind the front count as INFECTED.
9. **Tier order.** T1 has the widest gap and lowest pace, so the Bloom teaches first and bites later.

### HQ netrun (full form)

10. Rules 1–6 and 8 run on the HQ ladder. One front is shared by both towers.
11. **ACROSS** advances the front by `pace_cross` in addition to the node entry. The price shows before commit. The HQ tolls are retired and the debts are cut (S4).
12. **Ward rest.** The REST node calls `dose_push`.
13. **Exploit keys (S6).** Every Exploit slows the Bloom, in its own form, and they stack:
    - **Virus (patch):** a pace cut. `pace_node` and `pace_turn` are multiplied by `virus_pace_pct` (75 %).
    - **Breach (kill switch):** a one-time setback of the front. On the first node entry of each netrun, the front moves back `breach_setback_milli`. It also cancels the ACROSS toll (`pace_cross` = 0).
    - **Intel (pricing memos):** the front is read and slowed at fights. Every fight's turn cost is cut by `intel_turn_pct` (50 %), and the whole ladder shows exact gaps.
    - A held Exploit is one that was collected this campaign and equipped for the netrun, as built today for the Exploit effects. Holding all three gives a pace multiplier of 0.75, a 1.0-layer setback, no ACROSS cost and half the turn cost.
14. **Crown.** The caught check applies on entering the crown. The Genome Core fight is frozen, and its turns are charged at its end.

### Raid (one hook, campaign figure)

15. `campaign.infection_bp` (0–10000) persists across raids and netruns. It starts at 0 at campaign start.
16. **Each resolution step**, after assets fire and threats damage nodes, it rises by `bp_base + bp_per_threat × threats alive`.
17. **CITY LOST.** At 10000 bp at any step, the raid ends CITY LOST: a campaign loss through the BREACHED path with its own end text. Operatives are never killed in raids.
18. **Decay (S1).**
    - When a raid ends CELL HOLDS, infection falls by `decay_hold_bp` and by `decay_per_threat_killed_bp` × threats destroyed.
    - Each Heat-reduction objective site completed and each Proxy Relay completion falls by `decay_cure_bp`.
    - It never falls below 0. It reaches zero only by these paths, so a campaign that defends well returns to 0 (like a reset).
    - A raid ending with TAKEN nodes does not decay it.
19. A raid entered with infection above 0 starts the step loop at that value, so the figure carries the stakes.
20. **Setup.** There is no clock in setup. The preview is exact.

## 2. State and save fields

| Field | Type | Lives in | Notes |
|---|---|---|---|
| `bloom.front_milli` | int | `BloomState` in `run_state.gd` | Negative at start |
| `bloom.layer_milli` | int | `BloomState` | Current layer × 1000 |
| `bloom.doses_taken` | int | `BloomState` | Telemetry |
| `bloom.caught` | bool | `BloomState` | Latched |
| `bloom.enabled` | bool | `BloomState` | False on non-Solace |
| `bloom.breach_applied` | bool | `BloomState` | **New:** the setback fired once |
| `campaign.infection_bp` | int | campaign state (was the raid state) | **Moved, persistent** |

**Derived (not saved):** `bloom_gap`, `bloom_state`, `pace_node_eff`, `pace_turn_eff`, `raid_infection_pct`.

**Determinism:** no randomness and no RngService stream.

**Save impact:** additive. A missing `campaign.infection_bp` loads as 0. A missing `breach_applied` loads false. Old saves keep working, and the v1 per-raid field is dropped on load. If N8 bumps the save version, fold these in.

## 3. Preview

- **Route choice:** each next node shows a `FRONT -n.n` chip, the exact gap after entering, with Heat and Exploit pace already applied. In the HQ, ACROSS adds its cost (0 under Breach). A `CAUGHT` warning shows if the gap would be ≤ 0.
- **Fight nodes:** `FRONT -n.n → ?`, with the turn cost unknown. The tooltip shows the effective per-turn rate, e.g. `−0.1 per turn` (after Heat and Exploit cuts). Nothing here reads a stream, so `?` is for turn count only.
- **Shop and Terminal:** a dose option with price and resulting gap.
- **Fight result:** `FRONT -a → -b`.
- **Raid setup:** the projected outcome is joined by `POPULATION INFECTED nn% → mm%` (campaign value now and at raid end), `CITY LOST at step n` or `holds`, the `+n%/step` rate, and the decay if the raid holds (`−dd% if CELL HOLDS`). Exact, no `?`.

## 4. Numbers (placeholders)

| Number | Value | Config key |
|---|---|---|
| Start gap, street T1–T4 | 4000 / 3500 / 3000 / 2500 | `campaign_config.bloom_start_gap_milli_by_tier` |
| Start gap, HQ | 3000 | `campaign_config.bloom_hq_start_gap_milli` |
| Pace per node, street T1–T4 | 500 / 600 / 650 / 700 | `campaign_config.bloom_pace_node_milli_by_tier` |
| Pace per node, HQ | 700 | `campaign_config.bloom_hq_pace_node_milli` |
| Pace per combat turn | 100 | `campaign_config.bloom_pace_turn_milli` |
| ACROSS cost | 500 | `campaign_config.bloom_pace_cross_milli` |
| Heat pace multiplier by band (COOL..PURGE) | 100 / 110 / 125 / 140 / 160 % | `campaign_config.bloom_pace_heat_pct_by_band` |
| Dose push | 1000 | `campaign_config.bloom_dose_push_milli` |
| Dose price (Cycles) | 15 | `campaign_config.bloom_dose_price` |
| Max gap | 5000 | `campaign_config.bloom_max_gap_milli` |
| CLOSE / CATCHING gap | 2000 / 1000 | `campaign_config.bloom_close_gap_milli`, `bloom_catch_gap_milli` |
| Virus pace multiplier | 75 % | `campaign_config.bloom_virus_pace_pct` |
| Breach setback | 1000 | `campaign_config.bloom_breach_setback_milli` |
| Intel turn-cost multiplier | 50 % | `campaign_config.bloom_intel_turn_pct` |
| Raid rise per step / per living threat | 50 / 100 bp | `campaign_config.raid_infection_bp_base`, `raid_infection_bp_per_threat` |
| Decay on CELL HOLDS | 1000 bp | `campaign_config.raid_infection_decay_hold_bp` |
| Decay per threat destroyed | 100 bp | `campaign_config.raid_infection_decay_per_kill_bp` |
| Decay per cure objective | 1500 bp | `campaign_config.raid_infection_decay_cure_bp` |
| Removed | n/a | `bloom_free_doses_t1` (delete) |

**Arithmetic.**
- **Street T3, no Exploits, Heat NOTICED (110 %):** node +715 per entry vs +1000 layer, so +285 gap. A 4-turn fight costs 440, a net −155. An 8-turn elite costs 880, a net −595. Six fights and one elite lose about 1500 of the 3000 gap, which is CLOSE. Without T1's free dose, long play reaches CATCHING.
- **All three Exploits:** pace 0.75, turn cost halved. A 4-turn fight costs about 165, a net near +120, and the setback adds 1000.
- **Raid:** 3 threats for 10 steps add 3500 bp. A raid that holds with 3 kills decays 1300 bp. A defended campaign trends to 0, a neglected one reaches 10000 in about 3 bad raids.

## 5. Tests to write

| Name | Tier | Asserts |
|---|---|---|
| `test_bloom_gap_after_node_entry` | fast | Gap change = layer step − `pace_node_eff` |
| `test_bloom_turns_charged_at_fight_end_all_classes` | fast | Normal, elite, mini-boss and Rack fights all pay turns × `pace_turn_eff`; the front is frozen mid-fight |
| `test_bloom_caught_at_gap_zero` | fast | Latches CAUGHT and routes to the Q24.1 loss |
| `test_bloom_state_bands` | fast | Exact at each boundary |
| `test_bloom_dose_push_and_clamp` | fast | Push, then clamp to `max_gap` |
| `test_bloom_t1_no_free_dose` | fast | T1 starts with 0 doses and the wide gap |
| `test_bloom_heat_band_speeds_pace` | fast | Pace follows the band table, floored, minimum 1 |
| `test_bloom_virus_scales_pace_once` | fast | A single multiplier, no drift |
| `test_bloom_breach_setback_once_and_no_cross_cost` | fast | The setback fires on the first entry only; ACROSS is free |
| `test_bloom_intel_halves_turn_cost` | fast | The turn cost uses `intel_turn_pct` |
| `test_bloom_exploits_stack` | fast | All three together equal the product formula |
| `test_bloom_hq_across_preview_equals_result` | fast | The chip equals the real change |
| `test_bloom_infected_rooms_both_towers` | fast | Layer ≤ floor(front) on both towers |
| `test_bloom_save_roundtrip_midnetrun` | full | An identical `BloomState`; an old save loads disabled |
| `test_bloom_disabled_on_other_corporations` | fast | `enabled` is false |
| `test_raid_infection_rises_per_step_and_threat` | fast | base + per-threat × alive |
| `test_infection_persists_across_raids` | fast | The next raid starts at the saved value |
| `test_infection_decay_on_hold_and_cure` | fast | Decay amounts; the floor at 0; no decay when TAKEN |
| `test_raid_city_lost_ends_campaign` | full | 10000 bp ends the campaign lost, with the Solace text |
| `test_raid_infection_preview_equals_result` | fast | The projection equals the played-out value, including decay |
| `test_operatives_never_killed_in_raid_infection` | fast | No operative change |
| `test_bloom_config_has_no_magic_numbers` | fast | Only the config keys above are read |

## 6. Build slices

1. **Rework: remove T1 free dose and class exemptions (S).** Delete the config key and test; add the all-classes test. No dependencies.
2. **Rework: Heat pace multiplier (S).** The config table, `pace_*_eff`, the chip tooltip. Depends on 1.
3. **Rework: Exploit forms (M).** The three effect fields on `ExploitData`, the breach setback with its flag, the Intel turn cut, the stacking product, the tests. Depends on 2.
4. **Rework: campaign infection (M).** Move the field, remove the per-raid reset, the start-at-saved-value rule, the save field and the load default. No dependency on 1–3.
5. **Decay hooks (M).** The CELL HOLDS decay, the kill decay, the cure-objective decay and the tests. Depends on 4.
6. **Raid preview update (S).** Now/end figures and the decay line. Depends on 4 and 5.
7. **Route chip update (S).** Effective rates in tooltips; ACROSS at 0 under Breach. Depends on 3.
8. **Delete debt-pip code (S).** Depends on none.

Art-pass owns the TIDE gauge look and the infection art.

## 7. Q-DESIGNER

Q-DESIGNER: Should the infection decay on a held raid be a flat amount plus kills as drafted (a defended campaign trends to 0), or should it reset fully to 0 after each raid that CELL HOLDS with no TAKEN node? (Keep the partial decay.)
Q-DESIGNER: Should Heat objective sites and Proxy Relay completions also cure infection, or should only raids lower it? (Yes, both cure.)
Q-DESIGNER: Is stacking all three Exploits (pace 0.75, setback, half turn cost, free ACROSS) too strong, should a cap apply on the combined slowdown? (No cap for now; tune after the sim.)
Q-DESIGNER: Should Heat's pace multiplier reach 160 % at PURGE, or should it stop at HUNTED? (Keep 160 %; PURGE is a rare end state.)
