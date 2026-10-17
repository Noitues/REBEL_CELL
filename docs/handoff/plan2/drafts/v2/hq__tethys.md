<!-- draft via Message Batches API, claude-sonnet-5-5, batch msgbatch_01TQsqGnerTdLwJEata9mp6i, custom_id v2__hq__tethys; status ok; tokens in 12209 cache-write 0 cache-read 32585 out 27178; cost $0.151. A DESIGN DRAFT for the designer's review: nothing here is built. -->

## Changes vs v1

- **Issue 1 (BLOCKER, layer arithmetic)** -> Fixed. The act table and the layer map now agree and are re-added in §2: layers 3+3+1+3+4+4+3+3+3+2+1 = 30. Acts I–III (layers 1–7) are 21 nodes and Act IV (layers 8–11) is 9 nodes (3/3/2/1). The layer-4/5/6 labels overlapped, so I cleaned them up. The v1 claim of "13–15 nodes visited" was also wrong: a path visits exactly one node per layer, so **11**. I authored every node's type and Level tag, which makes the HQ truly unique and lets me re-add the contents (14 normals, 4 events, 3 sluices, 2 rests, 1 cache, 1 shop, 1 Hub, 3 elites, 1 boss = 30).
- **Issue 2 (BLOCKER, Pressure)** -> Replaced with a rule that produces its own numbers. Pressure is 0 on layer 8 and +1 per layer. Max RAM is reduced by (Pressure − 1), capped at −2, and floored at 4. The reduction is relative to the class's own max, not an assumed 12 (the Rigger has +1). The table is in §3.4: layer 10 = −1 and layer 11 = −2 without a reset; with the layer-9 rest, layer 11 = −1.
- **Issue 3 (BLOCKER, Lockkeeper vs R1)** -> The Lockkeeper is now a real 2-phase elite of 6–8 turns, with a T4 HP budget of 126 (R2 band 112–144). The arithmetic is in §3.3: 18 dpt × 3.5 turns × 2 phases = 126, threshold 0.5 (floor 63). The Head steps at the end of turn 4 and turn 8, and winning in 6 turns or fewer earns a choice. It is counted as an elite (3 elites in the HQ).
- **Issue 4 (MAJOR, Head)** ->
  - Removed the LOW nudge penalty. LOW now simply lasts 3 completed nodes instead of 2, which stretches the safe window.
  - Surge no longer respins anything. The enemy's turn-1 wheel position is authored per node and shown on it (no hash, no RNG, preview = result).
  - Removed the redundant "never closed at both HIGH and FALLING" line.
  - Added the structural guarantee that every layer has at least one UPPER node.
- **Issue 5 (MAJOR, HP budget)** -> Redone in §5 as a timeline: class HP 60, loss 4 normals × 8 + 2 elites × 16 = 64, healing 18 + 18 + 12 = 48, arriving at the boss at 44/60, with a low point of 14. The Hub heal is now one option in a pick-one list, not double counted. Rests are Decompression-type nodes at layers 6 and 9, both authored.
- **Issue 6 (MAJOR, sluices)** -> Three sluices (L2 ×2, L6 ×1) are stated consistently. Divert may only target a LOWER node on layers 8–9. I also fixed a deeper flaw: v1's L2 Hold/Skip changed a Head the lock then reset, so they did nothing. L2 Hold/Skip now shifts the lock's result step.
- **Issue 7 (MAJOR, Virus)** -> Removed the "buff down by one" effect, which duplicated R7. Contamination is now only the one-per-run Pollute. The determinism claim now reads "a function of completed nodes and the logged player actions".
- **Issue 8 (MAJOR, Ballast / dry run)** -> Ballast is a completion Daemon choice with a precise cap rule, with no always-true condition. The "dry run" is replaced by **Low Tide Run**: clear layers 8–10 entirely under LOW. This is verifiable, because v1's condition was vacuous (LOWER nodes are closed at HIGH).
- **Issue 9 (NIT, Heat)** -> The Wait action no longer costs Heat. The Head never raises Heat, and this is stated once.
- **Issue 10 (NIT, phantom references)** -> Removed the "AD rule 8.4" and "2026-10-16 Q2 ruling" references. The slot mapping is now marked as a proposal for the art session to confirm.
- **Triage rows** -> Layer count: Issue 1. Pressure: Issue 2. Lockkeeper: Issue 3.
- **Scope trims** -> Dropped the undefined "tide card" and "Sluice key" items. Hold comes only from sluices, and the second sluice action now comes from Master Valve (Breach). Dropped the Hub's "pay HP for a buff" option.
- **Kept** -> The Head as one legible run-wide clock tied to the art's gauges, the committed one-way descent, per-key themed Exploit payoffs, the data-only fallbacks, and the per-frame art hook table.
- **Rulings** -> No conflicts with a designer ruling. R1, R2, R7, R9, D5 and D10 are respected.

