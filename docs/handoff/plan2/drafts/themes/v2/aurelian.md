<!-- THEMES2 draft via Message Batches, claude-sonnet-5-5, batch msgbatch_01BLNcf54zM6exqecvb8qLg7, custom_id themes2__aurelian; status ok; tokens in 15442 cache-write 0 cache-read 34418 out 4265; cost $0.040. v2: designer answers 2026-10-19 applied. -->

# Aurelian Concord: COLOSSEUM RINGS (v2)

## 0. What changed from v1

- **A1 (HQ only):** the clock and turning gates exist in the HQ only. The street's key node, Street Key, arch gate and gated Cache are removed (rules S1-S5, tests, state fields, numbers). The street gets no Aurelian rule. The street arch is cosmetic (A4), so nothing on it is rule-bearing.
- **A2 (default):** telegraph depth stays 1 step, and Intel extends it to 4. No change.
- **A3 (random order):** ANY Exploit can unlock ANY gate. v1 C3 fixed a key to a gate by type (INTEL, BREACH and VIRUS each key one gate). v2 replaces that with **order-based unlocking**: the Nth Exploit extracted (any type) opens ring gate N. The Grid ring gates are no longer typed. Distinct-key tests and hover text ("KEY: INTEL") go away.
  - The Exploit Site that gives the Nth Exploit still has to be reachable. The generator guarantees at least one Exploit Site outside each gate (see 1.C3).
- **A4 (arch cosmetic, no Cache):** the gated Cache, `street_key`, `gate_link_id`, `key_node_id` and the Cache config keys are removed. The Street Key is gone. **Fallback Q6 from v1 is answered.**
- **A5 (same layout on retry):** v1 H9 said "room azimuths and types regenerate from the map stream". v2: the HQ layout (rooms, azimuths, types, gate steps) is generated once and **stored**; a retry resets only the clock to step 0 and the run state. This needs a stored HQ seed or layout.
- **A6 (full 9-level HQ):** v1 already used 9 levels (`hq_levels` = 9). Confirmed; no change.
- **Already built?** Aurelian is not yet built, so no rework slice. Consequences for v1 text: the "Art answers" section (§6) is dropped from this document as it was art-plan material. Its Q1 (HQ only), Q2 (fields), Q6 (arch off the boulevards) and Q7 stand as written for art, with the street fields removed.

## 1. Rules

### Campaign escalation (Grid)

- **C1.** An Aurelian Grid is built in 3 rings (outer, middle, inner) around a central plaza that holds the HQ. Every Site stores its `ring`.
- **C2.** The link from one ring to the next is a locked cross-link, a **ring gate**. There are 3 ring gates: outer→middle, middle→inner, inner→plaza.
- **C3.** Gates are untyped. Extracting **any** Exploit opens the next closed gate, innermost-last (outer→middle first). Exploit Sites are generated so that for each gate N at least one Exploit Site lies in a ring outside it and every Exploit type is placed at a different Site (GDD 4.1). The campaign can never lock itself.
- **C4.** Sites inside a closed gate are visible but cannot launch netruns.
- **C5.** The HQ entrance shows the **key ring**: `min_exploits_for_breach` segments, each lit when an Exploit is owned. Entry needs all of them lit.
- **C6.** Heat bands and tier chains are unchanged.

### Street (light form)

- **S1.** No Aurelian street rule. A street netrun is a standard netrun. The arch is a cosmetic landmark in the art (A4) and has no state.

### HQ (full form)

- **H1.** The HQ has 9 levels: T1, T2, T3 (loggia), AT (rim), R1-R4 (seating rings), VAULT. Levels come from `hq_levels`; art reads the generated level count.
- **H2.** Along-level links are always open. A **descent link** joins the last room of one level to the first rooms of the next. There are 5 descent gates: AT crossing, R1→R2, R2→R3, R3→R4, R4→VAULT.
- **H3.** Each descent gate is a window on a 30-tick ring (`GateData`: tick, width). Rooms have a tick azimuth. A descent link is powered only while its gate window overlaps the departing room's tick at the moment of commit.
- **H4.** After every completed node (fight, event, shop, rest), each gate rotates by its fixed step in ticks, alternating signs. Combat turns and raid interludes never step the clock.
- **H5.** The telegraph shows each gate's position for the next 1 step. With Intel owned it shows 4 steps.
- **H6.** **Breach effect:** once per gate, hold that gate in place for one step. Used at the room before leaving.
- **H7.** **Virus effect:** Rest nodes heal 40% instead of 25%.
- **H8.** The generator guarantees that from any reachable room some gate schedule reaches the next level within 4 steps. Waiting in place is not allowed; a sideways move is a node and costs a step.
- **H9.** The layout is generated **once per campaign HQ** and stored. A retry after a failed run resets `step_count` to 0 and all gate positions to their step-0 values; rooms, azimuths, node types and step table are identical (A5).
- **H10.** The Vault fight is the boss fight. Operatives lost during an HQ run follow Q24.1 (operative lost, netrun abandoned).

### Raid (one hook)

