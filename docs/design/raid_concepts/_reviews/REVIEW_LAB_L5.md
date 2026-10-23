# REBEL_CELL sweep-raid lab L5: critic review

**Verdict: 33/50. A clear, honest, well-previewed system with real persistence, held back by decisions that mostly have one obvious answer and by a playout with nothing left to resolve once you commit. It ties Kingdom Rush on this rubric, below FTL. The ceiling is mostly in the rules, not the art.**

Material: `shots_scrambled/` (leg 5, read first, notes in `scrambled_notes.md`, written before I opened `LAB_README.md`), `shots/` (leg 0 planned), `shots_jam/` (leg 3 planned), `shots_breach/` (leg 0 naive). Contact sheets are in `sheets/`. The reference sheet is `refs/side_by_side_l5.png`, built by `scripts/side_by_side.py`.

Process note: one shell command early in this review included a stray empty `python -c ""`, which breaks the lab rule. It did nothing (a no-op). Every script after it was a file run as `python <file>`.

## Scores

| Axis | Score | Reason |
|---|---|---|
| W, legible | 7 | Every touch is named in WHAT THE BEAMS TOUCHED, and the aftermath ledger rebuilds Heat, kit and leg value from numbers (`shots/11_r1_aftermath.png`). It is dense, though: the board needs the panel, and the panel needs reading. |
| P, predictable | 8 | The forecast shows each sealed line's result with hold and with the best spoof (`03_r1_forecast`). The response rows show the exact result and Heat after for every option (`06_r1_decision`). The intensity cards show next-raid breach risk. It loses points because the risk only looks one raid ahead (`shots_breach/14` "safe", then `28` "BREACH 3/3"). |
| N, no words | 5 | The scramble got the structure across: beams, order badges, the hidden "?" line, the levers, a mid-sweep pick with a meter delta, and the 1-of-3 between pick. It did not get across what node numbers mean, whether the meter is good or bad, or what 50/75 do. I also read a dark node as a damaged one. |
| D, depth | 5 | Lever placement against three possible lines is a real puzzle. But the response screen usually has exactly one row better than HOLD, the raid-3 spoof is often worth nothing, and LOW intensity looks dominant on the numbers shown. |
| C, consequences | 8 | DOWN assets pile up and count their age, TAKEN stays taken, HOME integrity and Heat carry across raids, the kit lasts the whole leg, and a breach ends the campaign (`shots_breach/36_r3_breach.png`). |
| **Total** | **33/50** | |
| S, suspense | 4 | The only real unknown is which of the three sealed lines is real. After the response click, the rest of the playout (`07`..`10`) is already printed on the row you picked. |
| V, visuals | 3 | Clean, consistent placeholder vectors and a good color code (teal good, amber battered, red breach), but no material, no motion feel and no sense of place. The stamp and breach screens are the strongest frames. |
| Fit | 6 | Corporate beams sweeping a hacker cell, Heat, ghosts and spoofs, home-server integrity: the theme reads well. The grid itself feels like a spreadsheet more than a city network. |

## Placement

| Game | /50 | S | V |
|---|---|---|---|
| Into the Breach | 45 | 5 | 8 |
| Slay the Spire | 42 | 6 | 7 |
| Invisible, Inc. | 39 | 9 | 7 |
| FTL | 35 | 8 | 7 |
| **L5 lab** | **33** | **4** | **3** |
| Kingdom Rush | 33 | 8 | 8 |
| Teamfight Tactics | 31 | 8 | 7 |

- **Against FTL (35):** the lab wins on P (FTL never shows you the result of an action before you take it) and roughly ties on C. It loses on D: FTL's power routing, crew placement and when-to-jump choices stay contested all run, while the lab's response is usually a one-row answer. It loses heavily on N, S and V.
- **Against Kingdom Rush (33):** the lab wins on P and C (Kingdom Rush waves forget everything between levels) and on W for its ledgers. It loses on N (Kingdom Rush reads with no words at all), S and V.
- **Against Into the Breach (45),** which shares its telegraphed-threat design: the lab matches ITB's "exact preview" philosophy on P, but ITB's previews create puzzles (push, block, trade a building), while the lab's previews mostly confirm the one right row. ITB's threat is drawn on the tile and readable at a glance. The lab's lives in a side panel (`refs/side_by_side_l5.png`).

