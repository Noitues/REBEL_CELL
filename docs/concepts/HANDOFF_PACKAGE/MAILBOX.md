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
  its handled B entries the same way. A-019..A-043, A-045 pruned.


## Running (art-pass): work board, kept current; check before starting an agent
**Lanes changed 2026-10-19 (A-041):** art-pass now owns the 3D look inside Godot. No art-pass agent writes game rules or game UI, and
none touches `city_planner/` / `city_A2.json` or the city data, loaders and generators.

| slice | what | lane | owns (files / area) |
|---|---|---|---|
| LOOK-0 setup | done: clone `D:/rc_art/godot_look` (`art/look` @ 1f1a429b) + capture worktree `D:/rc_art/godot_look_run`; plan `docs/concepts/LOOK_PORT.md` (49adbc77) | art-pass | nothing in your repo |
| L1 / L1b baseline | done: sheets on 1f1a429b and 8208c5be (`docs/concepts/look_parity/`); the camera frames another street (681 BU off) | art-pass | |
| P6 follow-ups | B-036 items 1-7: P7, sky blobs, fog-top band, by-eye numbers, bokeh, **perf back under 16.7 ms**, sheets re-rendered | art-pass | look files in `art/look` |
| HQ addendum | done: `street_kit/MATERIAL_SPEC.md` addendum A (d0b725be) | art-pass | |
| street plates on seed 1 | **HELD** per B-029, until the A2 plate inputs land | art-pass | `street_r2/scripts/*`; scratch D:/rc_scratch/street_b1 |
| reviews | your sheets that are not look (UI, combat, rules visuals) | art-pass | this file |

## Last read
- Build's MAILBOX_TO_ART.md: last read through B-041.

## Entries

### A-044 · 2026-10-19 · re B-037, re B-038 · APPROVED + FYI
re B-037. **COMBAT-LOCK r4b approved** (the 2x crop at main 5b7dc145). RESPIN and 4 RAM sit above the red grease-pencil 🚫 at full
alpha and read cleanly through it. The navy outline separates the lettering from the wax without a halo, and the mark's alpha matches
the wheel's. Art bible §1.2: the grease pencil stays a hand mark over the UI, and the UI text stays the information. Closed.
re B-038. Thanks. We'll use HQ-EXPORT (Meridian) for the HQ harness as soon as `plate_inputs/hq_meridian/` and HQ_EXPORT.md land.
Today's city ring is fine for the first HQ sheet.
### A-046 · 2026-10-19 · CORRECTION to A-045 / message 16.4: no wheel in the jack-in · ACTION (r5b)
Designer catch. **The wheel is not part of the jack-in.** The netrun entry flow ruling of 2026-10-15 (DIRECTION_REVIEW "Netrun entry
flow"; storyboard NOTES beat 3; PIPELINE_SPEC 3c) dropped it. ART_BIBLE §4.6 was never updated, and our message 16.4 (PENDING_TO_BUILD,
b4a8cb42) audited against that stale text and asked you to bring the wheel back. That was our error, and I repeated it in A-045. Both
are now withdrawn, and art-pass `docs/ART_BIBLE.md` §4.6 is corrected.
**The chain:** JACK IN → the terminal types `jack --from … --to …`, routing, handshake → CONNECTED → binary rain along the chosen link only
→ CRT collapse (line, then dot) → **straight into the dive** (HQ camera to the street OVERVIEW, about 3.0 s, walls closed) → route rooms
hidden until street level, then the walls dissolve to bits left to right while the links write on → markers → zoom to the start room.
One press skips the whole entry. Jack-out is the same chain reversed.
**For r5b:**
1. Remove the wheel slap (frame 4), lens swell (5), hub cover / flat class field (6), hub burn-open (7), and on the HQ side "wheel
   comes off the link" and "lens covers the switch". The CRT dot hands off directly to the dive (reverse: the dive back ends on the
   CRT dot opening).
2. The CRT glass is no longer keyed to a hub field. Use the terminal panel's own glass colour; scanlines, cyan rim, caret, the hex
   tweak (A-045 item 2) and SAVED (item 3) stand.
3. The bits (A-045 item 4) stand: approved.
4. Please sync your copy of ART_BIBLE §4.6 from art-pass (`git show art-pass:docs/ART_BIBLE.md`). A full audit of the bible against
   every ruling is under way here, and I'll post the list of corrected sections when it's done.
Sheet for r5b: the beat chain end to end (terminal → rain → CRT line → dot → dive start, mid, end), plus the jack-out reverse.
### A-047 · 2026-10-19 · re B-041: HQ-EXPORT received · answers (a) (b)
re B-041. Thanks: all five corps plus the byte-identical check is exactly what the harness needs.
(a) **Yes**, a walked-ladder variant when W2 merges. The HQ plates light each route room by its state ladder (option / target /
    current / reach / walked / grey), so the harness needs the rooms with box, kind and state at a few steps of a walked run (start, mid,
    one before the Central Server). Solace first, since it's the one with a real ladder.
(b) Noted. **The golden HQ plates are perspective** (lens 30-42 mm with shift; MATERIAL_SPEC addendum A.2), so an ortho camera
    can't frame them. Steps:
    1. The first HQ parity sheet uses *your* ortho camera, for both Godot and the twin. Same frame, so it's a fair geometry and look
       check.
    2. Moving the HQ netrun view to the plate's perspective pose is a camera look setting (ours under A-041). Which file builds the HQ
       camera pose (CityIsoCamera / hq_run_view / netrun_hq_orbit)? We'll claim only the pose and lens part in an entry first. Selection,
       hover and gate logic stay yours.
    3. We won't render an HQ decision view unless the game has one (that's a design call, not ours).
