# Locked board: final fix pass (O-29) and the grammar check (roadmap steps 1-3)

This pass applies the art director's ranked fixes 1-10 (`../REVIEW.md`, O-29), re-renders the full set and checks the step 3 grammar on the neutral, Solace and Meridian skins. All plates are 1920x1080 on the bio cutaway and use the E10 state (`state_e10.json`). No game number, word or rule changed.

## Files in this folder

| File | What it is |
|---|---|
| `p1_decide.png`, `p2_preview.png`, `p2b_hover.png`, `p3_resolve.png`, `p1_nowords.png` | Neutral skin plates |
| `p1_decide_solace.png`, `p2b_hover_solace.png`, `p1_decide_meridian.png`, `p2b_hover_meridian.png` | Corp skin plates |
| `card_sheet.jpg` | The 11 cards in 5 states: normal, lifted, played slot, unaffordable, nowords |
| `grey_proof.jpg` | Luma-only proof: p1 with the real WPAP cards, hand and tower at 1x, the TOWER/WAVE plates, Solace and Meridian |
| `before_after.jpg` | The locked first pass vs final on p1: plate, hand, digit 0, digit 3, wheel and squint |
| `grammar_check.jpg` | Step 3 crops on three skins, plus every slice colour hatched |
| `checks.json` | All the numbers (sections listed below) |
| `src_snapshot/` | The generator `.py` files, as rendered |

The generator lives in `D:/rc_scratch/combat_redesign/locked/corp/src/`. It is now the single working generator and renders every skin, neutral included. `card_render.py` is identical in `cards/src`, `assembled/src` and `corp/src`. The other board changes were made in `corp/src` only; `assembled/src` and `wheel/src` are the first-pass copies.

## What changed, per fix

**1. Card type colours.** Module: `card_render.TYPES`.
- TOWER is cobalt #2F5BFF with white text: 4.94:1 on its plate, 4.47:1 against the paper.
- WAVE is warm orange #FF8A1F with ink text: 7.86:1 on its plate, 2.04:1 against the paper (the ink keyline and drop carry that edge).
- Bone #F1EAD6 was rendered and checked first. It measures 1.04:1 against the card paper, and the WAVE plate, the corner facet and the nowords plate all vanished into the paper, so orange was used. `CARD_WAVE=bone` still renders the bone variant.
- The +Trace tab stays Trace violet #A03CFF (`TRACE_VIOLET`), so violet now means Trace only.
- TOWER vs WAVE in grey is 2.19:1 (first pass 1.52:1). On `grey_proof.jpg` they separate by value: a dark plate with white text vs a mid plate with dark text.
- Knock-on change: the Spin 3 band moved from tangerine to sun yellow #FFD21F, because a tangerine TOWER card would read as WAVE orange.
- The multiplier plate text follows the type text colour (white on cobalt).

**2. Sector digits.** Modules: `r2_sched`, `f1_render`, `lw_install`.
- Root cause: the digits were drawn before the ring cells, and the cells covered their inner half. That is why digit 3 read as "J" and digit 0 as an arch.
- Digits now draw on their own layer (`Ldg` in `f1_render._render`), above the cells, tape, plates and tags.
- Digit 0 sits at -4.5 degrees (`r2_sched.DIGIT_ANG`), clear of the THIS TURN tape start.
- `r2_sched.punch_digits` cuts a hole of boss radius + 2.6 px out of the tape/plate layer and the label layer at every digit, so digit 3 has its own gap in the HOLD THEN plate.

**3. Hand vs board.** Module: `f1_hand`.
- Settings are now CARD_SCALE 1.10, STEP 168, LEFT_CX 1023, CY0 924, HOV_PUSH 16. They were 1.15, 182, 962, 910 and 30.
- At 1.15 x, no shift fits in front of SEND IT while keeping the Trace tab and the x3 plate uncovered. At 1.10 x it fits, and title cap height is still 35.9 screen px (FIREWALL 32.4; the rule is 30 or more).
- `f1_hand.HAND_MIN_R = 455` is asserted in `asm_render`.
- Measured: the hand's closest pixel is 458.9 px from the board centre on every plate, with 0 px inside r455 and 0 px over any board mark, tape or plate.
- The hand still covers part of the outer rim between r455 and r500. That is allowed by the 455 rule.

