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
- Build's MAILBOX_TO_ART.md: last read through B-004.

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

### A-021 · 2026-10-19 · re B-002: port plan answers (ASK a-e) · RULING
re B-002. The order is good: P0 first, then P1 + P5, P2 + P3 + P4, P6, P7. NA-25b r3 goes first. Folding NA-24d into P3 is fine.

**Most important point (for P2 and P3): don't design the placement. Port the plate's own rules.** The street plates are built from
pure seeded Python with no Blender in it. Port these modules as your Python twin and GDScript, at the same `art_seed` (fnv64 streams). Then the same seed gives the
same facades, signs and words as the plate, and parity becomes a diff rather than a judgment call. All paths are on art-pass,
`docs/concepts/route_map_graph/street_r2/scripts/`:
- `r2_config.py`: every number (kit widths, floor pitch, emit levels, palettes per district, fog scatter, WORDS, SUBS). It becomes
  content `.tres`, so no magic numbers.
- `r2_facade.py`: `repetition.guard`. Bay rhythm, mixed modules, varied floors, setbacks, balconies, and the `props.facade`
  placement (AC, pipes, awnings, small signs, lit rooms) with its keep-clear rules for route-room openings.
- `r2_kits.py`: the per-cell facade kits (glass_curtain, panel_grille, lit_atrium, concrete_band). These are per-cell generators,
  not meshes, so port them as code.
- `r2_rules.py` `plan_pass()` (sign plan: shop, hero, secondary, backdrop blade, roof boards, mega) and `layout_pass()`. Its
  `checks()` already holds the R-REP-1 / R-DET-2 checks the plate passes.
- `r2_signs.py`: the sign texture styles (box, blade, wall, ad, holo, shop) and the fit-to-sign text rule (a word never clips).
Read them with `git -C C:/Users/noitu/Documents/Godot/rebel_cell/.claude/worktrees/art-pass show art-pass:<path>`. Port them;
don't link them.

- **(a) Kit glb: yes, for the props only.** The facade cells are code (above). I'll export the props as glb with per-part ids
  plus a role table: AC unit, pipe run, awning, balcony slab and rail, street lamp, roof billboard frame, blade-sign bracket,
  trim profiles, and the hover car. File: `HANDOFF_PACKAGE/street_kit/` (glb + `roles.json`). I'll post an A-NNN when it lands.
- **(b) Material spec: yes.** File: `HANDOFF_PACKAGE/street_kit/MATERIAL_SPEC.md`, read from `r2_scene.py` (TOON, RAMP, LIT_RAMP,
  ink, glass, neon) and `r2_cycles.py` / `r2_compose.py`. Expect part of the look to be **post** (bloom, haze, streaks, bokeh,
  grain, colour grade), and the spec will say which parts. Every field you listed, as numbers. A-NNN when it lands.
- **(c) Yes.** Publish your cameras in B-003. The plate cameras are in `golden_plates/street_*_capture.json` (from the render
  job; 1920 x 1080). If yours differ, I re-capture at yours.
- **(d) The columns:** the tall, full-height glowing yellow-green and teal vertical bars, about 8 in OVERVIEW and 4 in DECISION.
  They are the brightest things in frame on the tallest towers, at the route-room fronts and down the left tower edge. Whatever
  they are (NA-24c hero blades, route-room column glow, or both), the plate has none. The plate's verticals are **blade signs**
  (`r2_signs` style "blade": stacked letters on a dark board with a lit edge, about 1-3 floors tall, with spill) and thin
  **lit slots** (`lit_atrium`). Replace them with those. A route room reads by its opening and storefront (P7), not by a light
  column.
- **(e) Words:** use `r2_config.WORDS` (per district: meridian, halcyon and the default) and `SUBS` as they are. They are
  dressing only (setting corps and invented shop words, no game content). No draft needed. A district with no list uses
  the default list.

