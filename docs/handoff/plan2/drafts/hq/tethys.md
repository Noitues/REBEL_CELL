<!-- draft via Message Batches API, claude-sonnet-5-5, batch msgbatch_01HADBSF5pLwaHAq7nbABzZa, custom_id hq__tethys; status ok; tokens in 16303 cache-write 0 cache-read 32007 out 8832; cost $0.064. A DESIGN DRAFT for the designer's review: nothing here is built. -->

# Tethys Deep: HQ netrun draft

Working names: the HQ netrun is **THE DAM RUN**. The boss is **THE BLACK SMOKER boss** (the octopus; see the enemy/corp drafts). The Hub room is **THE VENT CAP**.

## 1. Concept & the named mechanic

**What the art shows.** A dry city, a warm-lit concrete dam holding the drowned quarter above street level (water at ZW 2.5 against a dry street at 0), and one company door through it: the DOCK LOCK. Beyond the dam is a calm-ringed pier city on stilts. Below it is a stair of pressure decks and a moon pool leading to the server on a vent chimney. The art has one rule: warm is the dam and the dry side, cool is Tethys and the water.

**The mechanic: THE WATER LEVEL.** The netrun has a single run-wide number, the **Head**, which is how much water stands above the dry side. The player moves through locks. Each node has a **Level** (a lock stage), and the Head determines which nodes are open, which fights are flooded, and how hard enemies are hit.

- The Head has 4 steps: **LOW, RISING, HIGH, FALLING** (the tide cycle the boss wheel art already uses).
- The Head advances by one step every **2 completed nodes** (a "tide tick"). It is fully deterministic and visible many steps ahead, with no RNG.
- The player gains control over it through **sluice gates**: puzzle nodes that hold the current tide step for N ticks, or skip ahead one step.

**Why it can't be mistaken for another HQ.** Halcyon is a read-the-eye stealth/gaze problem, Solace is a ladder up a tower, Meridian is a timed shuttle yard, Orbital is gates that open and shut, and REBEL_CELL is a mirror district. Tethys is the only HQ where *time cycles a shared resource that reshapes the map and every fight*, and where the player descends rather than climbs. The route goes from dry city through the lock, across the surface piers, and down the stair to the Black Smoker. Depth is progress, and the Head is the clock.

## 2. Structure

**Length: 11 layers**, longer than the standard 7. They break into 4 acts, each tied to a place in the landmark:

| Act | Layers | Landmark place | Nodes per layer |
|---|---|---|---|
| I. The Dry Side | 1–2 | Dam road, sluice bays, lock control tower | 3, 3 |
| II. The Lock | 3 | The DOCK LOCK chamber (a single choke layer) | 1 (the lock itself) |
| III. The Piers | 4–7 | Causeway, pier-end pods, ring pods, inner pods | 3, 4, 4, 3 |
| IV. The Deep Stair | 8–11 | Station main deck, decks 1–5, THE VENT CAP, moon pool | 3, 3, 2, 1 (the boss) |

Node totals: 3+3+1+3+4+4+3+3+3+2+1 = **30 nodes** on the graph, of which the player visits about 13–15 along their path.

**Edge rules.**
- Act I to the lock: every layer-2 node leads to the lock (convergence).
- The lock (layer 3) is a **hard choke**: it opens to all of layer 4 but with a Head-dependent subset visible (see 3.1).
- Act III: layers 4–5 are the **causeway and pier-end pods**, and layers 5–6 are the **hex ring**, with lateral edges only to the 2 neighbours on the ring (a hexagonal adjacency, so the player can walk around the ring at a Head cost). Layer 7 inner pods have forward edges only.
- Act IV: a descent: layers 8–10 each have forward edges only (the glass drops are one-way vertical links, so there is no backtracking). Layer 10 is the Hub room and layer 11 is the boss.
- No node has more than 3 outgoing edges. There are no cross-links in Act IV, so the descent feels committed.

**Layer map.**

```
L1  [D1a][D1b][D1c]        Dam road: fights/event
L2  [D2a][D2b][D2c]        Sluice bays (two are sluice puzzles)
L3        [LOCK]           Choke: Lock puzzle + mini-fight
L4  [C1][C2][C3]           Causeway / pier-end pods (3 of 6)
L5  [P1][P2][P3][P4]       Pier-end + ring pods (lateral ring edges)
L6  [R1][R2][R3][R4]       Ring pods (lateral ring edges)
L7  [I1][I2][I3]           Inner pods (last pods before the station)
L8  [S1][S2][S3]           Station: main deck / crown / hub-room approach
L9  [K1][K2][K3]           Deck stair 1–2
L10 [VC-a][VC-b]           THE VENT CAP (Hub) and the Decompression elite
L11       [BOSS]           Moon pool: THE BLACK SMOKER boss
```

