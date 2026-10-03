# Round 27: Meridian fortress and the Halcyon regular Site

## What is locked, and where it comes from
- **Locked from round 26:** Solace, the Halcyon HQ, Orbital, and the combat zoom framing. The comparison sheet reads their images from `round26_hq_targets/`, read-only.
- **Rules carried over:** the map = close-up rule and the view-corridor rule.
- REBEL_CELL is still the round 25 base on the map.

Earlier rounds are untouched. `scratch/` is cleared, and nothing is committed.

## Meridian: an angular container fortress
**`meridian_fortress_options.png`** compares four takes. Each shows a night close-up facing the gate and a map sprite at two sizes. None of them uses round shapes.

**Shared readability kit:**
- dark rust curtain walls against floodlit orange square towers;
- lit amber battlement lines;
- banners;
- a glowing gate with a portcullis, a container drawbridge and a lit moat.

The four takes:
- **A: the Container Wall (chosen).**
  - A straight curtain four containers high, with crenellated tops.
  - Square stacked corner towers whose container courses cross each other.
  - A square gatehouse.
  - A regular glass-and-steel MERIDIAN FREIGHT office tower standing inside.

  Of the four it reads most clearly as a fortress, both face-on and on the map.
- **B: stepped bunker.** It reads as a ziggurat again, which clashes with Halcyon.
- **C: walled freight yard with lattice watchtowers.** The weakest "fortress" read from afar.
- **D: citadel with a gatehouse face.** Strong face-on, but a single blocky mass on the map.

**Files:**
- `hq_meridian_city.jpg`
- `hq_meridian_close_night.jpg`, `hq_meridian_close_day.jpg`
- `combat_meridian.jpg`, facing the gate at the round 26 zoom.

The Meridian map sprite is drawn at 0.85 brightness, because the lit-toon towers are already bright. The regular Site is still the locked depot.

## Halcyon regular Site
**`halcyon_site_options.png`** compares three options, all on the same plot:
- **A: sculpted sphinx.** A smooth tube-sculpted body, chest, paws and head under a banded nemes headdress. It is better than the round 26 sphinx, but still lumpy at Site scale.
- **B: Halcyon Court with a Justice statue (recommended).**
  - A temple front with columns and a pediment bearing the eye.
  - A giant Justice statue: the eye replaces her blindfold, and she holds lit amber scales.
  - It reads instantly as "civic power".
- **C: surveillance obelisk.** Camera rings with red lights and the eye at the tip. It is strong, but close to Orbital's mast.

Court is now the default Halcyon Site (`site_halcyon_court_night.jpg`).

## Files
| File | What it shows |
|---|---|
| `meridian_fortress_options.png` | The four Meridian fortress takes. |
| `halcyon_site_options.png` | The three Halcyon Site options. |
| `hq_meridian_*` | The chosen Meridian fortress (city crop, close-ups). |
| `combat_meridian.jpg` | The Meridian boss fight. |
| `site_halcyon_{court,sphinx2,obelisk}_night.jpg` | The three Halcyon Sites. |
| `city_night_hq_v5.jpg` | The full city night view. |
| `hq_compare_v3.jpg` | The comparison sheet. |

**Build** (from `scripts/`):
1. `python citydata.py`
2. `render_all27.ps1`
3. `python backdrop27.py`
4. `python city_hq_v5.py`
5. `wheels_r18/render_bosses24.py meridian`, `wheels_r18/dump_boss_slots24.py` and `combat_r23/render_player24.py`
6. `combat_r23/make_combat27.py meridian`
7. `python make_sheets27.py`

New code is in `heroes27.py`. The option previews are `hq_scene.py -- meridian_hq <dir> preview|mapprev <wall|bunker|yard|citadel>`.

## Open
- **The fortress is tall and fills the gap between the wheels in combat.** The office tower inside is partly hidden behind the gatehouse face-on, so its MERIDIAN FREIGHT sign shows above the gate.
- **The Court's Justice statue is slim at map scale.** The scales carry the read.
