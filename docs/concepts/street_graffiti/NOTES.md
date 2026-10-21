# Street graffiti cyberpunk concept stills (2026-10-21)

Seven panels from `BRIEF.md`, informed by `RESEARCH.md`. Each `NN_*_graffiti.png` is 1920 x 1080; `NN_*_sbs.jpg` is current
(left) vs graffiti (right) on the same camera; `contact_sheet.jpg` has all seven. Every 3D still is a Cycles render of the
base pipeline (AAA-2: volume fog, PBR, wet ground, light streaks) with the graffiti hook patched in at run time; nothing in
the base pipelines was edited. Panel 2 is a 2D mockup over panel 1.

**Render note:** the shared GPU queue had six agents waiting, so these were rendered on the **CPU** (no GPU use, no lock) at
1280 x 720 and 24-32 spp with denoising, then upscaled to 1920 x 1080. They are concept quality; a pick can be re-rendered on the
GPU at full size with the same scripts.

## What graffiti changes, per panel
1. **Netrun street** (`graf_street.py`): every frontage wall carries paint: bubble pieces with extrude and drips, chrome
   throw-ups, posters and Latin / kana tags dense to about 3 floors, thinning above, with blockbuster heaven spots high up.
   Tokyo vertical shop signs (kana / kanji, lit) hang at the building corners. The glass towers are painted too: a run with
   clean glass (`street/g1`) left whole blocks bare and was dropped for `street/g2`. Neon haze lights behind the frontage tint
   the deep fog pink / cyan / violet.
2. **Combat wheel** (`graf_panel_combat.py`): each wheel frame is a throw-up ring painted on the wall behind it (black
   outline, fluoro gradient, highlight dots, 30 ticks as paint slashes, drips off the bottom, two tags on the bezel). Slices
   stay CRT and the numbers stay bare Anton. This is the one place the look touches UI (see the bible note below).
3. **Whole city** (`graf_city.py`): light touch, per the designer. Paint only on the lower floors and on rare heaven spots,
   so it is a hint at this zoom. The change is the air: a thicker low fog in pink-violet scatter, lit by the district glow
   lights pushed most of the way to Cell neon.
4. **Halcyon**, 5. **Meridian**, 6. **Orbital**, 7. **Solace** (`graf_look.apply_hq`): the surrounding city gets street-band
   paint and about one block in eight carries a heaven spot. Each corp compound is painted only at street level, so its
   landmark, hue and crest read as before. The fog is thicker and its glow lights are retinted to neon.

## The bible question this set asks
ART_BIBLE 1.2 lists "spray paint and stencils, the dripping marker" and "neon-painting cities" as rejected media. Here the
graffiti is world dressing (paint on walls inside the 3D city), not a UI medium. The combat frame in panel 2 is the
exception: it shows what a painted frame would look like, and it would need a bible ruling before any build work.

## How it is built (`scripts/`)
- `graf_atlas.py`: the seeded atlases (PIL only): `graf_*` (the street layer: buffs, old pieces, posters, bubble pieces,
  throw-ups, skull characters, tags, wear), `heaven_*` (blockbusters, big roller tags) and `signs.png` (vertical shop signs).
- `graf_look.py`: the shader overlay. The atlases are box-projected in world space, with a random tile offset per world cell
  so the tile never repeats. Height zones and a wall/roof mask decide where paint goes. The paint is matte, partly covers
  lit windows, and fluoro paint has a small self-glow. Fog tint and glow-light helpers.
- `graf_street.py`, `graf_city.py`, `graf_blender_*.py`, `graf_run_*.py`: the hooks, wrappers and runners for each base
  pipeline (the same route the art-deco set used). Outputs go to `D:/rc_scratch/graffiti/`, never the repo.
- `gpu_lock.py`, `graf_gpu.py`: the GPU queue helper. It queues last, writes no waiting file, and takes the lock only when
  nobody else is waiting.
- `graf_pack.py`: the side-by-sides and the contact sheet.

```
S=docs/concepts/street_graffiti/scripts
python $S/graf_atlas.py D:/rc_scratch/graffiti/tex 7 4096 2048
python $S/graf_run_street.py g2 1280 24 cpu 'cfg={"fog_col":[0.88,0.72,1.0],"haze_w":200000,"skip_mats":["oc_wet","oc_neon","oc_win","oc_panel","oc_glane","oc_lane","oc_fog","oc_haze","graf_","oc_ground","r2_haze"]}'
GRAF_SPP=24 python $S/graf_run_hq.py <corp> art g1 cpu=true 'res=[1280,720]' haze_k=<8|4|6|3 for halcyon|meridian|orbital|solace>
python $S/graf_run_city.py g1 0.3334 32 cpu 'cfg={"aaa":{"fog_peak":0.15,"fog_base":0.10,"haze":0.0006},"glow_light_k":4.0,"neon_mix":0.85,"fog_col":[0.95,0.50,1.0],"target":0.155}'
python $S/graf_panel_combat.py D:/rc_scratch/graffiti/street/g2/plate.png D:/rc_scratch/graffiti/combat.png
python $S/graf_pack.py '{"street":"g2"}'
```
For a GPU run, drop `cpu`, raise the resolution and spp, and wrap each command in `python $S/graf_gpu.py <label> <log> -- ...`.

## Known weak points
- The HQ landmarks come out dimmer and less saturated than in the current plates. The thicker haze takes their light, and
  the exposure is solved to the same median. A pick would get a landmark lift, or less haze near the compound.
- The city panel is noisy (CPU fog fireflies at 32 spp). `graf_pack.py` runs a 3 x 3 median on it, which a GPU render would
  not need.
- The pieces are procedural letterforms, not hand-styled. Wildstyle in particular is simpler than the real thing.
- Lamp posts and other dark kit parts share the facade material, so they also pick up paint stripes.
- Some corner signs still overlap the existing centred shop signs on narrow faces.