---

# Tethys Deep: HQ netrun draft

Working names: the HQ netrun is **THE DAM RUN**. The boss is **THE BLACK SMOKER boss** (see the enemy/corp drafts; referenced by name only). The Hub room is **THE VENT CAP**. The first elite is **the Lockkeeper**.

## 1. Concept & the named mechanic

**What the art shows.**
- A dry city, with a warm-lit concrete dam holding the drowned quarter above street level (water at ZW 2.5, dry street at 0).
- One company door through the dam: the DOCK LOCK.
- Beyond it, a calm-ringed pier city on stilts, then a stair of pressure decks and a moon pool leading to the server on a vent chimney.
- One art rule: warm is the dam and the dry side, cool is Tethys and the water.

**The mechanic: THE HEAD (water level).** The netrun has one run-wide state, the **Head**: how high the water stands.
- It has 4 steps in a cycle: **LOW → RISING → HIGH → FALLING → LOW**.
- It advances by completed nodes: LOW lasts 3 nodes, the other steps last 2 each, so a full cycle is 9 nodes.
- Every node has a **Level** (UPPER or LOWER). The Head decides which LOWER nodes are open and how fights on UPPER nodes feel.
- Sluice puzzles let the player hold, skip or divert the tide. The Head is deterministic and shown many steps ahead.

**Why it can't be mistaken for another HQ.**
- Halcyon is gaze and stealth, Solace is a tower ladder, Meridian is a shuttle yard, Orbital is gates, and REBEL_CELL is a mirror district.
- Tethys is the only HQ where a shared clock reshapes the map every few nodes, and the only one that descends: dry city → lock → piers → stair → moon pool. Depth is progress; the Head is the clock.

## 2. Structure

**Length: 11 layers, 30 nodes.** The player visits exactly 11 of them (one per layer).

| Act | Layers | Landmark place | Nodes per layer | Sum |
|---|---|---|---|---|
| I. The Dry Side | 1–2 | Dam road, sluice bays | 3, 3 | 6 |
| II. The Lock | 3 | DOCK LOCK chamber | 1 | 1 |
| III. The Piers | 4–7 | Causeway, pier-end pods, ring pods, inner pods | 3, 4, 4, 3 | 14 |
| IV. The Deep Stair | 8–11 | Station deck, pressure decks, THE VENT CAP, moon pool | 3, 3, 2, 1 | 9 |

Acts I–III = 21 nodes, Act IV = 9 nodes, total **30**.

**Authored layout (type, Level).** U = UPPER, L = LOWER. Level matters for closure at HIGH (§3.1). Rule: **every layer has at least one UPPER node**, so HIGH never closes a whole layer.

```
L1  [N U][N U][Event U]                 Dam road
L2  [Sluice U][Sluice U][N U]           Sluice bays (two puzzles)
L3          [LOCKKEEPER elite U]        Choke (hard convergence)
L4  [N U][N U][Event L]                 Causeway
L5  [N U][N U][N L][Event L]            Pier-end / ring (ring edges)
L6  [Rest U][Cache U*][Sluice U][N L]   Ring (ring edges); *cache open at HIGH only
L7  [Elite U][N U][Event L]             Inner pods
L8  [Shop U][N U][N L]                  Station deck
L9  [N U][Rest "Decompression" L][N L]  Pressure decks 1-2
L10 [HUB: VENT CAP U][Vent Guard elite L]   one of the two
L11         [BOSS U]                    Moon pool
```

**Count check.**
- Normals: L1 2, L2 1, L4 2, L5 3, L6 1, L7 1, L8 2, L9 2 = **14**.
- Events: L1, L4, L5, L7 = **4**.
- Sluices **3**, rests **2**, cache **1**, shop **1**, Hub **1**.
- Elites: Lockkeeper, L7 elite, Vent Guard = **3**.
- Boss **1**.
- 14+4+3+2+1+1+1+3+1 = **30**.

