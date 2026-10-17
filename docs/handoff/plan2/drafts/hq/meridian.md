<!-- draft via Message Batches API, claude-sonnet-5-5, batch msgbatch_01HADBSF5pLwaHAq7nbABzZa, custom_id hq__meridian; status ok; tokens in 13487 cache-write 0 cache-read 32007 out 39320; cost $0.213. A DESIGN DRAFT for the designer's review: nothing here is built. -->

# Meridian: HQ netrun draft

Working name: **THE DOCK CLOCK**, a netrun through the Gatehouse Gantry. The boss is the Meridian boss ("the Manifest"). I refer to it by that working name only.

## 1. Concept & the named mechanic

**What the art shows (v3):**
- A Π gantry crane built as a castle gatehouse stands over a container-walled yard.
- Containers shuttle between the wall and the train.
- The gantry rolls N-S on the wall runways. The keep, which is the trolley, rides the span E-W with the server in its crown.
- Trucks sit on three sides. The freight line leaves by the north gate.
- MANIFEST CONTROL is the named building.

**As a game mechanic.** The HQ is a map whose connections are driven by a clock. Every layer is one beat of the yard clock, and the clock moves three things on a fixed, visible timetable:
1. **Dock cycle.** Every other beat the shuttle containers swap between the wall and the train, and the train arrives or departs. This rewires which nodes connect to which, and it can remove a node (the Rack car leaves with the train).
2. **The Reach.** The crane's hook visits one sector per beat: W wall, N rail, E wall, yard. Fights in the hooked sector are *Hoisted*: more dangerous, better loot.
3. **The trolley.** The keep sits where the Reach is. The stair under it at layer 11 is the direct lift to the boss. Missing it costs you RAM.

You can read all three ahead of time. The skill is routing through a schedule, not luck. You also get two ways to shift the schedule: **Dwell**, and the MANIFEST CONTROL building.

**Why it can't be mistaken for another HQ.**
- Solace is a ladder of rooms (UP / ACROSS).
- Halcyon is an eye that retargets.
- Orbital is doors and a rocket.
- REBEL_CELL is a window sequence.
- Meridian is the only one whose **map changes shape on a timetable**. Pre-planning against the timetable is the whole identity.

## 2. Structure

**12 layers** (11 route layers plus the boss), 36 nodes, 2-4 nodes per layer. The layout generator runs once per HQ launch and draws from the `map` and `hq_manifest` streams (§3). The route differs every game: node types and the schedule are drawn per run, and the slot geometry is generated on demand (art 8.4 rule 5).

### Layer map (default phase, H = 0)

```
ACT I  THE GATE        W        S         E            ground, 3 gate sides
 L1                  [Rtr]    [Rtr]     [Rtr]          all Routers (GDD 4.2)
 L2                  [Evt]    [Rtr]     [Rtr]          W = truck box
 L3                  [Rtr]  [MANIFEST   [Rtr]          S = Intel building
                              CONTROL]
ACT II THE WALL & THE LINE   order of the four slots shifts with the shuttle
 L4  away  Reach W   OUT[Rtr*] SH@wall[Shop*] YARD[Rtr] RAIL[Siding: Repair/Dwell]
 L5  away  Reach N   OUT[Elite] SH@wall[Cache] YARD[Rtr] RAIL[Siding: Dwell only]
 L6  train Reach E   OUT[Rtr] YARD[Rtr] SH@train[Evt] RAIL[RACK car]
 L7  train Reach Yd  OUT[Rtr] YARD[Elite*] SH@train[Evt] RAIL[CUSTOMS GATE]
ACT III THE LEGS
 L8  away  Reach W   LegW[Rtr*]            LegE[Rtr]
 L9  away  Reach N   LegW[Elite]  CAB[SWITCHYARD]  LegE[Elite]
ACT IV THE SPAN & THE KEEP
 L10 train Reach E   SpanW[Rtr]  SpanC[Evt]  SpanE[Rtr*]   (+ EXP landing, see below)
 L11 train Reach Yd  StairW / StairC / StairE = {Rest, Router, Shop} shuffled
 L12                 CROWN: the Meridian boss
```

`*` = Hoisted at this phase. "Rtr" means a Router (normal fight). "Evt" means a Terminal event.

### Edge rules

Edges are rules applied to slots, not a hand-drawn list.

- **Act I (L1 to L3):** a node connects to the next layer's same column and the adjacent columns. W and E are not adjacent, so a W node reaches W and S.
- **L3 → L4:**
  - W3 → OUT, SH
  - S3 → SH, YARD
  - E3 → YARD, RAIL