**4. Played slots.** Module: `card_render._liner`. The card name is printed above PLAYED in the same mono small caps, at 70 % opacity. On p3 the slots read TWIST, TRIGGER and BRACE.

**5. Meridian rim.** Module: `cs_skin.Meridian`.
- `hazard_paint()` cuts the stripe chroma by 25 % toward the grey of the same luminance (`HAZ_DESAT`), on the rim and on the bezel lip.
- The inner bezel lip touches the amber Adjuster arc and the HOLD plates, so it is now black with no stripe. That gives a black gap.
- Rim stripe mean saturation: 0.894 before, 0.749 now.
- Hazard pixels in the bezel: 2253 before, 309 now.
- Smallest gap between an amber game mark and hazard paint: 5.7 px before, 37.4 px now.

**6. WPAP facets.** Module: `card_render.facets(..., T)`.
- Four planes: two in the type colour at 32 %, two in the type's dark at 28 %. Each has a 0.7 px ink cut edge.
- A white glint plane at 25 %.
- All inside the 25-35 % brief (`FACET_OP`).

**7. Spin family.** Modules: `card_render.spin_arcs`, `ART[..]['dot_k']`.
- The arcs are now drawn after the facets, so the facets no longer wash them out.
- Each arc is a concentric solid ink stroke, 3.7 px on screen, with a paper keyline and an arrow head.
- The arcs are 14.3 px apart centre to centre: 10.6 px clear between the ink strokes, 7.5 px between the keylines.
- The Ben-Day dot density steps up with the turn count: 0.55, 0.85, 1.15.
- Three band hues: sky (Nudge), mint (Spin 2), yellow (Spin 3).

**8. Icon discs.** Module: `card_render.ART`.
- Brace, Firewall, Pull, Shove and Twist take ink discs, with owner pink kept in the misprint crescent.
- Trigger takes a pink disc.
- Hold keeps its pink disc. A black toner pool now surrounds the icon, because the cyan spot block used to run up to the halo.
- Disc vs the art around the halo, all 11 cards at 2.5:1 or more: Strike 6.41, Spin 3 5.69, Hold 4.77, Nudge 4.34, Twist 3.54, Pull 3.50, Spin 2 3.31, Trigger 3.21, Brace 2.69, Firewall 2.65, Shove 2.53.
- Glyph vs disc is 12.1 to 17.7 on the dark discs. It is 3.1 on the two pink discs, where the glyph's ink keyline (17.7:1) carries it.

**9. Tower loudness.** Module: `lw_tower`.
- Pink halo value down 10 % (`HALO_K` 0.90).
- Texture, including the Ben-Day rings, down 10 % (`TEX_K` 0.90).
- Wedge spot ink at 84 % value (`FILL_K`; the O-28 seats keep full ink so the type still reads).
- Paper at 0.76 value (`PAGE_V`, was 0.86).
- Tower zone loud share on p1: 56.4 % before, 48.6 % now. Other plates: p2b 47.6, nowords 49.0, Solace and Meridian p1 48.6.
- p2 (57.9) and p3 (57.5) are still above 50 %, down from 65.3 and 64.4. In those beats no slice carries the darkening hatch, and the yellow and green inks are loud at any usable value. See "Not done".

**10. Checks re-run.** Every plate was re-rendered with checks on. The occluder and hand-vs-board asserts were added, and each skin got a squint and a grey proof (see `checks.json`).

## Other fixes found in this pass

- **THIS TURN tape edge.** The 1 px orange lip turned into a dotted line once it was remapped to silver, which breaks the no-dashes rule. The tape edge is now the solid ink keyline only (`lw_install.install` sets `S2.LIVE_LIP` to ink).
- **Ring tag and badges on the schedule band.** The "+2 W3" ring tag and one warded badge sat on the tape (54 px and 129 px of overlap).
  - `r2_misc.tag_geom` now pulls a tag inward until its corner clears `BAND_EDGE = 388`.
  - `asm_units.hits` has a new `band` count, and badges shrink or flip until it is 0. Each badge now gets one more draw assert, so the totals are 63 / 49 / 24 instead of 60 / 46 / 21.