**Edge rules.**
- L1→L2 free (each node has 2–3 forward edges). Every L2 node leads to the lock.
- The lock opens to all of L4.
- Layers 4–7 are forward edges plus lateral edges to the 2 ring neighbors on layers 5 and 6 (a hex ring, so the player can step sideways at the cost of a completed node, which also advances the Head).
- Layers 8–11 are **forward only**: the glass drops are one-way, with no cross-links, so the descent feels committed.
- Max 3 outgoing edges per node.
- A shortcut edge R2→S1 (L6→L8) exists only with Master Valve (§4).

**Mapping onto landmark slots** (proposal; the art session confirms the slot generator):

| Slot class | Landmark place | Layers |
|---|---|---|
| `dam_bay` (on the dam arc) | Sluice bays, dam crest | 1–2 |
| `lock` | DOCK LOCK | 3 |
| `pier_end`, `ring`, `inner` | The three pod rings | 4–7 |
| `station` | Main deck, crown | 8 |
| `deck` (floors 1–2) | Pressure decks | 9 |
| `vent_cap` | THE VENT CAP / guard | 10 |
| `core` | Moon pool server | 11 |

If a layer needs more pods than slots, the generator adds a small pod on the ring. No layer here exceeds 4 pod nodes.

## 3. Unique mechanics

### 3.1 THE HEAD (the spine)

- **Rule.**
  - The Head starts LOW. It advances one step after every **completed node** counted as follows: a fight, event, shop, sluice or cache is 1 node, and a **rest counts as 2** (it passes time). The counter runs 3 nodes at LOW and 2 at each other step.
  - Lateral ring moves count as 1 node. The lock fight does not use the counter; it sets the Head (§3.3) and the counter restarts from that step.
- **Effects by Head:**

| Head | UPPER nodes | LOWER nodes |
|---|---|---|
| LOW | open, normal | open, normal (the safe window) |
| RISING | open, normal | open, normal |
| HIGH | **Awash**: fights give the enemy +1 resistance (tier-independent, per R2) | **Closed** (drowned), unless Drained or opened by Master Valve |
| FALLING | open; fights get **Surge** (below) | open; fights get **Surge** |

- **Surge.**
  - The enemy's turn-1 wheel position is a fixed tick authored on the node and shown on it. It replaces the random turn-1 respin for the enemy wheel only, and the rewind checkpoint is unchanged.
  - It is a combat override, so it needs no RNG. Preview equals result because the tick is shown before entry.
  - The tick is placed so that it is sometimes a Perfect-exposure for the player and sometimes harmless: a puzzle, not a penalty.
- **Closed nodes and the guard.** The "every layer has an UPPER node" rule stops a whole layer from closing, but the player's current forward edges can all be LOWER. A free **Wait** action then appears: it advances the Head one step, costs nothing else (no Heat, no HP), and is shown only when every forward node is closed.
- **What the player sees.**
  - A tide gauge on the map (the art's ballast column and the dam's white-tick gauge) showing the current step plus the next 3, and a Level glyph (U/L) on each node.
  - Closed nodes are drawn drowned (clear-water look, deep fade). The 3D water plane rises and falls with the Head.
  - Surge nodes show the fixed enemy start tick.
- **Counters.** Sluices (§3.2), a Drained node, Master Valve, and planning the route so the Deep Stair falls under LOW.
- **Determinism.** The Head is a pure function of completed nodes and the logged player actions (sluice actions, lock result, Wait, Pollute). No RNG.

### 3.2 SLUICE GATES (3 puzzle nodes: L2 ×2, L6 ×1)

- **Rule.** A small non-combat page: a forecast row of the next 8 Head steps (one gate per future step) and 3 actions. The player takes **1 action** (2 with Master Valve) or declines:
  1. **Hold:** the next tide step is delayed by one completed node.
  2. **Skip:** the Head advances one step now.
  3. **Divert:** mark one **LOWER node on layers 8–9** (S3, K2 or K3) as **Drained**: it stays open at any Head until the run ends. The Head does not change.
- **At L2 (before the lock).** Hold and Skip shift the **lock's result step** one step earlier (Hold) or later (Skip) along the cycle. So an L2 sluice means "which tide do I want when I enter the piers?".
- **At L6.** Hold and Skip act on the live Head.
- **Cost.**
  - Hold and Skip are free but lose or gain time.
  - Divert is permanent and spends your only action, so you can't also shape the Head.
  - Each puzzle is a bet on which tide you will meet at layer 9.
