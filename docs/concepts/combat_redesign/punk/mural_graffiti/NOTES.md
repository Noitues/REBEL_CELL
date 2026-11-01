# MURAL GRAFFITI: punk-rock concept for the player wheel and the card hand (ART CALL 52)

Style brief: painted graffiti mural (ref 2, the Spider-Verse mural poster). Saturated spray on a brick or concrete wall, soft spray edges and drips, wildstyle outlines, warm and cool painterly light.
Base: finalist F1 (`finalist_1/`, never edited). Everything here comes from a copy of the F1 generator (`D:/rc_scratch/combat_redesign/punk/mural_graffiti/src`, changed files in `src_snapshot/`). The board (enemy rings, schedule, HUD, backdrop) is F1's, untouched.

## Files

| File | What |
|---|---|
| `plate_A.png`, `plate_B.png` | full `p1_decide` plate, 1920x1080, bio cutaway, same game state as F1 |
| `wheel_crop.jpg` | A and B wheels at 2x, side by side |
| `hand_crop.jpg` | A and B hands at 1x |
| `style_board.jpg` | palette, textures, line sample, one slice, the hub, one card large, the hand, manifesto |
| `src_snapshot/` | the files I added or changed (`mu_art.py` tower, `mu_cards.py` cards, `mu_ui.py` YOU strip / SEND IT / nameplate) |

## Idea

The Cell does not draw its board in a book (F1). It paints a wall. The wheel is a round section of wall with a mural on it: six wedges sprayed hot pink, lit by a warm sunset from the top left and a cool shade from the bottom right, outlined like a throw-up (ink, then a white keyline), with drips running off the outer rim and the wall (mortar lines, panel seams) still showing through the paint. The hub is the sun of the mural. The cards are painted plaques cut from the same wall: a sprayed sunset-and-skyline panel, a magenta spray disc with a white stencil icon, an ink title slab, plaster below.

Two variants, same layout, same grammar:

- **A, brick and airbrush.** Red brick roundel in warm light. Soft airbrushed light and shade on the wedges, orange paint drop under the icons, a yellow-orange sun hub. Cards: warm sunset panel, cream plaster over brick coursing, white title, teal type stripe.
- **B, concrete and cel.** Blue-grey concrete with panel seams and tie holes. Hard-edged cel light on the wedges (violet shadow plate, cyan rim on the shadow edge, warm sliver on the lit edge, like a comic print), a violet chunk-extrude under each wedge, cyan paint drop under the icons, a blue bubble hub. Cards: night-sky panel, pale concrete plaster, yellow title, yellow type stripe.

## Cards (designer note: keep the black-book layout, restyle for cohesion)

Layout is the F1 layout, position for position: cost badge top-left (RAM cyan coin, as before), big icon, title, type band, rules text, the Trace "+1" tab top-right, the x3 multiplier on Spin, the tag scribble bottom-right. Same hand fan (1.15x, 4 degrees per card, 182 px step).
Titles: the F1 pink-on-dark title was the unreadable bit. Now the title sits on a flat ink slab, white (A) or yellow (B) with a 2 px ink edge and a hot drop, at about 42 px Anton. Contrast against the slab is above 15:1 in both. The title never sits on the sky panel or the plaster. Rules text is dark marker on plaster, 21 px, same as F1's size but dark on light.
The loud (Trace) tab stays violet, the RAM coin stays cyan.

## How it keeps the ART CALL 51 grammar

