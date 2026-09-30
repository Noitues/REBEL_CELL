# r2d_neon_painting: vibrant neon digital painting

**Translating the reference.** The reference is a hacker lit by a vortex of light rings, with glass shards drifting through purple haze. I kept its rendering and dropped its subject.
- **Rings of light.** The vortex became the game's shape language. The city has the Halo, a hologram swirl hanging over the district. The spinners sit inside tilted rings of tapered light arcs. The "you are here" node, the GO button, card art and the shop sign all use the same swirl.
- **Shards and fragments.** Iridescent thin-film glass shards and small emissive data squares float through every scene.
- **Luminous spill.** Building walls pick up magenta, orange and violet spill according to which way they face, and it fades with height. Windows are small, scattered neon dashes.
- **Haze and finish.** Bounded volumetric fog boxes give the purple haze. An oil-paint pass softens the image into painted patches and adds glowing highlights.

**Palette.** A dark violet base (#1a0a2e to #3a1a55). Accents are hot magenta #ff2a8c, amber orange #ff8c1a and cyan #1ac8ff. Each UI meaning has a fixed hue: attack is magenta, block is cyan and hack is amber. Day is a pastel version (lilac shadows, peach and pink lit tops). High suspicion shifts the city to crimson and adds white searchlight cones.

**Technique.**
1. **Blender 5.2 EEVEE.** Emission and thin-film materials, a procedural window shader, fog volumes, spotlights for the searchlights, and compositor bloom. The UI is flat geometry parented to the camera, and depth of field pushes the city back.
2. **Pillow post-pass.** A Kuwahara oil filter built from Pillow primitives, a light layer of flow-field brush strokes that swirl around the Halo, multi-radius screen glow, a haze lift and grade, and grain.
3. **UI text.** All text is drawn last in Pillow, crisp with a glow, so it stays readable.

**In Godot (2D/2.5D).**
- **City.** Pre-render the city as layered plates (ground, mid, skyline, haze) per mood. Nodes and paths are live Line2D and Sprite2D objects on the ground plane.
- **Rings.** Build the swirls from Line2D arcs with width curves and additive blending, rotating at different speeds. This is cheap, and it animates, which the stills can't.
- **Glow and paint.** WorldEnvironment glow, or one bloom pass on the SubViewport, gives the glow. A Kuwahara-style screen shader can give the painted finish at low strength, kept off the UI CanvasLayer.
- **Shards.** Shards are GPUParticles2D with an iridescent gradient-map shader.
- **UI.** Cards and panels are NinePatch frames with neon edge sprites.

**Scripts.** `scripts/run_all.sh [samples] [tmp]` rebuilds everything. `layout.py` is the shared data, `bl_kit.py` and `bl_city.py` build the scene, `render_shot.py` renders each still, `post.py` does the paint and UI pass, and `contact_sheet.py` builds the sheet. All randomness is seeded.
