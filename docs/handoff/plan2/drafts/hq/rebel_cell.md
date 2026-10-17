<!-- draft via Message Batches API, claude-sonnet-5-5, batch msgbatch_01HADBSF5pLwaHAq7nbABzZa, custom_id hq__rebel_cell; status ok; tokens in 10499 cache-write 0 cache-read 32007 out 10516; cost $0.066. A DESIGN DRAFT for the designer's review: nothing here is built. -->

# REBEL_CELL: HQ netrun draft

Working names: the final run is "the Undercroft run", the boss is "DISPATCH core" (the Sync Strike pass, referenced by working name only), and the three lanes are Roofs, Alley and Tunnel.

## 1. Concept & the named mechanic

**What the art shows.** There is no tower. The district is an ordinary Tokyo-alley block grid, cut along one street line into a side-view section with three stacked lanes: roofs (L), the alley at street level (C), and the service tunnel under the street (R). A sunken service street, THE UNDERCROFT, lies below the tunnel. The window sequence `SEQ` (0 before, 1 blackout, 2 spreading, 3 full red) tints the fist drawn in windows. `PULSE` makes the fist's line blocks glow. The MAINFRAME red sign stands at the target and marks DISPATCH.

**As a game mechanic.** This is the only HQ netrun where **you run three operatives at once, one per lane, on one shared clock**. Every other HQ is one operative climbing one route.
- The run is a **district of three parallel lane-routes** that advance in lockstep. One step = every lane moves one layer.
- Each lane ends at a **kill switch**. All three must be thrown on the same step.
- The fist on the map is the run's progress meter. It starts hidden and ends full red, and it is driven by `SEQ` computed from the strike state, not from time.

**Why it can't be mistaken for another HQ.**
- Solace is one climb (UP / ACROSS) and Halcyon is one climb under an eye.
- Orbital is a countdown, with doors opening and shutting.
- Meridian is a moving shuttle between wall and train.
- Only the Undercroft run has three simultaneous routes and a synchronisation goal. It also asks you to commit your whole stationed crew and consume three operatives' HP.
- The final fight is not a long boss climb. It is a convergence: two operatives park as support and one enters DISPATCH core.

**Ruling basis.** G12 and D10 say every HQ run is unique and may exceed 7 layers. Sync Strike is the "design pass pending" item. This draft proposes one coherent answer to its open questions (turn order, HP, deaths, support, decks) so the designer can accept, change or reject it. Proposals are marked **(Sync Strike)**.

## 2. Structure

### 2.1 Layer count and shape

- **9 steps** (the HQ run may exceed 7), in three acts:
  - **Steps 1-3, INFILTRATE.** Each lane has 3 nodes. Fights are standard-strength. No coupling yet.
  - **Steps 4-6, BLACKOUT.** Each lane has 3 nodes. Lanes begin to interfere with each other (section 3.2). The fist goes dark and the red starts spreading (`SEQ` 1 then 2).
  - **Steps 7-8, CONVERGE.** The lane's two last rooms. Elite-class content, plus the kill-switch room at step 8.
  - **Step 9, SWITCH and SHOWDOWN.** All three operatives stand at their switches. A synchronised throw opens the shaft. One operative enters the boss fight.
- The player-facing graph has **3 lanes × 8 route layers + the switch layer + the boss**. That is 27 nodes plus the boss, on a graph where each lane keeps ordinary branching (2-3 options per layer).

### 2.2 Per-lane layer map

Each lane's own graph is a mini-route. Per layer, a lane offers **2 nodes (3 on steps 2, 5 and 7)**, one of which may be a detour (section 2.3).

```
STEP   L ROOFS (BREAKER)   C ALLEY (GHOST)     R TUNNEL (RIGGER)      coupling
 1     F  F                F  F                F  F                   none
 2     F  E  Cache         F  E  Cache         F  E  Cache            none
 3     F  Rest             F  Rest             F  Rest                none (INFILTRATE ends)
 4     F  Ev               F  Ev               F  Ev                  BLACKOUT: SEQ 1
 5     F  Shop  Hack       F  Shop  Hack       F  Shop  Hack          Relay (3.2)
 6     E  Rest             E  Rest             E  Rest                SEQ 2
 7     E  Ev  Detour       E  Ev  Detour       E  Ev  Detour          Counter (3.3)
 8     SW-prep (elite)     SW-prep (elite)     SW-prep (elite)        SEQ 3 trending
 9     [KILL SWITCH]       [KILL SWITCH]       [KILL SWITCH]  ->  SHAFT -> DISPATCH core
```

