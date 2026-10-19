<!-- THEMES draft via Message Batches, claude-sonnet-5-5, batch msgbatch_01QpYFZqBxUvn2JMgwTbAhtu, custom_id theme__aurelian; status ok; tokens in 22175 cache-write 33457 cache-read 0 out 13829; cost $0.133. DRAFT: designer picks. -->

# Aurelian Concord: COLOSSEUM RINGS

Working term: **the Ring**. Four concentric rings, three keys, and a gate in each ring. The same three-key, gate-per-ring structure appears at every scale: the Grid, the street, the HQ and the raid.

Dropped from the HQ draft: its VERDICT mark, Favor meter and Grand Stand finale (§3.2–3.4). They are boss/HQ content, not the corp theme, and the art plan drops them too. The HQ draft's turning gates (§3.1) are kept.

## 1. Rules: street, HQ, raid

**Reuse map**
- **Rim gates (N15):** one shared `GateData` (tick, width) and N15's lit-gate preview. Here the gate sits on a ring of 30 ticks instead of a wheel rim.
- **Inner ring:** the 3-segment, 10-tick geometry becomes the HQ entrance **key ring**, one segment per Exploit.
- **Cross-links:** the Grid's existing locked cross-links (GDD 4.1) become ring gates.
- **ICE Lock:** the raid's edge hold.

**Campaign Grid (carrier of the keys)**
- **C1.** An Aurelian Grid is built in 3 rings (outer, middle, inner) around a central plaza that holds the HQ. Every Site stores its `ring`.
- **C2.** The link from one ring to the next is a locked cross-link: a **ring gate**. There are 3 ring gates: outer→middle, middle→inner, inner→plaza.
- **C3.** Each ring gate is keyed to one Exploit type, drawn at campaign start so that each of INTEL, BREACH and VIRUS keys one gate. The Exploit Site that keys a gate lies in a ring outside that gate. Extracting the Exploit opens the gate for the rest of the campaign. This is D5: access key = Exploit.
- **C4.** Sites inside a closed gate are visible but cannot launch netruns.
- **C5.** The plaza (HQ) entrance shows the **key ring**: `min_exploits_for_breach` segments, each lit when an Exploit is owned. Entry needs all of them lit.
- **C6.** Heat bands and tier chains are unchanged.

**Street netrun (light form)**
- **S1.** Each Aurelian street netrun has one **key node**: a Router or Elite Router on layers 2–4, marked with a key glyph.
- **S2.** Winning that fight grants the **Street Key**. The key is lost if the operative dies.
- **S3.** Each street netrun has one **gated Cache**: an extra node between a layer-5 node and a layer-6 node. The link into it is an **arch gate**: SHUT without the Street Key, OPEN with it.
- **S4.** The Cache is an Elite-strength fight (R2 elite HP) that banks Schematics and offers one Firmware choice. It adds +1 Heat, as an Elite does. It is optional, so a netrun can never softlock.
- **S5.** The generator guarantees a path from layer 1 through the key node to the Cache's feeder node. The street has no clock.

**HQ netrun (full form)**
- **H1.** The HQ has 9 levels: T1, T2, T3 (loggia), AT (rim), R1–R4 (seating rings), VAULT. Levels come from `hq_levels` config, and the level count is not fixed art.
- **H2.** Along-level links are always open. A **descent link** exists between the last room of one level and the first rooms of the next. There are 5 descent gates: AT crossing, R1→R2, R2→R3, R3→R4, R4→VAULT.
- **H3.** Each descent gate is a window on a 30-tick ring (`GateData`: tick, width). Rooms have a tick azimuth. A descent link is powered only while its gate window overlaps the departing room's tick at the moment of commit.
- **H4.** After every completed node (fight, event, shop, rest, cache), each gate rotates by its fixed step in ticks, with alternating signs. Combat turns and raid interludes never step the clock.
- **H5.** The telegraph shows the gate position for the next **1** step. Intel extends it to **4** steps (preview rule, §3).
- **H6.** **Breach key:** once per gate, hold that gate in place for one step. It is used at the room before leaving.
- **H7.** **Virus key:** Rest nodes heal 40% instead of 25%, and Cache nodes offer an extra reward choice.
- **H8.** The generator guarantees that from any reachable room, some gate schedule reaches the next level within 4 steps. Waiting in place is not allowed; a sideways move is a node and costs a step.
- **H9.** On a retry, the clock resets to step 0. Room azimuths and types regenerate from the map stream.
- **H10.** The Vault fight is the boss fight (the corp draft). The key ring is shown at the HQ entrance (C5), not inside the run.

**Raid (one hook)**
- **R1.** An Aurelian raid draws 4 rings around the **defended node**. Ring links in the raid graph carry a `ring_gate` index (an ICE Lock-like edge hold).
- **R2.** A closed ring gate holds every threat on it. It opens by itself after `ring_hold_steps`, counted from the first threat arriving at it.
- **R3.** A **key-carrier** threat (a Levy wedge with `carries_key`) that reaches a ring gate opens it that step. The first key opens ring I and the second opens ring II.
- **R4.** Killing a key carrier before it reaches its gate keeps the gate closed until its timer runs out.
- **R5.** Gates stay open for the rest of the raid. Everything else follows GDD 7.2: 30 steps, assets fire, damage spreads.
- **R6.** Operatives are never killed in raids (Q24.1).

