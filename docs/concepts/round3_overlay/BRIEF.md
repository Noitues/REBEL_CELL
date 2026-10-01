# Concept round 3: the overlay medium (shared brief)

## Context (from the designer)
The goal is **polished AAA visuals built from mixed media**.
- **Base layer, now chosen:** the city and everything on the computer use style **C (Cv2)**. That's gritty triangulated low-poly vector: flat facets, no outlines, a dirty palette, harsh sparse neon, rain.
- **What's open:** the medium of the **overlay layer**. This is the Cell's human voice laid *over the screen*.
- **What the overlay used to be:** post-it notes, tape, and dripping pink marker, as if someone wrote on the actual monitor. The designer still likes that idea, but it **didn't read as polished or AAA**.
- **Your job:** propose and render **one alternative medium** for that overlay. It must stay human, handmade and rebellious, and it must sit clearly *on top of* the digital Cv2 world. It must also look premium and deliberately art-directed, like a shipped AAA title. Think of how Persona 5's collage, Hi-Fi Rush's cel/comic layer or Splinter Cell's planning screens sit over their games.

## The base images (use these exactly; don't re-render the base)
Paths are relative to `C:\Users\noitu\Documents\Godot\rebel_cell\.claude\worktrees\art-pass\`:
1. `docs/concepts/round2/r2c_geo_vector_gritty/stills/04_combat.png`: combat (two spinners, card hand, GO).
2. `docs/concepts/round2/r2c_geo_vector_gritty/stills/02_city_night.png`: the city map at night (nodes, paths).
3. `docs/concepts/round2/r2c_v2_modem/modem_shop.png`: the MODEM shop.

**These bases already contain some overlay elements** (e.g. the "UPGRADE OR DIE!" scrawl, BUY/SELL/TRADE stickers, taped prices). Where an element belongs to the overlay, **paint your medium's version over it, or cover and replace it.** You can lightly darken or desaturate the base under your overlay so it reads, but never repaint the base itself.

## The overlay elements to show (all in YOUR medium)
On **combat**:
- **The main verb:** "SEND IT" written over a washed-out digital "EXECUTE" button. This is the signature move: the human writes over the machine.
- **A target annotation** on the enemy spinner: a circle or arrow, with a short word like "NOW" or "HIT IT".
- **A tactical note:** a small 2–3 line human note somewhere sensible.
- **A crew photo slot:** the operative's portrait, in your medium's version of a Polaroid or ID.

On the **city map**:
- Mark the target node ("HIT THIS"), mark our home ("OURS"), draw an arrow along the planned path, and add a warning near a threat ("THEM").
- A **Heat poster/tag**: Heat 62, FLAGGED.

On the **shop**:
- Circle one card with "THIS ONE!".
- Your medium's version of the price tags.
- The shop's verbs: "BUY" over "PURCHASE", and "LEAVE" over "EXIT".

**Plus a 4th image:** `04_lifecycle.png`, a 3-panel strip of the verb's motion in your medium:
1. Appearing (being written, sprayed, stuck on, projected…).
2. Idle while waiting for the player (a subtle living motion: drip, flutter, shimmer…).
3. Leaving as the page transitions.

## Quality bar
- AAA polish: confident shapes, deliberate typography or lettering, a controlled palette, and real material response (light, gloss, paper, ink density). No clip-art feel.
- **Readability first:** the overlay must never hide spinner values, node icons or prices.
- **Contrast with the base:** the overlay should feel like a different *material* from the faceted digital world.
- **Restraint:** about 3–6 overlay marks per screen, not everywhere.
- **Originality:** no IP logos, characters or real brands.

## Tools
Windows. Use Pillow, and Blender 5.2 headless if your medium benefits from real lighting:
- Run Blender as `"C:\Program Files\Blender Foundation\Blender 5.2\blender.exe" -b --factory-startup --python x.py`. Redirect output to a log file, wrap it in `timeout 900`, and don't use the Blender MCP.
- Write `.py` files and run them. **Never run `python -`.**
- Use seeded randomness.
- Keep your scratch files in your own subfolder of the scratchpad.

Blender 5.2 tips:
- Grease Pencil v3: set `layer.use_lights=False`.
- Compositor: use `scene.compositing_node_group` with a `NodeGroupOutput`.
- Glare type is a socket.
- Use absolute paths.

## Output
Put everything in your own folder: `docs/concepts/round3_overlay/<slug>/`.
- `01_combat.png`, `02_city.png`, `03_shop.png`, `04_lifecycle.png` (1920×1080)
- `contact_sheet.jpg`
- `scripts/`
- `MEDIUM.md` (half a page): the medium, its palette, its lettering approach, how it reads as AAA, how you'd build it in Godot 2D (textures, shaders, animation), and its risks

Keep it under about 25 MB. Don't touch other folders or game files.

## Report (under 150 words)
Your folder, what the medium is, what worked, and what didn't.
