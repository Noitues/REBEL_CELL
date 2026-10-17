<!-- draft via Message Batches API, claude-sonnet-5-5, batch msgbatch_01TQsqGnerTdLwJEata9mp6i, custom_id v2__hq__rebel_cell; status ok; tokens in 13721 cache-write 0 cache-read 32585 out 21806; cost $0.126. A DESIGN DRAFT for the designer's review: nothing here is built. -->

## Changes vs v1

- **Issue 1 (BLOCKER, node count and structure):** The count is now stated correctly. There are 9 steps × 3 lanes, and each lane offers 2-3 nodes per step, of which the operative takes one. Per-lane options are 2+3+2+2+3+3+2+1+1 = 19, so the map draws 57 nodes and the three operatives resolve 27. The "27 nodes" claim and the "8 route layers + switch" wording are gone. "A step is three nodes" is replaced by "a step is one chosen node per lane."
- **Issue 2 (BLOCKER, clock and STALL contradiction):** The old model, with a lane that waits, a detour that costs +1 step and an "out of step" dial, is deleted. Lanes are now indexed by step slot and can never drift apart.
  - A step closes when every lane has resolved its chosen node or spent a STALL token.
  - STALL means that lane's node for the step is "idle": nothing happens, no heal, and the route advances. The old "hold in place" meaning is dropped.
  - A detour is a two-slot node in its own lane only, and it replaces the layer it spans.
  - The lone-throw and backlash rule is removed (see issue 5).
- **Issue 3 (BLOCKER, counter selector and Mirror dependency):**
  - The "most-used Firmware" selector, the use-count stat and the "profile scrub" shop service are all removed.
  - The countered lane is `perm[step mod 3]`. `perm` is a permutation of the three lanes drawn at graph build from the checkpointed `map` stream.
  - The counter is visible one step ahead as the baseline. Intel shows the whole schedule from run start. I did not make the full schedule visible by default, because then Intel would have no payoff.
  - The Mirror modifier is tagged **NEW: mirror_fight**. Its data-only fallback is an authored REBEL_CELL elite placed on the countered fight nodes at build time.
- **Issue 4 (BLOCKER, relay and N16):** The relay now writes a node-keyed `combat_overrides` entry on the next lane's fight nodes at the next step.
  - The −10 % HP effect is a PERCENT edit of the enemy's own max HP (N1 semantics, R2). Phase thresholds scale with it.
  - It is not run-level routing. This needs N16 plus a small extension, noted in §8.
  - "No fallback" and "weaker fallback" are reconciled. The primary is the result-driven relay. The fallback is a static, authored modifier per node, with no result dependence.
- **Issue 5 (MAJOR, lone pair):** The lone-pair penalty is now "boss enrage start −2 turns (N4), and the dead lane's parked passive is lost." There is no phase skip and no +25 % damage. The lone-throw backlash is removed rather than fixed, because lockstep slots make a lone throw impossible. The critic's 8 × `enemy_damage_by_tier` fix is therefore moot. I record this as a deviation from the critic's fix: removing the case was cleaner than keeping it.
- **Issue 6 (MAJOR, parked support):**
  - Parked passives are data rows only. The per-phase hit redirect is dropped, so parked operatives take no damage.
  - Breaker's unscaled +10 % OVERFLOW becomes a flat +2 damage on ON_PERFECT.
  - Botnet's hub-level drone cap becomes a DEPLOY_DRONE at combat start.
  - Rigger gets +1 RAM per turn, and Ghost is unchanged (an existing core effect).
- **Issue 7 (MAJOR, Virus and CORRUPTED on enemy wheels):** Removed. Virus now sets the boss's `enrage.start_turn` +3, which is plain N4 data. The invented "disabled one turn in two" text is deleted, and Q3 is no longer a dependency of this draft.
- **Issue 8 (MAJOR, win and failure semantics):** §6 and §7 now define each case.
  - A showdown win is the campaign win.
  - A showdown loss ends the run, the entering operative follows GDD 4.2, the two parked ones return, and the HQ netrun stays open.
  - Lane-death Heat is per death, per GDD 4.2, and is separate from the +10 node-Heat cap.
