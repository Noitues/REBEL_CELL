# Round 45: how the inner-ring modifiers read

This round renders the designer's direction exactly:
- a ghost wedge on the slice under the needle;
- a tiled pattern of the modifier's mark inside it;
- a raised, lit active inner segment with a notch tick;
- words only on hover or aim;
- a split wedge when a slice has two modifiers.

It builds on the round 41 typical wheel stack (`round41_wheel_stack/scripts`, imported, not copied) and the locked round 39/40 ring look (`ringlock.py`: lips, gunmetal band, segment textures, grooves and bolts).

**What it supersedes:**
- **Glyph plates on the ring (ART_BIBLE 3.10):** removed.
- **Texture extension into the slice (3.10):** replaced by the wedge.
- **Sub-needle:** left out. The notch tick now does its job, so drawing both would duplicate it.

## Files
| File | What it shows |
|---|---|
| `busy_ring.png` | The BREAKER wheel at 1:1 combat size (r = 220, locked position) on the left and a 2x close-up on the right. ×2 DOUBLE is in effect on SHIM 6. The ring also carries PIERCE, CORRUPT, ENCRYPTED and OVERCLOCKED. **Partial cover:** the DOUBLE segment covers only 70 % of the slice, and PIERCE covers the rest. The raised gold plate with end caps and the tick show which segment is in effect. A strip at 0.5x shows Q/E INNER: now (DOUBLE), E (PIERCE in effect), and Q (a blank segment under the needle, so no wedge). |
| `busy_ring_hover.png` | The same, hovered. The "×2 DOUBLE" plate sits at the wedge's outer edge, clockwise of the blade, with the tooltip to the right of the wheel. The 2x side shows the plate only. |
| `two_mods.png` | The split wedge, hovered. ×2 DOUBLE is in the inner band and CORRUPT in the outer band. One plate shows both; the tooltip lists them in order. |
| `quiet_ring.png` | The Breaker rank 1 ring (×2 / Pierce / –) with the blank segment under the needle. There is no wedge, only the notches and a neutral cream-capped plate. |
| `pattern_sheet.png` | Each of the 6 modifiers, plus NONE, at 1:1 and 2:1, on the red attack slice (SHIM 6) and the teal DEFRAG 5 slice. See the deviation note below. |
| `in_combat.png`, `in_combat_hover.png` | The busy ring in the round 41 `combat_typical_v4` frame (combat44 `screen`, with only the player wheel swapped in). The boss forecast tooltip is off. |
| `compare.jpg` | Four panels: the current build before and after W2-A5/A6 (from `W1B_W2_GROUP.jpg` section 10), then the concept at rest and hovered. |
| `scripts/ring45.py` | Holds all the specs (the `MODS`, `WEDGE` and `RING` dicts) and the code: `ring_var`, `wedge`, `pattern`, `notch_tick`, `wheel`, `plate` and `tooltip`. |
| `scripts/make45.py` | `python make45.py busy hover two quiet sheet combat compare` builds every output (the sheet takes about 3 min). |

**Deviation on the shield slice.** The teal slice in the pattern sheet is DEFRAG (FIREWALL, cyan-teal), not SANDBOX. The host renderer kept the pink EXPLOIT screen when the program was swapped to SANDBOX, so I used the wheel's real teal slice instead.

## Specs

All values are in master units: R_IN = 130, R_OUT = 360. At combat size (r = 220), 1 master unit is 0.611 px.

### Ghost wedge (on the slice under the needle only)
- **Shape:**
  - Area: r 133 to 353, ±30° less a constant 5-unit inset on both radial edges.
  - Two modifiers: split at r = 245. Inner band 133–243 = the first modifier; outer band 247–353 = the second. Maximum two.
- **Fill, bottom to top:**
  1. Ink shade #06050A at 25 %.
  2. Tint wash at 10 %.
  3. A 30 % ink halo under each mark (mark alpha, dilated 5 px, 3 px blur).
  4. The marks at 24 %.
- **Read-window clear:** inside the read block's ellipse (centre r = 268, radii 96 × 50, 10 px feather), the marks and halo are halved.
- **Read block:** always re-stamped on top, full strength.
- **Edge:**
  - A 3-unit tint line at 90 % around the whole band outline.
  - Plus a 12-unit tint glow at 45 %, blurred by 7.
  - With two bands, each band is outlined in its own tint, which gives a double line at the split.