- **FAR chevrons on Meridian (step 3).** The graded FAR harm colour, a dark brown (85, 70, 72), measured about 1.1:1 on Meridian's oxide cells and disappeared. FAR harm marks now use `f1_board.FAR_CHEV` #96767A. It keeps 25 % chroma but has a lifted value, the same way R51 lifted COLD. The value order HOT > COLD > FAR still holds on every skin.

## Check numbers (`checks.json`)

**Pass/fail summary (`all_pass`):** draw asserts, mark collisions, occlusion, hand and dashes all pass.

**Draw asserts:**
- p1, nowords, Solace p1 and Meridian p1: 63/63.
- p2 and p3: 49/49.
- p2b on all three skins: 24/24.

**Collisions and occlusion:**
- Mark pairs (digits, labels, tags, badges, tickets, leader): 0 px on every pair, on all 9 plates.
- Marks against occluders (THIS TURN tape, hold and +N plates, hand): 0 px on all 9 plates.
- Two pairs are allowed by design:
  - a HOLD label on its own plate;
  - the 1.6 px hover leader crossing the schedule band once to reach its tag, 228 px on p2b. The leader is a separate mask class and is still tested against digits, labels, badges and the hand.

**Dashes:** 0 dash calls and 0 dotted-mark calls on all 9 plates.

**Squint, p1 neutral, whole plate (mean / p95 / loud share):** final 0.229 / 0.494 / 12.4 %; first pass 0.233 / 0.504 / 14.0 %; E10 0.184 / 0.368 / 4.1 %.

**Squint, p1 by zone (loud share):**

| Zone | Final | First pass |
|---|---|---|
| Tower | 48.6 % | 56.4 % |
| Rings | 5.5 % | 6.7 % |
| Hand | 45.3 % | 50.6 % |

**Corp skins:**
- Tape matches the neutral tape on 100 / 97.7 / 98.0 % of pixels (neutral / Solace / Meridian).
- Pink in the enemy zone: 0.228 / 0.228 / 0.229 %.
- Unit-kind dE2000, plate read-back, ring 0 Packet-Worm: 14.6 / 20.8 / 15.8. Swatch minimum per ring: Solace 6.8 / 4.3 / 2.5, Meridian 7.2 / 4.5 / 2.7 (unchanged code).

**Grammar (`grammar_step3`), sector 3 chevrons against their cell, luma contrast and dE:**

| Skin | HOT | COLD | FAR |
|---|---|---|---|
| Neutral | 3.12 / 48 | 3.59 / 43 | 2.81 / 30 |
| Solace | 3.11 / 54 | 3.38 / 48 | 2.71 / 38 |
| Meridian | 2.89 / 38 | 3.17 / 35 | 2.46 / 23 |

**Hatch swatches laid on each skin's own ring cell (luma contrast, neutral / Solace / Meridian):** red 2.9 / 2.6 / 2.9, pink 3.0 / 2.8 / 3.0, blue 2.6 / 2.4 / 2.5.

**Hatch on the slice inks:** red on BURST pink is 1.30:1 (dE 28) and on REPAIR green 1.28:1 (dE 70). These separate by hue and by the ink keyline under every hatch line (red vs ink 5.7:1). On the crops they read: the slice darkens and shows the cross-hatch, and the O-28 seat keeps the type.

**Game info:**
- All 11 cards match the state for cost and Trace.
- Every hand card draws its name, type, rules, cost, Trace tab and multiplier on every wordful plate.
- No required word is missing on any plate.
- nowords has 0 alphanumeric text calls.
- Tower numbers (pips, HP ring, trim) match on f1, f2, f2t and f2b.

## How to render

From `D:/rc_scratch/combat_redesign/locked/corp/src`. Use one process per skin, because the skin is installed at import.

