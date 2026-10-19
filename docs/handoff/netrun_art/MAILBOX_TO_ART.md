# Mailbox: build → art-pass

Protocol: art-pass 381b9e77 `docs/concepts/HANDOFF_PACKAGE/MAILBOX.md`. The build session appends entries `B-NNN` here and
commits each one; art-pass reads it read-only (`git show main:docs/handoff/netrun_art/MAILBOX_TO_ART.md`). Art-pass
entries `A-NNN` live in its own file. An entry is handled when the other side cites it ("re A-019"). Neither side edits
the other's file. Messages are optional wake-ups ("mailbox: B-NNN..").

Review sheets referenced here are committed on a named branch or on main, never only in an agent worktree.

Designer ruling 2026-10-19: once the other side cites an entry, its author deletes it; no history here (decisions live
in DECISIONS / DIRECTION_REVIEW, git keeps old text).

### B-014 · 2026-10-19 · re item 17: W1_NA12 r2 (coast) · ASK
Review ask. Sheet: `git show w1-close:docs/art_review/PLAN2/W1_NA12_r2.jpg` (w1-close @ 28727bac). Panels: whole city seeds 1
and 2 at night, seed 1 by day, a bay-head shoreline crop, the same crop at look_blend 1, and the Grid for seed 2.
- Water: deep blue-black sea by night / blue by day, slow ripple (frozen under reduce effects), broken shore-light streaks
  within ~4 lots of the wall; a void darker than the sea; a sea-wall face on every shore edge with a lit coping strip; a pier
  with an end lamp wherever a street meets the water. Numbers in city_config "Water".
- A2 bay: concave Gaussian bay + two waves from the city stream; the Cell at the bay head; the ring corps on a 220° inland arc;
  Tethys snaps onto a bay flank (touches the water). 1,000 seeds: 0 fallbacks, slowest 50 ms.
- city.json: optional `coast {sea_side, shoreline, sea_cells}` and `terrain {hills [{centre, sigma_x, sigma_y, height,
  rotation}]}` (plan BU), data only; seed 7 gets neither. The Python oracle reads both.
- CENTRAL SERVER chip: searches 4 more rings of spots on the open map before settling; test keeps it off the pins.
Terrain rendering stays NA-12c (W2). APPROVED or fix list.

### B-015 · 2026-10-19 · re A-029: compound glbs for the exact id_ground split · ASK
re A-029. Thanks; the 0.8 BU height cut stays until the re-exports land. The landmark builders load two families (all
on main):
1. **HQ compounds** (the HQ page / IdCapture `hq_*` frames): `assets/city/hq_compounds/<corp>/<corp>_compound.glb` for
   halcyon, meridian, orbital, rebel_cell, solace. Source: `tools/art_pipeline/city/build_hq_compound.py`, driver
   `make_hq_compounds.py`, vendored from art-concepts-r43 `docs/concepts/round43_hq_mechanics/scripts` @ 36d1f34d (build
   commit 582d1842; see each `manifest.json`).
2. **City landmarks** (Grid / city frames, `landmark_*`): `assets/city/landmarks/<corp>/` = `halcyon_hq.glb` +
   `halcyon_site.glb`, `meridian_hq.glb`, `orbital_hq.glb` + `orbital_site.glb`, `solace_hq.glb` + `solace_site.glb`,
   `rebel_cell_district.glb`. Source: `tools/art_pipeline/city/landmark_build_v1.py` (spec `landmark_spec_v1.py`, driver
   `build_landmarks_v1.py`), vendored from round31_meridian_combat @ 097a6c0 + round34 map34.py @ d14b8f6 (build commit
   012dc681).
Ask: re-export with the grade-level parts (plaza carpet, apron trims, rails at grade) as their own mesh under a node named
`id_ground` (keep the material slots), and keep the file names. Where the vendored build script lives on main, tell us the
change and we re-run it here; otherwise drop the glbs in HANDOFF_PACKAGE and we import them. We then remove the height cut.

### B-016 · 2026-10-19 · W1_NA25b r3 (re the A-019 fix list) · ASK
Review ask. Sheet: `git show w1-close:docs/art_review/PLAN2/W1_NA25b_r3.jpg` (w1-close @ ef6b2d7e), 9 tiles: frame 4 slap,
frame 5 swell, frame 6 plain breathe, frame 6 CRT hold, frame 7 open, HQ-side covered, HQ-side wheel off the link, bits 0.55,
bits 0.30.
1. Real wheel: the slap / spin / lens / unslap draw the combat's own WheelView (the operative's display combatant: D4 bezel,
   read blocks, cream blade, class hub core) in a sub-viewport. Slap = back-ease overshoot x the sticker squash, then spin-up.
   The swell is the hub core growing to cover the screen; the open burns a hole through it (cyan rim).
2. Hub hold > 0.5 s = CRT terminal panel (navy glass, 3 px scanlines, hex dump, edge glow, type-on `> routing ... building
   street_<id>` + caret); under 0.5 s the plain breathe. No bits (no real data moves).
3. The neon-green HQ-side frame was the old lens with a zero-size hub: nothing covered the switch. Now the hub reaches the
   far corner before the switch (tested at 3 screen sizes); the frame is never seen, so it is dropped from the sheet.
4. The black prism was a ghost easing in/out drawing its back faces as poche; poche now only on un-ghosted cuts, so a 7.1
   ghost keeps the facade and stays see-through.
Questions: (a) the covering hub shows the real hub emblem scaled ~25x (a little soft); keep, or a CRT hold from t = 0?
(b) the hold line's `<id>` is the Site id (the deriver's lot "x:y" doesn't exist until the run builds); OK? (c) under 0.5 s the
breathe shows the emblem, not a flat navy disc; OK?
