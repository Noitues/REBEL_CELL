# HQ netrun set piece, round 2 (art/hq-netrun, commit 8cba0b88)
Composition kept (helix on the avenue axis, path leading in, 140 BU hero camera). Files: hero.png, alt_gate/high/far.png, alt_helix_closeup.png, fly_in/ + fly_in_strip.jpg, plate_vs_hero_r2.jpg, r1_vs_r2.jpg, squints/, logs/.

## Changes
1. Towers are REAL city buildings now. `CityHqNet._tower()` collects prisms (same dictionary schema as the model); `_city_mesh()` builds the city's own family MultiMeshes (CityMeshKit.families_of / instance_buffer / family_mesh) on the view's building material. So the flanking towers, slabs, backdrop towers, plaza arcade and the flank shop blocks have the city's ink, grain, cel bands, window patterns, roof trim and the zoom-rule facade layers, identical to the round-6 street. Slabs use the Solace kits (capsule / cell / clinic) on every second tower, the rest `rebel_cell` plain / setback shapes (flat prisms; `taper` 1.0 = full top, 0.0 gave pyramids). My flat window grids are gone; lit signs, shop bands, outlines and roof clutter remain as quads on top.
2. Helix: pods are lime (the office role) with pink accents (the window role), thicker lime / pink halo, lime rays across the plaza, a lime wash down the avenue.
3. Light distribution: plaza arcade (15 blocks on an arc behind the helix, sign tier at 11-18 BU, amber band, blade signs), a neon spill band behind the plaza (16 faded bays, additive), sign tiers on the far flank blocks, a second sign tier and a vertical lit sign on every slab, brighter gate bars. Foreground calmed: shop bands, pools and node pools fall off with distance to the camera (`fk`), near node column dimmer.
4. Reflections: no street mirror on the avenue (the ZoomRoad mirror is for real street lots); streak fake kept and extended: a lime glow column on the road under the helix with a lime and a pink strand glint, and wide lime / pink smears under the gate.
5. `tests/test_manifest.json` has `test_city_hq_net.gd`.

## Squint (1/16 + blur; mean, p95, loud > 0.38, brightest 24 px row)
| image | mean | p95 | loud | brightest row |
|---|---|---|---|---|
| HQ plate | 0.242 | 0.617 | 0.223 | 54 % (0.639) |
| round 1 hero | 0.217 | 0.602 | 0.144 | 83 % (0.349) |
| **round 2 hero** | **0.222** | **0.592** | **0.174** | **59 % (0.388)** |
| alt_gate | 0.247 | 0.659 | 0.210 | 55 % |
| alt_high | 0.200 | 0.512 | 0.109 | 72 % |
| alt_far | 0.140 | 0.352 | 0.041 | 64 % |
Targets: brightest row 50-65 % met (59 %); loud 0.18-0.22 just under (0.174; alt_gate 0.210); mean about 0.24 under (0.222). Upper frame (25-60 %) 0.219 (r1 0.206, plate 0.393). Row bands in logs/rows24.txt: hero peaks at rows 11-13 (0.30-0.35), the plate at 0.40-0.51.

## Checks
- City band zoom rules on vs off: 0 differing pixels; street stage 5 vs round 6 `street_frame.png`: 0 pixels.
- Targeted tests (round-6 nine + test_city_hq_net.gd): 144 tests, 0 failing, 8 pending.
- HQ-band gpu_city p95 (500 frames, limit 12.57), first three runs: **10.60, 13.73, 4.74**; three more: 4.57, 10.96, 14.46. Two of six are over, both with p99 20-33 ms, max 37 ms and means near 4 ms (spike runs, same pattern as round 6's 14.02 / 12.65; not proven to be other GPU load). The remaining four are 4.6-11.0. Round 1 was 10.89 / 11.90 / 11.98.

## Gaps
- The mid-frame band is partly an additive spill fake (16 bays) over the arcade; the plate's is a real bright storefront strip. The plate's upper frame is still twice as bright (wall-to-wall lit towers).
- Real towers show the zoom-rule facade lighting, which is sparse at 140 BU; the upper frame lift came from signs, not windows.
- No true mirror of the helix on the road; the smear is a fake and shows no strand detail.
- The two perf outlier runs (above).
- Slip-free: no `python -`.
