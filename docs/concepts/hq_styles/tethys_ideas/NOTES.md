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
