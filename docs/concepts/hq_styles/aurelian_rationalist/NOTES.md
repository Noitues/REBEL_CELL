# Aurelian Concord HQ, Rationalist Rome (exploration, 2026-10-21)

Exploratory single-HQ concept; no decisions logged. `aurelian_rationalist.png` (1920 x 1080, golden-plate overview camera) and
`aurelian_rationalist_sbs.jpg` (current golden plate | rationalist).

**What changes.** The Circus Aurelius keeps its footprint, three tiers, ring radii, room bays and Rostrum height, but is re-skinned in cold
white travertine: the outer wall is a flat-slab grid of identical round arches with deep reveals, no engaged columns, no archivolts, no
cornice mouldings, each opening framed by a thin verdigris light line (the grid glows); the seating rings are stark stepped white
terraces; the ring temple is a white 24-pier drum on a porphyry pad around a verdigris-lit core; the four round campanili become square
white shafts with slit lights, each carrying a colossal blocky figure; a ring of 60 small white athletes stands on the attic. The gilt
#C9A35A is gone (verdigris #29DBA6 as true linear light, travertine, porphyry #3A1426). The piazza is dark wet stone with a joint grid,
a three-step stylobate and two long verdigris axis lines. A low cold "moon" (sun, 15 deg, light-linked to the landmark, piazza and
statues only; the city casts no shadow on it) gives the raking shadows and god rays. The city is near-black blue-grey with cold windows.

**Method.** Nothing in the base pipeline is edited. `rat_blender.py` loads the Aurelian modules (`aur_env`), `rat_patch.py` patches
the palette and replaces `aurelian_landmark.canonical` in memory, then `hq_scene.py` runs with `rat_style.py` hooked in front of its render
section (the art-deco pattern). `rat_run.py` is the driver and does the post (`hq_post.finish`, exposure solved to median 0.16).

## Timings and values (RX 6700 XT, HIP, OIDN)
| Step | Result |
|---|---|
| Look-dev previews | CPU, 480x270 to 1280x720, 3-10 spp, 90-230 s each (11 runs) |
| Final | Cycles GPU 1920x1080, 52 spp: render + build 118 s wall (140 s with post); queue wait 450 s |
| Frame median (luma) | 0.157 |

## Rebuild
```
S=docs/concepts/hq_styles/aurelian_rationalist/scripts
RAT_SPP=52 python -B $S/rat_gpu.py art_rationalist <log> -- python -B $S/rat_run.py art f1 rat.moon=7 rat.L.gilt_k=1.0 rat.frame_w=0.13 rat.L.cavea_w=9000 rat.L.up_w=250 rat.L.vault_key_w=18000
python -B $S/rat_pack.py f1
# CPU preview: python -B $S/rat_run.py mini p1 cpu=true samples=8 'res=[800,450]' <same rat.* keys>
```
Output goes to `D:/rc_scratch/hq_styles/aurelian_rationalist/<tag>/`. `rat_gpu.py` takes the shared GPU lock (FIFO by waiting-file mtime).

## References (read as pages only; no files or images copied)
Traits taken from the pages, and what they became in the scene:
- [Palazzo della Civilta Italiana](https://en.wikipedia.org/wiki/Palazzo_della_Civilt%C3%A0_Italiana): 9 x 6 identical arches per face, travertine slabs on a plain
  skeleton, 28 statues of about 3.4 m under the base arches, Dioscuri groups at the podium corners, a stylobate. Taken: many identical stacked arches
  with no ornament, flat slab cladding, a stepped stylobate, statues as scale cues, colossal figures at the corners (on the campanile shafts).
- [Casa del Fascio, Como](https://en.wikipedia.org/wiki/Casa_del_Fascio_(Como)): half-cube volume, opaque marble slabs balanced against voids, loggia
  recesses. Taken: strict solid/void balance, deep reveals (dark soffits), clean heavy entablature slabs.
- [Stadio dei Marmi, Foro Italico](https://en.wikipedia.org/wiki/Stadio_dei_Marmi): 60 Carrara marble athletes, about 4 m, in a ring round the arena.
  Taken: the ring of 60 identical white figures on the attic parapet.
- [EUR](https://en.wikipedia.org/wiki/Esposizione_Universale_Roma): orthogonal axes, travertine / marble, simplified neoclassicism inspired by
  metaphysical art, axial planning. Taken: strict symmetry, two parallel verdigris axis lines across the piazza, cold stone palette.
- [Metaphysical art / de Chirico](https://en.wikipedia.org/wiki/Metaphysical_art): empty squares, receding arcades, low raking light, long
  shadows, tiny figures for scale. Taken: the low light-linked moon (15 deg) with long shadows across the arcade and cavea, dark empty piazza, small figures.
- Not fetched successfully (pages lacked the detail): Libera's Palazzo dei Congressi (the pier-and-cube colonnade idea was used only through the
  square-pier drum), Piacentini's Rome University (no usable detail found).

## Weakest points
- The statues are crude blocky figures (they read as robots or crosses); they need a sculpted silhouette.
- The ring temple's white drum is small and mostly in shadow; the verdigris core mast, not the white drum, carries the read.
- The wall grid is round arches, close to the Colosseum; a squarer arch with a heavier pier would say Rationalism more.
- Verdigris is bloomy and minty; the neon is a little thick at the ring lines on the terraces.
- Terraces and arena floor are dark grey in the moon shadow rather than stark white; the arena floor is a glossy black mirror.
- The front colossi and piazza axes sit at the cropped frame bottom and barely register.
