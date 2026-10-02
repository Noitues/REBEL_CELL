# Round 18: Solace and Meridian fixes, and the PRIORITY glyph

This round builds on round 17 (`round17_corp_wheels`, which is left untouched).
- Glyphs are round 17's final set (`round17_slice_system/scripts/glyphs17.py`).
- The animated card-play preview is locked as it was in round 17. It is not redone here.
- Halcyon, Orbital and Rebel Cell are unchanged. They are re-rendered only for `corps_compare.jpg`.

## Files
| File | What it shows |
|---|---|
| `corp_solace.png`, `motion_solace.gif` | The Solace kit sheet and its looping animations. |
| `corp_meridian.png`, `motion_meridian.gif` | The Meridian kit sheet and its looping animations. |
| `corps_compare.jpg` | The 5 bosses through phases 1, 2 and 3, plus the 5-corp squint test. |
| `special_priority.png` | The new PRIORITY glyph: 256 px, white on transparent. |
| `scripts/` | Everything needed to rebuild. |

**Rebuild:**
- `python scripts/make_round18.py corp solace|meridian`
- `python scripts/make_round18.py compare`
- `python scripts/glyph_priority.py` (also prints the twin scores)
- `python scripts/clear_cache.py all` clears the render cache.

New files this round: `scenes18.py`, `kits18.py` and `glyph_priority.py`. `crests15.CUSTOM` now registers `PRIORITY`.

## Changes
1. **Solace GROWTH.** The pink pinch arrows are gone. One round cell divides into two: the nucleus splits first, the cell pinches, then two round cells part.
2. **Meridian DEFEND.** The wall is laid in an offset bricklaying pattern (running bond), with every course offset half a container from the one below. The wall's top course is laid at the value's height:
   - container 1 drops in behind the "12";
   - container 2 lands next to it at the centre of the slice.

   Both drop from the crane jib on the outer edge. They are drawn brighter than the wall so they still read under the darkened read plate.
3. **Meridian swap.** The judgement theme didn't fit a shipping company.
   - **CRIT is now AIRMAIL.** A cargo plane flies from bottom-left to top-right, leaving a twin contrail.
   - **The RAM-drain slice is now PRIORITY.** Its screen uses the previous crit animation: a parcel slides in, PRIORITY is stamped on it, and it ships out.
   - **PRIORITY glyph (`special_priority.png`).** A rotating alarm beacon:
     - a tall rounded dome with a highlight cut-out;
     - a thick base plate, separated from the dome by a dark gap;
     - 5 short rays fanning out.

     It is a bold flat white silhouette in the round 17 glyph language.
   - **16 px twin check.** Soft-IoU against every glyph in `round17_slice_system/glyphs/`. The highest scores are VIRUS (biohazard) 0.56, TROJAN 0.53, CITATION 0.49 and WEIGHT 0.49, all under 0.62. A first, wider dome scored 0.61 against SOLAR FLARE, so I narrowed and heightened it.
   - **JUDGEMENT** (the gavel glyph and the gavel animation) stays in the library, unused (`special_judgement.png`; `scenes17.mer_judgement`).

## Weakest parts
- **The DEFEND containers sit behind the read block by design,** so they are partly hidden. The drop and the brighter colours carry the read.
- **The AIRMAIL plane is small at kit-sheet size.** It reads clearly in the GIF.
