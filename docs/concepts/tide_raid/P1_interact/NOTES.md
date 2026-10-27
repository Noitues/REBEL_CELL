# P1 interactivity concepts: Solace Infected Tide, "Jack-in over the Night City" (art-pass, 2026-10-27)

Polish iteration 1, interactivity. Annotated frame sequences at 1920x1080, built over the real city plates with the H2 scripts
extended (`scripts/ix_*.py` import the H2 `hb / hy / ui / hz` libraries unchanged). Heads are the current pass-2 heads (the H3
exploration is not used). Nothing here is committed. Stills only: timing belongs to `P1_motion`, the golden city to `P1_plates`.

Every frame exists twice: `frames/NAME.jpg` is annotated (designer layer: cream chips with leaders, never game UI) and
`frames/clean/NAME.jpg` is the game UI only. All judgements below were made on the clean frames.

## What is in the folder
| Sequence | Frames | Boards |
|---|---|---|
| 1 Hover / focus | `01a` Site, `01b` beam, `01c` card, `01d` HOME (disc focus = `04a-d`, lock/eye focus = `05a-c`) | `boards/01_focus_board.jpg` |
| 2 Card drag and drop | `02a` pick up, `02b` over a match, `02c` wrong type, `02d` occupied, `02e` snap, `02f` cancel, `02g` 2-guard limit, `02h` no route, `02i` already covered | `boards/02_drag_board.jpg`, `boards/02j_reasons_board.jpg` (seven reasons side by side) |
| 3 Forecast scrub / what-if | `03a` over t3_c, `03b` over t2_virus, `03c` over t1_c, `03d` over t3_b (nothing changes) | `boards/03_whatif_board.jpg` |
| 4 Response disc hover | `04a` DEPLOY, `04b` HOLD, `04c` MOVE, `04d` SACRIFICE | in the focus board |
| 5 Sealed / hunter inspection | `05a` hover a lock, `05b` hover the hunter eye, `05c` hover a Site and read the locks | `boards/05_sealed_board.jpg` |
| 6 Controller and keyboard | `06a` focus order, `06b` cursor snapping, `06c` prompts as glyphs, `06d` card wheel, `06e` shoulder cycle, `06f` input map | `boards/06_input_board.jpg` |
| 7 Layout | `07a_layout_1280_board` (naive shrink vs UI floors, 1:1 crops) + native `07a_layout_1280_native.jpg` (1280x720), `07b_safe_4x3` (1440x1080), `07c_safe_ultrawide` (2560x1080), `07d_safe_areas` (nesting diagram) | |
| 8 Onboarding without text | `08a` first raid, `08b_demo_1..4` ghost hand, `08c` type code, `08d` tier code, `08e` progressive light | `boards/08b_ghost_hand_board.jpg`, `boards/08e_progressive_board.jpg`, `boards/08_onboarding_board.jpg` |

`squint/` has, for eight key frames, normal | 320 px | blur 4 | deutan | tritan in one strip. `scripts/` rebuilds everything:
`python ix_a.py`, `ix_b.py`, `ix_c.py`, `ix_d.py`, `ix_e.py`, `ix_f.py`, then `python ix_g.py` (input map, reasons board, boards,
squint). Plates from `D:/rc_scratch/tide_concepts/plates`, cache in `D:/rc_scratch/tide_concepts/p1i_work`.

**Illustrative numbers.** The 12-outcome tiers, which Site a beam stops at and every "what changes" are a tidy stand-in, not the
rules (`ix_lib.BASE12`, `with_guards`). They are consistent across the sequences so each frame tells one story. Build supplies
the real values from `SolaceTideRules.forecast` (rule 6: preview == result).

