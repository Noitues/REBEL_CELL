# Concept round 2: style-reference brief (shared by all five agents)

## The game (this is all you need to know about it)
A **cyberpunk roguelite deckbuilder**. You play a hacker cell fighting corporations in a neon megacity.
- **Combat:** fights resolve on round **spinners**: wheels split into coloured slices, spun by playing **cards** from a hand. It's two spinners facing off, yours and the enemy's, each with a pointer and a health bar.
- **Campaign:** you move across a **wide shot of the city**, travelling between **nodes** (targets and sites) along **paths**. Your hacking raises the city's **suspicion**, and the city reacts.
- **Shop:** a black-market shop sells cards and spinner parts.
- **Mood:** cyberpunk. Neon, the net, hacking, corporations, surveillance.

There's no art bible for this round. **Your style comes from one reference image** (given in your prompt). Mimic its rendering: its shapes, surface treatment, palette logic, lighting, edge quality and level of detail. Translate it to this cyberpunk world. Don't copy the reference's subject.

## Deliverables: 5 stills, 1920×1080 PNG
The **same city** (same layout, same landmark buildings, same camera) appears in the first three stills:
1. `01_city_day.png`: a wide shot of the city in daytime, with the **node-and-path navigation overlay** on it. The nodes are clear markers; the paths join them and lie on the same plane as the nodes. One node is highlighted as "you are here".
2. `02_city_night.png`: the same city and overlay at night. Neon, lit windows, traffic.
3. `03_city_suspicion.png`: the same city at night under **high suspicion**. Searchlights, drones or helicopters, alarm lighting, and a tense colour shift.
4. `04_combat.png`: the combat screen.
   - Two **spinners** facing off: slices, a pointer, a health bar under each.
   - A hand of **cards** along the bottom.
   - A readable "go" button.
   - The city is visible behind, pushed back so the spinners dominate.
5. `05_shop.png`: the black-market shop screen. Cards and spinner parts for sale with prices, a shop sign, and a way to leave.

It has to read as a game: the UI elements (spinners, cards, buttons, nodes, prices) are clear, while carrying the style fully. Invent the UI's look in your style too.

## Tools (Windows; these rules matter)
**Blender 5.2 LTS, headless.** Run:

`"C:\Program Files\Blender Foundation\Blender 5.2\blender.exe" -b --factory-startup --python <script.py> -- <args>`

Always redirect output to a log file and wrap the run in `timeout 900`; never pipe it. **Don't use the Blender MCP tools**: that's a shared live Blender, and five agents would collide on it.

**Blender 5.2 gotchas** (learned in round 1):
- **Engine:** read the valid `scene.render.engine` ids at runtime. EEVEE is `BLENDER_EEVEE`.
- **Compositor:**
  - `scene.compositing_node_group` needs a `CompositorNodeTree` and a `NodeGroupOutput`; there's no `CompositorNodeComposite`.
  - Glare's "Type" is an input socket or menu, e.g. `inputs["Type"] = "Bloom"`.
- **Grease Pencil v3:** `bpy.data.grease_pencils.new` → `layers.new` → `frames.new(1).drawing.add_strokes([n])`.
  - Set `layer.use_lights = False`, or strokes render dark.
  - Fills need a non-zero `fill_id`.
  - Create attributes before `foreach_set`.
  - Grease Pencil isn't depth-tested against meshes, and it ignores camera depth of field.
- **Colour:** AgX washes out saturated emission. Setting `view_transform = 'Standard'` works even though RNA only lists 'NONE'.
- **Lights and fog:** many point lights overflow the EEVEE shadow pool, so turn shadows off on minor lights. A world volume dims the sun on every surface, so use bounded fog boxes instead.
- **Paths:** use absolute output paths (`//` fails headless). `matrix_world` isn't updated until `view_layer.update()`.
- **Post-processing:** use Pillow (no numpy): write `.py` files and run them with `python file.py`. **Never run `python -`**, because it hangs the shell.
- **Scratch files:** the shared scratchpad folder is used by other agents too, so keep yours in your own subfolder.

**Your choice of method:** real 3D meshes, Grease Pencil, shaders, compositing, and a Pillow post-pass, whatever best matches your reference. Use seeded randomness only. All designs must be original: no existing IP, logos or characters.

## Output
Your own folder is `docs/concepts/round2/<your_slug>/` under `C:\Users\noitu\Documents\Godot\rebel_cell\.claude\worktrees\art-pass\`. It holds:
- `stills/` with the five PNGs;
- `contact_sheet.jpg` with labels;
- `scripts/` with everything, runnable;
- `STYLE.md` (half a page): how you translated the reference, the palette, the technique, and how you'd build it in a 2D/2.5D Godot game.

Stay under about 30 MB, and delete intermediates. Never touch game files or other folders.

## Report (under 200 words)
- your folder;
- what each still shows;
- how faithful you were to the reference;
- what didn't work.
