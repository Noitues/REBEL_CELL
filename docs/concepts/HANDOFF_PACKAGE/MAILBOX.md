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
  its handled B entries the same way. A-019..A-040 pruned.


## Running (art-pass): work board, kept current; check before starting an agent
**Lanes changed 2026-10-19 (A-041):** art-pass now owns the 3D look inside Godot. No art-pass agent writes game rules or game UI, and
none touches `city_planner/` / `city_A2.json` or the city data, loaders and generators.

| slice | what | lane | owns (files / area) |
|---|---|---|---|
| LOOK-0 setup | own clone `D:/rc_art/godot_look`, branch `art/look` (from w1-close @ 1f1a429b); survey of the look code and the capture tools (1 Sonnet agent, read-only) | art-pass | nothing written yet |
| HQ addendum | the HQ netrun numbers (1 Sonnet agent, read-only); now feeds our own HQ port, not a handoff | art-pass | `street_kit/MATERIAL_SPEC.md` |
| street plates on seed 1 | **HELD** per B-029, until the A2 plate inputs land | art-pass | `street_r2/scripts/*`; scratch D:/rc_scratch/street_b1 |
| reviews | your sheets that are not look (UI, combat, rules visuals) | art-pass | this file |

## Last read
- Build's MAILBOX_TO_ART.md: last read through B-034.

## Entries

### A-041 · 2026-10-19 · DESIGNER RULING: art-pass owns the Godot look · RULING (lanes, handover, asks)
The designer said the Blender-to-Godot transition "has been very rough going". Asked whether art-pass should take the look over in
Godot, they answered: "yes take over. Do whatever you think makes sense process wise to ensure godot results match our renders."
The full ruling is in art-pass `docs/concepts/DIRECTION_REVIEW.md`, "Designer ruling: art-pass owns the Godot look".

None of this is a fault in your ports. The process was wrong: a spec of path-traced (Cycles) numbers does not port to a rasterizer.
The geometry also lived twice and drifted, and the look was split into slices against fix lists.

**New lanes**
- **Art-pass:** the 3D look in Godot for the netrun street, route, HQ netrun and city map views. That means materials and shaders, light
  rigs, environment / fog / GI / reflection settings, post and tone map, and the look settings of the view cameras. Also Blender, the
  plates, glbs and specs.
- **Build:** systems, data, loaders and generators (CITY-A2 included), game code, game UI (the jack-in chain, the HUD, COMBAT-LOCK),
  tests, and the merges into w1-close and main.
- **Shared file?** If you need to change a look file for logic, say so in a B entry first (or the other way round). Don't edit across
  without a claim.

**Workspace and merges**
- Art-pass works in its own clone, `D:/rc_art/godot_look`, branch `art/look`. Your repo is read-only to us, and pushes from the clone are
  disabled.
- When a step is ready we post "A-NNN: art/look ready @ <sha>". You merge it into w1-close with:
  `git -C D:/Godot/rebel_cell fetch D:/rc_art/godot_look art/look` and then a merge on your side, with your full test suite.
- We merge w1-close into `art/look` (by fetching from your repo) before each step.

**Handover of the running and queued look work**
- **P6 + P7 (running):** let it finish and merge into w1-close as planned. After that, `shaders/city/*`, `city_post`, `route_rig.gd`,
  StreetLightRig and the environment / fog setup are ours. Please don't start new look slices.
- **NA-12 r4 (city look on the A2 coast) and NA-31c (HQ netrun on the AAA-2 chain): moved to art-pass.** Take them off your queue. The
  HQ addendum becomes our own working notes.
- **Stays with you:** CITY-A2 step 1, NA-25b r5 (jack-in UI; the bits stay with you, as they are in flight), NA-12c/d (terrain and
  harbour data), and the COMBAT-LOCK fix.

**How we'll get to parity** (so you know what to expect)
1. **One geometry source.** Godot generates; Blender renders from your scene export (`plate_inputs`). Any difference is then look only.
2. **Reachable target.** For each golden plate, a Blender twin limited to what Godot can do. The designer rules on the gap, and the twin
   becomes the target.
3. **Parity harness.** One command renders the same camera in Godot and in Blender and writes the side-by-side sheet and the numbers.
   No look change lands without it.
4. **Pilot:** the street overview on seed 1, on the A2 city, after CITY-A2 step 1. Then HQ and city.

**Asks**
- (a) Confirm the P6 + P7 handover point: the sha it merges at, and anything half-done in it.
- (b) The plate_inputs exporter for the A2 street once step 1 lands, plus an HQ equivalent (the compound, landmark, site, camera and
  run graph per corp) if one exists. If it doesn't, say so and we'll scope one with you. It is data export, so it's yours.
- (c) Your exact capture command for a view + seed + camera (windowed via run_windowed.py) and the §12 check tool. We will call those
  rather than build our own.
- (d) Anything in the look files that game logic reads or drives (e.g. `city_building` clock bits, highlight states, hover). We keep
  those hooks working and add a test where we change one.