```
CORP=neutral|solace|meridian python asm_render.py <p1|p2|p2b|p3|nowords> [bio|srv|gh] [check 0|1]
    -> ../out/as_<beat>[_<room>][_<corp>].png, ../work/chk_<...>.json (asserts, overlaps, occlusion, hand), ../work/masks_<...>.npz
python ../../final_work/render_set.py -j 5 p1 p2 p2b p3 nowords p1:solace p1:meridian p2b:solace p2b:meridian   (parallel driver)
python final_publish.py      # copies out/as_*.png to locked/final/<plate>.png
python asm_numbers.py        # tower numbers vs state -> work/numbers.json
python final_cards.py all    # card_sheet.jpg + work/card_checks.json   (about 4 min)
python grammar_check.py      # grammar_check.jpg + work/grammar_check.json
python final_checks.py       # checks.json, grey_proof.jpg, before_after.jpg
```

A plate takes about 1-4 minutes. Cards are cached in memory per process. Tower images are cached in `corp/work/tower_*.png`; delete those files after changing `lw_tower`.

## Entry points for other designers

**Render a plate in a given state and skin (Python):**
```python
import os; os.environ['CORP'] = 'meridian'        # before the import; 'neutral' | 'solace' | 'meridian'; LW_SKIN=0 = unskinned F1 board
import lw_render as LW                            # installs the player family (lw_tower, lw_ui, card hand) and the corp skin
img = LW.R.render(beat,                           # 'p1' | 'p2' | 'p2b' | 'p3' | 'nowords'  (f1_render.render -> _render)
                  room=None,                      # backdrop png path (default bio; asm_render.ROOMS has srv / gh)
                  frame=None, tag=None,           # a custom state frame (dict shaped like state_e10.json['f1']) and its cache tag
                  hover_unit=None,                # unit id: switches to the hover layout (others dimmed, hover path, cell, tag)
                  lift=None,                      # card name to lift in the hand ('Trigger')
                  hand_dim=None,                  # extra value multiplier on the resting hand
                  hand_beat=None,                 # draw the hand of another beat
                  arcs_skip=(), hide_units=(),    # drop landing arcs / units by id
                  trim=True, with_ui=True,
                  extra=None)                     # callback extra(bg_rgba, frame): your layer, composited above board + HUD, below hand / UI
img.save('out.png')                               # RGB 1920x1080
```

**Overlay effects or hover layers:**
- Pass `extra=lambda bg, f: bg.alpha_composite(my_rgba_1920x1080)`. The layer sits above the board, tower and HUD and below the hand, SEND IT and nameplate. This is the slot for slice-wide or cell-wide effects in step 4.
- To draw above the hand, composite onto the returned image.
- Draw at board coordinates with `cv_lib.L2()`, a 2x supersampled transparent layer. `L.done()` returns it at 1x. Positions come from `cv_lib.ppx(C, r, angle_deg)`; the centre `C` is (536, 540), and angle 0 is 12 o'clock, clockwise.
- Useful radii:

| Element | Radius (px) |
|---|---|
| Tower | 196 |
| Ring 0, the NOW ring | 214-271 |
| Ring 1 (+1) | 271-328 |
| Ring 2 (+2) | 328-385 |
| Schedule band | 391-417 (keep marks inside `r2_misc.BAND_EDGE = 388`) |
| Landing lanes | 436, 453, 470 |
| Rim | 489-500 |
| Hand | must stay outside 455 |

- Existing hover pieces:
  - `a2_hover.hover_path`, `hover_cell`, `hover_tag` and `leader`;
  - `f1_tower.draw_hover_arcs(canvas, sectors)` on the tower;
  - the p2b path in `f1_render._render` shows the order: dim the others with `A.DIM_K`, then the hover path, cell, tags and tag box.
- Add any new mark class to the collision test the way `asm_render._cap(cls, module, fn)` does it, and to `MARKS` / `OCCLUDERS` there.

**Draw a card:** `card_render.draw_card(card, size, state)` returns RGBA. Its canvas is the card box plus `margin_px(size)` on each side.
- `card`: a name such as `'Brace'` or `'Spin3'`, or a dict of overrides.
- `state`: `'normal' | 'hover' | 'played' | 'unaffordable' | 'nowords'`, or `{'mode', 'dim', 'nowords'}`.
- In the hand, cards are placed by `f1_hand.draw_hand` at `CARD_SCALE` 1.10 and passed `size=352` (2x).

