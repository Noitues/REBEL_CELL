<!-- draft via Message Batches API, claude-sonnet-5-5, batch msgbatch_01TQsqGnerTdLwJEata9mp6i, custom_id v2__hq__orbital; status ok; tokens in 11818 cache-write 0 cache-read 32585 out 21567; cost $0.123. A DESIGN DRAFT for the designer's review: nothing here is built. -->

## Changes vs v1

- **Issue 1 (layer count and map contradictions) →** All counts are re-derived and the table, map and prose now agree.
  - Override route: **12 layers** (nodes per layer 1,2,3,1,1 | 3,1,1 | 2,1 | 2 | 1).
  - Extra-circuit route: **14 layers** (L11 ring relay, L12 antenna top room, L13 Retarget 4, L14 LAUNCH CONTROL).
  - v1's "15" is gone.
  - The antenna elite stays mandatory, so L4 and L7 are single-node chokepoints. I did not use the critic's 2-node L4, because a second node would bypass the elite. The event moved to L6.
  - The fork row is explicit that it holds two nodes and leads into different layer counts.
- **Issue 2 and triage BLOCKER 2 (no HP or thresholds) →** The Launch Guard (sabotage fight), Elite A and Elite B each have HP, a threshold, per-phase budget arithmetic against R2 and slice layouts (sizes re-added to 30).
  - The sabotage is now **elite-class**, because the R2 mini-boss table is "n/a" at T4.
  - Elites are 126 HP.
  - The Launch Guard is 112 HP, to offset its satellite guards.
- **Issue 3 and triage BLOCKER 3 (Pressure duplicates enrage) →** Pressure is deleted. Fights use R4 enrage with the elite default (start 8, every 5, +25 %).
  - Shut doors only move the antenna elites' start turn to 6, a per-fight override of `EnrageData`.
  - Normals stay enrage-off.
- **Issue 4 (Fallout garbled, preview timing) →** Rewritten.
  - Override Fallout is FLAT corruption (R5) of 2 non-NULL slices.
  - The draw (`hq_fallout`) happens once when the fork is first viewed, is checkpointed and locked in.
  - The fork card shows the exact slices (and an ENCRYPTED absorb), so the preview equals the result.