Legend: F = Router fight, E = elite, Ev = event, Hack = puzzle (section 4), Detour = a branch to the lane below or above (2.3), SW-prep = the room before the switch.

### 2.3 Cross-lane edges (the three-lane stack)

- Within a lane the graph is a normal branching route: edges go from a node to 1-2 nodes in the next layer.
- **Detours:** at steps 2, 5 and 7, one node in each lane is a **detour node**. It sits in a deeper or higher space (Roofs: raised roof huts; Tunnel: the Undercroft below; Alley has none because the alley already is the middle).
- A detour costs **+1 step**: the lane stays on its layer for one extra turn of the shared clock. The other two lanes keep advancing, so the operative **falls out of step** unless the others are also delayed or the player uses the stall (3.1).
- Why a detour is worth it: it holds a rare node (an elite with a guaranteed Daemon, or a Cache with a Firmware) that the main row doesn't.

### 2.4 Mapping onto the landmark slots

The art rule (8.4, C15) says topology comes from the game graph, assigned to slots in layer order and then node order, and the landmark generates slots on demand.
- **Slot classes:** ROOF room (on a lot roof), STREET room (the lot's ground floor), TUNNEL room (below the street), DEEP room (the Undercroft pit, for Tunnel detours), HUT room (a raised roof detour), SWITCH (a fixed column), SHAFT (fixed, joins the three levels).
- **Assignment:** lane L takes ROOF slots in layer order, then node order; lane C takes STREET slots; lane R takes TUNNEL slots. Detour nodes take HUT (L) or DEEP (R) slots.
- **Link geometry:** same-level steps are horizontal edges along the street line. A detour is a falling (R) or rising (L) step. The shaft is vertical.
- **Slot generation on demand:** the section picks a street line of the grid, a run of lots along it that fits the graph (at least 9 lot positions per lane for 9 steps, or fewer with wider lots), and a target lot (DISPATCH, under the MAINFRAME sign). The art's note says any district can host the lanes. If the lane has more layers than lots, the camera slides east along the street each step (art DECISION beat), and the extra layers wrap onto additional lots.
- **The countered room** (a preset id in the art) becomes game state: a single room chosen by the seed (3.3).

## 3. Unique mechanics

### 3.1 The shared clock and STALL (the Sync Strike spine)

- **Rule:** All three lanes share one step counter. Each step, **each operative resolves one node** in its own lane, in lane order L, C, R (fixed; no RNG). A lane cannot get ahead: if its operative finishes its node early, it waits at the room until the step ends. A lane that is delayed (a detour, a fight that takes extra turns, or a COUNTER stall, see 3.3) holds the whole step: **the step does not close until all three lanes are done**.
  - So a "step" is not real time. It is the fixed set of three nodes taken together.
- **STALL:** a lane can hold at a room by choice. Spending a STALL token keeps that operative in place for one step while the others move. Tokens come from rest nodes and cache rewards (max 2 held).
  - Why: it lets you fix a lane that is ahead or has a detour, so the three arrive in the same step.
- **Sync dial (what the player sees):** each lane shows its step number. When all three match at step 9, the switches can be thrown. If any lane is at 8 and another at 9, the dial shows "OUT OF STEP" and the lone-throw rule applies (3.4).
- **Per-layer trigger:** the sync check happens at the end of every step. At step 9 it decides the strike.
- **Counter:** STALL tokens, the detour choice, and fight outcomes. A faster lane can take a Rest node for a free hold.
- **Determinism:** no RNG. Lane order is fixed; the only variability is which nodes the player picks. Combat uses the existing netrun combat RNG streams, as in a normal run.
- **Turn order (answers art Q1):** all three choose at once at each step (one step = three moves), then resolve in lane order. Only one fight is on screen at a time. The UI queues the three lane nodes: the player sees all three choices, confirms, then fights them in L, C, R order. A skipped node (an event, a shop) resolves instantly.

### 3.2 The relay: lane interference (BLACKOUT act)

- **Rule:** from step 4, the Roofs, Alley and Tunnel are electrically linked. Each lane's **elite/fight results export a relay effect** onto the next lane in the order L → C → R → L:
  - Win a fight **without the NULL slice resolving** (Cold Exit style): the next lane gets a **free nudge** (+1 per fight) in its next fight.
  - Win a fight **with a Perfect-heavy landing** (at least 2 Perfects): the next lane's enemy gets **−10 % HP** in its next fight.
  - Take damage over 15 in a fight: the next lane's enemy gets **+1 weight** (resistance 1) in its next fight.
- **Why:** it makes the three lanes feel like one system. A strong lane helps a weak one, and a bad fight hurts the neighbour.
- **What the player sees:** relay arrows on the lane gaps at steps 4-8. The art draws these as the red lines of the fist: the "LINE" blocks pulse (`PULSE`) when a relay fires. The three-lane fist has its fingers as the relay links.
- **Counter:** play the fight cleanly, or STALL to let the next lane's operative recover.
- **Determinism:** the relay trigger reads the finished fight's tallies (a deterministic result). It writes a modifier into a run-level `next_combat_overrides`; this is N16. No RNG.

### 3.3 The Counter: DISPATCH counters one lane

- **Rule:** from step 4 on, DISPATCH picks **one lane per step** to counter. The counter is chosen deterministically: **the lane whose operative's most-used Firmware is highest in play count** (art Q7, GDD 8.5 "built from your profile"). A tie goes to the lane order L, C, R. The countered lane's next node gets **STALL +1** (the lane loses a step) and its fight gets the **Mirror modifier**: the enemy uses the operative's own wheel at ×1.5 with one pointer (M11).
- **The countered room** is visible one step ahead: the room is marked on the map ("COUNTERED" on the next layer) so the player can plan a STALL or a detour. **It is previewed, not hidden.** This preserves preview = result.
- **What the player sees:** the countered room glows with a faint red outline; the MAINFRAME sign's light angles toward it (the sign "moves to the target" in the art's rule: it moves to the active DISPATCH target, the final lot at step 9, and at each step it leans toward the countered lane). In the art this is a moving red light cone from the sign.
- **Counter:** STALL, a detour, or a Firmware swap at a Shop (changes the profile in the most-used count) before the counter is read. Swapping a Firmware late is a legitimate counter.
- **Determinism:** a pure function of the loadout and step number. No RNG.

