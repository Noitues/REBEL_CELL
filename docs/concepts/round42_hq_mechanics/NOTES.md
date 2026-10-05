# Round 42: unique HQ mechanics on the compound view

This round builds on the locked HQ-run view: the overhead **compound** (round 35 `hq_compound.png`). It uses the HQ models from rounds 26–31 and the locked netrun language:
- **option-A rings:** the sticker keeps its full colour and one outline ring carries the state (lime walked, orange selectable, white not yet, dim grey cut off);
- **node-type stickers** on inlay pads, with inlay links;
- the **Central Server**: rack sticker, gold chip and red pencil ring.

New this round: a **red ring means LOCKED**.

The designer's rule applies throughout: **when nodes move, their links DE-POWER, then are REMADE.**
- **De-powering** links turn dark red with sparks for one frame, fade for one more, then are gone.
- **Remade** links draw on from their source with a bright head over two frames.

Earlier rounds are untouched, nothing is committed, and `scratch/` is cleared.

## Files
| Corp | Still | GIF (960×540) | Mechanic shown |
|---|---|---|---|
| Meridian | `hq_meridian_compound.png` | `hq_meridian_mechanic.gif` (2.6 MB) | The crane lowers its node container onto the stopped train (the node moves from the yard to a car). The train leaves, taking that node and its links. The trolley carries the next node out from the yard. Car nodes link to a front tower only while alongside it. |
| Solace | `hq_solace_compound.png` | `hq_solace_mechanic.gif` (2.2 MB) | The helix (strands and walkways) turns 60°. The two lowest walkway nodes undock from pod 0 and redock at pod 1. You stand on pod 0, so your direct route up de-powers, and the podium ring to pod 1 is the way round. |
| Halcyon | `hq_halcyon_compound.png` | `hq_halcyon_mechanic.gif` (2.9 MB) | The eye turns 70°, sweeping its searchlight from the left face to the front corner. Nodes in the beam ring red (LOCKED) and their links de-power. Your route up the corner is cut, and the left face unlocks. |
| Orbital | `hq_orbital_compound.png` | `hq_orbital_mechanic.gif` (2.1 MB) | The silo doors slide apart under the rim, and their two nodes go with them (the bridge route across the silo de-powers). Then the rocket rises, and a node on its nose links straight to LAUNCH CONTROL. |
| REBEL_CELL / DISPATCH | `hq_rebel_cell_compound.png` | `hq_rebel_cell_mechanic.gif` (0.7 MB) | **Proposal: THE REHANG.** DISPATCH re-cables its base each step. The mast (DISPATCH CORE) and the courtyard each jump one relay clockwise. The old cables de-power and the new ones are strung. This fits the fiction: the Cell's own base, re-wired against it. |

Central Server names (from round 35, plus one new): THE MASTER MANIFEST, THE GENOME CORE, THE PANOPTICON, LAUNCH CONTROL and DISPATCH CORE (new).

## Proposed GDD rules (deterministic, step-count based)
A **step** is one move of the operative on the HQ run graph: one node entered. Let `s` be the step count since the run started.
- The mechanic state is a pure function of `s` and the HQ's content data. There is no RNG.
- Links are recomputed after each step. A node whose links all de-power stays where it is.
- **The player is never stranded.** If the current node has no powered out-link after a recompute, the next step is a WAIT: `s` advances and nothing is entered.
- **The Central Server is always reachable** by at least one route in every state. Content validation checks this for every `s` in one period.
- **Preview equals result.** The run map shows the next step's state when hovered (the "NEXT STEP" ghost), so the player can plan.

| HQ | Period | State as a function of `s` | Link rule |
|---|---|---|---|
| Meridian | 6 steps | Crane: carry out (s%6 = 0–1), lower onto the car (2), return (3–4), pick (5). Train: arrives at s%6 = 5, stands 0–2, leaves at 3. | The crane node links to the yard while over the yard, and to the cars while over the stopped train. A car node links to a front tower only while alongside it. When the train leaves, its nodes leave the graph until it returns. |
| Solace | 2 steps per turn | Helix angle = 60° × ⌊s/2⌋. | A walkway node docks to a pod if their angles are within 22°. The walkway chain up to the server is always powered. The podium ring is always powered. |
| Halcyon | 6 steps | Eye angle sweeps left face > front corner > back, 35° a step (cosine back and forth). | A node within ±24° of the eye's facing is LOCKED: it can't be entered and its links are off. The server is never locked. |
| Orbital | 6 steps | Doors shut for s%6 = 0–2 and open for 3–5. The rocket is up while the doors are open. | Doors shut: the bridge links across the silo (the short route). Doors open: the door nodes leave the graph, and the rocket node links rim > rocket > server. |
| REBEL_CELL (DISPATCH) | 6 steps | Rehang index r = s % 6. | The mast links to relays r and r+3. The courtyard links to relays r+1 and r+4. Relay-to-relay links follow the courtyard's pair. |

**Godot:** each HQ gets one `HqMechanic` pure function, `(hq_data, s) -> {node positions, powered links, locked set}`, under `scripts/core/`. The view only animates between two results: de-power the removed links (2 frames), move the parts, then remake the added links (2 frames). Seeded replays match because nothing reads RNG.

## Open questions for DECISIONS.md
1. **Does a WAIT step cost anything** (Heat +1, or a turn of the enemy clock)? Proposal: +1 Heat, so waiting for the train or the doors is a real choice.
2. **Meridian: a node that leaves on the train.** If the player is standing on it, do they ride along (moving to the far side)? Proposal: yes, a free move, which makes the train a tactical tool.
3. **Halcyon: entering a node the beam will reach next step.** Is that allowed? Proposal: yes. A locked node you are already on stays yours, but its out-links are off until the beam passes.
4. **DISPATCH** is the post-betrayal enemy, so the rehang uses the corrupted base. Before the reveal, the same base is home and has no mechanic.

## Build (from `scripts/`)
1. `python citydata.py`
2. `render_all42.ps1` (COMPOUND=1, anim view, every corp)
3. `python compound42.py`

New code:
- `heroes42.py`: the per-frame HQ parts and the node world positions;
- `compound42.py`: the overlay, the rules and the GIFs;
- the `hq_scene.py` compound camera and per-frame anchor JSON.

## Weakest parts
- **Halcyon:** the Central Server sits on the top terrace, under the eye. The eye is partly hidden by its sticker in some frames.
- **Meridian:** the yard is busy at this zoom, and the car nodes are small next to the castle.
- **Solace:** the redock is clear, but in the stills the nodes up the helix crowd its right side.