- **R1.** An Aurelian raid draws 4 rings around the defended node. Ring links carry a `ring_gate` index (an ICE Lock-like edge hold).
- **R2.** A closed ring gate holds every threat on it and opens by itself after `ring_hold_steps`, counted from the first threat arriving.
- **R3.** A **key-carrier** threat (`carries_key`) that reaches a ring gate opens it that step. First key opens ring I, second ring II.
- **R4.** Killing a key carrier before it reaches its gate keeps that gate closed until its timer runs out.
- **R5.** Gates stay open for the rest of the raid. Everything else follows GDD 7.2 (30 steps).
- **R6.** Operatives are never killed in raids (Q24.1).

## 2. State and save fields

| Field | Type | Lives in | Notes |
|---|---|---|---|
| `SiteData.ring` | int | Grid site data | Grid generator output |
| `CampaignState.ring_gates_open` | Array[bool] (3) | campaign state | Opened in order by Exploit count; derivable from owned Exploits |
| `LinkData.ring_gate` | int (-1 none) | Grid and raid links | |
| `ThreatData.carries_key` | bool | raid threat data | |
| `RaidState.ring_gate_timer` | Array[int] | raid state | -1 until first arrival |
| `CampaignState.hq_layout` | rooms (level, tick azimuth, type), gate step table | campaign state | Generated once on first HQ entry; stored (A5) |
| `NetrunState.step_count` | int | run state (HQ) | 0 on every start or retry |
| `NetrunState.gates_held` | Array[bool] | run state (HQ) | Cleared after each step |
| `GateData` | tick, width | shared with N15 | |

- **Removed from v1:** `ring_gate_keys`, `street_key`, `gate_link_id`, `key_node_id`.
- **Determinism:** the Grid ring layout uses the existing campaign stream at creation. The HQ layout uses the map stream once, at first HQ entry, then is stored; a retry draws nothing. Clock and raid hook use no RNG.
- **Save impact:** campaign save +1 (migration: `ring` and `ring_gate` = -1, `ring_gates_open` all true, `hq_layout` absent and generated on first entry). Run save +1 for the HQ step fields.

## 3. Preview

- **Grid:** hovering a ring gate shows "OPENS WITH EXPLOIT n of 3" and the owned count.
- **HQ:** every descent link reads "GATE OPEN NOW / OPEN IN n STEPS / CLOSED". Positions beyond the telegraph depth show "?" (a display limit, not a random value). Powered links are lit and unpowered links grey. A Breach hold shows its effect on the next step before commit. Preview equals result: the telegraph function equals the power check at step n+1.
- **Raid:** each ring gate shows "OPENS IN n" and whether a key carrier will reach it. Deterministic, no "?".
- **Street:** nothing Aurelian.

## 4. Numbers (placeholders)

| Key | Value |
|---|---|
| `config: campaign_config.aurelian_ring_count` | 3 |
| `config: campaign_config.hq_levels` | 9 |
| `config: campaign_config.hq_gate_steps_ticks` | [+2, -2, +3, -3, +2] |
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
| `test_grid_ring_gate_opens_in_order` | fast | The Nth Exploit of any type opens gate N; Sites inside a closed gate cannot launch. |
| `test_grid_exploit_sites_reachable` | full | 200 seeds: an Exploit Site lies outside each gate; no campaign soft-locks. |
| `test_hq_gate_power_function` | fast | Powered iff the window overlaps the room tick; telegraph at step n+1 equals the power check. |
| `test_hq_clock_steps_on_node_only` | fast | Combat turns and raid interludes do not step the clock; a node completion does. |
| `test_hq_breach_hold` | fast | A hold keeps one gate for exactly one step, once per gate. |
| `test_hq_reachability_guarantee` | full | 200 seeds: every room reaches the next level within 4 steps. |
| `test_hq_retry_same_layout` | fast | After a failed HQ run the layout equals the first; `step_count` is 0; no RNG drawn. |
| `test_hq_key_ring_entry` | fast | Entry needs `min_exploits_for_breach` lit segments, matching the owned count. |
| `test_raid_ring_gate_hold_and_open` | fast | A closed gate holds a threat; it opens on timer or a key carrier. |
| `test_raid_key_carrier_killed` | fast | Killing the carrier early leaves the gate on its timer. |
| `test_ring_save_roundtrip_and_migration` | fast | New fields round-trip; an old save migrates with all gates open. |

## 6. Build slices

1. Grid ring data, `ring_gate` links, order-based opening, key-ring display (M; none).
2. HQ layout generation, storage and retry reset (M; slice 1 for the Exploit count; N15 `GateData`).
3. HQ clock: step table, power and telegraph functions, descent links (L; slice 2, N15).
4. Breach hold, Virus rest bonus, Intel telegraph depth (S; slice 3).
5. Raid ring gates, `carries_key` threats (M; ICE Lock).
6. Save migration (S; with slices 1-3).

Art-pass owns the 3D look: B-ROT and SHUT frames, the arch, the rings.

## 7. Q-DESIGNER

Q-DESIGNER: When a Grid has more than 3 Exploits owned (extra beats), should the extras do anything for the gates, or only for story beats? (Only story beats.)
Q-DESIGNER: Should a failed HQ run keep the Breach "once per gate" uses already spent? (No, they reset with the clock.)
Q-DESIGNER: Should the stored HQ layout be fixed per campaign or per HQ attempt chain, since A5 says same on retry? (Per campaign.)