## 2. State and save fields

| Field | Type | Lives in | Notes |
|---|---|---|---|
| `SiteData.ring` | int | content `.tres` | Generated by the grid generator |
| `CampaignState.ring_gate_keys` | Array[ExploitType] (3) | `scripts/state/` campaign state | Drawn at campaign start from the campaign stream |
| `CampaignState.ring_gates_open` | Array[bool] (3) | same | |
| `LinkData.ring_gate` | int (−1 = none) | Grid and raid link data | |
| `ThreatData.carries_key` | bool | raid threat data | |
| `RaidState.ring_gate_timer` | Array[int] | raid state | −1 until the first arrival |
| `NetrunState.street_key` | bool | run state | |
| `NetrunState.gate_link_id` / `key_node_id` | StringName | run state | Written by the generator |
| `NetrunState.step_count` | int | run state (HQ only) | |
| `NetrunState.gates_held` | Array[bool] | run state (HQ) | Cleared after each step |
| `GateData` | tick, width | shared with N15 | |

- **Save impact:** campaign save version +1 with a migration that defaults `ring` and `ring_gate` to −1 and `ring_gates_open` to all true for old saves (old campaigns have no rings). Run save +1 for the new run-state fields.
- **Determinism:** gate keys and the Grid ring layout use the existing campaign stream at creation. The street key and Cache placement use the existing map stream at generation. The clock and the raid hook use no RNG. Both streams are checkpointed as they are today.

## 3. Preview

- **Grid:** hovering a ring gate shows "KEY: INTEL / BREACH / VIRUS" and whether it is owned.
- **Street:** the key node shows a key glyph. The arch shows "KEY NEEDED" or "OPEN". The Cache preview shows its Elite-strength HP and rewards.
- **HQ:** every descent link reads "GATE OPEN NOW / OPEN IN n STEPS / CLOSED". The gate's next position is drawn as the telegraph.
  - Positions beyond the telegraph depth show "?".
  - Powered links are lit and unpowered links are grey.
  - A Breach hold shows its effect on the next step before commit.
- **Raid:** each ring gate shows its timer ("OPENS IN n") and whether a key carrier will reach it. The projected outcome per node follows GDD 7.1. Everything in a raid is deterministic, so there is no "?".

## 4. Numbers (placeholders)

| Key | Value |
|---|---|
| `config: campaign_config.aurelian_ring_count` | 3 |
| `config: campaign_config.aurelian_ring_gate_keys` | 1 key per gate |
| `config: campaign_config.street_key_layers` | 2–4 |
| `config: campaign_config.street_cache_layer_gap` | feeder layer 5 |
| `config: campaign_config.street_cache_schematics` | 4 |
| `config: campaign_config.hq_levels` | 9 |
| `config: campaign_config.hq_gate_steps_ticks` | [+2, −2, +3, −3, +2] |
| `config: campaign_config.hq_gate_width_ticks` | 1 |
| `config: campaign_config.hq_telegraph_default` | 1 |
| `config: campaign_config.hq_telegraph_intel` | 4 |
| `config: campaign_config.hq_gate_reach_max_steps` | 4 |
| `config: campaign_config.hq_rest_heal_pct` | 25 (Virus 40) |
| `config: campaign_config.raid_ring_count` | 4 |
| `config: campaign_config.raid_ring_hold_steps` | 6 |
| `config: campaign_config.raid_key_carriers` | 3 |

## 5. Tests to write

| Name | Tier | Asserts |
|---|---|---|
| `test_grid_ring_gates_open_on_exploit` | fast | Extracting the keyed Exploit opens the gate. Sites inside a closed gate cannot launch a netrun. |
| `test_grid_ring_gate_keys_are_distinct` | fast | Each of INTEL, BREACH and VIRUS keys exactly one gate, and the key Site lies outside its gate. |
| `test_street_key_and_cache_guarantee` | full | 200 seeds: each street netrun has a key node on layers 2–4 and a Cache, with a path through the key node. |
| `test_arch_gate_requires_street_key` | fast | The arch is SHUT without the key and OPEN with it. The key is lost on death. |
| `test_hq_gate_power_function` | fast | Powered iff the window overlaps the room tick. The telegraph function matches the power check at step n+1 (preview = result). |
| `test_hq_clock_steps_on_node_only` | fast | A combat turn or raid interlude does not step the clock. A node completion does. |
| `test_hq_breach_hold` | fast | A Breach hold keeps one gate in place for exactly one step, once per gate. |
| `test_hq_reachability_guarantee` | full | 200 seeds: every room reaches the next level within 4 steps. |
| `test_hq_key_ring_entry` | fast | Entry needs `min_exploits_for_breach` lit segments, matching the owned count. |
| `test_raid_ring_gate_hold_and_open` | fast | A closed gate holds a threat. It opens after the hold timer or when a key carrier arrives. |
| `test_raid_key_carrier_killed` | fast | Killing the carrier early leaves the gate on its timer. |
| `test_ring_save_roundtrip_and_migration` | fast | The new fields round-trip, and an old save migrates with all gates open. |