- **Z-order:** slice screen → wedge → state overlay → firmware → read block → notch tick → drone band.
  - It sits where the old ring extension was, under the overlay. The overlay's 45 % wash cap still applies.

### Pattern marks

Every pattern is laid out in the slice's own polar frame, so it turns with the slice. Only the read block counter-rotates.

| Modifier | Family | Tint | Mark | Size | Layout | Rotation and motion |
|---|---|---|---|---|---|---|
| DOUBLE | inner | #FFD24D | "×2", Bahnschrift Bold Condensed | 58 tall | rows every 68 from r0 + 37; 92 of arc apart; odd rows offset half a pitch | glyph up = outward; static |
| PIERCE | inner | #F2F6FF | chevron pointing outward, 36 wide × 20 tall, stroke 0.24 × size | 36 | 5 radial columns at 0°, ±14°, ±28°; rows every 30 | streams outward at 2 rows/s |
| CORRUPT | inner | #3CFF8C, with #FF3DA8 at hash > 0.88 | dead blocks in polar cells, 22 radial × (1–3) × 22 arc; a cell fills at hash > 0.55 | 22 | plus 3 scan tears: 5-unit pink arcs spanning 30–60°, each with a 3-unit green ghost offset ±3–6 | blocks re-roll 12× a second (ring rule); seeded |
| OVERCLOCKED | status | #FF7A1A | `ST_OVERCLOCKED` glyph mask | 44 | rows 64, arc 78, staggered | up = outward |
| ENCRYPTED | status | #5CE1FF | `ST_ENCRYPTED` | 44 | rows 64, arc 78, staggered | up = outward; optional slow outward scroll (the 3.8 asterisks) |
| PARASITE | status | #C85AFF | `ST_PARASITE` | 46 | rows 66, arc 80, staggered | up = outward |

- The same tint is used for the ring notch, the wedge edge, the plate border and the tooltip title.
- DOUBLE gold and OVERCLOCKED orange are the closest pair. Their marks differ (text vs glyph), and OVERCLOCKED was pushed to Heat orange to separate them.

### Inner ring
- **Band:** the locked ring at master 100–127.
- **Segments:** any span, in clockwise degrees `[a0, a1)` in the ring frame.
- **The segment in effect:** the one whose span contains compass 0 (the needle).
- **Inactive segments:**
  - Texture at 42 %.
  - A tint notch along the outer lip (r 124–127, 90 %, ending 3 units short of each groove) — the handle.
  - Blank segments have no notch.
  - No glyph plates.
- **Active segment:**
  - A raised plate at r 97–131 (3 in, 4 out), lighter gunmetal (×1.15).
  - Texture at 100 %.
  - Tint lips (1.1-unit Gaussian lines) at both edges.
  - 5-unit tint end caps across r 95–133. **The end caps are what show partial cover.**
  - A tint glow (plate dilated, 7 blur, 85 %).
  - A blank active segment uses cream at 80 % instead of a tint.
- **Notch tick:**
  - A cream #F2EEE4 triangle on the needle line: base 17 wide at r 114, tip at r 146 (into the slice's hub edge, under the firmware socket at 160).
  - Ink outline, plus a 3-unit dot in the active tint at r 119.

### Words on demand
- **When it shows:** only on hover of the wedge or while aiming at that wheel.
- **Plate:**
  - At r = R_OUT – 14, starting 9° clockwise of the needle. It mirrors to the counter-clockwise side when it would leave the screen.
  - Box: 32 px tall at 1.0, #0C0A12 at 95 %, 2 px border in the first tint, radius 6.
  - Text: 22 px Bahnschrift Bold Condensed.
  - Contents: the glyph (none for ×2) plus the word, with " + " between the two modifiers.
  - A leader line runs to r = R_OUT – 40.
- **Tooltip:**
  - The terminal tooltip from round 41 (17 px title in the tint, 15 px Consolas lines).
  - Placed at wheel centre +219 px, just under the plate.
  - Content: the modifier and its result, "covers N%: whole slice" when the cover is partial, the next segment, and Q/E INNER.
  - With two modifiers it lists both in order (inner band = first).

