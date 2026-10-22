# Tethys HQ, five basic idea blockouts (2026-10-21)

Each idea replaces the whole HQ (no hex centre, no shell). Same overview camera (golden plate t_over), water, caustics, whales, fish and background city; the dam is
cooled and dimmed (the abyssal v2 settings, unchanged). Jelly-bell buildings are no longer part of any HQ: they are the district's signature building type, 8 to 9 of them
standing on columns in the drowned quarter round the HQ. (A is the exception by premise: its HQ is one colossal bell.)

Files: `A_jelly_bloom.png`, `B_coral_spire.png`, `C_whale_fall.png`, `D_man_o_war.png`, `E_manta.png` (1280 x 720), `ideas_sheet.jpg` (current plate + the five, 2400 px),
`E_manta_motion.jpg` (three frames along the loop: wings up, level, down).

## E MANTA (priority)
A flying arcology gliding on a loop round the compound, parallel to the dam walls, banking into the turn (nose to screen-right, counter-clockwise from above).
- Ray: broad pointed swept wings (the wings are the decks, lit edge lines, a few warm window rows, faint spars), two long curled cephalic horns, a segmented mechanical tail curling down.
- Back: a low tower cluster along the spine and centre, with lit floor bands and one taller crown tower (the target). Four thruster pods under the trailing edge with photophore-teal glow.
- Water: a faint dashed loop line, a foam wake trailing behind along the loop, ripple rings (downwash) under the body, a cyan uplight on the belly.
- Underneath: the HQ lot is filled with a copy of a drowned-city patch (`fill_city.py`), and the station trench is removed, so there is no empty lot below the manta.
- Shadow: a soft-edged dark manta silhouette on the drowned roofs (`manta_post.py`). The water hides a real shadow, so it is a decal: the outline is projected through the plate
  camera, offset ahead of the manta along the key light, blurred and multiplied in; landmark pixels (object index 1) are left alone.

## Squint-test critiques
| Idea | Reads as | Critique |
|---|---|---|
| A jelly bloom | A jellyfish, at once | The bell is huge and clear, but the flat teal stripes read as a parasol; the shaft stilts are thin and the bell crowds the frame top. |
| B coral spire | Coral, then a tree | Branching staghorn on a reef mound reads; it is pale and small against the busy city, tips glow too evenly. |
| C whale fall | A skeleton | Ribs over a deck and a lit skull hall read from the arcade shape; the skull looks like a boxy fish head, and colonies are lost in the rib stripes. |
| D man o' war | A pink cap on a stalk | Weakest: the float reads as a jelly cap, the crest sail is too small and the chains below are thin and dark. |
| E manta | A manta ray first, a city second | Best silhouette: wings, head horns and tail in a few big shapes. Weak: the towers are small and low in contrast, the thrusters hide under the wing edge, the deck is plain, the shadow also darkens part of the causeway. |

## Numbers
CPU Cycles (no GPU lock), 1280 x 720, 16 to 20 spp, post = the base `post_city.aaa` at median 0.160 (0.1599 to 0.1601 on every frame). About 8 to 10 min per frame on the CPU
(build 20 to 40 s). The motion-strip frames are 8 spp.

## Rebuild
```
S=docs/concepts/hq_styles/tethys_ideas/scripts
# scratch needs D:/rc_scratch/hq_styles/tethys_abyssal/scr/{zoned_base.json,meridian_rail.json,mainframe_blade.png}
python $S/fill_city.py D:/rc_scratch/hq_styles/tethys_abyssal/scr/zoned_base.json D:/rc_scratch/hq_styles/tethys_ideas/zoned_fill.json 38
$S/run_idea.sh E E5 1.0 20                                   # A..E, tag, res_k, spp; E also writes the shadow and the _sh.png
FLAP=1.0 LOOP_PHI=-135 $S/run_idea.sh E Eup 1.0 8            # motion frames
FLAP=-1.0 LOOP_PHI=-45 $S/run_idea.sh E Edown 1.0 8
python $S/make_sheet.py
```
`ideas.py` holds the five builders (`ideas_build.py` patches the base build at run time through the abyssal wrapper); the nautilus-shell files in `../tethys_abyssal` are untouched and unused here.

