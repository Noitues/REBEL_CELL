<!-- draft via Message Batches API, claude-sonnet-5-5, batch msgbatch_01TQsqGnerTdLwJEata9mp6i, custom_id v2__hq__aurelian; status ok; tokens in 11618 cache-write 0 cache-read 32585 out 26971; cost $0.150. A DESIGN DRAFT for the designer's review: nothing here is built. -->

## Changes vs v1

- **1 (BLOCKER, ring 4 mapping and 18+Rostrum).** Fixed. Ring 4 is L7 (2 rooms) plus L8, and the Grand Stand takes the third ring-4 slot. The art's 18 rooms include the Grand Stand, and the Rostrum is the 19th slot on the arena floor. I re-added the layers: 3+3+2+3+2+2+2+1 = 18, plus L9 = 19.
- **2 (BLOCKER, descent timing and the "one-way hop" contradiction).** Rewritten in §2 and §3.1.
  - Descent happens only from a ring's last layer.
  - Every move is a node completion and costs one step.
  - The only same-layer move is a **sideways edge between adjacent last-layer rooms**. It is a real node, a normal fight or event, and it costs a step.
  - The gate test happens at departure, using `step_count` after the current node resolves. This is the same function the HUD prints.
  - The clock is now discrete: one slot per step, so v1's 24°–31° angles are replaced. This is a consequence of the fix, because arbitrary angles cannot guarantee every room opens.
  - Layer sizes changed so the guarantee holds by construction (ring 2 is now L3 2 rooms, L4 3 rooms). The critic's "every room opens at least once in any 3 consecutive steps" cannot hold with 2 gates and 2 rooms. I replaced it with a stronger rule: at least one last-layer room is open at every step, checked by a lint test (the critic asked for lint, not the generator). A softlock is impossible and the player only ever loses time.
  - "Wait" (Q1) is answered: there is no waiting. The only way to shift the clock is a sideways node.
- **3 (MAJOR, VERDICT undefined, no tag).** Defined in §3.2. Tagged NEW: VERDICT status, with a data-only fallback. The R9 double-RAM effect of CORRUPTED is stated. It is no longer tied to N6.
- **4 (MAJOR, Favor).**
  - Favor now depends on the number of CORRUPTED slices at the winning blow: +1 for 0, 0 for 1, −1 for 2 or more.
  - The ≤1 / 0 / 2–3 tiers are stated.
  - "Breach adds +1 Favor" is removed. The critic called it invented, and Breach now has one job.
  - The elite-win "+1 regardless" is removed.
  - The conflict with the Rostrum VERDICT stays as Q2.
- **5 (MAJOR, HP budget).** Re-derived in §5 with a reference route of 9 content nodes: intake 70 against 45 healing, so the operative arrives at 35/60 HP (about 58%). Route length is now tied to layers plus detours, not 10–12 free nodes.
- **6 (MAJOR, invented enemies, N16 fallback).** Named enemies are replaced by "Aurelian pool (enemy drafts)". Jeered and the Grand Stand effects need N16, and I state the fallback explicitly (§8).
- **7 (NIT).** `telegraph_depth` and Intel are made consistent (default 1, Intel 4). Cache is renamed **Ring Vault**, a Server Rack reuse, so it does not collide with the D4 Cache event puzzle.
- **Triage BLOCKER 1 (phase-budget-arithmetic).** Covered by issue 1 above.
- **Triage BLOCKER 2 (rule-violation-R1-R13).** Covered by issue 2 above. R1 is respected: fights are not tolled and sideways nodes are normal nodes that cost pacing. The ruling "HQ may run longer than 7 layers" (D10) is kept.
- **Kept, because the critic marked them strong:** the deterministic gate clock as the spine, the data-only `open_on_steps` fallback, and the per-frame art hook list.

---

# Aurelian Concord: HQ netrun draft

Working names: the HQ is THE CIRCUS AURELIUS ("Circus"). The boss is the ROSTRUM FIGHT (designed in the corp draft). All numbers are placeholders pending the balance sim.

## 1. Concept & the named mechanic

**What the art shows.** The HQ is a colosseum with four concentric seating terraces. Each terrace has a bronze barrier with 2 gates, and the barriers turn each step in alternating directions. The Rostrum sits on the arena floor. Rooms are cutaway boxes on the terraces, 6 / 5 / 4 / 3 per ring (18 rooms; the Rostrum is the 19th slot). Links along a ring are always open. Links down a ring exist only where a gate stands. The next step's gate positions are shown as a yellow pencil telegraph.

