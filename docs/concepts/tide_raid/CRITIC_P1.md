P1: S8 V8 Read8 Motion8 Wordless8 · beats bar on: — (ties S only) · gap: V-1 Read-1 Motion-1 Wordless-1

# Fresh critic, polish iteration 1 (2026-10-27)

Method: viewed sheet, plate 01/03/05/07 at 1:1, the 04 hot crop, squint strip, deutan/tritan strip, four motion contact sheets,
board 08, `P1_motion/NOTES.md` timing claims, interactivity frames 02b and 03a, `P1_interact/NOTES.md`. I did not extract MP4 frames: the
contact strips at 3-5 f spacing were enough to read order, holds and the head sprite used. Bar (REF_BASELINE): S8 V9 R9 M9 W9. To pass,
beat S, V, R (so S9, V10 or V9 with the clearest read, R10 or R9 with nothing below reference) and meet M and W.

## Scores

| Part | S | V | Read | Motion | Wordless | Note |
|---|---|---|---|---|---|---|
| Plates (P1_plates) | 8 | 8 | 8 | n/a | 8 | The strongest part. Real occlusion and spill; a vivid city. |
| Motion (P1_motion) | 7 | 6 | 8 | 8 | 8 | Timing spec is excellent; the pixels are a 2D comp on the old plate. |
| Interactivity (P1_interact) | 7 | 6 | 8 | n/a (stills) | 8 | Grammar is the best idea in the set; the frames sit on the older, darker plate. |
| **Whole** | **8** | **8** | **8** | **8** | **8** | Weighted to the plates; V and Motion are capped by the other two parts. |
| Bar | 8 | 9 | 9 | 9 | 9 | |

Does it beat the bar? **No.** It ties S (8, not a beat: "beat" needs 9), and is one point short on V, Read, Motion and Wordlessness.
This is a big step up from pass 2 (flat PIL overlays), but it is a strong 8 across the board, not a 9-10 anywhere.

### Why, per axis, against the named holder
- **S 8 = Frostpunk / Bad North, tie.** The threat is a lit physical ribbon and CITY LOST is a real event (plum flood plus a skull). But the
  threat is a thin line over a big city: no Bad-North silhouette (the biggest dark shape in the frame), no Frostpunk horizon front. HOME
  integrity and the Bloom are still quantity-as-numbers in the HUD (44/50, 11). The Bloom front only exists in plate 07; it never creeps in
  plates 01-06. To reach 9, pressure must be visible on the map before anything is hit.
- **V 8 vs CP2077 / Google / Frostpunk 9.** Genuine wins: depth-true occlusion, the ghost pass, rain and bloom, light columns, towers
  as lit volumes. Not 9 because: (a) the whole frame is one indigo-violet value band, so the city is "vivid" only in tiny window
  chips; there is no warm/cool contrast, no hero light and no sky or horizon, which Frostpunk and CP2077 have; (b) the city
  textures are low-resolution and painterly (the 04 crop at 2x shows pixelated ink outlines and mush, not material: no wet streets,
  no reflections, no emissive signage); (c) the 2x crops are upscaled, which the notes admit; (d) the towers and the cage are flat
  white-blue wireframes of the same value as the beams, so nothing is a clear light source; (e) UI (cards, chips, tiles) is still the
  pass-2 kit and looks like a different, flatter material than the city (the 01 hand cards read as stickers). Fair V is 8: better than
  Bad North, below Frostpunk's painterly depth and CP2077's light.
- **Read 8 vs ITB / Mini Metro 9.** Squint (320 px): HOME ring, beam and the HQ cage read; the Sites do not (the 320 strip shows no
  defended-Site mark at all in 01, only the tower clump). In 01 three ribbons plus 10 towers plus the cage plus the eye plus the A/B/C
  locks in one 400 px band is clutter by Mini Metro standards. Yellow E is the loudest object, so the strongest signal in
  the frame is one type of beam, not the HOME threat. Heads at 44 px are lost at 320 px.
- **Motion 8 vs CP2077 9.** The numbers are right and the design is arguably better than any reference on paper (asymmetric in/out,
  held peak, reduce variants, skip codes, a table that maps to `tide_look`). But this is judged on the delivered pixels: the tests are
  2D composites over a still, with no camera, parallax, depth or shader response; the daemon head is the old dart, not the locked worm.
  The one shake is the only novel idea and is correctly gated. CP2077's 9 is real-time over real depth. A 9 needs the Godot capture.
- **Wordless 8 vs Mini Metro / Bad North 9.** Clean frames carry no words except HUD numerals and the DAMAGED poster; the tally of
  pictograms (shields, bars, hearts) works without text. But the wheatpaste "DAMAGED" poster in 06 is a word, and 08 onboarding
  and disc hover words are in the design. The 06 aftermath says "damaged" with a word where a cracked HOME ring would do.