## Researched or taken from the designer's reference
Gemini manta concept (via the designer): taken a low tower cluster on the spine, thruster pods with teal glow, a segmented tail, downwash ripple rings; not taken towers over the whole body,
airships and boats, pink sign spam, or the painterly finish.

## E MANTA v2 (detail pass, designer-approved, 2026-10-21)
`E_manta_v2.png` (1920 x 1080, Cycles GPU, 48 spp, median 0.160; render 423 s wall incl. build, FIFO lock wait 48 min, 15-min no-progress watchdog on our own Blender PID, never triggered)
and `E_manta_v1_v2.jpg` (v1 | v2). Builder: `idea_M` in `scripts/ideas.py` (run with `python scripts/run_final.py MF 1.5 48`).
What changed from v1:
1. Wings: a rounded convex leading edge to pointed tips, a concave trailing edge, tips drooping about 5 BU, a two-ring surface so the droop is smooth; banked into the turn.
   Head: two long horn-like curled cephalic lobes; tail: a segmented mechanical section then a slim whip with a glowing tip.
2. Arcology: stepped tiers (4 steps) plus eight smaller towers along the spine, floor bands and window lights, a crown tower with a warm top (the target), all inside the body.
   Wings: panel tones and a faint seam ring, running lights along the leading edge, spars, six landing pads.
