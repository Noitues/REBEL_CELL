# Street graffiti: the player wheel and the card hand as a painted street piece

Direction G1 of VISUAL_PLAN A.1. Two variants, both full 1920x1080 `p1_decide` plates on the same sim state (`state_e10.json` f1, same numbers, words and rules text).
Generator copy: `D:/rc_scratch/combat_redesign/street_graffiti/src` (the E10 board generator is untouched; the player layer is `sg_*.py`).

Files here:

| File | What |
|---|---|
| `style_board.jpg` | swatches, line and brush samples, type, one slice and one card at large size (A and B), the HP/hatch grammar in this style, manifesto, squint test |
| `plate_A.png`, `plate_B.png` | the two variants in context (p1_decide, f1) |
| `wheel_A_2x.png`, `wheel_B_2x.png` | true 2x crops of the wheel (re-rendered at 6x supersample, not upscaled from the plate) |
| `hand_A_2x.png`, `hand_B_2x.png` | true 2x crops of the hand, UNDO chip, SEND IT and hint |
| `checks.json`, `checks_squint_cvd.jpg` | pink vs red in deutan / protan / tritan, texture contrast, 320 px colour and grey, deutan and tritan views |

## 1. The idea

The cell paints its own machine. Everything the player owns is made by one hand with spray, marker, paper and tape, and it sits on the corp's clean glass like a piece on a wall. Pink (`CELL_PINK` #FF3DA8) is the ink, chrome (#C9D3E0) is the one extra ink, and nothing else is ever painted as paint.