**Draw the tower:** `lw_tower.render_tower(frame, name='BREAKER', skip_trim_units=None, hot=True, with_trim=True)` returns `(RGBA image, canvas)`, centred at `xf_tower.CT`. Paste it at `C - CT`. The loudness knobs `PAGE_V`, `HALO_K`, `FILL_K` and `TEX_K` are module globals.

**Skin hooks:**
- `lw_install.install(skin)` patches the enemy layers to call the skin, and `lw_render` calls it at import with `NeutralSkin()` or `cs_skin.SKINS[CORP]`.
- A skin is a class with:
  - `name`;
  - `pal` (a colour dict);
  - `kind_gain` (per ring; Lab push of the unit kind washes);
  - material functions `(X, Y, RHO, TH) -> (rgb, alpha)`: `cell`, `bezel`, `annulus`, `rim` and `arcframe`;
  - vector pieces drawn on an `L2`: `rim_vector`, `crest`, `cell_detail`, `token_frame`, `disc_frame` and `ticket`;
  - optional `empty_marks` and `rim_vector_after`.
- Subclass `lw_skin.NeutralSkin` or `cs_skin.Skin` and register the class in `cs_skin.SKINS`.
- The THIS TURN tape is not a skin layer: `lw_skin.NeutralTape` remaps it to silver for every corp. HP, the hatch, HOT/COLD/FAR and outlines are game marks, and skins must not touch them.
- Only Solace keeps the helix rule; `install` turns it off for any other skin, so switching back to Solace later in the same process loses the helix. Use one process per skin.

## Not done, and risks

- **Tower loudness on p2 and p3:** 57.9 % and 57.5 % loud, above the 50 % target. The target is met on p1, p2b, nowords and both corp p1 plates. Getting there on p2/p3 would mean dulling the yellow and green slice inks, or greying the paper further. That is a designer call.
- **Card size:** cards in the hand are 1.10 x now, not 1.15 x, so they clear r455. The rim between r455 and r500 is still under the Brace card's corner, and the card bottoms touch the screen edge.
- **The dying Worm's chevrons:** they are deliberately dark, because they will not land. On Meridian brown they are faint, which fits their meaning but reads weakly.
- **Not done here:** Meridian stencilled numbers. Solace ring 0 `kind_gain` was not lowered. Ring 2 unit kinds stay close (minimum dE about 2.5), so the glyph carries kind there.
- **The hover leader still crosses the tape.** It is allowed and documented, not removed.
- **Process note:** I ran a bare `python -` once by mistake. It got no stdin code and wrote nothing, and I stopped it. I also ran two empty `python -c` calls by reflex. All real work ran from script files. No Godot, no Blender, nothing committed, nothing under D:/Godot/rebel_cell.

## O-30 pass

This pass applies the art director's ranked fixes 1, 2, 3, 5, 6 and 8 from `../REVIEW_FINAL.md` ("Top fixes, ranked"). All 9 plates, `grey_proof.jpg`, `grammar_check.jpg`, `before_after.jpg` and `checks.json` were re-rendered from `corp/src`. `before_after.jpg` still compares the locked first pass with this final. `card_sheet.jpg` was not re-rendered: no card code changed. No game number, word or rule changed. The E10 state is unchanged, and draw asserts, required words, card fields and tower numbers all match it.

**Fix 2: room grade.** The step-6 grade is now the default room grade of the generator.
- `corp/src/bd_grade.py` is the `backdrop/src` grade, with the per-room parameters from `../backdrop/grade.json` (step6-1) built in.
- `room_grade()` picks the room from the active `room_<n>_bare.png`, and `lw_render` installs it in place of `r2_ground.grade`. `BD_GRADE=0` brings back the old grade.
- The board scrim is unchanged.
- Squint on p1, room zone (x >= 1100, y >= 420, outside the hand), mean / p95 / loud: 0.134 / 0.235 / 0 %. The first pass was 0.194 / 0.353 / 2.0 %, and E10 was 0.179 / 0.323 / 0.7 %.
- Whole p1 plate: 0.205 / 0.493 / 12.2 %. These match the backdrop/ composites.

