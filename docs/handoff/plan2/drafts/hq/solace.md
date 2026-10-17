<!-- draft via Message Batches API, claude-sonnet-5-5, batch msgbatch_01HADBSF5pLwaHAq7nbABzZa, custom_id hq__solace; status ok; tokens in 14369 cache-write 0 cache-read 32007 out 8197; cost $0.059. A DESIGN DRAFT for the designer's review: nothing here is built. -->

# Solace: HQ netrun draft

## 1. Concept & the named mechanic

**What the art shows:** two porcelain towers twist around each other through one full turn each, with glazed skybridges only on route floors. Every route floor has a room in each tower, and the climb ends in a crown holding THE GENOME CORE. Rooms above the read horizon are frosted (UNREAD).

**Restated as a game mechanic: THE LADDER.** The run is a climb of rungs, one per route floor. At each rung the player stands in a room of Tower A or Tower B and chooses **UP** (the same tower, next rung) or **ACROSS** (cross the bridge to the other tower, same rung, then continue up from there). Each tower is its own deck of room kinds, so choosing a tower is choosing a kind of climb.

Solace's disease theme gives the two towers fixed characters. The player is the infection climbing a treatment facility:

- **Tower A, "Ward":** the clinical tower. It has more fights and heals, and its rooms are fixed-layout.
- **Tower B, "Billing":** the financial tower. It has more shops, events and elites, and a pay-or-fight tax.

**Why no other HQ can be mistaken for this:**
- Only here does the player switch between two parallel lanes every rung (lateral choice).
- Only here does what you can see ahead depend on your own position (the READ rule).
- Only here does a bridge crossing carry a toll, and does a room's contents depend on what you have recently done in the other tower.
- Halcyon's eye, Meridian's shuttle, Orbital's gates and REBEL_CELL's mirror all act on the map from outside. Solace's ladder acts on the route itself.

**Spine rule:** every mechanic below is a property of the ladder: which tower you stand in, which rungs you can read, and what a crossing costs.

## 2. Structure

**Layer count: 9 rungs plus the crown (10 layers).** This exceeds the 7-layer standard, as D10 allows. Each rung has 2 nodes (A and B), except the entry and the crown.

**Floors:** the art has 27 building floors with route floors every third floor (3, 6 .. 24, which is 8 rungs). Adding the plaza gate gives a 9th rung at floor 27 (the crown floor), and the Genome Core is rung 10. The Godot port generates slots on demand (8.4 rule 5), so the game graph defines the rung count. The art must accept 9 rungs plus the crown. The preset's `route_floors` becomes `3·k` for k = 1..9, so the crown sits on the building's top floor, not above it.

| Layer | Name | Nodes | Content intent |
|---|---|---|---|
| 0 | Clinic Gate | 1 | Start, free. Pick a tower. Tutorial rule card. |
| 1 | Rung 1 | A1, B1 | Fights only (both). Learn UP vs ACROSS. |
| 2 | Rung 2 | A2, B2 | Fight / Event |
| 3 | Rung 3 | A3, B3 | Fight / Shop; **Waiting Room** option (see §4) |
| 4 | Rung 4 | A4, B4 | Elite / Event; **Server Rack (optional cache)** |
| 5 | Rung 5 | A5, B5 | Rest / Fight; **Mid-Boss: the Account Manager** on whichever tower you are not in (see below) |
| 6 | Rung 6 | A6, B6 | Elite / Shop |
| 7 | Rung 7 | A7, B7 | Fight / Event |
| 8 | Rung 8 | A8, B8 | Elite / Rest |
| 9 | Rung 9 | A9, B9 | Mini-boss gate (one of the two, see below) |
| 10 | Crown | 1 | THE GENOME CORE (boss) |

**Edges (the ladder rules):**
- From a node at rung r you may go **UP** to the same tower's rung r+1, or **ACROSS** to the other tower's rung r+1. Edges go to the *next* rung's node on either tower, and the crossing is expressed by which tower you pick.
- The art says ACROSS is the bridge on the *same* floor, then UP. To keep the graph a valid DAG for the existing map code, the game graph treats **ACROSS as an edge to the other tower's rung r+1 that passes through a bridge toll event** (see §3, Toll). In 3D the player walks the bridge at rung r and takes the stair up in the other tower. This is the same visual as the art, with only a graph encoding that fits layers.
- From the Clinic Gate, both rung-1 nodes are reachable.
- Both rung-9 nodes lead to the crown. The crown is not reachable from rung 8 directly.