- **No dashed lines.** Dotted is still only the +2 threat trim, which F1 already drew; this concept did not touch the trim, the rings or the schedule. I did not re-run the dash audit on these two plates (F1's audit logged 0 dashed calls; this concept adds no dashed or dotted draw calls: mortar and seams are solid, texture only).
- **HOT / COLD / FAR time marks:** unchanged (trim at r200-210 is F1's code and sits outside the wall).
- **Cross-hatch for pending HP loss:** unchanged and still the one hatch on the screen. It is drawn over the painted wedge (red hatch for harm, as on the plates: the two lower-right slices in the crops) and over the HP-ring blocks. Brick coursing is horizontal and faint, so the 45 degree hatch does not read as brick.
- **Arrowed outline = movement:** untouched (schedule THIS TURN cell, wave-queue feed arrow).
- **One enamel outline for enemy cells, W4-W6 tickets:** untouched.
- **Slice overlays:** the Brace plate is now a bolted chrome plate (two ink lines, jaw ticks, rivets) instead of taped paper; the soak funnel is unchanged. The F1 harm / protect overlay family was not redrawn here (no resolve beats were rendered).
- **Needle removed.** The `needle()` call is dropped from the plate (`f1_render.py`), so there is no marker at 12 o'clock on the outer schedule ring. The grey "0" disc at 12 o'clock is the sector-digit boss for sector 0 (one of six digit bosses, F1's), not the needle. The THIS TURN tape marks its own start.
- **Game information:** the same sim state (`state_e10.json` f1), same numbers, same words. Nothing in the wheel, hand or HUD data was changed. I did not re-run `f1_infocheck.py`.

## Legibility risks (read these before picking)

1. **The brick barely shows.** The page margin outside the wedges is only about 15 px (r177-192) plus the 9 px wedge gaps, so the "painted wall" reads mostly through the mortar lines inside the wedges and the chipped dark rim. If the designer wants a louder mural, the wall needs more area than the layout gives (a wider page ring or a smaller wedge radius).
2. **Red hatch on pink.** A wedge in break state is magenta under a red hatch plus a red outline. It reads, but less sharply than a blue or yellow underlay would; B's violet shadow plate helps a little.
3. **B's cyan and warm rim lines** read as a second outline next to the ink one at 1x (a thin neon edge on two sides of each wedge). It is punk, but it adds line count in the one place the screen is already busiest. Drop the rim first if it is too noisy.
4. **Drips are small.** At 1x the drips are 10-19 px pink sticks with a bulb; they read as drips at 2x and as small ticks at 1x. They are decoration only and sit outside the pips (never over a pip or an HP block).
5. **Loudness.** Brighter and more saturated than F1 (sunset gradients, yellow sun hub, orange SEND IT slab). The wheel is still the loudest object, but the hand and SEND IT in A are warm and close to it in value. I did not rerun the squint metrics. The cheapest cuts are the hub (A is the brightest thing on the wheel) and the sky panel value.
6. **A: warm hub on a pink wheel.** The yellow-orange hub is the one non-pink object in the wheel; it reads as "the sun", but it also draws the eye away from the slices. B's blue hub does the same in a cooler key.
7. **Plaster text.** Rules text is dark on light and readable, but A's brick coursing on the plaster adds line noise behind the text at 14 percent. Lower it if the text looks busy.
8. The cards at rest sit under the same shadow and 88 percent value as F1; the lifted-card print (pink offset) was not changed and was not rendered here.

## How it would be built in Godot

The wheel stays what F1 specifies (a Node2D with six wedge sprites, icons, pips, an HP ring); only the art and a few shaders change.

- **Wall:** one baked 1024 px wall texture per variant (brick courses with per-brick colour, or concrete with seams and tie holes) on a circular page sprite with a noise-eroded alpha edge (shader: `smoothstep` on a noise texture) for the chipped rim. A warm / cool light ramp is a second, multiplied gradient texture, not baked, so it can follow the player's UI theme.
- **Wedges:** one baked wedge mask (`Polygon2D` or a sprite) per slice. A single `ShaderMaterial` does the paint: gradient from a 1D `GradientTexture`, noise grain, a soft edge from the mask blur, and `multiply` of the wall texture sampled in the same UV so the mortar shows through (set the wall sample at 20 percent). A (soft light): two blurred offset copies of the mask, subtracted, tinted warm and cool. B (cel): the same offset subtraction but through `step()` instead of blur, so the shadow, rim and sliver are hard shapes.
- **Outline:** wildstyle outline is two `Line2D` strokes per wedge (ink 5.4 px under, white 2.4 px over) from the baked mask polygon, or one outline shader that dilates the alpha twice. Drops (3 x 4 px ink, 5 x 6 px violet) are an offset duplicate sprite.
- **Drips:** a small `Line2D` per drip with a round cap and a bulb sprite at the end; on slice break or HP change they can run 0.4 s with a `Tween` on `points[1].y`, which sells the "wet paint" without any new asset. Keep them outside the pip radius.
- **Overspray:** a low-count `GPUParticles2D` one-shot (or a baked speckle sprite) around each wedge, 2 px dots, alpha 0.5, only on load and on a slice becoming broken.
- **Icons:** the E10 silhouettes as white sprites with a duplicate offset under them in the drop colour (orange A, cyan B) and an ink 2 px outline shader.
- **Hub:** radial gradient sprite plus the `Label` "BREAKER" with a theme outline of 2 px ink and a 1.8 px magenta offset shadow. The 12-ray ring is eight lines of a baked sprite.
- **Cards:** one `Control` scene per card (cost, icon, title, type, rules as separate nodes), baked into a `SubViewport` texture per card at load. The panel is a `TextureRect` with a vertical gradient (variant colours from a theme resource); the skyline is a shared tiling sprite with random seed offset per card; the spray disc and rays are shared sprites; the title is a `Label` in Anton with outline size 3 (ink) and shadow offset (2.6, 2.8) in the variant drop colour, on a plain ink `Panel` slab. Plaster and its brick or concrete overlay are two textures with `multiply`. The hover lift and played-slot outline reuse the F1 mechanics.
- **Variant switch:** all colours (title, strip, panel gradient, drop colours, wall texture, hub gradient) live in one `Theme` or `Resource` per variant, so A and B can be flipped in the settings without touching scenes.
- **Cost estimate:** two wall textures, two hub gradients, one wedge shader, one outline shader, one card scene with a theme swap. The baked source here (about 45 s per tower in numpy) is only the concept path; in engine everything above is a texture sample or a one-time bake.
