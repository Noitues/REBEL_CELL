<!-- draft via Message Batches API, claude-sonnet-5-5, batch msgbatch_01HADBSF5pLwaHAq7nbABzZa, custom_id hq__aurelian; status ok; tokens in 13439 cache-write 0 cache-read 32007 out 8405; cost $0.059. A DESIGN DRAFT for the designer's review: nothing here is built. -->

# Aurelian Concord: HQ netrun draft

Working names: the HQ is THE CIRCUS AURELIUS ("Circus"). The boss is the ROSTRUM FIGHT (VERDICT every turn, Grand Stand hub). All numbers are placeholders pending the balance sim.

## 1. Concept & the named mechanic

**What the art shows.** The HQ is a colosseum with four concentric seating terraces. Each terrace has a bronze barrier with 2 gates, and the barriers turn each step in alternating directions. The Rostrum sits on the arena floor. Rooms are cutaway boxes on the terraces, 6 / 5 / 4 / 3 per ring (18 in the art). Links along a ring are always open. Links down a ring exist only where a gate stands. The next step's gate positions are shown as a yellow pencil telegraph.

**As a game mechanic.** The player descends from the outer ring (ring 1, the cheap seats) to the arena. Each time the player completes a node, the Circus takes one STEP and the four gate rings rotate by fixed amounts. You can always move sideways along your ring, but you can only descend through a gate that is open at the moment you leave. Every sideways move costs a node and so costs a step. The route is therefore a timing puzzle on top of the usual fight graph. Fights are not tolled by position, but position is tolled by time.

**Why it cannot be mistaken for another HQ.**
- Halcyon is a fixed ladder watched by an eye.
- Solace is an UP / ACROSS ladder.
- Orbital is doors and a rocket.
- Meridian is a shuttling freight line.
- Rebel Cell is an alley with a window sequence.
- Aurelian is the only HQ whose connectivity is a function of a deterministic clock. It is a rotating plan, not a vertical cycle, and it is solvable on paper from the telegraph.

**Spine.** The TURNING GATES (§3.1). Two supporting rules (§3.2, §3.3) are the VERDICT house rule scaled up to the run, and the crowd's Favor. §3.4 is the one-off Grand Stand finale gate.

## 2. Structure

**Size.** 9 layers, grouped as 4 rings plus the arena. Per D10 it may run long, and the Circus wants more than 7 because four rings need real descent room. Layers are numbered L1 to L9.

| Ring | Layers | Nodes per layer | Total |
|---|---|---|---|
| Ring 1 (outer, 6 rooms) | L1–L2 | 3, 3 | 6 |
| Ring 2 (5 rooms) | L3–L4 | 3, 2 | 5 |
| Ring 3 (4 rooms) | L5–L6 | 2, 2 | 4 |
| Ring 4 (inner, 3 rooms) | L7–L8 | 2, 1 | 3 |
| Arena | L9 | 1 (the Rostrum fight) | 1 |

Total 19 nodes. This is an honest superset of the art's 18 rooms plus the Rostrum, but room counts per ring are generated on demand (PIPELINE 8.4 rule 5). The art's 6 / 5 / 4 / 3 is the default for the 7-layer-compatible case. Rings are not layers: a ring holds one or two layers, which is why the ring has a "slot order" that matches layer order and then node order.

**Edges.**
- **Along-ring edge** (same ring, adjacent node in the same or next layer): always open and always powered. It costs a step like any move.
- **Descent edge** (ring r to ring r+1): exists in the graph from any node of the ring's last layer to the nodes of the next ring's first layer, but is powered only while a gate of ring r's barrier stands at the departing room's azimuth when the player commits the move.
- **Gate test happens at commit.** The step rotation happens after the node resolves and before the next move. So the player at node N sees the gates as they are now, which equal the pencil telegraph from the previous node. Moving along the ring costs a node. Descending is free only in the sense that the node you land on is the next layer's.

Because every node is a one-way graph hop, the "wait" question is only about whether to take a sideways node, not whether to idle (Q1).

**Layer map** (rooms are azimuth-slotted on the ring; `=` along-ring, `v` descent through a gate that must be open):