## Godot build notes
- **Recommended: one shader on the active slice's wedge.**
  - A sibling `Polygon2D` (or `ColorRect` + SDF) under the overlay node.
  - Uniforms: `mod_a`, `mod_b` (ids, -1 = none), `tint_a`, `tint_b`, `split_r`, `pattern_alpha` (0.24), `shade` (0.25), `wash` (0.10), `halo` (0.30), `read_center`, `read_radii`, `read_clear` (0.5), `time`, `seed`.
  - The fragment computes local polar (`r`, `u = θ·r`, slice-relative).
  - **Text and glyph families:** row `j = floor((r - r0) / row)`; column `k = round(u / arc - 0.5·(j & 1))`; cell centre `(r_j, θ_k)`. Rotate the fragment into the cell frame by `θ_k` and sample a **pattern atlas** (SDF cells: ×2, chevron, ST_OVERCLOCKED, ST_ENCRYPTED, ST_PARASITE; these can reuse the glyph SDF atlas from bible 6.2). Use `smoothstep` for the fill and a wider `smoothstep` for the halo.
  - **PIERCE:** fixed columns at multiples of 14°, `fract((r - time·60) / 30)`.
  - **CORRUPT:** a hash of `(floor(u / 22·w), floor(r / 22), floor(time·12) + seed)`, plus 3 tear arcs from uniforms.
  - **Edge and glow:** use the band SDF in the same shader.
  - One draw call per wheel. Numbers come from `UiConfig` (no magic numbers).
- **Alternative: a MultiMesh of glyph quads** (one instance per mark, the atlas shader per instance, masked by the wedge polygon via clip children). It is simpler to author but costs about 30–60 instances per wedge and still needs the glitch blocks in a shader.
- **Ring:** extend the existing annulus shader to `seg_start[8]`, `seg_end[8]`, `seg_type[8]` and `active`. The raised plate, caps and glow are the same SDF with `active` bounds. The tick is a `Polygon2D` child of the needle mount (it does not turn).
- **Motion:**
  - When the active segment changes, cross-fade the wedge pattern over 0.12 s (T1).
  - The plate grows to the new span (0.10 s ease-out).
  - The tick dot recolours.
  - Under reduce motion: no streaming chevrons and no re-rolling corrupt blocks (static frame).

## Checks done
- **Slice number and icon:** they read over every pattern at 1:1 on both slice types (pattern sheet). The "×2" marks at the read window are halved and stay behind the read block.
- **Active segment:** at 1:1, the gold raised plate plus caps plus tick identify it at a glance. In the partial-cover case the clockwise end cap sits visibly inside the slice, next to PIERCE's white notch.
- **Fix applied:** at first (14 % wash, 24 % marks, no shade) ×2 was hard to read at 1:1 over the busy EXPLOIT hex screen. The 25 % shade and 30 % halo fixed that, and DOUBLE went from 50 to 58.
- **Fix applied:** the CORRUPT blocks were enlarged from 16 to 22 because they vanished at 1:1.
- **Placement fix:** the hover cursor and tooltip were moved off the read block and the E nudge.

## Open
- **PIERCE (white) and OVERCLOCKED** are the weakest marks over the pink attack screen at 1:1. They are readable but quiet, so the edge colour carries the family there.
- **How a slice gets a second modifier** (card, Firmware, status) is not defined in the GDD. This round only renders the display.
- **The firmware socket sits over the tick tip** on the active slice. That is fine at r = 220, but tick vs socket needs a z-rule: the tick stays under the socket.

## Designer rulings (2026-10-13), override the specs above
1. **Stronger pattern.** Marks at **38 %** (was 24 %), halo 40 %, every mark about **1.3x** larger (DOUBLE 58 -> 75), spacing kept. The slice's number and icon still draw on top, with the marks halved under them. PIERCE and OVERCLOCKED get the largest boost: chevrons and bolts at 1.4x with a 2 px ink keyline.
2. **One modifier per slice.** The split wedge and `two_mods.png` are dropped. Shader uniforms drop to `mod`, `tint`. The plate and tooltip show a single modifier.
3. **Approved to build.**
