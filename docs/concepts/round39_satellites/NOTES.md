# Round 39: satellites v2 and the parasite ring

This round builds on round 38 (`round38_satellites`, which is untouched). It keeps the locked D4 frame, the C slices and the card-play preview.

## Files
| File | What it shows |
|---|---|
| `satellites_v2.png` | Botnet and Care Swarm at r = 220 and r = 60, an enlarged anatomy of one satellite, and 5 states: docked, carried by a spin, bodyguard, overwrite, destroyed. |
| `satellite_motion_v2.gif` | 28 frames, about 3.8 MB: NOW → spin preview → spin → bodyguard → destroyed → overwrite. |
| `parasite_ring.png` | A boss wheel (Renewal Engine) at r = 220 and r = 60, an anatomy close-up, and the proposed rules. |
| `parasite_ring.gif` | 15 frames, about 3 MB: latch → grow → applies ×0.5 → turns count down → detach. |
| `scripts/` | `sat2.py` holds the satellite, cradle, effects and parasite. `make_sat2.py sheet` / `gif` / `psheet` / `pgif` build the outputs. |

## Changes (the review numbering)
1. **Centred.** Each satellite sits on the centre line of the slice it is docked to: dock angle = slice mid.
   - It sits further out than in round 38, past the host blade and the HP arc, so it never covers the host pointer.
2. **Overwrite** (the designer's rule). When a new satellite docks on an occupied slice, the old one is knocked off, greys out and bit-bursts. The new one then takes the cradle. This is shown on the sheet and in the GIF.
3. **Rounded cradle** replaces the bars. It has three parts:
   - an arc band hugging the host rim over the docked slice, with round ends and rivets;
   - a waisted neck;
   - a collar ring round the satellite.

   The cradle is drawn under the host, so the host frame and blade stay on top.
4. **Centre bug, fixed.**
   - Round 38 cropped each frame to its own bounding box. That bounding box changed as satellites moved, so the wheel appeared to wander.
   - Every composite is now a fixed canvas with the host's exact centre at the same pixel.
   - Satellite positions are computed from that single centre (`Comp.C`), and the host image is placed by its centre, never by its box.
   - **Verified:** the GIF frames share one centre, and the host stays still while the satellites orbit it.
5. **Destroyed** uses the binary-bit explosion from rounds 21 and 23: a flash, a shock ring, then 0/1 bits blasting out and falling. The satellite greys out under it.
6. **Bigger read.** On each satellite slice, the glyph and value are drawn about 2.5× larger than round 38's. They are spread along the slice: glyph before the slice centre, value after it. Both stay upright on soft read plates.
7. **Nudge.** Satellites cannot be nudged by default, and that state has been removed. Drone classes may get "nudge a drone" as a class ability; this is a note only.

## Parasite ring (boss mechanic, concept)
- It latches onto **one** host slice. It forms a temporary, partial **third ring** over that slice's arc, outside the host frame. It has **3 small slices of negative effects** (an anti-inner-ring):

  | Effect | Meaning |
  |---|---|
  | ×0.5 | output halved (the PARASITE status glyph) |
  | −2 | drains 2 RAM (the RAM glyph) |
  | CRPT | the slice is CORRUPTED |
- Its screens use the VIRUS ooze, framed by a fleshy violet rim with barbs. Claws grip the host rim, and 3 pips count the turns left.
- **Proposed rules:**
  - It rides its slice through spins and flips, like a satellite.
  - When that slice resolves, the parasite sub-slice in line with the pointer tick applies its modifier. Example: EXPLOIT 14 × 0.5 = 7.
  - It lasts 3 turns, then detaches.
- **Open question:** it is mocked on the boss's own wheel, as briefed. Should the boss also latch it onto the player's wheel, as an attack the player has to outlast or cleanse?
- **Godot:** an `ArcSegment` node parented to the slice's `DockPoint`. It uses the same slice shader with the radii set to the outer ring, a grow tween on the outer radius, and three child glyph sprites.

## Weakest parts
- **At r = 60** the satellites and parasite slices are blobs. Their intent belongs on the forecast tag.
- **The overwrite strip on the sheet is small.** It reads better in the GIF.