### 3.4 The kill-switch throw (lone-throw rule)

- **Rule:** at step 9, each operative in its lane stands at a switch. The player presses **THROW** on each. All three must be thrown on the same step. If only one or two are thrown, the lone throw **re-arms** after the step, and the unthrown operatives take **a DISPATCH counter-attack** in the shared fight ("backlash": 8 flat damage each, tier-scaled).
- **A lane dead before step 9 (Sync Strike Q3):** the strike does not fail automatically. A dead operative's lane is **dark**: its switch is unreachable. The other two may throw as a **lone pair** at a penalty: the shaft opens, but DISPATCH core starts at **+1 phase advanced** (it skips phase 1, per the boss draft's phase list) and gets **+25 % damage for the whole fight**. If two operatives die, the strike fails and the run ends in retreat (section 7).
- **SEQ sets visuals:** the sequence advances as the throw progresses: before the first throw `SEQ` is 2; a successful triple-throw goes to 3 (full red) and `PULSE` fires on all line blocks at once; a failed one drops back to 1 (blackout) for a step.
- **Determinism:** pure state, no RNG.

### 3.5 The showdown (who enters DISPATCH core)

- After a successful synchronised throw, the shaft opens. **The player chooses one operative to enter; the other two park** as support and stay at their switches.
- **Parked support (art Q4):** each parked operative contributes a **passive tied to its class** that applies for the whole boss fight (values placeholder):
  - Breaker: +10 % damage on the entering operative's OVERFLOW.
  - Ghost: the first nudge each turn is free and ignores resistance.
  - Rigger: +2 RAM per turn.
  - Botnet: +1 drone cap.
  - A parked operative also **absorbs one DISPATCH counter-attack** per phase: the first enemy hit that would reach the player each phase is redirected and costs the parked operative's HP instead (shown as the parked token taking the hit).
- Why this and not a card: passives are data-only and previewable. Absorbing one hit per phase keeps the parked pair relevant without a second wheel on screen.

## 4. Node kit

HP and RAM answer (art Q2): **each operative has its own HP and RAM** (the stationed crew), carried across steps as in a normal run. Cycles and Schematics are shared (one pool). **Decks (art Q6):** one deck per operative, because each is a distinct class and their wheels differ.

