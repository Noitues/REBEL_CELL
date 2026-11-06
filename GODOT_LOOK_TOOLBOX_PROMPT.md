# Prompt: REBEL_CELL Godot look toolbox (`addons/rc_look`)

Paste everything below the line into a new Claude Code session. Its first step creates its own worktree
(`D:/rc_art/godot_look_toolbox`).

---

You are the **look-toolbox** session for REBEL_CELL, a cyberpunk roguelite deckbuilder in Godot 4.7 / GDScript
(Forward+). Your job is to build a reusable Godot library, `addons/rc_look/`, that gets high-quality results in Godot
for the visual building blocks many views share. Our Blender renders (the golden plates) and concept sheets look much
better than what Godot shows today. The usual cause is that each view re-invented its own shader or pencil code, and
none of them got enough work. You own making those building blocks good once, so every view gets them.

## Where you work and what you may touch

- **Workspace:** your own worktree. Other sessions work in `D:/rc_art/godot_look*` clones, so never switch a branch in
  a folder you didn't create. Run `git -C D:/rc_art/godot_look worktree add D:/rc_art/godot_look_toolbox -b
  art/look-toolbox art/look`, work only in `D:/rc_art/godot_look_toolbox`, and import there first. Commit there. Pushes are
  disabled. When a module is ready, the art-pass session (`D:/rc_art/art-pass`) reviews it and merges it into `art/look`.
  Build gets it from `art/look` through the mailbox, as now.
- **Read only:** `D:/Godot/rebel_cell` (main). Never write there.
- **Art only.** No game rules, no content ids, no save data, no new mechanics. Any hook the game reads must keep working,
  with a test: highlight states, the city clock, hover, VfxTier, reduce motion, colourblind and high contrast. That
  includes `ui_motion_data`. If a rules question comes up, write it down for the art-pass session; don't decide it.
- **Files:** follow `CLAUDE.md`. Static typing, one class per file, `class_name`, `##` docs, no magic numbers (tuning goes
  in `.tres` config resources). Views signal up and never change state. Any random jitter in GDScript (stroke wobble,
  dropouts, facet tone) comes from a seed you pass in, or from a hash. Never call global `randf()`/`randi()`.
- **Machine rules:**
  - Use the D: drive only. Scratch goes to `D:/rc_scratch/rc_look/`.
  - Import first: `godot --headless --path . --import`. Redirect Godot output to a file; never pipe it.
  - Never run `python -`.
  - Anything that needs a real window goes through `python tools/run_windowed.py --log <file> -- <args>`.
  - Use Blender headless only, and only with the GPU lock. Never touch the designer's open Blender or its MCP.
  - Kill only PIDs you started. Never use `taskkill /IM`.
- **Done gate for every commit that changes code:**
  - the full suite: `python tools/run_tests.py -j 4`;
  - the schema smoke test: `godot --headless --path . -s tools/schema_smoke_test.gd`;
  - content validation: `godot --headless --path . -s tools/validate_content.gd`.

  New test scripts go into `tests/test_manifest.json` with their tier.
- **Token lanes:** mechanical sweeps and file inventories go to Haiku subagents, and real Godot runs and capture loops to
  Sonnet. Keep Opus for look decisions and for reviewing sheets. Name the lane each time you spawn a subagent.

## Read first

1. `docs/ART_BIBLE.md` §1.2, *The media and their jobs* (LOCKED). It is the spec for every module below. Also read §2
   (palette tokens, corp palettes, heat colours, typography) and §5 (accessibility, VfxTier, reduce motion).
2. `D:/rc_art/art-pass/docs/concepts/DIRECTION_REVIEW.md`. Its newer rulings beat the bible: for example, the nudge lock
   is a red grease-pencil 🚫, and jack-in has no wheel.
3. `D:/rc_art/art-pass/docs/concepts/LOOK_PORT.md`, especially §3 (the reachable twin: Cycles feature → Godot
   equivalent), §4 (the parity harness) and §6 (the look code map).
4. `D:/rc_art/art-pass/docs/concepts/golden_plates/INDEX.md`, plus the plates themselves (`*.png`, `*_values.json`,
   `*_id.png`).
5. The current code:
   - `shaders/` (lib, kit, city, street_r2, fx, chrome, wheel, arena);
   - `scripts/ui/kit/` (all the `*pencil*`, `route_ink`, `hand_marks`, `sticker_*`, `terminal_*`, `paper_*`, `*holo*` files);
   - `scripts/ui/fx/` (bits, sticker seam, vfx_tier);
   - `scripts/netrun_art/street_r2_*`;
   - `scripts/city3d/city_materials.gd`, `city_mesh_kit.gd`, `city_lod.gd`.

