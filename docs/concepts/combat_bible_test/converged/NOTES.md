# Converged Shifting Waves (art-pass, 2026-10-28)

State: D4_E5 sim, seed 4, turn 2 (same as waves_e5). p2 uses the E5 convention: a hypothetical hand with Twist in place of Spin3 (Twist is not in the real seed-4 hand). p3 = the sim's best plan (Firewall + Nudge + Pull).
Files: `p1_decide`, `p2_preview`, `p2b_hover`, `p3_resolve`, `p1_nowords` (png), `compare_converged.jpg`, `cold_p1_nochips.png`, `e7_readiness.jpg`, `BIBLE_AMENDMENTS.md`, this file.
Work files: `D:/rc_scratch/combat_polish/CV_waves/` (`src/dump_cv.py` imports the sim read-only and writes `state_cv.json`; `src/check_cv.py` -> `check_cv.txt`; build `src/cv_build.py all`).

## What is built
- One board, top-down camera, so the three rings are concentric (no foreshortening). Code base r170 (family-C CRT slices, hub core), HP ring around it (60 segments, predicted loss hatched), 3 ring cells (76 px thick) as bible cells in the Meridian bezel with each unit's programme screen, Meridian wave bezel with the schedule as bezel cells, sector digits, needle.
- Unit = token on a lane-style base (now solid red / +1 pink / +2 dashed), value, HP, arrival sector; Adjuster is a unit cell (skull) in ring 1.
- Chrome per the bible: result chips beside HP, NEXT rows, closing bill line, terminal RAM/TRACE, CELL-9 sticker, SEND IT vinyl, vinyl cards with TOWER/WAVE bands, bit shards and popped numbers on p3, grease pencil only for the p2b hover path (and the p2 underline), round31 backdrop at the bible dim.
- Real 3D: none needed; the only 3D is the reused round31 backdrop. No Blender run, no GPU lock taken.

## Number check
`check_cv.txt`: 53 checks against a fresh run of the E5 sim, 0 FAIL: p1 bill 33 / 19 / 11 / raw 52 / raw before guns 62 / dealt 14 / HP after 27 / trace 2 / schedule 2,2,1; all 9 units + Adjuster ring, sector, HP and arrival sector; p2 next turn no-twist 49 (5) 4, +1: 24 (10) 8, -1: 19 (11) 9 and this-turn bill unchanged under both; p3 0 / 9 / 6 / raw 14 / dealt 35 / Adjuster 28 / trace 4 / rider 5 / next 39 (23) 17; p2b path 0>2>4 and arrival 20 (12 + 2 x 4 growth). The first run flagged one FAIL that was my check using the wrong function (base hit, not arrival); fixed, rerun clean.
Notes on closing the bill (PL6 flaw 2): the plate says 62 RAW - 10 SHOT DOWN = 52 = 33 + 19; the wounded Packet shows `24` struck then `10` (the sim: -4 growth lost, -10 for 5 HP lost). The p2 sector strips are the raw landing per sector AFTER next turn's guns (sim `next.raw_per_sector`, sums to 54 = 49 + 5); waves_e5's table used the lane totals before guns, so its numbers differ by design.

## Cold read (p1, chips hidden): `cold_p1_nochips.png`
Hidden: ring labels, values, HP, arrival, bill, all text. Kept: glyph tokens, lane borders, geometry. Read from the image, then checked against the sim.

| unit read | my read (ring, sector) | sim | |
|---|---|---|---|
| Worm, top, outer | ring 2, s0 | ring 2 s0 | ok |
| Jammer, top, inner | ring 0, s0 | ring 0 s0 | ok |
| Worm, upper right | ring 1, s1 | ring 1 s1 | ok |
| Payload diamond | ring 0, s1 | ring 0 s1 | ok |
| Packet, lower right inner | ring 1, s2 | ring 1 s2 | ok |
| Worm, lower right outer | ring 2, s2 | ring 2 s2 | ok |
| Adjuster skull, bottom | ring 1, s3 | ring 1 s3 | ok |
| Packet, bottom outer | ring 2, s3 | ring 2 s3 | ok |
| Packet, upper left inner | ring 0, s5 | ring 0 s5 | ok |
| Packet, upper left outer | ring 1, s5 | ring 1 s5 | ok |

