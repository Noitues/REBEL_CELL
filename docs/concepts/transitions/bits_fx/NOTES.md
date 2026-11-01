# T5 / T6 binary-bits FX: three designs (art only, compositing with PIL/numpy)

Base: the v3 storyboard keys (T5 1.2 s, T6 0.8 s), room_bio_bare (v3.1) and the E10 plate p1_decide, all at 960x540.
Rebuild: `python scripts/prep.py` then `python scripts/render.py` (scripts/quick.py previews single times; prep writes a `work/` cache).
Files: `t5_A|B|C.gif` (15 frames, 80 ms, 1.2 s, 960 px, about 3.2 MB each), `t6_A|B|C.gif` (10 frames, 0.8 s, about 2.4 MB),
`strip_A|B|C.jpg` (5 key frames for T5 and for T6, labelled), `sheet.jpg` (A/B/C at the same keys), `metrics.json`.

## Shared choices (logged, made without asking)
1. **What flies in and what is built from bits.** The wheel hub (the tower slices, r < 88 px at 960) flies in as a sprite on the K2 key
   (1.35x to 1.0x, 4 % overshoot, 7 degree spin settle, 0.25-0.55 s; the room dims to the plate scrim over 0.2-0.6 s). The rings around it
   (r 88-259) are the enemy, so they are NOT in the sprite: they are built from bits 0.50-1.05 s. This follows the brief (enemy rings fly from the room as bits and resolve into the wheel's rings). The storyboard K2 comp showed the whole wheel; K2 now shows the hub only.
2. **Bit source** is the lab floor of the bio cutaway (right half of the room). Bit paths are quadratic beziers with a swirl, ease-in-out.
3. **Lock** (K5, 90 ms snap, t = 0.96-1.05): a thin ink keyline round the finished board (A: the three ring paths; B: ink + cream; C: ink + schedule orange). No white.
4. **HUD** (top panels, cards and SEND IT, CELL-9 tag) slides in 1.05-1.20 s with a 20 ms stagger; K6 is the real p1_decide (t = 1.2 returns the plate pixel for pixel).
5. **T6 (win path):** UI fades 0-0.2 s, the board (hub included) breaks to bits 0.06-0.45 s which drain into the room (ease-in), the dim lifts back to the bare room by 0.8 s. The last frame is room_bio_bare. The fail branch (glitch tear) is not touched.
6. **Colour:** only BRIEF 3.3 tokens; enemy marks never use NET_CYAN (cyan appears only on the player's hub keyline in A's T6). No glow, no bloom; every bit has an INK keyline or edge (A: glyph stroke 18 % of size; B: 1 px; C: top cut line + paper shadow).

## A: cel-inked glyph bits + ink keylines riding the ring paths
- Idea: 0/1 glyphs (Consolas Bold, ink-outlined like the bible 3.5 glyph set) stream from the lab, curve in and land on three ring paths
  (inner r122, mid r178, outer r250 at 960). An ink keyline arc (8 px ink, 3.2 px colour) is drawn round each path by a head dot; the real ring art
  is revealed behind the head and the glyphs are absorbed into the stroke. Faint dashed ink ghosts of the three paths show the destination from 0.28 s.
  T6 runs it backwards: the keyline eats the board (outer, mid, inner, then the hub) and throws the glyphs back to the room.
- Tokens: CREAM #FFF4D6 (inner), LANE_PLUS1 #78AAFF (mid), HARM #FF4433 (outer), 1 glyph in 5 SCHEDULE_ORANGE #FF8C1A, INK #0C0A16; T6 hub in NET_CYAN #5CE1FF.
- Godot cost: **low to medium.** Ring reveal = one CanvasItem shader on the ring sprite (an angle-sweep uniform per ring, 3 uniforms); keyline = `Line2D` arcs or a ring shader;
  glyphs = 3 `GPUParticles2D` (one per ring, a 2-frame 0/1 atlas outlined in the texture, a curved path via Path2D/PathFollow2D or a baked curve; about 270 particles). No per-cell data.
- Read: clearest, most cel/ink (it reuses the ink language and the ring paths), lightest on screen.

## B: pixel/byte blocks in the ring's own colours stacking into ring cells
- Idea: each salient 6 px cell of the ring art (about 2.9 k) becomes a flat block in its own colour with a 1 px ink edge. Blocks (3 px growing to 6 px, 2 px stepped positions, a short streak) fly from the room in a swirl, inner cells first,
  and snap into place where the true cell pixels cross-fade in over 90 ms. The dark ring bed arrives in stepped 50 % steps. T6 reverses it (outer cells first, ease-in).
- Tokens: none added; each block takes the mean salient colour of its own cell in the plate (HARM, SCHEDULE_ORANGE, LANE_PLUS1, CREAM, GAIN, STEEL, TRACE, as drawn), INK edge.
- Godot cost: **highest.** A `MultiMeshInstance2D` of about 3 k quads with per-instance colour and target and a vertex shader driven by one progress uniform (bezier in the shader), or `GPUParticles2D` with a baked 160x90 cell-colour texture.
  Needs an offline bake (or a runtime downsample) of the ring art per board layout.
- Read: densest and most data-like, but closest to a generic pixel dissolve; about 3 k moving things is busy, and 6 px sits at the legibility floor.

## C: scanline / cut-paper strip peel
- Idea: the ring art is cut into 10 px paper strips; each strip peels off the lab floor (staggered by a golden shuffle so neighbours do not move together), slides out on a short arc with an alternating wobble,
  is printed flat (posterised, ink cut edge, paper drop shadow) while it travels and trails 5 digits (0/1 in the strip's strongest colour with an ink outline); on landing it prints in true colour. T6 peels the board off the same way, top to bottom.
- Tokens: ring colours as drawn, INK edges and shadow, SCHEDULE_ORANGE for the lock keyline.
- Godot cost: **lowest.** One fragment shader on the ring sprite (per-row offset from `floor(UV.y * N)`, a hash for the stagger, a progress uniform, posterise + edge line) plus a small `GPUParticles2D` for digits (or a digit texture masked by the strip alpha).
  No per-cell data, resolution independent, the same shader serves T6.
- Read: the most original and most paper-like, but it reads as a venetian-blind / TV tear more than as binary bits, and the dark strips look muddy at 12 fps. Weakest on the bits idea.

## Reduced motion and flashing
- Reduced-motion variant (all three): 0.25 s cross-fade room to board (T5) and board to room (T6), as in the storyboard; no FX, no motion. A `reduce_motion` flag simply skips the FX node.
- Strobing check (`metrics.json`, mean frame luma at 12.5 fps): the largest frame-to-frame change is 2.1 % of full scale in T5 and 1.8 % in T6 (A, B and C; it is the room dim and the HUD slide). There is no full-frame white flash; no frame is brighter than the end states (mean luma 0.21).
  The luma curve has at most 3 slow reversals in 1.2 s, each under 2.2 % of the screen luma, so it is far under the 3 flashes per second and 10 % screen-luma limits. The lock pulses are 90 ms thin coloured outlines, not area flashes.

## Recommendation
**A** for T5 and T6. It is the only option that shows binary bits as bits and also uses the city's ink language (outlined glyphs, a keyline that draws each ring path, flat colour), it animates the wheel's structure (three ring paths), it is the easiest to read and it is
one shader plus three particle emitters in Godot. Before it ships: more glyph variety (a few 1-0 pair clusters), a stagger so the three paths start from different parts of the building, and a check on the srv and gh rooms where the source point moves.
**C** is the fallback if A cannot be built in time (cheapest shader); **B** is not recommended (heaviest, generic).
Open point for the art director: K2 now shows only the hub (rings are the enemy); if the full wheel is wanted on K2 as in the storyboard comp, the rings can show as A's ghost paths only (that is already how A looks at K2-K3).
