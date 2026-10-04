# Round 40: hub cores v3, enemy lockdown, player defeat v2, inner ring v3, status stacks

This round applies the designer's round 39 review. Earlier rounds are not edited.

**Locked:**
- the Rigger, Overclocker, Ghost, Swarm and Hive cores;
- all enemy hubs;
- the inner-ring textures and their extension into the slices.

## Files
| File | What it shows |
|---|---|
| `hub_cores_v3.png` | Breaker (round 39 → 40, plus Mk2, glyph at 64/24/16 px, grey); Phantom frames; the LOCKDOWN stages including Short Circuit (2 turns); the player DEFEAT v2 strip. |
| `lockdown.gif` | The encrypted-bit waterline draining from full to empty: 32 frames. |
| `player_defeat_v2.gif` | The core dissolving: 32 frames. |
| `phantom_echo_v2.gif` | The Phantom echo with the ring held still. |
| `inner_ring_v3.png` | The sub-needle and the hangar with two drones, each at r = 300 and r = 60, plus grey. |
| `status_stacks.png` | Three stack-count styles on every status badge (×1, ×2, ×3, ×5, plus 24 and 16 px), and style B on the slice overlays and at r = 90. |
| `scripts/` | `glyphs40.py` (Breaker), `hub40.py` (lockdown, sub-needle, hangar pods, stack badge) and `make40.py`. Edited copies, all in this folder: `hub39.py` (defeat), `hubkit.py` / `ring2.py` (cache fix) and `overlays.py` (stack hook). |

## Changes
1. **Breaker.**
   - The pane is gone. A crowbar's claw strikes a point, and a spiderweb of glass cracks spreads from it: 9 radial spokes and 3 broken, jagged concentric rings.
   - About 30 % of the ring links are missing, so it reads as glass rather than a web.
   - 16 px twin: 0.45, against FINGERPRINT.
2. **Phantom: inner-ring pulsing removed.** The cause was a bug, not a design choice. Ring glyphs were taken from the shared glyph cache and faded in place, so they dimmed a bit more on every frame. The fix is `.copy()` in `hubkit.draw_ring` and `ring2.ring_glyphs`. Now only the echo trail moves.
3. **Enemy LOCKDOWN (Hub Breach).**
   - No cracks. A **waterline of encrypted bits** (cyan hex and symbol characters, slowly churning, with a bright wavy surface) fills the hub when Hub Breach lands and drains down in step with the lockdown timer.
   - The hub underneath is dimmed. A **LOCKDOWN** plate with a padlock shows, and the turns left sit at the top right.
   - Short Circuit starts at 2 and drains over two turns.
   - The passive is off while any water remains. When the water is empty, the hub is back online.
   - **Godot:** a shader on the hub disc with `level` (= remaining turns ÷ total, tweened over the enemy turn) and a scrolling glyph-atlas texture masked below `level`.
4. **Player DEFEAT v2.**
   - The bits fall and simply vanish when they reach the bottom of the core circle; the per-column floor is the circle's edge.
   - The drain line is removed. The bits keep full alpha until they vanish.
   - FLATLINED stamps in at the end, as before.
5. **Sub-needle** (proposal, not in game). The same cream blade with ink outline as the main D4 pointer, at about 60 % size. It is rooted on the ring's outer lip, points outward and turns with the inner ring. The slice it points at also triggers.
6. **Hangar with two drones** (proposal, not in game).
   - Two drone pods dock side by side on the slice's outer rim: clamps on the bezel, each pod with its own 3-pip HP.
   - It reads fine: the pods sit above the value block and outside the screen.
   - Three pods would crowd a 60° slice. Beyond two, show "+n" on the second pod.
   - **Open question for the designer:** how is damage dealt with several drones on one slice? Options:
     - each drone hits for its own value;
     - the drones split the slice's value;
     - the slice fires once per drone.
7. **Status stacks** (stacking is planned, not in game). A count of 1 shows nothing extra.

   | Style | What it is | Verdict |
   |---|---|---|
   | A, pips | one dot per stack under the badge | ambiguous beyond 3 |
   | **B, ×N tab (recommended)** | an ink tab with "×N" on the badge's top-right corner | scales to any count and reads at 16 px |
   | C, stacked + tab | ghost copies of the badge behind, plus the tab | — |

   On the slice overlays, the tab rides the corner badge at a larger ratio (0.66 of the badge), so the value block is untouched. On small wheels (r ≤ 90) the tab is too small, so the count should also appear in the forecast chip.

   **Godot:** a `Label` in a `PanelContainer`, child of the badge `TextureRect`, visible when stacks > 1.

## Weakest part
- **At full level, the lockdown bits read a little like a text wall.** A sparser, blockier glyph set might be calmer.
- **The Breaker cracks get busy at 16 px.**