- **Issue 5 (Venting, Solar Flares, Doors modifier) →** Venting and "Solar Flares unavailable" are removed, so N20 is no longer needed. The doors rule is reduced to two data fields: an extra free nudge when OPEN and an enrage start override when SHUT. Both ride on N4 plus one small NEW field.
- **Issue 6 (N# tags) →**
  - Added N12 (the sized slices are central to the fights).
  - N7 is not added, because nothing in this HQ locks nudges.
  - N11 is dropped, because no fight here uses a second needle.
  - N16 is relabeled to what it actually does here: the Tributes (Salvo, Jam, Kill zone) are `next_combat_overrides`, which is its real job.
  - Dish Link is a NEW action with a concrete card fallback.
- **Issue 7 (G11, strike tally, retry) →**
  - The campaign strike tally and the raid-source effect are **cut** (G11 says DOWN is a source for no one, and this is raid-pass scope). Replaced by Schematics per retarget.
  - Retry text fixed: a new seed, nothing in run state carries, only banked Schematics. The "override failure carries over" rule is removed.
- **Issue 8 (R7 and boss ownership) →**
  - "Cleared dishes disable buffs" and "Breach skips the 2nd needle" are deleted. Boss buffs are left to R7 and the corp draft.
  - The override now starts the boss at its phase-2 entry through a `start_phase` field, i.e. at the existing phase-1 threshold floor (R3 parking logic intact, no HP rewrite).
  - Q: remains whether to keep it.
- **Issue 9 (RNG stream names) →** `hq_rewards`, `hq_fallout` and `events` are named and checkpointed, each with its draw point.
- **Issue 10 (Salvo, Jam) →**
  - Salvo applies to normal fights only (1 phase, no thresholds, so parking is irrelevant).
  - Jam uses the existing FREEZE effect.
  - Kill zone sets an elite to 112, the lower band edge.
- **Critic Qs →** Override skipping P1 is kept, flagged as Q:. Whether 14 layers is within D10 is addressed in §5 and Q:. Dish Link preview now explicitly applies enemy resistance.
- **Kept because the critic marked it strong:** the cyclic retarget loop with echo nodes, the price-for-speed fork, Intel/Breach/Virus as convenience-only payoffs, and the art-state hooks.

---

# Orbital: HQ netrun draft

## 1. Concept & the named mechanic

**What the art shows:** a launch podium with a silo whose doors open and shut. A rocket rises out of it. Hacked bands on the rocket light lime, one per retarget. Dish stations ring the podium. A truss antenna tower carries two elite vaults. A red gantry holds LAUNCH CONTROL. An override link runs from the antenna's top room to LAUNCH CONTROL.

**Restated as a game mechanic: THE RETARGET CYCLE.** The HQ is a loop of laps ("circuits") around the dish ring, not a climb. Each circuit:

1. Fight at the ring (dish stations; cleared ones return as free "echo" stops).
2. Climb the antenna (a mandatory elite vault; the third circuit skips it).
3. Sabotage the rocket (the Launch Guard fight at the silo).
4. Each sabotage lights one hack band and **retargets** the rocket onto one of Orbital's own facilities, and grants a Strike Tribute.

After 3 retargets the **LAUNCH OVERRIDE** unlocks. The player may fire the rocket early into the shut doors and walk to LAUNCH CONTROL: faster, but the player arrives Fallout-corrupted. Or they may take one more circuit (a 4th retarget, a Firmware cache) and face a boss that begins enraged.

**Why it cannot be mistaken for another HQ:**
- Solace is a vertical ladder.
- Halcyon has a pyramid with an eye.
- Meridian has a freight line that shuttles.
- Rebel Cell is a mirror.
- Orbital is the only HQ that **revisits its own map**. Cleared stations change state each lap, and the player's own sabotage count is the clock.

**Core question of the netrun:** "How many times do I go round, and what do I carry into the boss for it?"

## 2. Structure

**Length:** 12 layers on the override route; 14 layers on the extra-circuit route. Both are longer than the 7-layer standard (D10 allows it).

| Layer | Content | Nodes |
|---|---|---|
| L1 | PAD (start, a fight-free arrival; Tribute and Link counters reset to 0) | 1 |
| L2 | SE dish fight or NE dish fight (Router fights, doors OPEN) | 2 |
| L3 | SE causeway outpost fight / Cache (shop) / NE causeway outpost fight | 3 |
| L4 | **Antenna elite vault A** (mandatory chokepoint) | 1 |
| L5 | **Silo Sabotage 1** (Retarget 1) | 1 |
| L6 | NW dish fight / Echo (a cleared dish) / Event | 3 |
| L7 | **Antenna elite vault B** (chokepoint) | 1 |
| L8 | **Silo Sabotage 2** (Retarget 2) | 1 |
| L9 | SW dish fight / Rest | 2 |
| L10 | **Silo Sabotage 3** (Retarget 3, override goes LIVE) | 1 |
| L11 | **FORK:** LAUNCH OVERRIDE / Ring relay (fight, the long route) | 2 |
| L12 | LAUNCH CONTROL: the Launch Control boss (override route) | 1 |
| L12-L14 (long route) | L12 antenna top room (Cache); L13 Silo Sabotage 4 (Retarget 4); L14 LAUNCH CONTROL | 1, 1, 1 |

Override route: 12 layers. Long route: L1-L11 plus L12, L13, L14 = 14 layers.

```
L1  PAD
     |
L2  [SE dish] [NE dish]
       |  \  /  |
L3  [SE outpost] [Cache] [NE outpost]
          \      |      /
L4        [ELITE VAULT A]        doors SHUT
                 |
L5        [SABOTAGE 1]           Retarget 1
         /       |       \
L6  [NW dish] [ECHO] [Event]
         \       |       /
L7        [ELITE VAULT B]        doors SHUT
                 |
L8        [SABOTAGE 2]           Retarget 2
             /       \
L9      [SW dish]   [Rest]
             \       /
L10       [SABOTAGE 3]           Retarget 3, override LIVE
             /       \
L11  [LAUNCH OVERRIDE]  [Ring relay fight]
         |                    |
L12  [LAUNCH CONTROL]    [Top room: Cache]
                              |
                         L13 [SABOTAGE 4]  Retarget 4
                              |
                         L14 [LAUNCH CONTROL]
```

**Edge rules:**
- Layers fan out and in as drawn. L4 and L7 are chokepoints, so the antenna elite cannot be skipped.
- Echo appears at L6 only when at least one dish was cleared on lap 1 (always true by then). It is the cleared dish the player walked, drawn as an echo node.
- Per the art rule, a seed may add one node to a 2-3 wide layer (never to a chokepoint).

**Mapping onto landmark slots:**
- PAD, SE, NE, NW, SW are the dish ring. The two causeway outposts are ring-link rooms between dishes.
- The two elite vaults are the antenna's two enclosed rooms (one per lap), and the top room is the L12 Cache on the long route.
- The silo rim is the sabotage slot (the shaft is the visible mover). The gantry deck is LAUNCH CONTROL.
- The override is the link from the antenna top room to LAUNCH CONTROL. The ring relay (L11, long route) reuses the PAD slot, revisited.
- No new geometry is needed: laps reuse built slots.

**Boss:** the "Launch Control boss" (working name) is designed in the corp/enemy drafts. This HQ only sets its pre-fight conditions (§3.3).

## 3. Unique mechanics

### 3.1 The Retarget Dial (spine)
- **Rule:** the run carries `retargets` (0-4). Each Sabotage clear increments it and lights one lime band on the rocket. Each also grants one **Strike Tribute**, a run-wide effect picked from 2 offered:
  - **Salvo:** the next normal fight starts with the enemy at 85 % HP (PERCENT; applies to normals only, so no parking interaction).
  - **Jam:** the next fight's enemy wheel is FROZEN on turn 1 (it skips its start-of-turn respin; existing FREEZE).
  - **Kill zone:** the next elite vault has 112 HP instead of 126 (the lower edge of the R2 band).
  - **Supply drop:** +1 item in the next Cache/shop.
- **Trigger:** on Sabotage clear. The offered pair is drawn from the `hq_rewards` stream at the checkpoint on entering the silo node. The preview of both Tributes is shown before choosing.
- **What the player sees:** the lime hack bands, a "RETARGET n/3" chip, and the readout naming the Orbital facility struck (a fixed list in `content/`).
- **Counter:** none; it is the player's clock. The cost is the fork (§3.3).
- **Determinism:** the pair is seeded and set before the fight, so undo and reload cannot reroll it.

### 3.2 Bay Doors (state sets a fight rule)
- **Rule:** the silo doors are OPEN on ring layers (L2, L3, L6, L9, L11 relay) and SHUT on antenna and silo layers (L4, L5, L7, L8, L10, L13).
  - **OPEN (ring fights):** the player gets **1 extra free nudge** per turn ("open sky"). These fights are normals (enrage off).
  - **SHUT (antenna elite vaults only):** the enrage starts earlier. `EnrageData.start_turn = 6` instead of the elite default 8 (every 5 turns, +25 % additive, R4). Sabotage fights keep the default start 8.
- **Trigger:** a pure function of node type, applied at fight start; the doors animate at the layer boundary.
- **What the player sees:** the doors, an OPEN/SHUT chip on the dial, and the enrage chip with its start turn.
- **Counter:** speed. A 126 HP elite at 18 damage per turn lasts about 7 turns, so the first step at turn 6 hits during phase 2. That makes the antenna elites a "land the burst before turn 6" puzzle. Breach turns SHUT back into the default 8 (§4).
- **Determinism:** no RNG. The preview shows the next enrage step as in R4.

### 3.3 The Fork: price of the Override
The fork card shows both prices as exact values. Neither the card nor the result involves a hidden draw.

**LAUNCH OVERRIDE (12 layers):**
- The rocket fires into the shut doors, and the Launch Control boss **starts at its phase-2 entry** (`start_phase = 2`, HP at the first phase threshold floor, R3 intact). The boss's own buffs and Exploit counters (R7) are unchanged and owned by the corp draft.
- **Fallout:** 2 non-NULL slices of your wheel become CORRUPTED (FLAT corruption, R5) at fight start, doubling RAM on them (R9).
  - The 2 slices are drawn once with the `hq_fallout` stream the first time the fork is viewed. The result is checkpointed, locked in, and shown on the card.
  - An ENCRYPTED slice absorbs its hit, and the card marks it "absorbed".
  - The player can still spend the pre-fight nodes on Cleanse/Encrypt cards before L11 knowing the draw happens at the fork.

**Extra circuit (14 layers):**
- No Fallout and no skipped phase, but **Retarget 4 Overdrive:** the boss starts with one enrage step applied (×1.25 damage from turn 1, additive).
- The player gains a 4th Tribute, the L12 Firmware cache and the Sabotage 4 Schematics.

**Determinism:** `hq_fallout` is a named stream drawn at the first fork view only; Overdrive and `start_phase` are deterministic.

### 3.4 Dish Link (cleared stations as ammunition)
- **Rule:** each dish fight won adds a **Link** (max 4). Before any later fight's first player action, the player may spend 1-2 Links, and each Link is one free nudge of ±1 tick on the *enemy* wheel (the enemy's resistance absorbs per tick, as in 2.5).
- **Trigger:** once per fight, in the player phase. The nudge sits in the undo stack and the preview applies resistance first. Echo stops restore Links.
- **What the player sees:** the dish rims lit per available Link, and the rim animating when aimed.
- **Counter:** enemies with Weight (resistance) absorb it, and a boss Compliance Lock blocks it.
- **Determinism:** pure arithmetic; no RNG.

