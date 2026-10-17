<!-- draft via Message Batches API, claude-sonnet-5-5, batch msgbatch_01HADBSF5pLwaHAq7nbABzZa, custom_id hq__orbital; status ok; tokens in 9431 cache-write 0 cache-read 32007 out 8669; cost $0.056. A DESIGN DRAFT for the designer's review: nothing here is built. -->

# Orbital: HQ netrun draft

## 1. Concept & the named mechanic

**What the art shows:** a launch podium with a silo whose doors open and shut. A rocket rises out of it. Hacked bands on the rocket light lime, one per retarget. Dish stations ring the podium. A truss antenna tower carries two elite vaults. A red gantry holds LAUNCH CONTROL. An override link runs from the antenna's top room to LAUNCH CONTROL.

**Restated as a game mechanic: THE RETARGET CYCLE.** The HQ is not a climb. It is a loop of laps ("circuits") around the dish ring. Each circuit has a fixed shape:

1. Fight at the dish stations (a short, branching ring).
2. Climb the antenna (a mandatory elite vault).
3. Sabotage the rocket (a fight at the silo).
4. Each sabotage lights one hack band and **retargets** the rocket onto one of Orbital's own facilities.

After 3 retargets the **LAUNCH OVERRIDE** unlocks. The player may then fire the rocket early into the shut doors, which destroys the HQ's defenses, and walk to LAUNCH CONTROL for the boss (the Launch Control boss, working name). The shortcut is a price-for-speed trade: a short, dangerous route to the boss with a weakened boss, or a longer, safer one with a stronger rocket.

**Why it cannot be mistaken for another HQ:**
- Solace is a vertical ladder.
- Halcyon has a pyramid with an eye that watches.
- Meridian has a freight line that shuttles.
- Rebel Cell is a mirror.
- Orbital is the only HQ that is **cyclic and revisits the same map**. Cleared stations change state each lap, and the player's own sabotage progress is the clock, not the enemy's.

**Core question of the netrun:** "How many times do I go round, and what do I bring to the boss for it?"

## 2. Structure

**Length:** 4 circuits' worth of structure but only one fully walked plus partial laps (answers Art Q2: laps shorten). Total **12 layers**, in three acts. The map is one graph, and the ring stations carry state across laps.

| Act | Layers | Content | Nodes per layer |
|---|---|---|---|
| Circuit 1 (full lap) | 1-5 | PAD start → dish ring → antenna deck 1 (elite vault A) → silo sabotage (Retarget 1) | 2, 3, 3, 2, 1 |
| Circuit 2 (shortened) | 6-8 | Ring (cleared stations stay cleared, one new) → antenna deck 2 (elite vault B) → Sabotage (Retarget 2) | 2, 2, 1 |
| Circuit 3 (shortest) | 9-10 | Ring (single choice) → Sabotage (Retarget 3); the override LIVE | 2, 1 |
| Decision | 11 | **FORK:** the override (to LAUNCH CONTROL) or one more circuit (NW dish) | 2 |
| Final approach | 12 | LAUNCH CONTROL: the boss fight, the Launch Control boss (working name; designed in the corp/enemy drafts) | 1 |

Detail of the extra circuit chosen at the fork: it adds **3 layers** (a ring node, antenna deck 3 top room, Retarget 4 sabotage) and so the route is 12 layers via the override or up to 15 layers via the extra circuit. Both end at layer-12-equivalent LAUNCH CONTROL.

**Layer map (core path; the 2-3 wide layers branch):**

```
L1  PAD (start)
     |
L2  [SE dish]  [NE dish]                  (both Router fights; choose one)
     |  \      /  |
L3  [SE2] [Mainframe/Cache] [NE2]        (3 nodes; ring causeway edges: each links to its ring neighbours)
      \     |     /
L4   [ANT-1 ELITE vault A] [Event node]  (the antenna elite is the only way up: Event node loops back to L3 stations)
          |
L5   [SILO SABOTAGE: fight, Retarget 1]  (rocket rises, band 1 lime)
          |
L6   [NW dish] [SW dish]                 (cleared stations from lap 1 appear as pre-cleared "echo" nodes)
          |
L7   [ANT-2 ELITE vault B] [Rest]
          |
L8   [SILO SABOTAGE: Retarget 2]
          |
L9   [Ring: single new station or cleared echo]  (2 nodes: a fight, or a Rest)
          |
L10  [SILO SABOTAGE: Retarget 3]         (override LIVE after clear)
          |
L11  FORK: [LAUNCH OVERRIDE]  |  [NW DISH: circuit 4]
          |                              |
L12  [LAUNCH CONTROL: boss]       [ANT top room → Retarget 4 → LAUNCH CONTROL]
```