10 of 10 (PL6: 1 of 4 rings in the iso plate, 13 of 13 on E4). Caveat: I built the plate, so this is not an independent read; ring depth here is a counting-circles read, which is the point of the camera change. A fresh critic should repeat it. Kind (glyph) read at 320 px is by hue only; at 1080p the token is 54 px and reads.

## Honest judgment of the three looks
- **Converged**: the only one where the question "which ring, which sector, which slice does it hit" is answered by position. The sector link is radial, the schedule is an arc you can measure, and it is unmistakably the same game as the city/raid (bible chips, vinyl, CRT). Cost: the board is dim and flat compared with E5; at 320 px the ring structure and the orange bezel read, the unit kinds do not (hue only), and ring-0 threats are darker than they should be. Dense in p3.
- **waves_e5 (pass 3/4)**: the most striking and the busiest; reads as a place at squint, but breaks bible media rules and loses ring depth in the iso camera (PL6).
- **Bible strict**: cleanest bill and closest to the shipped look, but the concept (rotation, next-turn landing, sector link) is invisible without hover; two far-apart wheels.
- Recommendation: adopt converged as the structure, borrow E5's brightness and enamel for the ring-0 threat cells (a render pass), and apply BIBLE_AMENDMENTS 1-5.

## Deviations
- Adjuster is a cell in a ring (ring 1), not a docked satellite on the rim; its position on the wave is therefore shown.
- Slice faces keep their baked numbers in p1_nowords (bible slices are glyph + number by design); everything else is bars or removed.
- Hover dim is applied to unit content only, not to cell screens.
- Backdrop is the round31 Meridian HQ frame (as in the strict study), not the Depot lot.
- p1 loose chips: 3 ring labels + 6 slice HP badges (+ BROKEN / HOLDS tags) = 9-11, within 12; sector digits are bezel engravings.
- Rules questions (not decided): can a Worm/unit be shown as an in-ring cell that a 2-3 sector wide unit stretches (E7)? Is the Adjuster a ring unit or a rim satellite? Nudge buttons when nudge is a card.

## Slips
- One accidental `python -` (stdin, no code) hung once; stopped with TaskStop, nothing ran, nothing written. No other violations: nothing outside CV_waves and the plates/waves_converged folder was written; waves_e5, P5_waves, BB_bible, the sim and ART_BIBLE.md were only read or copied. No Blender, no taskkill, no background processes left.
- The compare sheet's waves_e5 column shows whatever is currently in waves_e5/ (an E5 pass-2 agent is updating it), so it may change later.

## Addendum: PL7 lessons applied (rebuilt p1, p2, p2b, p3, nowords, sheet)
- p2: the sector table is gone. Twist both ways is ghost rim chips ON the bezel (`+1:<raw>` yellow, `-1:<raw>` white, from sim next.raw_per_sector) plus the three NEXT total rows only.
- Wounds: one form on the board, `24 -> 10` (old value, arrow, new value), no strike-through.
- Bill: the YOU bill is the single hero box (white 3 px outline); NEXT rows are secondary; the p3 equation includes the rider (14 RAW - 5 RIDER = 9 = 0 THROUGH + 9 ABSORBED).
- p1: gun tracers carry the shot number (-9 BURST on the Jammer, -5 TURRET on the wounded Packet) and the idle BURST says NO TARGET. Known weakness: the -9 chip sits partly under the Jammer token and the -5 chip is hard to find; needs one more nudge.
- Ring-depth pad equivalent kept: concentric rings + lane style + NOW/+1/+2 + arrival digits (cold read 10/10, self-run).
- Slip: an edit script crashed on a non-ASCII arrow and emptied cv_over.py; I rewrote it from my own session text (no other files affected).