**Fixed structure vs generated:** the layer count, the rung structure and the mini-boss and rest placements are fixed (hand-designed). The kinds in each room are drawn from each tower's seeded deck, weighted by the tower's character.

**Mapping onto landmark slots (per 8.4 rules 2 and 5):**
- Slot = (strand, route floor index). Rung r is assigned route floor `3r`.
- Within a rung, node order is A then B.
- Link geometry: UP = the stair up the outer edge of the front face. ACROSS = the bridge's front edge at the waist.
- **The mid-boss gets no special slot.** It is a normal elite-class room whose frame is the red kind colour.

**Mid-boss (rung 5, Account Manager gate):** the Solace mini-boss is not the HQ's end. In the HQ I use it as a **checkpoint elite**: at rung 5 the tower you are NOT standing in contains the Account Manager. You may bypass it by staying UP. If you cross ACROSS at rung 4→5, you enter *its* tower and fight it. This uses the working name from the mini-boss draft, with no new design. Beating it grants a Heat-free Exploit-adjacent reward (see §6).

**Mini-boss gate (rung 9):** both rung-9 rooms are guarded; one holds a second Solace elite pair (Recall Unit and Claims Adjuster as a 2-fight chain) and one holds the Account Manager if it was not already faced. So the player always fights the Account Manager once, but may choose when. If they already beat it at rung 5, both rung-9 rooms use the elite chain.

## 3. Unique mechanics

### 3.1 The READ rule (what you can see)

- **Rule:** you read rungs up to your current rung + 2 on both towers. Rooms higher than that are UNREAD: the kind is hidden and the room is frosted.
- **Trigger:** on arrival at each rung, the read horizon moves up by 1 rung.
- **Variation (the "Chart" key):** each Exploit owned adds +1 to the read horizon (see §4). Intel specifically reads the full ladder.
- **What the player sees:** frosted dimmed rooms above the horizon, with a "?" disc and UNREAD chip. As the horizon rises the frost clears in a wipe, driven by `read_horizon`.
- **Counter:** it is information, not damage. The counter is Intel, or scouting from the bridge: *standing on a bridge reads one extra rung* (Toll rule below), so crossing is also a scouting action.
- **Determinism:** the room kinds are drawn from the seeded decks at graph generation, so reading is only a reveal. No RNG at reveal time.

### 3.2 The Toll (crossing costs something)

- **Rule:** a crossing is never free. Taking ACROSS means walking the bridge at the current floor. The bridge holds a **Toll**, drawn from the table below by the bridge's rung number.
- **Trigger:** each time you choose ACROSS.
- **Which toll:** deterministic from `rung % 4`, so there is no RNG and the player can read it ahead.

| rung % 4 | Toll | Effect |
|---|---|---|
| 1 | Co-pay | Pay 8 Cycles, or lose 6 HP |
| 2 | Referral | Start your next fight with a CORRUPTED slice (1 slice, your wheel) |
| 3 | Audit | +2 Heat (Heat is the campaign meter; it persists on Death/retry per §7) |
| 0 | Quarantine | Your next fight starts with RAM at 4 instead of 6 |

- **Why it exists (Q3 in the art doc):** otherwise ACROSS is free and the ladder collapses to the best tower. A toll makes staying in one tower a real choice.
- **What the player sees:** the bridge glows its toll colour (data-driven `toll_kind`), and the toll chip appears on the ACROSS option before commit. Preview equals result.
- **Counter:** the Exploit **Breach** (Solace: the kill-switch key) waives one toll per crossing set (see §4). Stay in one tower to pay none.
- **Determinism:** pure function of the rung number and the player's choice.

### 3.3 Tower memory ("Chart Fatigue")