**Branching and edge rules:**
- Edges follow the game graph (GDD 4.2); the ring layers allow the ring causeway between neighbouring stations (same level), the antenna's outer stairs (rising edge), and the west stair (falling edge back to the ring).
- Per the art rule, slots generate on demand for whatever the route draws, so the counts above are the baseline shape and a seed may add one node to a ring layer (2-4 per layer, GDD).
- **Cleared stations stay cleared:** on later laps a cleared dish appears as an "echo" node. It is a free Rest-like stop (heal 10 % or a nudge-free shop item) and costs no fight. This is the lap-shortening rule.

**Mapping onto landmark slots:**
- PAD, SE, NE, NW, SW are the five dish stations, on the ring (r 96). The ring causeway links neighbours.
- Antenna deck 1 and deck 2 elite vaults are the two enclosed rooms, shared across laps (one per lap).
- The silo rim is the sabotage slot, with the shaft as the visible mover.
- LAUNCH CONTROL is the gantry deck.
- The override is the link from the antenna top room to LAUNCH CONTROL.
- Layers 9-11 reuse ring slots already built, so the landmark needs no extra geometry for the lap compression.

**Boss:** the fight at LAUNCH CONTROL is referenced by working name only: "Launch Control boss". Its phase count and tier come from the corp draft. This HQ only sets its pre-fight conditions (§3, rule 4).

## 3. Unique mechanics

### 3.1 The Retarget Dial (spine)
- **Rule:** the HQ run carries a counter `retargets` (0-4). Each sabotage clear (silo fight) increments it and lights one hack band lime on the rocket.
- **Trigger:** per sabotage clear. Each retarget grants a **Strike Tribute**, a one-time run-wide effect chosen from 2 offered (RNG stream `hq_rewards`, drawn at the checkpoint on entering the silo):
  - **Salvo:** your next normal fight begins with the enemy at −15 % HP (a percent amount, mode PERCENT).
  - **Jam:** all enemies' first turn is frozen (skip the first resolve).
  - **Kill zone:** one elite vault's HP uses the tier band's lower edge.
  - **Supply drop:** +1 shop item on the next Mainframe or Cache.
- **What the player sees:** the lime hack bands on the rocket, the dial chip "RETARGET n/3", and the readout naming the Orbital facility struck (a fixed list in `content/`).
- **Counter:** none; it is the player's clock. The cost is in §3.3.
- **Determinism:** the count and the offered pair are seeded (`hq_rewards`) and set before the sabotage fight, so undo and reload cannot reroll them. The preview of the Tribute is shown before choosing.

### 3.2 Bay Doors (door state as a rule)
- **Rule:** the silo doors are OPEN or SHUT. They open at the start of each circuit's ring phase and shut at its sabotage. State sets a global combat rule in the HQ:
  - **Doors OPEN (ring fights, layers on the ring):** the enemy wheels get **no extra pointer** (pointers fixed) but **Solar Flares** are unavailable. The player may use **Venting**: once per fight, a card with a `vent` tag hits the next enemy twice (uses the existing `hits` rider, N20).
  - **Doors SHUT (sabotage and antenna fights):** a **Pressure** rule: at the end of each turn the enemy gains +10 % damage (this stacks, additive, like enrage and shown on the enrage chip). It resets when the fight ends, so every fight at shut doors has a built-in tempo.
- **Trigger:** by node: ring and echo = OPEN, antenna elites and silo sabotage = SHUT. Doors change at the **layer boundary** and the art animates them.
- **What the player sees:** the doors, the OPEN/SHUT chip on the dial, and the Pressure percent on the enemy panel.
- **Counter:** killing quickly. The Pressure makes the antenna elites a burst puzzle (their phase 2 burst window must land before Pressure grows). A Breach-type Exploit can cancel Pressure (§4).
- **Determinism:** pure function of the node type; no RNG. The preview shows the Pressure value next turn.