**As a game mechanic.** The player descends from the outer ring (the cheap seats) to the arena. Each time the player completes a node, the Circus takes one STEP and each barrier turns by one slot. You descend only from the last layer of a ring, and only through a gate that stands over your room when you leave. A sideways move to a neighboring room on that layer is always possible. It is a real node, so it costs a step, and it is the only way to change which gate you face. The route is a timing puzzle on top of the fight graph. Fights are not tolled by position, but position is tolled by time.

**Why it cannot be mistaken for another HQ.**
- Halcyon is a fixed ladder watched by an eye.
- Solace is an UP / ACROSS ladder.
- Orbital is doors and a rocket.
- Meridian is a shuttling freight line.
- REBEL_CELL is an alley with a window sequence.
- Aurelian is the only HQ whose connectivity is a pure function of a clock. It is a rotating plan you can solve on paper from the telegraph.

**Spine.** The TURNING GATES (§3.1). VERDICT (§3.2) is the boss's house rule scaled to the run. FAVOR (§3.3) is the crowd's meter. §3.4 is the Grand Stand finale readout.

## 2. Structure

**Size.** 9 layers (L1–L9), 19 nodes. Four rings need real descent room, which is why this HQ runs longer than 7 layers (D10).

| Ring (slots) | Layers | Rooms per layer | Rooms |
|---|---|---|---|
| Ring 1 outer (6 slots) | L1, L2 | 3, 3 | 6 |
| Ring 2 (5 slots) | L3, L4 | 2, 3 | 5 |
| Ring 3 (4 slots) | L5, L6 | 2, 2 | 4 |
| Ring 4 inner (3 slots) | L7, L8 | 2, 1 (L8 is the Grand Stand) | 3 |
| Arena | L9 | the Rostrum fight | 1 |

18 terrace rooms (including the Grand Stand) plus the Rostrum gives 19 nodes. The ring sizes match the art's 6 / 5 / 4 / 3 exactly, so each ring is fully used. Slots are numbered clockwise per ring starting at 0. Rooms are placed by the landmark's on-demand slot generator.

**Edges.**
- **Forward edge:** each room links to its 1–2 nearest-azimuth rooms in the next layer of the same ring. It is always open and costs a step like every node.
- **Sideways edge (last layer of rings 1–3 only):** it links adjacent rooms of the ring's last layer and is always open. The target room is a normal node, so moving sideways costs a step. Each room can be cleared once, which bounds detours to (rooms − 1) per ring.
- **Descent edge:** it links a last-layer room to the nearest-azimuth rooms of the next ring's first layer. It is powered only if a gate stands on that room's slot at departure (the rule is in §3.1).
- **Grand Stand to Rostrum (L8 to L9):** always powered. Barrier 4 is the finale's door and swings aligned over the Grand Stand slot as you enter L8. This is animation only and carries no puzzle.

**Layer map** (`~` sideways, `v` gated descent, slot numbers in brackets):

```
RING 1 (6 slots)  L1: [0] [1] [2]            Routers
                       fan  fan  fan         forward edges
                  L2: [3]~[4]~[5]            sideways between neighbors
                       v    v    v           powered per §3.1
RING 2 (5 slots)  L3: [0] [1]
                  L4: [2]~[3]~[4]
                       v    v    v
RING 3 (4 slots)  L5: [0] [1]
                  L6: [2]~[3]
                       v    v
RING 4 (3 slots)  L7: [0] [1]
                  L8: [2]  GRAND STAND
ARENA             L9: ROSTRUM FIGHT
```

**Step count.** `step_count` = nodes completed in this HQ run. A route with no sideways moves departs ring 1 at step 2, ring 2 at step 4 and ring 3 at step 6. Each sideways node adds 1 to every later step.

**Mapping onto landmark slots.** The ring structure is the layer structure, so the visual descent equals the layer descent. Slots are (ring, slot index, floor_z), assigned in layer order and then azimuth order, starting from the half of the bowl facing the camera. Along-ring links run flat on the terrace and descent links pass through the gate anchor. The link type is a hint only and never names the node.

**RNG.** The layout (room slot to node type) uses the `hq` stream seeded at HQ build and checkpointed. Gate schedules use no RNG.

