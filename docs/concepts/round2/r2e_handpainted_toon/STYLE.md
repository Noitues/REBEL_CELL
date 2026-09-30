# R2E: Hand-painted toon (with ink outlines)

**Translating the reference.** The reference is a chunky, slightly wonky teahouse. It has thick dark ink outlines, hand-painted surfaces and a warm, saturated palette, and it sits on a small painted ground base. I kept how it's rendered and swapped the subject:
- **City:** the neon ward is a floating diorama island. It has a grass rim, rocks, drain pipes and an earth underside. The buildings are fat, bevelled boxes with a little taper and tilt, painted bricks, trim bands and rooftop clutter (tanks, AC units, antennas). The landmarks are playful in the reference's teapot spirit: a giant noodle bowl with chopsticks, a corp spire with a halo ring, a billboard and a water tower.
- **Spinners:** crafted props. Each has a wooden back disc, a riveted brass or steel rim, raised painted slices with slab-serif numbers and a chunky pointer. Each stands on its own ground base.
- **UI:** built from the same material. Plaques are wood with brass trim and bolts. Cards are painted paper in coloured frames. Buttons are fat bevelled pills.

**Palette logic.** There are no grey shadows. Each base colour gets a painted pair: a warmer, brighter lit tone and a purple-shifted, more saturated shadow. Night and alarm change that pair, not the lights: blue for night, magenta-red for alarm. The overlay and UI always use the day pair, so they read the same in every state.
- Slices and nodes: attack `#e8483c`, defend `#27b5ad`, hack `#f2b534`, glitch `#9a5ee0`
- Wood `#9a5f33`, brass `#d9a441`, cream `#fff0cf`, ink `#1c1210`
- Backdrops: day `#3f5566` slate (as in the reference), night navy, alarm maroon

**Technique** (Blender 5.2 EEVEE, `scripts/`):
- **Surface shader:** `tt_lib.paint` outputs an emission colour. Light only chooses between the lit and shadow tones, through Shader-to-RGB and a toon curve. Brush-stroke texture comes from stretched noise, blotch noise, brick/plank/tile mortar lines, bottom grime, AO and painted glints.
- **Worn edges:** bevel faces get a lighter "worn edge" copy of the same paint.
- **Ink:** Freestyle lines about 2.6–3.2 px with tapered ends and Perlin wobble. A second, thin line set handles small text.
- **UI lighting:** UI props use a fixed "fake" light direction.
- **Post:** Pillow paints the brushy backdrop, grain and vignette. For combat and shop it also pushes the night city back as a blurred plate. `build_all.py` rebuilds everything.

**Building it in Godot 2.5D.**
- **Surfaces:** pre-render the buildings, props and spinner parts as sprites with this pipeline, or hand-paint the textures. Use a Godot toon shader in place of the painted-pair shading: a `light()` step between two albedo tones.
- **Outlines:** use an inverted-hull or screen-space edge pass for the ink.
- **Night and alarm:** do them as palette swaps (a lit/shade LUT per state) plus emissive layers. There's no need for real-time lighting.
- **UI:** build it as NinePatch wood and brass frames with painted fills, using the same two fonts: chunky display and slab numerals.
- **Spinners:** slices as separate painted sprites rotating on a crafted rim sprite.
