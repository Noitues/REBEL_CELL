# Boss wheel polish session: hand-off prompt

Use this to start a dedicated session that brings ONE boss wheel to shipping visual polish. Run it once per wheel: Roman "The Pantheon", then Atlantis "The Tank".

---

You are the lead artist for one REBEL_CELL boss wheel. Your task is to take its approved design to AAA visual polish. The design and its mechanic are LOCKED; the execution is not.

## Workspace
- Art-pass worktree: `C:\Users\noitu\Documents\Godot\rebel_cell\.claude\worktrees\art-pass` (branch `art-pass`).
- Write under `docs/concepts/boss_wheel_polish/<boss>/`.
- Heavy scratch goes in `D:\rc_scratch\boss_polish_<boss>\`. C: is low on disk.
- `D:\Godot\rebel_cell` (main) is READ-ONLY.
- Commit small and often on art-pass with explicit `git add` paths, and push.
- Commit trailer: `Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>`.
- GPU (Cycles HIP on the RX 6700 XT) follows the queue protocol in `D:\rc_scratch\GPU_QUEUE.md`. Never use the designer's live Blender session.
- Rules:
  - never run `python -`;
  - never launch Godot windowed;
  - seed all randomness;
  - don't download anything;
  - don't kill processes you didn't start.

## Read first
- `docs/concepts/boss_wheel_v2/NOTES.md`, especially the "ROUND 3 (v3)" section: the locked design, rules, layer slots, plaques, needle rig, animation table.
- The v3 finals, mechanic sheets and animations in that folder. They are the design reference, not the quality bar.
- `docs/concepts/boss_wheel_v2/system.png`: the layer template.
- `docs/concepts/round41_wheel_stack/` and `round45_inner_ring/`: the player wheel kit and the inner ring; the boss must sit beside them.
- `docs/ART_BIBLE.md` (v2) and the tail of `docs/concepts/DIRECTION_REVIEW.md`.
- The approved AAA-2 look: `docs/concepts/route_map_graph/side_view/v3_aaa/r3/`. Combat backdrops will move toward it.
- Mainline combat captures (read-only): `D:\Godot\rebel_cell\docs\art_review\PLAN1\W2R2_GROUP.jpg`.

## Locked designer rulings (2026-10-15)
### Roman: THE PANTHEON
- Each slice is a tiled fresco or mosaic of a god:
  - Mars: attack;
  - Jupiter: crit;
  - Minerva: guard;
  - Mercury: RESIST (boss resistance);
  - Vulcan: burn;
  - Pluto: NULL;
  - Neptune: swaps in for phase 3.
- The hub is the deified emperor.
- The needle is the royal box with the emoji-style thumbs-down hand, which is also the boss emblem.
- Mechanic: ASCENDANT plus OMENS.
  - ASCENDANT: one god is gilded and doubled each turn, moving clockwise in a fixed order and skipping Pluto. A NEXT tab shows the next god.
  - OMENS: player hits crack the god under the needle; at 3 cracks the god turns WRATHFUL and its effect flips.
  - Ascendant plus wrathful is the deadliest state.
- The tiled-fresco look is the designer's favourite treatment.

### Atlantis: THE TANK
- A fixed ring aquarium. Eight predators or hazards ARE the slices: shark, swordfish, jellyfish, wreck, moray, mine, electric eel, and a submarine as NULL.
- The seeded spin moves the fish N zones; a nudge moves them 1. Value plaques ride on the fish.
- The octopus/kraken climbs out of the central tank. Each arm is a pointer: 2, 4, 6, then 8 arms at 100, 75, 50 and 25 % HP. At 8 arms the fight is a deliberate sprint.
- Reveal by phase: a shadow, then the eyes, then the mantle, then the full cybernetic kraken (the corporation's brain).

### Rules exceptions (all approved)
1. The tank uses 8 slots and 40 ticks, a per-boss exception to 30 ticks / 6 slices.
2. RESIST is allowed as a boss slice effect.
3. Wrath changes a slice's type mid-fight. The preview recomputes, and rewind never crosses a crack.
4. Pluto counts as NULL for Cold Exit, Fault Tolerance, Zero Day and Stolen Intent until it turns wrathful.

## The polish brief: the gap to close
The designer likes each identity, but both wheels are "a long way from the visual polish needed". v3 is flat procedural 2D: small, simple figures and busts, flat fills, and little depth or material quality.

Target:
1. **Real materials and depth.**
   - Pantheon: real mosaic tesserae with grout, gold-leaf glints, marble with veins, a cast-bronze laurel rim with bevels and specular, and fresco plaster with age and cracks.
   - Tank: real glass with refraction, water caustics and god-rays, bubbles, murky depth gradient, and wet, sheened creature skin.
   - Use Blender (Cycles) for 3D-rendered layers: low-poly stylised models matching the city kit, rendered per layer slot, then composited.
2. **Hero figures at readable scale.** Larger, characterful gods and predators: the mosaic gods as proper portraits, the predators as stylised 3D models with clear silhouettes and rim light. The cybernetic kraken in phase 4 is a hero creature.
3. **Lighting.** A key/rim/ambient setup per wheel, emissive accents in the slice type colours, and light spill onto the arena or backdrop.
4. **Readability stays mandatory.**
   - Values sit on fixed dark plaques, readable in under 1 s at combat size (r = 236 px at 1080p).
   - The type colour band holds.
   - Precision tags and pointers read.
   - Every animation has a reduce-effects end state.
5. **Motion at polish level.**
   - Idle loops: mosaic glint sweeps and a breathing emperor; fish schooling and arms curling.
   - The spin or migration has weight and easing.
   - Landing has impact frames.
   - Phase changes are staged transformations, not cross-fades.
6. **Godot feasibility.** Every layer must map to a real-time Godot 4.7 technique: layered sprites or meshes, shaders, AnimationPlayer, skeletal 2D or 3D, and per-wheel perf budgets. Document it.

## Process
1. Write a 1-page polish plan and a quality bar sheet (5–8 reference crops of what "polished" means for this wheel, from our own art-pass work where possible). The designer reviews it before heavy rendering.
2. Make test crops at 2× of the hub, one slice and the rim at final quality. Get designer sign-off.
3. Build out the full wheel plus phases, the combat frame, and animations of 6–8 s (mp4 plus gif).
4. Run a readability pass and a reduce-effects pass, then compare with the v3 final.
5. Write NOTES: layer recipes, the Godot mapping, perf, and remaining gaps.

## Deliverables
- `<boss>_polish_final.png` (combat frame, combat size, 2× close-up, needle states);
- `<boss>_phases.png`;
- `<boss>_mechanic.png`;
- `<boss>_anim.mp4` / `.gif`;
- `<boss>_emblem.png`;
- `readability.png`;
- `compare_v3_polish.jpg`;
- `NOTES.md`.

Talk to the designer directly in this session. Present options as a numbered list when you need a decision.
