# L13 rules (from RULE_BACKLOG.md: R2, R3, R4, R5; picked for the largest score movement)

Applies to sweep_l8.py (the oracle), l8_golden.py, l8_rules.gd and parity_check.gd. Everything in L9–L11 stays unless
changed here.

## R2: the hunter street is a second sealed unknown
- Each raid gains `hunter_cands`: 2 distinct streets, x in 0..3, both shown to the player. It also gains `hunter_real`
  (0 or 1), the street the hunter actually runs.
  - Both are drawn by `random.Random(9100 + 13 * seed + raid)`: first the two streets with `rng.sample(range(4), 2)`,
    then `hunter_real = rng.randrange(2)`.
  - The rest of `make_leg` stays unchanged, so all other leg data is identical.
- **The first-touch rule is gone.** The hunter runs `street(hunter_cands[hunter_real], down=True, hunter_type)`,
  y = 0→2, unless JAM. The `hunter_street` field is removed.
- **Reveal order in a raid:**
  1. beam 1 and the extras;
  2. the sealed route REVEAL;
  3. the RESPONSE, chosen without knowing the hunter street;
  4. the sealed beam;
  5. the HUNTER REVEAL;
  6. the hunter.
- **Functions:**
  - `resolve`, `trace` and `hunter_line` take an extra `hunt: int` (0 or 1) after `cand`. Callers use
    `raid.hunter_real` for the real line.
  - `forecast(leg, raid, st, place)` returns, per sealed candidate, `{cand, outcomes: [hold result for hunt 0,
    hold result for hunt 1]}`, each `{state, touches, tier}`.
- **Planner:** greedy chooses its response per sealed candidate to maximize the mean over the 2 hunter streets (the
  EV is over 3 × 2). naive is unchanged (HOLD).

## R3: SACRIFICE response (trade a district for HOME)
- **Option:** `["SACRIFICE", cell]`, for any owned, non-TAKEN cell. It costs no spoof and no Heat.
- **Effect,** applied at the response step, after beam 1 and the extras:
  - the cell becomes TAKEN now, and its sentry returns to the pool (L11 rule);
  - **HOME cannot lose integrity for the rest of this raid.** A route that reaches HOME records the touch
    `("HOME", "shielded")`, and HOME is unharmed.
- **Order of `response_options`:** HOLD, REDEPLOY…, DEPLOY…, SACRIFICE… (cells in cell order), JAM.
- **Tier:** a SACRIFICE counts as a newly TAKEN cell, so the raid is at least BATTERED unless HOME was hit earlier
  in it (then DAMAGED).

## R4: Heat in bands; HOME priced higher
- **Score Heat term:** `-0.5 * max(0, heat - 44) - 6 * (heat >= 50) - 6 * (heat >= 75)`. It replaces
  `-HEAT_CARRY * max(0, heat - 44)`.
- **`HOME_LOSS_COST` = 15** (was 8).

## R5: each intensity buys something different
- **LOW:** +6 Heat, income ×0.5, no perk.
- **NORMAL:** +12 Heat, income ×1.0, and **this between step's repair is free** (cost 0). It still repairs at most 1
  cell.
- **HOT:** +18 Heat, income ×1.5, and **the next raid's CAPTURE takes two cells.**
  - State gains `extra_capture: int`: HOT sets it to 1, and capture consumes it.
  - CAPTURE runs capture → capture again if `extra_capture > 0` (the second capture uses the updated state's
    options), then clears it.
  - In golden steps `capture` becomes a list of 0 to 2 cells.
- **`between()` order stays the same:** repair (free under NORMAL), build, income, Heat, perk flag.

## Golden and parity
- **Golden content:**
  - Leg JSON includes `hunter_cands` and `hunter_real` per raid.
  - Steps include `hunt` (the real one), `capture` as a list, and responses in the forms
    `["SACRIFICE", [x, y]]` and `["DEPLOY", t, [x, y]]`.
  - State JSON includes `extra_capture`.
  - Random raids draw `hunt` from `rng.randrange(2)`.
- **parity_check checks every new field and function.**
- **Measurement** (`__main__`, `sweep_l13.json`) adds:
  - `sacrifice_use`;
  - `hunter_split`: the share of raids where the 2 hunter streets give different HOLD outcomes for the chosen
    placement and the real sealed route;
  - the intensity mix;
  - `hot_double_captures`.