- **Act II (L4 to L7).** Every layer has the same four slots, and their order depends on the shuttle:
  - Shuttle on the wall: `[OUT, SH, YARD, RAIL]`
  - Shuttle on the train: `[OUT, YARD, SH, RAIL]`
  - A node at index i connects to indices i-1, i and i+1 of the next layer, using the next layer's own order. So the shuttle's side changes who can reach it. The wall shuttle is reachable from OUT and YARD. The train shuttle is reachable from YARD and RAIL.
- **L7 → L8:** indices 1-2 go to LegW and indices 3-4 go to LegE, and indices 2-3 reach both.
- **Acts III and IV:** W reaches W and C, C reaches all, E reaches C and E. Every L11 node connects to the Crown.
- **Express landing (needs the Breach building, §4):** CUSTOMS GATE (L7 RAIL) → EXP10, which is only available if the train is present at L7.

### Mapping onto the landmark's slots

The slots come from the art doc's slot types:

| Landmark slot | Map use |
|---|---|
| Gatehouse chamber (W, S, E) | L1 |
| Truck box, bay lanes | L2 |
| Wall outer face and inner face | OUT (L4-L7) and YARD |
| Corner towers (S) | L3 side nodes |
| Train car (cut-open carriage) | RAIL and SH@train |
| Gantry leg floors | L8-L9 |
| Span gallery windows | L10 |
| Keep crown | L12 |

The L11 stairs sit on the keep's turret stairs.

Slots are generated on demand for the graph the game sends. Nothing here depends on a fixed slot count.

## 3. Unique mechanics

All four rules read from one state, `hq_clock`: `{layer, H, p0, reach_order}`. They are a pure function of that state, with no hidden state.

**The clock**
- **Time T = layer + H.**
- **H is the dwell offset**, starting at 0 and bounded to [-1, 3].
- **P = floor((T + p0) / 2).** P parity gives the dock phase.
- **Train present** when P is odd. Away when P is even.
- **Reach sector** = `reach_order[T mod 4]`, with the default order W, N, E, Yard.

### 3.1 Dock cycle (the named mechanic)

- **Rule.** Every other beat (P changes) the train arrives or leaves, and the shuttle container swaps between the wall slot and the train slot.
  - **Train-side content exists only while the train is present.** The RAIL slot is a **Car** (fight, or the Rack at L6) while the train is present and a **Siding** (rest) while it is away.
  - **The shuttle moves.** It is at the wall slot when the train is away and at the train slot when the train is present. Its cargo goes with it. Its edges follow the index rule in §2, so each swap rewires the map.
- **Trigger.** Evaluated for each layer as `(layer + H)`. In the default seed the swaps fall on entering L2, L4, L6, L8 and L10: train away at L4-L5 and L8-L9, present at L6-L7 and L10-L11.
- **What the player sees.**
  - A clock chip: `T 5 · swap in 1`.
  - Every shuttle drawn with a ghost at its other slot.
  - The train's arrival and departure drawn on the freight line.
  - Edges drawn per the current phase.
  - Hovering the Dwell button previews the redrawn map at H+1 (a preview, not a commit).
- **Combat tags.** Fights on a lane carry a tag (the N16 `combat_overrides`):
  - **Wall (OUT):** the enemy starts with SHIELD = 10 % of its max HP (an R5 PERCENT amount).
  - **Car (RAIL):** the "train departs" timer. Enrage starts at turn 4 instead of off (R4, EnrageData start 4, every 3, +25 %).
  - **Yard:** no tag.
- **Counters.** Dwell (below), the MANIFEST CONTROL amend, and routing around the swap.
- **Determinism.**
  - Phase is a pure function of (layer, H, p0).
  - `p0 ∈ {0, 1}` is drawn once from the `hq_manifest` stream at launch.
  - The stream is checkpointed with the run, so reloading never rerolls it.

**Dwell.** At a Siding, instead of Repair you may Dwell.
- It costs one beat and +2 Heat. It sets H += 1, which shifts every later layer's phase, sector and trolley stop.
- It is allowed at most twice per HQ run.
- It also changes node types. A RAIL slot that was a Siding becomes a Car if the train is now present, and the Rack car **departs** if the shifted L6 falls on an away phase. Dwell can therefore cost you the Rack. Intel shows this in the preview.
- It is the player's one tool for steering the clock. It is limited because it is paid in Heat and in the Rack risk.

### 3.2 The Reach (the crane's hook)