| Node | Standard behaviour | Undercroft twist |
|---|---|---|
| Fight (Router) | 1 phase, 3-4 turns | Enemies are the corporation's mirror units (every elite wears MIRROR per the art). Normal Routers use REBEL_CELL normals (cell informant, dead drop, echo process, handler proxy, loyalty test, mirror script) at T4 scaling. |
| Elite | 2 phases, 6-8 turns | REBEL_CELL elites. From step 6, one elite per lane per act. Elites drop a Daemon only on the detour variant. |
| Event | Choice node | Events carry a lane tag: "Roofs", "Alley", "Tunnel". An event may affect another lane (a relay-style effect) or grant a STALL token. Impromptu events spawn a fight (N16). |
| Shop | Cycles | One shop per lane at step 5, selling **Firmware and a "profile scrub"**: a service that resets the countable use of one Firmware (3.3 counter). Price placeholder 60 Cycles. |
| Rest | Heal | Heals that operative 30 % max HP **or** grants a STALL token. Not both. |
| Cache | Reward node | A guaranteed Firmware or Daemon. Only in the detour-eligible lanes at step 2. |
| Hack (puzzle) | New node type | A no-combat puzzle: the lane's wheel is shown with the relay lines. See below. |
| Kill switch | The step 9 node | Not a fight. See 3.4. |