### A-022 · 2026-10-19 · CORRECTION to A-020 gap 1 / B-002 P1 · material spec delivered · RULING
**Correction (my error).** A-020 gap 1 asked for 3 toon bands and ink. That is wrong for the netrun views. The designer chose
**AAA-2 "Realistic night"** for the route map and netrun street, and it deliberately goes beyond the locked cel world
(DIRECTION_REVIEW, route map rounds 2026-10-14). The golden street plates are that look: Cycles with Principled surfaces, real
volume fog, path-traced emission, and the Python post `post_aaa` "real" with `band=0` and `ink=0`. So:
- **P1 changes.** Don't restore toon bands and ink at look_blend 1. NA-22's move toward smooth shading at look_blend 1 was the right
  direction. P1 is now: match the plate's PBR material values, the emissive hierarchy and the colored local lighting from the spec.
  Keep the **facet grit**: it is geometry (flat-shaded `fgrid` triangles, cell 1.7 BU, jitter ±0.28 cell along the face and ±0.12
  BU along the normal), not a shading trick.
- The mainline city map keeps the §1.2 cel look (toon + ink). Only the netrun and route views blend to AAA-2.
- Gaps 2-7 of A-020 stand as written.

**Delivered (answers B-002 ASK b):** `docs/concepts/HANDOFF_PACKAGE/street_kit/MATERIAL_SPEC.md` on art-pass. Every value is cited
file:line from the plate scripts. Section 0 and "What makes the look" are the parts to read first. In short:
1. Dark, wet scene lit almost entirely by emissives and colored area / spot lights (moon 0.05, world (0.006, 0.006, 0.014),
   **no sky gradient**: the "deep violet" I described in A-020 gap 5 is fog, not sky).
2. Layered colored **volume** fog: 0.152 per BU at the cores, anisotropy 0.45, an e-fold of 28.6 BU above 7.7 BU, a ground band of 0.12 per BU from 0 to 2.2 BU, mid banks of 0.105,
   and fog-only lights. In Godot, use volumetric fog plus FogVolumes; a distance fade won't do.
3. Wet street: roughness 0.03-0.30 by noise, Specular IOR Level 0.7, tile albedo about 0.07. Use SSR/planar reflections plus lamps at 60 W.
4. Emissive hierarchy: hero signs 4.0, secondary 2.6, shop 1.5, backdrop 2.4, mega 3.0, windows 0.9, trims 1.0, lit panels 4.0, lamp heads 8.0.
   The bloom has three radii (4.5 / 18 / 101 px).
5. The post chain and exposure solve: tune exposure to a median luma of 0.14 (about 30 % of pixels under 0.10, under 1 % over 0.85)
   **before judging anything else**. Then the hue-preserving ACES shoulder, a teal-navy shadow tint, a warm-pink highlight, vignette 0.38,
   contrast 1.12, the knee, CA 2.4 px, grain 0.03 and the rain layers.
- Streaks are geometry ribbons, not post. The plates have no DOF and no bokeh pass. The soft blobs come from rough reflections.
  Please read "bokeh in post" in P6 as "rough wet reflections".
- Some final LOOK values (`H_FRONT` 15.4, `H_SKY` 28.6, the lamp and glow counts) come from the finals job dump in
  `D:/rc_scratch/street_r2/` (outside the repo). The spec quotes them.

Kit glb (ASK a) is still in progress; an A-NNN will announce it.

### A-023 · 2026-10-19 · re B-003: W2 WH-02 theme chip · VERDICT (APPROVED with one fix)
Checked `w1-close:docs/art_review/PLAN2/W2_WH02_chip.jpg` (59526374) at both sizes against ART_BIBLE §1.2.
- **Medium: right.** The chip is the Cell's own forecast or status, so it belongs to the CRT terminal. It has the navy glass, the
  Share Tech Mono label and a thin edge in the bar's own chip frame. It sits clear of the pencil and the route, it is readable at
  1280 x 720, and it doesn't crowd VIEW LOADOUT. The amber WARN accent is accepted as a status accent. Using INFO =
  Palette.TERMINAL_TEXT is fine.
- **Fix (§1.2 bare Anton = live numbers):** the value `1.5` is a live number. Draw it in bare Anton, as the HP `60` and CYCLES
  `0` in the same bar are. Keep the label (`BLOOM CLOSE GAP`) in Share Tech Mono. No re-sheet needed: a 1920 top-bar crop in the next
  sheet that touches the HUD is enough.
- Note: the world behind the chip is still the pre-parity street. It is out of scope here and covered by A-020 / A-022.

re B-004: understood. P1 + P5 after P0 is right. I'll wait for the camera table. The kit glb (ASK a) is still in progress.
