# Round 13: wheel frame details

This round settles the **frame** around the locked parts: the C "Screens & Data" slices (round 11), the V2 telemetry ring and the round 11 HP arc. Slice content (glyphs, tiers, states) is not touched here; that work is in `round13_slice_system/`.

## Files
| File | What it shows |
|---|---|
| `d1.png` … `d4.png` | One 1920×1080 sheet per version. Each sheet has the player hero (r = 220), the boss, a close-up of the active slice under the pointer, r = 60 player and boss, greyscale, and notes. `d3.png` also has the 3-frame parallax strip. |
| `compare.jpg` | The four heroes (top row) and the four bosses (bottom row), side by side at the same size. |
| `combat_d3.png`, `combat_d4.png` | The night Manifest fight (round 11 layout, HUD and overlay), using the two best frames for both wheels. |
| `scripts/` | Everything needed to rebuild. |

**Rebuild:** `python scripts/make_sheets.py all`, then `python scripts/make_sheets.py combat d3 d4`. Renders are cached in `scratch/r` (git-ignored); to re-render, run `python scripts/clear_cache.py all` (it removes `scratch/` only). `scripts/t_quick.py` is a fast ss=1 preview of the player and the boss.
- New files: `frames.py` (the four frames) and `make_sheets.py`.
- The round 11 scripts are copied unchanged, except:
  - `slicelib.render_slice` has a `defer_icons` option. It returns the upright glyph/value block instead of pasting it, so a frame can draw a needle under the block or lift the slice with its block.
  - `make_combat.py` is parameterised: it takes frame meta (pointer and HP radii), sets the wheel sizes to player r = 220 and boss r = 236, and reads round 11's backdrop cache read-only.

**What the wheel must say (art_asset E1):** whose wheel it is (bezel), which slice is under the needle and its value (the most important read), the HP, the inner ring and the hub. Each version below is judged on the under-pointer read first.

---

## D1 Blade & window
- **Under the pointer.** A cream notched blade comes down from outside the rim; its tip bites into the slice's outer bezel. Its dark window shows the live value (white digits, a program-colour glow and a program-colour pip strip). The active slice is scaled 6.5 % about the centre, so it rides over the telemetry ring, with a cream outline, a program-colour halo and a cast shadow. The other five slices are dimmed to 66 %. The value reads twice, and the lift says which slice even with no colour.
- **At r = 60.** The blade is scaled ×1.55 in LOD, so the window still shows "12" (about 9 px). The lifted, outlined slice is the strongest r = 60 read of the four.
- **Greyscale.** Excellent. The read comes from lift, outline and dimming, not hue.
- **Boss.** (1) The nameplate banner **is** the blade's mount: the blade hangs from a notch under it, with struts down to the bezel. (2) A bolted armour band with hazard chamfers, plus corp crest lugs at 3 and 9 o'clock. (3) A crowned orange blade with a red "HITS YOU" tab. Phase pips stay on the HP arc.
- **Godot.**
  - The wheel is a `Node2D` with a rotating `Slices` child: 6 `Polygon2D` screen shaders, plus counter-rotated glyph `Sprite2D`s.
  - The active slice is reparented, or z-raised, to a `Lifted` node, then tweened `scale` 1.0→1.065 with `modulate` on the others.
  - The outline is a `Line2D` on the wedge polygon. The shadow is a `CanvasGroup` copy, offset, with `modulate` black at alpha 0.6 (or a blurred-alpha shader).
  - The blade is a static `Sprite2D` (9-slice not needed) with a `Label` in the window.
  - The boss banner is a separate `Sprite2D` parent of the blade.

## D2 Instrument readout
- **Under the pointer.** A long gauge needle runs from a collar around the hub out over the 30-tick scale.
  - It is bold off the glass, a hairline across the slice screen, and passes **under** the glyph/value block, so it never cuts a number.
  - The active slice gets white instrument corner brackets and a lit program-colour hairline.
  - The hub is a CRT readout: program name, glyph and big value, then kind and aim pips ("ZERO-DAY / 12 / CRIT ●●●"). This is the accessibility second read and is very clear.
  - The needle also marks the live inner-ring segment.
- **At r = 60.** The weakest pointer of the four: the needle is a thin line. The hub collapses to the value only, which does survive (about 12 px).
- **Greyscale.** Good at hero size: the brackets and hub text carry it. Small sizes lose the needle against the slice.
- **Boss.**
  - (1) A counter-rotating red threat ring of chevrons, with hollow "NEXT" needle marks that telegraph migrate/multiply positions (E1 "telegraphed next").
  - (2) The hub readout turns hostile ("ATK > YOU" in red) over a faint corp watermark.
  - (3) An ambient corp-colour radar sweep across the face.
  - The standard round 11 banner and phase pips stay.
- **Godot.**
  - The tick scale is one texture on the rotating node.
  - The needle is a `Sprite2D` on a static pivot node, with its middle third at alpha 0.85.
  - Draw order puts the slice screens, then the needle, then the glyph blocks, so the glyphs need their own `CanvasLayer` or z_index above the needle.
  - The hub CRT is a `SubViewport` or just `Label`s plus a scanline shader.
  - The radar sweep is a fragment shader (conic gradient, `TIME`) on a `ColorRect` masked to the disc.
  - The threat ring is a `Sprite2D` with negative rotation speed.

## D3 Layered stack
- **Under the pointer.** The pointer is a physical part:
  - a steel arm with a program-colour tip;
  - a counterweight outside the rim;
  - a pivot housing with a **split-flap counter** showing the value, plus program-colour indicator lamps.

  A lamp in the housing spotlights the active slice (×1.08 plus a warm cone). The other slices sit at 70 %, in the shadow of the bezel lip.