## Initial scope: the modules

Each module gets the following:
- a public API documented in `addons/rc_look/README.md`;
- config resources for every number;
- a **lab scene** (`addons/rc_look/lab/<module>_lab.tscn`) that shows it at day/night, at every VfxTier, and in reduce
  motion;
- tests;
- a **parity or reference sheet** against the matching plate or concept sheet.

### A. Foundation
1. **Shared shader library and tokens.**
   - Grow `shaders/lib/rc_common.gdshaderinc` into the toolbox's include set: colour space, hash/noise, triangle facet
     ids, screen-space helpers, time from the netrun/city clock.
   - Make the ART_BIBLE §2 palette, corp palettes, heat and class colours global shader parameters, generated from one
     `.tres` so GDScript and shaders never drift.
2. **Quality and tier layer.**
   - One place maps VfxTier, reduce motion, colourblind and high contrast to each module's settings.
   - Every module reads it, and no module checks the tier on its own.
3. **Look lab and parity harness integration.**
   - A gallery scene that loads any module on a neutral test set.
   - Wire `tools/visual_qa` (capture_pack, contact_sheet) and the LOOK_PORT §4 sheet (golden | twin | Godot, region
     numbers) so any module can produce `D:/rc_scratch/look_parity/<module>_<sha>/sheet.png` + `values.json` with one
     command.
   - Numbers alone never pass. Every sheet also gets a §1.2 read.

### B. World medium (Cv2 low-poly + E cel shading)
4. **Toon shading.**
   - 3 hard bands (`toon_bands.gdshaderinc`) and per-triangle tone jitter for the Cv2 facet look.
   - Grime and dirt masks, and corp material tone.
   - One material family that city, street, HQ, combat backdrop and busts all use.
5. **Ink lines.**
   - Wobbly lines from id, normal and depth edges, as a post `CompositorEffect` that reads an id buffer (`id_flat`), plus
     the hull fallback (`toon_ink_hull`).
   - Line weight by distance, a day/night ink colour, and no lines on glow.
6. **Light spill, glow and bloom.**
   - Emissive spill onto walls and streets (`light_spill`, `city_glow*`, `city_pool*`, `spot_pool`).
   - The faked emissive bounce from LOOK_PORT §3.
   - The hierarchy of light (corp beams > signs > windows > street) as named presets.
7. **Atmosphere.**
   - Depth haze layers and `FogVolume` with baked density textures.
   - Fog-only lights (low `light_energy`, high `light_volumetric_fog_energy`).
   - Narrow beams (`beam_shaft`, `city_beam`), with the cone-mesh fallback where volumetric resolution can't hold 1°.
   - Night rain (streaks, splashes, wet darkening).
8. **Wet ground and water.**
   - Wet street with SSR plus reflection probe placement rules (`wet_street`, `street_r2_surface`).
   - Puddles, neon reflections and water (`city_water*`, caustics, shore foam).
9. **Post chain.**
   - Port the Python `post_aaa` "real" / `hq_post` as one CompositorEffect chain, exact to 1/255 on a fixed linear input
     (LOOK_PORT L3).
   - Grade, tilt-shift/DOF (`city_tilt_shift`, `city_post`, `route_grade`), and the heat glitch and CRT overlays as
     optional stages.

### C. Street view layers
10. **Street-view layer system.**
    - Stacked depth layers for the netrun street and route views: foreground frontage, mid street, back skyline, sky.
    - Each layer has its own fog, ink weight, light and parallax.
    - One API that `street_r2_builder`, the route view and the HQ approach all use.
11. **Signage and neon.**
    - Sign boards and sign canvas (`street_r2_sign*`, `dress_sign`, `dress_neon`, `holo_billboard`).
    - Neon tube glow with spill, flicker driven by the clock, and diegetic lettering only (no labels baked into the world).

### D. The 2D media (ART_BIBLE §1.2)
12. **Grease pencil.** This is the most important 2D module, and today it is split across `pencil_plan`, `pencil_words`,
    `pencil_note`, `pencil_set`, `raid_pencil*`, `hq_plan_pencil`, `aim_line_pencil`, `nudge_lock_pencil`, `route_ink`
    and `hand_marks`. Make one stroke engine:
    - **Look:** opaque wax (alpha 0.96), thick, a rough edge with dropouts, a sheen line and a dark under-shadow, so it
      reads by day and by night.
    - **Colours:** yellow `#FFE200` (plan / valid) and red `#FF1C2C` (threat / invalid). Solid = what will happen;
      dashed = what-if.
    - **Motion:** it writes on along the path and wipes off with a cloth wipe. It never fades its alpha.
    - **Primitives:** line, arrow, circle, partial circle, 🚫 slash, underline, tick, cross, handwritten word.
    - **Spaces:** screen-space and world-projected (drawn on the 3D city and street, staying on its anchor as the camera
      moves).
    - **Seeded wobble:** the same plan always draws the same stroke.
    - Rule from the bible: no UI ever covers grease pencil, so give it a layer-order guarantee and a test for it.
