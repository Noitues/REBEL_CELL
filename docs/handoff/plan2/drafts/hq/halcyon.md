<!-- draft via Message Batches API, claude-sonnet-5-5, batch msgbatch_01HADBSF5pLwaHAq7nbABzZa, custom_id hq__halcyon; status ok; tokens in 16372 cache-write 0 cache-read 32007 out 20929; cost $0.124. A DESIGN DRAFT for the designer's review: nothing here is built. -->

# Halcyon: HQ netrun draft

Working name for the run: **THE LONG WAY ROUND**. Working name for the boss: **the Panopticon boss** (designed in the boss draft). The mini-boss is the **Halcyon mini-boss** (designed in the mini-boss draft).

## 1. Concept & the named mechanic

**What the art shows.** The art shows a square stepped pyramid with a helix route that orbits it counter-clockwise, one tier per face. On top sits the eye turret. It throws a 90° gaze sector that turns 45° per step, against the climb. A blade line crosses the lit faces. A lighthouse beam passes through the city. Lit rooms go lockdown red. Climbs run straight up the outside of a face.

**As a game mechanic, the HQ is a stealth-timing climb against a rotating watcher.** You never fight the eye directly. You read where it will be and choose when to cross its light. The consequence of each light is fixed by the eye's three visible parts:

| Art element | Game rule |
|---|---|
| Gaze sector (90°) | Nodes inside it are **IN THE EYE**. Entering one is **SPOTTED**. |
| Lighthouse beam (the sector's centre line) | A node on the beam line is **BLOCKED**. It can't be entered at all while the beam holds it. |
| Blade scan line | The in-combat form of SPOTTED. In a Spotted fight a scan line sweeps your wheel, one slice per turn. |
| Lockdown red | The **Alert** meter at its cap. The compound seals the next node and sends a Warden fight. |

**Why no other HQ reads like it.** Every other HQ is spatial or economic: Meridian's rail and crane cycle, Solace's ladder, Orbital's doors. Here the player's map choice is a **timing** choice. The map has no fixed safe route, because the safe route moves every layer and is visible ahead of time. Nodes are not good or bad. They are lit or dark, and which ones are lit is a pure function of how many nodes you have completed.

## 2. Structure

**Layers:** 12 route layers, plus a vault layer (L13) that holds the boss.

**Nodes:** 2–3 per layer, up to 4 when an owned Exploit adds its Annex (section 4). A route is a set of **bays**, one per layer. A bay is a short run of rooms on one tier's face, and the layer's alternatives sit side by side in it.

**Mapping rule (art 8.4):** the game graph is assigned to slots in layer order, then node order. The landmark generates its slots on demand.
- Six segments: S, E, N, W, S, E. One segment per tier, counter-clockwise from above.
- A segment's tier gets as many bays as its layers.
- Tier width is **derived from the rooms it must hold** (rooms × 23 BU pitch + margin). It is not the fixed 73 / 61.5 / … numbers. Q: whether the podium scales to match.
- Tier 6 is the vault, so the segment count is 6 plus the vault.

**Layer map** (kinds are defaults; the build seeds the exact mix, but the rules in the notes hold):

| Layer | Tier / face | Nodes | Kinds |
|---|---|---|---|
| L1 | 1 / S | 3 | Router ×3 (GDD: layer 1 all Routers) |
| L2 | 1 / S | 2 (+Archive) | Router, Terminal |
| L3 | 1 / S | 3 | Router, Terminal, Mainframe. **Climb origin A** (any node) |
| L4 | 2 / E | 2 | Router, Elite Router. **Climb origin B** |
| L5 | 2 / E | 3 | Maintenance Bay, Router, Evidence Locker. **Climb origin B** |
| L6 | 3 / N | 3 | Rack (optional), Router, Elite |
| L7 | 3 / N | 2 (+Panel) | Elite, Router |
| L8 | 4 / W | 3 | Router, Control Room, Mainframe |
| L9 | 4 / W | 2 (+Leak) | Maintenance Bay, Router |
| L10 | 5 / S | 3 | Router, Elite, Router. **Climb target A** |
| L11 | 5 / S | 2 | Rack (elite-strength), Maintenance Bay |
| L12 | 6 / E | 1 | Antechamber: the Halcyon mini-boss. **Climb target B** |
| L13 | vault | 1 | The Panopticon boss |

Total: 30 nodes, 13 fights at most on a long path.

**Edge rules** (seeded from stream `hq_graph`; no crossings):
- **Within a segment:** node i of an n-node layer links to the 1–2 nodes of the next layer whose bay position is nearest (scaled index), as a **gallery** link. Every node has at least one way in and one way out.
- **Segment end:** the link is a **corner stair** up to the next tier.
- **Guarantees:**
  - A Mainframe sits in layers 3–5 and an Elite in every layer 4–10 (GDD 4.2, adapted).
  - Rests (Maintenance Bay) appear at L5, L9 and L11.
  - A Rack is at L6, and at L11 as an alternative to a Rest.
- **Climbs** (the art's shortcut rule, same u one lap up): at most 2 exist per run, one per face that carries two segments.
  - **Climb A:** a node of L3 to the same-u node of L10 (S face, tier 1 → tier 5). It skips 6 layers.
  - **Climb B:** a node of L4 or L5 to the Antechamber at L12 (E face, tier 2 → tier 6). It skips 6 layers.
  - Climb edges are drawn at graph build from stream `hq_graph`. A run offers both, or one, never zero (hint: Intel shows the unused one).
  - At most 2 climbs are used in a run.

**Ties:** every order is by node id, never dict order.

## 3. Unique mechanics

### 3.1 The Gaze: IN THE EYE and the beam

**Rule.**
- `step` = nodes completed in this run. A climb adds 2 steps instead of 1.
- Gaze centre azimuth = `45° × (phase + step)`, clockwise. It turns against the spiral, so it closes on the operative quickly, about 90° of relative motion per layer.
- A node is **IN THE EYE** if its azimuth lies in `[centre − 45°, centre + 45°)`.
- A node within ±4° of the centre is **ON THE BEAM** (lockdown red).

**Consequences:**
- **IN THE EYE, fight node (Router, Elite, Rack):**
  - It can be entered as **SPOTTED**. Spotted fights follow 3.2.
  - Heat +1 per Spotted fight.
  - Alert +1.
- **IN THE EYE, non-fight node (Terminal, Mainframe, Maintenance Bay, Evidence Locker, Control Room):**
  - It is **shuttered**. It can't be entered, and a Breach passive can open one per run (section 4).
  - You may use it only on the dark side.
- **ON THE BEAM:** **BLOCKED**, whatever its kind. Nothing enters it.

**Per-layer trigger.** The sector advances when a node is completed, not per turn or per tick. The eye is therefore **not a clock on your thinking**. It is a pure state function: `gaze(phase, step)`.

**What the player sees.**
- The turret's gaze washes the lit faces.
- Rooms in the eye carry a red ring, the IN THE EYE chip and the eye badge. The beam room is lockdown red with the scan-line plane.
- An **eye dial** shows the next 3 sector centres (**next 6** with Intel). A hover on any link shows what the gaze will be on arrival.

**Counters:**
- Cross the eye's dark side. The gaze closes on you quickly, so look at what it will cover next layer.
- Use Exploits and Annex rooms (section 4).
- A Control Room can **Stall** (3.3).

**Fairness guarantee.** At graph build, a phase solver tries the 8 phases. A phase is valid only if every layer has at least one unblocked, unshuttered option on the climb-free path **and** with each possible climb offset (+2, +4). It picks the lowest valid phase index. Since the gaze is a pure function of `(phase, step)`, the solver is exact. If none of the 8 is valid (rare), the graph is rebuilt with the next `hq_graph` draw.

**Determinism.** The only randomness is the one draw of `phase` plus the graph, from the named streams `hq_layout` and `hq_graph`. Both are saved at a checkpoint at HQ start. Gaze and consequences are derived, never stored.

### 3.2 The Blade: SPOTTED as a fight modifier

A SPOTTED fight is the normal fight for that node, plus these three data-driven riders. The enemy's HP is unchanged and still inside the R2 band for its tier.

1. **Enforcer.** A fixed satellite (N13) docks on one slice of the enemy wheel. It acts as a bodyguard (GDD 2.7).
   - It has 12 HP and one 2-slice mini-wheel: SHIM 3 and DEFRAG 3. The numbers are flat enemy amounts × the tier damage factor (T4: ×2.2).
   - It is placed on the slice that holds the enemy's biggest hit.
2. **The Blade.** At the start of each player turn the scan line crosses **one of your slices**, in fixed order by slot index: turn 1 slot 0, turn 2 slot 1, and so on, wrapping at 6.
   - That slice reads **TIER_DOWN ×1** for that turn's resolve (Perfect → Good, Good → WEAK).
   - It is visible before you commit. The preview shows the scanned slot, so previews equal results.
   - Order is by slot index, never by tick, so it isn't random after a respin. Because of the order, you can plan around it.
3. **Early enrage.** The class enrage (R4) turns on at turn 5 for normals, 4 for Elites and Racks, repeating every 5 as usual. Normal fights otherwise have no enrage.

**Question it asks:** which slice do you need Perfect this turn, and does the blade fall on it? Answers that shorten the fight: bank a Perfect on the unscanned slice, spend a nudge to move your pointer off the scanned slot, or kill the Enforcer first.

**Counters:**
- Encrypt (ENCRYPTED absorbs a status applied to that slice).
- Cleanse the scanned slice before the resolve.
- Standing on the unscanned slot, since the blade order is fixed.

**Budget arithmetic** (R2, T4 normal 56–70 HP):
- The reference player deals about 18 per turn over 3.5 turns, which is about 63 damage.
- The Enforcer's 12 HP are damage needed only when a needle lands on its slice.
- That adds about 0.7 turns to the fight. So 4.2 turns against 3–4, which is the intended small overshoot for a Spotted fight.

### 3.3 Alert and Lockdown

**Rule.**
- **Alert** is a run-level counter from 0 to 5. It starts at 0. It is +1 per Spotted fight, +1 per climb, and +2 if you choose a **Stall** (below).
- It is −1 at a Maintenance Bay if you rest in the eye's dark side.
- **Lockdown at Alert 5:** the next node you move into is replaced by a **Warden fight**.
  - It is elite-strength with the Spotted riders and the eye parked on your current face.
  - It must be fought. It pays a Rack-sized reward (6.), and Alert resets to 2.
- **Control Room (a node kind):** its event offers **Stall**.
  - The gaze steps 1 forward now, without moving you. You pay 2 Alert.
  - Use it to dodge an eyed bay one layer ahead.

**What the player sees.** A thin lockdown-red band rises up the pyramid's sides as Alert rises. It reaches the cornice at 5. The scan-line plane covers the room.

**Boss tie-in.** Alert on arrival at the vault shifts the boss's enrage (R4):
- Alert 0–1: default enrage (turn 10).
- Alert 2–4: enrage turn is 10 − (Alert − 1), minimum 6.
- Alert is shown before the vault door. The boss draft reads this one number, `starting_alert`.

**Counters.** Rest in the dark, avoid Spotted fights, and spend Exploits.

### 3.4 The Climb

**Rule.** A climb edge leads to a **Climb node**, which is a puzzle node, not a fight. The gaze steps 2 forward over the climb.
- Alert +1.
- At the end, the operative arrives at the target node. Arrival counts as entering it, so the gaze at `step + 2` is used for that arrival check.
- If the target room is in the eye at arrival, you are SPOTTED there as usual. If it is ON THE BEAM, the climb **fails**: you are sent back down to the Climb node's start with the loss of the climb, and Alert +1.
- Climb nodes always show the arrival-time gaze, so the check is a plan, not a gamble.
- You skip 6 layers of rewards and Racks. Climb B lands you at the mini-boss without healing, so it is a trade of rewards for speed.

**Determinism:** none beyond the graph draw.

## 4. Node kit

| Node | This HQ's twist | Type |
|---|---|---|
| **Router** (fight) | Halcyon normals, T4 budgets. Spotted adds the three riders. | Fight |
| **Elite Router** | Halcyon Elite (2 phases, R1). Spotted riders apply. Heat +1 as normal. | Fight |
| **Server Rack** | Elite-strength combat that banks Schematics on capture. Spotted adds riders. L6 optional, L11 an alternative to a Rest. | Fight |
| **Terminal** (event) | Events that read the eye. See below. Shuttered when in the eye. | Puzzle |
| **Mainframe** (shop) | Civic Concession. Shuttered when in the eye. The prices are normal. | Shop |
| **Maintenance Bay** (rest) | Heals 35% max HP. Shuttered when in the eye. Resting on the dark side gives Alert −1. | Rest |
| **Evidence Locker** (cache) | One Daemon or Firmware pick from a pool of 3. Shuttered when in the eye. | Cache |
| **Control Room** | Stall (3.3), or a free Alert read. | Puzzle |
| **Climb node** | See 3.4. | Puzzle |
| **Antechamber** | The Halcyon mini-boss. | Mini-boss |
| **Vault** | The Panopticon boss. | Boss |

**Terminal events** (a few examples, each with two options): "Camera 17 is looping" (gain a nudge; the eye is not shortened), "A maintenance crew waves you through" (step skip: the gaze does not advance for this node). Others come from the shared event pool.

**Exploit buildings (D5).** Each Exploit you own gives a **passive** inside the HQ and adds one **Annex** node, once per run, at a fixed layer:

| Exploit | Passive in the HQ | Annex room | Annex effect (once) |
|---|---|---|---|
| **Intel** (council minutes) | The eye dial shows 6 steps instead of 3. | **Archive**, +1 node at L2 | Reveals the kind and content of every node in the run, plus the unused climb. |
| **Breach** (emergency override) | One shuttered (not beam) node per run may be entered. | **Override Panel**, +1 node at L7 | **Cut the Power:** the eye sleeps. No sector and no beam for 3 steps. |
| **Virus** (open data leak) | The Enforcer satellite starts at half output. | **Open Leak**, +1 node at L9 | **Spoof:** shift the gaze 90° clockwise or counter-clockwise, your choice. |

- An Annex that isn't owned simply doesn't appear. A run with all 3 has 3 more nodes, up to 4 in a layer.
- `min_exploits_for_breach = 3` stays. Which three of the drawn Exploits are owned decides which Annexes exist.
- The boss's buffs and their Exploit counters (R7) are designed in the boss draft. This HQ adds no buff counter.

## 5. Pacing & difficulty curve

**Assumptions:** T4, operative around 55 HP, 18 reference damage per turn (R2).

| Piece | Count (typical path) | Turns | Minutes | Expected HP loss |
|---|---|---|---|---|
| Normal fights | 5 | 3–4 | 2 each = 10 | ~7 each = 35 |
| Elites | 2 | 6–8 | 3.5 each = 7 | ~12 each = 24 |
| Rack | 1 | 6–8 | 3.5 | ~14 |
| Spotted riders | ~3 fights | +0.7 turn | included | +3 each = 9 |
| Events, shop, cache, rests, Control Room | 5 | n/a | 6 | n/a |
| Antechamber (mini-boss) | 1 | 6–12 | 5 | ~16 |
| Boss | 1 | 12–20 | 8 | the boss draft |

**Total:** about 40 minutes with the boss, around 31 before the vault. This exceeds GDD 15 minutes per netrun by design (D10).

**HP loss before the vault:** about 98 against a budget of 55 HP plus 2 or 3 rests (35% of 55 is about 19 each, so +38 to +57) plus Rack and shop healing. A player taking 2 rests ends around 0–15 HP before the boss at average play. This is tight but deliberate. The sim should aim for about half of ICE-0 players reaching the boss at 40% HP. Placeholders until the balance sim.

**Climb economics:** a climb skips about 6 layers, which is about 17 minutes and 55 HP of fights, but also 2 rests and a Rack. A good player takes it only if short on time or strong.

**Heat:** Router 0, Elite +1, Spotted fight +1, Rack per the GDD table. The expected HQ run adds about 6–8 Heat.

## 6. Rewards

Beyond the boss (campaign victory on a breach with enough Exploits, as GDD 1.3):
- **Schematics** at each Rack, banked immediately.
- **"Clean Signal" bonus:** a clear at Alert 0–1 on arrival at the vault pays +20 Schematics. At 2–4 it pays +10. This is also an N18 row.
- **Lockdown fights** pay a Rack-sized reward (the Warden reward list).
- **Profile unlock:** a Daemon, "Blind Spot" (placeholder), unlocked for a Spotted-free clear (zero Spotted fights, no Lockdown). The Daemon's effect is a later pass.
- **Story:** the Halcyon story beat is delivered at the vault, per GDD 8.4.
- **Unspent Cycles** convert to Schematics as normal.

## 7. Failure & retry

- **Death:** the operative is permanently lost with all unbanked loot. The campaign gains 10 + tier Heat (GDD 4.2). Banked Rack Schematics stay.
- **Carry-over:** a dead run leaves an **Alert floor**: the next HQ attempt starts at Alert 1 per prior death, capped at 3. It resets on a win. This is the Panopticon remembering you. It also nudges the player toward a different approach rather than a rerun, since the route differs every game (art Q2).
- **Retreat:** leaving the run follows GDD 4.5. Abandon run is a death.
- **Lockdown loss:** losing the Warden fight is an ordinary death.
- **Raid interludes** can interrupt as normal. A raid does not change the gaze, because the gaze counts completed nodes, not time.
- **Retries** get a new `phase`, a new graph and a new Annex layout, so a retry is a fresh route, not a memorised one.

## 8. Systems needed

| System | Used for | Data-only fallback? |
|---|---|---|
| **NEW: HQ run layout (`HqRunData`)** | Layers, bays, tier sizing, segment faces, Annex nodes, climb edges, `hq_layout` and `hq_graph` streams, the phase solver | No. This is the core of the draft. A fixed 13-layer authored graph is the fallback, but it loses the generator. |
| **NEW: Eye rule (`EyeData` + RunState `step`, `alert`)** | `gaze(phase, step)`, the sector test, the beam test, node access (OPEN / SHUTTERED / BLOCKED) | No. The gaze is a pure function with a validator. |
| **NEW: node access rules** | Shuttered and blocked nodes on `map_graph` | Partial: a non-enterable flag per node, set at map entry. |
| **N13** fixed satellites | The Enforcer | Yes: a normal satellite that happens to be an enemy-docked bodyguard. |
| **N8 / N9** (TIER_DOWN status) | The Blade | Yes: use the existing PARASITE (halves output) on the scanned slice, which reads the same on a single turn. |
| **N4** enrage | Early enrage in Spotted fights, and the boss's enrage shift | Data-only if class defaults exist. |
| **N16** run-level `next_combat_overrides`, `EventChoiceData.starts_combat`, `map_edits` | Spotted riders as overrides; Control Room Stall; the Warden fight at Lockdown; Climb nodes | The rider set could be baked into elite variants if N16 is late. |
| **N18** reward table | Clean Signal bonus, Lockdown reward | Hard-coded rewards as the fallback. |
| **N2, N3** | Tier tables and phases for the Elites and boss | Already in the foundation wave. |
| **N19** | Sim metrics: Spotted rate, Alert at the vault, turns per Spotted fight | Needed to tune. |

**Build order:**
1. The foundation wave (N1–N4, N13, N19).
2. The eye rule and its solver as a standalone pure function with tests (the phase-validity test).
3. `HqRunData` with the slot generator, wired into `map_graph`.
4. The node-access rules and Spotted overrides via N16 (or the elite-variant fallback).
5. The Annex nodes and the Climb node.
6. The Blade rider (PARASITE fallback first, TIER_DOWN when N8 / N9 land).
7. The reward rows and the Alert floor.
8. Sim sweeps.

## 9. Art hooks

Game state the art must read per frame:
- `step` (int) and `phase`, so the tools can compute the gaze azimuth (deg) and sector.
- Per node: `state` ∈ {open, in_eye, shuttered, blocked, walked, current, ahead, past}.
- A `beam_node` id (or none).
- `eye_asleep` (for Cut the Power) with remaining steps.
- `alert` (0–5) for the red band on the pyramid's sides, and `lockdown` (bool).
- During a Spotted fight: `blade_slot` (0–5) and `blade_progress` (0..1 within the turn) for the sweeping scan line.
- `climb_progress` (0..1) with the two endpoints.
- Annex nodes with `owned` and `used`.
- The `consequence` word: `spotted` (shown as +1 enforcer) for fights, `shuttered` for non-fights, `blocked` for the beam.
- The dial's next-3 (or next-6) centres.
- At the vault door: `starting_alert`.

Pure visualisation: the sweep speeds, the reveal's beam-pass timing, and the lighthouse's lens flash. They stay art-only.

## 10. Q: open questions

- **Q:** Should the gaze advance per completed node (this draft) or per layer travelled? With climbs they differ. The first is simpler to preview and to solve.
- **Q:** Are SPOTTED fights too punishing at T4 (a scan blow every turn plus early enrage)? Or is the Blade better only on Elites, with plain Enforcer-only for normals?
- **Q:** Is the Alert floor on retry (Alert 1 per death) too harsh or too soft?
- **Q:** Should climbs be limited to one per run to keep long routes meaningful?
- **Q:** Should the pyramid scale its tiers to the generated graph (this draft), or should the generator cap layers per tier to fit the art's fixed dimensions?
- **Q:** Does the mini-boss at L12 stay a separate gate, or does the boss draft want it folded into the vault as a phase?