3. Thrusters: four pods on the trailing edge angled outward, photophore teal, with a pale jet column down to the water and a teal spot on the water.
4. Water: soft irregular broken downwash ripples and spray round each thruster, two broad broken swells under the body, the foam wake along the loop, the dashed loop.
5. Shadow: the decal now also excludes everything below the projected dam crest and a strip along the causeway (`manta_post.py`, from the zoning file's dam line), so it stays on the drowned city.
6. Belly: a cyan spot from the water onto the underside (the camera sees almost none of it).
Populated drowned city, jelly district buildings, dam brightness and loop are as in v1.

### Squint critique of v2 (honest)
- Reads as a flying ray with horn lobes and a tail, and a city on its back: yes, but weaker than hoped. With the nose along the dam and the wings pointing up and down the screen, the planform
  squints as a crescent or leaf (a boat hull) more than a manta; the horns and tail carry the manta read, not the wings. A heading toward or away from the camera, or a more 3/4 pose on the loop,
  would give the classic wide chevron; this would break "parallel to the dam" for that frame.
- The tower cluster is lit and stepped but its tiers read as grey slabs at this size; the crown glow is the only strong accent.
- Thrusters read as grey cannon-like tubes at the trailing edge; their teal glow is mostly hidden under bloom, the jet columns are faint.
- The downwash ripples and spray are soft and natural but almost invisible at thumbnail; the shadow is the strongest water-level cue.
- The far wing is foreshortened to a thin sliver, which is part of why it reads as a crescent.

## E MANTA v3 (Hawaiian detail pass, designer-approved, 2026-10-21)
`E_manta_v3.png` (1920 x 1080, Cycles **CPU**, 32 spp, OIDN, median 0.160, 24 min) and `E_manta_v2_v3.jpg` (v2 | v3). Builder: `idea_N` in `scripts/ideas.py` (`IDEA=N`).
**Why CPU, not the 48 spp GPU final:** I held the FIFO lock twice (gpu_lock helper, 15-min no-progress watchdog on my own PID) and both times the v3 scene made the HIP render stall: nothing past
"WATER calm" in the log after 15 min, so the watchdog killed only my Blender PID (PIDs 8812 and 18348) and the lock was released each time (about 18 and 16 min held). The v2 manta scene rendered fine on
the same GPU in 423 s, and the v3 scene renders on the CPU, so the cause is something new in v3 (probably the few thousand tiny emissive algae polygons, the gable-end emissive faces or the
extra landmark light beams, 46 vs 37). Not diagnosed further. A GPU re-render needs that scene trimmed first (e.g. fewer algae patches).

What changed from v2:
1. Planform and pose, read top-down: broad flat wings (half span 52, span about 2.2 x body), bank 10 degrees (tan 10 deg across the span), no droop, a rounded leading edge to pointed tips.
2. Cephalic lobes: short paddles either side of the mouth, about 7 BU on a 47 BU body (about 1/7; real lobes are about 14 % of disc width from tip to mouth, curled forward and rolled).
3. Colour: a pale desaturated Tethys teal-blue skin (albedo about 0.40, 0.56, 0.64), a continuous neon outline in the photophore teal (#7CF2E4) round wings, lobes and a neon centre line along the tail.
4. Tail: long (about 1.3 x body), mostly straight with one gentle C (5 BU sideways bulge), a segmented mechanical root, then a slim whip.
5. White kakau-style skin: a row of niho mano (shark tooth) triangles along each leading edge with a base band, a second band following the wing curve, a solid tip triangle, four lozenges per wing,
   three nested forward chevrons on the rear body. Generic geometric vocabulary only, mirrored left and right, a few bold shapes.
6. Arcology: three stepped dark heiau terraces with lit lips and window dots, one crown hale (steep thatched roof, glowing open interior, lit ridge and gables) on the top tier, four hale on the
   middle tier, four on the lowest, small lit lauhala-style hatch screens; low and inside the body outline.
7. Thrusters: four trailing-edge pods angled out, pale body, teal glow at moderate strength (1.6, not the earlier 2 to 3).
8. Water: patchy teal-cyan algae glow (small irregular polygons, about half of them just under the surface, with a few sparkle dots), clustered under the body, round the thrusters and along the wake; no rings.
Everything else (populated drowned city, jelly district, dam, loop, shadow decal masked off the dam and causeway) as v2.

### Squint critique of v3
- Reads as a manta first: yes. The broad pale wings, neon outline, white tooth rows, short lobes and the long straight tail say ray at once, and the shadow on the city says "something huge passes over".
- The Hawaiian city on its back is the weakest part: at this size the three terraces and hale read as a stack of sandy blocks; the steep gables and the lit interiors of the hale are hardly legible, and the
  warm stack is the only warm object, so it also pulls the eye more than the manta's own teal. A taller crown hale and a darker, more clearly pitched roof would help.
- The white skin pattern reads at thumbnail (teeth along the leading edge, lozenges); the chevrons on the rear body are lost under the tail root.
- Thrusters read as pale tubes with a small teal tip; the glow is visible but small.
- The algae glow reads as sparkle and small pale discs; patchy, but it can look like debris on the water more than a living glow. The soft diffuse haze I wanted is missing.
- The first lobe curl is not visible at this scale; they read as small flaps, which is the anatomy but not much of a feature.

### References (pages read only; nothing downloaded or copied)
- Kakau (traditional Hawaiian tattoo): generic web summaries (niho mano shark teeth for protection and strength, often used as rows and borders; enata human figures; kakau as a record of lineage): searched
  2026-10-21; the pages were secondary and partly low quality, so only the broad vocabulary (tooth rows as borders, solid bands, mirrored geometric fields) is used; v4 may draw on real kakau directly (designer ruling below).
  Polynesian manta tattoo pages (tattootribes.com entries, general tattoo guides): mirrored wing fields, lines and geometric fills; manta as protection and voyaging. Designer ruling (Native Hawaiian, 2026-10-21): the cultural concerns are waived for this concept art and real kakau and Hawaiian references may be used directly.
- Hale and hale pili: https://en.wikipedia.org/wiki/Hale_(architecture) and the Hawaii Public Radio piece on master builder Francis Palani Sinenci: post-and-beam, thatch of pili grass or lauhala, a ridgepole with layered braided ridge thatch,
  raised floors and open walls for air; taken the steep gable, the open lit interior, the ridge line.
- Heiau: https://en.wikipedia.org/wiki/Heiau: stacked lava rock platforms and terraces, some tiered, structures standing on the platforms; taken the stepped dark stone base tiers carrying hale.
- Hawaiian Regional architecture (Charles Dickey, Vladimir Ossipoff; Hawaii Home magazine and SAH pages): steep or double-pitched roof modelled on hale with deep eaves, lanai and breezeways, coral-stone columns; taken the deep roof
  overhang, the lit lanai terrace lips.
- Manta anatomy (Florida Museum species profile, Georgia Aquarium, UCT news on cephalic lobes): lobes about 14 % of disc width, paddle-like, rolled forward when not feeding; taken the short paddle size and the forward curl.


## E MANTA v4 (hale-biodome compound, designer-approved, 2026-10-21)
`E_manta_v4.png` (1920 x 1080, Cycles **GPU**, 48 spp, median 0.160; Blender 301 s wall incl. build, 324 s with post; FIFO lock wait 24 min; the 15-min watchdog did not fire) and `E_manta_v3_v4.jpg`.
The v3 GPU stall did not recur: v3's several thousand separate emissive algae polygons were the cause (v4 has none). Builder: `idea_P` in `scripts/ideas.py` (`IDEA=P`, `scripts/run_final.py`).
Cultural note from the designer, who is Native Hawaiian: the cultural concerns are waived for this concept art; real kakau and Hawaiian references may be used directly.
What changed from v3:
1. A compound of nine hale-biodomes on the back and wings (one hero, a tall gabled A-frame hale-biodome on two lava-stone heiau tiers; two hip-roof hale; five gabled hale, two of them across the wings; one small hip hale far out on a wing),
   joined by walkways with lit edges and lanai decks. Each is a steep hale roof rebuilt as a glass gridshell (clear glass slopes and gables, bronze rafters with a diagonal kapa/lauhala-style lattice and purlins, a lit ridge and eaves),
   a warm glowing interior with tropical planting (palm-like fans) and a stone plinth with a lit lip. Buildings may cover the far wing.
2. Rounded wing tips (a half-ellipse cap); the cephalic lobes are part of the head outline (they flow out of the head, no separate pieces).
3. Two thrusters only, integrated at the tail root: a low cowl on the back, a glowing teal slot on the trailing edge, a faint jet column to the water. No pipes.
4. Kakau across the whole back, drawn as a soft white glow so it reads on the pale skin: niho mano teeth on the leading edge, three bands following the wing curve, zig-zag teeth and lozenge fields between them, trailing chevrons, tip triangles, a dorsal lozenge chain.
5. Algae: one emissive texture in the water surface material (a baked haze field: soft teal cloud under the body, round the thrusters and along the wake), six swirls and 22 sparkles in the wake, about 150 small objects in total.
Kept: colour, neon outline, straight-C tail, shadow and dam mask, loop, drowned city, jelly district.

### Squint critique of v4
- Manta first, hale city second: yes. The pale wings, neon edge, white kakau, rounded tips and the long tail read as a ray at once; the cluster of steep gabled roofs reads as a roofed village on its back, with the hero spire clear.
- The glass and bronze lattice reads at full size, but at thumbnail the roofs read as warm tan peaks; the glass transparency and the planting are not visible below about 1000 px.
- The compound sits on the head and body and hides much of the far wing; the manta's near wing still carries the silhouette, as intended.
- The haze is soft and reads as a living glow, but it is faint and mostly a cloud left of the body; the wake swirls are hard to see.
- The thrusters are barely visible at the tail root (the slots are hidden under the compound shadow and the haze).
- Walkways and lanai decks are too small to read; the compound reads as nine roofs, not as a connected village.
