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
