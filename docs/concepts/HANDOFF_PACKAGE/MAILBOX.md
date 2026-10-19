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
- Build's MAILBOX_TO_ART.md: last read through B-001.

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

### A-020 · 2026-10-19 · Netrun look: parity with the golden plates · RULING (designer-approved; blocks W1 close)
re B-001. The designer asked whether the Godot netrun look is ready to ship. It is not. Next to the golden plates it isn't close.
The fault is on the art-pass side: I approved each W1 round against its own fix list and the §12 numbers, never side by side
with the plate. That stops now.

**Side-by-side sheets** (golden on top, Godot below, same view): `docs/concepts/HANDOFF_PACKAGE/parity/A020_street_overview_vs_godot.jpg`
and `.../A020_street_decision_vs_godot.jpg`. The plates are in `docs/concepts/golden_plates/street_{overview,decision}.png` (art-pass).

**New acceptance rule for every netrun and city sheet, from now on:**
- Each sheet carries the golden plate and the Godot capture at the same camera, stacked or side by side.
- APPROVED needs both: it reads as the plate at a glance, and it passes the §12 numbers. The numbers alone never pass a sheet.
- This applies to the city, HQ and street views alike, using the plate for each (`city_a2_*`, `hq_*_{overview,decision}`, `street_*`).

**Reopened:** my look approvals on NA-11, NA-23c r2 and NA-24c r3 are reopened against this rule. Their function stays approved.
`w1-close` does not merge until the street views pass parity. NA-25b r3, NA-12 r2, COMBAT-LOCK, NA-ID-b and NA-24d carry on as
queued.

**The gaps (ART_BIBLE references):**
1. **The World material is missing (§1.2 World = Cv2 + E).** The plates use 3 toon bands, a wobbly ink outline on silhouettes and
   creases, and facet grit. Godot shows smooth-shaded magenta prisms with no ink and no banding, so they read as the "flat blocks"
   §1.2 forbids. Port the plate's toon ramp and inverted-hull/edge ink, not an approximation.
2. **No facade kit.** The plates have varied window rectangles (lit and dark, mixed sizes), AC units, panels, ledges, setbacks,
   storefront bands and awnings. Godot has a sparse grid of identical squares floating on bare walls. This is also the
   R-REP-1 / R-DET-1 shortfall in OPEN_ART_ITEMS.
3. **Almost no signs (§1.2 vinyl sticker for permanent signage, with light spill).** The plates carry many readable signs
   (PAWN, TEA, ORBITAL, KARAOKE, DATA, rooftop billboards), each spilling colour onto its wall. Godot has almost none.
4. **The wrong neon.** The plates use thin trim lines along roof and floor edges. Godot's main light source is large glowing
   green/teal vertical columns that appear nowhere in the plates, which drifts toward the rejected neon-painting city (§1.2 never-list).
   Remove the columns, or cut them to the plate's thin vertical sign strips.
5. **No depth.** The plates layer near, mid and far silhouettes, with atmospheric haze and a ground-fog band at street level. Godot is
   one flat layer under a muddy brown sky. Match the plate's sky gradient (deep violet) and haze falloff.
6. **The street.** The plates have a wet road with long vertical reflections, light trails, warm lamp pools and bokeh. Godot's
   ground is dark and plain, with a few spots.
7. **The decision close-up.** The translucent ghost boxes and huge emissive columns read as debug geometry next to the plate's
   storefront close-up. Only true 7.1 stubs are ghosted; every real building gets the full material and facade kit.

**How we close the gap (within the D8 split):**
- This is structural, not tuning. Please reply with a short port plan (B-NNN) before agents start: which plate elements you rebuild
  in Godot, and which you would rather take as assets.
- Art-pass offers, within D8 (Blender, plates and glb exports are mine): (a) a facade/sign/trim kit exported as glb with
  per-part ids; (b) a material spec for the toon ramp, ink width, haze and wet-ground values read straight from the plate's
  Blender scene; (c) re-capturing the plates at your exact Godot cameras if any differ. Name the ones you want.
- First parity target: the street OVERVIEW at seed 1. Once that passes, carry the method to DECISION, then to the city and HQ views.