- **What the player sees.**
  - The dam's hoist gantry and white-tick gauge light up, and each future-step gate shows open (white water down the spillway) or shut (dark culvert grate, red light).
  - The map previews the Head track with the chosen action ghosted.
- **Determinism.** No hidden info and no RNG. Preview equals result.

### 3.3 THE LOCK CYCLE (layer 3, the Lockkeeper)

- **Rule.** The DOCK LOCK is an elite fight per R1: **2 phases, 6–8 turns**. While it runs, the chamber fills. The Head steps at the end of **turn 4** (LOW→RISING) and **turn 8** (→HIGH).
- **Result** (it sets the Head for the start of Act III):

| Win turn | Head at layer 4 |
|---|---|
| ≤ 6 | the player **picks LOW or RISING** |
| 7–8 | RISING |
| ≥ 9 (enrage has begun) | HIGH (half the pier-end nodes are Awash or closed) |

  An L2 sluice may shift the result one step (§3.2).
- **HP budget (R2, T4 elite).**
  - Phase budget = `reference_dpt_by_tier[T4]` 18 × `target_turns_per_phase` 3.5 × 1 needle = 63 per phase.
  - 2 phases = **126 HP** (inside the 112–144 band). Sustain is 0, so no deduction.
  - Threshold 0.5: HP floor ceil(126 × 0.5) = 63, so P1 is 63 and P2 is 63.
  - The expected win is turn 7 (126 / 18), which gives RISING. Turn 6 or fewer needs ~21 damage per turn, so choosing the Head is the skill reward.
- **Enrage.** The elite default (start turn 8, every 5, +25 %) coincides with the second tide step: the water is rising and so is the damage.
- **The phase design itself** (two questions, one per phase) belongs to the corp drafts. This draft fixes only HP, threshold and the clock.
- **What the player sees.** The mitre gates, with the chamber water level tracking the Head steps; they open on a win and the water covers the gates on a late result.
- **Determinism.** Standard combat. The turn counts are exact thresholds.

### 3.4 THE PRESSURE STAIR (layers 8–11)

- **Rule.**
  - **Pressure** is an integer that is 0 on entering layer 8 and gains +1 per layer descended.
  - **Max RAM −(Pressure − 1)**, never below 0 reduction and capped at −2 (max RAM never goes under 4). It is relative to the class's own max (Rigger +1 and so on).
  - It applies in fights on layers 8–11, including the boss.
  - The L9 Decompression rest resets Pressure to 0. The Hub can reset it as one of its options.

| Layer | Pressure (no reset) | Max RAM change | With the L9 rest reset |
|---|---|---|---|
| 8 | 0 | 0 | 0 |
| 9 | 1 | 0 | 1 (reset after the rest, then 0) |
| 10 | 2 | −1 | 1 (0) |
| 11 | 3 | −2 | 2 (−1) |

  Resetting at L9 turns the boss's −2 into −1. Resetting at the Hub as well turns it into 0.
- **Why.** The descent becomes a resource decision: slower and more deliberate play buys the LOW window, but arrives with less RAM.
- **What the player sees.** A depth gauge next to the tide gauge (deck rim lights and fog), and a RAM cap pip on the RAM bar.
- **Determinism.** A pure function of the layer index and the logged resets.

## 4. Node kit

Fights follow R1 (normals 1 phase, 3–4 turns; elites 2 phases, 6–8 turns), at T4.

| Node | On the map | Tethys twist |
|---|---|---|
| **Normal fight** | 14 | The Head's Awash and Surge modifiers apply (§3.1). Enemies come from the Tethys pool (corp drafts). |
| **Elite fight** | 3: the Lockkeeper (L3), the L7 inner-pod elite, the Vent Guard (L10) | Awash gives +1 resistance at HIGH, and Surge fixes the enemy's turn-1 position at FALLING. Each elite has 2 phases (126 HP at the T4 band minimum, tuned per elite in the corp drafts) and +1 Heat. |
| **Sluice puzzle** | 3 | §3.2. |
| **Event** | 4 | Tide events: each offers one choice per Head step, with the available choice shown. A choice can carry a heal (~10), a Divert, or a fight. Data-only: an event condition on `head_step`. |
| **Shop** | 1 (L8) | Prices are set by the Head (RISING cheapest), fixed per step and shown. |
| **Rest** | 2 | L6 Pier Rest: heal 30 % max HP, counts as 2 nodes. L9 Decompression: same, plus resets Pressure; it is LOWER, so the tide matters. |
| **Cache** | 1 (L6) | A diving-bell cache, open **only at HIGH** (UPPER, so reachable). Pays Schematics. |
| **Hub (VENT CAP)** | 1 (L10) | The last safe room: pick **one** of: heal 12, reset Pressure to 0, or a boss preview that reveals the next phase's layout. The alternative at L10 is the Vent Guard elite (a Firmware reward), so the player chooses between the Hub and the elite. |

