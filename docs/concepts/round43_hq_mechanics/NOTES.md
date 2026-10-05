# Round 43: HQ mechanics after the designer's review

Everything is on the locked compound view and the round 42 netrun overlay:
- option-A rings: lime walked, orange selectable, white not yet, dim grey cut off, red danger;
- node-type stickers;
- the Central Server: gold chip and red pencil.

Links that change **de-power** (2 frames, sparks) and are **re-made** (drawn on over 2 frames). Earlier rounds are untouched, nothing is committed, and `scratch/` is cleared.

## Files
| Corp | Still | GIF |
|---|---|---|
| Meridian | `hq_meridian_compound.png` | `hq_meridian_mechanic.gif` (2.5 MB) |
| Solace | `hq_solace_compound.png` | `hq_solace_mechanic.gif` (2.9 MB, 800×450) |
| Halcyon | `hq_halcyon_compound.png` | `hq_halcyon_mechanic.gif` (2.6 MB) |
| Orbital | `hq_orbital_compound.png` | `hq_orbital_mechanic.gif` (2.9 MB) |
| DISPATCH | `dispatch_idea_1_sync_strike.png`, `dispatch_idea_2_mirror_run.png`, `dispatch_idea_3_the_playbook.png`, `dispatch_idea_4_memory_lane.png` | `dispatch_sync_strike.gif` (0.9 MB) |

**Build** (from `scripts/`):
1. `python citydata.py`
2. `render_all43.ps1` (COMPOUND=1 anim view; meridian 24 frames, solace 15, halcyon 16, orbital 3)
3. `python compound43.py`

DISPATCH (`dispatch43.py`) reuses `round34_rebel_cell/canyon_dispatch.jpg`, read-only.

## MERIDIAN: crane + train
**Rules.** A step is one move of the operative. Steps run in a fixed 6-step cycle:

| Step | What moves |
|---|---|
| 0 | The crane carries container A out over the track while the train arrives. |
| 1 | The crane lowers A onto the empty car. |
| 2 | The train **stays for this whole turn**. |
| 3 | The train shunts one car, and the crane lifts container B **off** the train. |
| 4 | The crane carries B **into the fortress** and sets it down in the yard. |
| 5 | The train leaves with A. |

Link rules:
- **Every crane or train move re-makes the links it touches.** They de-power and are recreated next frame, even when they reconnect to the same place.
- **The next container to move is telegraphed** one step ahead: a yellow pencil ring with "NEXT: ONTO THE TRAIN / OFF THE TRAIN / INTO THE FORT / LEAVES".
- **Train cars beside a north-wall node link both ways**, so a player who steps onto a car can step back while it stands.
- **When B lands in the yard it adds a new link inside the fortress** (wN1 > B > wS2): a shortcut across the yard to the server side.
- **The paths run along the walls.** The routes are gate > corner tower > wall-top nodes > the server tower (THE MASTER MANIFEST, back corner). The crane and train links are side branches off the north wall.

The GIF plays one cycle:
1. The player walks gate > tower.
2. The player steps onto car B while the train stands.
3. Warned by the NEXT telegraph, the player steps back before B is lifted.
4. The player then uses B's new yard link.

## SOLACE: climb the helix (no spinning)
**Rules.** Solace's mechanic is a choice, not a clock.
- **The start forks** onto one of the two strands:
  - **strand A:** elites and better loot;
  - **strand B:** terminals and shops.
- **Each strand is a chain** up to the cap, where the Central Server (THE GENOME CORE) sits.
- **Walkway rungs are CROSSOVERS** (3 of them, at about ⅓, ½ and ⅘ of the height). A crossover node sits mid-walkway and links both strands below to both strands above, so it is the only place to switch.
- **The goal is the top.**

**Camera.** It orbits and climbs so the player's node stays centre screen. Its azimuth follows the node around the helix. The GIF path is start > A0 > A1 > crossover > B2 > B3 > crossover > A4.

## HALCYON: the long way, shortcuts, and the eye
**The long way.** The front face holds switchback rows of 6, 5, 4, 3, 2 and 1 nodes: 21 nodes, numbered in path order (row 1 left to right, row 2 right to left, and so on). The top server room (THE PANOPTICON) comes after them.

**Shortcuts.** The links are 4>9, 9>13, 13>17 and 17>20.
- They are shown in gold, and **the runner may use at most 2**.
- Their only benefit is fewer nodes: less loot and less damage taken.

