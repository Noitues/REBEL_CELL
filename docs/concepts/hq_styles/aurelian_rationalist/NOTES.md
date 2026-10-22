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

---

# v3 and v4 (2026-10-21)

## v3 (not rendered as a final)
v3 fixes (brighter frames, smaller statues, darker stylobate, softer terrace fill) were previewed only (`v3g`, 960 px; CPU, 6 spp). At thumbnail it
had a cleaner hierarchy than v2 (dark city, bright landmark) but the designer preferred v2's richness; v3's bigger arch at the entrance was a
v1 leftover. Its preview stands in as "v3" in `aurelian_v2_v3_v4.jpg` (upscaled; not a final render).

## v4: v2 base + v3's brighter teal + v1's fence + a reworked entrance (designer notes)
`aurelian_rationalist_v4.png` (1920x1080) and `aurelian_v2_v3_v4.jpg` (v2 | v3 preview | v4). Switch `rat.v2=true rat.v4=true` (`rat_patch4.py`).
- **One arch module.** Piers are re-spaced at equal arc length on all tiers (every grid arch has the same clear width, 1.37 BU, same height,
  same frame, keystone and sill). Before, bay widths ran 0.17 to 3.6 BU on the ground tier and 1.04 to 1.68 on the upper two (checked with
  `rat_bays.py` / `rat_bays4.py`); slivers narrower than 0.9 BU become solid pier wall.
- **Entrance and the ground-tier room bays.** The oversized lit arch frames of the base (`arch_frame` in the base landmark build) are suppressed at
  run time. The entry and the outer gate are now designed portals: rectangular opening 2.6 BU wide with deep jambs, a heavy lintel, a verdigris line,
  wide pilasters with capitals and bases, and a lettered tablet (abstract capitals) on the architrave band, aligned to the arcade rhythm;
  the two entry-flanking statues stand on plinths either side of the portal and face outward. The room bays (2.2 to 4.0 BU wide, where the game's
  rooms sit) are rectangular lintel openings with the same frame vocabulary, so a wide opening reads as a deliberate window bay, not a stray arch.
- **Fence.** v1's parapet is back as a balustrade: about 150 posts (turned shaft, cap, base) with a top rail and a lower rail round the wall top,
  skipping the eight attic statue plinths.
- **Teal.** Frame light 3.4x (gilt_k) at the lower exposure of this lighting, frame width 0.10: brighter than v2 and as bright as v3's, still thin.
- **Everything else as v2:** statues, inscription, pilasters, stone, paved arena, the drum.

## Why the final took long, and the hang
The first v4 GPU attempt (f4, 52 spp, with a light-linked moon) hung in Blender before sampling (no log output after the occlusion check) and was
killed. I rejoined the queue with a fresh waiting file. Changes made for the retry: (1) no light linking at all: the moon is a far narrow SPOT
(cone 24 deg, 900 BU away) instead of a linked sun, and the arena / drum / fill lights are unlinked (`rat.nolink=true`); (2) the moon, drum and
arena lights do not scatter in the fog (`rat.no_vol=true`), which would otherwise lift the whole frame and dim the city; (3) `rat_run.py` has a
watchdog (`watchdog=420`: no log output for 420 s kills only its own Blender PID with taskkill /T). The retry rendered normally. Whether linking
was the real cause is unproven (the same linking rendered fine for v1 and v2); it may have been the GPU, so treat the cause as unknown.
Timings: look-dev 8 CPU previews of 125-380 s; final Cycles GPU 1920x1080, 40 spp, 370 s wall (289 s Blender), median 0.165; queue wait about 2 h in total.

## Rebuild (v4)
```
S=docs/concepts/hq_styles/aurelian_rationalist/scripts
RAT_SPP=40 python -B $S/rat_gpu.py art_rationalist <log> -- python -B $S/rat_run.py art f4 watchdog=420 rat.v2=true rat.v4=true rat.win_boost=1.0 rat.nolink=true rat.no_vol=true rat.flank=true rat.flank_dt=0.30 rat.plaza_h=32 rat.moon=7 rat.L.gilt_k=3.4 rat.frame_w=0.10 rat.L.cavea_w=9000 rat.L.up_w=250 rat.L.vault_key_w=18000 rat.arena_w=350000 rat.drum_w=400000 'post={"bloom":[0.05,0.045,0.04]}'
python -B $S/rat_pack.py f4 v4
```

