<!-- draft via Message Batches API, claude-sonnet-5-5, batch msgbatch_01TQsqGnerTdLwJEata9mp6i, custom_id v2__hq__solace; status ok; tokens in 11653 cache-write 0 cache-read 32585 out 17247; cost $0.101. A DESIGN DRAFT for the designer's review: nothing here is built. -->

## Changes vs v1

- **Issue 1 (BLOCKER, layer count and crown vs rung 9 on floor 27) -> fixed.**
  - The layout is now gate L0 + 8 rungs (L1–L8, floors 3–24) + crown L9 = **10 layers, 10 nodes on a path**.
  - The 9th rung is deleted. The crown sits on the building's top floor (27), above the last route floor, so it shares a floor with nothing.
  - This matches the art's existing 8 route floors, so the "28 floors / move the crown" ask is gone. §5 now says 10 nodes on a path.
- **Issue 2 (BLOCKER, Account Manager contradictions) -> fixed.**
  - The Account Manager is fixed at rung 8 and is mandatory. It is exactly one 2-phase fight, and both rung-8 rooms resolve to the same fight.
  - Deleted: the rung-5 placement, the "bypass by staying UP" rule, the Breach Maintenance Duct, the rung-9 elite chain and the "fight it once, choose when" logic.
  - The 12-turn gate before the boss is gone. The rung-8 mini-boss is the only gate, and it pays a heal.
- **Issue 3 (BLOCKER, undefined Cache, nonexistent damage field, pressure vs enrage) -> fixed.**
  - The "Cache" is dropped from this HQ. The D4 Cache needs vetting, and GDD 4.2's optional layer-4 Server Rack already does the job.
  - Pressure feeds a named field, `enemy_damage_pct`, added to the N16 `next_combat_overrides` payload (marked NEW field).
  - Pressure is capped at +30 %. It sums with enrage steps in one additive buff (R2/R4), and the stacking is shown in §3.3.
- **Issue 4 (MAJOR, tolls and zig-zag) -> fixed.**
  - Crossing now also adds +1 pressure to the destination tower, so zig-zagging is no longer nearly free.
  - Audit no longer costs Heat, which was dominated at high Heat. It is now +1 enemy resistance on your next fight.
  - Tolls exist only on rungs 1–6. The rung-7 → rung-8 ACROSS edge is removed, so the Co-pay no longer lands on the last crossing.
- **Issue 5 (MAJOR, overlapping read systems, weak Virus) -> fixed.**
  - Key Fragments are dropped. Read horizon = current rung + 2 + one per owned Exploit, and Intel reads the whole ladder.
  - Tolls and pressure are always visible, so Intel no longer "reveals" them.
  - Virus is now "a Rest resets both towers' pressure". The incoherent "countered by the Genome Core's Exploit list" line is deleted. Exploits keep only their R7 job against boss buffs, which the boss draft owns.
- **Issue 6 (MAJOR, HP and rest arithmetic) -> fixed.**
  - Intake is recomputed as per-class HP lost (§5). I use the R2 intake target of 2–4 per turn for normals, not the loose 5.
  - The rest placement matches the layout: Ward rests at rungs 3 and 6, Billing shops at 3 and 6.
  - A full path walk with the HP cap is shown for both towers. Heal is capped by missing HP, which v1 ignored.
  - The mini-boss kill pays a 40 % heal, so the player reaches the boss at roughly 55–60 % HP.
  - Rest also offers the D4 option of swapping Firmware locations.
- **Issue 7 (MAJOR, retry graph and the Triage Unit) -> fixed.**
  - The layout is fully authored and fixed (no kind weights), so there is no per-attempt graph.
  - Only content picks (enemy and event per room) use the `hq_graph` stream. It is seeded once at campaign start, and a retry reuses it, so the learning loop survives.
  - This also serves D10's unique-experience intent, because the HQ is unique per corporation.
  - The Ward pool excludes the Triage Unit until its design pass lands.
