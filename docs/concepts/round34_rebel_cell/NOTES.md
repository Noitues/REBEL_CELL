# Round 34: two fixes on round 33

1. **Fist: the upper horizontal line is removed.**
   - The knuckle-crease line across the fingers is gone; its rule is deleted in `map34.Crest.zone`.
   - What stays:
     - the finger splits;
     - the thumb's upper edge;
     - the thumb tip;
     - the half palm line on the right;
     - the vertical tucked-thumb line.
   - The fully-lit (washed-out) start of the reveal is unchanged, as it is locked.
   - Outputs:
     - `map_A_*`, `map_ring_*` (city-wide and crop, home and DISPATCH);
     - `map_fist_reveal.gif` (2.6 MB).
2. **The DISPATCH combat animation is slower and calmer** (`kit26.anim`):
   - **Longer holds.** Each sign holds its state for 4 frames, and the start of each hold is staggered per sign, so few change together.
   - **Gentler flicker.** Signs drop out 4 % of the time (was 18 %) and dim to 70 % (was 45 %), only 10 % of the time.
   - **Softer glitch.** It is rarer (15 %) and gentler (0.25).
   - **Slower movement.** Content swaps and scrolling advance once per hold. Hologram tears and slices change every 4 frames.
   - **The GIF.** `combat_rebel_cell_motion.gif` is 880 × 495, 24 frames at 200 ms (4.8 s loop), 3.1 MB.
   - **Behind the fist.** The struck-out human hologram that peeked out behind the fist hologram is now only an empty projector.

## Build (from `scripts/`)
1. `python layout27.py`
2. `python map_all34.py`
3. `python render_all34.py stills gif`
4. Render the wheels:
   - `python wheels_r18/render_bosses24.py rebel_cell`
   - `python wheels_r18/dump_boss_slots24.py`
   - `python combat_r23/render_player24.py`
5. `python make_out34.py`