**Exploit payoffs (D5).** Intel, Breach and Virus stay as the Grid gate types and keep their R7 role against the boss's buffs. In this HQ each also gives a **netrun bonus on top** (it does not replace the gate function). Nothing here adds a boss effect.

| Exploit | HQ name | Effect inside the netrun |
|---|---|---|
| **Intel** | Tide Tables | The full Head forecast is shown for the whole run (not 4 steps), and every node's Level glyph is visible from layer 1 (otherwise the next 2 layers). |
| **Breach** | Master Valve | Opens **one** Closed node per HIGH step, gives a second sluice action, and unlocks the shortcut edge R2→S1 (skips the L7 elite, so the player forgoes its reward). |
| **Virus** | Contamination | **Pollute:** once per run, the player may set the Head to any step immediately (not during the lock). It is a logged player action (§3.1). |

## 5. Pacing & difficulty curve

**Expected run: 27–32 minutes** (a standard netrun is ~15). That is a deliberate HQ stretch inside D10.

**Typical safe path** (one node per layer, 11 nodes) and its HP timeline at T4 (class HP 60; normals cost 8, elites 16):

| Layer | Node | HP change | HP after |
|---|---|---|---|
| start | | | 60 |
| 1 | Normal | −8 | 52 |
| 2 | Sluice (Divert K2) | 0 | 52 |
| 3 | Lockkeeper | −16 | 36 |
| 4 | Normal | −8 | 28 |
| 5 | Normal | −8 | 20 |
| 6 | Pier Rest | +18 | 38 |
| 7 | Elite | −16 | 22 |
| 8 | Normal | −8 | **14** (low point) |
| 9 | Decompression | +18 | 32 |
| 10 | Hub (heal) | +12 | 44 |
| 11 | Boss | | arrives at 44/60 |

Loss = 4 × 8 + 2 × 16 = **64**. Healing = 18 + 18 + 12 = **48**. 60 − 64 + 48 = 44. ✓

**Alternatives.**
- Swapping L8 for the shop, or L1/L4/L5 for an event (~10 heal), raises the low point.
- Skipping a rest for a fight cannot be paid for (supply is 60 plus 48): at least one rest is required, so the budget forces both rests and the Hub heal.
- The L7 elite and the Vent Guard are optional risk-for-reward picks.

**Time.** 4 normals × 2 = 8, 2 elites × 4 = 8, sluice 1, rests 1, Hub 1, boss 7–9, plus map and story ~2, which is about **28–29**.

**Heat.** Each elite is +1, so the safe path adds +2 (the Lockkeeper counts as an elite). The boss carries the standard boss Heat. The Head never adds Heat.

**Curve.**
- Act I is the teaching act: LOW, with a forecast and one sluice.
- Act II is the first test (the lock clock).
- Act III is the widest choice (ring, cache, rest, sluice).
- Act IV removes lateral choice: only descent, Pressure and the Hub trade.
- The boss is the exam.

## 6. Rewards

- **Schematics.** The cache (HIGH only) and the Hub-or-Vent-Guard choice bank Schematics immediately (Server-Rack-style banking). The cache pays the most.
- **Tide Chart.** After the first completion, a profile flag grants Tide Tables' 4-step to full forecast on later Tethys netruns (not the HQ). Data-only.
- **Ballast (Daemon, completion choice among two rare Daemons).** Once per combat, a single hit that would deal 10 or more HP damage deals at most 6. It applies after block and shield, includes pierce, and does not apply to self-damage or parasite loss.
- **Low Tide Run.** Clear layers 8–10 with the Head LOW on every node: one extra rare Firmware choice. This is verifiable from the logged Head, and reachable via the Divert and Hold sluices.
- **Corp story beat.** The corporation's finale beat is delivered after the boss (GDD 8.4).

## 7. Failure & retry

