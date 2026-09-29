# Concept round: shared brief (all five agents)

You're a concept artist and art director for **REBEL_CELL**, a 2D cyberpunk roguelite deckbuilder. Combat resolves on spinning 30-tick wheels, called "spinners". Between fights, a campaign plays out on a neon city grid with Heat, raids and a cyberdeck HQ. The Cell's own voice is a punk zine: marker, stickers and tape. The system around it is cold glass terminal UI. The city watches you.

Each of the five agents renders the **same subjects** in a **different style**, so the designer can compare directions. You're not writing game code. You're writing Blender Python scripts that paint concept stills.

## Read first (all paths are relative to `C:\Users\noitu\Documents\Godot\rebel_cell\.claude\worktrees\art-pass\`)
1. `docs/ART_FEEDBACK_R2.md`: the designer's feedback. **Every still must answer the items that apply to it.**
2. `docs/ART_BIBLE.md`: §1 north star, §2 materials, §3 palette, §7 characters, §9 city. The palette and pillars are a starting point; your style may push them.
3. The current game, to see what you're improving on:
   - `docs/art_review/FINAL/gallery/*.jpg` (before | after)
   - `docs/art_review/FINAL/sheets/combo_1.0_mouse_re-off_none.jpg`
   - the **original Modem sign** the designer likes: `docs/art_review/W10/baseline/1.0_mouse/modem.jpg`.

## Tools (Windows)
- **Blender 5.2 LTS**, headless: `"C:\Program Files\Blender Foundation\Blender 5.2\blender.exe" -b --factory-startup --python <script.py> -- <args>`.
  - Always redirect output to a log file and wrap the command in `timeout 900`. Never pipe it.
  - **Don't use the Blender MCP tools.** That's one shared live Blender, and five agents would collide on it.
- **Grease Pencil** is the v3 API (Blender 4.3+): `bpy.data.grease_pencils` / GreasePencil v3 layers → frames → drawing → strokes/points. The API changed from 4.x v2, so **probe it first** with a tiny script that prints `dir()` of the objects and writes a test PNG, then build up from there.
  - Mix Grease Pencil strokes with meshes, emission materials, lights, volumes and the compositor as your style needs.
- **Render engine:** EEVEE (`scene.render.engine`: read the valid ids at runtime; in 5.x EEVEE is `BLENDER_EEVEE`). Add bloom/glare in the compositor. If EEVEE fails headless, fall back to Cycles on the GPU at a low sample count, or to Workbench for line work.
- **Output:** 1920×1080 PNG. Keep renders fast, at low samples.
- **Post-processing:** Python with Pillow is available, e.g. contact sheets or a subtle grain pass. Write `.py` files and run them with `python file.py`. **Never run `python -`**, because it hangs the shell.
- **Randomness:** seeded only (`random.Random(seed)`), so reruns match.
- **IP:** original designs only. Never copy characters, logos or signs from any existing IP.

## Deliverables, in your own folder `docs/concepts/<your_slug>/` (don't touch anyone else's folder or any game file)
1. **`DIRECTION.md`**, one page:
   - name and one-line pitch
   - three visual pillars
   - palette with hex values and roles
   - materials and layering
   - lighting, including how glows spill onto neighbours (feedback 10)
   - motion ideas: marker write-on and drips (6), sticker slaps (8), binary damage shards (5), heat glitch (11)
   - **how the spinners get depth** (4): give 3–5 concrete techniques
   - how it answers each of feedback items 2–11
   - what it would take to build in Godot 4.7 2D/2.5D (shaders, layers, pre-rendered sprites vs real-time)
   - its risks
2. **`stills/`**, these five PNGs at 1920×1080:
   1. `01_combat.png`: a fight.
      - Two spinners, the operative's and an enemy's, that feel **3D and layered**: bezel, glass, inner rings, depth and shadow.
      - The city behind is **desaturated and receding** (feedback 3).
      - A hit throwing off **binary 0/1 shards** (5).
      - A hand of cards **slapped on as stickers** (8).
      - Marker **SEND IT scrawled over a washed-out digital EXECUTE** (9).
      - Glows spilling light onto nearby UI (10).
   2. `02_city_night.png`: the city grid at night.
      - Elevated multi-level highways with traffic and flying vehicles (7.5).
      - Projected hologram billboards with illegible text (7.6).
      - Patchy fog with varying blur (7.2), and ortho **tilt-shift** blur with distance (7.3).
      - Grid nodes and link lines **on one plane** (7.4).
      - The HQ tower **fully framed, not cut off** (7.1).
   3. `03_heat.png`: the same city at high Heat. Helicopters, searchlights, drones, and a screen-wide heat glitch/flicker (7.7, 11).
   4. `04_hq_modem.png`: the cyberdeck HQ or the Modem shop.
      - If you pick the Modem, keep the spirit of the **original** vertical MODEM / CYBER SHOP neon sign, as your own original redraw (2).
      - Include zine stickers and marker on the glass UI.
   5. `05_marker_strip.png`: a 3-panel strip of the marker's life (6):
      1. the words writing on;
      2. drips forming and pausing;
      3. drips running down the screen as the page leaves.
3. **`scripts/`**: every Blender and Pillow script you used, runnable.
4. **`contact_sheet.jpg`**: all five stills with labels.

**Budget:** your folder stays under about 40 MB. Delete intermediates. Disk has about 20 GB free; don't fill it.

## Report back (under 250 words)
- your folder path
- the style name and pitch
- what each still shows
- which feedback items you nailed or couldn't
- the Blender API gotchas you hit (so the other agents and the implementation can reuse them)