**Mapping onto slots.** Per the AD rule (8.4), the graph is assigned to slots in layer order, then node order, and the landmark generates slots on demand. The Tethys module exposes these slot classes:

| Slot class | Landmark place | Link geometry |
|---|---|---|
| `dam_bay` (frame on the dam line, ordered along the arc) | Sluice bays, dam crest | Same level: walk along the crest |
| `lock` (single slot) | DOCK LOCK | Fixed |
| `pier_end` / `ring` / `inner` | The three pod rings | Same level: ring walkway. Rising/falling: the piers |
| `station` | Main deck, crown | Rising |
| `deck` (floor 1–5) | Pressure decks | Falling: glass drops |
| `core` | Moon pool server | Falling |

Overflow rule for graphs with more nodes than slots: reuse slots by stacking an additional pod around the ring (the generator can create more pods at `s` 0.19, per the "small versions of itself" rule). A layer with more than 6 nodes in the pod classes is not expected.

## 3. Unique mechanics

### 3.1 THE HEAD (tide tick) — the spine

- **Rule.** The Head runs LOW → RISING → HIGH → FALLING → LOW. It starts at LOW on entry. It advances one step after every **2nd completed node** (fight, event, shop, rest all count; moving through an empty corridor does not). The current step and the next three are always shown.
- **Per-layer effect.** Every node has a **Level** tag, **UPPER** (surface: dam road, pier pods, station) or **LOWER** (decks, flooded rooms, the causeway's underside). Level interacts with the Head:

| Head | UPPER nodes | LOWER nodes |
|---|---|---|
| LOW | open, normal | **Dry**: normal, but 1 free nudge less in the fight (cramped, no room to tune) |
| RISING | open, normal | open, normal |
| HIGH | **Awash**: enemies get +1 resistance (the water slows your wheel) | **Flooded**: the node is **closed** unless the player holds a Sluice or Exploit that opens it |
| FALLING | open, normal | open, normal; **Surge**: all enemy wheels respin their first Needle once on entry (deterministic: the value is fixed by the node's seed, shown ahead) |

  The values above are placeholders. The design intent: LOW is the safe window for the Deep Stair, HIGH is the time to be on the surface and out of the stair, and the player plans where to be on which tick.
- **What the player sees.** A tide gauge (the art's ballast column and the dam's white-tick water gauge) on the netrun map: the current step plus the next three, and each node's Level glyph. Closed nodes under HIGH are drawn as drowned (the art's clear-water look, with the deep fade). In the 3D landmark the water plane rises and falls by the Head value. Caustics are stronger at RISING and FALLING.
- **Counters.** Sluice puzzles (3.2), the Exploit effects in section 4, and the **tide card**: a one-use netrun pickup, "HOLD", that freezes the Head for one tick.
- **Determinism.** The Head is a pure function of completed-node count and the player's sluice actions. There is no RNG. The Surge's respin value is derived from a hash of (run seed, node id), so it is fixed and previewable. If a Surge value must come from an RNG stream, use the existing `combat` stream at the combat checkpoint, which already supports rewind.

### 3.2 SLUICE GATES — the puzzle nodes

- **Rule.** Layer 2 (two of the three nodes) and one node in layer 6 are **Sluice puzzles**, not fights. The player faces a small row of 4 gates, each open or shut, with the tide's next four steps shown. Each gate has a cost in **Tide Ticks**. The player picks one of three outcomes:
  1. **Hold:** freeze the Head for the next tick.
  2. **Skip:** advance the Head one step now.
  3. **Divert:** mark one LOWER node on the next layer as **Drained**: it is open and safe at any Head until the run ends.
- Each puzzle allows exactly 1 action (2 with a Sluice key). A puzzle is solved by reading the forecast: the answer is "which tide do I want when I reach the stair".
- **What the player sees.** The gate bay on the dam lights up (the art's hoist gantry, steel lift gate, white-tick gauge), and one in three gates already runs white water down the spillway when open. The map shows a "preview": the Head track with the player's chosen action ghosted.
- **Counters / risks.** The Skip makes the next tick come sooner, so the player pays for a window with less recovery. Divert is permanent and per-run, a real commitment.
- **Determinism.** Fully deterministic, no RNG. The puzzle has no hidden information, and the preview equals the result.

### 3.3 THE LOCK CYCLE — the layer 3 choke

- **Rule.** The DOCK LOCK is the single node on layer 3. It is a **mini-fight with a clock**: a 4-turn fight against **the Lockkeeper** (an elite-class mini-encounter, 2 phases per R1). Under the clock, the lock chamber fills: at the end of turn 4 the Head steps once. The player's reward for winning inside the turn limit is that they **pick the Head** for the start of the pier act (LOW or RISING). If they run over, the Head is set to HIGH at entry to layer 4 and half the pier-end nodes are Awash.
- **Counters.** Burst, or spend RAM on the tide card. The outcome is committed at the end of the fight, and it shows as the mitre gates opening (win) or the water over the gates (loss).
- **Determinism.** Standard combat. The turn count is an exact threshold.

### 3.4 THE PRESSURE STAIR — the descent

- **Rule.** On each layer below 7, the player carries **Pressure**, an integer that rises by 1 per layer descended (starting at 0 at layer 8). Pressure acts as a **cap on the player's max RAM** for fights in the Deep Stair: −1 max RAM per 2 Pressure (so 11 at layer 10, 10 at layer 11 for a base of 12). The Hub (THE VENT CAP) and a **Decompression** event (3.4a) can reset it.
- **Why.** It makes the descent a resource decision. A slower, deliberate player gets more value from the Head windows but fights deeper fights with less RAM.
- **What the player sees.** A depth gauge beside the tide gauge, and the art's deck pressure rims. The wheel shows a RAM cap pip.
- **Determinism.** A pure function of the layer index.

**3.4a Decompression** (a rest-type node on layers 9 and 10 only): the player may stay for 2 tide ticks to reset Pressure to 0, at the cost of heal (see section 4). The tick cost makes it a real tide decision, not free.

## 4. Node kit

Fight tiers follow R1: normals 1 phase, 3–4 turns; elites 2 phases, 6–8 turns. Tier assumption is T4 (HQ), with enemy stats from the tier tables.

| Node | Count on a typical path | Tethys twist |
|---|---|---|
| **Normal fight** | 5 | Level and Head modify it per 3.1. Enemies are drawn from the Tethys pool (to be written in the corp drafts). |
| **Elite fight** | 2 (layer 7 inner pod, layer 10 Decompression guard) | Each flips on the tide: at a LOW Head the elite is in the **Dry** variant, at HIGH it is **Awash** (resistance). The elite's 2 phases are separated by a **Surge** at the threshold (Surge applies the FALLING rule once). |
| **Mini-fight (Lockkeeper)** | 1 (layer 3) | See 3.3. |
| **Sluice puzzle** | 2 (layers 2 and 6) | See 3.2. |
| **Event** | 2 (e.g. the dam road, the ring walkway) | Tethys events show the Head: one choice per Head step (a "tide event"). Data-only: reuse the event schema with a `head_step` condition (see 8). |
| **Shop** | 1 (station main deck) | Prices are set by the Head: RISING is cheapest. Prices are fixed per step and shown. |
| **Rest (Decompression)** | 1–2 | Heal 30 % max HP, costs 2 tide ticks; also resets Pressure. |
| **Cache** | 1 | A diving-bell cache on the ring: opens only when the Head is HIGH. It holds a Schematics reward (see 6). |
| **Hub (THE VENT CAP)** | 1 (layer 10) | The last safe room before the boss. Offers the **final trade**: pay Pressure for heal, or pay HP for a buff, or pick a **boss preview** that reveals the next phase's layout (see 3 of the boss draft). |

**Exploit payoffs (D5: each key is an Exploit with its own building).** Every Exploit the player holds opens one thing in the HQ netrun. The three existing gate types are Intel, Breach and Virus. Because Tethys is a water corporation, each Exploit is a water tool:

| Exploit | Name in this HQ | Effect inside the netrun |
|---|---|---|
| **Intel** | Tide Tables | The Head forecast is shown for the entire run instead of 4 steps, and every node's Level glyph is visible from layer 1. Also reveals the Surge value on each node. |
| **Breach** | Master Valve | Opens **one** closed (Flooded) node per HIGH step, and lets the player take a **short cut**: an extra edge from layer 6 to layer 8, bypassing layer 7. |
| **Virus** | Contamination | At the start of the boss fight, the boss's first phase starts with its buff list **down by one** (it carries the counter, per R7). Also, a Virus run can **pollute** a Tide step: the player may mark one future step as FALLING instead of its natural step, once per run. |

Other Exploits that a corporation grid draws (R7: `exploits_per_grid` = 5) map to buff counters in the boss fight. This HQ does not add its own buff counters. It adds the three above as netrun modifiers. A route with 0 Exploits can still be completed (see section 7), since `min_exploits_for_breach = 3` is a Grid gate, not a netrun one.

## 5. Pacing & difficulty curve

**Expected run: 28–35 minutes** (the standard netrun is 15 minutes with about 5 combats). This run has about 7 fights and a boss.

| Part | Fights | Minutes (target) |
|---|---|---|
| Act I (dam road) | 1 normal + 1 sluice | 4 |
| Act II (lock) | 1 mini-fight | 3 |
| Act III (piers) | 2 normals + 1 sluice/event | 8 |
| Act IV (stair) | 2 normals + 1 elite + hub | 10 |
| Boss | 1 (4–5 phases, 12–20 turns) | 7–9 |

At 3–4 turns per phase and about 2 turns of thought per phase, a normal fight is about 2 minutes, an elite about 4, and the boss about 8.

**HP and Heat pressure.**
- Entry is at full HP (HQ runs start fresh, as the existing rule gives survivors full HP at HQ).
- Estimated HP loss: normals 8–12 HP at T4, elites 18–24, the Lockkeeper 14. A typical path loses about 90–110 HP before the boss against a pool of about 55–65 (class HP), so the player must heal about 40–50 HP across the run. This forces use of the rest and heal nodes.
- **Heal budget:** 2 Decompression rests at 30 % (about 18 HP each), plus 1 event heal (about 10), plus one heal from the Hub (about 12–15), for roughly **55–65 HP of healing** across the run. If the player skips both rests, they arrive at the boss at 30–40 % HP. The tide ticks cost: each rest costs 2 ticks, so the player is forced to plan their route around the Head.
- **Heat.** Entering the HQ netrun adds no Heat at the door. Each Elite adds +1 (existing rule), and the boss kills carry the standard boss Heat. The HQ run does not raise Heat from the Head.
- **Curve.** Act I is a teach: the Head is LOW for the first 2 nodes, and the sluice shows its forecast. Act II is the first test (the lock clock). Act III is the widest choice (the ring). Act IV removes choice: only descent and Pressure. The boss is the exam.

## 6. Rewards

Beyond the boss kill:
- **Schematics.** Each cache and the Hub grant a Schematic payout (Server Rack-style banking, immediate). The Cache on the ring (HIGH only) pays the most.
- **The Tide Chart (permanent campaign unlock for that corporation).** After the first completion, a note unlocking the Head forecast as a free **Tide Tables** effect on later Tethys netruns (not the HQ run). Data-only: a profile flag.
- **Daemon: "Ballast".** A rare Daemon dropped by the Hub if the run ended with Pressure under 4. Placeholder effect: once per combat, when you would take 10+ damage, take at most 6.
- **A Rack-style bonus.** Completing the run without ever letting the Head hit HIGH while on a LOWER node (a "dry run") grants one extra rare Firmware choice.
- **Corp story beat.** The finale beat for the corporation is delivered after the boss (per GDD 8.4).

## 7. Failure & retry

- **Death in the HQ netrun:** the standard rule applies: the operative is permanently lost with everything unbanked, and the campaign gains 10 + tier Heat. The run graph is **not** reset or persisted: a retry is a **new** run of the same HQ netrun.
- **Retry.** A new operative can re-enter the DOCK LOCK. The route graph is regenerated (the route differs every game, per the 2026-10-16 Q2 ruling), but **solved sluice puzzles are not remembered**. The Exploits the Grid holds stay, so keys already collected make later attempts easier.
- **Banked loot** (caches, Schematics from the Hub that were already banked) is kept on death, as the existing rule says for Server Racks.
- **No mid-run checkpoint** beyond the standard Rewind within a fight. A quit saves exactly, per section 4.5.
- **Heat on failure.** Standard death Heat only. No additional Head penalty.
- **Soft-lock guard.** The Head always advances by completed nodes, so the player can never stall at a closed node. If every forward node is closed (all Flooded at HIGH, no Exploit), the game offers a free **Wait** action that advances the Head one step at a cost of 1 Heat. Nodes can never be closed at both HIGH and FALLING.

## 8. Systems needed

| System | Used for | N# | Fallback |
|---|---|---|---|
| Phases on every class, threshold parking | Elites with 2 phases, the Lockkeeper, the boss | N3 | none, required by R1 |
| Enrage | The boss and elites | N4 | none |
| Boss buffs and Exploits | Boss fight and Exploit payoffs in 4 | N5 | The three Exploit effects in section 4 can ship as data-only netrun flags. |
| Fixed satellites | Not used here | N13 | n/a |
| Data-driven rewards list | Hub and Cache rewards | N18 | Hard-coded offers, as today. |
| Events that alter future fights or paths | Tide events, Divert, Drain | N16 | Events could only grant items. Divert would need to be cut or replaced by a pickup. |
| Sim metrics | Turns per phase, fight length balance | N19 | none |
| **NEW: Run Clock (the Head)** | The Head, tick rule, Level tags, HIGH closure, Surge, Wait action | NEW: `netrun_head` | A **data-only** reduced form is possible: the Head becomes a fixed per-layer tag baked into the generated graph (no player control). It loses sluice and Hold. |
| **NEW: Puzzle node (Sluice)** | A small non-combat page with 4 gates and a forecast | NEW: `sluice_node` (could reuse the event page and the N17 event wheel kit) | An event with 3 fixed choices (Hold, Skip, Divert) and no forecast row. Loses the planning feel. |
| **NEW: Netrun-wide modifiers** | Pressure (max RAM cap), Dry/Awash fight modifiers | NEW: `netrun_modifiers` (reuses `next_combat_overrides` from N16) | N16's overrides, applied by hand per node. |
| Variable HQ graph (unique graph, 11 layers, ring adjacency) | The layer map | NEW: `hq_graph_spec` per corporation (map graph generator with a lateral ring rule) | Generate a standard layered graph with the lateral edges added by a post pass. |

**Build order.**
1. N3 → N4 → N19, with the Lockkeeper and elite designs on top (foundation wave, already planned).
2. NEW `hq_graph_spec` (11 layers, ring) and the Level tags (data-only Head, as a fixed fallback first).
3. NEW `netrun_head` (dynamic Head, Wait action, soft-lock guard).
4. NEW `sluice_node` (event-page reuse first, then forecast row).
5. NEW `netrun_modifiers` (Pressure, Dry/Awash) with N16 overrides.
6. N5 (Exploits) → the three netrun payoffs of section 4 → the boss.
7. N18 for the Hub and Cache tables.

## 9. Art hooks

Per frame, the game passes these to the landmark (8.4 rule 4):

| State | Used for |
|---|---|
| `head_step` (0–3) and `head_next[3]` | The water plane height in the drowned quarter and the dam gauge, the caustic strength at RISING and FALLING |
| `gate_state[]` (open/closed per sluice) | The sluice leaves: lifted with white water down the spillway, or closed with a dark culvert grate and red light |
| `lock_state` (shut / filling / open) | The DOCK LOCK mitre gates, the chamber water level, the signal lights red or green |
| `node_level[]` and `node_open[]` | UPPER/LOWER glyphs, and drowned look for closed nodes (deep fade, dimmed windows) |
| `pressure` (0–4) | Deck rim lights deepen, and the camera fog sigma rises by a small step per level |
| `route_position` | The pier, ring or deck lit as the current room, the glass drop lift light |
| `drained[]` | Diverted lower nodes drawn dry (no water in the room) |
| `exploit_flags` | Tide Tables: the future-step ghost on the gauge. Master Valve: the opened Flooded node's light. Contamination: black smoke tint at the vent |
| `surge_warn` | A pulse in the surface wave bump on the node's pod |
| `boss_phase` | The Black Smoker vent glow rising up the moon pool, the ink phase darkening the water around the server |

The art already has the gauges (the dam's gauge, the ballast column), the gates, the lock and the pressure decks, so nothing new needs modelling: only per-frame parameters.

## 10. Q:

Q: Should the Head advance on completed nodes (current draft, player can stall) or on a hard per-layer step (no stall, but no planning from rests)?

Q: Is an 11-layer, about 30-minute HQ run the right length for the designer, given the 15-minute standard netrun and the open-ended D10 range?

Q: Does the player keep a **permanent** Divert (a node stays drained for the run), or should Divert fade after one tide cycle to keep the puzzle repeatable?

Q: Should the Lockkeeper's turn limit be a hard fail (the Head is set to HIGH) or a softer penalty, given that the HQ boss's own enrage is also a turn clock?

Q: Do the Exploit payoffs (Tide Tables, Master Valve, Contamination) replace the existing Intel/Breach/Virus Grid functions in this HQ, or sit on top of them as bonuses?

Q: Is the Pressure RAM cap acceptable alongside the corruption RAM tax (R9), or do the two stack into too much RAM pressure for the final boss?
