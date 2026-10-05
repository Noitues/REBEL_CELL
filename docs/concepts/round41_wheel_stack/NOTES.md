# Round 41: multi-drone docking, the parasite pop-up, and the full wheel stack

Builds on round 40 (untouched). The blended dock, the replace animation and parasite option A are kept as agreed. The other agents' locked layers are redrawn in their agreed form for the combined mock:
- tier V2 strong;
- state overlay with the badge plus ×N tab and rule tag (outer clockwise corner);
- firmware socket at r = 168 (round 34);
- inner-ring texture extension and sub-needle (rounds 39 and 40).

## Files
| File | What it shows |
|---|---|
| `multi_drone.png` | Two drones on one slice (hangar): Botnet and Care Swarm at r = 220, the pair under the needle, and r = 60. |
| `parasite_popup.gif` | 25 frames, about 3.6 MB. The steps: 1. attached while the needle is elsewhere; 2. a 35-tick spin where it crosses the needle mid-spin and stays attached; 3. the wheel settles with the needle on it and it pops up beyond the tip; 4. the in-line sub-slice fires (PATCH 6 heals the boss); 5. on the next spin it drops back to attached. |
| `parasite_drones.png` | A parasite plus 1 or 2 drones on one slice, both attached and popped. Also the whole wheel at r = 220 and r = 60, and the rules. |
| `wheel_stack_combined.png` | The worst case. The whole wheel at r = 220, the slice enlarged, r = 60, the z-order, the radial zones of one slice drawn to scale, and the conflicts with their rules. |
| `scripts/` | `stack41.py` holds `dock_multi`, `put_drones`, the parasite states and the per-slice layers; `make41.py multi`, `popup`, `pdrones` and `combined` build the outputs. Also patched: `sat3.parasite2(radii=)`, `d4corp` (per-slot tier) and `tiles` (player tier colours). |

## 1. Two drones on one slice
- **One blended dock:** one rim band over the slice, plus a neck and collar per drone.
- **Placement:** the pair sits at the slice centre ±14°, so the collars clear each other and the needle blade passes between them. A single drone stays centred.
- **Replacing on a full hangar:** the targeted drone is replaced (default: the older one). It returns to the core as green bits.
- **Still open:** how damage works with two drones on one slice.

## 2. Parasite pop-up
- **Attached state:** a thin band hugging the frame over its slice (r RA + 6 to RA + 48), glyphs only. It stays like this while the needle is elsewhere, and during any spin, even when it crosses the needle.
- **Popped state:** once the wheel settles with the needle on its slice, it tweens out to option A. That means beyond the needle tip, at full depth, with glyphs and values. The sub-slice in line with the tick fires.
- **On the next spin** it drops back to attached.

## 3. Parasite plus drones
- **Radial order:** frame, then parasite, then drones. Drones dock beyond the parasite with a 26-unit gap, and their necks pass under it.
- **When it pops,** the drones move out with it, tweened together.
- **Bodyguard is unchanged:** a pointer attack on the slice hits a drone first.
- **The parasite is not a satellite.** It is never hit and never guards.

## 4. The full stack: z-order, bottom to top
1. slice screen
2. ring texture extension
3. tier inset
4. state overlay wash
5. firmware socket
6. sub-needle
7. **read block**
8. state badge + ×N tab + rule tag
9. frame + telemetry
10. dock lobes
11. parasite
12. drones
13. needle blades
14. card-preview ghosts

## Radial zones (master units, player wheel)
| Element | Radius |
|---|---|
| Hub + inner ring | < 127 |
| Sub-needle | 122 – 152 |
| Ring extension | 132 – 182 |
| Firmware socket | 142 – 194 |
| Read block | 230 – 306 |
| Badge | 300 – 352 |
| Frame | 360 – 414 |
| Needle | 336 – 510 |
| Parasite (attached) | 420 – 462 |
| Parasite (popped) | 526 – 616 |
| Drones | 642 – 884 |

## Conflicts and proposed rules
1. **Ghost blade vs a popped parasite or drones.** While a card is hovered, popped parasites on other slices drop back to attached. Ghosts draw on top of everything.
2. **Sub-needle vs firmware socket.** The sub-needle's tip stops at the slice lip (r 152). The socket sits at r 168. They always have a gap between them and never overlap.
3. **State overlay vs read block.** The wash stays at 45 % or less, and the read block is always re-stamped on top.
4. **Drones vs needle.**
   - A pair flanks the blade at ±14°.
   - A single drone on the needle's slice sits centred, beyond the blade top or the parasite. It is never under the blade.
5. **Headroom.** A popped parasite plus drones needs about 470 master units above the rim (about 290 px at r = 220).
   - When that happens on the top slice, the forecast tag shifts sideways.
   - Alternatively, the wheel scales down 10 %.
   - This is an open question for the designer.
6. **At r = 60** only colour, glyphs and the parasite and drone silhouettes survive. All values move to the forecast chip.
7. **Tier III gold border vs ring extension.** Both are warm, so the extension (hatch) is drawn at 120 alpha under the inset line. Tier always wins at the screen edge.

## Weakest parts
- **The worst case is tall.** It is legible at r = 220 but crowds anything placed above the wheel.
- **The sub-needle and firmware socket are small** next to the tier III border at sheet scale.