Reference images (sheet `refs/side_by_side_l5.png`; built by `scripts/side_by_side.py`):
- Into the Breach: https://shared.akamai.steamstatic.com/store_item_assets/steam/apps/590380/ss_1ac6f8ce8e81bc1b3fe9cb23f58c477cbda04a04.1920x1080.jpg?t=1755610784 (`refs/itb.jpg`)
- Slay the Spire: https://shared.akamai.steamstatic.com/store_item_assets/steam/apps/646570/ss_8af73365121b1b1e2d8004fca2cbffb9b9f6d7a5.1920x1080.jpg?t=1774015376 (`refs/sts.jpg`)

These are the only screenshots the store pages exposed: an ITB briefing screen and the StS card library, not combat boards. They are good evidence for finish, type and the "icon + number + one line" card pattern (V and N). They are weak evidence for board readability, so those comparisons lean on how well these games are known.

## What the scrambled run conveyed (leg 5)

My notes from the images alone are in `scrambled_notes.md`.

**Conveyed:**
- the board, HOME (the server icon with 3 pips) and the order of beams (numbered badges);
- hidden versus known beams (dashed lines with "?");
- three lever types, each with limited counts;
- a mid-sweep pick whose options change the orange meter (`06_r1_decision`: 49->41 versus 49->51);
- a final "hunter" beam that targets a node (`38_r3_hunter_turn` red ring);
- the response-unavailable beat (`36_r3_no_spoof_left`, crossed glyph);
- the between screen as a 1-of-3 pick with escalating +6/+12/+18 and x0.5/x1/x1.5;
- the leg as three raids, ending in a record.

**Not conveyed:**
- **Node numbers.** I could not tell whether they are value, HP or income.
- **Meter polarity.** The meter climbed all leg and nothing visibly broke, so I could not tell it was bad, or what 50 and 75 do.
- **Dark versus damaged.** I read the dark node (grey ring with a red-slashed income badge, `03_r1_forecast`) as a damaged node.
- **The three lever types.** I could not tell how they differ beyond their shapes.
- **The red ring on the hunter's target.** I could not tell whether it cost anything.
- **Speed controls.** I only guessed that 1x/2x/4x was playback speed.
- **Stakes.** Nothing in the scrambled leg told me that HOME at zero loses the whole campaign.

## Findings

### P1

1. **A settled breach still makes you play a dead raid, and the warning jumps from "safe" to "doomed" in one step.**
   - After raid 1 of the naive leg, HOME is at 2/3 and every intensity card says "safe / no line breaches" (`shots_breach/12_r1_between_open.png`..`14_r1_between_picked.png`).
   - One raid later, every card says "BREACH on 3/3 lines, whatever you pick" (`shots_breach/28_r2_between_open.png`..`30`). The player then has to plan and launch raid 3 under a red banner that says no lever helps (`32_r3_plan_empty`..`35_r3_breach_touch`).
   - The risk reads only the next raid, so the campaign-losing consequence has no two-raid warning. Once it is settled, the game spends a whole raid confirming it.
   - Axes: P and D, and the fairness of C.
2. **Most decisions have one obvious answer.**
   - **Response.** Every spoof row costs the same +2 Heat, so the screen reduces to "is any row better than HOLD?":
     - `shots/06_r1_decision`: only SKIP-HOME avoids HOME -1.
     - `shots_jam/06_r1_decision`: JAM gives x1 DOWN against x3 for every other row.
     - `shots/38_r3_decision`: every row is identical, so HOLD wins.
     - `shots/34_r3_forecast`: "no node to save" on all three lines.
   - **Intensity.** With Heat carried at 1 point per point and income at bank value, LOW nets -3, NORMAL -6 and HOT -9 on `shots/13_r1_between_repairs`. Every card says "safe", and HOT adds beams on top.
   - The planned lines pick LOW at every between step (`shots/44_record.png`, `shots_jam/41_record.png`). This is the main D and S limit.
3. **No-words readability falls short on the three things that matter most:**
   - what a node is worth;
   - whether Heat is danger;
   - a dark node versus a damaged one (`shots_scrambled/03_r1_forecast.png`, where the grey slashed ring reads as damage).

   The between screen's key effects (`+12 Heat`, `x1.5`) are numbers, and nothing graphic separates good from bad. Axis: N.

### P2