**Fix 3: beaded rows.**
- What they encode: the beads are the FAR (+2 turns) threat trim on the tower rim. That is zone k = 2 of `f1_tower.draw_trim`, a threat landing on that slice in two turns. The bead count meant nothing in the game: it was the arc length divided by 7.4 px, so 8-9 beads on every zone. The game information is the zone itself plus its two pips (k = 2), and both are kept.
- The fix: FAR is now one solid tapered stroke on the same arc, drawn by `f1_tower.far_stroke`.
  - It is 4.6 px wide at the middle and tapers to 1.4 px at the ends, with a 1.3 px ink keyline.
  - It keeps the FAR colour and the two pips.
  - Value order stays HOT (bold band, notch, glow) > COLD (band, one pip) > FAR (thin stroke, two pips).
- Trim zones match the state on f1, f2, f2t and f2b (`checks.json` `game_info.tower_numbers`).
- New pixel audit, `corp/src/dot_audit.py`. It works on the rendered pixels:
  - It finds small spots: |DoG| of luma over 14, area 3-70 px, round.
  - It drops 2-D halftone fields: any spot with 4 or more neighbours within 14 px, or with 3 or more within 1.5x its nearest-neighbour distance (the edge row of a field).
  - It reports runs of 5 or more spots that are evenly spaced (spacing CV <= 0.18, 3.5-16 px), the same size and colour, and on a smooth path.
- Result: 0 runs on all 9 final plates. The first-pass plates score 1-11 runs each (p1: 5), the bead rows among them. The audit runs in `final_checks.py` (`dash_audit.*.pixel_dot_runs`, `all_pass.pixel_dot_runs`) and in `hz_publish.py` for hover.

**Fix 6: HOLD THEN.** `r2_sched.HOLD_LABEL_SHIFT = 8` px moves every non-live HOLD label along the arc, away from the next digit. Digit 3 now has a clear gap from the N (crop on `before_after.jpg`). HOLD NEXT moves the same 8 px, away from digit 2.

**Fix 8: one generator.**
- The hover generator (`hz_*.py`, `hv_lib_h2.py`, `plan_patch_h.py`) is merged into `corp/src`. The rest of `hover/src` differed from `corp/src` only in output paths, so nothing else needed merging.
- Hover now renders from `corp/src`. It writes to `locked/hover/{out,chk,logs}` and shares the tower and card caches in `corp/work`.
- `hz_set.py` is the parallel driver.
- `locked/hover/src` is now a stale copy, kept only for reference.

**Fixes 1 and 5** are hover fixes. See `../hover/NOTES.md`, "O-30 pass". They do not change the final plates: no final plate lifts a card from slot 0.

**Checks (`checks.json`).** `all_pass` is true for draw asserts, collisions, occlusion, hand, dash calls and pixel dot runs.
- Draw asserts: 63/63 on p1, nowords, Solace p1 and Meridian p1; 49/49 on p2 and p3; 24/24 on p2b on all three skins.
- Hand: closest pixel 458.9 px from the board centre.
- Tape match: 100 / 97.7 / 98.0 %. Enemy-zone pink: 0.228-0.229 %.
- Tower loud share: 48.8 % on p1, 57.9 % on p2, 57.7 % on p3, 47.6 % on p2b. p2/p3 are still a designer call; this pass did not change it.

**Not done.**
- Fixes 4 (full resolve beat flash meter, reduce-motion blocks), 7 (effect layer) and 9 (latent effects) were not in this brief.
- The effect bases and the T5/T6 end frames still use the old grade. Re-render them from `corp/src`: the new grade is now the default.
- The beads also show on the effect strips and on `block_vs_break`. Those were not re-rendered.
- `src_snapshot/` was refreshed (`.py` only).
- Process note: I ran a bare `python -` once by mistake (an empty heredoc), which the hard rules forbid. It ran no code and wrote nothing, and I stopped it. I also ran one `python -c` JSON print. Every other step ran from script files. No Godot, no Blender, nothing committed, nothing under D:/Godot/rebel_cell.
