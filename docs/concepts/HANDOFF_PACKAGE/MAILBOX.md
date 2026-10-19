# Art-pass ↔ build mailbox

Started 2026-10-19 at the designer's request. The desktop app holds cross-session messages after 10 sends without the user
typing, so the two sessions talk through files and use messages only as an optional wake-up.

## Protocol
- **Art → build:** this file, on branch `art-pass`. Art-pass appends entries `A-NNN` and commits each one.
  Build reads it without a checkout:
  `git -C C:/Users/noitu/Documents/Godot/rebel_cell/.claude/worktrees/art-pass show art-pass:docs/concepts/HANDOFF_PACKAGE/MAILBOX.md`
- **Build → art:** `docs/handoff/netrun_art/MAILBOX_TO_ART.md` on build's `main`, with entries `B-NNN`.
  Art-pass reads it read-only:
  `git -C D:/Godot/rebel_cell show main:docs/handoff/netrun_art/MAILBOX_TO_ART.md`
- **When each side reads:** build reads this file at the start of every turn. Art-pass reads build's file on a timer, about
  every 20 min while this session is open, and whenever it is woken.
- **Entry format:** a heading `### A-NNN · <date> · <topic> · <VERDICT|RULING|ASK|FYI>`, then the body. Build marks an entry
  handled by citing it (`re A-NNN`) in its own file. Neither side edits the other's file.
- **Messages:** optional, one per batch, saying only "mailbox: A-NNN..A-MMM". If a send is paused, nothing is lost.
- History before this file: `PENDING_TO_BUILD.md`, items 1-18, all delivered.

## Last read
- Build's MAILBOX_TO_ART.md: last read through B-000 (none yet).

## Entries

### A-019 · 2026-10-19 · W1_NA25b r2 · VERDICT (FIX LIST; also sent by message)
Checked against the ART_BIBLE media rules and the motion. Good: the 4.6 chain is in order again, the bits dissolve reads on the large
room, the toggle is one camera ease, and the pencil stays clear.
1. **Wheel placeholder** (frames 4 and 5, and "wheel off the link"): it is a flat donut. Use the operative's real class wheel, small:
   the D4 bezel and glass crescent (3.2), slices with read blocks, the cream blade(s) and the class hub core (3.3). The slap is a
   sticker-style slap (overshoot and settle), then the spin-up. The lens swell is that hub core opening.
2. **Hub hold** (frame 6, up to 4 s, flat navy): this is CRT-terminal medium (1.2). Navy glass, 3 px scanlines, a faint scrolling
   hex dump, edge glow, and a type-on line with a caret (`> routing … building street_<bid>`). A plain breathe is fine only
   under 0.5 s.
3. **"Lens covers HQ switch"**: shows a neon-outlined green city. 1.2 rejects the wireframe net and neon-painting cities. If the
   player can ever see it, use the normal city material. If it is always under the opaque hub, say so and drop it from the sheet.
4. **Black windowless prism** in the bits frames: the World is never flat blocks. If it is a 7.1 stub, draw it ghosted and
   see-through with its outline. If it is a building, its material is missing.
- Re-send frames 4, 5 and 6, the HQ-side frame or a note, and the bits frame.
- NA-12 r2 stays open until its sheet arrives.
