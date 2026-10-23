**Verdict: 37/50. A very legible, very honest raid with strong persistence. Its one live decision is usually trivial, and its campaign-losing breach is settled two raids early with no warning that looks past the next raid. It places between Invisible, Inc. and FTL.**

Critic: fresh, no prior reviews, scoreboards or design docs read. Material: only `critic_lab_l7/` (LAB_README.md, shots, shots_scrambled, shots_jam, shots_breach, clip_frames). I read the scrambled run first. My notes from it were saved to `sheets/SCRAMBLED_NOTES.txt` before I opened the README or any unscrambled shot.

## Scores

| Axis | Score | One-line reason |
|---|---|---|
| W: what / why / when | 8 | Numbered beam track, a "what the beams touched" log, a ledger that rebuilds every number, and a legend strip on every screen. Lost points: unexplained red X marks and crowded lane pills. |
| P: predictability | 8 | The forecast gives the outcome per sealed line (hold vs best spoof), and each response row shows the exact chips and Heat after. That is Into the Breach level for one raid, but the breach-risk cards look only one raid ahead and say "safe" on a doomed leg. |
| N: no words | 6 | Structure, Heat, the reveal beat, tier colors and the risk/reward of the between cards all read. Node value, what each lever does, why rows differ (digits only) and the red X do not. |
| D: decision depth | 6 | Plan placement against 3 candidate lines and the between trades are real. The post-reveal response is usually degenerate (one obvious row, or all rows equal), and the planned line is BATTERED in all three raids. |
| C: consequences persist | 9 | DOWN stacks into TAKEN, only one repair per step, HOME integrity, Heat carried into the score, a depleting leg kit, and campaign loss on breach. All of it is visible in the record. |
| **Total** | **37/50** | |
| S: suspense | 6 | The unseal beat (shimmer, collapse, ignite) and the stamp slam work. But the forecast already showed all three outcomes, the playout is hands-off, and the breach raid plays out pre-decided. |
| V: visuals | 7 | The 3D slab, bloom, amber and cobalt palette and tower states are coherent and handsome. The board is small (about 55% of the screen), the side panel is text-dense, and beams are flat ribbons. |
| Fit | 7 | The cyberpunk "hacker network under corp sweep" premise plus Heat fits REBEL_CELL. The lever kit is not tied to cards or deck, so it reads as a separate minigame. |

## Placement

| Game | /50 | S | V |
|---|---|---|---|
| Into the Breach | 45 | 5 | 8 |
| Slay the Spire | 42 | 6 | 7 |
| Invisible, Inc. | 39 | 9 | 7 |
| **REBEL_CELL raid lab L7** | **37** | **6** | **7** |
| FTL | 35 | 8 | 7 |
| Kingdom Rush | 33 | 8 | 8 |
| Teamfight Tactics | 31 | 8 | 7 |