- **Rule.** One sector is hooked per beat. A fight node in it is **Hoisted**.
  - Enemy pointers ORBIT 1 tick per turn (existing PointerBehavior.ORBIT, applied via `combat_overrides`).
  - In exchange, the node pays +50 % Cycles and one extra Firmware choice.
  - Non-fight nodes are unaffected.
- **Which nodes are in which sector.** Sides are assigned per slot in data:
  - Act I: W, Yard, E.
  - OUT alternates W / E by layer (L4 W, L5 E, L6 W, L7 E).
  - RAIL and SH@train are N. SH@wall takes OUT's side that layer. YARD is the Yard.
  - Legs are W and E, the CAB is N, SpanW / SpanC / SpanE are W / Yard / E.
  - Stairs are W / Yard / E.
- **Seeded variation.** `reach_order` is a permutation of {W, N, E, Yard}, drawn from `hq_manifest`. The default order W, N, E, Yard is only the example in §2.
- **What the player sees.** A hook marker on the sector that the hoisted layer will use. The Hoisted nodes are lit with a crane glow, and the gantry/trolley sits over the sector in the scene.
- **Counters.** Step around it, or take it on purpose. It is the risk-reward dial for each layer. Because it is visible, there are no surprises.
- **Determinism.** Pure function of T and the drawn order. No RNG at play time.

### 3.3 The trolley and Direct Lift

- **Rule.** The keep rides the span, so it sits where the Reach is. At L11 the stair under the trolley (W, C or E) is the **Direct Lift**:
  - Direct Lift: the boss fight starts with +2 RAM and your first card costs 0.
  - Any other stair: the fight starts with -2 RAM. That is a 4 RAM swing, about one nudge plus one card.
- **Mapping.** Reach sector W → StairW, E → StairE, N and Yard → StairC. The default seed ends on the Yard, so StairC.
- **The puzzle.** Stair types (Rest, Router, Shop) are shuffled each run, so the free Rest stair may or may not be the Direct Lift stair. Choosing it means taking the missing-lift penalty in exchange for the heal.
- **What the player sees.** The trolley stop for L11 is visible from L9 onward (and from the start with Intel). The keep draws its parked position and a lit lift shaft on the matching stair.
- **Counters.** Dwell and MANIFEST CONTROL shift T. The Switchyard rewrites the order.
- **Determinism.** Pure function of T and `reach_order`.

### 3.4 Railhead: the Express and the north gate

- **Rule.** The freight line leaves north. With the Breach building (§4) you can board the train at L7 (train present only) and ride the line to the span, landing on EXP10 and skipping L8-L9 (the two legs layers, which hold the elites).
  - **Cost:** +4 Heat and a forced Hoisted elite fight at EXP10.
  - **Reward for skipping:** two fewer fights and a shorter run.
  - **Cost of skipping:** you miss the leg elites' rewards and the CAB.
- **What the player sees.** The train leaves the north gate lit when you board. An Express edge is drawn from the CUSTOMS GATE to the span.
- **Determinism.** The edge exists if the node is owned and the phase is right at L7. The forced elite is drawn from the `map` stream at generation.

## 4. Node kit

- **Router (normal fight).** A T4 Meridian normal, 1 phase, HP in the R2 band (56-70). Tags per §3.1 and §3.2.
- **Elite.** Two phases (R1), HP 112-144 at T4. Placed at L5 (Wall Garrison), L7 (Yard Foreman) and L9 (one per leg). Heat +1 per GDD. A Hoisted elite is the hardest regular node.
- **Terminal (event).** Truck box, train box and reading room events. The events keep the Meridian voice. With N16, some events can alter the schedule (for example, "reschedule: H ±1").
- **Mainframe (shop).** L4 Wall Stock (shuttle cargo, at the wall); a Shop is also one of the L11 stair types. Shop stock is not changed by Hoist. A shuttle shop is reachable only while the shuttle is on your side.
- **Cache.** L5 shuttle cargo, a Firmware offer.
- **Server Rack.** One optional Rack, L6 RAIL. It is on the train: if the train is away at L6 (after a Dwell) the car is gone and the slot is a Siding. It is elite-strength and banks its Schematics on capture (GDD 4.2).
- **Rest (Siding).** Repair heals 25 % max HP. Dwell shifts the clock. At L5 the Siding is Dwell only. The pre-boss Rest stair heals 40 %.
- **Puzzle nodes.** The three buildings are fights-or-puzzles by Exploit (D5). Each is a node only if the Exploit is owned. Otherwise the slot is a plain Router:

| Building | Exploit (placeholder pairing) | What it does here |
|---|---|---|
| **MANIFEST CONTROL** (L3 S) | Intel | Shows the whole timetable from the start. One free **Amend**: H ±1. (Free, once.) |
| **CUSTOMS GATE** (L7 RAIL) | Breach | Opens the rail gate: the Express (§3.4). |
| **SWITCHYARD** (L9 CAB) | Virus | **Reroute:** swap two sectors in `reach_order` (this also moves the trolley stop at L11). One use. Also the only place you can see or change the L11 stop before L11. |

If you own more than one Exploit of a type (extra bonus beats), the extras do nothing here. See Q1 for the pool question.

**Mini-fights vs puzzles.** There is no mini-boss at T4, so the HQ route is regular fights plus elites plus the boss. The buildings are the puzzles. Without an Exploit the slot is a fight, which is harder but still playable.

## 5. Pacing & difficulty curve

Assumptions: T4 enemy values (R2 bands), the reference player (R2 DPT 18 at T4), 3-4 turns per phase.

| Piece | Count on a typical path | Time |
|---|---|---|
| Normal fights (1 phase, 3-4 turns, ~25 s per turn) | 7 | ~2 min each = 14 |
| Elites (2 phases, 6-8 turns) | 2 | ~4 min each = 8 |
| Non-fight nodes (event, shop, rest, building) | 3 | ~1 min each = 3 |
| Boss (12-20 turns) | 1 | ~7 |
| Map reading and decisions | | ~4 |
| **Total** | **12 nodes** | **~36 min** |

**Express path:** 10 nodes, 2 fewer fights (one is replaced by the forced elite), about 28 min.

**HP pressure (placeholder).**
- A normal fight costs 8-12 % max HP at the reference player. An elite costs 16-22 %.
- Typical path: 7 × 10 + 2 × 19 = ~108 %.
- Heals: Siding Repair 25 %, pre-boss Rest 40 %, events about 10 %.
- Net: the player arrives at the boss at about 65-80 % HP if they take both rests, and about 40 % if they skip the pre-boss Rest. That is the designed choice: Rest, or the Direct Lift.
- Skipping fights (Express, Dwell) saves HP but gives up loot.

**Rest and heal budget:** two Sidings (L4 Repair, L5 Dwell-only), one pre-boss Rest, and events. At most 2 Repair opportunities on a path plus the pre-boss Rest.

**Heat.** Elite +1 each. Rack per the GDD 11.5 table. Dwell +2 each (at most 2). Express +4. Heat thresholds still apply (50 gives +1 enemy resistance).

**Boss difficulty.** The baseline says T4 boss wins are 4-8 % in campaigns. Because the HQ route is long, the boss-entry HP and RAM matter. The Direct Lift swing and the HP-recovery choice are the lever. Treat those as the tuning dials in the balance pass.

## 6. Rewards

- **The Rack car (L6):** Schematics banked on capture, plus a rare Daemon (GDD 6.3).
- **Hoisted fights:** +50 % Cycles and an extra Firmware choice. Elite rewards per the normal table.
- **Completion (beyond the boss):**
  - The unspent-Cycle to Schematics conversion (10:1), as for any netrun.
  - Rank +1.
  - The Meridian finale story beat, delivered with the boss.
  - An ICE record step for Meridian.
  - A one-time **Dock Ledger** bonus: Schematics scaled by the number of unused Dwells (0-2), so careful clock play pays.
- Armory assets can drop from the Rack and bank on capture.

## 7. Failure & retry

- **Death:** the standard netrun death (GDD 4.2). The operative is lost with everything unbanked (Cycles, cards, Firmware, Daemons). The campaign gains 10 + tier Heat (14 at T4). The Rack's Schematics, if captured, are banked and kept.
- **Retry:** the HQ is relaunchable with another operative. The layout is **redrawn from a new `hq_manifest` draw**, so p0, `reach_order` and node types are new. Knowing the schedule from the last attempt does not carry over. What carries over is understanding the rules.
- **Abandon:** a run abandoned from the pause menu is a death, per GDD 4.5.
- **Heat effects:**
  - Dwell and Express add Heat. At 75+, raid strength rises (GDD 4.3) and elites are more frequent, which does not change the fixed HQ layout.
  - Express is the Heat-heavy option, which matters for a campaign near a raid threshold.

## 8. Systems needed