**Hack puzzle (the one puzzle node, at step 5).** The player gets a mini-wheel with 6 slices and a target landing (a specific slice at Good or better) and must hit it using nudges only, with a 2-nudge budget and no cards. Success grants a **relay boost** (the next lane's first fight starts with the enemy at −15 % HP) and reveals the next step's countered room two steps ahead instead of one. It is deterministic: the start rotation is seeded from the netrun seed, then fixed. Failure costs nothing but forfeits the boost. It's a puzzle, not a mini-fight.

**Mini-fights vs puzzles.** Fights: Router, elite, SW-prep. Puzzle: Hack. Events are narrative choices. The switch is a coordination step.

### 4.1 Exploits as keys (D5)

D5 says each access key equals an Exploit, and each Exploit gets its own building. In this HQ the three Exploit types (Intel, Breach, Virus) each pay off in one lane's structure. Each is held by the player from the campaign:

- **Intel (pricing memos / schematics of the district):**
  - Reveals the **whole counter schedule** (all countered rooms across all steps) at run start instead of one step ahead.
  - The Hack puzzle is skipped as a free success.
- **Breach (override keys):**
  - Opens a **shortcut**: one detour per lane becomes free (no +1 step cost).
  - The Tunnel can reach the shaft directly, skipping the SW-prep room for one lane.
- **Virus (a payload that corrupts DISPATCH):**
  - At the showdown, the boss starts with its first phase's heal and shield disabled.
  - Also flags **one lane's enemies as CORRUPTED** at the start of each fight (their wheel slices pay RAM ×2 to act... they use the R9 rule on enemy wheels; see Q1 in section 10).
- **Exploit count scaling:** the standard `min_exploits_for_breach = 3` gates entry. Owning all three Exploits is the full strike; the HQ run is allowed with the required minimum but each missing key removes its benefit above. So the three-Exploit run is easiest, which is the campaign's reward for finishing the Grid.
- **Boss buffs:** the boss draft's buffs are countered by Exploits drawn for the Grid (R7). The HQ run does not re-roll them. It passes them in as run state.

## 5. Pacing & difficulty curve

**Assumptions:** T4 fights, the R2 reference player (about 18 damage per turn) with each operative on its own HP.

- **Fights per lane:** about 5 combats (3 routers, 2 elites) over the 8 route steps (events, a shop, rests and the Hack take the rest). So about **15 combats across the three lanes**, plus the boss.
- **Duration:** a Router is 3-4 turns (about 1.5-2 min), an elite 6-8 turns (about 3-4 min). Per lane, that is 3 × 1.75 + 2 × 3.5 ≈ 12 min; three lanes ≈ 36 min of fighting, plus events, shops and the Hack ≈ 9 min. The boss is 12-20 turns (about 6-10 min). Target total: **~50-55 minutes**. This is deliberately longer than a normal 15-minute run, per D10, and is the finale.
- **Save and quit:** the existing mid-run save works. A step boundary is a safe save point (the three-lane choice screen).
- **HP pressure:**
  - Each operative has its own HP (45-60 at base) and no free refill. Rest nodes heal 30 %. Each lane has 2 rests (steps 3 and 6), about +60 % of max HP total.
  - Expected damage per lane: Routers 8-12 each, elites 15-25 each at T4, about 70-90 per lane, against 50 HP plus 60 % healing. This is tight by design; the relay and STALL mechanics soften it.
- **Heat:** the HQ run uses the standard per-node Heat table, but **elites inside the HQ do not add Heat** (the corporation is already alerted). Total Heat gain is capped at +10 for the run. It does not trigger new raids unless Heat crosses 100 (Purge). **Raids do not interrupt the HQ run** (see section 7).
- **Difficulty curve:** INFILTRATE is easy (a warm-up where lanes don't interact), BLACKOUT is the teaching of relay, then CONVERGE tightens with the counter and elites. The curve peaks at step 8, then the boss.

## 6. Rewards

Beyond the boss's own drop:
- **Campaign win:** per GDD 1.3, breaching the final server with enough Exploits wins the campaign. This is the entry point to the finale, so winning ends the campaign.
- **Profile unlocks:** completing the Undercroft run unlocks:
  - the REBEL_CELL ICE ladder tier ("final final" progress);
  - a profile-level cosmetic: the **red-fist skin** on the home server;
  - **a lane trophy:** one extra class alternative per operative who finished a switch **alive** (a data row, UnlockKind CLASS_ALTERNATIVE).
- **Run rewards:** unspent Cycles convert to Schematics at 10:1. Each switch thrown alive banks **+10 Schematics** (placeholder).
- **Story:** the DISPATCH finale (fully voiced); one bonus beat for each of the three operative classes that took part (art "Ghost Patient" foreshadows).
- **Clean strike bonus:** finishing with no STALL token spent and no lone throw gives a one-time **Daemon from the REBEL_CELL pool** (placeholder).

## 7. Failure & retry

- **Operative death in the run:** per GDD 4.2, death is permanent for that operative, and the campaign gains 10 + tier Heat per death. Inside the HQ run:
  - One death: the lane goes dark and the run continues as a lone pair (3.4). The Heat penalty applies.
  - Two deaths: the strike fails. The surviving operative **retreats** (returns to HQ at its current HP, keeping its deck). The campaign gains 10 + tier Heat for each death. The run is **not** consumed: the HQ netrun stays open, and the player may launch it again with a fresh crew.
  - Three deaths: same as two, and no survivors.
- **Retry:** each attempt is a new seeded graph (the route differs every game, per Designer Q2), but the **boss's phase layout and the Exploit subset are fixed for the campaign**, so learning carries over.
- **Mid-run raid:** HQ runs are not interrupted by raids. If a raid threshold is crossed during the run, the raid is queued and resolves **when the run ends**, either way.
- **Boss defeat after a successful strike:** the entering operative dies (permanently, per the rule), the two parked ones survive. The HQ netrun remains open; a retry needs a new entering operative and a re-throw of the switches (the strike re-arms; the district goes back to `SEQ` 1).
- **Abandon:** per GDD 4.5, abandoning kills all operatives currently on the run (three deaths here).
- **Heat effects:** no special Heat on failure beyond the standard death Heat.

## 8. Systems needed

| # | Use here | Fallback without it |
|---|---|---|
| N2 | Tier-band HP for REBEL_CELL normals/elites at T4 | Use current `hp_by_tier`-less values |
| N3 | Phases and parking for elites and the boss | Required for the boss; none for Routers |
| N4 | Enrage inside HQ elites | Skip |
| N5 | Boss buffs and Exploits (boss draft, run state passed in) | Boss runs unbuffed |
| N6 | Listeners for the mirror enemies' Echo | Data-only mirror elites without Echo |
| N7 | Lock effects in some elites | Skip |
| N11 | Uneven needles on elites | Even needles |
| N13 | Fixed satellites in some elites | Skip |
| N16 | `next_combat_overrides` carries the relay and Counter modifiers; events that start fights | **Required; no data-only fallback** for the relay. A weaker fallback: apply the modifier through a per-node `combat_overrides` field authored at graph build time |
| N18 | Reward rows for the clean strike Daemon and the switch bonus | Hard-coded rewards |
| N19 | Sim metrics (turns per step) | Skip |

**NEW systems:**
1. **NEW: Multi-operative run (the Triple Run).** The netrun session holds 3 operative states (HP, RAM, deck, Firmware, Daemons), a shared Cycles pool, and a step counter. **Largest item; this is a reworking of `netrun_session`.** No data-only fallback. A reduced fallback is one operative walking all three lanes in sequence (no simultaneity), which loses the spine.
2. **NEW: Lane graph generator.** A generator for 3 parallel lane-routes (9 steps, 2-3 nodes per layer, detour edges). Reuses the existing seeded `map_graph` generator with a lane parameter. Stream: the existing `map` RNG stream, checkpointed.
3. **NEW: Step clock and STALL tokens.** Run state: the step number, per-lane position, tokens. Pure data.
4. **NEW: Counter selector.** A pure function of loadout use counts and the step. Needs a per-Firmware use-count in the profile or run stats (`most-used firmware`).
5. **NEW: Relay and sync resolution.** Reads fight tallies, writes N16 overrides.
6. **NEW: Hack puzzle node.** A small page reusing the wheel kit (like N17's event wheel); seeded rotation.
7. **NEW: Showdown support passives.** Data rows per class (`parked_support`), plus the damage-redirect rule for one hit per phase. Needs the preview to show the redirect.

**Data-only parts:** node tables, the lane layout, the Mirror elite data (existing M11), rewards rows, shop stock, event text.

**Build order:**
1. Foundation (N1-N4, N19) and the REBEL_CELL enemy pass.
2. N16 and N18.
3. The lane graph generator and step clock on a **single-operative stub** (one lane active, the other two scripted), to prove the data.
4. The multi-operative session, then relay and Counter.
5. The Hack node, the kill-switch step and the showdown support passives.
6. N5 and the boss. Last, the art hookup (section 9).

## 9. Art hooks

Per frame the game passes the following state; the art only visualises it.

| State | Used by |
|---|---|
| `seq` (0-3 float, or int plus a 0-1 blend) | The window sequence: before (0), blackout (1), spreading (2), full (3). Mapping: steps 1-3 → 0; step 4 → 1; steps 5-8 → 1 to 2 interpolated by the lane's progress; step 9 → 2; a successful triple throw → 3; a failed throw → back to 1 for one step. |
| `pulse` (0-1) | The LINE blocks. Fires on a relay trigger (a short pulse), and fully on the triple throw. |
| `lane_pos[3]` | The three operative tokens (pink BREAKER, cyan GHOST, green RIGGER) and their rooms. |
| `lane_nodes[3][layer]` | Slot assignment: node id, type, class (ROOF / STREET / TUNNEL / HUT / DEEP) and state (UNREAD frosted, current, cleared). |
| `countered_room` | The red outline on the next countered room, and the MAINFRAME sign's light cone leaning to it. |
| `sign_target` | Where the MAINFRAME sign sits: the DISPATCH lot at all times (target); the leaning is cosmetic. |
| `step`, `stall_tokens`, `sync_state` (IN_STEP / OUT_OF_STEP) | The SYNC dial. |
| `relay_events[]` | An arrow on the lane gap per fired relay, with a type icon. |
| `switch_state[3]` | UNTHROWN / THROWN / RE-ARMED; the shaft open flag. |
| `parked[3]` | Which operative enters; the parked tokens and the hit-absorb flash. |
| `dark_lane[3]` | A lane's lights go out when its operative dies. |
| `camera_beat` | DECISION, OVERVIEW or REVEAL; the camera slide east each step. |

**Occlusion rule** (camera rig, not game state): the game passes the active-room front points and the visible route nodes. The art computes the flatten and ghost states.

**Per-Exploit visual:** one boolean per Exploit (`intel`, `breach`, `virus`). Intel shows all countered rooms on the map from the start, Breach opens the shortcut doors, Virus adds a faint static on the sign.

## 10. Open questions

Q: **Operative count.** The draft needs three stationed operatives. If the campaign has fewer (the start is 2 rookies), is the HQ run gated on three alive operatives, or does a smaller crew run fewer lanes (2 lanes, a shorter fist)?

Q: **Counter source.** Is "the operative's most-used Firmware" the right basis for the countered room, or should the counter always be a lane chosen by seed so the player cannot game it with a shop swap?

Q: **Virus on enemy wheels.** Under R9, what does CORRUPTED do on an enemy wheel (this draft assumes the enemy pays double RAM-equivalent, i.e. its nudges and listener actions are disabled one turn in two)? This needs the Q3 ruling of CONTENT_DESIGN_V2.

Q: **Run length.** Is 50-55 minutes acceptable for the HQ run, or should it be cut to about 7 steps (one lane has 2 fewer nodes) to keep it near a long normal run, with the showdown carrying the weight?

Q: **Boss retry state.** After a failed showdown, should the strike re-arm with the lanes cleared (this draft) or force the lanes to be replayed, which makes failure very costly?

Q: **Shared or separate decks.** One deck per operative is proposed. If the designer prefers a single deck, the relay and parked-support rules need rebalancing, since the parked pair would then contribute no cards at all.
