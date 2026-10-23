# L9 → L10 changes (from the L9 batch critic; applied in place to the l8 files)

## Rules (sweep_l8.py and l8_rules.gd change identically)
1. **POOL_START = {D: 1, N: 1, E: 0}** (was 1/1/1).
   - Two sentries against three sealed routes means one route is always uncovered, so the reveal decides the outcome.
   - REDEPLOY after the reveal, which moves a sentry onto the revealed route, becomes the key response.
   - Building (price 3) can add any type between raids.
2. **New metrics** in the `__main__` SUMMARY, for greedy and for naive:
   - `split_raids`: the share of raids where the three candidates' HOLD tiers or touches differ.
   - `response_decides`: the share of raids where the chosen response's outcome differs from HOLD's on the real
     candidate.
   - `redeploy_use`.

   It writes `D:/rc_tmp/raid_design_lab/sweep_l10.json`.
3. **Nothing else changes.**

## Presentation
1. **Tier language (shape and hue, readable without words), used everywhere: stamps, forecast rows, record pips and
   response rows:**

   | Tier | Mark | Color |
   |---|---|---|
   | EVADED | check | acid green |
   | HOLDS | shield | green-cyan `#3FE0B0` |
   | BATTERED | cracked shield | amber |
   | DAMAGED | X | red |
   | BREACHED | skull on black with a red border | — |
2. **Highlights by meaning.**
   - Capture targets: an amber plus.
   - Repair targets: a red wrench outline.
   - Picked or committed choices: a white check ring.
3. **Lethal stakes.**
   - At HOME 1/3, the last HOME pip pulses red with a skull, in the HUD and on our HQ tower.
   - The between screen shows a red banner: "Next HOME hit ends the campaign".
   - When the next raid's forecast-free worst case could reach HOME, the build and repair choices say which one
     protects HOME. This uses the known beam 1 route and whether any route reaches HOME.
4. **The hunter's identity.** It has its own silhouette and color whatever its type: a white hound with a cobalt trail.
   A small type badge shows its type.
5. **The scramble covers board labels too** (route names and street numbers). `L8Board.set_scramble(on: bool)`
   replaces them with noise of the same length.
6. **Board clarity in PLAN and FORECAST:**
   - The non-selected candidate routes are drawn at 25% alpha.
   - The selected route and the known beams are drawn at full strength.
   - The planned paths have no block ticks; block shields only appear for the selected route.
7. **"Leg value now"** has a hover or one-line breakdown under it: bank, districts, exploits, HOME, Heat.
8. **Fix:** the main scene calls `board.decay(cells)`, the board's name for the decay beat.
