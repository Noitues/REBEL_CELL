# r2b_painterly_matte: style notes

**How I translated the reference.** The reference is an establishing matte painting: a big blue sky with cumulus banks, hazy distant peaks, a crisp sunlit foreground and one ornate focal building with patina, all in loose painted brushwork. I kept that structure and changed the subject. The distant mountains became hazed corporate mega-towers and an arcology spire. The domed temple became "the Spire", a corp building with a verdigris dome, brass ribs and a finial that is also an antenna. The oasis became a turquoise canal with broken rock shelves. The small figures and red standards at the porch are still there for scale. At night and under suspicion, neon, lit windows and searchlights take over from the sun. The UI reads as the city's own ornament: brass frames with rivets, dark enamel plates and serif lettering, with cyan neon only where the net shows through.

**Palette.**
- Day: sky blue (40,92,186) to a warm horizon (232,222,200); sand and terracotta walls; verdigris (70,138,122); brass (214,172,92); canal turquoise.
- Night: navy (6,9,26) with magenta city-glow clouds; warm windows plus cyan and magenta neon.
- Suspicion: crimson sky, red-shifted grade, white searchlights.
- Always warm highlights over cool shadows (a split tone).
- UI: gold (214,172,92), enamel (18,24,32), and slice kinds ATTACK red, BLOCK teal, HACK violet, CREDIT gold.

**Technique.** The city, spinners and shop are 3D in Blender with EEVEE, the Standard view transform and a transparent film. I also render a depth pass, a sqrt-encoded view depth written through a material override. All of the Pillow post-pass (`paintlib.py`) is driven by depth:
- a painted sky with shaded cumulus puffs;
- atmospheric haze that veils geometry by distance;
- a brush repaint: tapered strokes that follow edges, grow with distance and sample softer colour far away;
- the crisp render blended back in the foreground;
- bloom, a split-tone grade, seeded canvas grain and a vignette.

The node overlay is projected from 3D, so paths sit on the ground plane and turn dotted where buildings hide them. All UI is drawn after the paint pass at 2x and downsampled, so it stays crisp. Everything is seeded. `scripts/build_all.sh <workdir>` rebuilds all five stills.

**Building it in Godot (2.5D).**
- Bake each district as layered matte plates: sky, far haze, mid city and foreground, with day and night versions. Use the same Blender scene and paint pass offline.
- Show them as parallax `Sprite2D`/`TextureRect` layers.
- Blend day, night and suspicion with a shader lerp plus an additive light layer for neon and searchlights. Animate the searchlights as additive cone sprites.
- Put nodes and paths in a `Node2D` overlay using baked projected coordinates, or a `Camera3D` projection if the map stays 3D.
- Pre-render spinners as a painted wheel texture that rotates, with a separate pointer sprite and glyphs drawn in code so layouts can change.
- Build cards and plates with `NinePatchRect` brass frames and a serif font. Card art is cut from the district plates.
