# R2 hybrid E+C: a painted world with a crystal net

**The rule.** The physical world is E-gritty: chunky, wonky, bevelled props with thick wobbly Freestyle ink and hand-painted grime (rust runs, stains, chipped paint). That covers "The Sump" slab city, the salvaged spinners, the plaques and the stall. The digital layer uses C's triangle language: the net, the data and the UI. Every piece of it is faceted crystal with **no ink line** (`tt_facet.py`). Each triangle takes one of three tones of its colour, lit by a fixed facet light plus a fresnel glint, and outputs emission, so it glows at night.

**What's crystal.**
- Map nodes are faceted hex platforms with crystal pins pointing down onto them.
- Paths are ridged faceted ribbons: gold for open routes, cyan for the route out of "you are here", with data shards floating over it.
- The suspicion, HP and legend pips, the card cost pips, and the RAM counter are cut gems.
- The GO, REROLL and LEAVE buttons are big gems set in painted iron bezels.
- The spinner hub gem and its slice inlays are crystal, and so is the VS diamond.
- The billboard eye and the holograms are triangulated projections (`tri_panel` with an image function).
- Data effects are tetrahedral shards.

**Designer feedback, applied.**
- **Day:** the palette pair now warms the lit faces (toward `#ffd9a0`) and cools the shadows (toward `#26344c`). The smog backdrop is less brown.
- **Night:** every live sign spills its own coloured light onto the walls and street. Each also has a coloured haze cone and three glowing wet-street reflection streaks, and the lit tones are more saturated.
- **Suspicion:** it's an overlay on the normal day or night lighting, with no red wash. It brings helicopter and drone searchlights, red and blue strobes on armoured cars, hazard barriers, roof beacons, the LOCKDOWN plaque and crystal meter pips.
- **Close-up:** the hero wheel shows dented rim plates, welds, hazard arcs, loose wiring into a junction box, crystal slice inlays and hub, the pointer and a gem-pip HP bar.

**Palette.**
- World: soot navy, rust, oily teal-grey and concrete.
- Digital: cyan `#3ff0ff`, gold `#e8b030`/`#ffc830`, magenta `#ff2fb0`, acid `#8cff2a`, and fight red `#ff4a5a`.

**Godot.**
- The world uses the E recipe: painted sprites, a two-tone toon shader and ink outlines.
- The digital layer is flat-shaded `MeshInstance2D`/`Polygon2D` triangle sets. Each triangle carries a tone index into a per-colour three-step ramp, with no outline shader.
- Glow comes from HDR 2D plus a glow pass.
- The contrast between inked painted props and unlined crystal UI is the readability rule: anything you can click is crystal.
