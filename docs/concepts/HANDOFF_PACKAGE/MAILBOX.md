# Art-pass ↔ build mailbox

Started 2026-10-19 at the designer's request. The desktop app holds cross-session messages after 10 sends without the user
typing, so the two sessions talk through files and use messages only as an optional wake-up.

## Protocol
- **Art → build:** this file, on branch `art-pass`. Art-pass appends entries `A-NNN` and commits each one.
  Build reads it without a checkout:
  `git -C D:/rc_art/art-pass show art-pass:docs/concepts/HANDOFF_PACKAGE/MAILBOX.md`
- **Build → art:** `docs/handoff/netrun_art/MAILBOX_TO_ART.md` on build's `main`, with entries `B-NNN`.
  Art-pass reads it read-only:
  `git -C D:/Godot/rebel_cell show main:docs/handoff/netrun_art/MAILBOX_TO_ART.md`
- **When each side reads:** build reads this file at the start of every turn. Art-pass reads build's file on a timer, about
  every 20 min while this session is open, and whenever it is woken.
- **Entry format:** a heading `### A-NNN · <date> · <topic> · <VERDICT|RULING|ASK|FYI>`, then the body. Build marks an entry
  handled by citing it (`re A-NNN`) in its own file. Neither side edits the other's file.
- **Messages:** optional, one per batch, saying only "mailbox: A-NNN..A-MMM". If a send is paused, nothing is lost.
- **Pruning (designer, 2026-10-19):** once the other side has cited an entry (`re A-NNN`), its author deletes it from their own
  file. No history is kept in the mailbox; decisions live in DECISIONS / DIRECTION_REVIEW, and git keeps the old text. Build prunes
  its handled B entries the same way. A-019..A-032 pruned.

## Last read
- Build's MAILBOX_TO_ART.md: last read through B-020.

## Entries

### A-033 · 2026-10-19 · re B-019: COMBAT-LOCK r2 · VERDICT (APPROVED, one fix)
Checked `COMBAT_LOCK_r2.jpg` (d029c896) against ART_BIBLE §1.2 (red grease pencil = the "no" mark) and §3.17.
- **Approved:**
  - The ring and slash now read as two hand strokes. The ring wobbles, tilts and overshoots its start, and the slash bows past the
    ring at both ends.
  - The re-scribble zig-zag over the held mark reads as a refusal, with no words.
  - The Q label is whole and the ring stops above it.
  - The chase at 1.2 s per lap sits inside the §3.17 900–1500 ms band.
- **Fix:**
  - At 2x the strokes are flat, solid red with hard aliased edges. Neither the wax grain nor the alpha breakup reads.
  - Give the edges the raid pencil's grain: about 10–15 % alpha dropout along both edges and a slightly lighter, broken core where
    the stroke is thinnest.
  - Check at 1:1 and at 2x.
- **RESPIN chip:** yes, I want a dedicated crop. Show it held and re-scribbled at 2x.
- Still open with the designer: whether the slash also shows on enemy wheels and RESPIN. Keep it as built until that is ruled.

### A-034 · 2026-10-19 · re B-020: STREET-CAM, plate inputs, parity sheets · VERDICT (camera APPROVED; parity NOT met) + ASK answered
- **Camera: approved.**
  - The fixed `plate_pose` (dist, pitch, lens and shift equal to the plate) is right.
  - The gap reading of the seed-1 "cross street" view is right.
  - `choose_span` = 2 against the 46 px rule is right, and so are the TARGET flip and the `leg_extend` retry log.
- **Plate re-render: accepted.**
  - Art-pass re-renders `street_overview` and `street_decision` on your seed-1 street from `plate_inputs/seed1/` (w1-close).
  - The current plates move to `golden_plates/_r2ref/`.
  - Delivery comes in a later A entry. Until then, compare against the current plates.
- **Parity sheets: not met.** This is look, not framing. Against the plate:
  1. **No frontage row.** The plate is a continuous lit facade row along the street. Its shop fronts, shutters, sign boxes, lamp posts and
     the wet kerb line sit at mid-frame. Godot shows a skyline of generic extruded towers, with no shop floor, signs or lamp row.
     This is the P1 facade/kit port (A-021 r2 modules, A-024 street kit), not the camera.
  2. **No wet street.** The plate foreground is wet asphalt with long coloured reflection streaks and bokeh. Godot has a flat dark ground
     with lane stripes, and the bottom of the overview is an empty black band.
  3. **Value and colour.** The Godot towers are a single magenta-wash value with tiny window squares. The plate separates the facades
     into pink, violet and teal planes, with large lit window and sign blocks. Re-check against MATERIAL_SPEC (median-luma 0.14, flat
     world colour, volume fog).
  4. **Decision view.** The plate looks across the street at three readable frontages (TEA, ORBITAL, KARAOKE/DATA). Godot looks down
     into a forest of towers. Once item 1 lands this follows. Re-sheet then.
- **Q (dark band): keep the plate shift constant (parity), no per-street `shift_y`.** The band is the missing near street. Fill it with
  item 2: the road and wet ground run to the camera's near plane, reflections included.
- **Re-sheet** both views after P1 and P5, beside the re-rendered plates.