### 3.3 The Cost of the Shortcut (Override)
- **Rule:** the LAUNCH OVERRIDE (layer 11 fork) fires the rocket into the shut doors. Effect on the boss fight, set by the number of retargets at that moment:
  - The HQ's defenses blow: the Launch Control boss starts with **its first phase skipped** (HP set to the threshold of phase 2, so effectively −(P1 budget) HP) and **no boss buffs it has drawn on dishes you cleared** (each cleared ring station disables one buff, per D5 Exploit pairing; see §4).
  - The price: **Fallout**. You enter the fight with **all your slices' statuses CORRUPTED on 2 random non-NULL slices** (RNG stream `hq_fallout`, drawn on entering the boss node at its checkpoint). Corrupted slices cost 2× RAM (R9).
- **The longer path (circuit 4):** no Fallout, no skipped phase, but the boss gets **Retarget 4 Overdrive**: it begins with an enrage step already applied (×1.25 damage at turn 1, additive per R4).
- **What the player sees:** the override link in red pencil (dashed + LOCKED before 3/3), a preview card at the fork showing both prices as exact numbers, the explosion cutscene on the override.
- **Counter:** Cleanse (before the fight) is useless for Fallout because it applies at fight start; Encrypt cards pre-applied on slices can absorb it (ENCRYPTED absorbs the next status applied). The preview shows which slices Fallout would hit only after the draw, so it is unavoidable but mitigated.
- **Determinism:** `hq_fallout` is a named RNG stream drawn once at the boss node's entry checkpoint; the preview shows the result after the draw. The skipped-phase and Overdrive effects are deterministic.

### 3.4 Dish Link (cleared stations as ammunition)
- **Rule:** each cleared dish station adds a **Link** (max 4). At the start of any later fight, the player may spend Links (0-2) to **aim** one dish: the enemy's wheel is nudged ±2 ticks (a free, resisted nudge: the enemy's resistance applies). This is an exposed, previewed free nudge.
- **Trigger:** once per fight at the start of the player phase; spending removes the Link until the next circuit's echo stop restores it.
- **What the player sees:** the dishes' ice rims lit for each available Link, the rim animating when aimed.
- **Counter:** enemies with Weight (resistance) absorb it; the Compliance Lock buff on the boss blocks it.
- **Determinism:** pure arithmetic from the preview; the action sits in the undo stack.

## 4. Node kit

| Node | Twist here | Type |
|---|---|---|
| **Dish fight** (Router) | Doors OPEN rule; Venting; a Link is earned on win | Fight (normal, T4 band) |
| **Echo station** (cleared dish) | No fight. Restores up to 2 Links and heals 10 % max HP (a PERCENT heal). One use per echo | Rest |
| **Antenna elite vault** (A, B) | Doors SHUT; Pressure; 2 phases. Phase 1 asks "can you find the safe slice with the pointer", phase 2 flips it (uneven needles, R10). Reward: a Firmware | Elite (a puzzle fight) |
| **Silo Sabotage** | The retarget fight. A puzzle-hybrid: the rocket's hacked band count sets enemy phases (see below). Doors SHUT | Mini-boss-scale fight |
| **Cache** (Mainframe variant) | Shop with a "retarget discount": prices −10 % per retarget | Shop |
| **Event** (Terminal) | The two HQ events (below) | Event |
| **Rest** | One node per lap on layers 7 and 9 | Rest |

**Silo Sabotage design (direct):** the enemy is the rocket's guard (working name "Launch Guard"). It has 2 phases (mini-boss class budget at T4 via the band analog). Phase 1: **Prep** with 2 satellite guards fixed on its slices (R12) so the player must choose which slice to push to. Phase 2: **Countdown**, 2 needles (0 / 11), a damage slice and a "fuel" slice that heals the guard if it lands Perfect. The hacked band count adds: each earlier retarget removes one guard in phase 1 (3 = none). It rewards progress, and it is a simple data hookup.

**Events (2, unique to this HQ):**
- **Crossed Wires:** choose a dish: +2 Links, or the next elite loses Pressure.
- **Fuel Leak:** the rocket leaks. Take 8 % max HP damage (PERCENT) and gain one extra Tribute option on the next retarget.

**D5, Exploits as keys, paying off inside this HQ** (each Exploit also unlocks its own special building; here it sets one rule of the run):

| Exploit owned | Effect in this HQ |
|---|---|
| Intel (launch codes) | The fork preview shows the boss's phases and buffs; Tribute choices become 3 offers instead of 2; the HQ map shows all of layers 9-12 from the start |
| Breach (ground station override) | Pressure caps at +20 % and the boss's skipped phase on override also skips its 2nd needle; the override unlocks after 2 retargets instead of 3 |
| Virus (open spectrum) | Dish Links go to max 6 and aim ±3 ticks; Fallout hits one slice instead of two |

