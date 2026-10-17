<!-- draft via Message Batches API, claude-sonnet-5-5, batch msgbatch_01TQsqGnerTdLwJEata9mp6i, custom_id v2__hq__meridian; status ok; tokens in 12106 cache-write 0 cache-read 32585 out 19493; cost $0.113. A DESIGN DRAFT for the designer's review: nothing here is built. -->

## Changes vs v1

- **Issue 1 (BLOCKER, clock vs p0):**
  - Removed `p0`. The train is present when `floor(T/2)` is odd, with T = layer + H.
  - At H = 0 the schedule is fixed: present at L2-3, L6-7 and L10-11, away at L4-5 and L8-9.
  - The Rack car (L6) is therefore guaranteed at H = 0. Per-seed variation comes from `reach_order`, node-type draws and the stair shuffle.
  - Re-derived Dwell's cost from the formula (§3.1). The Rack is lost only at H ≥ 2 or H = -1, so it takes Amend + Dwell or Amend -1. A single Dwell closes the Express instead.
  - v1's claim that a lone Dwell can cost the Rack was wrong and is removed.
  - Dwell is capped at 1 per run (§3.1: with only one Dwell-capable Siding per path, a second use was impossible anyway). H is bounded to [-1, 2].
- **Issue 2 (BLOCKER, edges):**
  - Replaced the L7→L8 rule with an explicit index table.
  - Added L8→L9, L9→L10, L10→L11 and L11→L12.
  - Every node now has an exit and an entrance, and RAIL (idx 4) reaches LegE.
  - Edges are now written out per layer pair (§2).
- **Issue 3 (node count):** Corrected to 37 nodes, or 38 with EXP10. L1-3 = 9, L4-7 = 16, L8-L12 = 2+3+3+3+1 = 12.
- **Issue 4 (pacing):**
  - Re-counted on 11 route nodes plus the boss, with two sample paths (fight-heavy and balanced).
  - Used 2.5 min per normal fight.
  - Totals are now ~40 and ~37 min, with an explicit heal budget (§5).
- **Issue 5 (Car enrage):** The Car tag is now one step: +25 % enemy damage from turn 3 (EnrageData start 3, every 99). It bites in a 3-4 turn fight.
- **Issue 6 (Hoist readability):**
  - The ORBIT trail is always shown in the preview (GDD 2.11 telegraph).
  - L1 is never Hoisted.
  - Added a sim check (N19) that Hoisted fights stay within the class turn target.
  - Marked as untested.
- **Issue 7 (Direct Lift):**
  - Clarified that start RAM is 6, so -2 means 4, never negative.
  - Tagged "first card costs 0" as NEW: boss start modifier, with an N16 field and a fallback of RAM ±2 only.
- **Issue 8 (permuted Reach for Act I):** Stated that slot sectors are fixed and only the beat-to-sector map is permuted. Added a quiet-beat rule for beats whose sector holds no fight node.
- **Issue 9 (nit):** Kept, because there is nothing to change.
- Also fixed incidental v1 errors: the Hoist asterisk on Shop nodes (non-fights are unaffected) and the Dock Ledger (now scaled by one Dwell).
- No fix conflicted with a designer ruling.

---

# Meridian: HQ netrun draft

Working name: **THE DOCK CLOCK**, a netrun through the Gatehouse Gantry. The boss is the Meridian boss ("the Manifest"), referred to by that working name only.

## 1. Concept & the named mechanic

**What the art shows (v3):**
- A Π gantry crane built as a castle gatehouse stands over a container-walled yard.
- Containers shuttle between the wall and the train.
- The gantry rolls N-S on the wall runways. The keep, which is the trolley, rides the span E-W with the server in its crown.
- Trucks sit on three sides. The freight line leaves by the north gate.
- MANIFEST CONTROL is the named building.

