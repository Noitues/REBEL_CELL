# Hover plates on the final locked board (roadmap step 5)

These are the 11 per-card hover plates and the grammar key from `../../hover_final/`, re-rendered on the final locked board (O-29 fix pass, `../final/`). They use the neutral skin, the final WPAP cards and the xerox/linocut spinner. Brace (h02) and Twist (h04) are also rendered on Solace and Meridian. All plates are 1920x1080, bio room, E10 state (`state_e10.json`, turn 2). No game number, word or rule changed.

Start with `contact_sheet.jpg` (all 11 plates plus the key) and `h00_key.png` (the grammar).

## Files

| File | What it is |
|---|---|
| `h00_key.png` | The hover grammar key. Marks are drawn with the plate code at use size; the crops are 1x from the plates. |
| `h01_tower_turn` ... `h11_unit` `.png` | One plate per card effect type |
| `*_nowords.png` | All 11 without words (0 alphanumeric text calls) |
| `h02_brace_solace/_meridian`, `h04_twist_solace/_meridian` | Corp skins |
| `contact_sheet.jpg` | All 11 plates at small size, plus the key |
| `checks.json` | `all_pass`, a per-plate `summary`, and the `full` per-plate reports |

## What is recomputed, and how

Every plan comes from the E10 sim (`hover_sim.frame`, read only), with the card actually played: the tower angle, guns, landing arcs, kills, refunds, RAM, TRACE and the bill. Ghosts are the sim's plan units, drawn by the board's own unit and arc code at 74 percent. None of them is a shifted copy. The live frame from the sim equals `state_e10.json` f1 exactly (every unit record matches).

| Plate | Card (sim action) | What the plan changes (sim) |
|---|---|---|
| h01 | Spin 3 `(Spin3,3)`; insets Spin 2 `(Spin2,2)` and Nudge `(Nudge,1)` | Tower drawn at the plan angle (rot 3), with guns and landings at plan values. LANDS 12 -> 13 and RAM 4 -> 3. Each inset is its own sim plan. |
| h02 | Brace `(Brace,2)` | Clamp on the TURRET slice. LANDS/THROUGH 12/6 -> 9/4 and HP after 9 -> 11. The clamp ghost is the plan tower's own brace plate, cut to the plate band at 74 percent. The pencil bars sit on the landing arcs that now stop. |
| h03 | Trigger `(Trigger,4)`; inset Twist + Trigger | The Payload resolves now down sectors 3 and 4 and kills the ring NOW Packet: all 5 HP are hatched and its arc is gone. 12/6 -> 6/3, HP after 9 -> 12, RAM 4 (1 spent, 1 refunded; green ring on the refunded coin) and TRACE 3 -> 4. |
| h04 | Twist `(Twist,(1,1))` | Ring +1 turns one extra sector. Payload lands [0,5] -> [0,1] and Packet [2] -> [3]; their arcs get a pencil edge, and the twist pill sits on the +1 tag. |
| h05 | Strike `(Strike,5)` | The Packet on ring +1 dies (2 HP hatched as lost at END TURN), and its landing arc is gone. The bill is unchanged, because it lands next turn. Corners mark every legal target, including the Adjuster. |
| h06 | Shove `(Shove,(5,1))`; inset bump `(Shove,(1,1))` | The ghost Packet sits at sector 1 with its plan arc ([3], 0 through). The origin is veiled. The inset is a real sim bump: the Packet and the Worm each lose 1 HP. |
| h07 | Pull `(Pull,7)`, the only legal Pull | The Packet goes from ring +2 to ring +1 and lands a turn sooner (k 2 -> 1). |
| h08 | Hold `(Hold,0)` | Schedule 2.0.0 -> 0.2.0. The band shows HOLD THIS TURN and +2 NEXT; the PLAN arrow outside the rim runs from the THIS TURN slot to NEXT. The Payload now lands [3,4] and the Packet on ring +1 now dies, both recomputed by the sim and edged in pencil. The bill is unchanged. |
| h09 | Firewall `(Firewall,0)` | Burns come from the sim (`hurt` wrapped during the plan preview): the Payload loses 0 (armour, so no burst) and the 9-wide Packet loses 1 (hatched, burst). RAM 4 -> 2 and TRACE 3 -> 5. |
| h10 | Soak toggle, END TURN option `[1]` | The SHIELD slice at sector 1 soaks. THROUGH 6 -> 5 and HP after 9 -> 10. The board's own indigo soak pip and the SOAK hatch on the bill carry it. |
| h11 | Unit hover (the p2b form) | The board's p2b route, cell brackets and tag (content parked, note 8). The hover dim sits on top, and the landing slices get a pencil rim. |