## Requested checks

- **Vision (living vibrant night city, not a dark map): partially met.** Better than a dark map: windows, parks, dense geometry, rain, bloom.
  It is a violet monochrome with a lot of small bright squares, not a lit city. Where it is alive is around the route; away from the route
  (right, bottom, left) it is uniform and a bit dead. The 28 % off-route dim plus indigo lift removes the sense of a city living beyond the
  raid. Add warm streets, a skyline glow and one or two hero lit buildings.
- **No-panel: yes for plates, mostly for interactivity.** 01-07 contain no panels. P1_interact needs the tally tray (a panel in 03a)
  and the hand strip; those are pictogram trays, not panels of text, so the raid can run without text panels, but not without trays.
- **Squint:** beam yes, HOME yes (white ring), HQ cage yes. Defended Sites: no, they vanish (the 320 px strip shows only the tower cluster).
  Heads and tags: no. 03 and 06 are weakest (03: the reveal is pale lavender, 06: nearly empty).
- **Colour-blind:** Deutan: D blue and N magenta both go blue-lavender, and the E yellow stays distinct; pattern (chain links versus
  braid versus chevrons) does the work. It holds at 1920, not at squint. Tritan: the yellow E turns pale pink-white and DAMAGED goes
  salmon; HOME-hit 05 still reads through the starburst shape (good, a real non-hue cue). The 04 flash looks the same in all three.
  The ruling "DAMAGED orange vs N magenta vs BREACHED" is better than pass 2, not solved: salmon vs N magenta in tritan 05 are
  near-neighbours in value.
- **Clutter:** t1 cluster (the three towers at left plus ring plus block plus tile plus old-ring ghost) is the worst spot, in both plates and
  interactivity (03a tally diff is a tangle past 4 changes, as the notes say). The towers: 10 wireframes of equal weight read as a forest
  of glass, not a ranked threat. The cage: bright, tall, and the same cyan-white as the towers, so it competes with the beam at squint.
- **Consistency: poor between parts.** This is the biggest process finding.
  - Plates use the H6 locked heads (D worm, N claw, E mine) with the P1 grade and the new Blender city.
  - **Motion tests and interactivity use the pass-2 heads (dart, bracket block, ram) over the older, flatter plate** (`plates/clean/default`),
    with a darker, more desaturated grade and the old cage; the interact notes say so ("Heads are the current pass-2 heads").
  - The motion strip for HOME shows a magenta pass-2 head and an FF6A1A-ish orange hex; the plates changed DAMAGED to FF9A00 and SITES LOST
    to C98410. The interact frames still show an amber ring in the old yellow-orange.
  - Consequence: a reviewer cannot say the three show one game. A Godot session cannot match all three at once.
- **Godot buildability: good for most, risky in four places.** Depth-holdout occlusion (ribbon x-ray pass, ghost corridor), towers
  as alpha shader plus wire, grade as a post parameter, ground-mist sealed corridors, the Bloom as a field-driven overlay shell: all
  buildable and specified with numbers. Risks: (1) the ghost pass plus the "darkened corridor of the city under it" needs a custom
  depth-inverted pass and a ground decal, not a one-liner; (2) the plates are built from a baked 0.6 BU height field and a plate
  projected as albedo, so the Godot city (real meshes) will not match unless the grade and AO are also matched; (3) rain and light
  columns near lights are comp-time, so they will need a screen-space pass; (4) the Bloom shell body with Voronoi veins plus the
  hot hairline plus not being sampled as a light is under-specified for Godot lighting. Build sketch is honest and good.

## The SITES LOST colour change (F29A1A to C98410): does it work?
Partly, and I would not keep it as is.
- It fixes the actual conflict (DAMAGED FF9A00 beside SITES LOST F29A1A was nearly identical), and C98410 is separated from FF9A00 by
  value (a darker ochre) and, in the plates, by a diagonal hatch against the DAMAGED chevrons. Value and pattern are the right channels.
- But it creates two new problems: (a) an ochre-brown ring on an indigo city at night is the lowest-contrast mark in the system, yet
  SITES LOST is the second worst news the player gets; at squint it is gone. (b) It sits within about 15 degrees of hue of E yellow
  and FF9A00, so deutan and tritan collapse all three to "yellow-ish things", leaving the hatch as the only cue, and hatching
  does not survive 320 px. (c) It is not applied in the motion tests or interact frames.
- Better: keep the hue family, but carry the loss by **value and shape**: an ink-black filled ring with a white outer rim and a bold C98410
  diagonal hatch (a "blacked-out" Site), so SITES LOST is the darkest, most solid thing in its neighbourhood rather than a dim amber one.
  Or let the tier be carried by a glyph (a collapsed hex) and drop hue as a tier cue altogether.

## Iteration-2 punch list (ranked by score impact)