```
RING 1  L1: [a1]=[a2]=[a3]
            |   |   |        (all L1 nodes are Routers; each connects to the L2 node(s) at its slot or adjacent)
        L2: [b1]=[b2]=[b3]
                 v   v       (descent edges from b2, b3 to ring 2; b1 only via b2)
RING 2  L3: [c1]=[c2]=[c3]
        L4: [d1]=[d2]
                  v  v
RING 3  L5: [e1]=[e2]
        L6: [f1]=[f2]
              v
RING 4  L7: [g1]=[g2]
        L8: [h1]              (single node, the Grand Stand gate, §3.4)
ARENA   L9: [ROSTRUM FIGHT]
```

**Branching rules (generator).**
- Every ring's last layer has at least 2 rooms that can descend, so the player always has a choice, but at any given step at most 1 to 2 gates are aligned with them.
- Gate azimuths and step angles are authored per ring (§3.1), so the schedule is deterministic. Generation only places room azimuths and node types.
- Guarantee: from any reachable node there is a gate-open schedule that reaches the next ring within 4 steps (checked by the generator, Q2). The player never softlocks, only wastes time.
- A fresh level layout uses the `hq` RNG stream seeded at HQ build (checkpointed). Gate schedules use no RNG at all.

**Mapping onto landmark slots.** Per PIPELINE 8.4: the landmark generates slots on demand. Slots are (ring, azimuth, floor_z). Nodes are assigned in layer order, then node order, walking each ring's slot list from the far half of the bowl, which faces the camera. The ring structure is the layer structure (L1–L2 to ring 1, and so on), so the visual descent equals the layer descent. Link geometry follows the step class: along-ring links run flat on the terrace, descent links run through the gate anchor (falling). The type is a hint only and never names the node.

The Rostrum fight is the one slot on the arena floor, at the TARGET on THE ROSTRUM.

## 3. Unique mechanics

### 3.1 THE TURNING GATES (spine)