## The grammar on every plate

The grammar is unchanged from `hover_final`. Only positions moved to the final board's geometry: tower r197, rings 214/271/328/385, band 391-417, lanes 436/453/470.

- **Dim.** Value x0.40, chroma x0.45 outside the lit mask. The hand not in play is at 70 percent; UNDO, SEND IT and the nameplate are at 62 percent.
- **Focus.** Lime corners only: 2 px for a legal target, 3.5 px for the aimed one. Each corner is placed on its own, and it slides up to 12 degrees inward if it would touch a digit, label, tag, badge or ticket. 0 corners were dropped on any plate.
- **PLAN arrow.** The yellow arrowed outline is used for movement only: the tower turn, Shove, Pull, the Trigger resolve path, the Twist ring and the Hold step.
- **Ghost.** 74 percent, with a pencil outline; the origin is veiled.
- **Pencil ring.** On every number the plan changes: LANDS and THROUGH, the YOU pips that change, spent RAM coins (from the HUD's own pip registry) and added TRACE pips (a square).
- **Hatch.** The board's own HP grammar, with the hatch colour set by the cause.
- **Burst.** Only on a hit that removes HP. It sits beside the token, never on it.
- **Lifted card.** The lifted card is the locked WPAP hover card on its pink print. When the lifted card sits in slot 0 (Brace and the showcase cards), the whole fan slides right by 32 px and the lift is 40 px lower (LIFT_CY 906), so no hand pixel enters r455 (measured minimum 455.6). The lifted card covers its neighbour exactly as a normal lift does.
- **Z-order.** Board digits, labels, tags, badges, tickets, the THIS TURN tape and the label plates are drawn back on top of the hover marks. The number of pixels a mark would otherwise have covered is reported per plate (`z_order`). Most come from ghost cells: on h06 the ghost cell sits under the +1 W2 tag, 1079 px.

## Checks (`checks.json`)

**`all_pass` is true on all 26 plates:** draw asserts, mark pairs, occlusion, hover marks vs board marks and occluders, hand vs board, dashes, and nowords text.

**Draw asserts.**
- They run on the board frame of every plate: 64/64 (h01), 63/63 (h02, h04, h09, h10), 62/62 (h05-h08), 56/56 (h03), 24/24 (h11).
- They also run on every inset render: Spin 2 63/63, Nudge 63/63, Twist + Trigger 56/56, Bump 63/63.
- Ghost landing arcs are asserted against the plan frame (rows, diamonds = HP through, chevrons, k dots, soak and clamp marks): h06 and h07.
- h03 and h05 draw the units the plan removes as dying (`as_dying`: HP hatched, no arc), so the asserts check the plan bill.

**Collisions.** These use the asm_render capture and occluders (tape, plates, hand), with three new classes: `hover`, `ghost` and `inset`.
- Mark pairs are 0 px, and occlusion is 0 px, on every plate.
- hover/ghost/inset against digits, labels, tags, badges, tickets, tape, plates and hand: 0 px.
- Overlap with units and arcs is reported as info only, because corners and arrows sit on cells by design.

**Dashes.** 0 dash calls and 0 dotted calls.

**Squint (whole plate, mean / loud share).**
- Mean 0.13 to 0.18 and loud 5 to 11 percent, against final p1 0.229 / 12.4 percent. Dimming lowers the whole plate, as intended.
- lit/dim luma ratio 1.20 (h03) to 1.86 (h10 nowords).
- Tower loud share where the tower is lit: h01 37.6, h02 53.4, h10 47.4 percent.

**Corp skins.** The same asserts pass (63/63). Hover marks are game marks, so the skins do not touch them.

## Not done, and risks

- **Slot-0 lift.** The 32 px fan shift moves the Twist card's right edge under the UNDO and SEND IT plates, which are drawn on top as on the locked board. It hides about 8 px of card frame and no words. The lifted card also sits 40 px lower, so its bottom triangles touch the screen edge. The alternative is a smaller lift scale.
- **Hover labels.** The Firewall flame strokes and the Hold arrow outside the rim are my own placements on the new geometry. Twist + Trigger gives the same bill as Trigger alone in this state; I kept the inset from the old plate set.
- **h05.** In this state the Strike kill does not change this turn's bill (k = 1), so no hero number is ringed.
- **Process.** I ran a bare `python -` twice by mistake (empty heredocs). Both hung waiting on stdin and were stopped, and neither ran any code or wrote anything. All real work ran from script files. No Godot or Blender was used, nothing was committed, nothing was written under D:/Godot/rebel_cell, and no shared generator file was edited.

## How to render

The generator is a private copy of the final locked generator (`locked/corp/src`), at `D:/rc_scratch/combat_redesign/locked/hover/src/`. Paths point at `locked/hover/`. The new files are `hz_core.py`, `hz_plates.py`, `hz_run.py`, `hz_key.py`, `hz_publish.py` and `hv_lib_h2.py` (the hover_final mark library).

```
CORP=neutral|solace|meridian python hz_run.py h01 h02 ... h11 [hNN:nw]   -> ../out/<name>.png, ../chk/<name>.json
python hz_key.py        # h00_key.png (needs h01 h02 h04 h05 h06)
python hz_publish.py    # copies to locked/hover/, contact_sheet.jpg, checks.json
```

## O-30 pass

This pass applies the art director's fixes 1, 2, 3, 5 and 8 from `../REVIEW_FINAL.md`, and fix 6 through the board. All 26 plates, `h00_key.png`, `contact_sheet.jpg` and `checks.json` were re-rendered. No game number, word or rule changed. Every plan still comes from the E10 sim, and the draw asserts pass on every plate and inset (64/64 down to 24/24, as before).

**Fix 8: one generator.** Hover now renders from `D:/rc_scratch/combat_redesign/locked/corp/src`, the single working generator.
- The hover files (`hz_*.py`, `hv_lib_h2.py`, `plan_patch_h.py`) were merged into `corp/src`. The rest of `hover/src` differed from `corp/src` only in output paths.
- `hz_core.HERE` still writes to `locked/hover/{out,chk}`. Caches are shared in `corp/work`.
- `locked/hover/src` is now a stale copy; do not edit it.
- Render commands, from `corp/src`:
  - `python hz_set.py -j 5 all` renders all 26 plates in parallel, one process per plate (logs in `locked/hover/logs/`).
  - `CORP=<skin> python hz_run.py hNN[:nw]` renders one plate.
  - Then run `python hz_key.py`, then `python hz_publish.py`.

**Fix 1: HUD words are an occluder class.**
- While the board renders, every word drawn through `hud2.txt` or `obj2.txt` records its text box as `hud_labels`. These are the column labels (LANDS, THROUGH, RAW, SHOT, BRACE, RIDER, ...), the row tags, and RAM / TRACE.
- The hero digits (or their nowords proxies) and the arrow are recorded as `hud_hero`, by capturing `hud2.hero_pair`.
- Both are occluders in the hover collision test (`hover x hud_labels`, `hover x hud_hero`). `hud_labels` is also restored on top in `compose`.
- `hud_hero` is tested on its glyph fill: a mark may lie on the digit's 2 px black keyline, never on the digit.
- `hz_core.fit_oval` places every HUD pencil mark (LANDS / THROUGH, YOU pips, RAM coins). In order, it tries:
  1. the normal ring, then wider, flatter and less drifting rings, nudged up and down;
  2. an open horseshoe;
  3. pencil brackets "( 9 )".
- A candidate passes only with 0 px on the forbidden masks, measured on the real drawn ring.
- On the bill, the hero digits sit only 2-4 px from the labels above and below, so no closed ring fits. LANDS / THROUGH therefore take pencil brackets: h01, h02, h03 and h10 (h03 nowords THROUGH takes the horseshoe). RAM, YOU and TRACE keep their rings.
- Result: `hover x hud_labels` and `hover x hud_hero` are 0 px on all 26 plates. BRACE on h02 and SHOT on h03 are uncut (`all_pass.hud_labels_clear`).
- The key's PENCIL RING entry now shows the bracket form.

**Fix 5: slot-0 lift.**
- `hz_core.ui_layers` measures the lifted card on its own: the other cards are drawn transparent. The card must keep every pixel outside r459 (r455 + `LIFT_CLEAR` 4 px) and stay 3 px clear (`LIFT_ARC_GAP`) of every landing mark (`MASKS['arcs']`). The whole hand still keeps outside r455.
- The search tries lift scale (1.10 / 1.07 / 1.04), lift height (866-906) and fan slide (0-96 px), and takes the least total move.
- Result: lift scale stays 1.10 and the lift stays 906 on every slot-0 plate.
  - h05, h06 and h08 slide 36 px: lifted card r min 459.1.
  - h02, h07 and h09 slide 52 px: lifted card r min 473.2. Here the Brace card's corner also has to clear the landing diamonds on lane 470.
  - 0 lifted-card px near a landing mark on every plate (`hand_vs_board.lift_*`).
- The lifted card covers part of its neighbour, as every lift does. On h02 the Spin 3 rules line reads "urn the tower 3" under the lifted Brace (before: "Turn the to..."). The Twist card sits a little further under UNDO / SEND IT, with no words lost.

**Fix 2: room grade.** The plates use the step-6 room grade (`corp/src/bd_grade.py`, now the default). The dim then applies on top as before.

**Fix 3: beaded rows and dot audit.**
- The FAR trim is a solid tapered stroke (see `../final/NOTES.md`).
- `hz_publish.py` runs `dot_audit.py` on every published plate (`pixel_dot_runs`).
- Dimmed to 40 %, Meridian's hazard stripes on the bezel lip and the rim read as dashed lines. `hz_core.soften_hazard` blurs those two bands into a flat dim band, only at angles where nothing in the band is lit. That brought h02 Meridian from 3 runs to 0, and h04 Meridian from 6 to 1.
- Result: 25 of 26 plates have 0 runs.

**Fix 6.** The HOLD THEN label moved 8 px off digit 3 on the board (`r2_sched.HOLD_LABEL_SHIFT`). It shows on h08.

**Not done and risks.**
- **h04 Meridian keeps 1 dot run** (`checks.json` `all_pass.pixel_dot_runs` is false only because of it). It is 5 faint spots at (780-797, 333-355). The Meridian corrugated cell ribs meet the ring gutter edge, and that leaves a row of light dots along the edge next to the Twist PLAN channel. It is the skin's material texture, not a drawn mark. The fix belongs in `cs_skin.Meridian` (rib phase or edge line). The same texture is on the Meridian board plates, where the audit's field rule drops it.
- **Brackets instead of rings on the bill digits** is a small change to the grammar. The key documents it. The alternative is moving the HUD rows apart, which is a HUD layout change.
- **Tower loud share on h02** is still 53.4 % (designer call, unchanged).
- **Process note:** I ran a bare `python -` once by mistake (an empty heredoc), which the hard rules forbid. It ran no code and wrote nothing, and I stopped it. I also ran one `python -c` JSON print. Every other step ran from script files. No Godot, no Blender, nothing committed, nothing under D:/Godot/rebel_cell.