1. **One source of truth across the three parts.** Beat: all. Wrong: motion and interactivity use pass-2 heads and the old plate and old
   palette. Fix: rebuild the 4 motion tests and the 12 boards' hero frames, and the interact clean frames, on the P1 depth-true plate with H6
   heads (worm / claw / mine at 44 px) and FF9A00 / the new SITES LOST. Axes: V (6 to 8 for two parts), Read, Motion (to 9), consistency.
2. **Break the single indigo value band; add warm/cool and a hero light.** Beat: 01-07. Wrong: the whole frame is one violet value
   and hue, so V caps at 8. Fix: add a warm sodium-orange district glow and a cool teal canal or sky reflection, wet street speculars
   under the beam, one lit landmark; keep the off-route city cooler but not dead. Axes: V +1 (the main route to 9).
3. **Make the Sites readable at 320 px.** Beat: 01, 02, 04. Wrong: tier rings and blocks vanish at squint; only the tower clump reads.
   Fix: a tier ring about 1.6x bolder with an ink under-stroke and a white inner rim, a stop-block wedge in value contrast against the street
   plus a pulsing HOLDS bar silhouette, and test on the 320 strip until each defended Site shows as a dot. Axes: Read +1 (the squint
   win condition).
4. **Rank the towers: hero versus quiet.** Beat: 01, 02, 05. Wrong: 10 towers plus the cage at equal weight and a similar cyan-white to the beams.
   Fix: only the towers that stop a beam get the bright wireframe and scanlines (about 5), the rest at 35 % lit glass with no wire; the
   cage at 60 % brightness and shifted to a Solace green or teal so it stops sharing the beam hue; drop the gold light column from E to
   keep one yellow. Axes: Read +1, V +0.5.
5. **Yellow E is loudest; reduce its bloom, grow the HOME read.** Beat: 01-02. Wrong: E at 4.8 BU with the strongest glow outshines the
   HOME ring and the other types. Fix: cut E bloom by 40 %, give HOME the brightest white ring, a warm pool and a physical ticked
   gauge that reads as a quantity (tick ring thicker), so the pressure is a shape at squint. Axes: Read +1, S +0.5.
6. **Show pressure on the map before the hit (S to 9).** Beat: 01-04. Wrong: threat is a thin ribbon; the Bloom front appears only at 07.
   Fix: a faint plum creep at the edge of the HQ cage that grows plate to plate, a visible dread shadow ahead of the head (a dark corridor
   in front of it), and the DOWN clock as a drained ring. Frostpunk's cold front and Bad North's longships do this. Axes: S +1.
7. **City material and texture resolution.** Beat: all, especially the 2x crops. Wrong: pixelated painterly outlines, no
   reflection, no signage, upscaled crops. Fix: re-render the hot-spot crops at native 2x (3840x2160) or accept that the plate is 1920
   native, add wet-ground reflection of the ribbons, emissive signage on 10-15 hero facades, and a sharper ink line only on hero
   buildings. Axes: V +1.
8. **Impact flash is blown out and eats the head.** Beat: 04, 05. Wrong: in the 04 crop the head is a small ink worm lost in a
   solid white disc, and the 05 star is a hard-edged sticker with a bright orange blur. Fix: cap the core at about 70 % area, keep a thin dark ring so the head
   and the shield stay legible at peak, give the burst real streaks and a radial lens flare (Frozen Synapse), cut the datamosh tear
   band to a narrow strip across the HOME only. Axes: V +0.5, S +0.5, Read +0.5.
9. **Fix the weak beats: 03 reveal, 06 aftermath, 07 CITY LOST.** 03: sealed corridors are thin pale lavender and the lock glyphs are
   tiny; make the fog a visible thick band with the lock silhouettes 1.5x. 06: the "DAMAGED" poster is a word on a sticker and the
   plate is empty; replace with a cracked HOME ring plus decayed ribbons and burn marks in place (Bad North fire), keep the poster as
   an optional beat. 07: the plum body is dark red with noisy hairlines and the skull plus datamosh stack three effects; pick one
   (flood with climb edge), thin the datamosh, and keep the skull but smaller. Axes: Wordless +1, Read +0.5, S +0.5.
10. **Fix the SITES LOST mark and tritan separation.** Beat: 02, 04, 06. Wrong: ochre-brown at night, hue-collapsed with E and DAMAGED. Fix: the
    ink-black plate with white rim and hatch described above, plus a distinct glyph per tier (not only ring pattern), then re-run
    deutan and tritan on all seven plates and require every tier distinct at 320 px greyscale. Axes: Read +0.5, Wordless +0.5.

Also: before Godot, add one real-time capture (any engine pass) of the HOME hit and the daemon to prove the Motion 9 claim on
pixels, not on a table; and re-state the Wordless test with a naive viewer, since the 8 here is a critic read, not a user read.
