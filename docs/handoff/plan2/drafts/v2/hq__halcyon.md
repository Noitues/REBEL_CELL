<!-- draft via Message Batches API, claude-sonnet-5-5, batch msgbatch_01TQsqGnerTdLwJEata9mp6i, custom_id v2__hq__halcyon; status ok; tokens in 12012 cache-write 0 cache-read 32585 out 22316; cost $0.127. A DESIGN DRAFT for the designer's review: nothing here is built. -->

## Changes vs v1

- **Issue 1 (BLOCKER, map vs. guarantees):**
  - The guarantee line now matches the table: Elite is offered at L4, L6, L7 and L10. Rests are at L5, L9 and L11. The Mainframes at L3 and L8 meet the GDD's "layers 3–5" rule via L3. The "Elite in every layer 4–10" claim is dropped.
  - Totals are restated. The table has 30 base nodes (3+2+3+2+3+3+2+3+2+3+2+1+1 = 30) and 33 with all three Annexes. 11 layers offer a fight option (L1–L11), so a no-climb path has at most 13 fights, counting the mini-boss and boss.
  - §5 uses an explicit typical path with 5 normals, 2 Elites, 1 Rack, 3 non-fight nodes, the mini-boss and the boss. The path node count is 13, matching the layers.
- **Issue 2 (BLOCKER, climbs):**
  - **Step model:** the step model is rewritten. A climb is an edge through a transit node that adds 2 steps.
  - **Mutual exclusion:** climbs A and B are mutually exclusive on any path, because B's origin lies between A's origin and A's target. So there is at most one climb per path. The v1 "+2/+4 offsets" and "both used" claims were wrong and are removed.
  - **Arrival check:** the solver now validates every offered climb. The arrival node must be enterable at the exact arrival step, and a full path to the vault must still exist. A climb that fails validation is not drawn. The "sent back down" failure is deleted, so a climb can never trap you.
  - **Layers skipped:** skipped layers are corrected to 6 for A and 6–7 for B.
- **Issue 3 (MAJOR, enrage and budget):**
  - **R4 wins:** the Spotted enrage rider is dropped entirely, since R4 sets Normal to "off". Spotted Elites and Racks use the class default.
  - **Enforcer HP:** its 12 HP is now carved out of the host's HP, so host + Enforcer equals the authored R2 value (the sum is budgeted, not added).
  - **Turn overshoot:** recomputed to about +0.3 turn from the Blade alone.
- **Issue 4 (MAJOR, Blade):** the Blade is reframed as output reduction, not intake. The PARASITE fallback is stated honestly as a different rule (−50 % output), usable only until N8/N9.
- **Issue 5 (MAJOR, N4):**
  - N4 is a new system, so I claim no data-only path.
  - Spotted no longer needs N4 at all. N4 is only the foundation default.
- **Issue 6 (MAJOR, boss enrage formula):** the HQ now outputs only `starting_alert`. The enrage formula is removed, and the boss draft decides its use.
- **Issue 7 (MAJOR, Alert chains):**
  - Alert resets to 0 after a Warden fight, and the Warden fight adds no Alert.
  - Stall costs +1, and the retry floor is capped at 2.
  - Bay −1 now applies whenever the Bay is OPEN. In v1 the "dark side" condition was meaningless, because an eyed Bay is shuttered.
- **Issue 8 (MAJOR, systems tags):**
  - Node access is a derived overlay on `map_graph`, built on N16 plumbing, with no separate system. This is tagged and has a fallback.
  - The Alert floor is `NEW: hq_alert_floor`, a per-campaign field.
- **Issue 9 (NIT, art blade vs. Spotted):** §1 states that the art's blade line is the visual of the in-combat Blade, drawn across the wheel.
- **Issue 10 (NIT, fight count):** the §5 table is rebuilt from the typical path. It shows both L11 forks, Rack and Bay.
- **Issue 11 (NIT, no-heal path):** the solver now requires a full path to the vault that passes at least 2 OPEN rest nodes.
- **Additional fix:**
  - Terminal events that changed `step` are removed. Step-changing choices (Stall, Spoof, Cut the Power) are re-validated by the solver and disabled if they would leave the run unsolvable.
  - The mini-boss, boss and Warden are specified, and the L12/L13 beam rule is added.
