# R2E-G: Hand-painted toon, gritty

**What's kept from r2e.** The same shapes, surfaces and camera:
- chunky, wonky, bevelled shapes with lighter worn edges;
- thick wobbly Freestyle ink;
- emission-output painted toon shading;
- a diorama on a painted backdrop;
- the same city layout and node/path overlay in 01–03;
- the same wood/metal plaque UI construction.

**What makes it gritty:**
- **City fabric:** mega-blocks are patched together, with older and newer towers stacked on top and rooftop shacks. Walkways and a pipe bridge run between blocks. There are exposed pipe runs, sagging cable bundles and scaffolding. Every roof has AC units, dishes, tanks and antennas.
- **Signs:** stacked vertical signs, some of them dead or flickering, and an "OBEY / COMPLY" eye billboard over the slums. The corp tower is dark glass with an eye logo.
- **The island:** a torn-out slab of concrete strata with hanging broken chunks, rebar, dangling cables and burst pipes. Rubble replaces the grass.
- **Surfaces** (`tt_lib.paint`, grit pass driven by `MODE["grit"]`): vertical rust runs, dark water stains and chipped paint showing a pale undercoat, all from stretched noise bands.
- **Street details:** graffiti tags in Ink Free, and wet asphalt with puddles that carry painted neon reflections at night. There are also trash bags, a dumpster, steam from grates, surveillance cameras on poles and drones with searchlights.
- **Lockdown:** helicopter searchlights, armoured vehicles with red/blue strobes, and concrete barriers with hazard paint.
- **Post** (Pillow): smog bands, painted rain streaks and grain over the backdrop. The day backdrop is a dirty yellow-grey, night is a sooty navy, lockdown is maroon.
- **Combat and shop:**
  - **Spinners:** salvaged hardware. The rim is 28 dented plates with hazard-striped arcs, weld beads and loose wires. The enemy rim is cracked, with a bolted patch plate.
  - **Cards:** worn paper with tape and dog-ears.
  - **Shop:** a stall under a dripping, patched tarp, with corrugated rusty walls and caged shelves. The vendor is a hooded robot with a dead eye. The neon sign has two dead letters, and the prices are scrawled on tape.

**Palette:**
- **Base:** soot navy `#39414f`, rust `#6e4632`, oily teal-grey `#4d5e5e`, stained concrete `#7d776a`.
- **Neon, used sparingly:** sickly magenta `#ff2fb0`, acid green `#8cff2a`, cold cyan `#3ff0ff`, sodium orange `#ff9a2a`.
- **Day:** a smog palette with desaturated lit tones tinted `#cfc08e`.
- **UI and overlay:** they keep a clean, readable palette so they read in every lighting state.

**Godot 2.5D.** Same plan as r2e:
- pre-rendered or hand-painted sprites, a two-tone toon shader and ink outlines;
- grime as an overlay texture: a tileable rust/stain mask multiplied per material;
- rain, smog and neon reflections as screen-space layers (particles for rain, scrolling smog sprites, additive reflection decals);
- lighting states as palette LUT swaps.