## 4. Node kit

| Node | Twist here | Type |
|---|---|---|
| **Dish fight / outpost fight** (Router) | Doors OPEN (extra free nudge); a Link earned on win; normal, 1 phase, T4 HP 56-70 | Fight (normal) |
| **Echo station** (L6) | The cleared dish. No fight: heals 10 % max HP (PERCENT) and restores 2 Links. One use | Rest |
| **Antenna elite vault A and B** | Doors SHUT (enrage from turn 6); 126 HP, 2 phases; reward 1 Firmware | Elite |
| **Silo Sabotage** | The Launch Guard (below); doors SHUT; banks Schematics | Elite-class fight |
| **Cache** (L3, L12) | L3: a shop with −10 % price per retarget. L12 top room: pick 1 of 3 Firmware (fallback: a plain offer if the cache puzzle is not vetted) | Shop / Cache |
| **Event** (L6) | One of 2 HQ events, drawn from the `events` stream | Event |
| **Rest** (L9) | Heal 25 % max HP (PERCENT) or swap Firmware locations (D4) | Rest |

### 4.1 Elite vault A: "Truss Warden" (T4: 126 HP, threshold 0.5)
Budget: (18 dpt × 3.5 turns) × 2 phases = 126, no sustain, one needle. Band 112-144 ✓. Phases are 63 HP each.