## 3. Unique mechanics

### 3.1 THE TURNING GATES (spine)

- **Rule.** Each barrier has 2 gates, each one slot wide, turning one slot per step in alternating directions. Descent is allowed only from the last layer of a ring, and only if a gate stands on that room's slot at the moment you depart, after the current node has resolved. Here `s` is `step_count`.

| Ring | Slots | Gates at step s | Turn | Last-layer rooms (slots) | Open room at step s |
|---|---|---|---|---|---|
| 1 | 6 | {s, s+3} mod 6 (opposite) | +1 per step | 3, 4, 5 | slot 3 + (s mod 3): exactly one |
| 2 | 5 | {−s, −s+2} mod 5 | −1 per step | 2, 3, 4 | s mod 5 = 0 → 2; 1 → 4; 2 → 3; 3 → 2 and 4; 4 → 3 |
| 3 | 4 | {s, s+2} mod 4 (opposite) | +1 per step | 2, 3 | slot 2 if s is even, slot 3 if odd: exactly one |
| 4 | 3 | scripted: aligned over the Grand Stand | n/a | n/a | always open |

  - **Guarantee.** At every step, at least one last-layer room of rings 1–3 is open. Rings 1 and 3 have exactly one open room because their gates are opposite and the last-layer rooms cover every pair. Ring 2's rooms {2, 3, 4} always intersect a gate pair, because the only pair missing all three would be {0, 1}, and gate pairs are always two slots apart. So no softlock exists, and the cost of a mistake is only time. A lint test enumerates all three rings over s = 0 to 29 and asserts at least one open room.
  - **Riding the gate.** The open room in rings 1 and 2 shifts each step. Moving sideways with the rotation keeps you aligned, and moving against it misaligns you by 2.
- **Trigger.** Every completed node (fight, event, shop, rest, vault, sideways node) is one step. It is not per combat turn. Raid interludes do not advance the clock.
- **What the player sees.**
  - Gate rings turn between steps.
  - The yellow pencil telegraph shows the next step's gate slots.
  - Every descent link is lit (powered) or grey (unpowered).
  - Each last-layer room's tooltip says "GATE OPEN NOW / OPEN IN n STEPS / CLOSED NEXT".
  - By default the HUD prints 1 step of lookahead (the current and next step). Intel extends it to 4.
  - The Codex prints the period of each ring (3, 5, 2), so the puzzle can be solved on paper.
- **Counters.**
  - Spend a Breach hold: it freezes one ring's turn for the next step (the ring's gates stay where they are), once per ring.
  - Spend a Box Office ticket (§4) for the same effect.
  - Take a Thumbs-Up descent at Favor 3 or higher (§3.3).
  - Take a sideways node to shift your own step.
- **Determinism.** No RNG. The state is `step_count`, a per-ring hold counter, and the authored schedule. The telegraph, the powered check and the tooltip use one function, so preview equals result.
- **Fallback.** Data-only: `open_slot_by_step` tables per ring (period 3 / 5 / 2) on the descent edges. No geometry is needed. It costs readability, not rules.

### 3.2 VERDICT of the Circus (the boss's house rule, scaled to the run)

- **Rule.** Every fight node in the Circus opens with one VERDICT mark. It is placed once, at combat start, on the player slice under the pointer after the first start-of-turn respin. Marks are never placed on NULL slices; if the pointer reads NULL, the mark goes to the nearest non-NULL slice clockwise. When the marked slice next resolves:
  - **Perfect:** the mark is cleared and the slice becomes OVERCLOCKED (1.5× its next trigger, then CORRUPTED, per GDD 2.9).
  - **Good:** the mark stays.
  - **WEAK:** the mark is cleared and the slice becomes CORRUPTED (R9: cards and nudges acting where the pointer reads it cost 2× RAM).
- **Trigger.** Once per fight, at start.
- **What the player sees.** A thumb badge on the marked slice, and the preview chip showing the outcome before the player commits the turn.
- **Counter.** Nudge the marked slice to Good (a safe hold), or take the Perfect and accept the OVERCLOCK burn. Cleanse removes the mark, and Encrypt absorbs it.
- **Determinism.** No new RNG. The placement uses the respin that is already a named random event, behind its checkpoint. Tiers follow GDD 2.4.
- **Dependencies.** NEW: VERDICT status (permitted under R8: new status types after the rules were approved).
- **Fallback.** An existing ON_COMBAT_START APPLY_STATUS OVERCLOCKED on the slice under the pointer. This drops the Good and WEAK branches.