**As a game mechanic.** The HQ is a map whose connections are driven by a clock. Every layer is one beat of the yard clock, and the clock moves three things on a fixed, visible timetable:
1. **Dock cycle.** Every other beat the train arrives or departs and the shuttle container swaps between the wall and the train. This rewires which nodes connect to which, and it can remove a node (the Rack car leaves with the train).
2. **The Reach.** The crane's hook visits one sector per beat: W wall, N rail, E wall, Yard. Fights in the hooked sector are *Hoisted*: more dangerous, better loot.
3. **The trolley.** The keep sits where the Reach is. The stair under it at L11 is the direct lift to the boss. Missing it costs RAM.

All three can be read ahead of time. The skill is routing through a schedule, not luck. You get two ways to shift the schedule: **Dwell** and the MANIFEST CONTROL **Amend**.

**Why it can't be mistaken for another HQ.**
- Solace is a ladder of rooms.
- Halcyon is an eye that retargets.
- Orbital is doors and a rocket.
- REBEL_CELL is a window sequence.
- Meridian is the only one whose **map changes shape on a timetable**.

## 2. Structure

**12 layers** (11 route layers plus the boss), **37 nodes** (38 with the Express landing EXP10), 2-4 nodes per layer.
- Count: L1-L3 = 3 each (9), L4-L7 = 4 each (16), L8 = 2, L9 = 3, L10 = 3, L11 = 3, L12 = 1.
- The generator runs once per HQ launch and draws node types, `reach_order`, the stair shuffle and the Express elite from the `map` and `hq_manifest` streams (§3).
- The dock timetable itself is fixed. The per-run variety is in what sits on it and where the hook falls.

### Layer map (default, H = 0)

```
ACT I  THE GATE        W        S         E            ground, 3 gate sides
 L1                  [Rtr]    [Rtr]     [Rtr]          all Routers (GDD 4.2), never Hoisted
 L2                  [Evt]    [Rtr]     [Rtr]          W = truck box          (train present)
 L3                  [Rtr]  [MANIFEST   [Rtr]          S = Intel building     (train present)
                              CONTROL]
ACT II THE WALL & THE LINE   slot order shifts with the shuttle
 L4  away    Reach W   OUT[Rtr*] SH@wall[Shop] YARD[Rtr] RAIL[Siding: Repair/Swap/Dwell]
 L5  away    Reach N   OUT[Elite] SH@wall[Cache] YARD[Rtr] RAIL[Siding: Swap/Dwell]
 L6  present Reach E   OUT[Rtr] YARD[Rtr] SH@train[Evt] RAIL[RACK car]
 L7  present Reach Yd  OUT[Rtr] YARD[Elite*] SH@train[Evt] RAIL[CUSTOMS GATE]
ACT III THE LEGS
 L8  away    Reach W   LegW[Rtr*]            LegE[Rtr]
 L9  away    Reach N   LegW[Elite]  CAB[SWITCHYARD]  LegE[Elite]
ACT IV THE SPAN & THE KEEP
 L10 present Reach E   SpanW[Rtr]  SpanC[Evt]  SpanE[Rtr*]   (+ EXP10, see §3.4)
 L11 present Reach Yd  StairW / StairC / StairE = {Rest, Router, Shop} shuffled
 L12                   CROWN: the Meridian boss
```

`*` = Hoisted at this phase. "Rtr" = Router (normal fight). "Evt" = Terminal event.
- At L2 the E Router and at L3 the S node are the Hoisted ones (Reach E, Reach Yard).
- A beat whose sector holds no fight node (L5, L6, L9 here) is quiet, and nothing is Hoisted.

### Slot-variant table (what a slot is, by dock phase)

| Layer | SH, shuttle on wall (train away) | SH, shuttle on train (train present) | RAIL, train away | RAIL, train present |
|---|---|---|---|---|
| L4 | Shop | Evt | Siding (Repair / Swap / Dwell) | Car (Router) |
| L5 | Cache | Evt | Siding (Swap / Dwell) | Car (Router) |
| L6 | Rtr | Evt | Rtr (empty siding) | RACK car |
| L7 | Rtr | Evt | Rtr (empty siding) | CUSTOMS GATE (Car if no Breach) |

OUT is fixed per layer (L4 Rtr, L5 Elite, L6 Rtr, L7 Rtr). YARD is fixed (L4-L6 Rtr, L7 Elite).