- **Death.** The standard rule: the operative is lost with everything unbanked, and the campaign gains 10 + tier Heat. Banked Schematics are kept.
- **Retry.** A new operative re-enters the DOCK LOCK. The layer shape, node types and Level tags are authored and identical, so the player can learn the map; the Tethys enemies in the normal slots are drawn from the run's seed. Solved sluices and the Head are not remembered. Exploits the Grid holds persist, so earlier keys still help.
- **No mid-run checkpoint** beyond Rewind within a fight. Quit saves the exact state (GDD 4.5).
- **Heat on failure.** Standard death Heat only.
- **Soft-lock.** The Wait action (§3.1) guarantees progress.

## 8. Systems needed

| System | Used for | N# | Fallback |
|---|---|---|---|
| Phases, threshold parking | Elites (2 phases), the Lockkeeper, the boss | N3 | none (R1) |
| Enrage | Lockkeeper, boss | N4 | none |
| Boss buffs and Exploits | Exploit payoffs and boss counters | N5 | The three netrun bonuses ship as data-only netrun flags. |
| Events that alter paths/fights | Divert (`map_edits`), Surge start tick and Pressure (`combat_overrides`) | N16 | Cut Divert; Surge becomes a node tag only. |
| Event wheel kit | Sluice page | N17 (optional) | An event with 3 fixed choices and no forecast row. |
| Data-driven rewards | Hub, cache and Vent Guard tables | N18 | Hard-coded offers. |
| Sim metrics | Turns per phase, parked damage | N19 | none |
| **NEW: `netrun_head`** | Head state, step counter, Level closure, Wait, Pollute | NEW | **Data-only fallback:** Level tags and a fixed per-layer Head baked into the graph, with no player control (loses sluices and Pollute). |
| **NEW: `sluice_node`** | Forecast page, Hold, Skip, Divert | NEW (could reuse N17) | An N16 event with 3 choices. |
| **NEW: `netrun_modifiers`** | Pressure max-RAM cap, Awash resistance, Surge fixed turn-1 tick | NEW (extends N16 `combat_overrides`) | N16 overrides authored per node by hand. |
| **NEW: `hq_graph_spec`** | An authored 11-layer graph with ring lateral edges and one-way descent | NEW | A standard layered generator plus a post-pass for lateral and shortcut edges. |

**Build order.**
1. N3 → N4 → N19, with the Lockkeeper and elite designs (foundation wave).
2. `hq_graph_spec` with the Level tags and the fixed-Head fallback.
3. `netrun_head` (live Head, Wait, Pollute).
4. `sluice_node` (event-page reuse first, then the forecast row).
5. `netrun_modifiers` (Pressure, Awash, Surge) over N16.
6. N5 → the three Exploit bonuses → the boss.
7. N18 for the Hub, cache and Vent Guard tables.

## 9. Art hooks

Per frame, the game passes these to the landmark:

| State | Used for |
|---|---|
| `head_step` (0–3), `head_next[3]` | Water plane height in the drowned quarter, the dam gauge, caustic strength |
| `gate_state[]` | Sluice leaves: lifted with white water, or shut with a dark culvert grate and red light |
| `lock_state` (shut / filling / open), `lock_result` | Mitre gates, chamber water level, signal lights |
| `node_level[]`, `node_open[]` | U/L glyphs, drowned look for closed nodes (deep fade, dimmed windows) |
| `cache_open` | The diving bell surfacing at HIGH |
| `surge_tick[]` | A pulse in the surface wave bump on the pod, showing the fixed enemy start tick |
| `pressure` (0–3) | Deck rim lights deepen, camera fog sigma rises per level |
| `drained[]` | Diverted lower nodes drawn dry |
| `route_position` | The current pier, ring or deck lit, the glass drop lift light |
| `exploit_flags` | Tide Tables: future-step ghost on the gauge. Master Valve: the opened node's light. Contamination: black smoke tint at the vent when Pollute is spent |
| `boss_phase` | The Black Smoker vent glow rising, ink darkening the water around the server |

The art already has the gauges, gates, lock and decks, so only per-frame parameters are needed.

## 10. Q:

Q: Is LOW lasting 3 nodes (the other steps 2) the right way to make LOW the safe window, or should all steps last 2?
Q: Does the Pressure RAM cap (−2 at the boss) stack acceptably with R9's corrupted-slice RAM doubling in the final fight, or should Pressure cap at −1?
Q: Is the Lockkeeper's graded result (choose / RISING / HIGH by win turn) acceptable, given that its enrage and the second tide step both land on turn 8?
Q: Is a roughly 28-minute, 11-layer HQ run the right length for the designer within D10's open range?
Q: Should Divert stay permanent for the run, or fade after one tide cycle to keep the puzzle repeatable?