### 3.3 THE CROWD'S FAVOR

- **Rule.** A run-wide meter, Favor, 0–5, starting at 2. When a fight is won, count the CORRUPTED slices on your wheel at the winning blow:
  - 0 CORRUPTED: +1.
  - 1 CORRUPTED: no change.
  - 2 or more CORRUPTED: −1.
- **Tiers.** At Favor 3 or higher, your next descent is a **Thumbs Up**: that ring's gates are held for one step (as with a Breach hold), and the meter drops by 1 when used. At Favor 0, the next fight's enemies are **Jeered**: +1 resistance (the existing ENEMY_RESISTANCE rule). Favor 1–2 is neutral.
- **What the player sees.** A laurel / thumb meter in the HUD, and the terraces filling with warm light as Favor rises (dark at 0).
- **Counter.** Cleanse, Encrypt and clean play keep the count low. A cheap Router fight is a recovery option.
- **Determinism.** A pure function of combat state at the winning blow, with no RNG.
- **Dependencies.** The counter and the HUD chip are NEW: Favor meter. Jeered needs N16 (`next_combat_overrides`). Without N16, Jeered is dropped and Favor 0 only removes the Grand Stand bonus.

### 3.4 THE GRAND STAND (L8, ring 4's third slot, a readout node and not a fight)

- **Rule.** The emperor's box reads your Favor and sets the Rostrum's starting state:
  - **Favor 4–5 (OPEN):** the Rostrum starts with the Grand Stand hub already breached for the first 3 turns, regardless of owned Exploits. It also offers the "Imperial Favor" Daemon choice (§6).
  - **Favor 2–3 (NEUTRAL):** no change.
  - **Favor 0–1 (SEALED):** the Grand Stand hub cannot be breached this fight, and the Rostrum starts with one extra VERDICT mark on your wheel.
- **Trigger.** On entering the node. The state is shown on the node before the player commits to the Rostrum. Favor then resets.
- **Counter.** Manage Favor over the preceding layers. Exploits do not change the tier, and Breach is only its usual hub breach in the boss fight.
- **Determinism.** A threshold on a counter.
- **Dependencies.** The starting-state overrides need N16. Without N16, the OPEN reward becomes the Daemon alone, and SEALED does nothing.

## 4. Node kit

| Node | Circus twist | Kind |
|---|---|---|
| Router | Opens with the VERDICT mark (§3.2). Enemies come from the Aurelian pool at T4 (enemy drafts). | Fight |
| Elite Router | An Aurelian elite, 2 phases, with the same VERDICT opening. | Fight |
| Terminal (event) | Circus events. One offers "Bribe the gatekeeper": spend Cycles to hold one ring's gates for one step. | Choice |
| Mainframe (shop) | The Box Office: it sells a heal, Cycles-priced "tickets" (one-use gate holds, max 2 carried), Firmware and Daemons. Max 1 per ring. | Shop |
| Rest (D4) | The Hypocaust: heal 25% max HP, or remove one CORRUPTED slice. The step still passes. Max 1 per ring. | Heal |
| Ring Vault | A Server Rack reuse: elite-strength (2 phases) at ring 2 L4 and ring 3 L6, in one specific last-layer room each. It banks Schematics and offers a rare Daemon. This is not the D4 Cache event puzzle, which is not used here. | Fight |
| Grand Stand | The §3.4 readout. | Readout |
| Rostrum | The ROSTRUM FIGHT, designed in the corp draft. | Boss |

**Layer typing** (guaranteed picks, not a schedule):
- L1–L2: Routers, plus one Terminal at L2.
- L3: Routers and one Mainframe.
- L4: an Elite, the Vault, a Router.
- L5: Rest or Router.
- L6: an Elite, the Vault, a Router.
- L7: Rest or Router.
- L8: the Grand Stand. L9: the Rostrum.

Because the Vault sits in a specific last-layer room, it pulls the player toward a gate decision: a free bank is worth a sideways step.

**Exploit / key buildings (D5).**