## The interaction grammar (one page)
1. **Lime is the focus and only the focus, and it is a shape, not a hue.** On the ground it is four **corner brackets of an iso
   diamond** (Site, HOME, the eye, a head hex) plus a faint dotted inner ring; on a card it is the outline glow; on a disc the ring;
   on a beam two thin hairlines either side of the ribbon (the ribbon itself stays its pure type hue). Why brackets: the first
   attempt, a lime ring, collided with the amber SITES LOST ring (both yellow-green, and equal under deutan). No tier uses a
   bracket, so the focus can never be mistaken for a tier. Lime also appears at 35% as a one-step ghost of the previous focus.
2. **Focus de-emphasis (the CP2077 scanner shift).** The city is graded, not dimmed: value -45%, saturation -60%, with a soft hole
   around the focus (disc, or the path of the beam). The ladder: focus 100%, related 85%, context 45%, unrelated beams 24-30%
   (still a readable silhouette), sealed corridors and locks 30-45%, HUD never dims. Entering is a 6 f ease, leaving 3 f
   (asymmetric, like the CP2077 overlay in REF_BASELINE).
3. **Preview = a dashed white outline around the usual carrier.** The new ring, block and tile are drawn at normal weight inside a
   dashed outer outline; the old ring and tile stay as thin ghosts (dotted amber ring, small dashed hex). Committed = no dashed
   outline. One channel (dashed) says "uncommitted" everywhere: drag hover, what-if, disc hover.
4. **Intent never hides behind hover.** Idle plan frames keep the ribbons, heads, locks and eye as in H2. Hover adds: pass-through
   dots, pair read-outs (beam head -> tile), "?" chips, prompt pills. These are the only focus-only marks.
5. **Type matching is shown by identical shape and hue.** A card of type X lights a Site with a pad ring in X's hue and X's head
   glyph standing above it, only where a KNOWN beam of type X crosses. Sites crossed only by a sealed route get a fog "?" pad:
   the type of a sealed route is hidden, so the pad is never a promise (see build item 1, this is a leak risk in the shipped
   `useless_reason`). Wrong type = grey pad with [card glyph != beam glyph]. Already covered = "=" chip.
6. **One refusal mark.** The red grease circle-slash (the nudge-lock mark) means refused: occupied, 2-guard limit. "Nothing here"
   (no beam reaches / Site DOWN) is a grey hollow ring cut by a hairline and nothing lights. Legal-but-flagged (`!=`, `=`, `?`) are
   grey or fog and never red. Every reason has a shape; colour is never the only channel.
7. **Hidden information.** What can be inspected without text: the route (corridor lifted +34 px off the street so it never hides
   under a known ribbon), its length (one pip per street segment), the Sites it can reach ("?" chips), its share of the odds
   (the tally marks underlined: 4 of 12 per route, 6 of 12 per hunter street), and, from a Site, which locks can hit it (a fog
   thread). What stays hidden: the type (three overlapping outline silhouettes, "any of D / N / E") and the tier.

## States, per object
States are idle | hover-or-focus | pressed (held or carried) | selected (pinned) | refused. Hover and keyboard/pad focus are the
same state by design (one look, one code path).