- **Issue 8 (NIT, tags) -> fixed.** REST is labeled a D4 ruling, not an N#. The 9-rung slot generation is gone. Key Fragments are gone. Debts name N16 and the new `enemy_damage_pct` field.
- **Issue 9 (NIT, tier and enrage) -> fixed.**
  - §5 now states that the R2 mini-boss band is n/a at T4. The rule I applied is the T3 HP band with T4 damage, flagged as a Q.
  - Enrage defaults and the pressure stacking are spelled out.
- **Critic Qs:**
  - Crossing costs both a toll and +1 pressure (a Q remains).
  - The retry graph is the same seed.
  - The mini-boss is mandatory.
- **Kept, because the critic marked it strong:** the two-lane ladder, the deterministic previewable tolls and the art-state hooks table.
- **Ruling conflicts:** none. R1 (mini-boss 2 phases, 6–12 turns), R7 and D4 are respected. HQ netruns are exempt from the 7-layer norm under D10.

---

# Solace: HQ netrun draft

## 1. Concept & the named mechanic

**What the art shows:** two porcelain towers twist around each other through one full turn, with glazed skybridges only on route floors. Every route floor has a room in each tower, and the climb ends in a crown holding THE GENOME CORE. Rooms above the read horizon are frosted (UNREAD).

**Restated as a game mechanic: THE LADDER.** The run is a climb of rungs, one per route floor. At each rung the player stands in a room of Tower A or Tower B and chooses **UP** (the same tower, next rung) or **ACROSS** (cross the bridge, then continue up the other tower). Each tower is its own authored lane, so choosing a tower is choosing a kind of climb.

The player is the infection climbing a treatment facility:
- **Tower A, "Ward":** the clinical tower. More fights, two guaranteed rests (rungs 3 and 6), clinical events.
- **Tower B, "Billing":** the financial tower. Fewer fights, a Server Rack, shops at rungs 3 and 6, contract events. It has no rests and heals only by paying.

**Why no other HQ can be mistaken for this:**
- Only here does the player switch between two parallel lanes every rung.
- Only here does what you can see ahead depend on your own position and keys (the READ rule).
- Only here does a bridge crossing carry a toll and a pressure cost.
- Halcyon's eye, Meridian's shuttle, Orbital's gates and REBEL_CELL's mirror act on the map from outside. Solace's ladder acts on the route itself.

**Spine rule:** every mechanic below is a property of the ladder: which tower you stand in, which rungs you can read, and what a crossing costs.

## 2. Structure

**Layer count: gate (L0) + 8 rungs (L1–L8, floors 3–24) + crown (L9) = 10 layers, 10 nodes on any path.** This exceeds the 7-layer standard, as D10 allows.

| Layer | Floor | Ward (A) | Billing (B) |
|---|---|---|---|
| L0 Clinic Gate | – | one node, free; pick a tower; tutorial card | same node |
| L1 | 3 | Fight | Fight |
| L2 | 6 | Fight | Waiting Room (event, §4) |
| L3 | 9 | **Rest** | **Shop** |
| L4 | 12 | Elite | **Server Rack** (elite-strength, optional) |
| L5 | 15 | Event (clinical, heals ~12 HP) | Event (contract) |
| L6 | 18 | **Rest** | **Shop** |
| L7 | 21 | Fight | Fight |
| L8 | 24 | **Account Manager** | **Account Manager** (the same fight; whichever room you enter) |
| L9 Crown | 27 | THE GENOME CORE | same node |

**Count check:** 1 gate + 8 rungs + 1 crown = 10 layers. A path visits 10 nodes. The art's 8 route floors (3, 6, …, 24) hold the 8 rungs, and the crown is the building's top floor (27).

**Edges (the ladder rules):**
- From the gate, both L1 nodes are reachable (the choice of tower).
- From rung r (1–6) you may go **UP** to the same tower's rung r+1, or **ACROSS** to the other tower's rung r+1. ACROSS passes through that rung's toll (§3.2).
- Rung 7 has **UP edges only** (A7→A8, B7→B8). The floor-21 bridge is sealed ("Staff Only"), so no crossing happens just before the mini-boss.
- A8 and B8 are one fight instance shown in both rooms. Entering either consumes both. Both lead to the crown.
- The crown is reachable only from rung 8.
- The graph is a valid layered DAG for the existing map code. ACROSS is an edge to the other tower's next layer with a `toll_kind` attribute. In 3D the player walks the bridge at rung r and takes the stair up in the other tower, so the visual matches the art.