| Exploit | What it does inside the Circus |
|---|---|
| INTEL (client rolls) | The gate telegraph shows 4 steps ahead instead of 1, and every node's type is revealed from L1. |
| BREACH (gate codes) | Once per ring, hold that ring's gates for one step (triggered by the player at the room, no node cost). In the boss fight it is the usual Grand Stand hub breach. |
| VIRUS (open dole) | Rest heals 40% instead of 25%, the Ring Vault offers an extra reward choice, and one Box Office item is free per run. |

`min_exploits_for_breach = 3` stays for entering the HQ at all, so a 3-Exploit player has all three effects. Exploits do not change the Circus layout, only how readable and controllable it is.

## 5. Pacing & difficulty curve

**Assumptions.** T4 enemies, 3–4 turns per phase (R1), and the R2 reference player at 18 damage per turn. A normal has 56–70 HP (18 × 3.5 ≈ 63). An elite or Vault has 112–144 HP over 2 phases (about 126). The reference operative has 60 HP.

**Intake per node:**

| Node | Intake |
|---|---|
| Router | 5–8 (call it 6.5) |
| Elite or Vault | 16 (about 8 per phase) |

**Reference route** (the example seed from §3.1, 9 content nodes = 7 layer nodes plus 2 sideways):

| Node | Kind | HP change |
|---|---|---|
| L1 | Router | −6.5 |
| L2 | Router | −6.5 |
| L2′ (sideways) | Router | −6.5 |
| L3 | Mainframe (heal) | +15 |
| L4 | Elite | −16 |
| L4′ (sideways) | Vault | −16 |
| L5 | Rest | +15 |
| L6 | Elite | −16 |
| L7 | Rest | +15 |
| L8 | Grand Stand | 0 |

- **Intake.** 3 Routers 19.5 + 2 Elites 32 + Vault 16 ≈ 68 (I use 70 with rounding).
- **Heal.** 2 Rests (25% × 60 = 15 each) + Mainframe 15 = 45.
- **Net loss.** About 25 HP, so the player arrives at the Rostrum at about 35 / 60 HP (58%). A Virus Rest (24 each) adds about 18 HP.
- **Gate check.** On this route the descent steps are s = 3 (ring 1, slot 3 open), s = 6 (ring 2, slot 4 open) and s = 8 (ring 3, slot 2 open). I checked each against the §3.1 formulas.

**Minutes.** 3 Routers × 2 = 6; 2 Elites × 3 = 6; Vault 3; 2 Rests 1; Mainframe 1.5; Grand Stand 1; Rostrum 6–8. The total is about 25 minutes. The range is 22 minutes (no detours) to about 32 minutes (4 detours). This is longer than a 15-minute Site netrun by design, because it is the campaign's climax (D10). Fights per route: 6 plus the Rostrum.

**Heat.** Each fight node adds the usual Heat (Elite +1), and the HQ run happens at Heat 60–90 in a typical campaign, so ENEMY_RESISTANCE +1 (the 50 threshold) is already on. Every detour node adds its Heat, so catching a gate costs Heat as well as time.

**Difficulty curve.**
- Ring 1: the open room cycles every step (period 3), and the telegraph is forgiving.
- Ring 2: the open room is irregular (period 5) and, at s ≡ 3, two rooms are open.
- Ring 3: a strict even/odd alternation, so a one-step slip costs a full detour.
- Ring 4: scripted, so no puzzle remains, only the Favor outcome.

## 6. Rewards