- **Against Invisible, Inc. (39, above):** the lab wins P (the full forecast, where Invisible, Inc. shows only the guard's next step) and roughly ties C. It loses D, because Invisible's every-turn action and alarm economy is far deeper than one response per raid. It loses S badly (6 vs 9), because Invisible's alarm ticks under the player's own hand while the lab watches a playout.
- **Against FTL (35, below):** the lab wins W and P (FTL's random combat outcomes are opaque by comparison) and C (both persist, but the lab's ledger is clearer). It loses S (6 vs 8). FTL's pausable real-time fights keep the player acting mid-crisis, which the lab does not.
- **Against Into the Breach**, the clear model: the lab copies the telegraph idea and gets P close. The gap is D, since ITB has every unit, every turn, push and positional puzzles, and N, since ITB's tile outcome glyphs carry the whole preview with no digits (side-by-side sheet: `refs/side_by_side.png`).

## What the scrambled run conveyed (leg 5, `shots_scrambled/`)

Conveyed without words:
- The grid is a network. The big stacked tower is HOME (the thing to protect). The blue lanes with arrowheads are sweeps, and a `?` token marks a beam whose path is hidden (`01_r1_plan_empty`).
- The flame meter is a threat track with two thresholds. Crossing the first adds a beam: raid 2 at 53 shows an extra beam (`24_r2_plan_empty`, `28_r2_beam_b1`, `29_r2_beam_extra`).
- Placing a tool costs flame: the +5 (`02_r1_plan_levers`).
- The forecast rows mean "good or bad per hidden-line shape" (green check vs arrow, `03_r1_forecast`).
- The hidden beam reveals mid-raid, followed by one choice with flame costs (`06`–`09`). One beam later turns toward a target (`12_r1_hunter_turn`).
- Stamp color is the tier: lime on a clean raid (`14_r1_stamp_slam`), dark red on worse ones (`37_r2_stamp_slam`, `62_r3_stamp_slam`).
- Between raids is a stakes choice of +6/+12/+18 flame for x0.5/x1/x1.5 (`18_r1_between_fill_a`).
- The record shows one card per raid (`66_record`).

Not conveyed:
- What the number on a node is (value? HP?). What the clock-coin number and the "48 → 42" top-right count are (bank and assets kept).
- What each of the four lever glyphs does individually. Only "the diamond is an object on a lane" and "the sleeping circle hides" come through.
- What distinguishes the response rows. Only the digits differ, and the scramble keeps digits, so the test was easier than a true no-words test.
- What the red X marks on the board mean (`07_r1_unseal_collapse` onward).
- Why raid 2's stamp is red. That raid lost an asset for good (TAKEN), and you cannot tell from the stamp.
- What the yellow squares are (HOME integrity).

## Findings

### P1

1. **The post-reveal response, the raid's only live decision, is usually degenerate.**
   - `shots/11_r1_decision.png`: 6 rows, 5 of them identical (x2 DOWN, HOME −1). Only the "skip HOME" row avoids the −1, so it is a forced move.
   - `shots/38_r2_decision.png`: every row shows x2 DOWN / x1 TAKEN except one SKIP 8 (x1 DOWN). The others are pure "+2 Heat for nothing" rows against HOLD.
   - `shots/63_r3_decision.png`: all 6 rows are x2. HOLD strictly dominates.
   - The one real trade I saw is the JAM leg (`shots_jam/11_r1_decision.png`: x3 / x3 / x4 / x3 / JAM x1). There JAM is the obvious best, so again there is no tension.

   The screen is beautifully honest about this, which only makes the emptiness more visible. This is the biggest cap on D and S.

2. **The campaign loss is settled two raids early, and the risk display never looks past one raid.**
   - After raid 1 of the careless line, all three intensity cards say "safe / no line breaches" (`shots_breach/23_r1_between_repairs.png`, `24_r1_between_picked.png`).
   - Raid 2 then costs HOME again (`34_r2_impact_home.png`, 3 → 1 over the leg).
   - After raid 2 every card reads BREACH 3/3 "whatever you pick" (`47_r2_between_fill_a.png` to `51_r2_between_picked.png`). Raid 3 auto-plays as "THE CELL FALLS" with no forecast and no choice (`52_r3_fall_start` to `55_r3_breach`, clip `breach_raid/00_decided` to `06_breached_card`).

   Losing the whole campaign with a full raid of zero agency, after a screen that said "safe", is the worst feeling the mode can produce. The honesty of "DECIDED" is right; the missing horizon and the dead last raid are not.

### P2

3. **The planned (good) line still reads as losing.** Leg 0's planned play stamps CELL BATTERED in all three raids (`shots/16_r1_stamp_slam`, `43_r2_stamp_slam`, `68_r3_stamp_slam`). The record ends "CELL KEPT 5/6, score 11" (`72_record`). There is no EVADED or HOLDS peak on the showcase line, so the tier ladder flatlines and the player gets no "I outplayed the corp" beat.

4. **The forecast pre-spends the reveal's suspense.** `shots/03_r1_forecast.png` already lists the hold and spoof result for every sealed shape. The unseal ignite (`10_r1_unseal_ignite`, clip `planned_raid/04_unseal_ignite`) then only tells you which of three known outcomes you get. It is good for P, but S is capped at a lottery reveal plus a playout with no input (the speed and skip controls are the only interaction, `04_r1_launch_b1`).

5. **Intensity cards rarely differ on risk**, so the main between decision is a flat Heat-for-income trade. All three cards read "safe" in `shots/23_r1_between_repairs.png` and `shots/47_r2_between_fill_a.png`. In the breach leg they read BREACH 3/3 on every card (`shots_breach/47_r2_between_fill_a.png`). Either way, the one new number on the cards never separates them.

6. **No-words gaps (N).**
   - Response rows differ only by digits (`shots_scrambled/09_r1_decision`, `33_r2_decision`).
   - Node value is a bare number with no pip or size coding (`shots_scrambled/00_r1_contact`).
   - The red X marks are not in the legend strip (`shots/11_r1_decision`, `13_r1_beam_b2`).
   - Lever function is carried by the text cards (`shots_scrambled/02_r1_plan_levers`).

7. **Board crowding at plan and forecast time.** Outcome pills sit on the lanes and overlap tower caps (`shots/03_r1_forecast.png`, `shots_jam/03_r1_forecast.png`). The board renders at about 55% of the target framing, so towers and chips are small, and at Heat 63+ badges sit on nodes (`shots/58_r3_beam_b1`, `66_r3_hunter_turn`).

### P3

8. "worst: 2 DOWN, HOME −1 / with a spoof: 3 DOWN" reads as if the spoof made things worse; it is trading HOME for an asset (`shots/03_r1_forecast.png`).
9. The JAM confirmation is small: a struck beam 3 pip plus a corner chip (`shots_jam/12_r1_after_decision.png`). The JAM moment deserves its own beat the way the unseal gets one.
10. The side panel is dense with small text on every screen. The between screen is a full spreadsheet (`shots/23_r1_between_repairs.png`). It is readable at 1280×720, but heavy.
11. Positive, kept as reference: the breach card and record (`shots_breach/55_r3_breach.png`, `56_record.png`) and the HOME-drain red flash (`clip_frames/breach_raid/02_home_hit`) are excellent. They are clear, final and on-palette.

## The 3 changes that would raise the score most

1. **Make the response a real trade every raid (D +2, S +1).** Guarantee at least two non-dominated rows: for example, SKIP saves HOME vs SKIP saves the highest-value asset, or JAM vs SKIP with different Heat and beam consequences next raid. Alternatively, let the response spend a second kit item (a late decoy). Flag rows that change nothing as "no effect" instead of listing them as options. This is a rules change.
2. **Give the risk a leg-long horizon and kill the dead raid (P +1, D +1, S +0.5).**
   - The between cards should show a fuse, for example "HOME 1 left: next HOME touch ends the campaign", plus a two-raid projection ("safe next raid, breach likely in raid 3 at this Heat").
   - Raise a warning when HOME first drops.
   - Give a "decided" raid one desperate out (an emergency ghost on HOME at a large score or Heat cost) so the final raid is never a cutscene.

   This is mostly presentation plus one small rule.
3. **Put the consequences on the board, not in digits (N +2, W +0.5).**
   - Hovering a response row should paint each affected tower with its outcome glyph (DOWN, TAKEN, HOME crack) and grey out untouched ones. Rows then read with no words or numbers.
   - Code node value as cap pips or tower height.
   - Add the red X to the legend, or drop it.
   - Move the forecast pills off the lanes into per-tower badges.

   This is presentation only.

(Next in line: tune leg 0 so the planned line reaches at least one HOLDS or EVADED stamp, S +0.5 and D +0.5.)

## Rules ceiling or presentation ceiling?

Mostly a **rules ceiling**.
- W, P and C are already 8–9, so presentation has little left to win there apart from N, where change 3 is worth about +2.
- The cap is D and S. The raid gives one meaningful mid-raid input, and the rules often make it forced or empty. The forecast is complete enough that the reveal is a lookup. The best line still erodes the network every raid. The leg-level loss can be locked in by mid-leg with no counterplay.

Presentation fixes alone get this to about 39–40 (around Invisible, Inc.). Passing Slay the Spire's 42 needs the response and between choices to produce genuine, non-dominated trades. Raising S toward 8 needs either player input during the sweep or a reveal that the forecast does not fully pre-resolve.

## Method and references

- Contact sheets: `sheets/scr_a`–`scr_e.png` (scrambled), `l0_a`–`l0_d.png` (leg 0), `jam_a.png`, `breach_a`–`breach_c.png`, `clips.png`. Built by `scripts/contact.py`.
- Side-by-side: `refs/side_by_side.png`, built by `scripts/side_by_side.py`. It pairs the lab forecast with ITB, the response with Invisible, Inc., the playout with FTL, and between with StS.
- Reference images (Wikipedia, non-free screenshots), sources listed in `refs/URLS.txt`:
  - https://upload.wikimedia.org/wikipedia/en/d/d0/Into_the_Breach_Screenshot.png
  - https://upload.wikimedia.org/wikipedia/en/0/0c/Slay_the_spire_screenshot.jpg
  - https://upload.wikimedia.org/wikipedia/en/9/98/Tactical_View_Invisible_Inc.png
  - https://upload.wikimedia.org/wikipedia/en/d/d7/FTL_Faster_Than_Light_Screenshot.jpg
- No Kingdom Rush or TFT image was fetched; their anchors are used as given.
- Process note: my first shell command chained `python -c ""` after `python --version`, which breaks the brief's rule. It ran nothing and wrote nothing. Every script after that went through a file in `scripts/`.
