# r2c_geo_vector_v3: gritty triangulated vector with variable facets and neon spill

**Kept.** The flat, crisp, outline-free triangles, with each triangle's tone taken from a ramp. The gritty megacity model, its palette and camera are unchanged from `r2c_geo_vector_gritty`. The day city is untouched apart from the facet change.

**Variable facet size.** Facet density now follows attention:
- **Big calm facets:** sky, the skyline, ground, the slab, ordinary buildings (about 2.2 world units per facet column, with fewer tone flips), and the alley and street walls (6×6 per wall).
- **Small dense facets:** signs, billboards, the focal buildings (corp spire, mega-block, billboard block at 1.6–2× density), spinners (2–4× slice subdivision), UI gems and the vendor.

**Night colour.** Coloured light now spills onto nearby facets. Every working sign, billboard and sodium street lamp is a point light. A `Lights.wrap` pass adds its colour, with a quadratic falloff, to walls, rooftops, streets and lots. Wet streets carry faceted neon reflection streaks, and coloured haze pools sit under the signs, with translucent coloured fog around the tall ones. The confetti is gone. Traffic is now a few light trails, skyline lights are sparse strips, and window lights are fewer and larger.

**Suspicion as an overlay.** The base colours are left untouched. The overlay adds white helicopter and drone spotlights with ground spots, red and blue strobe fans from armoured vehicles, hazard-striped barricades, roof alarms, the LOCKDOWN banner and a full suspicion meter. It works on both the day and the night city (stills 03 and 04).

**New stills.**
- **06, spinner close-up:** hero hardware. It has 4× facet density, slice glyphs and numbers, a needle with a counterweight, a bent pointer, a hazard band, rust, bolts, a serial plate, and an HP and legend readout.
- **07, shop exterior:** a storefront wedged into a wet street. A tall stacked "MODEM" neon blade and a "CYBER SHOP" sign light the walls (spill) and the puddles (a mirrored band reflection). The shop UI (cards, parts, prices on tape, REROLL, LEAVE) sits in a side panel.

**Godot.** Give each triangle mesh a ramp coordinate and a per-vertex light-accumulation colour. Bake the static spill, and animate the flickering signs by modulating their own lights. Build reflections and haze as additive `Polygon2D` fans, and the suspicion overlay as a separate `CanvasLayer` that sits over the unchanged base scene. Run `python scripts/render_all.py` to rebuild everything (about 15 s).