## v4 critique (viewed: previews v4a, v4b at 1280, v4c-v4f at 960, the first hung attempt's log, and the final at full size and 480 px)
- **Squint test (480 px, v1 | v2 | v3 preview | v4):** the colosseum ring, the arcade, the stepped terraces, the central drum, the four tower shafts,
  and "HQ in a dark city" all read. The balustrade is visible as a fine ring at the top (it reads as v1's fence). Landmark is the brightest
  area, the city the darkest. Better than v2 for the fence and the arcade glow, and richer than v1 and v3.
- **Arches:** at 1:1 every ground-to-top arch bay is the same module with the same frame; ground-floor rect bays and the two portals look
  deliberate (frame, sill, pilasters, tablet). The entrance is no longer an oversized round arch. Remaining weakness: the portal is only a
  little taller than a room bay and is half hidden behind the left tower at this camera; it is not "grand" at overview distance.
- **Stylobate:** the unlinked light and the matte stone lit the stylobate slab almost white; it is now the second-brightest flat area and pulls the
  eye at the frame's left and bottom (the v3 darker stylobate was the right call and should be merged into a v5).
- **Statues:** unchanged from v2: faceted, slightly large on the tower tops; the entry-flank statue at the bottom reads as a figure on a plinth but
  its wreath arm is clumsy. No smooth normals yet.
- **Terraces:** white risers and the soft light line read; the lit rings are still a bit silver in the shadowed part.
- **Teal:** brighter than v2 and clearer in the grid, but the verdigris lines on the terraces now compete (many concentric lines); thinning them
  to 0.04 would calm the cavea.
- **Noise:** none introduced by the balustrade; the city windows are fainter than v2 (lower exposure) but readable.

---

# v5 (designer-approved changes on v4, 2026-10-21)
`aurelian_rationalist_v5.png` (1920x1080) and `aurelian_v4_v5.jpg` (v4 | v5). Switch `rat.v5=true` (`rat_patch5.py`, plus `smooth_figs`, `no_attic`,
`near_h`, `sty_dark` in `rat_style.py`). Everything else is v4 (uniform arch module, balustrade, bright teal, no light linking).
- **Stylobate:** darker stone (albedo about 0.2 instead of 0.62; v3's idea), so the slab no longer blows out at the left and bottom.
- **Grand portal:** the entry and the outer gate now rise through two tiers (opening 2.6 x about 7.4 BU with a round head, against 2.5 BU for a room
  bay), a deeper reveal with an inner step, 0.95 BU wide fluted pilasters with bases and capitals, an architrave, a recessed tablet with abstract
  capitals, and a cornice. The tier cornice and architrave rings are cut across the portal, and tier 1's own arches are replaced by solid wall round
  the opening. The entrance sits at the visible front (it was never behind the left tower; the earlier thought was wrong).
- **Statues:** all attic and ring-top figures removed. The four tower-top colossi stay; the near one (front left) is scaled from 46 to 30 BU. All
  figures are lofted with 22 ring points / 12 tube points, welded and shaded smooth (a separate smooth-shaded mesh). The two entrance flankers stay.
- **Cavea:** terrace light lines 0.04 wide, the outer ones at 45 % brightness; a stronger soft cold fill over the arena (spot 700000 W) lifts the
  shadowed terraces.
Timings: one preview 1280x720 (297 s); first GPU attempt hung again at the same point as before (after the OCC lines, no sample output) and the
420 s watchdog killed only my Blender; the retry (300 s watchdog, 40 spp, 1920x1080) rendered in 369 s Blender, 461 s wall, median 0.161.
So the hang is NOT caused by light linking (it hit with no linking at all) and is intermittent; it occurs before sampling starts, so it is probably
the GPU or driver kernel/scene upload, not the scene content. Queue wait about 30 min plus the retry's.

## v5 rebuild
```
S=docs/concepts/hq_styles/aurelian_rationalist/scripts
RAT_SPP=40 python -B $S/rat_gpu.py art_rationalist <log> -- python -B $S/rat_run.py art f5 watchdog=300 <the v4 rat.* keys> rat.v5=true rat.no_attic=true rat.smooth_figs=true rat.near_h=30 rat.sty_dark=[0.18,0.20,0.23] rat.arena_w=700000 'post={"bloom":[0.05,0.045,0.04]}'
python -B $S/rat_pack.py f5 v5
```

## v5 critique (viewed: preview v5a at 1280, its portal crop at 4x, the final at full size, its portal crop at 3x, and a 480 px squint against v4)
- **Squint:** ring, arcade, terraces, drum, towers and "HQ in a dark city" all read. v5 is cleaner than v4: the wall top is now a calm balustrade
  ring (no figures), the stylobate is a quiet mid-grey slab, the landmark is the brightest object, the city the darkest.
- **Portal:** at 1:1 it reads as a deliberate grand entrance (tall, fluted pilasters, tablet, cornice, lit steps inside). At overview distance it is
  about twice a room bay's height and visibly different, but still small in a 1920 frame (about 60 px wide); it needs the lit teal frame line on the
  pilasters, and a verdigris glow inside, to read from far.
- **Tablet:** the abstract lettering is only legible when zoomed in; at overview it is a pale band.
- **Statues:** the smooth colossi look better (no facets) but remain stylised blockish bodies; the front-left tower figure is now small relative to the
  tower and the other three tower tops are still large. The entry flanker's wreath-holding arm reads oddly.
- **Cavea:** the thin dim lines no longer fight the arcade; the shadowed terraces are lighter but still silver-grey rather than white on the right
  side where the tower shades them.
- **Value hierarchy:** fine; one remaining bright spot is the plaza around the plinths (mid-grey), acceptable.