- **Rule.** Each ring has 2 gates, each `gate_w` 9° wide. After every node the player completes, each ring's gates rotate by that ring's step: ring 1 +24°, ring 2 −26°, ring 3 +29°, ring 4 −31° (clockwise / counter-clockwise alternating). A descent link is powered only when a gate overlaps the room's azimuth (within gate_w / 2) at the moment you leave.
- **Trigger.** Per node completed (fight, event, shop, rest, cache all count; a step is a node resolution). Not per turn of combat.
- **What the player sees.** The gate rings turn. The pencil telegraph in yellow shows where each gate will be after the next step. Powered descent links are lit, unpowered are de-powered grey. The room tooltip says "GATE OPEN NOW / OPEN IN N STEPS / CLOSED" for each ring-down edge. Because angles are fixed integers, the HUD can print a lookahead of the next 4 steps per room.
- **Counter.** Plan your sideways nodes. Spend an Exploit (see §4):
  - Breach (gate codes) holds one ring's gates in place for one step, once per ring.
  - Intel (client rolls) extends the telegraph from 1 step to 4 steps. This matters only when the printed lookahead is withheld by default (Q3: the 4-step lookahead should be Intel's reward, with one step shown by default).
- **Determinism.** No RNG. The state is `step_count` and the authored angle table. Preview equals result: the telegraph is computed with the same function as the powered check.
- **Fallback.** Data-only: it can be built as authored "open on steps {a, b}" tables per ring-edge, with no geometry, if the angle math slips.

### 3.2 VERDICT of the Circus (house rule applied to the run)

- **Rule.** Every fight node in the Circus carries the crowd's VERDICT: the first time your pointer resolves a slice marked by the corp's VERDICT, it behaves as in the house rule (Perfect OVERCLOCKED, WEAK CORRUPTED, GOOD keeps the mark). On top of that, a Circus-only layer: at the start of each fight the crowd marks the player slice under the pointer, so combat opens with a mark.
- **Per-layer trigger.** The opening mark is every fight. There is no random mark choice (it uses the slice under the pointer after the start-of-turn respin, which is already a named random event with a checkpoint).
- **What the player sees.** A thumb badge on the marked slice, and the preview chip shows the verdict result before SEND IT.
- **Counter.** Nudge the marked slice to a Perfect, or burn it on a WEAK in a safe fight; Cleanse or Encrypt removes or absorbs the mark.
- **Determinism.** No new RNG. VERDICT uses existing statuses and tiers (GDD 2.4, 2.9). Needs the VERDICT rule (listed in §8).

### 3.3 THE CROWD'S FAVOR

- **Rule.** A run-wide meter, Favor, 0–5. Each fight node ends with a result: win with at least one Perfect on a marked slice gives +1; a win with a CORRUPTED verdict landing gives −1; the others do not change it. At Favor 3+ the next descent through a gate is a "Thumbs Up": the gate is held open for one extra step (as though Breach). At Favor 0 the next fight's enemies are "Jeered": each starts with +1 resistance (existing ENEMY_RESISTANCE rule). Favor resets at the Grand Stand.
- **Trigger.** Evaluated at each fight end.
- **What the player sees.** A laurel / thumb meter in the HUD and the crowd lights on the rings: the terraces fill with warm light as Favor rises, go dark at 0.
- **Counter.** Fight cleanly, or accept the jeering with a cheap Router for a reset.
- **Determinism.** Pure function of combat results. No RNG.
- **Fallback.** Data-only: it can be implemented as event-style consequences with the Favor counter in RunState; the HUD chip is the only new UI.

### 3.4 THE GRAND STAND (finale gate, L8)

- **Rule.** The single L8 node is the emperor's box, a puzzle node and not a fight. A VERDICT is called on the player, not a slice: the crowd reads your run. Favor decides what you carry into the Rostrum:
  - Favor ≥ 4: THE GRAND STAND is "on your side": the boss fight starts with the Grand Stand (its hub) already breached, regardless of owned Exploits, for the first 3 turns.
  - Favor 2–3: neutral.
  - Favor ≤ 1: the Grand Stand is "sealed": it cannot be breached this fight, and the Rostrum starts with one more VERDICT mark on your wheel.
- **Determinism.** A threshold on a counter. The result is shown on the L8 node before you enter.
- **Counter.** Manage Favor for 8 layers. Breach Exploit adds +1 effective Favor here (see §4).

## 4. Node kit

**Fight node types** (node-type table follows the GDD: Router, Elite Router, Terminal, Mainframe, Server Rack). The Circus adds Rest and Cache as HQ-only content (D4 REST node is approved).

| Node | Circus twist | Mini-fight / puzzle |
|---|---|---|
| Router (standard fight) | Opens with the VERDICT mark (§3.2). Enemies from the corporation's pool at T4: Lictor with fasces satellites, Legionary drone, Tax Farmer, Lanista, Vestal Firewall. | Fight |
| Elite Router | A Praetorian or Censor, 2 phases. Wins grant +1 Favor regardless of verdict. | Fight |
| Terminal (event) | Speakers: the Patron, Lanista Corvina, the Tribune of Clients. A Circus event may offer "Bribe the gatekeeper": spend Cycles to hold one ring's gates one step. | Puzzle / choice |
| Mainframe (shop) | The Box Office: sells Cycles-priced "tickets", which are one-use gate holds, and the usual Firmware and Daemons. One per ring maximum. | Shop |
| Rest (REST, D4) | The Hypocaust: heal 25 % max HP, or remove one CORRUPTED slice, but the step still passes. Max 1 per ring. | Heal |
| Cache | A Server Rack variant at the ring's last layer: an Elite-strength fight that banks Schematics and, at ring 2 and ring 3, a rare Daemon. | Fight |
| Grand Stand | The L8 puzzle node (§3.4). | Puzzle |
| Rostrum fight | The boss fight, ROSTRUM FIGHT (designed in the corp draft). | Boss |

**Layer typing** (Router default; guaranteed picks, not a schedule):
- L1–L2: Routers only, plus one Terminal at L2.
- L3–L4: Routers, one Elite, one Mainframe.
- L5–L6: Routers, two Elites, one Rest, one Cache on L6.
- L7: Routers, an Elite, one Rest.
- L8: the Grand Stand.
- L9: the Rostrum.

**Exploit / key buildings (D5).** Each owned Exploit pays off inside the Circus:

| Exploit | What it does here |
|---|---|
| INTEL (client rolls) | The gate telegraph shows 4 steps ahead instead of 1, and the HUD shows each node's type from L1 (no unknown nodes). |
| BREACH (gate codes) | Once per ring, hold that ring's gates for one step (the player triggers it at the room). It also adds +1 effective Favor at the Grand Stand. In the boss fight it is the usual hub breach (Grand Stand). |
| VIRUS (open dole) | Rest nodes heal 40 % instead of 25 % and Cache nodes give an extra reward choice. It frees the ration chips: one free Mainframe item per HQ run. |

`min_exploits_for_breach = 3` remains for entering the HQ at all. Exploits do not change Circus layout, only how readable and controllable it is, so a 3-Exploit player still faces the same clock.

## 5. Pacing & difficulty curve

**Assumptions.** T4 enemies (R2: normal 56–70 HP, elite 112–144 HP), 3–4 turns per phase (R1). Reference damage 18 per turn at T4.

| Node class | Count (typical route) | Turns | Minutes |
|---|---|---|---|
| Routers | 7–8 | 3.5 | ~2 each |
| Elites | 2–3 | 7 | ~3 each |
| Cache | 1 | 7 | ~3 |
| Terminal / Mainframe | 2 | | ~1.5 each |
| Rest | 1–2 | | ~0.5 each |
| Grand Stand | 1 | | ~1 |
| Rostrum | 1 | 12–20 | ~6–8 |

A typical 10 to 12 node route is about 30 to 36 minutes. This is longer than a 15-minute Site netrun by design. A HQ is the campaign's climax (D10). Detouring along a ring adds 1 to 3 nodes at about 2 minutes each, a deliberate cost for waiting.

**HP pressure.** Normal fights lose roughly 8 to 12 HP at a reference player (5 to 8 intake per phase). Elites lose about 15 to 20. HP carries between fights as in any netrun. Over ~10 fights that is ~110 to 140 HP of damage against about 60 HP. The budget therefore needs about 100 HP of healing:
- 2 Rests at 25 % (about 30 HP, scaled on a 60 HP operative);
- Mainframe heals, event heals, a Virus Rest boost;
- Favor as a soft heal: a Thumbs-Up descent skips a likely detour node (Q4).

Rest nodes are scarce on purpose, so route choice matters. The first-pass target is for a reference player to arrive at the Rostrum around 50 to 60 % HP.

**Heat.** Each fight node adds the usual Heat (Elite +1). The HQ run is a campaign endgame run at Heat 60 to 90 in a typical campaign, so ENEMY_RESISTANCE (+1 at 50) is already on. Additional pressure: every detour node adds Heat as normal, so waiting for a gate costs Heat in addition to time.

**Difficulty curve.** Ring 1 teaches the gate clock with a forgiving window (a gate open at the start). Ring 2 introduces opposing rotation, with the telegraph's first miss expected. Ring 3 has the tightest windows (29° steps against narrow rooms). Ring 4 is short but its gate is the 31° counter-step, so a mistake there costs one node, not several.

## 6. Rewards

Beyond the boss (the campaign's win condition per GDD, the kill code):
- **Per-ring Cache bank:** Schematics banked immediately on capture, as a Server Rack (GDD 4.2). Ring 2 and ring 3 caches also offer one rare Daemon.
- **Favor payout:** at the Grand Stand, Favor 4 to 5 grants a one-time "Imperial Favor" Daemon choice (a VERDICT-themed Daemon, for example "a GOOD landing on a marked slice clears the mark without a verdict").
- **Completion:** the usual run completion (survivors home at full HP, unspent Cycles convert at 10:1, Rank +1).
- **Story:** the Triumph beat (the path finale) plays from the Rostrum win. Per-path flavour comes from the story path chosen at campaign start.
- **Per-Exploit bonus:** each unused Breach hold at the end converts to 2 Schematics ("returned gate codes"), because the HQ run is a one-shot, so unused codes would otherwise be wasted.

## 7. Failure & retry

- **Death.** The same as any netrun (GDD 4.2): the operative is permanently lost with everything unbanked. Campaign gains 10 + tier Heat. Banked Cache Schematics and Daemons are kept.
- **HQ retry.** The Circus resets: the gate clock returns to step 0 and Favor to its start value. The layout (room azimuths, node types) regenerates from the `hq` stream with a new seed per attempt, so the route differs (PIPELINE 8.4 rule 5). Intel knowledge does not carry over.
- **Breach (home server) mid-HQ.** A raid interlude can occur mid-netrun (GDD 4.4). The gate clock pauses during interludes. It advances only on node completion.
- **Heat consequences.** Death adds Heat as normal; a raid interlude during the HQ is possible at the Heat thresholds. Because the Circus is long, raid risk is real. A mid-HQ interlude should not alter the clock, so the player can plan around it.
- **Giving up.** Abandon run follows GDD 4.5.

## 8. Systems needed

| Dependency | Source | Fallback |
|---|---|---|
| Gate clock, powered descent edges, telegraph | NEW: Circus clock (`step_count`, per-ring angle table, edge-power function in the map graph). Related to N16 (map edits) in spirit but not covered by it. | Data-only: edges carry `open_on_steps` lists per ring (authored tables). No geometry needed. Costs readability only. |
| VERDICT status rule | Needs a GDD line and test (art notes). Uses existing statuses, so rule-only. Interacts with N6 (opening mark is a combat-start rule). | The opening mark may be made via an existing APPLY_STATUS on combat start, with VERDICT as an enemy-only slice rider first. |
| Favor meter | NEW: run counter plus HUD chip. | Data-only through event-style consequences in RunState, as in N16. |
| REST node, Cache node | D4 REST approved. Cache is a Server Rack with N18 reward rows. | Server Rack reuse. |
| Run-level overrides (jeered enemy resistance, Grand Stand starting state) | N16 (`next_combat_overrides`) | None; needs N16. |
| Reward rows (Imperial Favor, ring Daemons) | N18 | Hard-coded offers as today. |
| Boss phases, parking | N3, N5 (Rostrum fight), N14 in the corp draft | n/a |
| Per-HQ unique graph and generation on demand | G12 / D10 route redesign (not an N#) | Fixed 9 layer template. |
| Event wheel (optional "Bribe") | N17 (optional) | A plain event choice. |

**Build order.**
1. Fixed 9-layer graph with tabled `open_on_steps` descent edges (data-only fallback). Playable with no art.
2. The Circus clock function, telegraph, and the 4-step Intel variant.
3. Favor meter, Rest and Cache nodes, Box Office shop.
4. VERDICT opening mark (waits on the VERDICT rule), N16 overrides for Jeered and the Grand Stand.
5. Grand Stand puzzle node and Favor payouts.
6. Angle-driven version of the clock once the art slot generator exists.

## 9. Art hooks

The build must pass these per frame (PIPELINE 8.4 rule 4):
- `step_count`, and per-ring `gate_angles_now` and `gate_angles_next` (for the pencil telegraph); `gate_w` per ring.
- Per descent link: `powered` (bool) and `opens_in_steps` (int, or null).
- Per room: `ring`, `azimuth`, `state` (UNREAD / READ / CURRENT / CLEARED), `node_type`.
- `held_rings`: which rings are held by a Breach or Thumbs-Up this step, so the barrier can show a bronze lock.
- `favor` (0–5), which drives terrace crowd light (the warm fill).
- `verdict_marked` on the current fight (a thumb on the arena preview).
- `grand_stand_state` (OPEN / NEUTRAL / SEALED) for the box's lighting, and `rostrum_phase` for the boss phase 2 arcade shift (verdigris to gilt, per the art notes).
- Intel `telegraph_depth` (1 or 4) so the art shows one or four ghost positions.

Rotation is a tween between `gate_angles` of consecutive steps. Angles are always integers from the authored table, so the visual can never disagree with the rule.

## 10. Open questions

Q: May the player wait in place (a step passes with no fight) to catch a gate, or only walk? Proposed: walk only, because a wait would make the clock free. A cheap alternative is a "Rest" node as the only wait, at a limit of one per ring.
Q: Is the guarantee "every room reaches the next ring within 4 steps" enough, or should a designer-set minimum of 2 simultaneously open descents per ring be enforced per ring-edge?
Q: Should the 4-step lookahead be Intel's reward (proposed) or default knowledge? A default lookahead makes the Circus a pure planning puzzle, while an Intel-gated one makes it partly guesswork for 0-Intel players.
Q: Does Favor from VERDICT landings pull the player toward Perfect-hunting in every fight, so that it conflicts with the Rostrum fight's own VERDICT, which punishes Perfects elsewhere?
Q: Is a 30 to 36 minute HQ run acceptable, or should the Circus be capped near 25 minutes by dropping a ring (3 rings plus arena)?
Q: Should the HQ's total heal budget come from Rest nodes, or should the HQ run start the operative healed, with Favor acting as the scarce resource instead of HP?