**The eye (integrated).** Each step the eye watches **one half** of the face (LEFT, then RIGHT, then LEFT, ...) **plus the centre column, always**.
- Entering a watched node = **SPOTTED**: an alarm encounter (proposal: +1 enforcement enemy in the next fight, or +1 Heat).
- The shortcuts are placed so the choice is real:
  - **4>9 and 13>17 land in the centre column, which is always watched.** These are the "endure the eye" shortcuts: fast, but you will be spotted.
  - **9>13 (left half) and 17>20 (right half) can be timed.** Take them on a step when the eye looks the other way and they are free.
- The long way also crosses the halves, so a careful runner can weave back and forth to avoid the eye, at the cost of more nodes.
- The GIF shows: walk 1–4, take 4>9 (SPOTTED), wait for the eye to swing right, take 9>13 safely (shortcuts used: 2/2), then walk on.

## ORBITAL: the launch loop
**Rules.**
- **The loop is a fixed circle:** platform > NE dish > E dish > antenna tower > W dish > SW dish > platform.
- **Each lap the player must clear every node in it.** Cleared state resets each lap.
- **While the player laps, the next missile is prepped.** The MISSILE BAY prep bar fills one sixth per node cleared.
- **At the end of each lap the doors open and the missile stands ready.** The player sabotages it from the platform (red X, tally +1).
- **After 3 sabotages, lap 4's path bypasses the platform** (SW dish > NE dish). The SW dish links straight to the 4th missile while the doors are still shut.
- **Sabotaging it launches the missile inside the closed bay:** the base is destroyed and the run is won. The Central Server here *is* the bay.

The GIF shows lap 1 node by node, sabotage 1, laps 2 and 3 condensed, then lap 4 (the bypass), the launch and the blast.

## DISPATCH (REBEL_CELL): four final-run ideas
All four play in the Tokyo-alley DISPATCH base (round 34 canyon). DISPATCH knows every trick the Cell used, and has all its slices and firmware.

1. **SYNC STRIKE (recommended; `dispatch_sync_strike.gif`).**
   - Three operatives netrun at once: left rooftops, the alley, right rooftops. The player moves each one every step.
   - The core's three locks must be hit **on the same step**; a lone hit re-arms.
   - DISPATCH counters any firmware it has seen, so a lane can stall. Keeping the runners in step is the puzzle.
   - When the core opens, **one** runner goes in to fight DISPATCH while the others hold their locks.
   - It turns the whole roster you built into the final exam.
2. **MIRROR RUN.**
   - DISPATCH runs a copy of *you* (your wheel, deck and firmware) one step behind.
   - Every node you leave it **retakes**. If it lands on you, you fight your own build.
   - Outpace it, or turn and fight it where you choose.
3. **THE PLAYBOOK.**
   - DISPATCH learns: every card you play is **PATCHED** (stamped, unplayable) for the rest of the run.
   - Nodes ahead show what they counter ("COUNTERS: HEAVY SPIN").
   - Bait it with cards you can afford to lose, and save your best for the core.
4. **MEMORY LANE.**
   - The alley is rebuilt from the Cell's own Sites that you cleared this campaign: THE OLD SAFEHOUSE, FIRST RACK, RELAY ROOFTOP, MEMORIAL WALL and so on.
   - Each is held by its old enemy, now running your firmware.
   - Deleting a memory opens a shortcut through it, but costs that Site's reward for good.

## Open questions for DECISIONS.md
1. **Halcyon: what does SPOTTED cost?** Proposal: +1 enforcement enemy in the next fight (it stacks).
2. **Meridian: what happens to a player who stays on a car when the train leaves?** Proposal: they ride out and are ejected at the gate (back to the start, with Heat +1).
3. **Orbital: what does sabotage take?** Proposal: one fight at the platform. And can a lap be skipped? Proposal: no; every node must be cleared, which is the design.
4. **Sync Strike: one deck, or one per operative?** Proposal: one per operative, from the stationed crew, which ties the raid crew system to the finale.

## Weakest parts
- **Halcyon:** the bottom row runs under the HUD at this zoom (nodes 5 and 6).
- **Solace:** the GIF had to drop to 800×450 to stay under 3 MB (the camera moves every frame).
- **DISPATCH:** the ideas are diagram overlays on the round 34 still. Their own renders would follow once one is picked.