## 6. Art answers

**Answers to the art plan's questions**
1. **Q1:** Yes, with a limited scope. The step clock and SHUT are adopted for the HQ only (H3–H4). The Street, Grid and Raid use static gates (open or shut by key). B-ROT and SHUT frames are therefore needed in the HQ only. B-ROT is a lit window moving on the ring-edge line, driven by `gate_tick_now` and `gate_tick_next`.
2. **Q2:** Per frame the HQ provides these fields:
   - `step_count`;
   - per gate: `gate_tick_now`, `gate_tick_next`, `gate_width`, `held`;
   - per descent link: `powered` and `opens_in_steps` (null when not displayed);
   - `telegraph_depth` (1 or 4).

   The plan's `gate_angles` become integer ticks (tick × 12° if an angle is needed). `held_rings` becomes `gates_held`.
3. **Q3:** Yes. The three keys are the three Exploits (INTEL, BREACH, VIRUS). The Grid ring gates and the HQ key ring check them. `min_exploits_for_breach` gates HQ entry. Art needs `exploits_owned` (0–3) and the owned types.
4. **Q4:** Raid rings centre on the **defended node** (the home server for a raid on it). The Aurelian HQ is the centre of the Grid layer's rings, not of the raid rings.
5. **Q5:** Raid data is:
   - 4 rings (`raid_ring_count`) with one gate per ring, as an edge flag;
   - 3 key-carrier threats (`raid_key_carriers`) hold the keys;
   - a breached ring means its gate is open and the threats pass inward;
   - a held key means a carrier is alive and on its way.
6. **Q6:** The arch no longer depends on boulevard crossings. It sits on the street's gated Cache link (`gate_link_id` is in run data). The street map does not show the HQ landmark; the skyline laurel stays off.
7. **Q7:** The Aurelian Grid ring contours are rule-bearing, so they are always on for Aurelian and are not a toggle. Other Grid layers are unchanged.
8. **Q8:** Raid state names are in the table below.
9. **Q9:** The HQ ring count follows the generated level count (`hq_levels`, default 9, with 5 descent gates). Art reads `level_count` and does not treat it as fixed.

**State names**

| Art plan's name | Game name | Notes |
|---|---|---|
| Rooms UNREAD / READ / CURRENT / CLEARED | unchanged | No new room states |
| Gate: available | OPEN | `powered` is true |
| Gate: taken | PASSED | The player has gone through it |
| Gate: not offered | UNOFFERED | Not reachable from the player's room |
| Gate: SHUT | SHUT | HQ: window not on the room. Street: no key |
| Gate: HOVER | HOVER | |
| Raid PENDING | PENDING | |
| Raid ACTIVE | ONGOING | |
| Raid DEFENDED | CELL HOLDS | The GDD end state |
| Raid LOST | BREACHED | The home server fell. PACIFIED stays as the art stamp |
| Key held / not held | `exploits_owned` and `carries_key` | The Grid and the raid read different fields |

## 7. Reuse and dependencies

| Dependency | Source | Fallback |
|---|---|---|
| Gate data, lit-gate preview | N15 (rim gates) | None; gates need N15's `GateData` |
| Inner-ring geometry for the key ring | Inner ring (existing) | A plain 3-pip row |
| Locked cross-links as ring gates | Existing (GDD 4.1) | n/a |
| Raid edge hold | ICE Lock (existing) | n/a |
| Elite-strength Cache with rewards | N18 reward rows, Server Rack combat | The Server Rack is reused as it is today |
| Run-level state | N16-style run overrides | None needed |

**NEW code**
- **Ring clock:** `step_count`, the per-gate step table, the power function and the telegraph function. Data-only fallback: authored `open_on_steps` per link (readability cost only).
- **Ring gate flags** on Grid and raid links.
- **`carries_key`** on threats.
- **Street key and Cache generator step.**

Not used: the Parasite ring, enrage and resistance.

## 8. Q-DESIGNER

Q-DESIGNER: Does the HQ clock (the turning gates) stay in the HQ only, or does a light version belong in street netruns too?
Q-DESIGNER: Is the default HQ telegraph depth 1 step with Intel extending it to 4, or should a default of 4 make it a pure planning puzzle?
Q-DESIGNER: Should the 3 ring gates be keyed by the 3 Exploits in a random campaign order, or fixed (INTEL outer, BREACH middle, VIRUS inner)?
Q-DESIGNER: Is a gated Cache (key-gated optional Elite-strength node) the right street reward, or should the arch simply be cosmetic?
Q-DESIGNER: Should a retry of the HQ regenerate the layout from a new seed, or replay the same layout so the player can learn the clock?
Q-DESIGNER: Is a 9-level HQ of roughly 30–36 minutes acceptable, or should the HQ drop a seating ring to about 25 minutes?