| # | System | Use here | Data-only fallback |
|---|---|---|---|
| NEW: **HQ clock map** | `HqMapData` resource (lanes, slot sides, phase_len 2, `reach_order`, `p0`) and a pure function `phase(layer + H)` that picks the active edge table and node variants in `netrun_session` / `map_graph` | Dock cycle, Reach, trolley, Dwell | **Yes:** the generator emits one prebaked edge table and node-variant table for each H in [-1..3]. The engine only switches table by H, draws the ghosts, and stores H and the seed. |
| **N16** | `next_combat_overrides` and `map_edits` | Hoist (enemy ORBIT), Wall shield, Car enrage, boss start RAM ±2, Amend / Reroute / Dwell as run-state edits | Partial: authored enemy variants per tag for a subset of six enemies |
| **N4** | EnrageData | The Car "train departs" timer | Author as a class default override |
| **N1** | PERCENT amount mode | Wall shield 10 % | A flat shield × tier factor |
| **N2** | HP bands | Normal and elite HP at T4 | None |
| **N18** | Data-driven rewards | Hoist loot rows, Rack, Dock Ledger | Hard-coded offers |
| Rest node (D4) | A Rest node type with Repair / Dwell choice | Sidings | A Terminal event with two choices |
| **N19** | Sim metrics | Hoisted vs plain fights, Direct Lift rate, Dwell use | None |

N5 (buffs / Exploits) matters indirectly: the boss draft uses it, and the buildings use the owned Exploit list.

**What is already data:** node types, slot sides, edge rules, the three buildings, tags and rewards.

**What needs code:** the clock function in `netrun_session`, the table switch, saving H and the seed (a save-version bump), the Siding choice UI and the schedule HUD.

**Build order**
1. `HqMapData` with the baked per-H edge tables, H and the seed stored in the save, and the clock chip (no combat changes). This alone delivers the dock cycle and Dwell.
2. N16 overrides for Hoist, Wall and Car tags, plus N4.
3. The three buildings (Amend, Express, Reroute).
4. Trolley, Direct Lift and the boss start modifier. This is coordinated with the boss draft.
5. N18 rows and the Dock Ledger.
6. N19 metrics, then the balance pass (Hoist loot, Dwell Heat, Direct Lift value).

**Determinism notes**
- The only RNG is the layout draw at HQ launch (`map` and `hq_manifest` streams, checkpointed in the run).
- After that, everything is a function of (layer, H, p0, `reach_order`).
- The preview equals the result because the map is computed from the same function the run uses. The Dwell preview uses H+1 but changes nothing until committed.
- No combat RNG is touched.

## 9. Art hooks

The art needs these per-frame values from game state (`mt`, `room_state`, `affected`, `movers`):

- `dock_phase` (P, and T) and a `train_present` flag. The train animates in and out on the freight line.
- `shuttles`: a list of `{slot_wall, slot_train, at}`. These drive the shuttle containers moving between the wall and the train (the kit's `mover()` and `MOVER_POS`).
- `reach_sector` (W / N / E / Yard) and the next sector. These drive the gantry N-S position and the hook marker.
- `trolley_stop` (W / C / E) and a `lift_shaft` highlight for the stair under the trolley. The keep rides the span to the stop.
- `affected`: the node ids that are Hoisted (lit with a crane glow) and the ids that Dwell would change (ghosted).
- `express_boarded`: the train leaves north, lit, and the Express edge is drawn.
- `rack_car_present`: the Rack car is on the train or gone.
- Building states for MANIFEST CONTROL, CUSTOMS GATE and SWITCHYARD (owned / lit / used).
- A clock-chip anchor on the HUD and a schedule strip for the next 4 beats (T..T+3).
- Edges drawn per phase. The route UI must handle edges that appear and disappear when the phase flips.

The art supports all of this today as movers and room states. It makes no rules.

## 10. Open questions

Q: **Exploit pairing.** R7's Exploits are named buff counters drawn per Grid (5 from the pool), while the buildings assume the three GDD types. Are Intel / Breach / Virus still fixed gate types (Q5 in the rules doc)? If not, which Meridian Exploits own each building?

Q: **Dwell strength.** Is "at most 2 Dwells, +2 Heat each, may cost the Rack" the right price? Alternatively it could cost HP or require a Siding visit, as it does now.

Q: **HQ tier.** Are all HQ fights always T4 enemies, or do they follow the campaign's current tier? The draft assumes T4.

Q: **Express.** Is skipping both leg elites acceptable? Or should the Express require the Hoisted elite plus another cost, like a lost Rest?

Q: **Direct Lift value.** Is ±2 starting RAM and a free first card the right swing? It couples to the boss draft (the Customs Seal hub and any RAM-drain mechanics).

Q: **Crane naming.** The art doc says the keep crane slews, but v3 is a gantry plus trolley. Does the art confirm the Reach as gantry N-S plus trolley E-W, so the hook sectors read correctly?