Beyond the boss (the campaign's win condition, the kill code):
- **Ring Vault banks.** Schematics are banked immediately on capture (GDD 4.2). Ring 2 and ring 3 Vaults also offer one rare Daemon.
- **Imperial Favor.** At the Grand Stand OPEN tier, a one-time VERDICT-themed Daemon choice (for example, "a Good landing on a marked slice clears the mark without a verdict").
- **Completion.** The usual run completion: survivors home at full HP, unspent Cycles convert at 10:1, Rank +1.
- **Story.** The path finale beat plays from the Rostrum win.
- **Returned gate codes.** Each unused Breach hold at the end converts to 2 Schematics.

## 7. Failure & retry

- **Death.** The same as any netrun (GDD 4.2): the operative is permanently lost with everything unbanked, and the campaign gains 10 + tier Heat. Banked Vault Schematics and Daemons are kept.
- **HQ retry.** The Circus resets: `step_count` returns to 0, Favor to 2, and holds are restored. The layout (room-to-node-type assignment) regenerates from the `hq` stream with a new seed per attempt. The gate schedules are fixed, so the knowledge a player gains about periods carries over, but a specific route does not. Intel's revealed node types do not carry over.
- **Raid interlude mid-HQ** (GDD 4.4). The gate clock pauses, because it advances only on node completion, so a player can plan around the interlude.
- **Heat consequences.** Death adds Heat as normal. Because the Circus is long, a raid threshold crossing mid-run is a real risk.
- **Giving up.** Abandon run follows GDD 4.5.

## 8. Systems needed

| Dependency | Source | Data-only fallback |
|---|---|---|
| Gate clock: `step_count`, per-ring schedule, powered-edge function, hold counters | NEW: Circus clock (in the map graph, with the G12 route redesign; spiritually near N16 but not covered by it) | Yes: `open_slot_by_step` tables on descent edges, with the telegraph as table lookahead |
| Lint that every ring has at least one open room at every step | Test only | n/a |
| VERDICT status | NEW: VERDICT status | ON_COMBAT_START APPLY_STATUS OVERCLOCKED (drops the Good / WEAK branches) |
| Favor meter and HUD chip | NEW: Favor meter | RunState counter with event-style consequences; the chip is the only new UI |
| Jeered, Grand Stand starting state | N16 (`next_combat_overrides`) | None. If N16 slips: drop Jeered, and the Grand Stand becomes the Daemon reward only |
| Rest node | D4 (approved) | n/a |
| Ring Vault (Server Rack reuse) and reward rows | N18 | Hard-coded offers as today |
| Rostrum boss, phases and parking | N3, N5, N14 in the corp draft | n/a |
| CORRUPTED as a 2× RAM cost | N9 | Per R9 |
| Per-HQ unique graph and generation on demand | G12 / D10 route redesign (not an N#) | A fixed 9-layer template |
| Event wheel (optional Bribe) | N17 (optional) | A plain event choice |

**Build order.**
1. A fixed 9-layer graph with `open_slot_by_step` descent edges (the data-only fallback), plus the lint test. Playable with no art.
2. The clock function, the 1-step and 4-step telegraph, and Breach holds.
3. The Favor meter, Rest nodes, the Box Office, and the Ring Vault.
4. The VERDICT opening mark, then N16 overrides for Jeered and the Grand Stand.
5. The Grand Stand readout and Favor payouts.
6. The slot-driven landmark version, once the art's slot generator exists.

## 9. Art hooks

The build exposes these per frame (PIPELINE 8.4 rule 4):
- `step_count`; per ring `gate_slots_now` and `gate_slots_next` (for the pencil telegraph); `ring_slots` (6 / 5 / 4 / 3); `held_rings` (a bronze lock on the barrier).
- Per descent link: `powered` (bool) and `opens_in_steps` (int or null).
- Per room: `ring`, `slot`, `state` (UNREAD / READ / CURRENT / CLEARED), `node_type`.
- `sideways_available` per last-layer room, for the always-open link glow.
- `favor` (0–5), driving the terrace crowd light.
- `verdict_marked` on the current fight (a thumb on the arena preview).
- `grand_stand_state` (OPEN / NEUTRAL / SEALED) for the box's lighting, and `rostrum_phase` for the arcade shift.
- Intel `telegraph_depth` (1 or 4), so the art shows one or four ghost positions.

Rotation is a tween between the `gate_slots` of consecutive steps. Slots are integers from the authored schedule, so the visual can never disagree with the rule.

## 10. Open questions

Q: The sideways node is the only way to shift the clock. Is that enough control, or should a paid wait (a ticket that advances the clock one step without a fight) exist, at the cost of making the clock partly free?
Q: Favor reads CORRUPTED count, which pushes the player to cleanse in every fight, while the Rostrum's own VERDICT punishes Perfects. Is that tension wanted, or should Favor be dropped?
Q: Should the 4-step lookahead be Intel's reward (proposed) or default knowledge? A default lookahead makes the Circus a pure planning puzzle; an Intel-gated one makes it partly guesswork for a 0-Intel player.
Q: Is a 22–32 minute HQ run (about 25 typical) acceptable, or should the Circus drop a ring to land near 20 minutes?
Q: Should operatives start the HQ run healed with Favor as the scarce resource, or keep the Rest-node heal budget (45 HP) that gives a 58% arrival?