The hand (what makes a P object look like it came from the same person):
- **Spray with a soft edge, grit and overspray dots.** Fills are not flat: a fade from pink to a deeper pink, a cel glare along the upper-left edge, a soft shade on the lower-right, grit specks.
- **A chunky outline stack:** ink 5.6 px, chrome 3.2 px (white at the top, blue-grey at the bottom), then the fill. A 3D drop (extruded 4.6 x 5.4 px) in dark magenta sits under it.
- **Wobble.** Every shape is warped by 0.8-1.4 px of smooth noise (the plan's cap is 1.5 px), so no edge is machine-true.
- **Marker strokes** for tracers, underlines and the zig-zag tag: tapered, 0.5 px wobble.
- **Drips and splatter** where paint is heavy. Drips are keylined so they show on pink.

**Variant A, burner wall.** The wheel is a wall plate (dark concrete, with roller-buffed patches and ghost tags in dead teal, violet and brick) carrying six wildstyle wedges: fat-cap spray fade, chrome and ink outline, extruded drop, small wildstyle arrows in the gutters, drips off the hub bubble. The hub is a throw-up bubble ring (chrome, pink spray) around a dark core with the BREAKER tag. Cards are wheat-paste posters: torn paper on a second, older sheet (wheat-paste stack), a dark wall chunk with a spray bloom, radial speed strokes and a fat-cap ring around a white stencil icon with a pink drop, a tag title (skewed Anton with chrome rim and drop), a masking-tape type strip, marker rules text on a pink swipe, and a marker zig-zag tag mark in the corner (a mark, no letters). SEND IT is a spray-painted pink slab with a white tag, drips and tape. The nameplate is a taped paper tag and the YOU strip is a taped paper strip.

**Variant B, stencil and sticker-bomb.** The wheel is a roller-shutter steel plate (ribs, rust streaks, bolts). Each wedge is a die-cut vinyl piece: a hard offset ink key plate (3 px misregistered), a paper-white border, flat pink with two hard stencil layers (shade with hand cross-hatch, light glare) misregistered by about 1.4 px, masking tape across three gutters. The hub is a round die-cut sticker. Cards are die-cut stickers: paper border, flat pink field with black stencil icon and a paper-white offset plate, a black paint-pen title slab with a pink drop, a pill type tag, a peeled corner on every second card, a gloss sweep. SEND IT, nameplate and YOU strip are the same sticker language.

A is wilder and warmer (paint and paper). B is more graphic and holds up better at small sizes (hard shapes, no soft fades).

## 2. How it meets the plan

**Family.** All of this is family P (VISUAL_PLAN A): the tower, slices, slice pips, player HP ring, guns and hit marks, cards, SEND IT, nameplate, and the YOU strip taped onto the HUD. The enemy side and HUD are the current E10 plate, with one change: the E10 mauve hues inside the board disc (r 392 around the board centre) are remapped to cool slate (`tone_enemy` in `sg_base.py`: hues 245-350 degrees go to about 208 degrees, saturation x0.55). That removes the "mauve next to pink" ownership clash. Nothing else on the board or HUD was redrawn.

**Line grammar.**
- L1 ink keyline: under every coloured mark (4.5 px: 5.6 for the wedge outline stack as a deliberate P identity border).
- L2 painted stroke: wedge outline, gun tracers (pink, tapered 6.8 to 3 px, ink keyline), card ring, underlines, tag marks.
- L7 cross-hatch is used for one meaning only, "lost at the end of this turn": red hatch on the six HP ring segments that go (the enemy takes them), red hatch on the two slice pips that go (sectors 3 and 4), red hatch across the two slices that break (sectors 1 and 2, kept 6 px away from the icon and the pips), and red hatch on the YOU strip segments. The strip and the ring show the same grammar. Indigo (soak) and pink (our hits) hatches are drawn on the style board; they do not occur in f1.
- L8 dotted: the +2 threat trim dots (T family, flat, not painted).
- L9 glow: only the hot red marks (the pending HP hatch, slice-pip hatch, hot trim). Paint never glows.
- **No dashed line anywhere in the player layer.** (The E10 board behind it still has its dashes: that is the E and K streams' job.)
- L5 arrowed outline is not used by the player layer in p1 (it appears in hover and preview plates).

**Time grammar.** Hot trim (this END TURN): solid 4.2 px red stencil with ink keyline, glow, and the END notch on the tower-facing edge, on sectors 1-4. Cold (+1): thinner, desaturated brick colour, one turn pip, no glow, on sectors 0, 2, 5. Far (+2): dots, on sectors 0, 1, 4, 5. The trim is the T family (flat red stencil, no paint texture) so it does not look painted by the player.

**HP grammar.** Segment shapes: rounded capsules (r3 equivalent). Current: GAIN green with ink edge and a white glint. Lost at END TURN by the enemy: dark socket, red cross-hatch, solid 1.5 px red edge, glow. Gone: dark socket with a hairline. Mend pending: GAIN outline with a plus (drawn on the board). Player HP ring is 15 segments in 3 groups of 5 (9 degree group gap, 2.5 degree segment gap, 6.8 px thick at r 148.8-155.6); the pending run starts at the needle (top) and runs clockwise: 6 hatched, 9 lit (15 to 9, same as the E10 bill).

**Colours.** Pink is only "ours". Red is only harm (hatch, chevrons, trim). Green is only life. Chrome, ink, paper and the wall are neutral. The cyan RAM coin and the violet Trace tab are kept as stickers on the cards (S colours, with a paper border so they look slapped on). Paint is never red, yellow, orange, indigo or green. The wedges are all one pink: slice type is told by the icon alone (plan E).

**Invariants.**
- Ownership read: tower and cards share the spray grit, the 3D drop, the wobble and the chrome keyline. The squint sheet (`checks_squint_cvd.jpg`) shows both as the rough, bright, textured objects against the thin dark corp board.
- Readability cap: texture contrast inside a slice is 5.1 percent of the icon's contrast (high-pass luminance std at sigma 6 px, sector 0, outside a 6 px buffer around the icon and the pips; `checks.json`). Nothing textured sits within 6 px of an icon or an HP segment (the overspray is clipped at r 135, the hatch on breaking slices is cut 6.5 px around icons and pips).
- Slice icons are white silhouettes with an ink outline, 44 px (the shield is drawn as a heater with a split).
- No texture on rings, arcs or threat marks. Decoration lives inside r 160.5 (the wall plate), on the cards and on the stickers.
- No halftone dots anywhere (halftone belongs to X). No glow on paint.
- Pink and the damage red: CELL_PINK vs HARM dE is 66 normal, 62 deutan, 67 protan, 23 tritan (plan floor 12). The red hatch vs the mid wedge pink is 66 / 64 / 67 / 19. No fallback pink is needed.

**Deviations from the plan numbers (all on purpose, all small).**
- Wedges end at r 122 (not 143) so that the tower can hold three trim tracks and the HP ring inside r 160 without crowding. The trim tracks are r 124-141 and the HP ring r 148.8-155.6.
- Slice pips are 23 degree capsules, 8 px thick at r 106-114 (not 30 degrees at r 128-136, which does not fit two per wedge once the gutters are 16 px).
- The YOU strip segments are 12.6 x 17 px with a 15.6 px pitch (not 22 x 14): 15 segments at 22 px would not fit beside the hero pair without moving it.
- The wave info, ring cells, landing arcs and HUD rows are the E10 ones. I did not apply plan F (wave queue) or the clock restyle here.

## 3. Legibility risks (honest list)

1. **Hatch pitch.** The hatch is 3.5-4.6 px pitch with 1.1-1.5 px lines because the HP segments are only 6.8 px thick (the plan says 5 px pitch, 2 px line). At 1080p it reads as a red mesh. At 320 px wide it collapses to a solid red segment. The 1.5 px solid red edge and the glow carry the meaning, so it does not fail, but "cross-hatch" is only seen at 1080p or above. A reduced-motion or low-res mode should fall back to the solid edge plus a diagonal notch.
2. **Busy tower.** Splatter, drips, ghost tags and overspray are all kept out of icons and HP segments, but at 1x they read as grime on the wheel. In A the wall ghost layer is the first thing to cut if it tests as noise. B is calmer.
3. **Cards are the brightest things on screen.** Paper cream and white borders are higher value than any board element. That helps the ownership read, but it pulls the eye to the hand. If the designer finds it too loud: paper to 85 percent value, and dim unaffordable cards further.
4. **Marker rules text at 14-21 px.** Permanent Marker has tight counters. It is fine at 1080p; at 720p scaling the smallest line ("Turn the tower 3", 16 px) is borderline. A fallback: Anton or a plain condensed sans for the rules text when the UI scale is below 0.75.
5. **Red-on-pink on the breaking slices.** The red hatch sits on a dark wash over the pink so it reads, but this is the lowest-contrast mark on the wheel (tritan dE is 19). The X stencil in the outer corner and the shape of the hatch help.
6. **B's white die-cut borders** could be mistaken for the enemy's white `ENAMEL` outlines. They are warm paper (#F2EEE4) against cool enamel (#D9E1EA), a small difference. Keep an eye on this at the squint size.
7. **Pink tracers cross ring cells.** They are L2 strokes (allowed) with an ink keyline, but they cover the unit tokens' neighbourhood. The hit starbursts sit on the cell centre and can hide a unit's HP ticks. If that is a problem, stop the tracer 12 px short and put the burst on the cell edge.
8. **Not rendered:** the nowords plate, p2/p2b/p3, brace and soak states, the broken (0 HP) slice. The slice stage is written to support them (hatch colours, brace and soak marks would be paper and paint plates), but they are not drawn here. The nowords variant only drops the BREAKER label.
9. **The board behind is the E10 board** (dashed lane outlines, white landing lanes, orange and blue outlines). Next to P it looks busy, which makes the P layer look cleaner than it will in the final plate.

## 4. How it would be built in Godot

The python here (`sg_gfx.py`) is the art reference and the bake tool. The runtime does not need numpy.

**What is baked offline (PNG atlases, import as lossless, mipmaps off for the line art):**
- `wall_plate_{a,b}.png` (tower plate at 2x, 720 px), seamless `concrete_256.png`, `steel_rib_256.png`.
- One `wedge_sdf.png` (the slice shape, 256 px, signed-distance in R, the interior gradient in G, grit in B). All six slices reuse it, rotated 60 degrees each. Six `wedge_wobble_n.png` variants (alpha masks with 1 px warp) make the pieces not identical.
- `hub_bubble.png`, `icon_*.png` (4 slice icons, white silhouettes with the ink outline baked), `crest.png`.
- `paper_256.png` (seamless wheat-paste tile, ridge in A), `torn_mask_{0..5}.png` (card-size alpha with the fibre rim in G), `tape_{0..7}.png`, `drips_atlas.png` (3x3 drip variants, 64 px), `splat_atlas.png`, `starburst_{0..3}.png` (hit marks), `hatch_tile.png` (R = 45 degree lines, G = 135 degree lines, seamless 32 px).
- Card art bands: 11 pre-painted `art_<card>.png` (160 x 118 at 2x: wall, spray bloom, rays, ring, stencil icon). These do not change at run time.
- Tag titles are **not** baked: use a `Label` with `LabelSettings` (Anton, outline 5, chrome outline as a second label behind, shadow offset (3.2, 3.8) in `PINK_DK`), skewed by a `Transform2D` (-0.16) and rotated -3 degrees. This keeps localisation free.

**Shaders (canvas_item):**
- `player_paint.gdshader`: takes the wedge SDF atlas and the palette as uniforms (`pink`, `pink_hi`, `pink_lo`, `ink`, `chrome`). It draws, from one SDF sample: ink band (d in 0..5.6 px), chrome band (0..3.2), the fill gradient radially, glare (SDF offset by (5.2, 6) px and subtracted), shade (offset by (-9, -10) px), grit from a noise texture, and the 3D drop by sampling the SDF at a shifted UV (one extra tap). Overspray is a threshold of a dot texture against a pre-blurred mask in the SDF's alpha. Cost: two texture taps per pixel.
- `hatch.gdshader`: clips `hatch_tile.png` (screen-space pitch, no time input so it does not shimmer) to the segment SDF, with `HARM`, `SOAK` or `CELL_PINK` as a uniform. HP segments (15 ring + 12 pips + 15 YOU strip) are one `MultiMeshInstance2D` with per-instance custom data (state, hatch colour).
- `boil.gdshader` (optional): re-seeds the UV wobble at 8 fps on hover only, to make hovered things feel hand-drawn. It is off under reduce-effects.
- `marker_text.gdshader`: a 0.3 px sine UV warp on the rules `Label` so marker text is not machine-straight.
- Hot marks (pending hatch, hot trim) get a separate additive sprite with a baked 4 px blur at 35 percent (no WorldEnvironment glow in the 2D pass). All other paint has no glow.

**Scene layout:** `PlayerWheel` (Node2D) holds `WallPlate`, six `Slice` nodes (wedge sprite with the shader, icon, two pips), `HubBubble`, `TrimArcs` (T family, plain `Line2D`s, drawn after the paint), `HpRing` (MultiMesh), `Guns` (Line2D with a tapered width curve and the keylined material, starburst sprites at the end). `Hand` is a `Control` that fans the cards on an arc (pivot below the screen, 1000 px radius, 170 px spacing, 94 percent scale in these plates). Each `Card` is: the shadow, the under-sheet, the paper with the torn mask, the art band, the title labels, the type tape, the rules label, the cost sticker, and the loud tab.

**Sprite sheets and animation (all at 60 fps, none above 3 flashes per second):**
- `spray_in` for a slice that changes state (8 frames, the fill grows from the hub).
- `scribble_out` for a slice that breaks (6 frames, the hatch is drawn on, then the stencil X stamps).
- `drip_grow` (8 frames), played once when a slice takes a hit.
- `paste_slap` for a card entering the hand (6 frames: scale overshoot, the paper settles, the glue halo appears), and `peel` for a played card (8 frames, B only).
- Hover: the existing grow (1.06) plus the shadow offset widening 4 px. Reduce-effects: all of the above become single frames, and the boil is off.

**Budget:** the whole player layer is about 40 sprites and one MultiMesh (about 60 quads), one 2048 px atlas, two shaders. That is a few dozen draw calls on a Godot 4 canvas.

## 5. Re-running

`sg_base.py` renders the non-player layers once (12 s). `sg_plate.py A|B [redo=tower,guns,cards,ui]` assembles a plate from cached components. `sg_crops.py wheel:A hand:B ...` makes the 2x crops. `sg_board.py` makes the style board. `sg_checks.py` makes the checks. All need the E10 `PYTHONPATH` used for `asm_r2`.
Process note: I ran `python -` once by mistake (an empty stdin heredoc). It hung and I stopped that background task straight away; no other process of mine was left running.