- **Issue 9 (NIT):**
  - The Hack start rotation is drawn at build from the `map` stream and stored in the node, so there is no play-time draw.
  - Spelling is now US ("synchronized").
  - Run length is now budgeted against the ~395-minute campaign target. I also recomputed it, because v1's 12.25 min per lane did not match its own path.
- **Critic Qs:**
  - The minimum crew is carried as a Q.
  - Heat per death is answered (per death).
  - The per-step save is stated: the step boundary is the checkpoint.
- **Kept, because the critic marked them strong:** the three-lane synchronization spine, the previewed countered room, the per-Exploit payoffs and the §9 state table. The Exploit payoffs themselves were changed as described above.
- **Detour placement:** I moved detours from steps 2, 5 and 7 to steps 2 and 6, so a detour never skips the mandatory switch-prep room.

---

# REBEL_CELL: HQ netrun draft

Working names: the final run is "the Undercroft run," the boss is "DISPATCH core" (the Sync Strike pass, referenced by working name only), and the three lanes are Roofs, Alley and Tunnel.

## 1. Concept & the named mechanic

**What the art shows.** There is no tower. The district is an ordinary Tokyo-alley block grid, cut along one street line into a side-view section with three stacked lanes: roofs (L), the alley at street level (C), and the service tunnel under the street (R). A sunken service street, THE UNDERCROFT, lies below the tunnel. The window sequence `SEQ` (0 before, 1 blackout, 2 spreading, 3 full red) tints the fist drawn in windows. `PULSE` makes the fist's line blocks glow. The MAINFRAME red sign stands at the target and marks DISPATCH.

**As a game mechanic.** This is the only HQ netrun where **you run three operatives at once, one per lane, on one shared clock**.
- The run is a **district of three parallel lane-routes** that advance in lockstep. One step means every lane resolves one node.
- Each lane ends at a **kill switch**. All three operatives must arrive alive to throw them together.
- The fist on the map is the run's progress meter. It starts hidden and ends full red. `SEQ` is computed from step and strike state, never from time.

**Why it can't be mistaken for another HQ.**
- Solace is one climb and Halcyon is one climb under an eye.
- Orbital is a countdown with doors, and Meridian is a moving shuttle.
- Only the Undercroft run has three simultaneous routes that feed one another. It also spends three operatives' HP and ends in a convergence: two operatives park as support and one enters DISPATCH core.

**Ruling basis.** G12 and D10 say every HQ run is unique and may exceed 7 layers. Sync Strike is a pending design pass. This draft proposes one coherent answer to its open questions (turn order, HP, deaths, support, decks) for the designer to accept, change or reject. Proposals are marked **(Sync Strike)**.

## 2. Structure

### 2.1 Layer count and shape

- **9 steps × 3 lanes.** Each lane offers 2-3 nodes per step and the operative takes one. The drawn nodes per lane are 2+3+2+2+3+3+2+1+1 = 19, so the map shows 57 nodes and the player resolves 27.
- **Three acts:**
  - **Steps 1-3, INFILTRATE.** Standard-strength fights, no coupling.
  - **Steps 4-6, BLACKOUT.** The relay (3.2) and the counter (3.3) begin, and `SEQ` goes 1, then 2.
  - **Steps 7-8, CONVERGE.** Elite-class content. Step 8 is a mandatory switch-prep elite in every lane.
  - **Step 9, SWITCH and SHOWDOWN.** The three operatives throw together, and one enters DISPATCH core.

### 2.2 Per-lane layer map

```
STEP  options per lane (same shape in L Roofs/BREAKER, C Alley/GHOST, R Tunnel/RIGGER)   coupling
 1    F  F                                                    none
 2    F  E  DetourA(Cache vault, spans 2-3)                   none
 3    F  Rest                  (not on detourA's path)        none
 4    F  Ev                                                   relay + counter begin, SEQ 1
 5    F  Shop  Hack                                           relay
 6    E  Rest  DetourB(Elite vault, spans 6-7)                SEQ 2
 7    E  Ev                    (not on detourB's path)        counter
 8    SW-prep elite (single)                                  SEQ trending 2
 9    KILL SWITCH (single)  ->  SHAFT -> DISPATCH core
```