- **Depth.**
  - A machined bezel (numpy height-profile shading: inner lip that overhangs the disc, a glass telemetry channel, outer bead with screws) casts a real offset shadow onto the recessed disc.
  - The raised hub (with machined rim) casts its own shadow.
  - A glass dome adds a crescent, a band and a spark.
  - Parallax depths: disc −6, bezel 0, hub +5, pointer +10, glass sheen −14 (moves against the tilt). The strip shows spin (with rotational blur, tilt left), slowing (centred) and landed (tilt right).
- **At r = 60.** The pointer and split-flap are scaled ×1.5. The value is about 7 px, decorative only. The spotlight contrast still marks the slice, and the bezel stays a nice solid silhouette.
- **Greyscale.** Good: the shading is all value contrast. The spotlight-vs-shadow read survives.
- **Boss.** (1) A riveted armour collar outside the machined bezel. (2) Embossed corp crest bosses at 3 and 9 o'clock. (3) An orange-anodised bezel and a longer pointer. The round 11 banner and phase pips stay.
- **Godot.**
  - Bake the bezel, armour and hub rim as `Sprite2D`s (Blender or this numpy shader), with a normal map if live light is wanted.
  - Build it as stacked `Node2D` layers, each with `position = tilt * depth` (tilt from spin velocity or the mouse), lerped.
  - Shadows: a `CanvasGroup` per raised layer with a shadow-copy child (offset, black, `modulate.a` 0.6) and a blur shader, or one shared "drop shadow" shader that samples the alpha at an offset.
  - Glass is an additive `Sprite2D` with its own offset.
  - The split-flap is two `Label`s plus a flip tween (scale.y through 0) on value change.
  - This is the costliest version, about +3 draw layers per wheel.

## D4 Lens & rail (my own)
- **Idea.** Keep D1's unbeatable read, borrow D3's physicality only where it is cheap, and make the locked telemetry ring do work.
  - Over the pointer, ±50° of the V2 ring becomes the **active slice's readout rail**: tinted with the program colour and bracketed, scrolling "ZERO-DAY 12 // CRIT // PERFECT //" in white. The rest of the ring keeps scrolling class/corp telemetry.
  - The blade is a slightly smaller D1 blade rooted in the bezel. The slice lift is gentler (2.5 %), so the rail stays visible. Other slices are dimmed to 68 %.
  - The bezel is a D3-lite machined profile with a glass channel, lip shadow on the disc, hub shadow and a glass crescent. No screws or second layer stack.
- **Under the pointer.** The value reads three times (blade window, slice, rail), and the slice name is spelled out on the rail, so the hub stays free for name, core and the inner ring.
- **At r = 60.** The rail becomes a solid colour arc over the pointer, which is a great "this one" mark at a glance. The blade is scaled ×1.6, and the hub shows the HP number (borrowed from round 4's W-D, useful for multi-enemy small wheels).
- **Greyscale.** Very good: lift, dimming, the bright rail band and the cream blade are all value-based.
- **Boss.** (1) The nameplate banner as the blade mount, with a crowned orange blade. (2) A counter-rotating threat ring with NEXT needle telegraphs (from D2). (3) Corp crest lugs on the threat ring. Phase pips stay on the HP arc.
- **Godot.** D1's node setup, plus:
  - Rail: the telemetry ring is already a scrolling text shader (or `Label`s on a path). Add a second masked arc (`Polygon2D` + shader with `rail_half_angle` and `rail_colour` uniforms) that is static under the pointer. Its text is set from the forecast data the Forecast tag already has.
  - Bezel: one baked sprite plus one shadow sprite.
  - Threat ring: as in D2.

---

## Recommendation
**D4 Lens & rail** as the shipping frame.
- It keeps D1's under-pointer read (the strongest at every size and in greyscale).
- It turns the designer-approved telemetry ring into a second, *named* read without adding a new widget.
- It costs little more than D1 in Godot.

**D3 Layered stack** is the hero-quality runner-up. If the budget allows, its machined bezel shading and the split-flap counter can be layered onto D4 for bosses only, where "heavier hardware" is itself the boss signal.

D2's hub readout is the best accessibility read. Keep it as an **option** (Settings: "hub shows slice value"), because in D4 the hub carries name, core and ring.

## Weakest parts / open
- **D2 needle at small sizes:** too thin, and it disappears into busy slice screens. Its r = 60 read depends on the hub.
- **D3 split-flap at r = 60:** decorative only.
- **D4's rail text** is 14 px mono at hero size. It is readable, but it competes with the scrolling telemetry next to it. Scroll speed should differ (rail static, rest scrolling).
- **Boss banners as blade mounts (D1/D4)** sit high. In combat they reach into the top HUD band, so a shorter banner (one line) may be needed at 1080p.
- **The yellow grease loop in `combat_d4`** circles the blade window and clips the banner's subtitle. With a banner-mounted blade, the loop should sit below the banner, or be replaced by a short arrow.
- **The D3 pointer arm** is mostly hidden by its housing at hero size, so only the tip shows. The arm reads as a pin rather than a lever. A longer arm or a lower housing would fix it.
- **The D3 parallax strip** is exaggerated ×2.2 for legibility. At real depths the shift is 3–6 px at r = 220.
- **The lifted slice overlaps the V2 ring** by about 15 px in D1, which hides part of the readout over the pointer. D4 avoids this with a gentler lift.