| Object | hover / focus | carried or pressed | selected | refused |
|---|---|---|---|---|
| Site (01a) | lime brackets; city graded; beams that reach it stay lit, others 24%; readout chip above it: one row per beam [head] -> [tile or pass dot], three fog locks for sealed; ring + block of the beam that lands here stay lit | target while a card is carried: brackets + ghost program + dashed carriers + old-ring ghosts + tally diff (see sequence 3) | none (a Site is not selectable; a placed program is: grab to take back) | grey ring (nothing here) / red slash (occupied) |
| Beam (01b) | lime casing both sides of the whole ribbon; others 26%; pass dots on crossed Sites; the dead trail it would run to HOME; hand cards that answer it lift 26 px and glow in its hue | n/a | n/a | n/a |
| Card (01c) | lifts 40 px, lime outline; the matching street glows, MATCH pads at 70% | ghost card: tilted, shadowed, tether to its socket; hand slot = dashed socket | picked (click-to-place mode): same as carried | at limit: card cannot lift further than 8 px, sockets flash red |
| Disc (04) | lime ring, the word in grease marker appears (hover only); its consequence drawn dashed on the map; tally diff row | pressed: ring thickens 2 px for 3 f | selected = the committed response, brackets stay | lethal discs carry the existing double-press confirm (flow already has it) |
| HOME (01d) | lime brackets; likely loss ticks orange + worst-case ticks red; the last stretch of every beam cased; the 12-mark tally lights; Sites and sealed fall to 45% | n/a | n/a | n/a |
| Lock (05a) | lime hex brackets; its corridor lifted and brighter, pips on every segment, "?" chips on reachable Sites, 3 ghost silhouettes at the mouth; tally: its 4 outcomes underlined, others 32% | n/a | n/a | n/a |
| Hunter eye (05b) | lime brackets on the eye; the street under the pointer bright, the other 45%; each street's own tile; two pips "1 of 2"; tally: 6 of 12 underlined | n/a | n/a | n/a |
| Guard slots (02a/g) | two hex sockets: empty = dashed, filled = verb glyph + type tab | n/a | n/a | full + a third card carried: both red |

## Sequence notes
**2 Drag and drop.** Pick up (`02a`): the ghost leaves a dashed socket, a tether runs to the pointer, every legal Site is lit by class at
once. Snap radius 90 px (proposal): the nearest legal Site wins, the card tilts toward it, the pad takes the brackets (`02b`).
Wrong type (`02c`): card jitters +-26 px (two echoes), no preview, a drop is allowed and lands flagged grey. Occupied (`02d`) and the
limit (`02g`) are refusals: red slash, red tether, the card flies home on release. The limit is shown as two physical sockets,
and while both are full the placed programs grow a small grab hand ("take one back to place another"). Snap (`02e`): wall solid,
ring flash, one shock ring, dashed outlines drop away, the socket fills, the hand re-fans. Cancel (`02f`): ease home along the
tether in 10 f with 3 echo ghosts, pad lights fall to the 45% level, no state changes. Esc/B only ever drops the carried card.

**3 What-if.** A card carried (or picked in click mode, or aimed on a pad with the stick) previews on every hover, no separate "peek"
button: scrubbing the pointer across Sites re-runs the preview every frame (`03a`-`03d`). The carriers move with it: the
block and ring slide along the street, the old amber ring/tile stay as ghosts, the **tally redraws as two rows**: the old odds as
a small ghost row on top, the new odds below, a white hairline from every outcome that changed tier to its new slot and a
white underline under each changed mark. Marks keep their identity (the same outcome index), so the eye follows a mark
that hops from "damaged" to "holds". Better and worse marks both move (`04c`). When nothing changes (`03d`) the rows are
identical, there are no hairlines, and an "=" badge sits at the left of the tally.

**4 Response discs.** Each disc previews uncommitted on the map and in the tally: DEPLOY the best placement of the card that would
be played (the card rides above the disc, other candidate Sites show only a tier chip), HOLD nothing (the control: the heads wake,
rows identical), MOVE the curved arrow with the old wall/ring left as ghosts and the stop block/ring moving, SACRIFICE the grease DOWN
+ amber ring + tile on the given-up Site, the dashed arc from HOME, HOME's chip mint and its ticks cleared. The word appears on
hover only: the glyph alone must carry the disc at rest (see weak points).

**5 Sealed / hunter.** See grammar point 7. `05c` is the answer to "who can hit this Site" and is also the fix for the pass-2 open
question 9 (sealed fog hiding under known ribbons): an inspected corridor is lifted off the street.