Exploits are a permanent campaign pickup (Grid), so an HQ with all 3 is much easier. That reflects the campaign gating, and the Virus and Intel effects are only convenience, so a missing one never locks anything.

## 5. Pacing & difficulty curve

**T4 assumptions:** the reference damage per turn is 18 at T4 (R2). Phase length is 3.5 turns.

| Segment | Fights | Turns | Minutes |
|---|---|---|---|
| Circuit 1 (L1-5) | 2 dish + 1 elite + sabotage | 3.5 + 3.5 + 7 + 8 = 22 | ~9 |
| Circuit 2 (L6-8) | 1 dish or echo + 1 elite + sabotage | ~3.5 + 7 + 8 = 18.5 | ~7 |
| Circuit 3 (L9-10) | 1 fight or echo + sabotage | ~3.5 + 8 = 11.5 | ~5 |
| Fork + boss | the boss, 12-20 turns | ~16 | ~7 |
| **Total (override route)** | **7 fights (+1 echo/rest)** | **~68 turns** | **~28 min** |
| Extra circuit (if chosen) | +1 fight + sabotage (+ the top room) | +12 | +6 |

- **Minutes** are above GDD 4.2's 15, but D10 says HQ runs may run longer. Fights are the ~3.5-turn 2-minute unit, and a longer run is the designer's ruling.
- **HP pressure:** the chain has 3 elite-grade fights (2 antenna + 1 sabotage per lap beyond the first). The player has **10 % heal per echo stop** (up to 3 stops), 2 Rest nodes (full 25 % PERCENT heal each), and the Fuel Leak event as a cost. Budget: about 70 % of the operative's HP lost over the run, recovered about 65 %, leaving the boss entry near 60-70 % HP. That is a playable gap, not a certainty.
- **Heat:** each elite adds +1 and each sabotage +2 (as Server Rack-grade). The expected Heat for the HQ run is +10, so the preceding Grid must land the player at under 90 before start (Purge at 100). If Heat hits 100 mid-run, the Purge raid fires as an interlude (§7).
- **Difficulty curve:** lap 1 teaches (OPEN, easy ring); lap 2 introduces Pressure at the antenna; lap 3 compresses (one fight + sabotage); the fork is the decision peak; the boss is the final test.

## 6. Rewards

Beyond the boss:
- **Per Retarget:** a Strike Tribute (§3.1), run-wide until the netrun ends.
- **Elite vaults A and B:** one Firmware each (rare pool; band by rarity).
- **Sabotage clears:** Schematics banked immediately, as a Server Rack (e.g. 6 / 8 / 10 per sabotage, placeholder).
- **Completion bonus (campaign):** the **Orbital strike tally**. Each retarget actually fired remains as a city-level effect for the rest of the campaign: a defeated Orbital facility named on the readout becomes a *DOWN* source for corporation raids (no raid enters from it). One retarget = one corporate Site is neutralised as a raid entry point. This makes the shortcut-versus-circuit choice matter outside the HQ. The extra circuit yields 4 sites, and the override yields 3. It stays within existing state because raids already come from corporate Sites and G11 says DOWN is a source for no one.
- **Final reward:** the boss's rewards per the corp draft. The HQ win is the campaign's corporation win.

## 7. Failure & retry

- **Death** follows GDD 4.2: the operative is lost permanently with everything unbanked; campaign +10 + tier Heat.
- **Retry:** the HQ netrun regenerates with a new seed, but **progress that was banked stays**: retargets already fired at *sabotage clear* remain as city-level DOWN sources (above). On the next attempt the dial starts at 0 but the previously struck facilities are listed and removed from the strike list, so each failed run still takes some pressure off. Dish Links and Tributes do not carry over.
- **Override failure:** if the operative dies at the boss after the override, the HQ's defenses stay destroyed for the retry: the next attempt skips the ring layers L2-L4 (start at the antenna) but the rocket is spent, so the override is gone. The route is the long circuit.
- **Heat:** an HQ run adds the Heat in §5. A Purge firing mid-run triggers an interlude raid (GDD 4.4) that uses the Armory; the HQ run resumes after.
- **Abandon:** as GDD 4.5. Abandoning counts as a death, but banked retargets still stand.

## 8. Systems needed