### Edge rules

Edges are rules applied to slots, not a hand-drawn list.

- **L1→L2→L3:** a node connects to the next layer's same column and adjacent columns. W and E are not adjacent, so W reaches W and S, S reaches all three, and E reaches S and E.
- **L3→L4 (by slot name, independent of order):**
  - W3 → OUT, SH
  - S3 → SH, YARD
  - E3 → YARD, RAIL
- **L4→L5→L6→L7:**
  - Shuttle on the wall: order `[OUT, SH, YARD, RAIL]`.
  - Shuttle on the train: order `[OUT, YARD, SH, RAIL]`.
  - A node at index i connects to indices i-1, i and i+1 of the next layer, using the next layer's own order.
  - Every next-layer index receives from at least one node, and every node has an exit.
- **L7→L8 (by L7 index, L7's own order):**

| L7 index | Reaches |
|---|---|
| 1 | LegW |
| 2 | LegW, LegE |
| 3 | LegW, LegE |
| 4 | LegE |

- **L8→L9:** LegW8 → LegW9, CAB. LegE8 → CAB, LegE9.
- **L9→L10:** LegW9 → SpanW, SpanC. CAB → SpanW, SpanC, SpanE. LegE9 → SpanC, SpanE.
- **L10→L11:** SpanW → StairW, StairC. SpanC → all three. SpanE → StairC, StairE.
- **L11→L12:** every stair connects to the Crown.
- **Express (Breach building, §3.4):** CUSTOMS GATE (L7 RAIL) → EXP10, only while the train is present at L7. EXP10 → all three stairs. EXP10 is not reachable by any other edge.

### Mapping onto the landmark's slots

| Landmark slot | Map use |
|---|---|
| Gatehouse chamber (W, S, E) | L1 |
| Truck box, bay lanes | L2 |
| Corner towers (S) | L3 side nodes |
| Wall outer and inner face | OUT (L4-L7) and YARD |
| Train car (cut-open carriage) | RAIL and SH@train |
| Gantry leg floors | L8-L9 |
| Span gallery windows | L10 |
| Keep crown | L12 |

- The L11 stairs sit on the keep's turret stairs.
- Slots are generated on demand for the graph the game sends. Nothing depends on a fixed slot count.

## 3. Unique mechanics

All rules read from one state, `hq_clock`: `{layer, H, reach_order}`. They are a pure function of that state, with no hidden state.

**The clock**
- **T = layer + H.**
- **H** is the dwell offset: starts at 0, bounded to [-1, 2].
- **Train present** when `floor(T / 2)` is odd (T = 2, 3, 6, 7, 10, 11; the train is away at T = 0, 1, 4, 5, 8, 9).
- **Reach sector** = `reach_order[T mod 4]`. The default order is W, N, E, Yard.

**What H does to the key beats** (the schedule the preview shows):

| H | Rack car (L6, T=6+H) | Express (L7 train present) | L4 / L5 RAIL | L11 stop (T=11+H) |
|---|---|---|---|---|
| -1 | gone (T 5, away) | open (T 6) | Car / Siding | StairE |
| 0 | present | open | Siding / Siding | StairC |
| 1 | present (T 7) | closed (T 8) | Siding / Car | StairW |
| 2 | gone (T 8) | closed | Car / Car | StairC |

The H = 1 and H = 2 rows assume the L4 and L5 Sidings were reached at their H = 0 value, since earlier layers are already behind you. H = 2 is reachable only by Amend +1 plus a Dwell.

### 3.1 Dock cycle (the named mechanic)

- **Rule.** Every other beat the train arrives or leaves, and the shuttle container swaps between the wall slot and the train slot.
  - **Train-side content exists only while the train is present.** RAIL is a Car (fight, the Rack at L6, the gate at L7) while present, and a Siding or empty siding while away.
  - **The shuttle moves.** At the wall slot when the train is away, at the train slot when present. Its edges follow the index rule in §2, so each swap rewires the map.
- **Trigger.** Per layer, evaluated from T. The timetable is fixed: the train arrives at L2, leaves at L4, arrives at L6, leaves at L8 and arrives at L10.
- **What the player sees.**
  - A clock chip: `T 5 · swap in 1`.
  - Every shuttle drawn with a ghost at its other slot.
  - The train's arrival and departure drawn on the freight line.
  - Edges drawn per the current phase.
  - Hovering Dwell or Amend previews the redrawn map at the new H (a preview, not a commit).
- **Combat tags** (N16 `combat_overrides`):
  - **Wall (OUT):** the enemy starts with SHIELD = 10 % of its max HP (R5 PERCENT).
  - **Car (RAIL):** the "train departs" timer is one enrage step, +25 % enemy damage from turn 3 (`EnrageData` start 3, every 99). The normal class default is off, so this is an authored override, and it bites inside a 3-4 turn fight.
  - **Yard:** no tag.
- **Counters.** Dwell, the Amend, and routing around the swap.
- **Determinism.** The phase is a pure function of (layer, H). No RNG at play time.

**Dwell.** At a Siding, instead of Repair you may Dwell.
- It costs one beat and +2 Heat, and sets H += 1. It is allowed once per HQ run. Only one Siding per path exists in practice, since a Dwell turns the next RAIL into a Car.
- **What it buys:**
  - It moves the Hoist away from, or onto, a layer you care about.
  - It moves the L11 trolley stop (to StairW at H = 1), so the free Rest stair can become the Direct Lift.
- **What it costs:**
  - It closes the Express at L7 (train away at T = 8).
  - With the MANIFEST CONTROL Amend +1 first, it also loses the Rack car.
  - The preview shows both.

### 3.2 The Reach (the crane's hook)

- **Rule.** One sector is hooked per beat. A fight node in it is **Hoisted**, except at L1, which is never Hoisted.
  - Enemy pointers ORBIT 1 tick per turn (existing `PointerBehavior.ORBIT`, applied via `combat_overrides`). The preview always draws the orbit trail (GDD 2.11 telegraph).
  - The node pays +50 % Cycles and one extra Firmware choice.
  - Non-fight nodes are unaffected.
- **Which nodes are in which sector.** Slot sectors are fixed in data:
  - Act I: W, Yard (S), E.
  - OUT alternates W / E by layer (L4 W, L5 E, L6 W, L7 E).
  - RAIL and SH@train are N. SH@wall takes OUT's side that layer. YARD is the Yard.
  - Legs are W and E, the CAB is N, SpanW / SpanC / SpanE are W / Yard / E.
  - Stairs: W / Yard / E.
- **Seeded variation.** `reach_order` is a permutation of {W, N, E, Yard}, drawn from `hq_manifest`. Only the beat-to-sector map is permuted, never a slot's sector. A permuted order can therefore Hoist Act I nodes at different layers, and leaves some beats quiet.
- **What the player sees.** A hook marker on the sector of each layer's beat. Hoisted nodes are lit with a crane glow.
- **Counters.** Step around it, or take it for the loot. Because it is visible, there are no surprises.
- **Determinism.** Pure function of T and the drawn order.
- **Untested:** whether a one-needle ORBIT normal stays inside 3-4 turns. N19 checks this in the balance pass.

### 3.3 The trolley and Direct Lift

- **Rule.** At L11 the stair under the trolley is the **Direct Lift** (W, C or E). The mapping is Reach W → StairW, E → StairE, N and Yard → StairC.
  - Direct Lift: the boss fight starts with +2 RAM and your first card costs 0.
  - Any other stair: the boss fight starts with -2 RAM.
  - Start RAM is 6, so the worst case is 4, never negative. The swing is 4 RAM, about one nudge plus one card.
- **The puzzle.** Stair types (Rest, Router, Shop) are shuffled per run, so the free Rest stair may or may not be the Direct Lift stair. Taking it means the missing-lift penalty in exchange for the heal.
- **What the player sees.** The trolley stop for L11 is visible from L9 onward (from the start with Intel). The keep draws its parked position and a lit lift shaft on the matching stair.
- **Counters.** Dwell and Amend shift T. The Switchyard rewrites `reach_order`.
- **Determinism.** Pure function of T and `reach_order`.
- **Dependency.** "First card costs 0" is **NEW: boss start modifier** (`first_card_free` and `start_ram_delta` fields on N16 `next_combat_overrides`). Fallback: RAM ±2 only.

### 3.4 Railhead: the Express and the north gate

- **Rule.** The freight line leaves north. With the Breach building you can board the train at the L7 CUSTOMS GATE (train present, so H ≤ 0) and ride to **EXP10**, skipping L8-L9 (the two leg elites and the CAB).
  - **Cost:** +4 Heat and a forced Hoisted elite fight at EXP10.
  - **Reward:** two fewer fights and a shorter run.
  - **Cost of skipping:** the leg elites' rewards and the CAB.
- **What the player sees.** The train leaves the north gate lit when you board, and an Express edge is drawn from the CUSTOMS GATE to the span.
- **Determinism.** The edge exists if the building is owned and the phase is right at L7. The forced elite is drawn from the `map` stream at generation.

## 4. Node kit

- **Router (normal fight).** A T4 Meridian normal, 1 phase, HP 56-70 (R2). Tags per §3.1 and §3.2.
- **Elite.** Two phases (R1), HP 112-144 at T4. Placed at L5 (OUT, Wall Garrison), L7 (YARD, Yard Foreman) and L9 (one per leg). Heat +1 each per GDD. A Hoisted elite is the hardest regular node.
- **Terminal (event).** Truck box, train box and reading-room events in the Meridian voice. With N16, some events alter the schedule (for example, "reschedule: H ±1"). This costs the same Amend/Dwell budget, so H stays in [-1, 2].
- **Mainframe (shop).** L4 Wall Stock (shuttle at the wall). A Shop is also one of the L11 stair types. Hoist doesn't change stock. A shuttle shop is reachable only while the shuttle is on your side.
- **Cache.** L5 shuttle cargo, a Firmware offer. The event mini-puzzle is not used here until it is vetted (D4).
- **Server Rack.** One optional Rack at L6 RAIL (the train present). It is elite-strength and banks its Schematics on capture (GDD 4.2). It is lost at H = -1 or H = 2 (§3).
- **Rest (Siding).**
  - Repair heals 25 % max HP; Swap Firmware locations is the other D4 option; Dwell shifts the clock.
  - The L4 Siding offers all three. The L5 Siding offers Swap or Dwell only.
  - The pre-boss Rest stair heals 40 %.
- **Puzzle nodes.** Three buildings, each a node only if the Exploit is owned (D5). Otherwise the slot is a plain Router:

| Building | Exploit (placeholder pairing) | What it does here |
|---|---|---|
| **MANIFEST CONTROL** (L3 S) | Intel | Shows the whole timetable from the start. One free **Amend**: H ±1 (once). |
| **CUSTOMS GATE** (L7 RAIL) | Breach | Opens the rail gate: the Express (§3.4). |
| **SWITCHYARD** (L9 CAB) | Virus | **Reroute:** swap two sectors in `reach_order` (this also moves the L11 stop). One use. It is also the only place to see or change the L11 stop before L11. |

Extra Exploits of a type do nothing here (see Q1).

**Mini-fights vs puzzles.** There is no mini-boss at T4. The route is regular fights, elites and the boss, and the buildings are the puzzles.

## 5. Pacing & difficulty curve

Assumptions: T4 enemy values (R2 bands), the reference player (DPT 18 at T4), 3-4 turns per phase (normal), 6-8 (elite), about 25 s per turn and 2.5 min per normal including overhead.

A path crosses 11 route nodes plus the boss. Two sample paths:

| Piece | Fight-heavy path | Balanced path |
|---|---|---|
| Normal fights (2.5 min) | 8 = 20 | 6 = 15 |
| Elites (~4 min) | 2 = 8 | 2 = 8 |
| Non-fight nodes (~1 min) | 1 = 1 | 3 = 3 |
| Boss (12-20 turns) | 7 | 7 |
| Map reading and decisions | 4 | 4 |
| **Total** | **~40 min** | **~37 min** |

**Express path:** about 32 min.
- Nodes: L1-L6 (including the Rack), the L7 gate, EXP10 (forced Hoisted elite), L11, then the boss.
- It replaces two leg elites with one Hoisted elite.
- Its Heat is +4 for the ride plus 1 for the elite.

**HP pressure (placeholder, % of max HP):**
- A normal costs 8-10 % and an elite 16-20 %.
- Balanced path: 6 × 9 + 2 × 18 = 90 %.
- Fight-heavy path: 8 × 9 + 2 × 18 = 108 %.
- Heal supply on the map:
  - L4 Siding Repair, 25 %.
  - One event, about 10 %.
  - Pre-boss Rest stair, 40 %.
  - A shop heal, about 15 %, for Cycles.
- Balanced path arithmetic: damage through L10 is 90 % against 35 % healed, so it reaches L10 at about 45 % HP. The Rest stair then gives 85 % at the boss. Taking the Direct Lift stair instead leaves about 45 % HP with +2 RAM.
  - That is the designed choice: Rest, or the Direct Lift.
  - It is made easier by a Dwell that moves the lift onto the Rest stair.
- A fight-heavy path is not survivable on heals alone. It needs a Siding, a shop and the Rest. It is tuned to trade HP for Hoist loot.

**Rest and heal budget:** at most one Repair (L4) plus the Rest stair plus events and the shop. Heal is deliberately scarce.

**Heat.** Elite +1 each. Rack per the GDD 11.5 table. Dwell +2 once. Express +4. The Heat thresholds still apply (50 gives +1 enemy resistance).

**Boss difficulty.** The baseline has T4 boss wins at 4-8 % in campaigns. Boss-entry HP and RAM are the levers. Treat the Direct Lift swing and the Rest choice as tuning dials in the balance pass.

## 6. Rewards

- **The Rack car (L6):** Schematics banked on capture plus a rare Daemon (GDD 6.3). Armory assets can drop and bank on capture.
- **Hoisted fights:** +50 % Cycles and an extra Firmware choice. Elite rewards follow the normal table.
- **Completion (beyond the boss):**
  - The unspent-Cycle to Schematics conversion (10:1).
  - Rank +1.
  - The Meridian finale story beat, delivered with the boss.
  - An ICE record step for Meridian.
  - A one-time **Dock Ledger** bonus (N18 row, placeholder): +4 Schematics if no Dwell was used, +2 if the Amend was unused.

## 7. Failure & retry

- **Death:** the standard netrun death (GDD 4.2). The operative is lost with everything unbanked. The campaign gains 10 + tier Heat (14 at T4). A captured Rack's Schematics are banked and kept.
- **Retry:** the HQ is relaunchable with another operative. The layout is **redrawn from a new `hq_manifest` draw**, so node types, `reach_order`, the stair shuffle and the Express elite are new. The dock timetable is the same, so what carries over is understanding the rules.
- **Abandon:** a run abandoned from the pause menu is a death (GDD 4.5).
- **Heat effects:**
  - Dwell and Express add Heat. At 75+, raid strength rises and elites are more frequent (GDD 4.3), which doesn't change the fixed HQ layout.
  - Express is the Heat-heavy option, which matters for a campaign near a raid threshold.

## 8. Systems needed

| # | System | Use here | Data-only fallback |
|---|---|---|---|
| NEW: **HQ clock map** | `HqMapData` (lanes, slot sectors, phase length 2, `reach_order`, slot-variant table) and a pure function `phase(layer + H)` picking the edge table and node variants in `netrun_session` / `map_graph` | Dock cycle, Reach, trolley, Dwell | **Yes:** the generator emits one prebaked edge table and node-variant table for each H in [-1..2]. The engine only switches table by H, draws the ghosts and stores H and the seed. |
| **N16** | `next_combat_overrides`, `map_edits` | Hoist (ORBIT), Wall shield, Car enrage, Amend / Reroute / Dwell as run-state edits | Partial: authored enemy variants per tag for a subset of enemies |
| NEW: **boss start modifier** | `first_card_free`, `start_ram_delta` on `next_combat_overrides` | Direct Lift | RAM ±2 only |
| **N4** | EnrageData | The Car one-step enrage | Author as a class default override |
| **N1** | PERCENT amount mode | Wall shield 10 % | A flat shield × tier factor |
| **N2** | HP bands | Normal and elite HP at T4 | None |
| **N18** | Data-driven rewards | Hoist loot, Rack, Dock Ledger | Hard-coded offers |
| Rest node (D4) | Rest node type with Repair / Swap / Dwell | Sidings | A Terminal event with choices |
| **N19** | Sim metrics | Hoisted vs plain fights, Direct Lift rate, Dwell use | None |

N5 (buffs / Exploits) matters indirectly: the boss draft uses it, and the buildings read the owned Exploit list.

**Already data:** node types, slot sectors, edge rules, the buildings, tags and rewards.

**Needs code:** the clock function, the table switch, saving H and the seed (a save-version bump), the Siding choice UI and the schedule HUD.

**Build order**
1. `HqMapData` with baked per-H edge tables, H and the seed in the save, and the clock chip. This alone delivers the dock cycle and Dwell.
2. N16 overrides for the Hoist, Wall and Car tags, plus N4.
3. The three buildings (Amend, Express, Reroute).
4. Trolley, Direct Lift and the boss start modifier, coordinated with the boss draft.
5. N18 rows and the Dock Ledger.
6. N19 metrics, then the balance pass (Hoist loot, Dwell Heat, Direct Lift value).

**Determinism notes**
- The only RNG is the layout draw at HQ launch (`map` and `hq_manifest` streams, checkpointed in the run).
- After that everything is a function of (layer, H, `reach_order`).
- The preview equals the result because the map is computed from the same function the run uses.
- The Dwell and Amend previews use the new H but change nothing until committed.
- No combat RNG is touched.

## 9. Art hooks

Per-frame values the art needs from game state (`mt`, `room_state`, `affected`, `movers`):

- `dock_phase` (floor(T/2), and T) and a `train_present` flag. The train animates in and out on the freight line.
- `shuttles`: a list of `{slot_wall, slot_train, at}`, driving the shuttle containers between the wall and the train (the kit's `mover()` and `MOVER_POS`).
- `reach_sector` (W / N / E / Yard) and the next sector, driving the gantry N-S position and the hook marker. A quiet beat shows the hook with no glow.
- `trolley_stop` (W / C / E) and a `lift_shaft` highlight on the stair under the trolley. The keep rides the span to the stop.
- `affected`: the Hoisted node ids (crane glow) and the ids a Dwell or Amend would change (ghosted).
- `express_boarded`: the train leaves north, lit, with the Express edge drawn.
- `rack_car_present`: the Rack car is on the train or gone.
- Building states for MANIFEST CONTROL, CUSTOMS GATE and SWITCHYARD (owned / lit / used).
- A clock-chip anchor and a schedule strip for the next 4 beats (T..T+3).
- The orbit trail on Hoisted enemy wheels in the combat preview.
- Edges drawn per phase. The route UI must handle edges that appear and disappear when the phase flips.

The art supports all of this today as movers and room states. It makes no rules.

## 10. Open questions

Q: **Exploit pairing.** R7's Exploits are named buff counters drawn per Grid (5 from the pool), while the buildings assume the three GDD types. Are Intel / Breach / Virus still fixed gate types? If not, which Meridian Exploits own each building?

Q: **Fixed timetable vs per-run variety.** The dock schedule is now identical every run, and only the hook order, node types and stair shuffle vary. Is that enough variety, or should a second seeded offset return, with the L6 Rack guaranteed by generation?

Q: **Dwell value.** At once per run, closing the Express and risking the Rack with Amend, is Dwell worth taking? Should it also cost HP, or give a bigger payoff such as a free Firmware swap?

Q: **HQ tier.** Are all HQ fights always T4, or do they follow the campaign's current tier? The draft assumes T4.

Q: **Direct Lift value.** Is ±2 RAM with a free first card the right swing? It couples to the boss draft (the Customs Seal hub and any RAM-drain mechanics).