- **Kept, because the critic marked them strong:** the pure `gaze(phase, step)` function, the spotted / shuttered / blocked split, and the Annex-per-Exploit design.

---

# Halcyon: HQ netrun draft

Working name for the run: **THE LONG WAY ROUND**. Working name for the boss: **the Panopticon boss** (designed in the boss draft). The mini-boss is the **Halcyon mini-boss** (designed in the mini-boss draft).

## 1. Concept & the named mechanic

**What the art shows.** A square stepped pyramid with a helix route orbiting it counter-clockwise, one tier per face. On top sits the eye turret. It throws a 90° gaze sector that turns 45° per step, against the climb. A blade line crosses the lit faces. A lighthouse beam passes through the city. Lit rooms go lockdown red. Climbs run straight up the outside of a face.

**As a game mechanic, the HQ is a stealth-timing climb against a rotating watcher.** You never fight the eye directly. You read where it will be and choose when to cross its light. The eye's visible parts map to fixed rules:

| Art element | Game rule |
|---|---|
| Gaze sector (90°) | Nodes inside it are **IN THE EYE**. Entering a fight node there is **SPOTTED**. |
| Lighthouse beam (the sector's centre line) | A node within ±4° of the centre line is **BLOCKED** while the beam holds it. |
| Blade line | Drawn across the lit faces on the map. In a Spotted fight the same line sweeps your wheel, one slice per turn (the Blade). |
| Lockdown red | The **Alert** meter at its cap of 5. A Warden fight is inserted before your next node. |

**Why no other HQ reads like it.** Every other HQ is spatial or economic: Meridian's rail and crane cycle, Solace's ladder, Orbital's doors. Here the map choice is a **timing** choice. There is no fixed safe route, because the safe route moves every step and is visible ahead of time. Nodes are not good or bad, only lit or dark. Which ones are lit is a pure function of how many nodes you have completed.

## 2. Structure

**Layers:** 12 route layers plus a vault layer (L13) that holds the boss.

**Nodes:** 2–3 per layer in the table, 30 base nodes in total. Each owned Exploit adds one Annex node (section 4), so a run has up to 33 nodes and up to 4 in a layer. A bay is a short run of rooms on one tier's face, with the layer's alternatives side by side.

**Mapping rule (art 8.4):** the game graph is assigned to slots in layer order, then node order. The landmark generates its slots on demand.
- Six segments: S, E, N, W, S, E, counter-clockwise from above, one per tier.
- A segment's tier gets as many bays as its layers.
- Tier width is **derived from the rooms it holds** (rooms × 23 BU pitch + margin), not from fixed widths. L12 is the sixth segment, and L13 is the vault above it.
- Each node's azimuth comes from its slot, so the eye test is a pure function of geometry the art already owns.

**Layer map** (the build seeds the exact mix; the rules in the notes hold):

| Layer | Tier / face | Nodes | Kinds |
|---|---|---|---|
| L1 | 1 / S | 3 | Router ×3 (GDD: layer 1 all Routers) |
| L2 | 1 / S | 2 (+Archive) | Router, Terminal |
| L3 | 1 / S | 3 | Router, Terminal, Mainframe. **Climb A origin** (any node) |
| L4 | 2 / E | 2 | Router, Elite Router. **Climb B origin** |
| L5 | 2 / E | 3 | Maintenance Bay, Router, Evidence Locker. **Climb B origin** |
| L6 | 3 / N | 3 | Rack (optional), Router, Elite Router |
| L7 | 3 / N | 2 (+Panel) | Elite Router, Router |
| L8 | 4 / W | 3 | Router, Control Room, Mainframe |
| L9 | 4 / W | 2 (+Leak) | Maintenance Bay, Router |
| L10 | 5 / S | 3 | Router, Elite Router, Router. **Climb A target** |
| L11 | 5 / S | 2 | Rack (elite-strength), Maintenance Bay |
| L12 | 6 / E | 1 | Antechamber: the Halcyon mini-boss. **Climb B target** |
| L13 | vault | 1 | The Panopticon boss |

**Counts:**
- 30 base nodes.
- 11 layers (L1–L11) offer a fight option, so a no-climb path has at most 11 + mini-boss + boss = 13 fights.
- Typical paths take 8 fights and 3 non-fight nodes before the Antechamber; see §5.

**Guarantees** (match the table):
- An Elite is offered at L4, L6, L7 and L10.
- Rests (Maintenance Bay) are at L5, L9 and L11.
- Mainframes are at L3 and L8.
- Racks are at L6 and L11. L11 is a fork between Rack and Bay.

**Edge rules** (seeded from stream `hq_graph`; no crossings):
- **Within a segment:** node i of an n-node layer links to the 1–2 nodes of the next layer whose bay position is nearest (scaled index), as a **gallery** link. Every node has at least one way in and one way out.
- **Segment end:** the link is a **corner stair** up to the next tier.
- **Ties:** every order is by node id, never dict order.

**Climbs** (the art's shortcut rule). At most one climb applies per path, because the two are mutually exclusive:
- **Climb A:** from any L3 node to the same-u node of L10. It skips L4–L9, which is 6 layers.
- **Climb B:** from an L4 or L5 node to the Antechamber at L12. It skips 7 layers from L4, or 6 layers from L5 (L11 is among them).
- B's origin lies between A's origin and A's target, so a path can't take both.
- Climb edges are drawn at graph build from `hq_graph`, but only if valid (3.1 solver). A run can offer zero, one or both. Intel shows which are offered.

## 3. Unique mechanics

### 3.1 The Gaze: IN THE EYE and the beam

**Rule.**
- `step` = map nodes completed in this run. A climb's transit node counts as 2 steps. A Warden fight counts as 0.
- Gaze centre azimuth = `45° × (phase + gaze_offset + step)`, clockwise. It turns against the spiral. `gaze_offset` is 0 unless a Stall or Spoof was taken.
- A node is **IN THE EYE** if its azimuth lies in `[centre − 45°, centre + 45°)`.
- A node within ±4° of the centre is **ON THE BEAM**.
- The gaze used for a node is the gaze at the step when it is entered: `gaze(phase, offset, step)`.

**Consequences:**
- **IN THE EYE, fight node (Router, Elite, Rack):**
  - It can be entered as **SPOTTED** (3.2).
  - Heat +1 and Alert +1.
- **IN THE EYE, non-fight node (Terminal, Mainframe, Maintenance Bay, Evidence Locker, Control Room):** **SHUTTERED**. It can't be entered. The Breach passive opens one per run (section 4).
- **Annex rooms** are never shuttered (they are an Exploit's building). They are still blocked by the beam.
- **ON THE BEAM:** **BLOCKED**, whatever the kind.
- **The Antechamber and the vault** are never Spotted. They are the single node of their layer, so the solver forbids the beam on them at any entry step.

**Trigger.** The gaze advances when a node completes, not per turn or per tick. The eye is therefore **not a clock on your thinking**.

**What the player sees.**
- The turret's gaze washes the lit faces.
- Rooms in the eye carry a red ring, an IN THE EYE chip and the eye badge. The beam room is lockdown red with the scan-line plane.
- An **eye dial** shows the next 3 sector centres (6 with Intel). A hover on any link shows the gaze on arrival, including for a climb.

**Counters.** Cross on the dark side, plan one layer ahead, use Annex rooms, or use a Control Room Stall (3.3).

**Fairness: the solver.** At graph build, for each of the 8 phases, a pure DP over the graph (30–33 nodes) checks:
1. A path L1 → L13 exists through enterable nodes (OPEN, or IN THE EYE fight nodes) using no climb, with steps computed from the real path.
2. That path set passes at least 2 OPEN rest nodes (L5, L9, L11), so a run can't lose all healing.
3. L12 and L13 are not on the beam at any entry step.
4. For each drawn climb, the arrival node at the exact arrival step is enterable (not on the beam, not shuttered).
5. A full path from that arrival to L13 exists with the shifted steps. Climb A arrives at L10 at step 5. Climb B from L4 arrives at L12 at step 6 and from L5 at step 7.

The lowest valid phase index is used. A climb that fails 4 or 5 is not drawn, so a climb can never trap you. If no phase passes 1–3, the graph is rebuilt with the next `hq_graph` draw.

**Gaze-altering choices.**
- Stall, Spoof and Cut the Power (sections 3.3 and 4) re-run the solver from the current node with the new offset (it takes `gaze_offset`).
- An option that would leave the run unsolvable is disabled, with the reason shown.
- Cut the Power only helps. While the eye sleeps for 3 steps nothing is IN THE EYE or blocked, and afterward the pure function resumes.

**Determinism.** The only randomness is the draw of `phase` and the graph, from named streams `hq_layout` and `hq_graph`, checkpointed at HQ start. Gaze and consequences are derived, never stored.

### 3.2 The Blade: SPOTTED as a fight modifier

A SPOTTED fight is the node's normal fight plus two data-driven riders. They apply to Router, Elite, Rack and Warden fights, never to the mini-boss or boss.

1. **Enforcer.** A fixed satellite (N13) docks on the slice of the enemy wheel that holds its biggest hit. It acts as a bodyguard (GDD 2.7).
   - It has 12 HP and a 2-slice mini-wheel: SHIM 3 and DEFRAG 3. These are flat enemy amounts × the tier damage factor (T4 ×2.2 = about 7 each).
   - **Budget:** the host's HP is reduced by 12 for the fight, so host + Enforcer equals the authored R2 value. The sum is what the band validator checks.
2. **The Blade.** At the start of each player turn the scan line crosses one of your slices. The scanned slot is `(turn − 1) mod 6`, by slot index in fixed order, never by tick.
   - That slice gets **TIER_DOWN ×1** for that turn's resolve (Perfect → Good, Good → WEAK). It is removed after the resolve.
   - It is visible before you commit, and the preview shows the scanned slot, so previews equal results.
   - It is an output reduction, not damage taken.

**Enrage:** none added. Spotted normals have no enrage (R4). Spotted Elites and Racks use the class default (turn 8).

**Question it asks:** which slice must be Perfect or Good this turn, and does the Blade fall on it? Answers that shorten the fight: land on the unscanned slice, spend a nudge to leave the scanned slot, or kill the Enforcer first.

**Counters:** Encrypt, Cleanse the scanned slice before the resolve, or use the fixed order to plan.

**Budget arithmetic** (R2, T4 normal 56–70 HP, mid 63):
- Reference damage is 18 per turn × 3.5 turns = 63. Host (63 − 12 = 51) + Enforcer 12 = 63, so the total is unchanged.
- The Blade costs output only when it lands on a landing slice: about 1 in 6 turns, losing 50 % on a Good landing. That is about 8 % of damage, so about +0.3 turn: 3.8 turns against the 3–4 target.

### 3.3 Alert and Lockdown

**Rule.** **Alert** is a run-level counter from 0 to 5. It starts at the campaign's `hq_alert_floor` (0–2).
- **+1** per Spotted fight, **+1** per climb, **+1** per Stall.
- **−1** at an OPEN Maintenance Bay (not one entered through the Breach passive).
- **Lockdown at Alert 5:** a **Warden fight** is inserted before the node you chose.
  - The Warden is elite-strength with the Spotted riders and counts 0 steps. After it you enter the chosen node, with the gaze unchanged.
  - It pays a Rack-sized reward (N18 row).
  - Alert resets to **0** afterward. The Warden fight adds no Alert, so Wardens can't chain.
- **Control Room** (an event node): its event offers **Stall**. The gaze steps 1 forward without moving you (`gaze_offset` +1) and Alert rises by 1. Use it to dodge an eyed bay one layer ahead.

**What the player sees.** A thin lockdown-red band rises up the pyramid's sides as Alert rises, reaching the cornice at 5.

**Output to the boss draft:** the single number `starting_alert` (0–5), shown before the vault door. The boss draft decides what it does. This draft sets no enrage rule.

**Counters.** Rest, avoid Spotted fights, spend Exploits.

### 3.4 The Climb

**Rule.** A climb edge leads to a **Climb node**, a transit node with no fight and no event. Entering it consumes 2 steps and Alert +1. You then arrive at the target node, and the gaze at that arrival is the gaze at `step + 2`.
- **Preview:** the Climb node always shows the arrival node's state, the gaze there and the path onward. Arrival is validated at build (3.1), so a climb is a plan and never a gamble.
- **A SPOTTED arrival** at a Router, Elite or Rack applies the normal Spotted riders and Alert +1.
- **Trade-off:** you skip 6–7 layers of rewards, rests and Racks. Climb B lands you in the Antechamber with no healing, so it trades rewards for speed.

**Determinism:** none beyond the graph draw.

## 4. Node kit

| Node | This HQ's twist | Type |
|---|---|---|
| **Router** | Halcyon normals, T4 budgets. Spotted adds the Enforcer and Blade. | Fight |
| **Elite Router** | Halcyon Elite (2 phases, R1). Spotted riders apply. Heat +1. | Fight |
| **Server Rack** | Elite-strength combat that banks Schematics on capture. L6 optional; L11 is the fork with the Bay. | Fight |
| **Terminal** | Eye-reading events (below). Shuttered when in the eye. | Event |
| **Mainframe** | Civic Concession shop, includes a heal item (+15 HP). Shuttered when in the eye. | Shop |
| **Maintenance Bay** | Heals 40 % max HP and Alert −1 (when OPEN). Shuttered when in the eye. | Rest |
| **Evidence Locker** | One Daemon or Firmware pick from 3. Shuttered when in the eye. | Cache |
| **Control Room** | Stall, or a free read of the next 6 gazes. Shuttered when in the eye. | Event |
| **Climb node** | See 3.4. | Transit |
| **Antechamber** | The Halcyon mini-boss. Never Spotted. | Mini-boss |
| **Vault** | The Panopticon boss. Never Spotted. | Boss |

**Terminal events** (each with two options, none changing `step`):
- "Camera 17 is looping": the next Spotted fight this run has no Blade.
- "A maintenance crew waves you through": Alert −1, or a free Firmware swap.
- Others come from the shared event pool.

**Exploit buildings (D5).** Each Exploit you own gives a **passive** inside the HQ and adds one **Annex** node, once per run, at a fixed layer:

| Exploit | Passive in the HQ | Annex room | Annex effect (once) |
|---|---|---|---|
| **Intel** (council minutes) | The eye dial shows 6 steps instead of 3. | **Archive**, +1 node at L2 | Reveals the kind and content of every node, plus the climbs offered. |
| **Breach** (emergency override) | One shuttered (not beam) node per run may be entered. | **Override Panel**, +1 node at L7 | **Cut the Power:** the eye sleeps for 3 steps. |
| **Virus** (open data leak) | Each Enforcer starts at half output. | **Open Leak**, +1 node at L9 | **Spoof:** shift the gaze 90° clockwise or counter-clockwise. |

- An Annex is an alternative node of its layer, so using it skips that layer's other options. It still advances `step` by 1.
- An Annex that isn't owned doesn't appear.
- `min_exploits_for_breach = 3` stays. Which three of the drawn Exploits are owned decides which Annexes exist.
- The boss's buffs and their Exploit counters (R7) are designed in the boss draft. This HQ adds no buff counter.

## 5. Pacing & difficulty curve

**Assumptions:** T4, operative about 55 HP, 18 reference damage per turn (R2). All numbers are placeholders pending the balance sim.

**Typical path:** L1 Router, L2 Router, L3 Mainframe, L4 Router, L5 Bay, L6 Elite, L7 Router, L8 Router, L9 Bay, L10 Elite, then **L11 forks**, then L12 mini-boss and L13 boss.
- That is 13 nodes: 5 normals, 2 Elites, 3 non-fight, 1 L11 node, the mini-boss and the boss.

| Piece | Count | Turns | Minutes | Expected HP loss |
|---|---|---|---|---|
| Normal fights | 5 | 3–4 | 2 each = 10 | ~7 each = 35 |
| Elites | 2 | 6–8 | 3.5 each = 7 | ~12 each = 24 |
| Spotted riders | ~3 fights | +0.3 turn | included | +3 each = 9 |
| Non-fight nodes (Mainframe, Bay, Bay) | 3 | n/a | 4 | heal |
| Antechamber (mini-boss) | 1 | 6–12 | 5 | ~16 |
| **L11 fork** | | | | |
| — Rack path | Rack | 6–8 | 3.5 | ~14 |
| — Rest path | Bay | n/a | 1 | heal |
| Boss | 1 | 12–20 | 8 | the boss draft |

**Totals:**
- **Rack path:** 37.5 minutes with the boss, about 29.5 before the vault.
- **Rest path:** 35 minutes with the boss, about 27 before the vault.
- This exceeds GDD's 15 minutes per netrun by design (D10).

**HP arithmetic before the boss:**
- **Loss, Rack path:** 35 + 24 + 9 + 16 + 14 = 98. **Healing:** 2 Bays × 40 % × 55 = 44, plus the Mainframe heal item of 15, so 59. Arrival: 55 + 59 − 98 = 16 HP, about 29 % of max.
- **Loss, Rest path:** 35 + 24 + 9 + 16 = 84. **Healing:** 3 Bays = 66, plus 15, so 81. Arrival is capped at max HP, about 45 HP after cap waste.
- **The fork:** the L11 choice is Schematics and a Rack's rewards against about 29 more HP at the boss. The sim target is half of ICE-0 players arriving at about 40 % HP on the Rack path. The levers are the Bay's heal % and the Spotted HP cost.

**Climb economics:** Climb A skips about 15 minutes and 50 HP of fights, but also 2 rests and a Rack. Climb B from L5 skips L6–L11 and lands you at the mini-boss without healing.

**Heat:** Router 0, Elite +1, Spotted fight +1, Rack per the GDD table. The typical run adds about 6–8 Heat (2 Elites, ~3 Spotted, ~2 for a Rack). A Warden fight (about 0.3 per run) is extra and carries Elite Heat.

## 6. Rewards

Beyond the boss (campaign victory on a breach with enough Exploits, per GDD 1.3):
- **Schematics** at each Rack, banked immediately.
- **"Clean Signal" bonus:** arrival at the vault with `starting_alert` 0–1 pays +20 Schematics. At 2–4 it pays +10 (an N18 row).
- **Warden fights** pay a Rack-sized reward.
- **Profile unlock:** a Daemon, "Blind Spot" (placeholder), for a clear with zero Spotted fights and no Lockdown. The Daemon's effect is a later pass.
- **Story:** the Halcyon story beat is delivered at the vault (GDD 8.4).
- **Unspent Cycles** convert to Schematics as normal.

## 7. Failure & retry

- **Death:** the operative is permanently lost with all unbanked loot. The campaign gains 10 + tier Heat (GDD 4.2). Banked Rack Schematics stay.
- **Carry-over:** each death of an HQ run raises `hq_alert_floor` by 1, capped at **2**. It resets on a win. The next attempt starts at that Alert. The route is still new every retry: only the number carries.
- **Retreat:** leaving the run follows GDD 4.5. Abandon run is a death.
- **Warden loss:** an ordinary death.
- **Raid interludes** can interrupt as normal. A raid does not change the gaze, because the gaze counts completed nodes, not time.
- **Retries** get a new `phase`, graph and Annex layout.

## 8. Systems needed

| System | Used for | Data-only fallback? |
|---|---|---|
| **NEW: HQ run layout (`HqRunData`)** | Layers, bays, tier sizing, segment faces, Annex nodes, climb edges, `hq_layout` and `hq_graph` streams, the phase solver | No. A fixed 13-layer authored graph is the fallback, but it loses the generator and the fairness solver. |
| **NEW: Eye rule (`EyeData` + RunState `step`, `alert`, `gaze_offset`)** | `gaze(phase, offset, step)`, the sector and beam tests, node access state, the solver with offsets | No. The gaze is a pure function with a validator. |
| **NEW: `hq_alert_floor`** | A per-campaign field, 0–2, that carries across HQ attempts | Fallback: drop the carry-over (starts at 0). |
| **Node access overlay** | Shuttered and blocked flags derived each step on `map_graph`, built on the N16 `map_edits` plumbing | Partial: a precomputed per-node flag set at map entry and refreshed on each node completion. |
| **N13** fixed satellites | The Enforcer | Yes: a normal satellite docked at combat start. |
| **N8 / N9** (TIER_DOWN) | The Blade | Partial. PARASITE ×1 (−50 % output) is a different rule. It is stronger on Good landings and has no effect on Perfect hooks. Use it only until N8/N9 land; the sim values differ. |
| **N16** `next_combat_overrides`, `starts_combat` | Spotted riders as combat overrides, the Warden insert, Control Room events | The rider set could be baked into elite variants if N16 is late. |
| **N18** reward table | Clean Signal bonus, Warden reward | Hard-coded rewards. |
| **N2, N3, N4** | Tier tables, phases and default enrage for Elites and boss | Foundation wave. N4 has no data-only path. |
| **N19** | Sim metrics: Spotted rate, Alert at the vault, turns per Spotted fight | Needed to tune. |

**Build order:**
1. The foundation wave (N1–N4, N13, N19).
2. The eye rule and solver as a standalone pure function with tests: the phase-validity and climb-arrival tests, and the gaze-altering re-validation.
3. `HqRunData` with the slot generator, wired into `map_graph`.
4. Node access overlay and Spotted overrides via N16 (or the elite-variant fallback).
5. The Annex nodes, Climb node and Control Room.
6. The Blade rider (PARASITE fallback first, TIER_DOWN when N8 / N9 land).
7. Reward rows and `hq_alert_floor`.
8. Sim sweeps.

## 9. Art hooks

Game state the art must read per frame:
- `step`, `phase` and `gaze_offset`, so the tools can compute the gaze azimuth and sector.
- Per node: `state` ∈ {open, in_eye, shuttered, blocked, walked, current, ahead, past}.
- A `beam_node` id (or none).
- `eye_asleep` with remaining steps (Cut the Power).
- `alert` (0–5) for the red band, and `lockdown` (bool).
- During a Spotted fight: `blade_slot` (0–5) and `blade_progress` (0..1 within the turn) for the sweeping scan line. This is the art blade line drawn across the wheel.
- `climb_progress` (0..1) with its two endpoints, and the arrival-state preview.
- Annex nodes with `owned` and `used`.
- The `consequence` word per node: `spotted` (shown as +1 enforcer) for fights, `shuttered` for non-fights, `blocked` for the beam.
- The dial's next-3 (or next-6) centres.
- At the vault door: `starting_alert`.

Pure visualisation, art-only: the sweep speeds, the reveal's beam-pass timing and the lighthouse's lens flash.

## 10. Q: open questions

- **Q:** Where should the effect of `starting_alert` on the boss live? This draft only outputs the number. Is that the right split with the boss draft?
- **Q:** Are Spotted fights too punishing at T4 (the Enforcer plus a Blade every turn)? Should the Blade apply only to Elites and Racks, leaving plain Enforcer-only for normals?
- **Q:** Is `hq_alert_floor` capped at 2 the right strength, given that every retry also gets a fresh route?
- **Q:** Should the pyramid scale its tiers to the generated graph (this draft), or should the generator cap layers per tier to fit the art's fixed dimensions?
- **Q:** Does the L12 mini-boss stay a separate gate, or does the boss draft want it folded into the vault as a phase?