- **P1, Locked Gate (100 → 50 %, 63 HP):** the question is "which slice do I park it on".
  - Layout: Block 6, Strike 4, Strike 4, Block 6, Overflow 4, Null 6 = 30 ✓.
  - Strike and Overflow are 4 ticks, so there is no Perfect window on them: the wheel is a puzzle of angle, not of precision.
  - Block base 8, Strike 4, Overflow 9, all × 2.2 at T4 (R2).
- **P2, Thin Air (50 → 0 %, 63 HP):** the defense is gone, and the question flips to "deny the Perfect".
  - Layout: Overflow 3, Strike 4, Null 6, Overflow 3, Strike 4, Strike 4, Null 6 = 30 ✓.
  - Overflow is a 3-tick slice (G P G); a 1-tick nudge turns the Perfect Overflow into a Good.
  - Enrage: start turn 6 (SHUT), so the first step lands during P2.
- **Transition:** parks damage at 63 and keeps statuses (R6); the layout is revealed on entry.

### 4.2 Elite vault B: "Dish Controller" (T4: 126 HP, threshold 0.5)
Same arithmetic.
- **P1, Aim (63 HP):** Flare 5, Strike 5, Block 5, Flare 5, Strike 5, Null 5 = 30 ✓. A Flare overclocks your slice (burns into CORRUPTED, the Orbital status). The question: which of your own slices do you put under its needle.
- **P2, Orbit (63 HP):** the needle orbits 2 ticks per turn (readable ahead, existing pointer behavior).
  - Layout: Flare 4, Overflow 4, Strike 4, Null 6, Flare 4, Strike 4, Overflow 4 = 30 ✓.
  - The question: plan the next two turns, and spend a nudge to meet the safe window.

