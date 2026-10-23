# L8 → L9 changes (the batch critic's three changes, applied in place to the l8 files)

## Rules (sweep_l8.py and its GDScript port l8_rules.gd; both change identically)
1. **DECAY.** At the start of every raid after the first, before CAPTURE, every owned cell whose status is still DOWN
   becomes TAKEN and loses its sentry (removed from the sentries and from the pool).
   - It's a new step, `decay(leg, st) -> State`. `capture_options` and `capture` work on the decayed state.
   - The replay order is decay, then capture.
   - In Python, greedy_leg and naive_leg apply it, and so does the golden's replay: l8_golden.py calls `S.decay` before
     each capture when raid > 0.
2. **SENTRY_PRICE** = 3 (was 4).
3. **No other rule changes.** Forecast, responses, tiers and score stay the same.

## Lab presentation (raid_lab_city.gd and l8_board.gd)
1. **The reveal decides.** The FORECAST panel shows, per sealed route, only the HOLD outcome, plus one line: "a
   response changes this" or "no response changes this". That line comes from comparing every
   `L8Rules.response_options` result for that route. The BEST row is gone.
   - The RESPONSE screen collapses options with identical outcomes (same touches, same tier) into one row:
     "REDEPLOY (4 ways)". It also shows each row's result.
   - When every option gives the same outcome, it says "nothing you can do changes this" and offers HOLD only.
2. **The forecast goes on the board.** In PLAN and FORECAST, one sealed route is selected (default: the first). Keys
   Q, W and E, or a click on a panel row, change the selection. The board then shows that route's HOLD outcome:
   - every cell that will be hit: a crack glyph in red;
   - every block: a shield glyph in the sentry's type color;
   - HOME hit: a red skull glyph over our HQ;
   - the hunter's path: a dashed line in the hunter's type color, with a hound glyph at its start.

   The board API adds `show_outcome(o: Dictionary)` and `clear_outcome()`, where
   `o = {hits: Array[Vector2i], blocks: Array[Vector2i], block_types: Array[String], home: bool, hunter: line or null}`.
   The main scene builds `o` from `L8Rules.trace` (HOLD) and `L8Rules.hunter_line`.
3. **Colors:**
   - streets go neutral gray (not orange);
   - tier colors: EVADED = acid green, HOLDS = amber (ours), BATTERED = yellow, DAMAGED = red, BREACHED = white on black
     with a skull glyph and a red border;
   - each tier stamp has its own shape too (check, shield, crack, cross, skull), so tiers read when scrambled.
4. **Bloom:** cap glow on impact moments, so hits read as a shape and not a white blob. Use a lower glow intensity
   and smaller flash sizes.
5. **Board size:** the board should fill most of the free area (x 0..860, y 64..670). Cut the fit headroom and margin,
   and keep the skyline out of the fit box.
6. **Coordinates:** draw large readable route labels (NORTH, MID, SOUTH) at the corp end of each road, and street
   numbers 0–3 at the north edge. Text everywhere uses those names.
7. **Intensity cards** include the plan-side Heat in their "next raid: N known beams" preview, as a range: the Heat
   with no ghost, and with a ghost (+5).
8. **DECAY is shown:** at the start of raid 2 and raid 3, a short beat shows each decaying cell turning TAKEN (cobalt),
   with a line in the panel: "Left DOWN: SOU 1 is TAKEN by the corp". The between screen warns per DOWN cell: "repair
   it or lose it".
9. **SCORE in the HUD** is labeled "leg value now". The record keeps the final score.