- **Rule:** each tower has a *pressure* counter. Every fight you win in a tower adds 1 to that tower's pressure. Every fight in a tower reads its pressure. Its next fights get +10 % enemy damage per pressure, capped at +40 % (enemy damage buff, tier-independent per R2).
- **Trigger:** on entering a combat node in a tower, the combat's `enemy_damage_pct` is set from that tower's pressure.
- **What the player sees:** a pressure meter on each tower's base (the porthole rows fade from green-white to a warning amber as pressure rises). A crossing resets the destination tower's visible read, but not its pressure.
- **Counter:** alternating towers resets neither pressure. It *spreads* it, so a zig-zag path takes lower pressure per tower at the cost of tolls. Resting in a tower sets its pressure to 0 (a rest node's "treatment").
- **Why:** it makes the climb a tradeoff between a toll cost (crossing) and a damage cost (staying). Neither side is dominant, so UP vs ACROSS is a real choice every rung.
- **Determinism:** counters are part of the run state, updated only on combat finish. No RNG.

### 3.4 Wing character (the two towers are different decks)

- **Rule:** the towers draw from different weighted kind tables, set at graph generation (stream `hq_graph` seeded by the campaign seed, a named RNG stream).
- **Ward (A):** fight 45 %, rest 20 %, event 15 %, elite 15 %, shop 5 %. Its fights use Solace's heal-flavoured normals (Triage Unit, Care Swarm, Dosage Dispenser).
- **Billing (B):** fight 30 %, shop 25 %, event 20 %, elite 20 %, rest 5 %. Its fights use the RAM-economy normals (Billing Daemon, Collections Agent, Compliance Officer).
- **What the player sees:** Ward's portholes are green-white, Billing's are cooler white-blue. This is a tint only, not the route lime. Rooms use the standard kind colours.
- **Counter:** this is the build's information. A bridge crossing is how a weak build gets to the other lane's rests or shops.
- **Determinism:** one RNG stream `hq_graph`, drawn once at generation and checkpointed with the campaign.

## 4. Node kit

| Node | Standard | Solace HQ twist |
|---|---|---|
| Fight | Router combat | Enemy kinds follow tower character (§3.4); pressure damage (§3.3). Normals are single phase (3–4 turns). |
| Elite | Elite combat | 2-phase Solace elites. Each elite awards a *Key Fragment*, 3 of which count as a tick of the read horizon (+1) once per run. |
| Event | Terminal | Billing events are contract-shaped ("sign the waiver"), Ward events are clinical ("experimental treatment"). Both use existing events. Event wheels (N17) are not needed. |
| Shop | Mainframe | Billing: stock +1 slot, prices +20 %. Ward has almost none. |
| Rest | NEW node kind (D4) | Heals 30 % of max HP, resets that tower's pressure to 0, and clears one CORRUPTED slice. Costs a turn of nothing: no other effect. |
| Waiting Room (rung 3) | Puzzle | A no-fight node: a *consent form* with 3 clauses. Each clause grants a reward and applies a debt that comes due in the Genome Core fight (a one-time listener, see §6). Data-only event with `next_combat_overrides` (N16). |
| Cache (rung 4, optional) | Server Rack | An elite-strength combat in the Ward tower; banks Schematics and an Armory asset. This is the layer-4 Rack in the standard netrun, kept as an option. |
| Mini-boss | Mini-boss | The Account Manager (working name), at rung 5 or rung 9 (§2). |
| Crown | Boss | THE GENOME CORE (working name), always last. |

### How each owned Exploit pays off inside this HQ (D5)

Each Exploit key grants a *special building* back in the city. Here, each key also changes the ladder:

- **Intel (pricing memos):** the full ladder is READ (the whole climb visible). Also, Intel reveals each tower's pressure and every toll before committing.
- **Breach (kill-switch):** one toll per run can be waived (the player picks which). Also, rung 5's mini-boss is optional (you may skip the fight by crossing a *Maintenance Duct*: an extra edge from rung 4 to rung 6 on the opposite tower, with an automatic Audit toll).
- **Virus (open-source patch):** Ward's rest nodes also remove the pressure of the *other* tower by 1. Also, the HQ boss's Sterile Field buff (see its draft) is countered if the Genome Core's Exploit list includes it.
- **Each key that is not in the player's pool** leaves its benefit out. A player with 0 keys still has a full ladder, just harder.
- Because a Grid draws a subset of Exploits per run (R7), this HQ's set of advantages differs between runs.

**Mini-fights vs puzzles:** the Waiting Room and the tolls are puzzles (decisions with a known cost). Everything else resolves in combat.

## 5. Pacing & difficulty curve

**Targets (T4 assumptions, the HQ is the endgame):**

| Item | Number |
|---|---|
| Rungs | 9 + crown |
| Nodes on a path | 11 (gate, 9 rungs, crown) |
| Fights per run (path) | 6–7 normals/elites, 1 mini-boss, 1 boss |
| Normal fight | 3–4 turns, ~1.5 min |
| Elite | 6–8 turns, ~3 min |
| Mini-boss | 6–12 turns, ~4 min |
| Boss (Genome Core) | 12–20 turns, ~7 min |
| Events / shops / rests | ~1 min each, 3–4 of them |
| **Expected total** | **~30 min** (about 2× a normal netrun; the HQ is the capstone) |

**Difficulty curve:** normals follow the R2 T4 band. Pressure and tolls scale the climb. The Genome Core is far harder than any room.

| Rung | Enemy mix | Pressure risk |
|---|---|---|
| 1–2 | Normals only, T4 | Low |
| 3–4 | Normals + first elite | Medium |
| 5 | Mini-boss gate or its bypass | High (optional) |
| 6–8 | Elites at 40 % of nodes | High |
| 9 | Elite chain or mini-boss | Very high |
| Crown | Boss | n/a |

**HP/Heat pressure:** HP carries between fights (GDD 4.2). The reference damage intake (R2) for a normal at T4 is ~5/turn, so a 3.5-turn fight costs ~18 HP. Over 6 non-rest fights that is about 110 HP of intake against operative HP of 45–60, so healing is essential.

**Rest/heal budget:**
- 2 Ward rests (30 % each) plus event heals give about 60–70 HP total across a pure-Ward path, which is enough.
- A Billing path has about 1 rest, so it relies on shops (a heal item is priced at the shop's +20 %) and is riskier.
- Crossing to rest costs a toll, so reaching a rest is a priced choice.

**Heat:** each HQ fight adds standard Heat (Router 0, Elite +1). Audit tolls add +2. A pure-Ward run, with Heat mostly flat, is the low-Heat route.

**Enrage:** no change from the class defaults (R4).

## 6. Rewards

Beyond the boss:

- **Per-run:** Schematics from the Cache (banked), plus the standard banking at the crown.
- **Key Fragments:** collect 3 from elites for one extra read-horizon step (fixed this run only). This is a run-level reward, not carried over.
- **Mini-boss kill:** a rare Daemon draw plus one Armory asset.
- **Waiting Room clauses:** each accepted clause grants one reward (a Firmware, a Cycles bundle, or a heal), and adds a *debt* tag listened to by the boss encounter. Debts are rewards with a price. The boss fight's `next_combat_overrides` (N16) applies a modifier (e.g. start with one CORRUPTED slice). Maximum 3 debts, so the worst case is predictable and shown on the preview.
- **First-clear:** the Solace story beat (finale) plays, and *the Genome Core* is recorded as defeated for this corporation's ICE ladder.
- **No unique profile unlock** here. The boss's own draft owns the profile reward.

## 7. Failure & retry

- **Death on a node:** the standard rule (GDD 4.2). The operative is permanently lost with everything unbanked, and the campaign gains 10 + tier Heat.
- **Retry:** an HQ netrun is *not* reset. The next attempt gets a **fresh seeded graph** (new seed from the campaign `hq_graph` stream), so the player re-plans. Pressure and tolls are rebuilt from the new seed.
- **Mid-run exit:** the standard abandon rules (4.5). There is no checkpoint saving of ladder position except the normal quit-and-resume state.
- **Banked loot:** Cache assets and Schematics stay banked.
- **Heat effects:** unchanged. The HQ adds Heat only through Elite fights (+1 each) and Audit tolls (+2). A raid interrupt during the HQ run is allowed (GDD 4.4).
- **Boss loss:** counts as operative death. Because the run is long, the audit and debt rules carry no persistence beyond the run.

## 8. Systems needed

| # | System | Use here | Fallback |
|---|---|---|---|
| N2 | Tier tables | T4 bands for all rooms | none; core |
| N3 | Phases | elites, mini-boss, boss | none; required |
| N4 | Enrage | defaults | none |
| N5 | Boss buffs and Exploits | the Genome Core's buffs, and Exploit keys changing the ladder | read/toll effects can be data on `ExploitData` fields |
| N16 | Events altering future fights | Waiting Room debts, pressure damage via `next_combat_overrides` | Debts as a plain modifier field on the node |
| N18 | Reward list data | Key Fragments, mini-boss rewards | hard-coded offers |
| NEW: Ladder graph generator | Two-lane graph with UP/ACROSS edges, 9+ rungs, per-tower decks, a fixed mini-boss/rest/cache placement | no fallback; replaces the 7-layer generator for this HQ only. Data-only parts: tower weights, toll table, rung layout |
| NEW: Read horizon | `read_horizon` run-state, Exploit modifiers, per-room `unread` flag | UI-only if the graph is fully known to the client (it is) |
| NEW: Toll nodes | An edge attribute `toll_kind` with preview and resolution | Could be modelled as an event node on the bridge edge; weaker preview |
| NEW: Tower pressure | Run-state counters per tower, feeding an enemy damage percent | `next_combat_overrides` can carry it, one number per fight |
| NEW: REST node (D4) | Heal, pressure reset, cleanse one slice | None; it is already ruled in by D4 |

**Build order:**
1. REST node (D4); needed everywhere.
2. Ladder graph generator with the data table (towers, tolls, rungs), plus slot generation for N rungs.
3. Read horizon and the UNREAD flag (art can drive frost from it).
4. Toll edges with previews.
5. Tower pressure through `next_combat_overrides` (N16).
6. Exploit effects on the ladder (§4), after N5.
7. Waiting Room (event data).
8. Playtest the rung curve once N19 metrics are in.

**Data-only parts:** tower kind weights, the toll table, the rung layout, room contents, Key Fragment counts and the Waiting Room clauses.

## 9. Art hooks

The art must expose these per frame (as game-state inputs, not baked):

| State | Visual |
|---|---|
| `current_node` (tower, rung) | The lit window and bridge position (existing CURRENT) |
| `read_horizon` (an integer rung) | Frost decals on unread rooms; the wipe animation as it rises |
| `walked_nodes` | WALKED state (existing) |
| `tower_pressure[A/B]` (0–4) | The porthole tint from mint to amber on that tower (base to current floor) |
| `bridge_toll[rung]` kind (4 values) | A coloured accent on the bridge's lit strip, visible only when the rung is read; a toll chip on the ACROSS option |
| `crossing_in_progress` | The camera walks the bridge in the orbit-and-rise beat |
| `mini_boss_room` | The elite frame colour on the Account Manager's room |
| `debts` (0–3) | Small pink pips on the crown's halo, which grows with debts (the crown's pink halo is already in the art) |
| `rung_count` | The landmark builds slots for 9 route floors on demand (rung r at floor 3r; the crown on floor 27) |

**Art change flagged:** the art builds 8 route floors on 27 floors. The 9th rung is at floor 27, which is the crown floor. Either the crown moves up one floor, or the preset gets 28 floors. This is a small art ask: the slot generator takes N rungs.

No mechanic here needs UI that breaks the bible rule: lime stays out of links and rings.

## 10. Q: open questions

Q: Does the Account Manager appear once (either rung 5 or 9), or is it always at rung 9 with rung 5 being an elite only? One fixed position is simpler for balance.

Q: Are tolls shown on the route before the player commits at every rung, or only on rungs inside the read horizon? I chose the read horizon, so scouting has value, but a blind toll may feel unfair.

Q: Should Tower pressure also affect the Genome Core fight (a boss at +40 % damage would be too harsh), or reset at the crown? I assumed it resets at the crown.

Q: Is 9 rungs (about 30 minutes) acceptable, given the HQ's role as the campaign capstone, or should it be 7 for a typical session?

Q: Should the HQ's tower decks use only Solace's normals, or can the Waiting Room's debts bring in a cross-corporation foreshadow (Meridian, per the Hostile Takeover story path)?

Q: Who owns the toll rule table: this HQ, or should future HQs reuse tolls on their own links? I kept it unique to Solace.
