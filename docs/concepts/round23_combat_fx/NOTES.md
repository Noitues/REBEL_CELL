# Round 23: CORRUPTED as the locked glitch overlay; temporary labels applied

**Base:** the locked D4 combat screen (no NEXT arrows), with the locked SEND IT sticker. The round 22 scripts were copied here; earlier rounds are untouched. All new code is in `scripts/fx_r23.py`.

## Rules (in force)
1. **Card effects come from the card play.** The card slaps over the target spinner and dissolves (dissolve A, the bit stream). The bits travel to what the card affects.
2. **Statuses are only their overlay.** The slice shows the locked round 14/15 state overlay and nothing else:
   - no corner badge or icon;
   - no rule chip or tooltip, not even a dissolving one.
3. **Labels are temporary.** Word stickers and result chips pop in, hold about 0.75–0.9 s, then dissolve left to right into 0/1 bits that drift up and fade. This covers EVADED, CHECKPOINT, PHASE 2, DELETED, `-4 RAM`, `-1 RAM` and `2 NEEDLES`.

## Files
| File | What |
|---|---|
| `fx_corrupt_apply_v4.gif` | CORRUPT PACKET slaps on THE MANIFEST and dissolves (A). The pink bits swirl into the slice under the needle, and as they land the **CORRUPTED glitch overlay** takes the slice left to right (320 ms), with doubled tears for 500 ms. Result: the overlay only. |
| `fx_corrupt_tick_v3.gif` | The standing state is the glitch overlay. On resolve: a white flash and a tear spike, then the glitch wipes left to right into pink/green 0/1 bits. The bits run round the rim to the HP arc: −3. A bolt hits the RAM meter and a pip cracks: −1 RAM, with a temporary chip. At 1500–1800 ms the glitch writes back on, left to right. |
| `fx_corrupted_storyboard.png` | Four key frames each for the apply and the tick. |
| `fx_evade_v4.gif` | The locked evade v3; EVADED now dissolves away. |
| `fx_respin_v2.gif` | The locked respin; CHECKPOINT and the `-4 RAM` chip now dissolve away. |
| `fx_phase_change_v3.gif` | The locked phase change v2; PHASE 2 and the `2 NEEDLES` chip now dissolve away. |
| `fx_enemy_defeated_v2.gif` | The locked enemy-defeated effect; DELETED now dissolves away. |

## The CORRUPTED overlay: what was ported
Round 15 `overlays.corrupted` was ported line for line into screen space, clipped to the slice wedge (bezel included). The tear bands may poke past the outline.
1. **Tear bands:** 5 bands of the whole slice slide sideways, ±6–20 px, re-rolled every 83 ms (12 fps loop).
2. **Pink/green split:** the outline and the bright content split into a pink ghost and a green ghost, ±3–5 px.
3. **Colour bands and scanlines:** pink/green colour bands on the screen and an 18 % scanline flicker.
4. **Tear line:** a bright pink/green line sweeps down the slice once a second.
- **Read window:** layers 2–4 thin to 35 % over the glyph and value block.
- **Godot:** the slice overlay `ShaderMaterial` with `state = CORRUPTED` (round 17 build notes). Add a `wipe_x` uniform for the apply (glitch takes the slice) and the tick (glitch leaves, then returns), and a `spike` uniform (tear amplitude ×2).

## Build
Run from `scripts/`:
- `python plates.py warm`
- `python fx_r23.py`

`scratch/` is git-ignored and cleared.

## Respin v3 (`fx_respin_v3.gif`)
- The temporary word now reads **RESPIN**, not CHECKPOINT. It still dissolves to bits.
- The undo block is shown on the **UNDO button** instead of a word. After the landing it greys out (200 ms fade) and a small lock tick appears on its top-right corner.
- The GIF is full frame so the button is in view. v2 is kept.
