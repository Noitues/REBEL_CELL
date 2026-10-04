# Round 38: satellites (docked mini-wheels)

The GDD gives satellites their own mini-wheels: §2.1, §2.7, the Botnet rules and Appendix A.3. Until now the concepts only drew them as tokens. This round draws them in the locked language: the D4 frame, C screen slices, upright glyph and value, and the corp themes from rounds 14–18.

## Files
| File | What it shows |
|---|---|
| `satellites.png` | The player (Botnet) and enemy (Care Swarm) wheels at r = 220, each with docked satellites. An enlarged anatomy of one satellite. Both wheels at r = 60. Five states: docked, nudged on its own, carried by a spin, bodyguard, destroyed. |
| `satellite_motion.gif` | 20 frames, about 3.4 MB. NOW → hovering HEAVY SPIN 9 (the locked preview: chevrons, then dashed ghosts) → SEND IT, the spin carries every satellite → one satellite nudged (only its mini-wheel turns) → bodyguard hit → destroyed. |
| `scripts/` | `sat.py` draws the satellite and the composite; `make_sat.py sheet` and `make_sat.py gif` build the outputs. |

## Content shown
All values come from `content/enemies/*_drone.tres`, read-only.
- **Most drones:** a 2-slice wheel (ATK 3 / DEF 3, 15 ticks each) with 5 HP. These are the Botnet, Courier, Civic, Orbital, Collections and Echo drones. The Seed drone has 1 HP.
- **Care Drone (Solace):** a 3-slice wheel (ATK 3 / ATK 3 / DEF 2, 10 ticks each) with 4 HP. Care Swarm carries 3 of them.
- **Botnet** docks its drones on its two DEPLOY slices (TROJAN 1).

## Design
- **The mini-wheel** is the D4 frame scaled to 0.30 of the host:
  - C slices in the owner's skin: the player's own programs, or the corp's full-screen animations;
  - a narrow machined bezel with 30 ticks, the major ticks marking slice borders;
  - the active slice lit with a cream outline, the others dimmed (the D4 rule);
  - its **own D4 blade pointer**, with the active slice's value in the window;
  - **HP in the hub**, as a big number plus one pip per HP. Lost pips turn red.
- **Oriented radially.** The satellite's pointer always faces *away* from the host, so it never points into the host's slices. Values stay upright.
- **Docking.** The satellite sits on its slice, 22° clockwise of the slice centre, so it is never under the host blade or value. It sits out past the HP arc, joined by twin struts to a **clamp plate on the host rim**. The plate marks which slice it is docked on.
- **Carried by a spin or flip.** It rides its slice: a spin of N moves it +12N°. The card-play preview uses the locked behaviour: chevrons for the top needle only, and a dashed ghost satellite where each one *ends up*.
- **Nudged on its own.** Each satellite has its own small `<` `>` buttons, and nudge cards can be aimed at it. Only the mini-wheel turns; the host does not.
- **Bodyguard.** A pointer attack aimed at a slice with a satellite hits the satellite: a cyan guard arc on the host-facing side, an impact star, and HP pips turning red. Pierce does not bypass it (ruling 2026-09-24).
- **Destroyed.** At 0 HP the satellite is greyed out and cracked. It then undocks and falls away, and the slice is unguarded again.
- **At r = 60** the satellites are about 18 px across and use the LOD slices. They read as a coloured blob, a blade and an HP number. Their intent is better shown on the forecast tag.

## Godot
- A `Satellite` scene (`Node2D`) is a child of a `DockPoint`, which is itself a child of the host's rotating `Slices` node. The satellite therefore rides spins and flips automatically. Its `rotation` is set to face outward.
- It reuses the wheel's slice shader, the D4 blade scene and the `CorpTheme` material. `SAT_K` (0.30) and `DOCK_OFF` (22°) are layout constants and should live in the UI config, not in code.
- The preview overlay adds one dashed ghost per satellite at `dock_angle + 12 × N`, using the same forecast data as the needle ghosts.

## Weakest parts / open
- **The state tiles crop part of the host,** so the satellite is not always centred.
- **At r = 60 the satellite's values are near-illegible.** A satellite's intent should also appear as a chip on the host's forecast tag.
- **Docking 22° off the slice centre is my rule,** made for legibility. The designer should confirm it.