### 4.3 Silo Sabotage: the Launch Guard (T4: 112 HP, threshold 0.5)
HP is the lower edge of the elite band because its guards add effective HP.
- **P1, Prep (56 HP + guards):** the budget is 18 × 3.5 = 63.
  - Fixed satellite guards (6 HP each, R12) sit on its Strike and Overflow slices.
  - Guards on the first sabotage: 2 (56 + 12 = 68, a bit over budget on lap 1, deliberately).
  - On the second: 1 (62, on budget). On the third and fourth: 0 (56).
  - Each retarget already fired removes one guard, so progress makes the fight easier.
  - Layout: Strike 5, Overflow 5, Block 5, Strike 5, Null 5, Strike 5 = 30 ✓.
  - The question: steer the Pointer onto an unguarded slice or kill the guard that matters.
- **P2, Countdown (56 HP):** one needle; the enemy has a fuel slice.
  - Layout: Overflow 4, Fuel 6, Strike 5, Null 5, Strike 5, Overflow 5 = 30 ✓.
  - Fuel heals 5 % max HP (about 6, PERCENT) on a Perfect landing only. Expected sustain is about 2 per turn.
  - Budget: (18 − 2) × 3.5 = 56 ✓.
  - The question: deny the Fuel Perfect with a nudge, then burst.
- **Enrage:** elite default (turn 8, every 5, +25 %).

### 4.4 Events (one node; draws one of two)
- **Crossed Wires:** choose a dish: +2 Links (max 4), or the next elite vault uses the Kill zone HP (112).
- **Fuel Leak:** take 8 % max HP damage (PERCENT) and get a 3rd Tribute option on the next retarget.

### 4.5 D5: Exploits as keys, paying off inside this HQ
Each Exploit also unlocks its own special building (D5); here each sets one run rule. All are convenience, so a missing Exploit never locks anything.

| Exploit owned | Effect in this HQ |
|---|---|
| Intel (launch codes) | The fork card also shows the boss's phases and buffs; Tributes are 3 offers instead of 2; L9-L12 are visible from the start |
| Breach (ground station override) | SHUT doors no longer change the enrage start (it stays 8); the override unlocks after 2 retargets instead of 3 |
| Virus (open spectrum) | Link max is 6 (each Link still ±1 tick; see Q:); Fallout corrupts 1 slice instead of 2 |

## 5. Pacing & difficulty curve

**T4 assumptions:** reference damage 18 per turn (R2), 3.5 turns per phase.

| Segment | Content | Turns |
|---|---|---|
| L1-L3 | up to 2 normals (3.5 each), or 1 normal plus a Cache | 3.5-7 |
| L4-L5 | elite A (7) + sabotage 1 (7) | 14 |
| L6-L8 | normal or echo (0-3.5) + elite B (7) + sabotage 2 (7) | 14-17.5 |
| L9-L10 | normal or rest (0-3.5) + sabotage 3 (7) | 7-10.5 |
| Boss (override route) | 12-20, expected about 16 (starts in phase 2, so closer to 12 in practice) | ~13 |
| **Override route total** | **5 elite-class fights + 0-4 normals + the boss** | **~55-65 turns** |
| Long route add-on | ring relay (3.5) + top room (0) + sabotage 4 (7) + the boss at its normal length (+3) | +13.5 |

