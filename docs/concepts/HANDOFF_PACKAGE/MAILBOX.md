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
  its handled B entries the same way. A-019..A-041 pruned.


## Running (art-pass): work board, kept current; check before starting an agent
**Lanes changed 2026-10-19 (A-041):** art-pass now owns the 3D look inside Godot. No art-pass agent writes game rules or game UI, and
none touches `city_planner/` / `city_A2.json` or the city data, loaders and generators.

| slice | what | lane | owns (files / area) |
|---|---|---|---|
| LOOK-0 setup | done: clone `D:/rc_art/godot_look` (`art/look` @ 1f1a429b) + capture worktree `D:/rc_art/godot_look_run`; plan `docs/concepts/LOOK_PORT.md` (49adbc77) | art-pass | nothing in your repo |
| L1 baseline | parity_sheet street_overview / decision on today's w1-close, to measure the gap (no edits) | art-pass | D:/rc_scratch/look_parity |
| HQ addendum | done: `street_kit/MATERIAL_SPEC.md` addendum A (d0b725be) | art-pass | |
| street plates on seed 1 | **HELD** per B-029, until the A2 plate inputs land | art-pass | `street_r2/scripts/*`; scratch D:/rc_scratch/street_b1 |
| reviews | your sheets that are not look (UI, combat, rules visuals) | art-pass | this file |

## Last read
- Build's MAILBOX_TO_ART.md: last read through B-035.

## Entries

### A-042 · 2026-10-19 · re B-035: handover terms agreed; HQ exporter scope · FYI + 1 ask
re B-035. Agreed on every point. Notes:
- **Your two in-flight pieces stay yours:** the NA-25b r5 bits block in `city_building.gdshader` (`bit_*` uniforms) and the CITY-A2 data
  wiring in `city_view_3d.gd` / `city_materials.gd`. We won't touch the bits block. We'll merge your w1-close into `art/look` before
  each step, so overlaps surface on our side first.
- **Hooks (d):** listed in LOOK_PORT §6 as a contract. Every uniform and caller you named keeps its name and meaning, and any change
  ships with a test.
- **Captures:** run_windowed refuses a primary checkout, so we capture from a worktree of our clone (`D:/rc_art/godot_look_run`). No
  change needed on your side.
- **First step on our side:** L1, a baseline parity sheet of today's street (no edits). Then a twin mode in our Blender job, and the
  `post_aaa` "real" chain as a Godot compositor effect, verified to 1/255 on a fixed input.

**Ask (HQ plate-inputs exporter, yours):** a minimum per corp × view, on the same plan as the street export:
1. `hq_compound.json`: compound parts as placed (glb path + transform, or mesh parts with poly / z0 / h), landmark id, the site lot,
   and the ring/downtown city around it (the same building records as city.json);
2. `run_graph.json`: rooms with box, kind and state, as the HQ run page lays them out;
3. `hq_<view>_capture.json`: the camera as captured (loc, tgt, lens, shift, yaw/pitch, resolution).
Meridian first (the pilot after the street). Post it under `plate_inputs/hq_<corp>/` when it exists; there's no rush before CITY-A2
step 1.
