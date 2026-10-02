# Round 22: combat FX revisions

**Base:** the locked D4 combat screen (no NEXT arrows). The round 21 scripts were copied here, plus a local copy of `sticker_lib19.py` from `round20_raid_ui`. Earlier rounds are untouched. All new code is in `scripts/fx_r22.py`.

## Rules (in force from this round)
1. **Card effects come from the card play** (from round 21). The sticker slaps on the target wheel and dissolves (dissolve A, the bit stream). The effect's bits leave from that slap point.
2. **Labels are temporary.** No word sticker, rule chip or tag stays on the screen after an effect.
   - Each one pops in, holds about 0.7–0.8 s, then **dissolves left to right into 0/1 bits** in its own colours. The bits drift up 60–140 px/s and fade within 0.5 s.
   - A slice keeps **only** its locked state overlay (the tear bars) and its corner badge. The badge is printed flat in the overlay layer; it is not a vinyl sticker.
   - **This applies retroactively** to `EVADED` (evade v3), `CHECKPOINT` (respin), `PHASE 2` (phase change v2) and `DELETED` (enemy defeated). In game each uses the same `TempLabel` behaviour; those locked GIFs show them held only because they were made before this rule.
   - **Godot:** one `TempLabel` scene (a sticker `Sprite2D` plus a dissolve shader with a `wipe_x` uniform). It shares the 0/1 emitter with dissolve A (`emission_points` from the label's alpha cells, spawn delay proportional to x). It frees itself when the last bit dies.

## Files
| File | Change |
|---|---|
| `fx_drone_destroyed_v3.gif` | The `HP 0` chip is gone. The drone sticker's own HP plate counts **5 → 0** in 150 ms from the impact: the plate turns red and flashes, and the drone then breaks apart reading 0. The `-5` number stays, with no sub-label. |
| `fx_corrupt_apply_v3.gif` | As locked v2 (card slap, then dissolve A into the slice). The rule chip `CORRUPTED: 3 self-dmg, -1 RAM` now pops in, holds 0.8 s, then binary-dissolves. The badge is the flat printed corner badge, not a vinyl sticker. Only the tear overlay and the badge remain. |
| `heat_city_v4.gif` + `heat_city_v4_strip.png` | NOTICED and HUNTED as in round 21. **New FLAGGED:** two searchlights from rooftops at the screen sides, sweeping the sky **away** from the target, plus **two alarm beacons on the target building**. There is no police-light cluster. |
| `send_it_sticker.png` | SEND IT restyled as a raid-style vinyl sticker (see below), shown on the combat screen and in four states. |

## SEND IT sticker
- **Look:** the same toolkit and recipe as the raid **START DEFENSE** sticker. It uses `sticker_lib19.lettering`:
  - Anton, keyline 6, extrude 9, pink gradient `#FF60AC → #DE1270`;
  - `build_sticker`: die-cut white border 15, gloss 0.22 at rest;
  - −3° tilt.
- **Underneath:** the washed-out system word **EXECUTE** (Share Tech Mono, scanlined, about 45 % alpha, with a `> turn_resolve.exe [SPACE]` caption). This follows the overlay rule: marker or sticker verbs go over system words.
- **States:**
  - **Hover:** lift 0.6, ×1.05, a 0.12 top-right corner curl and a full gloss sweep (gloss_k 1).
  - **Pressed:** squash 1.04/0.90, and the shadow snaps in (0.6).
  - **Disabled** (while resolving): greyscale vinyl at 80 %, with a `RESOLVING...` chip.
- **Godot:** a pre-baked sticker texture per state (idle, hover, disabled); pressed is the idle texture with a scale tween. EXECUTE is a `Label` under it with a scanline material.

## Open
- The EXECUTE word is wider than the sticker, so its edges show on both sides. If that reads as clutter, cut it to `EXEC` or make it smaller.

## Build
Run from `scripts/`:
- `python plates.py warm`
- `python fx_r22.py`

`scratch/` is git-ignored and cleared.
