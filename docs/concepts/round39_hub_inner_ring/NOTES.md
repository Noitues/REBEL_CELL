# Round 39: hub cores v2, enemy breach timer, player defeat, inner ring v2 + proposals

This round applies the designer's round 38 review. Earlier rounds are not edited.

**Approved in round 38 and unchanged:** the Ghost, Swarm and Hive cores, and all 6 enemy hubs.

## Files
| File | What it shows |
|---|---|
| `hub_cores_v2.png` | The 5 redone cores (round 38 → round 39, base and Mk2, at 64, 24 and 16 px, grey, nearest twin), the approved row, the enemy BREACHED 1-turn timer strip (5 stages, r = 60, grey) and the player DEFEAT strip. |
| `phantom_echo.gif` | The Phantom Core's moving echo trail: 16 frames. |
| `player_core_defeat.gif` | The combat-loss core drain: 32 frames, ending on FLATLINED. |
| `inner_ring_v2.png` | Before/after (round 38 flat band against the round 39 machined ring), a ×2.4 close-up, r = 60 and grey, and every segment under the pointer extending into its slice. |
| `inner_ring_proposals.png` | Six inner-ring proposals, **all proposal (not in game)**. |
| `scripts/` | `glyphs39.py` (new shapes), `hub39.py` (echo, breach timer, defeat), `ring2.py` (machined ring, textures, extension) and `make39.py`. The rest is copied from round 38. |

Rebuild with `python scripts/make39.py all`.

## Hub cores
| Core | Change | 16 px twin |
|---|---|---|
| Breaker | A crowbar strikes an **unfilled** glass pane; crack lines spread from the hit. | 0.35 |
| Wrecker | The round 38 speed lines are removed. They were meant as "swing", but read as noise. Only the sledgehammer remains. | 0.55 |
| Phantom | The mask is kept. In the hub, the masks behind it are drawn as a moving echo trail: after-images slide left and fade, looping. For static icon use, `CORE_phantom_echo` has the mask plus two trailing echo arcs. | 0.69 (to CITATION, on the static shape) |
| Rigger | A firmware chip, with legs and die window, dropping into a socket with contacts. The power cord is gone. | 0.59 |
| Overclocker | An RPM gauge: tick scale, a solid red zone, the needle buried in the red, and an x1000 window. | 0.52 |

The Overclocker gauge is distinct from the OVERCLOCKED status gauge thanks to the red-zone wedge and the window plate.

## Enemy BREACHED: a 1-turn timer state
This follows GDD 2.8 and A.2 #13: **Hub Breach** disables the target Hub's passive for 1 turn, and **Short Circuit** for 2. Several bosses only heal or shield unless their Hub is breached.

The art keeps the round 38 breach: cracks, static, sparks and the passive struck out. It adds a **timer**:

| Stage | What it shows |
|---|---|
| 1. ONLINE | Normal hub. |
| 2. BREACHED | A red timer ring is full, with the turn count "1". |
| 3. Enemy turn | The ring drains. |
| 4. TIMER OUT | The ring is empty, showing "0". |
| 5. REBOOT | A scan wipe brings the screen back, labelled REBOOTING; the passive is on again. |

Short Circuit shows "2" and drains over two turns. At r = 60, a thick HARM ring carries the state.

**Godot:**
- a `TextureProgressBar`, radial, for the timer ring, bound to the remaining breach turns from the combat state;
- the reboot is a shader wipe (`progress` uniform) when the timer hits 0.

## Player DEFEAT
For the combat-loss screen (an operative is lost):
1. The core's pixels break into 4 px bits, bottom rows first.
2. The bits fall, tint toward the class accent and drain into a glowing slot at the bottom of the disc.
3. The ring and disc darken.
4. A **FLATLINED** plate with a flat line stamps in at the end.

**Godot:** a one-shot shader, `progress` 0 → 1 over about 2.2 s:
- block-quantise UVs;
- per-block delay = f(row) + hash;
- offset each block down by `q²·2R`;
- alpha `(1 − q)^0.6`.

FLATLINED is a `Label` fading in at progress 0.7. It plays once and holds.

## Inner ring v2 (concept art; the rules are a designer to-do)
**1. A substantial ring.**
- Outer and inner machined lips with accent hairlines.
- A recessed gunmetal band.
- Grooves with two bolts between the segments.
- A glass sheen.
- The lit segment (under the pointer) gets an accent edge glow.

**2. Full-segment textures.** Each segment carries a texture across its whole band, and keeps its glyph on a small plate at the centre. When the segment is under the pointer, its texture **extends into the outer slice it modifies**. The extension fades toward the rim and thins under the value block.

| Segment | Texture | Extension into the slice |
|---|---|---|
| ×2 | doubled gold hairline pairs | the same pairs rising |
| Pierce | white chevrons pointing outward | the chevrons stream outward through the slice |
| Corrupt | pink and green dead blocks | the blocks climb into the slice |
| Anchor | steel chain links | the chain reaches up |
| Accelerator | amber speed streaks running round | the streaks continue |
| Echo | cyan ripples | the ripples travel outward |
| Blank | brushed steel | none |

**At r = 60.** The ring reduces to lit and unlit colour bands. Textures and glyphs drop out.

**Godot:**
- One ring shader on an annulus `Polygon2D`, with uniforms `seg_type[3]`, `active` and `ring_rot`; the textures are procedural.
- The extension is a second `Polygon2D` wedge over the aligned slice, using the same texture function and a `fade` uniform, drawn under the slice's value block (layer order as round 17).

## Proposals (all proposal, not in game)
1. **ACCELERATOR → SUB-NEEDLE.** A mini second needle rides the segment and points outward. Whatever outer slice it points at also triggers ("TRIGGERS" tag). It turns with the inner ring.
2. **HANGAR (drone).** When aligned, it docks a drone on the slice it modifies: bay rails and dock lights, a drone landing at the slice rim, and a "DOCK +1" tag.
3. **DOUBLE STATUS** (a Corrupt rework). Statuses this slice applies land twice, or stack 2: paired diamonds. Its glyph is 0.70 to FLIP at 16 px and needs another pass if it is adopted.
4. **SPLASH (adjacent AOE).** The effect also hits the neighbouring slices or adjacent enemies; bursts spread into 3 slices.
5. **BROADCAST (global AOE).** The slice hits every enemy; waves leave the ring into all six slices, tagged "ALL ENEMIES".
6. **BLANK START.** Operatives start with 1–2 blank (brushed steel) segments and earn real segments as they rank up.

## Weakest part
- **The Anchor extension's chain links distort into a zigzag** in the slice's polar space.
- **The Phantom static icon is 0.69 to CITATION** at 16 px. The animated hub version is unaffected.
- **The ring glyph plates are small at r = 220.**
