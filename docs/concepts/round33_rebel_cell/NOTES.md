# Round 33: tucked thumb, toned down, the blackout reveal, a fist hologram in the takeover

## Map
- **Shape** (`map33.Crest.zone`):
  - The bottom cuff line is removed.
  - The palm line is now half length, fixed on the right (from u = 0.4 to 5.0 crest units).
  - A vertical black line at u = 0.4 joins it up to the thumb's upper edge: this is the tucked thumb.
- **Toned down:**
  - Red window density is lower: home 70 % (was 90 %), DISPATCH 90 % (was 100 %).
  - The reds are softer, the red glow is about two thirds as strong, and the dark-line overlay is lighter.
- **The REBEL_CELL label** now sits below the fist on the city-wide shot.
- **Deliverables:**
  - `map_A_{home,dispatch}.jpg` (city-wide) and `_crop.jpg`;
  - `map_ring_{home,dispatch}.jpg` (with the round 31 blackout ring) and `_crop.jpg`.
- **`map_fist_reveal.gif`** (640 × 460, 2.6 MB, home then DISPATCH): the sector starts fully lit, then the blackout ring and the hand's black lines go dark (frames 3–10) and the fist appears.
  - Fully lit means extra city windows across the ring, and the hand's lines also lit.
  - The red fist starts washed out among the lights.

## DISPATCH canyon
- The nearest hologram on the right is now the Cell's **fist**: a red scanline hologram on its projector.
- The struck-out human hologram on the left stays.
- Deliverables: `canyon_dispatch.jpg`, `combat_rebel_cell.png`, and `combat_rebel_cell_motion.gif` (960 × 540, 2.5 MB).

## Weak / open
- **A second struck-out human peeks out behind the fist hologram.** It is the far hologram on the same side.
- **The fist hologram reads as a solid red block at combat zoom** more than a projection.
- **During the reveal, home's red is subtle against the fully lit start** (as intended, "washed out mostly").

## Build (from `scripts/`)
1. `python layout27.py`
2. `python map_all33.py`
3. `python render_all33.py stills gif`
4. Render the wheels:
   - `python wheels_r18/render_bosses24.py rebel_cell`
   - `python wheels_r18/dump_boss_slots24.py`
   - `python combat_r23/render_player24.py`
5. `python make_out33.py`