Legend: F = Router fight, E = elite, Ev = event, Hack = puzzle (section 4), Detour = a two-slot node (2.3), SW-prep = switch-prep elite.

Edges are ordinary branching: each node connects to 1-2 nodes in the next step's list. A detour node connects to the node two steps later (3→4 for A, 7→8 for B).

### 2.3 Detours: two-slot nodes in one lane

- A detour node occupies **two consecutive step slots in its own lane only**.
  - Slot s resolves its fight.
  - Slot s+1 resolves its reward room.
- It **replaces** the layer it spans, so lanes never drift out of step.
- The trade is a fight plus a guaranteed reward against skipping that layer's Rest or other options:
  - **DetourA** (step 2-3): a Router fight, then a Cache with a guaranteed Firmware. It skips step 3's Rest or fight.
  - **DetourB** (step 6-7): an elite, then a Daemon room. It skips step 6's Rest and step 7's elite, event or alternate.
- In the art, detours sit in HUT rooms (Roofs, a raised roof hut) and DEEP rooms (Tunnel, the Undercroft pit). The Alley's detour is a back room off the street.

### 2.4 Mapping onto the landmark slots

The art rule (8.4, C15) assigns topology to slots in layer order, then node order. The landmark generates slots on demand.
- **Slot classes:** ROOF, STREET, TUNNEL, HUT (Roofs detour), BACKROOM (Alley detour), DEEP (Tunnel detour), SWITCH (fixed column), SHAFT (fixed, joins the three levels).
- **Assignment:** lane L takes ROOF slots, lane C STREET slots and lane R TUNNEL slots, in layer order, then node order. Detour nodes take HUT, BACKROOM or DEEP slots, and a two-slot detour uses one room that spans two columns.
- **Link geometry:** same-level steps are horizontal edges along the street line. A detour is a rising (L), side (C) or falling (R) edge. The shaft is vertical.
- **Slot generation on demand:** the section picks a street line, a run of lots long enough for the graph (at least 9 columns per lane), and a target lot (DISPATCH, under the MAINFRAME sign). If lots are fewer than columns, the camera slides east each step (the art's DECISION beat) and extra columns wrap onto further lots.
- **The countered room** (a preset id in the art) becomes game state: one fight node per step, derived from `perm` (3.3).

## 3. Unique mechanics

### 3.1 The shared clock (the Sync Strike spine)

- **Rule:** all three lanes share one step counter. Each step, the player picks one node per lane from that lane's options and confirms. The three nodes then resolve **in lane order L, C, R** (fixed, no RNG).
  - Only one fight is on screen at a time.
  - Non-fight nodes (event, shop, rest, Cache, Hack) resolve instantly in the same order.
  - **The step closes when every lane has resolved its node or spent a STALL token.** No lane waits or runs ahead.
- **STALL:** instead of a node, a lane may spend a STALL token. The operative idles in its room that step (no fight, no heal, no reward) and the route advances to any exit of its last node.
  - **Use:** slip past a countered or unaffordable fight.
  - **Source:** a Rest node (instead of its heal), a Cache reward, or the step-5 shop at 40 Cycles.
  - **Cap:** 2 held.
- **Detours** take two slots in their lane only, so lane position is always the step number.
- **Sync dial:** shows the step number and each lane's operative HP. At step 9, if all three are alive and standing at their switches, THROW is enabled (3.4).
- **Turn order (answers art Q1):** all three lanes choose at once, then resolve in lane order.
- **Determinism:** no RNG in the clock. The fights use the normal netrun combat streams. Saves: the step boundary, after all three nodes are resolved, is the checkpoint.
- **What the player sees:** three route strips, the step dial and held STALL tokens.
- **Counters:** STALL, detours and the node choices.

### 3.2 The relay: lanes feed each other (BLACKOUT onward)

- **Rule:** from step 4, each fight's result writes a modifier onto the **next lane in the ring L → C → R → L**:
  - **Clean win** (no NULL slice resolved): the next lane's fight starts the player with +2 RAM.
  - **Perfect-heavy win** (at least 2 Perfects): the next lane's enemy starts with max HP −10 %. This is a PERCENT edit of the enemy's own max HP, so phase thresholds scale with it, and R2 and N1 semantics hold.
  - **Rough win** (the operative lost more than 15 HP): the next lane's enemy gets +1 resistance for that fight.
- **Timing:** a lane's result at step s writes a node-keyed `combat_overrides` entry on the fight nodes among the next lane's **step s+1 options**. The chip is visible before the player chooses. A lane that picks a non-fight node loses the modifier.
- **Why:** a strong lane helps a weak one, and a bad fight hurts the neighbor. The three lanes feel like one system.
- **What the player sees:** relay arrows on the lane gaps. The art's LINE blocks pulse (`PULSE`) when one fires.
- **Counter:** fight cleanly, or STALL the next lane's fight away.
- **Determinism:** the relay reads a finished fight's tallies (deterministic) and writes one entry. No RNG.
- **Dependency:** N16, plus a small extension to key `combat_overrides` by node id. **Fallback:** authored static modifiers per node at graph build (no result dependence).

### 3.3 The Counter: DISPATCH answers one lane per step

- **Rule:** the graph build draws `perm`, a permutation of the three lanes, from the `map` stream (checkpointed). At steps 4-8, the countered lane is `perm[step mod 3]`.
  - That lane's **fight nodes** that step become **mirror fights**: the enemy uses the operative's own wheel at ×1.5 output with one pointer (the M11 rule for REBEL_CELL elites).
  - Non-fight nodes in that lane are unaffected. This is the dodge: a Rest or a STALL avoids the counter.
- **Visibility:** the countered lane for the next step is shown one step ahead, marked "COUNTERED" on its fight nodes. Preview equals result, and nothing is hidden. Intel reveals the full schedule from run start.
- **What the player sees:** a faint red outline on the countered fight nodes, and the MAINFRAME sign's light cone leaning toward that lane (cosmetic; the sign itself stays on the DISPATCH lot).
- **Counter:** pick a non-fight node, STALL, or accept a tougher fight with the relay's help.
- **Determinism:** `perm` is fixed at build and is a pure function of the `map` stream.
- **Dependency:** **NEW: mirror_fight** (a combat flag using the operative's wheel at ×1.5 and one pointer). **Fallback (data-only):** an authored REBEL_CELL elite (the `rc_template_elite` family) placed on the countered fight nodes at build.

### 3.4 The kill-switch throw

- **Rule:** at step 9, if all three operatives are alive, each stands at a switch and the player presses **THROW**. All three throw at once and the shaft opens.
- **A lane dead before step 9 (Sync Strike Q3):**
  - **One death:** the lane goes dark. The other two throw as a **lone pair**, which costs the boss fight: **boss enrage start −2 turns (N4)** and the dead lane's parked passive is lost.
  - **Two deaths:** the strike fails and the run ends in retreat (section 7).
- **SEQ:** before the throw it is 2. A successful throw sets it to 3 (full red) and `PULSE` fires on all line blocks. A failed strike drops it to 1.
- **Determinism:** pure state, no RNG.

### 3.5 The showdown (who enters DISPATCH core)

- After a successful throw, **the player chooses one operative to enter; the other two park** at their switches.
- **Parked support (art Q4):** each parked operative contributes a class passive for the whole boss fight. These are data rows (values placeholder):
  - Breaker: +2 damage on each Perfect (ON_PERFECT).
  - Ghost: the first nudge each turn is free and ignores resistance (the existing Ghost core).
  - Rigger: +1 RAM per turn.
  - Botnet: 1 drone docked at combat start (DEPLOY_DRONE, ON_COMBAT_START).
- Parked operatives take no damage and no new rule is needed. This keeps the pair relevant without a second wheel, a hit redirect or a preview change.
- **Entering the fight:** the chosen operative brings its own HP and deck.

## 4. Node kit

Each operative has its own HP and RAM, carried across steps as in a normal run (answers art Q2). Cycles and Schematics are one shared pool. Each operative keeps its own deck (art Q6), because each is a different class with a different wheel.

| Node | Standard behavior | Undercroft twist |
|---|---|---|
| Fight (Router) | 1 phase, 3-4 turns | REBEL_CELL normals at T4 (cell informant, dead drop, echo process, handler proxy, loyalty test, mirror script). |
| Elite | 2 phases, 6-8 turns | REBEL_CELL elites. Step 8 is a mandatory switch-prep elite in every lane. A detour elite (DetourB) also pays a Daemon. |
| Event | Choice node | Events carry a lane tag. An event may grant a STALL token or write a relay-style modifier on another lane. Impromptu fights use N16. |
| Shop (step 5) | Cycles | Firmware and Daemons as usual, plus a **STALL token for 40 Cycles**. |
| Rest | Heal | Heals that operative 30 % max HP, or grants a STALL token instead of the heal. Not both. |
| Cache | Reward node | A guaranteed Firmware (DetourA's second slot, and the step 7 alternates). |
| Hack (puzzle) | New node type | A no-combat puzzle (below). |
| Kill switch | The step 9 node | Not a fight (3.4). |

**Hack puzzle (step 5 option).**
- The player gets a mini-wheel of 6 slices and a target landing (a named slice at Good or better). They must hit it with nudges only, a 2-nudge budget and no cards.
- The start rotation is drawn at graph build from the `map` stream and stored in the node, so there is no play-time draw.
- Success grants a relay boost (the next lane's first fight starts with the enemy at max HP −15 %) and extends counter visibility to two steps ahead. Failure costs nothing but forfeits the boost. It is a puzzle, not a mini-fight.

**Mini-fights vs puzzles.** The Router, elite and switch-prep are fights. The Hack is the only puzzle. Events are narrative choices, and the switch is a coordination step.

### 4.1 Exploits as keys (D5)

Each held Exploit type pays off once inside this HQ:

- **Intel (pricing memos, district schematics):**
  - Shows the whole counter schedule from run start.
  - Makes every Hack node a free success.
- **Breach (override keys):**
  - Each lane's step 8 switch-prep elite is replaced by a Router fight (a side door opens).
  - It still counts as a combat for relay writes.
- **Virus (a payload that corrupts DISPATCH):**
  - Sets the boss's `enrage.start_turn` +3 turns (N4).
  - It does not use CORRUPTED on enemy wheels, so it needs no Q3 ruling.
- **Entry gate:** `min_exploits_for_breach = 3` stays. The three payoffs above are fixed-type bonuses, so owning all three types is the easiest run. Whether any 3 of the drawn Exploit subset open the breach is the V2 Q5 ruling and is not decided here.
- **Boss buffs:** DISPATCH core's Exploit-countered buffs (R7) come from the Grid's drawn subset and are passed in as run state. The HQ run does not re-roll them.

## 5. Pacing & difficulty curve

**Assumptions:** T4 content. The R2 reference player does about 18 damage per turn at 0.5 min per turn (placeholder). The R2 T4 bands are 56-70 HP for a Router and 112-144 HP for an elite, which gives about 3.5 turns for a Router and 7 for an elite.

- **Typical lane path** (steps 1-9): F, E, Rest, F, Shop, Rest, E, SW-prep elite, switch. That is 2 Routers and 3 elites, so 5 combats per lane and **15 combats in all**, plus the boss.
- **Time per lane:** 2 × 1.75 + 3 × 3.5 = 3.5 + 10.5 = **14 min**. Three lanes make **42 min**. Non-fight nodes and step confirmations add about **10 min**, so about 52 min. The boss at 12-20 turns adds 6-10 min, for **~58-62 min**.
- **Campaign budget:** the minimum path is 8 runs at about 15 min each (120 min). This finale replaces the last 15-min run and adds about 45 min. That is about 11 % of the ~395 min campaign target.
- **HP pressure** (50 HP operative, 30 % rest heal):
  - Per lane: 2 Routers at 8-12 and 3 elites at 15-25 gives about 61-95 HP of damage.
  - Healing: two Rests give +60 % of 50, or +30 HP.
  - Net: roughly 80 HP of resources against 61-95 HP of damage. **Tight by design.** The relay, non-fight picks on counter steps and STALL soften it.
- **Heat:** the standard per-node Heat table applies, but **elites inside the HQ add no Heat**, and node Heat is capped at +10 for the run. Death Heat (10 + tier per death, per GDD 4.2) is separate and uncapped. **Raids do not interrupt the HQ run.** A threshold crossed mid-run queues its raid, which resolves when the run ends.
- **Curve:** INFILTRATE is easy and uncoupled. BLACKOUT teaches the relay and the counter. CONVERGE tightens with elites, and step 8 is the peak before the boss.

## 6. Rewards

Beyond the boss's own drop:
- **Campaign win:** a showdown win is the campaign win (GDD 1.3: breach the final server with enough Exploits).
- **Profile unlocks:**
  - The REBEL_CELL ICE ladder progress ("final final" track).
  - A profile cosmetic: the red-fist skin on the home server.
  - A **lane trophy:** one class alternative (`UnlockKind.CLASS_ALTERNATIVE`) per operative who reached a switch alive.
- **Run rewards:** unspent Cycles convert to Schematics at 10:1. Each switch reached by a living operative banks +10 Schematics (placeholder).
- **Story:** the DISPATCH finale (fully voiced) plus one bonus beat per operative class that took part (it foreshadows Ghost Patient).
- **Clean strike bonus:** finishing with no STALL token spent and no lone pair gives a one-time Daemon from the REBEL_CELL pool (placeholder).

## 7. Failure & retry

- **Operative death during the run (GDD 4.2):** death is permanent for that operative, and the campaign gains 10 + tier Heat **per death**.
  - **One death:** the lane goes dark and the run continues. The lone-pair rule applies at the switch (3.4).
  - **Two deaths:** the strike fails and the surviving operative retreats to HQ at its current HP, keeping its deck. The run ends.
  - **Three deaths:** same as two, with no survivors.
- **Failed showdown:** the entering operative follows GDD 4.2 (dies, 10 + tier Heat). The two parked operatives return to HQ at their current HP. **The run ends and the HQ netrun stays open.** A retry is a new run with a fresh seeded graph and a new entering operative.
- **What persists across retries:** the boss's phase layout and the campaign's Exploit subset are fixed per campaign, so learning carries over.
- **Mid-run raid:** queued and resolved when the run ends (section 5). A campaign win voids any queued raid.
- **Abandon (GDD 4.5):** it kills every operative on the run (three deaths here, so three times the death Heat).
- **Heat on failure:** only the standard death Heat applies.

## 8. Systems needed

| # | Use here | Fallback without it |
|---|---|---|
| N1 | PERCENT max-HP edit in relay overrides | Fixed enemy HP per node |
| N2 | Tier-band HP for REBEL_CELL normals and elites at T4 | Use today's values |
| N3 | Phases and threshold parking for elites and the boss | Required for the boss; none for Routers |
| N4 | Enrage fields: the Virus +3 and the lone-pair −2; HQ elites on class defaults | Skip both rules |
| N5 | Boss buffs and Exploits, passed in as run state | Boss runs unbuffed |
| N6 | Echo listeners on mirror enemies | Data-only mirror elites without Echo |
| N11 | Uneven needles on elites | Even needles |
| N13 | Fixed satellites in some elites | Skip |
| N16 | Node-keyed `combat_overrides` for the relay; events that start fights | Static authored modifiers per node (3.2) |
| N18 | Reward rows for the clean strike Daemon and the switch bonus | Hard-coded rewards |
| N19 | Sim metrics (turns per step) | Skip |

**NEW systems:**
1. **NEW: Multi-operative run (Triple Run).** The netrun session holds 3 operative states (HP, RAM, deck, Firmware, Daemons), a shared Cycles pool and a step counter. This is the largest item, a rework of `netrun_session`. **Fallback:** one operative walking the three lanes in sequence, which loses the spine.
2. **NEW: Lane graph generator.** Three parallel lane routes of 9 steps with two-slot detours, the `perm` draw and stored Hack rotations. It reuses the seeded `map_graph` generator with a lane parameter and draws from the checkpointed `map` stream.
3. **NEW: Step clock and STALL tokens.** Pure run-state data: step number, per-lane position, tokens.
4. **NEW: mirror_fight** (3.3). **Fallback:** authored elites.
5. **Relay resolution.** It reads fight tallies and writes node-keyed overrides through N16. This is an extension of N16, not a separate system.
6. **NEW: Hack puzzle node.** A small page reusing the wheel kit (like N17's event wheel), with a stored rotation.
7. **Showdown parked passives.** Data rows per class (`parked_support`) on existing triggers. No new rule.

**Data-only parts:** node tables, lane layout, REBEL_CELL enemy data, reward rows, shop stock, event text, static relay fallback.

**Build order:**
1. Foundation (N1-N4, N19) and the REBEL_CELL enemy pass.
2. N16 (with the node key) and N18.
3. The lane generator and step clock on a **single-operative stub** (one lane active, two scripted), to prove the data.
4. The multi-operative session, then the relay and the counter (authored-elite fallback first, mirror_fight after).
5. The Hack node, the kill-switch step and the parked passives.
6. N5 and the boss, then the art hookup.

## 9. Art hooks

Per frame the game passes this state, and the art only visualizes it.

| State | Used by |
|---|---|
| `seq` (0-3, int plus a 0-1 blend) | The window sequence. Steps 1-3 → 0; steps 4-5 → 1; steps 6-8 → 1→2 blended by step; step 9 before the throw → 2; a successful throw → 3; a failed strike → 1. |
| `pulse` (0-1) | The LINE blocks. A short pulse on each relay write, and a full pulse on the throw. |
| `lane_pos[3]` | The three operative tokens (pink BREAKER, cyan GHOST, green RIGGER) and their rooms. |
| `lane_nodes[3][step]` | Slot assignment: node id, type, slot class (ROOF, STREET, TUNNEL, HUT, BACKROOM, DEEP), span (1 or 2), and state (UNREAD frosted, current, cleared). |
| `countered_lane[step]` | The red outline on the countered lane's fight nodes, one step ahead (all steps if Intel is held), and the sign cone's lean. |
| `sign_target` | The MAINFRAME sign sits on the DISPATCH lot at all times. |
| `step`, `stall_tokens` | The step dial and held tokens. |
| `relay_chips[3]` | The chip on a lane's next fight nodes, with a type icon, and an arrow on the lane gap per write. |
| `switch_state[3]`, `shaft_open` | UNTHROWN or THROWN, and the open flag. |
| `parked[3]` | Which operative enters, and the parked tokens. |
| `dark_lane[3]` | A lane's lights go out when its operative dies. |
| `camera_beat` | DECISION, OVERVIEW or REVEAL, and the east slide per step. |

**Occlusion rule** (camera rig, not game state): the game passes the active-room front points and the visible route nodes. The art computes the flatten and ghost states.

**Per-Exploit visual:** one boolean each for `intel`, `breach` and `virus`. Intel shows the full counter schedule, Breach opens the side doors on the step 8 rooms, and Virus adds a faint static on the sign.

## 10. Open questions

Q: **Crew size.** The run needs three living operatives, but the campaign starts with 2 rookies. Is the HQ netrun gated on three, or does a smaller crew run fewer lanes (a 2-lane fist, a shorter run, with the relay ring shrinking to a pair)?

Q: **Relay readability.** Is a next-step chip enough to read result-driven modifiers, or should the relay be the static authored fallback to keep the board fully predictable?

Q: **Run length.** Is about 60 minutes (+45 min on the campaign budget) acceptable for the HQ run, or should it be cut to 7 steps with the showdown carrying the weight?

Q: **Counter on non-fight nodes.** Should a countered lane's Rest or shop also be affected, or does letting the player dodge the counter with a non-fight pick make the counter too easy to avoid?

Q: **Showdown loss.** After a failed showdown the whole run is lost and the entering operative dies. Is that acceptable, or should the strike re-arm with the lanes kept cleared so a retry needs only the boss fight?