**6 Controller and keyboard.** Focus order of the map zone: the three beam heads (the way to focus a beam), then Sites by their
distance from the corp HQ along the threat (min arclength over every route crossing them, ties by site id: rule 7), then HOME,
the sealed locks A-C, the hunter eye. DOWN Sites and Sites no beam reaches are skipped. The hand is its own zone (LB/RB, Q/E,
wrapping). The stick is a direction, never a free pointer: it jumps to the best target in a +-45 deg cone, score = distance x
(1 + 2 x angle / 45), lowest wins (`06b`: t2_breach is nearer but 24 deg off, t2_intel is dead ahead and wins). Deadzone 0.35,
12 f repeat after the first press. LT/RT (Tab/Shift+Tab) walk the focus order, or only the valid targets while a card is carried.
Prompts are glyph pills that follow the focus (`06c`): layout-neutral four-dot face diamond with the pressed dot filled (no
A/B/X/Y letters), bumpers L/R outlined, triggers filled, stick arrows, keycaps, mouse; the action icon (place = card into a hex,
cancel = x, cycle = < >) is shared by all three families, only the button glyph swaps. The card wheel (`06d`, hold LB / R / middle
mouse) puts the 5 cards on a ring in the bottom third, the centre shows the selected card's type glyph big; the shoulder cycle
(`06e`) is the quiet alternative, with the neighbours' type glyphs shown on the side pills.

### Input map (also `frames/06f_input_map.jpg`)
| Verb | Pad | Keyboard | Mouse |
|---|---|---|---|
| Move focus | L stick / D-pad | W A S D | hover |
| Pick up / place / confirm | face S | Enter, Space | click, drag-drop |
| Cancel / drop back / undo last | face E | Esc, Backspace | right-click |
| Take a placed program back | face W | X | drag it off its Site |
| Forecast / launch (second press confirms) | face N | F | click the HOME tally |
| Cycle the hand (tap) | LB / RB | Q / E | wheel |
| Card wheel (hold) | hold LB | hold R | hold middle |
| Walk the focus order / valid targets | LT / RT | Tab / Shift+Tab | n/a |
| Pause / menu (nothing carried) | Menu | Esc | n/a |

**7 Layout.** 1280x720 (`07a`): the world shrinks to 67% but the grammar does not, so marks are scaled x1.3 against the city (floors at
1280: glyph >= 24 px, tile >= 52 px wide, ribbon >= 12 px, head >= 30 px, text >= 24 px, stick/tap target >= 44 px). Declutter rules
applied on top of H2's (idle collapse, one tile per target, fan >= 66 px -> 86, two lanes, programs on the ground side):
the 12-mark tally becomes 4 glyph x count groups (the full row returns on HOME focus), the hand becomes a tab strip (type tab +
verb glyph, 62 px; the focused card lifts to full), pass-through dots / "?" chips / read-outs / prompt pills exist only on focus, at most
two dashed previews at once (the second replaces the first on scrub). 4:3 (`07b`): the camera zooms out x0.75 so HQ and HOME both fit,
and the freed 270 px under the map carry the hand and the guard slots, so nothing overlaps the map; HUD chips stay on the 1440 box
corners. Ultrawide (`07c`): same height, the world continues at the sides (mock-up: mirrored, blurred, darkened, NOT real
content), no UI outside the central 16:9; HUD pins to the 16:9 box, not the screen edge. `07d` nests the three.

**8 Onboarding.** Never a panel. (a) First raid (`08a`): staged by light, not by hiding (rule-free): one beam, one card, one target at full
light, concentric echo rings in the D hue on the head and on the pad, the rest at 15-30%. (b) Ghost hand (`08b`): after 6 s idle on
raid 1 a dashed white hand plays the whole move once (tap, carry, hover shows the preview, release places) and vanishes;
reduce-motion shows the four beats as cuts. (c) Type code (`08c`): the first time a head is focused a **type key** opens: head
silhouette big + a sample of its body, joined by dashed hairlines to the same shape on the card tab and on the pad chip; N and E
are empty dashed slots that fill the first time that type is met. (d) Tier code (`08d`): the first time a tile appears a wheatpaste
**ramp** is stuck near HOME: the five tiles light to heavy over a thickening wedge (a non-hue channel), a hairline from the live tile to
its slot; it appears once per profile. (e) `08e` shows the light levels for raids 1, 2, 3+.