13. **Vinyl sticker.**
    - Ink keyline, extrude, white die-cut border, gloss 0.22, and one slow sweep on one sticker at a time (a global
      sweep scheduler).
    - Peel, slap and dissolve motion.
    - Merge the two diverging `vinyl_sticker.gdshader` copies (`shaders/kit` and `shaders/chrome`) with `sticker_fill`.
14. **CRT terminal.**
    - Navy glass, cyan edge, 3 px scanlines, faint scrolling hex dump, edge glow, type-on text, `>` caret, and the accent
      per use.
    - Sources: `crt_terminal`, `scanline`, `crt_panel`, `hex_dump`, `typing`.
15. **Corp paper and decrypted holo.**
    - **Paper:** stock, redactions, stamps, seals, clips, polaroid frames (`corp_paper`, `zine_paper`, `rubber_stamp`).
    - **Holo:** about 78 % corp tint, 4 px scanlines, 3–4 slow bands, ±2 px RGB split on the edge only, 0.88 scrim, and
      a cracked seal (`decrypted_holo`, `glass_blur`).
16. **Binary bits FX.**
    - `0`/`1` atlas particles: white-hot for the first 60–100 ms, flipping, tumbling, then pulled along a curve into
      their target.
    - Presets for card dissolve, damage shards, heal inflow, status apply/tick, destruction and jack-in rain
      (`binary_bits`, `bits_atlas`, `bit_path`, `bits_seam`).
    - Bits go round a wheel's rim, never across its face.

### E. Pipeline
17. **Blender → Godot asset path.**
    - GLB import conventions: naming, the material slot → toolbox material mapping, id-colour export for the ink pass,
      LOD and collision flags.
    - An import plugin or post-import script that assigns toolbox materials automatically.
    - The bake helpers (`tools/art_bake`) for anything Godot can't render live: signs, facade atlases.
    - The rule from LOOK_PORT: one geometry source. Godot generates the scene and Blender renders from its
      `plate_inputs`.
18. **Performance budget.**
    - Instancing and LOD helpers (`city_mesh_kit`, `netrun_instance_pack`, `city_lod`).
    - A per-module cost readout in the lab (GPU ms at 1080p on this machine).
    - A rule that every module has a cheap tier.

## How to work

1. **Phase 0, audit (no code changes).** Use a Haiku subagent for the inventory, then write
   `addons/rc_look/AUDIT.md`. For each of the 18 areas it lists:
   - the files that implement it today;
   - which views use it;
   - duplicates and drift between copies;
   - the gap against its plate or concept sheet, shown on a screenshot;
   - a priority by how many views share it × how big the gap is.

   Then post a short ranked order to the art-pass session and wait for the designer's pick before Phase 1.
2. **Foundation first** (modules 1–3), so each later module comes with a lab and a sheet from day one.
3. **Then one module at a time, in the agreed order.** For each module:
   - build it in the lab;
   - make the sheet against the plate or concept;
   - **migrate the existing call sites one view at a time**, so each view looks the same or better at its own parity
     capture;
   - delete the old copy;
   - run the full gate;
   - commit, with the module and criterion in the message.

   Never leave two live implementations.
4. **Where the art comes from:**
   - Lead with the look, not with plumbing. If a module has no strong reference yet, render a concept in Blender
     headless first (the designer judged a past art pass "underwhelming": be bold).
   - The reachable twin (LOOK_PORT §3) is the target wherever Cycles features don't exist in Godot.
   - The designer rules on any gap that's left.
5. **Reporting.**
   - At each module's end, send the art-pass session one message: the sheet path, what changed, which views migrated,
     and the gate result.
   - Show images to the designer with SendUserFile.
   - Log every new config field and public API in `docs/DECISIONS.md` under a LOOK-TOOLBOX entry.

## Out of scope

- Game rules or UI layout.
- New screens.
- The undesigned items in ART_BIBLE §4.14.
- Anything from the bible's "Rejected" list: spray paint and stencils, the dripping marker, ransom collage, ink brush,
  light pen as an overlay, the wireframe net, painterly or neon-painting cities.

## First reply

Read the docs above, then reply with:
- your understanding of the 18 areas in one line each;
- anything in the code map that doesn't fit them (a missed area);
- the Phase 0 plan with its subagent lanes.

Then start Phase 0.