4. **The reference "planned" line forgoes a visible good trade and ends the leg with an unused spoof.** In `shots/22_r2_decision.png`, the third row (SKIP 8) shows x1 DOWN against x2 for HOLD, for +2 Heat, and the line holds. Raid 3's spoof then has no node to save (`34_r3_forecast`), and the record shows spoof used 0 in raids 2 and 3 (`44_record`). Either the planner is weak or the row misstates the result. In both cases, a leftover spoof at leg end is wasted value, so saving it carries no reward. Axis: D.
5. **Good play looks like losing.** The leg-0 planned line is CELL BATTERED in all three raids and ends at 2 OK / 3 DOWN / 1 TAKEN, score 11 (`shots/44_record.png`). Only the JAM leg shows HOLDS and EVADED (`shots_jam/41_record.png`). If the best line on leg 0 is battered three times, the tier words punish the player for the map, not for their play. Axes: S and Fit.
6. **Lines crowd at Heat 50 and above.** Beam 1 and the "+" beam draw almost on top of each other, and beam 2 is offset into the gap between rows, so it reads as missing the row (`shots_jam/36_r3_no_spoof_left.png`, `33_r3_beam_b1`). The forecast's per-node glyph pairs (a shape plus a lightning bolt) are tiny and cryptic (`shots/03_r1_forecast.png`, `shots/18_r2_forecast.png`). Axes: N and W.
7. **The playout has no suspense left.** The exact row result is shown before the click, and the hunter's column is drawn during planning. After the response, beats `07`..`10` play out a known answer. Only the sealed reveal (`05_r1_unseal`) carries tension. Axis: S.

### P3

8. On the JAM preview, the red X sits on node 10's column and reads as "node 10 destroyed", not "hunter cancelled" (`shots_jam/06_r1_decision.png`).
9. Two names for one quantity: "Leg value" (aftermath and between screens) and "SCORE" (record) are the same formula (`shots/11_r1_aftermath.png`, `44_record.png`).
10. ASSETS KEPT drops mid-playout ("36, was 40") before the aftermath confirms it (`shots/06_r1_decision.png`). It is honest but noisy.
11. The designer toggle strip and the long hint line stay on every frame and add reading load (any frame, bottom).
12. Strong frames worth keeping: the BREACHED screen (`shots_breach/36_r3_breach.png`), the tier stamps, the record mini-maps with ring marks (`44_record`), and the "no spoof left" beat (`shots_jam/36`).

## The three changes that would raise the score most

1. **Make responses and intensity real trade-offs.** Estimate: D +2 (to 7), S +1, about +3 total.
   - Give SKIP and JAM different, situational costs. For example, JAM costs more Heat or both spoofs, SKIP is cheap.
   - Make an unused spoof worth something at leg end (it carries over, or refunds Schematics). Then saving it versus spending it becomes a real question.
   - Re-tune intensity so the higher settings can pay off. Options: a Heat-carried weight below 1, income that buys things you cannot otherwise get, or a schematic or kit reward only HOT gives.
   - Check by finding at least one golden leg where each intensity and each response form is the best choice somewhere.
2. **Give a two-raid breach outlook and never force a dead raid.** Estimate: P +1, D +1, and better perceived fairness on C, about +2.
   - Show "raid after next" risk on the cards, or a "HOME line" projection, so the step from safe to settled can be seen one raid early.
   - When breach is certain on every line, either resolve it at once or offer a last-stand choice with a real effect, such as evacuating an asset or sacrificing kit for an integrity point.
3. **A no-words pass on the three key reads, plus beam lanes.** Estimate: N +2, W +1, about +3.
   - Show node value as ring size or a pip count, not a bare number.
   - Give dark nodes a distinct "unplugged" look, unlike the damaged and TAKEN states.
   - Color the Heat meter as a danger gradient with beam icons at 50 and 75.
   - Draw parallel beams in fixed lanes inside the row, never between rows.
   - Draw the forecast's per-line outcome on the board (ITB-style tile marks), not only in the panel.

## Rules ceiling or presentation ceiling?

**Both, but the hard ceiling is the rules.**
- **Already near the top:** W, P and C are close to what this design can reach (7, 8, 8). The exact previews and persistent ledgers are the lab's best asset.
- **Presentation:** N (5) and V (3) are presentation problems, and a real art and motion pass would recover several points, mostly on V, which is outside the /50.
- **Rules:** D (5) and S (4) are capped by the rules. Once every option shows its exact result and the options rarely compete, no art makes the choice harder or the playout tenser. Into the Breach scores 45 with exact previews because its previews set up trade-offs: block this, lose that.

The single biggest change toward 40 is to make the response rows and the intensity cards compete, not to draw them better.