## What build must change (tide_raid_screen / tide_raid_flow). Layout and flow are build's; art owns tide_fx / tide_look.
1. **Drop-target classification with a reason enum.** `place_error` returns text today. Add `drop_class(card_id, site) -> {class, reason}`
   with class in match | maybe | dud | same | none | occupied | limit (map onto `SolaceTideTally.sentry_check`'s why = type | none | same
   and `place_error`'s four refusals). `maybe` = only sealed routes cross. **`useless_reason` / `sentry_check` must name only KNOWN
   beams' types; a sealed route's type must never reach the UI before REVEAL.**
2. **`whatif(card_id, site) -> Dictionary`** without mutating `raid.place` (or on a copy): returns, per known beam, {stop site, tier, stop
   arclength anchor}, and the 12 outcome tiers **in a stable outcome order** with each outcome's sealed index A and hunter street.
   Preview must equal the committed forecast (rule 6; add a test comparing `whatif` to `place_on` + `forecast`).
3. **Stable outcome identity.** `SolaceTideTally.ladder` is sorted by tier; the tally diff and the sealed/hunter underlines need the
   unsorted per-outcome list (index j, A, B-pick, hunter street). Add `rows_of(hunter = -1)` beside the existing `rows_of(a, tier, inf)`.
4. **Focus model in the screen.** A deterministic focus list (heads, Sites by HQ distance then id, HOME, locks, eye, skipping DOWN and
   off-line Sites), directional navigation with the cone score, `focus_changed(target)` signal up (Signal Up), the flow only answers queries.
5. **Hover = focus** (one code path). The screen derives the dim ladder from the focus target: each target type returns the set of
   related beams / Sites / cards; everything else takes the unrelated level. Pure function of (focus, raid state), unit-testable.
6. **Carried-card state is the screen's**; the flow keeps `sel_card` (click mode) and `place_on`/`unplace`. Esc drops the carried card only,
   B/undo calls `undo()`, X / drag-off calls `unplace(site)`. The two guard slots read `cfg.solace_tide_max_placed` and `raid.place["sentries"].size()`.
7. **`response_preview(resp)`** for every response row the groups already hold: per beam {stop site, tier}, the changed Sites for
   DEPLOY / REDEPLOY / SACRIFICE, and the 12 outcomes. DEPLOY previews `groups` rank 1 and lists the other candidate Sites with their tier.
8. **Sealed inspect queries (no type):** `route_sites(a)`, `route_len_links(a)`, `cands_through(site) -> mask A/B/C`, hunter street target Sites.
9. **Layout services:** UI scale floor (marks never below the 1280 floors), tally grouped form, hand strip mode, safe-box anchoring (HUD to the
   16:9 box), 4:3 tray band, ultrawide extra width as world only, camera fit to the HQ-HOME bounding box with a 6% margin. A `TideLayout`
   helper (RefCounted, pure) returning rects from (viewport size) would make these testable.
10. **Onboarding profile flags** in the saved profile: `tide_seen_type[D,N,E]`, `tide_seen_tier_ramp`, `tide_first_raid_done`,
    idle timer 6 s for the ghost hand (plays once per profile, reduce-motion = cuts). Presentation only, no rule reads them.
11. **Input actions** (`tide_move`, `tide_confirm`, `tide_cancel`, `tide_takeback`, `tide_forecast`, `tide_card_prev/next`, `tide_card_wheel`,
    `tide_target_prev/next`, `tide_pause`) and a prompt-glyph service that reads InputMap and the last device used.
12. **Tests to add (rule 6):** whatif == commit; drop_class never exposes a sealed type; focus order deterministic and skips DOWN; cancel
    never changes `raid.place`; cone navigation picks the lowest score; layout rects stay inside the 4:3 box at 1280.

Art-owned (tide_fx / tide_look): lime bracket decal + dotted inner ring; the dashed preview outline shader; the world-grade shift as a
single post parameter (value / saturation / soft hole by mask) with a 6 f ease in and 3 f out; ghost-program tint; refusal slash decal;
the lifted sealed corridor (lane offset +34 px) and its pip decals; echo rings for the onboarding pulse; the ghost hand sprite.

## Self-score against the REF_BASELINE bar (honest, stills only)
Readability **8** (bar 9, not beaten), Wordlessness **9** (bar 9, matched, provisional).
- Why not 9 Readability: in the dense t1 cluster (three Sites, five ribbons, a DOWN mark) the lime brackets are the only focus
  channel and share the area with the ring, block, tile, old-ring ghost and the wall; the tally ghost row is small at 1920 and gone
  at 1280; the 24% beams are still silhouettes but under tritan the DAMAGED orange / BREACHED red / N magenta collision from pass 2
  carries over into the tally and the hairlines.
- Why 9 Wordlessness: in the clean frames the only characters are numerals (counts, HUD) and the disc word on hover, and every reason,
  preview and state has a shape. It is provisional: no naive viewer has been tested on it.
- Beats the bar on: intent-in-place plus the previewed outcome on the map and in the tally (ITB's best idea, with a diff), a world-grade
  focus shift (CP2077 scanner), one refusal mark, and information about hidden routes with no text (nobody in the baseline has it).
- Could not beat: Mini Metro's calm. This screen carries more states at once and a few of them depend on dashed outlines that
  must survive the squint (see weak points).

## Weak points
1. **Dashed = uncommitted is a thin channel.** It holds at 1920 and 1:1, it blurs at the 320 px squint and is nearly gone at 1280.
   A second channel (a slow brightness pulse on the preview carriers, or a 10% hatch in the ring fill) is needed; motion is
   P1_motion's, so a static fallback is open.
2. **The tally diff is the busiest mark on screen.** Two rows, hairlines and underlines in a 540 px tray. It reads for 1-4 changed
   marks, and for 5+ it is a tangle. A change-count badge or bars may replace the hairlines past 4 changes.
3. **The t1 cluster is still crowded**: lime brackets, old-ring ghost, dashed new ring, block and tile on three Sites 90-190 px apart.
4. **Discs at rest rely on the glyph alone.** DEPLOY and SACRIFICE glyphs are learnable but not obvious; the word shows only on hover.
5. **Pad glyph legibility is untested on a real device**; the four-dot diamond is layout-neutral but slower to learn than letters.
6. **The ultrawide sides are a mock-up** (mirrored, blurred); the real city continues there and could pull the eye.
7. **Lifting a sealed corridor 34 px** works for A/B/C on these streets; on narrow streets it may land on a neighbouring street.
8. **Snap radius (90 px), deadzone 0.35, repeat 12 f, hold 250 ms, the 6 s ghost-hand idle** are my proposals, not tuned.
9. **The 12-outcome list, the outcome-per-route mapping (4 per sealed route, 6 per hunter street) and the stops are illustrative.**
10. Stills only: the grade ease, the pulse, the ghost hand, the wheel and the jitter are unproven in motion.
11. The hand drawn in the ghost-hand frames and the cursor are simple placeholders.
12. `08e` thumbnails are small: they show the light levels, not detail.

## Process notes
- One slip against the hard rules: a bare `python -` heredoc was started once, with an empty stdin, and exited immediately (an
  interactive banner, no code run). No python process of mine remains.
- I also built the H2 frames once by mistake into my own `frames/` (a star-import side effect) and deleted those files by explicit name.
- Nothing outside `P1_interact/` and `D:/rc_scratch/tide_concepts/p1i_work` (a new folder, my cache) was written. `D:/Godot/rebel_cell` was only read.
