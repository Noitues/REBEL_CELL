# r2c_geo_vector_gritty: the triangulated poster, pushed dystopian

**What stayed.** The rendering language is unchanged from `r2c_geo_vector`. Every surface is a jittered grid of flat, crisp, outline-free triangles. Each triangle's tone comes from a ramp (*light + surface gradient + seeded jitter + an occasional tone flip*). All randomness is seeded, and the three city stills share every triangle.

**What changed.**
- **City fabric:** denser 2- and 4-parcel lots. Row heights go up (9–15 at the back, and 1–2.6 for a shanty front row). Newer towers are stacked on old ones, sometimes overhanging the street, and there's a three-tier mega-block. Walkways bridge streets, pipes run up walls, and roofs carry AC units and antennas. Sagging cable bundles hang between buildings, scaffolding lattices cover some facades, and cameras stand on poles. A hazy skyline of distant towers fills the background.
- **Signage:** stacked vertical blade signs and shopfront bands, about 30% of them broken (missing facets). Three huge corp billboards (an eye on the spire, a chevron logo on the twin tower, an eye over the slum block) have dead facets.
- **Grime:** facades darken toward the ground, dark streaks run down from the roofline, and rust-stain patches appear per facet. Graffiti is angular triangle glyphs, not letters.
- **Weather:** rain is long translucent triangle slivers. Smog is translucent triangle bands (yellow-grey by day, soot-violet at night, blood-red under lockdown). Wet streets show sky-shine facets, and there are faceted neon reflections under the signs.
- **Surveillance:** corp searchlights rake the night sky and drones patrol. Under lockdown you get red and blue strobe fans cast across the facets, hazard-striped barricades, armoured vehicles with light bars, gunship searchlights and roof alarms.

**Palette.** The base is soot navy `#262b36`, rust `#5a2c1a`, oily teal-grey `#2a4441`, concrete `#48463f`, brick `#4e2822` and corp slate `#223246`, all low saturation. The day sky is dirty yellow-grey (`#6e6a58` to `#a89c74`). Neon is kept sparing and harsh: sickly magenta `#c8287e`, acid green `#8ad010`, cold cyan `#1cb8d8`, sodium orange `#d86e10`, plus police red and blue under suspicion. At night only about 22% of windows are lit, mostly sodium. The UI keeps the same key as before: sodium path, cyan "you are here", magenta target, acid shop and red boss.

**Combat and shop.**
- **Combat:** the spinners are salvaged hardware. They have hazard-striped outer bands, bolts, rust blooms, facets chipped to bare metal and a bent pointer. The enemy wheel has a cracked rim with a missing chunk. Cards are worn stickers: a scuffed paper margin, edges rubbed through, scratches, torn corners and masking tape. The backdrop is a one-point-perspective alley built from triangles, with rain and smog.
- **Shop:** a stall under a dripping striped awning. The goods sit in cages, cables are tangled overhead, and the vendor is patched, with a respirator and a cracked visor. One letter of the neon sign is dead. Prices are handwritten on tape (Ink Free font), and there's a hazard-striped counter with graffiti tags.

**Technique and Godot.** It's still pure Python and Pillow. Run `python scripts/render_all.py` (about 10 s). The Godot recipe from `r2c_geo_vector` still applies: triangle meshes carry a ramp coordinate, and each theme swaps the ramp. The new layers map to cheap Godot parts:
- rain: a scrolling `MultiMesh` of slivers;
- smog: translucent `Polygon2D` bands with parallax;
- strobes and searchlights: additive triangle fans on a `CanvasLayer`;
- broken signs: a per-facet on/off mask animated by a flicker timer.