**Fixed structure:** the entire layout (kinds per room) is authored and fixed. Only content picks inside a room (which enemy from the tower's pool, which event) draw from the seeded `hq_graph` stream (§3.4).

**Mapping onto landmark slots (8.4 rules 2 and 5):**
- Slot = (strand, route floor index). Rung r is route floor 3r, node order A then B.
- UP = the stair up the front face's outer edge. ACROSS = the bridge's front edge at that floor.
- The rung-8 pair draws as two rooms in the same "mini-boss" kind frame and the same state.

## 3. Unique mechanics

### 3.1 The READ rule (what you can see)

- **Rule:** you read rungs up to **current rung + 2 + the number of Exploits you own** (0–3). **Intel reads the entire ladder.** Rooms above the horizon are UNREAD: the kind is hidden and the room is frosted.
- **Trigger:** the horizon recomputes on arrival at each rung and when an Exploit state changes.
- **Bridge scouting:** walking a bridge reads +1 rung beyond the horizon for the destination tower's next rung only, so crossing is also a scouting action.
- **What the player sees:** frosted dimmed rooms above the horizon with a "?" disc and an UNREAD chip. The frost clears in a wipe as `read_horizon` rises.
- **Not hidden:** toll kinds and pressure are always visible, because they are deterministic.
- **Counter:** information only. The counters are Exploits and bridge scouting.
- **Determinism:** the layout is fixed, and content picks are drawn at generation, so reading is a pure reveal. No RNG at reveal time.

### 3.2 The Toll (crossing costs something)

- **Rule:** ACROSS means walking the bridge at the current floor, and the bridge holds a toll. The toll is a pure function of the departure rung. There is no RNG, and it is visible on the ACROSS option before commit.

| Departure rung | Toll | Effect |
|---|---|---|
| 1 and 5 | Co-pay | Pay 8 Cycles or lose 6 HP (player's choice at the bridge) |
| 2 and 6 | Referral | Your next fight starts with 1 CORRUPTED slice on your wheel (cards and nudges there cost 2× RAM, R9) |
| 3 | Audit | Your next fight's enemies get +1 spin resistance (ENEMY_RESISTANCE rule modifier) |
| 4 | Quarantine | Your next fight starts with RAM 4 instead of 6 |

- **Why it exists:** otherwise ACROSS is free and the ladder collapses to the single best tower.
- **Also on every crossing:** +1 pressure to the destination tower (§3.3). This is the second price of crossing, so zig-zagging is not cheap.
- **What the player sees:** the bridge's lit strip takes the toll's accent colour and a toll chip appears on the ACROSS option. Preview equals result.
- **Counter:** the **Breach** Exploit waives one toll per run, and the player picks which. Staying in one tower pays no toll.
- **Determinism:** pure function of the rung and the player's choice. The Co-pay choice is a player decision.

### 3.3 Tower pressure ("Chart Fatigue")

- **Rule:** each tower has a pressure counter, 0–3.
  - A won combat in a tower adds +1 to that tower.
  - A crossing adds +1 to the destination tower.
  - A **Rest** sets its own tower to 0. Virus extends this to both towers (§4).
- **Effect:** a combat in a tower gets `enemy_damage_pct` = +10 % × pressure, **capped at +30 %**.
  - It sits in the same additive buff sum as enrage steps (R2/R4): total damage buff = 1 + 0.25 × enrage steps + 0.10 × pressure.
  - Worked case: enrage step 2 (+50 %) with pressure 3 (+30 %) gives ×1.8, so it is bounded and shown.
  - It is a buff, so it is tier-independent (R2). The tier damage factor (2.2 at T4) is applied first.
- **Delivery:** at the start of each combat the session writes `enemy_damage_pct` into `next_combat_overrides` (N16, with the NEW field).
- **What the player sees:** each tower's porthole rows tint from mint to amber with pressure, and a number badge sits on the tower's base. The tooltip on a combat node shows "+20 % enemy damage".
- **Why it makes UP vs ACROSS a real choice:**
  - Staying stacks pressure by fights won.
  - Crossing resets nothing and adds +1, plus a toll.
  - The player is trading a damage cost against a crossing cost. Ward's rests are the release valve for staying.
- **Crown:** pressure is ignored for THE GENOME CORE and resets to 0 there. Boss damage is controlled by its own draft.
- **Determinism:** counters live in run state and update only on combat finish or crossing. No RNG.

### 3.4 Lane character (the towers are different authored lanes)

- **Rule:** the kind layout in §2 is fixed. The tower decides which content pool each room draws from. The draw uses the `hq_graph` RNG stream, seeded once from the campaign seed at campaign start and checkpointed with the campaign.
- **Ward pools:** the Solace normals that heal or shield, using their post-design-pass versions only (Care Swarm, Dosage Dispenser, Compliance Officer). **The Triage Unit is excluded until its pass lands** (it is the worst heal offender). Ward events are clinical ("experimental treatment").
- **Billing pools:** the RAM-economy normals (Billing Daemon, Collections Agent, Compliance Officer). Billing events are contract-shaped ("sign the waiver").
- **What the player sees:** a cooler white-blue porthole tint for Billing and a green-white one for Ward. This is a tint only and is not the route lime.
- **Retry:** the same seed is reused (§7), so a returning player knows what each room holds.

## 4. Node kit

| Node | Standard | Solace HQ twist |
|---|---|---|
| Fight | Router combat | A single phase (3–4 turns), T4 band. Pressure damage (§3.3). |
| Elite | Elite combat | 2-phase Solace elites, 6–8 turns. Only at A4 (Ward) and as the Rack in Billing. |
| Server Rack (B4) | GDD 4.2 optional layer-4 Rack | Elite-strength combat that banks Schematics and an Armory asset on capture. It is the only Rack in the HQ netrun, and Billing's pressure and risk pay for it. |
| Event | Terminal | Ward: a clinical event that heals about 12 HP (A5). Billing: contract events with a price. Existing event data. |
| Waiting Room (B2) | Event (puzzle) | A consent form with 3 clauses (see below). |
| Shop | Mainframe | Billing: stock +1 slot, prices +20 %. A heal item is sold at both B3 and B6. |
| Rest | NEW node kind (D4 ruling) | Heal 40 % of max HP, **or** swap Firmware locations (the D4 rest options). Also resets that tower's pressure to 0 and clears one CORRUPTED slice. |
| Mini-boss (L8) | Mini-boss | The Account Manager (working name), 2 phases, fixed here, mandatory. Kill reward: a 40 % heal plus a rare Daemon draw and one Armory asset. |
| Crown | Boss | THE GENOME CORE (working name), always last. |

**Waiting Room (a puzzle, not a fight):** each clause grants one reward (a Firmware, a Cycles bundle, or a heal) and adds a debt. The debts are:
- Debt 1: the boss fight starts with 1 CORRUPTED slice.
- Debt 2: the boss fight starts with 1 less RAM.
- Debt 3: the boss's first phase has +10 % max HP.

Rules:
- At most 3 clauses, and the player may sign none.
- The total debt is shown on the crown's halo and in the form's preview, so the worst case is predictable.
- Debts apply through `next_combat_overrides` (N16) when the crown fight starts.

### How each owned Exploit pays off inside this HQ (D5)

Each key also keeps its R7 role against the boss's buffs (the boss draft owns that). Inside the ladder:

- **Intel (pricing memos):** the full ladder is READ, so the player can plan the whole climb from the gate.
- **Breach (kill-switch):** waives one toll of your choice per run.
- **Virus (open-source patch):** any Rest resets *both* towers' pressure to 0.
- **Each key not in the run's drawn subset (R7)** leaves its benefit out. A player with 0 keys still has a full ladder, and a read horizon of rung + 2.
- Because a Grid draws a subset per run, the HQ's set of advantages differs between runs.

**Puzzles vs mini-fights:**
- The Waiting Room and the tolls are decision puzzles with known costs.
- Everything else resolves in combat.

## 5. Pacing & difficulty curve

**Targets (T4 assumptions, the HQ is the endgame):**

| Item | Number |
|---|---|
| Layers | 10 (gate, 8 rungs, crown) |
| Nodes on a path | 10 |
| Combats per path | Ward: 3 normals + 1 elite + mini-boss + boss = 6; Billing: 2 normals + Rack + mini-boss + boss = 5 |
| Normal / Elite / Rack | 3–4 turns (~1.5 min) / 6–8 turns (~3 min) / 6–8 turns (~3 min) |
| Mini-boss (Account Manager) | 6–8 turns (~4 min) |
| Boss (Genome Core) | 12–20 turns (~7 min) |
| Non-combat nodes | 2 rests + 1 event (Ward), or 2 shops + 2 events (Billing), about 1 min each |
| **Expected total** | **~22–25 min** (about 1.5× a normal netrun) |

- **Tier:** normals use the R2 T4 band (56–70 HP) and elites the T4 band (112–144 HP).
- **Mini-boss rule gap:** R2 has no T4 mini-boss band (n/a). I use the **2-phase T3 HP band (88–112, take ~105) with the T4 damage factor (2.2)**, and say so as a Q.
- **Enrage:** class defaults (R4). Mini-boss and boss start at turn 10, then every 5 turns, +25 % each. Pressure adds to the same buff sum (§3.3).

**HP walk (operative HP 55; intake per fight from the R2 intake targets: a normal ~9, an elite or Rack ~25, the mini-boss ~32; heals capped by missing HP):**

*Ward path (pure UP):*
- 55 → F1 −9 → 46 → F2 −9 → 37.
- Rest (rung 3) heals 18 → 55.
- Elite (rung 4) −25 → 30.
- Event (rung 5) +12 → 42.
- Rest (rung 6) +13 → 55.
- F (rung 7) −9 → 46.
- Account Manager −32 → 14.
- Kill heal +22 → 36 of 55 (~65 %).
- Enter the boss at ~36 HP, without counting pressure (up to +30 % on the first 5 fights).

*Billing path (pure UP):*
- 55 → F1 −9 → 46.
- The Waiting Room clause may heal +10 → 55.
- Shop 3 (heal item, ~35 Cycles with the +20 % premium) → 55.
- Rack −25 → 30.
- Event (contract) ±0.
- Shop 6 (a second heal item) → 55.
- F (rung 7) −9 → 46.
- Account Manager −32 → 14.
- Kill heal +22 → 36.

Both towers reach the boss near 36 HP. Billing gets there by paying Cycles, and Ward by tolerating more fights. All HQ intake figures are placeholders pending the sim, and the margins are intentionally tight.

**Heat:** HQ combats add the standard Heat (Router 0, Elite +1). Tolls add none, since the Audit now acts on the next fight. A raid interrupt during the HQ run is allowed (GDD 4.4).

## 6. Rewards

Beyond the boss:
- **Server Rack (Billing only):** Schematics and an Armory asset, banked on capture. A Ward-only path misses this.
- **Mini-boss kill:** a 40 % heal, a rare Daemon draw and one Armory asset.
- **Waiting Room clauses:** a Firmware, a Cycles bundle or a heal each, in exchange for debts (§4).
- **First clear:** the Solace story beat (finale) plays, and THE GENOME CORE is recorded as defeated for this corporation's ICE ladder.
- **No unique profile unlock here.** The boss draft owns the profile reward.

## 7. Failure & retry

- **Death on a node:** the standard rule (GDD 4.2). The operative is permanently lost with everything unbanked, and the campaign gains 10 + tier Heat.
- **Retry:** the HQ layout and content picks are **the same** on the next attempt (the seed is fixed at campaign start). The player re-plans with what they learned: which rooms hold what, and where the tolls are.
- **State that resets:** pressure, debts, read horizon and the HP walk start fresh for the new operative.
- **Banked loot:** Server Rack assets and Schematics stay banked.
- **Mid-run exit:** the standard abandon rules (4.5). Quit-and-resume restores the ladder position through the normal run state.
- **Boss loss:** counts as operative death. Debts and pressure do not persist.

## 8. Systems needed

| # | System | Use here | Fallback |
|---|---|---|---|
| N2 | Tier tables | T4 bands for rooms; mini-boss uses the T3 HP band (a rule gap, see Q) | none; core |
| N3 | Phases | elites, mini-boss, boss | none |
| N4 | Enrage | defaults | none |
| N5 | Boss buffs and Exploits | the boss's counters; the three keys' ladder effects | read, waive and reset effects can be data on `ExploitData` fields |
| N16 | Next-combat overrides | debts, pressure damage | one number per fight via a plain modifier field |
| N16 (extension) | `enemy_damage_pct` field on the override payload | pressure | NEW field; data-only |
| N18 | Reward list data | mini-boss heal + Daemon + asset; Rack | hard-coded offers |
| D4 ruling | REST node | heal, Firmware swap, pressure reset, cleanse one slice | none; ruled in |
| NEW: Ladder graph | Two-lane layered graph, fixed authored kinds, 8 rungs, a sealed bridge at rung 7, a merged mini-boss node | none for this HQ. Data-only parts: the layout table, content pools, toll table |
| NEW: Read horizon | `read_horizon` run state and a per-room `unread` flag | UI-only (the graph is fully known to the client) |
| NEW: Toll edges | An edge attribute `toll_kind` with preview and resolution | A toll modelled as an event on the bridge edge (weaker preview) |
| NEW: Tower pressure | Run-state counters per tower, +1 on win and crossing, reset on rest | `next_combat_overrides` carries the result, one number per fight |

**Build order:**
1. REST node (D4); needed everywhere.
2. Ladder graph with its data tables (layout, pools, toll table).
3. Read horizon and the UNREAD flag.
4. Toll edges and previews.
5. Tower pressure through `next_combat_overrides` (needs the N16 field).
6. Exploit effects on the ladder (after N5).
7. Waiting Room event data and debts.
8. Playtest the HP walk once N19 metrics exist.

**Data-only parts:** the layout, pools, toll values, clause rewards, debts, heal sizes and the horizon bonus per Exploit.

## 9. Art hooks

The art must expose these per frame (as game-state inputs, not baked):

| State | Visual |
|---|---|
| `current_node` (tower, rung) | The lit window and bridge position (existing CURRENT) |
| `read_horizon` (an integer rung) | Frost decals on unread rooms; the wipe animation as it rises |
| `walked_nodes` | WALKED state (existing) |
| `tower_pressure[A/B]` (0–3) | The porthole tint from mint to amber, plus a number badge on the tower's base |
| `bridge_toll[rung]` kind (4 values) | A coloured accent on the bridge's lit strip (always visible); a toll chip on the ACROSS option |
| `sealed_bridge` (rung 7) | The floor-21 bridge drawn dimmed ("Staff Only"), with no ACROSS edge |
| `crossing_in_progress` | The camera walks the bridge in the orbit-and-rise beat |
| `mini_boss_pair` (rung 8) | Both rooms share the mini-boss frame colour and one state |
| `debts` (0–3) | Small pink pips on the crown's halo, which grows with debts (the halo is already in the art) |
| `rung_count` | 8 route floors (3–24), the crown on floor 27. No art change is needed. |

No mechanic here needs UI that breaks the bible rule: lime stays out of links and rings.

## 10. Q: open questions

Q: Should crossing cost both a toll and +1 pressure (as now), or one of them? If playtests show ACROSS is never worth it, the pressure is the first thing to drop.

Q: R2 has no T4 mini-boss band. Is "T3 HP band with the T4 damage factor" right for the Account Manager here, or should the HQ author a dedicated band?

Q: Is ~22–25 minutes right for the capstone, or should the HQ be shorter (7 layers)?

Q: Billing has no rest and heals only by paying Cycles. Should a Billing path be viable with 0 Cycles, or is that its intended risk?

Q: Should the Waiting Room's third debt (+10 % boss phase-1 HP) exist at all, or do debts only touch the player's start state?