- **Minutes:** about 0.57 min per turn (the GDD's "5 combats of 2 minutes" at 3.5 turns each), plus event and shop time. The override route is **about 35-42 min**, and the long route adds about 8. That is far above GDD 4.2's 15 min. D10 allows longer HQ runs; whether 14 layers is acceptable against the campaign length target is Q:.
- **Cut the weight if needed:** a Cache or Echo replaces a normal, so a speed-minded player's minimum route is L2 fight, L3 Cache, L4, L5, L6 Echo, L7, L8, L9 Rest, L10, boss. That is about 52 turns (~31 min).
- **HP pressure:** five elite-class fights are the main drain.
  - Heal sources: Echo 10 %, Rest 25 %, Cache items, plus Firmware from the vaults.
  - The Fuel Leak costs 8 %.
  - Budget: about 80 % of the operative's HP lost across the run, about 55-65 % recovered, so the boss entry is at 50-65 % HP (override route; it also carries Fallout).
- **Heat:** elites +1 each (2), sabotages +2 each (Server Rack-grade, 6 on the override route, 8 on the long route). So the HQ run adds about **+8 (override) or +10 (long)**. A Grid state at 90+ before start risks a Purge interlude mid-run.
- **Curve:**
  - Lap 1 teaches (OPEN ring, then the first elite and the 2-guard sabotage).
  - Lap 2 asks the speed question (the turn-6 enrage on the antenna).
  - Lap 3 compresses (no antenna, 0-guard sabotage).
  - The fork is the decision peak.
  - The boss is the final test.

## 6. Rewards

Beyond the boss:
- **Per Retarget:** a Strike Tribute (§3.1), lasting until the netrun ends.
- **Sabotage clears:** Schematics banked immediately, as a Server Rack: **6 / 8 / 10 / 12** for retargets 1-4 (placeholder). This replaces v1's campaign-level strike tally (cut; raid-pass scope and G11).
- **Elite vaults A and B:** one Firmware each (rare pool).
- **Long route extra:** the L12 top-room Cache (1 of 3 Firmware) and the 4th sabotage's 12 Schematics.
- **Final reward:** the boss's rewards per the corp draft. The HQ win is the campaign's corporation win.

## 7. Failure & retry

- **Death** follows GDD 4.2: the operative is lost permanently with everything unbanked; the campaign gains 10 + tier Heat. Schematics banked at Sabotage clears stay.
- **Retry:** a new attempt generates a new seed. Run state (`retargets`, Links, Tributes, doors) starts from zero, and nothing carries over except banked Schematics. A failed run never grants the override.
- **Death after the override:** the same. Fallout and the skipped phase belong to that attempt only.
- **Heat:** the run adds the Heat in §5. If Heat reaches 100 mid-run, the Purge raid fires as an interlude (GDD 4.4), using the Armory, and the HQ run resumes afterward.
- **Abandon:** as GDD 4.5; it counts as a death, banked Schematics stand.

## 8. Systems needed

| System | Used for | Status |
|---|---|---|
| N1 (amount modes) | PERCENT heals (Echo, Rest, Fuel, Fuel Leak) and FLAT corruption for Fallout | Required |
| N2 (tier tables) | T4 HP for elites and the Launch Guard, flat values × 2.2 | Required |
| N3 (phases, parking, status keep) | Elite, sabotage and boss phases; `start_phase` for the override | Required (`start_phase` is a data field in N3 territory) |
| N4 (enrage) | Elite default enrage; the per-fight start-turn override for SHUT doors; the Overdrive step | Required |
| N5 (boss buffs/Exploits) | The boss's buffs and Exploit draw (owned by the corp draft) | Required |
| N12 (variable slice sizes) | 3-, 4-, 6- and 7-tick slices in every elite and Launch Guard layout | Required; fallback: 5-tick slices only (loses the Perfect-window puzzle) |
| N13 (fixed satellites + replacement) | The Launch Guard's guards | Required; fallback: ordinary bodyguards with no replace rule |
| N14 (defense trio) | Block/Shield/Sandbox used implicitly | Required |
| N16 (next-combat overrides) | Salvo, Jam, Kill zone Tributes | Needed; fallback: Tributes limited to a flat item or heal |
| N18 (rewards list) | Tribute rows, Firmware rows | Needed; fallback: a scripted offer |
| N19 (sim metrics) | Turns per phase, enrage step reached, tuning | Needed for balance |
| **NEW: HQ run state** | `retargets`, `links`, `doors` fields on RunState; `hq_rewards`, `hq_fallout` streams registered and checkpointed | S-M; data fields |
| **NEW: node combat modifier** | Two fields: `extra_free_nudges` (OPEN) and `enrage_start_override` (SHUT), keyed by node type | S; data-only fallback: drop the extra nudge and keep the enrage start at 8 |
| **NEW: Dish Link action** | A free ±1 enemy-wheel nudge at the start of the player phase, count-limited, resistance-aware preview | S, reuses nudge code; fallback: a card ("Aim") added to the hand at fight start |
| **NEW: cyclic route graph** | Echo nodes (a cleared node reused), the fork that adds layers | M; data-only fallback: an authored 14-layer graph with the echoes pre-placed |

Not needed: N6, N7, N10, N11, N15, N17, N20.

**Build order:**
1. Foundation: N1, N2, N3, N4, N19.
2. N12, N13, N14.
3. The run state, the node combat modifier and the Dish Link action (all small).
4. The cyclic graph (the authored linear fallback first).
5. Content: the dish and outpost fights, the two elite vaults, the Launch Guard, the 2 events, the Tribute table (N16/N18).
6. N5, then the Launch Control boss; the override Fallout and Overdrive hooks.

## 9. Art hooks

Per frame the art needs from game state:
- `doors`: OPEN or SHUT (a tween value 0-1).
- `rocket_height`: below ground with doors shut, risen 62 BU during a sabotage fight or cutscene.
- `retargets`: 0-4, which hack bands are lime, and the readout name of the struck facility.
- `override_state`: LOCKED / LIVE / FIRED (dashed pencil, red solid, then the explosion cutscene).
- `circuit`: 1-4, so the camera orbits per circuit and per the camera rule.
- `room_state` per slot: option, current, walked, echo (a cleared dish with a dimmed look and a lit rim), vault current / walked.
- `links`: Links available (lit dish rims), plus an `aimed_dish` index for the animation when spent.
- `enrage_step`: current step during a SHUT fight (a warning strobe on the gantry).
- `fork_preview`: both prices as text for the DECISION frame, including the 2 Fallout slice indices.
- `strike_site`: the city point and name for the launch cutscene.

The tools only visualise these. The occlusion rule needs the target volume of the current room plus its options, which the camera rig already supplies.

## 10. Open questions

Q: Should the override start the boss at its phase-2 entry (as drafted), or only trim its buff set? The first is stronger for the player, and the boss draft must accept a `start_phase` field.

Q: Is a 14-layer route (about 43-50 min at the long end) within the D10 allowance for a campaign that already runs 605 min against a 395 target, or should the extra circuit lose its ring relay fight and become 13 layers?

Q: Do Virus's 6 Links trivialize resistance-heavy elites, or should Links be capped at 4 for everyone and Virus give a different benefit?

Q: Should Fallout be FLAT corruption of 2 slices (drafted) or a flat HP loss, given that CORRUPTED doubles RAM and could snowball a phase-2 boss fight?

Q: Should the SHUT-doors enrage change (start turn 6 on antenna elites only) stay a per-node override, or become an authored trigger on each elite?