| System | Used for | Status |
|---|---|---|
| N3 (phases, parking, status keep) | Elite, sabotage and boss phases | Required |
| N4 (enrage) | Pressure shares the enrage chip; the Overdrive step | Required (Pressure is data-only on top as an additive damage step from the doors state) |
| N5 (boss buffs/Exploits) | The boss's buffs disabled by cleared dishes | Required |
| N1 (amount modes) | PERCENT heals, the Salvo and Fuel Leak | Required |
| N2 (tier tables) | T4 HP bands | Required |
| N6 (listeners) | None strictly; Venting uses a card | Not needed |
| N11 (pointers on any tick) | Uneven needles (0 / 11) | Required; no fallback beyond 15/10 spacing |
| N13 (fixed satellites + replacement) | Guards at the sabotage | Required; fallback: ordinary bodyguards with no replace rule |
| N14 (defense trio) | Used implicitly | Required for the fights |
| N16 (events altering future fights) | The Fuel Leak and Crossed Wires | Needed; fallback: data-only events that grant items or HP |
| N18 (rewards list) | The Strike Tribute table, Firmware rows | Needed; fallback: a scripted offer |
| N19 (sim metrics) | Turns per phase, tuning | Needed for balance |
| **NEW: HQ run state** | `retargets`, `doors`, `links`, the strike tally persisted to the campaign | Data fields on RunState; M |
| **NEW: Doors rule modifier** | A fight-start modifier (Pressure ramp, Venting tag) keyed by node type | Reuses enrage data (additive step per turn); S |
| **NEW: Dish Link action** | A free resisted enemy-wheel nudge at fight start, with a count | S; reuses nudge code; fallback: a card |
| **NEW: Cyclic route graph** | Layers with "echo" nodes (cleared node reused), cleared state carried across laps, a fork that adds layers | M; a data-only fallback is to author a 15-layer linear graph with the echoes pre-placed |
| **NEW: Campaign strike tally** | A per-corp record of retargets that sets Orbital Sites DOWN-sources | M; fallback: a flat Schematics reward |

**Build order:**
1. Foundation (N1, N2, N3, N4, N19) as in the plan.
2. N11, N13, N14.
3. The run state, the Doors modifier and the Dish Link action (small).
4. The cyclic graph (with the pre-placed linear fallback first).
5. Content: the dish fights, the elite vaults, the Launch Guard, the 2 events, the Tribute table (N18).
6. N5, then the Launch Control boss; the override Fallout and Overdrive hooks.
7. The strike tally (campaign layer) last.

## 9. Art hooks

Per frame the art needs from game state:
- `doors`: OPEN or SHUT (a tween value 0-1, so they animate).
- `rocket_height`: below ground with the doors shut, risen 62 BU during a sabotage fight or cutscene.
- `retargets`: 0-4, which hack bands are lime, and the readout name of the struck facility.
- `override_state`: LOCKED / LIVE / FIRED (dashed pencil → red solid → explosion cutscene).
- `circuit`: 1-4, so the camera orbits the complex per circuit and per the camera rule.
- `room_state` per slot: option, current, walked, echo (a cleared dish, a distinct dimmed look with a lit rim), and the elite vault current / walked.
- `links`: the number of Links available (lit dish rims), and an `aimed_dish` index for the animation when spent.
- `pressure`: current Pressure percent during a SHUT fight (a warning strobe rate on the gantry).
- `fork_preview`: the two prices as text for the DECISION frame.
- `strike_site`: the city point and name for the launch cutscene.

The tools only visualise these. The occlusion rule needs the target volume of the current room plus options, which is already given by the camera rig.

## 10. Open questions

Q: Is the extra circuit (the 15-layer route) worth keeping alongside the override, or does it make the HQ too long for a campaign that already runs 605 min against a 395 target?

Q: Should the override cost Fallout (corruption at fight start) or a stronger, simpler cost such as a flat HP loss, given that CORRUPTED is a 2× RAM tax and could snowball the boss fight?

Q: Is the campaign-level strike tally (each retarget turns an Orbital Site into a raid-free source) in scope for the raid pass, or too large an effect for an HQ reward?

Q: Does the Pressure ramp (+10 % per turn at shut doors) duplicate the R4 enrage too closely, or should the antenna elites author their own trigger instead?

Q: Should cleared dish stations disable boss buffs one-for-one (D5-linked), or is that too much overlap with the Exploit draw (R7)?

Q: Do Dish Links need a cap at the netrun level so they cannot trivialise resistance-heavy elites?
