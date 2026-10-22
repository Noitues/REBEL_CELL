# Meridian as a Mughal freight palace (concept, 2026-10-21)

Exploratory single-HQ concept; the castle gatehouse is retired. Nothing in the base pipeline was edited: `scripts/mg_run_hq.py` patches
`hq_meridian_v3` at run time (`mg_blender_hq.py` hook -> `mg_restyle_v2.py`; v1 is `mg_restyle.py`). The castle objects (walls, towers, gantry,
rooms, yard containers) are cut out of the scene inside |x|,|y| < 124 and the compound is rebuilt: the city, ring road, trucks, rail line and sky
beam stay.

## Outputs
- `meridian_mughal_v2.png` (1920x1080, Cycles HIP, 34 spp), `meridian_mughal_v1_v2.jpg` (left: v1 CPU look-dev preview 1280x720 8 spp, because the
  v1 GPU final was cancelled in the queue to spend the slot on v2; right: v2 final).
- (v1 as first designed: a palace dropped into the yard, 4 minarets. v2 = the designer's notes: the whole compound is one ensemble.)

## v2 design
- Main building toward the centre, slightly off-centre toward the back (mausoleum at (0, 16); compound centre (0, 0)): square-chamfered white marble
  block, pishtaq (rectangular frame + pointed-arch iwan, backlit orange jali with dark lattice bars, hot-red arch outline, barcode band) on all four
  faces, drum, onion dome (R 20.5, H 50, brightest object), gilded finial with a lit crescent, four corner chhatris, on a red-sandstone plinth with a row of
  backlit pointed-arch cells.
- Eight crane-minarets: four on the plinth corners, four taller / stouter at the outer corners of the wall (H 112, base r 5.4). Each is a three-section
  tapering minaret with balconies, orange inlay rings, a top chhatri, a mast, lattice jib with counter-boom and a trolley hanging an orange-lit container.
  Outer jibs point outward over the ring road, inner jibs point sideways, so no jib crosses the dome.
- One walled charbagh: water axis (pool 24 wide) from the iwan gate to the plinth, cross channel and square basin; south garden is four container parterres
  (concentric rings of stacked containers, 3 / 2 / 1 high), two flank parterres beside the plinth, a rear freight canal with barges and two rear parterres.
  Barges with containers sit on the axis and on the canals. White marble coping, barcode (shipping-mark) inlay bands along the pool and round the terrace.
- Walls: pointed-arch backlit niches on the S and W faces, chhatri kiosks every ~30-50 units, small pishtaqs at the middle of the W / E / N walls.
- Iwan gate (Buland Darwaza idea) at the S wall for the trucks: two piers, pointed arch, backlit orange jali wall, tiers of small niches, barcode frieze,
  chhatri crown; the existing truck ring road and queues stay in front of it.
- City: dark blue-steel facades, cool windows and cool fog; uplights (white) on the dome, small spots on the minarets, orange gate wash.

## Critique (each output viewed before moving on)
- v1 m1: reads as the Taj instantly (dome, minarets with jibs) but the water was black, the yard was loud red/orange stripes that fought the dome, the jibs were thin. Fixed
  (water metallic + cool glow, calmer containers, thicker jibs, orange hanging containers).
- v1 m3/m4: water now a blue ribbon but the yard went dark and flat; flank land beside the plinth was empty. Fixed (flank parterres, mid-tone steel containers).
- v1 m5: yard too bright, competing with the dome. m6: hierarchy right (dome > yard > city). v1 critique that remains: canal still thin, the compound is a palace
  sitting in the yard, not an ensemble (hence v2).
- v2a: eight minarets read but two dark jibs crossed the dome base; dome small and hazy. v2b: dome enlarged, water widened. v2c/v2d: jibs re-aimed so none crosses
  the dome (outer jibs outward).
- v2 final (squint test): dome, 8 crane-minarets, quartered garden, iwan gate with the truck queue, and the walled ensemble all read at thumbnail size; the dome
  is the brightest element. Remaining faults: the water axis is only a pale-blue ribbon between the parterres (it needs a stronger dome reflection); one thin dark
  jib still overlaps the left of the dome and the front outer jib foreshortens into a vertical pole; the final's city windows are busier and brighter than the
  8 spp previews, so the city is "dark" but not as dark as it could be; the barcode / jali inlay is mostly lost below ~1000 px (fine at full size only on the
  pishtaqs and the gate); the target (keep) inside the dome is not visible.

## Timings and values (RX 6700 XT, HIP, 1920x1080)
v2 final: 34 spp, Blender 433 s (498 s with post), median (luma) 0.165. The first v1 attempt at 52 spp passed 20 minutes and was stopped (own PID) per the GPU
protocol; v1 and v2 then ran at 34 spp. About 100 min were spent waiting for the shared GPU lock. CPU look-dev previews: 1280x720, 8 spp, 150-290 s each
(m1-m6, v2a-v2d).

## Rebuild
```
S=docs/concepts/hq_styles/meridian_mughal/scripts
cd D:/rc_scratch/hq_styles/meridian_mughal
MG_RESTYLE=mg_restyle_v2 bash $S/prev.sh <tag> haze_abs=0.0013      # CPU preview, no GPU lock
touch USE_V2; SL_SPP=34 python $S/mg_gpu.py art_mughal_final gpu.log -- python $S/mg_run_hq.py art final haze_abs=0.0013
python $S/mg_sbs.py       # writes the v2 png and the v1/v2 sheet here
```
Scratch: `D:/rc_scratch/hq_styles/meridian_mughal/`.

## References (pages read only; nothing downloaded or copied)
| Source | Trait taken |
|---|---|
| [Taj Mahal](https://en.wikipedia.org/wiki/Taj_Mahal) | Chamfered square mausoleum with identical faces on a plinth; pishtaq (framed pointed-arch iwan) with stacked flank niches; drum and onion dome with gilded finial and crescent; four corner chhatris; four three-section minarets with balconies at the joints and a chhatri on top; reflecting pool on the axis; charbagh quartered by walkways; white marble with dark inlay (-> barcodes) |
| [Humayun's Tomb](https://en.wikipedia.org/wiki/Humayun%27s_Tomb) | Red-sandstone plinth with arcaded cells under white marble; charbagh with central water channels; gateways |
| [Buland Darwaza](https://en.wikipedia.org/wiki/Buland_Darwaza) | Monumental gate: huge central arch in a stepped facade, tiers of small arches, a skyline of chhatris -> the truck iwan |
| [Jali](https://en.wikipedia.org/wiki/Jali) | Pierced screens with holes about as wide as the stone is thick -> dark lattice bars over an orange emissive panel |
| [Charbagh](https://en.wikipedia.org/wiki/Charbagh) | Four quarters divided by axial waterways meeting at a central basin -> four container parterres and a square basin |
| [Pietra dura](https://en.wikipedia.org/wiki/Pietra_dura) | Cut-stone inlay in marble -> shipping-mark barcode bands |
| Port ship-to-shore cranes (general knowledge; the Wikipedia page 404'd) | Boom, trolley and spreader hanging a container on cables -> jib, counter-boom, trolley and hanging container on each minaret |

## v3 (designer notes on v2): `meridian_mughal_v3.png`, `meridian_mughal_v2_v3.jpg`
Script `scripts/mg_restyle_v3.py` (v2 stays as the base; run with `MG_RESTYLE=mg_restyle_v3`, composite with `scripts/mg_sbs3.py`).
- Dome: emission 0.60 -> 0.12 (more than one stop down), marble emission 0.05 -> 0.03, white uplights 140k -> 40k W, and every added light is invisible to volume
  scatter (no fog halo from them). A shadow-casting key spot from the camera side (SW, high, 2.8 MW, soft size 8) models the onion, drum, pishtaq arches and chhatris.
- Water removed (axis, cross channel, basin, rear canal, barges). Main axis is a paved walkway (white runner, two orange lines); the cross axis and the rear strip are
  container-rail strips (dark bed, chrome rails, sleepers, flatcars with stacked containers, lit edges); the crossing is a paved square with an eight-point star inlay and
  a fountain disc. The four south quarters, two flank quarters and two rear quarters are unchanged.
- Cranes untouched (including the jib that crosses the dome). City: window emission x0.35, facade albedo and band glow lowered; nothing else done there; haze 0.0013 -> 0.0009.

Critique (viewed): v3a (dome emit 0.30, key 1.5 MW): form appears, but the whole frame went hazy (exposure rose because the dome was dimmer) and a halo remained. v3b (haze
0.0009): veil lighter, halo still visible. v3c (emit 0.12, key 2.8 MW): drum, pishtaq and chhatri shading read, halo mostly gone. v3 final (squint test): the dome is still the
brightest element and now reads as an onion form, not a white blob; 8 crane-minarets, the quartered garden (rail strips and the walkway make the cross read clearly), the gate and
the trucks read at thumbnail size; the city is darker and quieter than v2. Remaining faults: the city at full size still has many red dots and lit windows (brighter in the 40 spp final than in the 8 spp previews); a soft glow
remains round the dome and the gate (post bloom on orange emitters); the rail strips read as grey stripes with scattered coloured boxes rather than obviously as rail; the key light
makes shadows of the minarets fall on the terrace, which is correct but slightly dirty; the target inside the dome is still not visible.

Timings v3 final: 40 spp, 402 s Blender (513 s with post), median 0.157 luma. Waited about 120 min for the GPU lock (FIFO). CPU previews v3a-v3c 170-200 s each.
Rebuild: `MG_RESTYLE=mg_restyle_v3 SL_SPP=40 python $S/mg_gpu.py art_mughal_v3 gpu.log -- python $S/mg_run_hq.py art final3 haze_abs=0.0009`.

## v4 (haze and contrast pass on v3): `meridian_mughal_v4.png`, `meridian_mughal_v3_v4.jpg`
Script `scripts/mg_restyle_v4.py` (run with `MG_RESTYLE=mg_restyle_v4`; composite `scripts/mg_sbs4.py`). `mg_gpu.py` now has a watchdog: it kills only its own child tree
(`taskkill /PID <pid> /T`) if nothing under the scratch folder changes for 15 minutes. The runner's target median default is now 0.14.
- Haze: scene haze 0.0013 -> 0.0007; the base scene's glow lights near the compound (`bankglow`, gate, ring, quay, rail, wash, rim, corp group within 200 units) are invisible to volume
  scatter and the bank glows are x0.2; all added lights were already invisible to volume. Post: bloom (0.12, 0.10, 0.08) -> (0.05, 0.04, 0.03), halo from the volume pass x0.4 (0.8 -> 0.3), chromatic
  aberration 2.4 -> 1.2, contrast 1.12 -> 1.10, exposure solved to median 0.14 (not 0.16), so the marble is not lifted to a blown white.
- Contrast: marble emission 0 (dome 0.04), uplights 12 kW, garden fill 50 kW, key spot 2.0 MW neutral white and tighter (soft size 3, blend 0.25), so the shadow side of the dome, drum and
  terrace falls away and the lit side stays white. Orange emitters cut (7 -> 4, red 6 -> 4.5) so the jali glow stays at its openings.
- Rail: dark ballast, light concrete sleepers across, twin chrome rails 1.2 wide with a white highlight, flatcars with bogies and chrome wheels, 40 ft containers with corrugation ribs on both long
  sides and chrome door bars, 60% of the slots filled so the track shows in the gaps.
- City: win_boost 0.9 -> 0.55 only to cancel the extra exposure (lower fog and the contrast pass made it read brighter at equal settings); otherwise as v3.

Critique (viewed): v4a (key 4.5 MW, haze 0.0005): dome blown out and yellow, city brighter than v3. v4b (key 2.8 MW, orange emitters down, haze 0.0007): crisper, rails still invisible. v4c/v4d (target median 0.14,
key 2.0 MW, light sleepers on dark ballast): dome now has a lit side and a shadow side; haze reduced. v4e (60% flatcars): same. v4 final (squint test): dome, 8 crane-minarets, gate, trucks and the quartered garden
read; the dome is the brightest object and reads as an onion form; haze and orange fog over the compound and round the gate are gone. Faults: the rails still do not read as rail at thumbnail size (the container ring
parterres around them are as strong as the rail flatcars, and the track is 4 px wide); the city in the final is a little busier than v3 (lower fog shows more of it); the dome's shadow side is a soft gradient rather than a hard
terminator (area light spread through the fog-free scene); the orange glow that remains is bloom on the gate arch and the wall niches (kept tight but visible).

Timings v4 final: 40 spp, Blender 170 s (242 s with post), median 0.145 luma. About 27 min waiting for the lock (FIFO). CPU previews at 1280, 1600 and 1920 wide, 6-8 spp, 180-270 s each.
Rebuild: `MG_RESTYLE=mg_restyle_v4 SL_SPP=40 python $S/mg_gpu.py art_mughal_v4 gpu.log -- python $S/mg_run_hq.py art final4 haze_abs=0.0007 'post={"bloom":[0.05,0.04,0.03],"vol_glow":0.3,"ca":1.2,"contrast":1.1,"shadow_tint":[0.46,0.50,0.58],"sat":0.92}'`.

## v5 (designer notes on v4): `meridian_mughal_v5.png`, `meridian_mughal_v4_v5.jpg`
Script `scripts/mg_restyle_v5.py` (`MG_RESTYLE=mg_restyle_v5`; composite `scripts/mg_sbs5.py`). `mg_blender_hq.py` now writes a persistent render heartbeat (`heartbeat.txt`, from the Cycles stats handler) so the
`mg_gpu.py` watchdog (kills only its own child tree after 15 min without file changes) can see progress during a render; the first v5 attempt was killed by the watchdog at 977 s because a render writes no files until it ends.
- Streets instead of rails: both cross-axis halves and the rear strip are paved streets (dark asphalt, white kerbs, dashed centre line, two lanes) carrying 16 container trucks (white cab with windscreen and headlamps, chassis, bogies with
  tyres, trailer with a 40 ft weathered container, tail lamps). The cross street is 20 wide; the parterre stacks beside it are one level lower (2 / 1 / 1) so the street is not hidden behind them from the overview camera.
- Gate: all orange bloom and glow removed from the gate arch, its tier niches and the wall; they are now warm-white openings at emission 0.45 (below the bloom threshold) and the old orange gate area light is a weak neutral one;
  a neutral-white spot from the camera side lights the gate front. The arch outline neon is a marble moulding.
- Perimeter wall: raised 11 -> 24 and clad in white marble; a two-storey arcade of framed pointed-arch lit openings (6 unit pitch) runs round all four outer faces (gate and mid-wall pishtaq bays skipped), with a string course
  between the storeys and a plinth band. Kiosks sit on the raised coping; the mid-wall pishtaqs are 32 high.
- White: marble albedo 0.92 neutral, wall, plinth base (was red sandstone), minarets and mausoleum all marble; key, uplight and minaret lights neutral white; post highlight tint neutral, saturation 0.85. Jali glow on the pishtaqs is a dimmer own
  material (emission 2.2).
- Containers: four saturated hues (mustard yellow, orange, cobalt blue, oxide red), each pick differs from the previous one and from the one below; rust streaks on the two camera-facing faces and a rusty foot.

Critique (viewed): v5a: walls and building clearly white, arcade and colours read, but the streets were not visible: the 15-high parterre stacks beside the cross street hid it from the camera, and the gate was a black box.
v5b: stacks lowered and the street widened, gate lit; the street shows as a dark strip. v5c/v5d: more and brighter trucks, lighter asphalt, stronger gate light. v5 final (squint test): the dome, 8 crane-minarets, white walled ensemble with its
two-storey arcade, the quartered garden and the mixed colours all read; containers no longer blend with the white. Faults: the trucks inside the compound read as long rows of coloured boxes with small white cabs, not clearly as trucks,
because the front wall (24 high) and parterre stacks hide most of the street from this camera and the cabs are about 14 px; the gate arch still has a soft white glow from the front spot and its own openings; the arcade openings read as glowing
cream windows (as asked) but make the wall the second-brightest element after the dome; rust is visible only as dark streaks at 1920 px; the city is as in v4.

Timings v5 final: 36 spp, Blender 1811 s (1882 s with post) because other agents' windowed Godot captures were sharing the GPU (the same scene is about 3 minutes on a free GPU); median 0.145 luma. About 25 min waiting for the lock (FIFO).
Rebuild: `MG_RESTYLE=mg_restyle_v5 SL_SPP=36 python $S/mg_gpu.py art_mughal_v5 gpu.log -- python $S/mg_run_hq.py art final5 haze_abs=0.0007 'post={"bloom":[0.05,0.04,0.03],"vol_glow":0.3,"ca":1.2,"contrast":1.1,"shadow_tint":[0.46,0.50,0.58],"sat":0.85,"hi_tint":[1.0,1.0,1.0]}'`.
