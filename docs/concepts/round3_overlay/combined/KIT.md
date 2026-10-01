# Combined overlay kit (as built)

Four materials sit over the Cv2 base, and each has one job:
- **Spray (B): verbs and headlines.** SEND IT, BUY, LEAVE, HIT THIS and UPGRADE OR DIE. Each has a pink face, a white offset key and a black shadow, with overspray and glossy drips. The full stencil cuts (bridges and the horizontal slice) are used only on these big words.
- **Vinyl stickers (C): objects.** The crew ID and Heat poster have holo foil. The kraft note card carries grease-pencil text that was written before it was stuck down. The price dots and the house-rule card are white vinyl.
- **Grease pencil on glass (A): plans and marks.** Yellow is for plan and route (route, waypoints, OURS, THIS ONE!). Red is for threat and target (circles, HIT IT, THEM, range rings, the printed reticle).
- **Light spill (D): a base layer, not an overlay.** Bright, saturated emitters inside chosen regions (the spinner rims, the VS crystal, the MODEM / CYBER SHOP sign, the chip icons, the city neon) light the facets around them. It uses D's projected-light model and tonemap shoulder, applied to the added light only.

**Layer order (enforced in code):**
1. The base.
2. Light spill (into the base).
3. Pencil, with its 4–6 px cast shadow, then the glass. Compared with A, the glass has a stronger sheen band, a finger print and a palm wipe smudge.
4. Stickers.
5. Spray.

**Marks per screen:**
- **Combat (4):** SEND IT, the target on slice 6, the note card, the crew ID.
- **City (6):** the route, the target ring with HIT THIS, OURS, THEM, the Heat poster.
- **Shop (5):** UPGRADE OR DIE on the house card, the price dots, THIS ONE!, BUY, LEAVE.

**Colours:** pink, white, black, yellow, red, kraft, holo. The sticker library's coral, teal and yellow are remapped to the kit's red, pink and yellow at import.

**Old base marks:**
- The combat tape is inpainted away.
- The BUY/SELL/TRADE stickers are covered by washed PURCHASE and EXIT buttons.
- The "UPGRADE OR DIE!" scrawl is covered by the house-rule sticker, and the headline is re-sprayed over the sticker.
- EXECUTE is drawn as a washed button under SEND IT and stays readable.

## Godot build
- **One CanvasLayer per material, in z order**, plus spill in the base `CanvasLayer`. Overlay layers never write game state; they listen for view signals (screen enter / idle / exit).
- **Spill:** use `PointLight2D` with a blurred emitter-mask texture for each glowing base element, on a light mask that hits only the base layer. Alternatively, use one additive multiply pass driven by a pre-baked emitter mask for each screen.
- **Pencil:**
  - Strokes are `Line2D` or meshes with arc-length UVs, using A's lit wax shader.
  - A `progress` uniform drives the write-on, a band uniform drives the idle glint, and a screen-space smear shader drives the exit.
  - The glass is a full-screen sheen, smudge and band texture.
- **Stickers:**
  - Baked albedo plus an RGB mask (holo, die-cut, gloss).
  - The holo and curl shaders are C's, with `fold` driving the idle flutter (0.08↔0.20) and the peel (→0.6).
  - The slap is a tween on scale, squash and shadow lift.
- **Spray:**
  - The stencil is an SDF or alpha mask. The spray shader takes a `reveal` sweep, a blue-noise speckle and an SDF halo.
  - Drips are `Line2D` strips with stepped length tweens.
  - The exit is B's solvent-wipe shader: UV offset along the wipe, streak multiply, wet runs.
- **Content and timing:**
  - Timings, colours, words and marks per screen come from content `.tres` files.
  - Randomness (jitter, drip picks) comes from a seeded `RngService` view stream.
  - The appear, idle and exit beats register as skippable motion helpers.

Scripts are in `scripts/`. Run `python scripts/build_all.py`. They import the A, B and C libraries in place from their concept folders, and load D's `lightpen.py` by file path.
