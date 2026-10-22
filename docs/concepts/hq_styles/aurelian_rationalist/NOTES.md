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

---

# v2: refined detail pass (2026-10-21)

`aurelian_rationalist_v2.png` (1920x1080) and `aurelian_rationalist_v1_v2.jpg` (v1 | v2). v1 files are unchanged. Switch: `rat.v2=true`
(`rat_patch2.py`, `rat_statue.py`, the v2 branch of `rat_style.py`).

**What v2 changes.**
- Arches: taller and narrower (wider grid piers), each with a flat proud frame, a keystone block, a projecting sill and a recessed inner
  frame in a deep reveal (real shadows under the moon); the verdigris line is thinner and sits on the frame edge.
- Wall: rusticated base courses, an architrave band and stepped cornice on every tier, and an abstract relief inscription (monumental
  capitals made of bars, no real words) on the attic.
- Towers: stepped plinth, four pilasters per face, stringcourses, heavy cornice.
- Stone: per-block tone variation, pitting (bump + darkening noise) and clearer joints on the engine's civic material.
- Statues: 12 slender figures (contrapposto athletes and draped figures, raised arm with spear or laurel) replace the 60 blocks: 4 on the tower
  tops, 4 on the attic parapet, 4 on plinths in the piazza.
- Terraces: white risers with a soft light line and a cold arena spot, so the rings read white; the arena has stone paving (joint grid, matt).
- Verdigris: oxidised copper (#2BBF8F-ish, linear 0.024 / 0.52 / 0.275), thin lines, bloom cut to 40 %. The drum is now two-stage (24 piers,
  pilastered upper drum, stepped cap) with its own cold key light. The axis lines are paired and sit at x = +-62 so they reach into frame.

**Research (pages only, in addition to the list above).**
- [Palazzo della Civilta Italiana (it)](https://it.wikipedia.org/wiki/Palazzo_della_Civilt%C3%A0_Italiana): 54 full-round arches per face, 28 statues
  in the ground-floor arches, Dioscuri groups at the base corners, a three-line inscription in monumental Roman capitals carved in the travertine
  near the top. Taken: the inscription band (abstract), statues as part of the arcade, the corner groups.
- [Palazzo dei Ricevimenti e dei Congressi (it)](https://it.wikipedia.org/wiki/Palazzo_dei_Ricevimenti_e_dei_Congressi): piers clad in travertine that
  serve as support rather than ornament, full travertine cladding. Taken: wide plain piers and a flat frame instead of columns.
- [Stadio dei Marmi (it)](https://it.wikipedia.org/wiki/Stadio_dei_Marmi): 60 marble statues of athletes (discus, javelin, wrestling) on terraces of
  white Carrara marble, donated plinths. Taken: athletic poses (raised spear or laurel), white terraces; fewer, larger figures instead of 60.
- No page gave reveal depths, pier ratios or slab sizes; those numbers are my estimates (pier half-width 0.78, frame 0.17, reveal 1.7 BU).

## v2 timings and values
Look-dev: 6 CPU previews (480x270 to 1280x720), 90-330 s each. Final: Cycles GPU 1920x1080, 52 spp, 161 s render + build wall; median 0.157;
GPU queue wait 4804 s (FIFO).

## v2 rebuild
```
S=docs/concepts/hq_styles/aurelian_rationalist/scripts
RAT_SPP=52 python -B $S/rat_gpu.py art_rationalist <log> -- python -B $S/rat_run.py art f2 rat.v2=true rat.moon=7 rat.L.gilt_k=0.7 rat.frame_w=0.09 rat.L.cavea_w=9000 rat.L.up_w=250 rat.L.vault_key_w=18000 rat.arena_w=350000 rat.drum_w=400000 'post={"bloom":[0.05,0.045,0.04]}'
python -B $S/rat_pack.py f2 v2
```

## v2 weak points
- Statues are still faceted low-poly (flat shading); smooth normals and a drapery pass would help, and the tower-top and attic figures are
  still a little large against the arcade.
- The arch coffering is only a recessed inner frame; no true coffers. The inscription is abstract bars, only legible as lettering up close.
- Moon shadows from the figures and pilasters are strong on the wall; the terraces are silver rather than white in the shadowed half.
- The front plaza colossi and the far axis lines sit at the frame bottom; only one pair of axis lines is clearly visible.

## Critique (designer rule: view and critique every output; squint test at 480 px, v1 left, v2 right)
Reviewed: previews v1p, v2p, v3p, v4p (v2 look-dev) and the final f2; the earlier v1 previews p1-p11 and final f1.
- **Form (squint):** v2 passes on the colosseum ring, the stepped cavea, the white drum with the verdigris mast, the four tower shafts, and "a
  lit HQ in a dark city" (city is the darkest value, landmark the brightest). It does not beat v1 at thumbnail size.
- **Arcade: regressed.** The thinner, deeper-green verdigris lines (0.09 wide, 0.7 k) and the mid-grey stone make the arch grid read as a
  grey wall with faint arches; v1's bright frames gave a clearer, glowing grid. The detail (frames, keystones, sills, inscription) only
  appears at full size. Fix: raise gilt_k to about 1.0 and frame_w to about 0.11 (a thin line, but brighter), keep the oxidised colour.
- **Statues: clutter.** 12 figures is the right count but they are too big: the front plaza figure and the left tower figure cover arches and
  fight the tower shafts, and the white figures on the attic read as noise at thumbnail size. Fix: attic_h 22 to about 14, tower-top figures
  about 38, drop the front pair that overlaps the arcade, and give the figures smooth normals.
- **Terraces:** still silver-grey rather than white in the shadowed half; the arena spot lifts them but washes the highlights. The paved floor
  reads (grid visible) and is no longer black. A second, softer fill, not a stronger spot, is the fix.
- **Stylobate / piazza:** the large pale slab at the frame's left and bottom is the brightest flat area in the picture after the wall and pulls
  the eye; it should be darker (about half) so the landmark keeps the top of the value hierarchy.
- **Stone detail:** pitting and joints are visible on the towers and wall at full size, and add some weight without noise; the inscription
  reads as lettering. Good.
- **Verdict:** v2 is richer at 1:1 and fails the squint comparison on the arcade glow and statue clutter. These fixes were identified after the
  final was rendered; applying them needs one more GPU slot (queue wait was about 80 min), so v2 is left as rendered and the fixes are listed above
  for a v3 pass.
