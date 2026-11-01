# HQ netrun set piece (Solace), overnight round 1
Godot worktree `D:/rc_art/godot_look_hqnet`, branch `art/hq-netrun`, from `22979681` (round-6 street). Commits `e607e6ac`, `837124d2` (the last one is the final state; hash in the report). Art only (REBEL_CELL, Solace slice).

## What it is
`CityHqNet` (`scripts/city3d/city_hq_net.gd`), a Node3D that `CityView3D.set_hq_netrun(true)` adds when `CityConfig.hq_on` (OFF by default). The set piece is hand-authored in layout space (u from the helix toward the camera, v across), in the REAL city: the live seed-7 model, the real Solace park, skyline and highways stay; the lots under the avenue and the plaza are cleared, the landmark helix and the stand-in tower are hidden, the Solace park mesh loses the triangles under the avenue.
Authored: the v5 helix glb in cel tones (own shader `city_hq_helix.gdshader`: three flat tones by a fixed key light, glow rim, written as emission with the neon class tag), a lime / pink halo over the top, the plaza (rings, ticks, bollards), the avenue (dark wet road, lime edge lines, pink dashes, cyan lane dashes, lamp row with warm pools and wet streaks, a security gate with a board), the flanking storefront row (shop band, fascia, window rows, blade signs, roof clutter, roof boards), five lit slabs per side with outlines and window grids, six backdrop towers behind the helix (the real skyline stands beyond them), lime / cyan sky beams from the slabs, and the node path.
Node path (six nodes, all on ground floors the camera sees; types and colours are placeholders): street cabinet (cyan), kiosk (amber), relay mast (pink), storefront (magenta), data-hall entrance (white-lime), server on the plinth (lime). A pink ribbon with chevrons joins them, the next node is larger with a taller column.
The look is the city cel look zoomed in: the zoom rules (street look, sky, fog, far-tower plum rule, near-black grade point) are on, the staged street widening is off (`CityZoomStage.active` is false while `hq_on`).
Config: `hq_*` group at the end of `city_config.gd` (hq_on, axis, lengths, camera `hq_cam_d` / `hq_eye_bu` / `hq_fov` / `hq_horizon` / `hq_focus_bu` / `hq_pitch`, gains `hq_lime_gain` `hq_pink_gain` `hq_window_k` `hq_helix_glow` `hq_pool_k` `hq_streak_k` `hq_beam_k` `hq_road_k`, `hq_slabs`, `hq_helix_scale`, `hq_hide_hwy`).

## Frames (this folder)
- `hero.png`: eye 20 BU over the ground, 140 BU from the helix on the avenue axis, 56 deg vertical fov, horizon 0.58; focus 36 BU ahead, focus ppb 28.2 (street look range).
- `alt_gate.png` (street level on the avenue, eye 3.5), `alt_high.png` (aerial, eye 58), `alt_far.png` (235 BU out, 40 BU up; shows the real highways and towers), `alt_helix_closeup.png`.
- `fly_in/` and `fly_in_strip.jpg`: 8 frames for T11 (raid view to HQ netrun): t 0 is the raid view's iso plan over the HQ (focus ppb 6.4), the zoom's dolly to an aerial approach on the avenue axis (t 0..0.45), then a glide down the axis to the hero camera with fov, horizon, aim and a log-space focus distance easing (focus ppb 6.0 to 28.2, so the zoom rules fade the city look into the netrun look). t 1 is exactly the hero camera. The strip shows the helix glowing in the real city in frames 1 to 6 and the netrun look settling in frames 7 to 8.
- `plate_vs_hero.jpg` (plate and hero, and their squints), `squints/`, `plan_overview.png` (top view, zoom rules off: the avenue through the real Solace park, highways crossing it).
- `logs/`: `squint_stats.txt`, `rows24.txt`, `perf1-3.log`, `targeted_tests.log`, `city_band_on_vs_off.txt`, `street_stage5_vs_round6.txt`, `capture_*.log`, `probe_hq_location.log`. `scripts/`: the capture tool (`hq_net.gd/.sh`, lock wrapper), `squint_stats.py`, `rows24.py`, `plate_vs.py`, `strip.py`, `crop.py`, `px.py`.

## Squint numbers (1/16 BOX + blur 0.6; mean, p95, share above 0.38, brightest 24 px row of the full frame)
| image | mean | p95 | loud > 0.38 | brightest row | upper 25-60 % mean |
|---|---|---|---|---|---|
| HQ plate (hq_rebel_cell_overview) | 0.242 | 0.617 | 0.223 | y 587 (54 %) val 0.639 | 0.393 |
| street plate | 0.203 | 0.483 | 0.123 | 73 % | 0.173 |
| concept frame4_solace_hq | 0.218 | 0.496 | 0.105 | 73 % | 0.241 |
| **hero** | **0.217** | **0.602** | **0.144** | y 900 (83 %) val 0.349 | 0.206 |
| alt_gate | 0.246 | 0.694 | 0.184 | 65 % | 0.239 |
| alt_high | 0.177 | 0.410 | 0.058 | 72 % | 0.193 |
| alt_far | 0.131 | 0.288 | 0.026 | 52 % | 0.148 |
Hero against the HQ plate: mean 90 %, p95 98 %, loud share 65 %. Not matched: the loud share and the brightest row. The plate's light is one wide, very bright band at mid-frame (the storefront strip, 0.40-0.51 for rows 8-11 of 20) over a dark base; mine rises toward the bottom (the near flank blocks and lamp pools, rows 15-18 at 0.29-0.34) and has no band at mid-frame. The upper frame is half the plate's (0.21 vs 0.39: the plate has lit towers wall to wall; mine has sky, beams and the dim real skyline). alt_gate, a street-level frame, is closer to the plate on mean / p95 / loud (0.246 / 0.694 / 0.184).

## Checks
- City band, zoom rules on vs off, stage 1 (`nr_zoom --zr --target --stages=1 --layers=both --freeze`): **0 differing pixels** with the HQ code in (`hq_on` off). Also the street netrun stage 5 frame is **bit-identical (0 px) to round 6's `street_frame.png`**.
- Targeted tests, the round-6 nine scripts (zoom layers / r2 / rules / stage, neon kit, shaders, city3d model, city motion; the shader render test rides in `test_city_shaders`) plus the new `test_city_hq_net.gd` (7 tests: off by default, street staging gives way only when on, numbers, look-camera projection, lens-shift horizon, helix shader is emission-only, hash determinism): **144 tests, 0 failing, 8 pending** (round 6: 137). Never the full suite. `test_city_hq_net.gd` is not in `tests/test_manifest.json` (a run warning only).
- HQ-band perf (`hq_net --hq --perf --frames=500 --poses=hero --live`, motion on, GPU lock), gpu_city p95, limit 12.57 ms: **10.89, 11.90, 11.98 ms** (a 4th early run 11.14). Spread 1.09 ms. Means 6.07 / 7.19 / 4.51 ms and p50 5.06 / 9.11 / 3.07 (the GPU clock steps between two states in a run; the p95 is the upper state). p99 11.45 / 12.09 / 14.89, max up to 34 ms in run 3 (a spike outlier). Wall p95 about 20 ms (window shared with the tool).

## Choices (the designer is asleep; made and logged)
1. **Helix scale 1.0** (as exported, 88 BU) and the camera at 140 BU on the avenue axis from the north. Considered scaling the helix to 1.2-1.3 for the hero; it then clipped the top of the frame, so the camera sits where the hero fits with the halo.
2. **Camera 140 BU out (not 200)**, because two real elevated highways cross the avenue axis at about 145-175 BU from the helix and sat across the hero frame. The camera stands between the helix and the highways; they show in `alt_far` (real city). Hiding them is not possible per piece (they are in the global `Roads` mesh); `hq_hide_hwy` exists but only hides flyover / pillar meshes that are not the deck, so it is off.
3. **Eye 20 BU up, looking slightly down**: a rooftop-level street view, so the flank rows read as roofs and fronts at once (closer to the plate's 3/4 view than a pavement eye). `alt_gate` is the pavement-level version.
4. **Real city kept**: skyline, Solace park, highways, sea all live. Authored additions behind the helix are six backdrop towers (50-100 BU) so the frame is not empty sky; the real skyline shows between them. Logged as staging.
5. **Avenue axis north** (`hq_axis` (0,-1)): the sea is behind the camera, the dense city lies behind the helix (S ray: towers 26-40 BU at 50-200 BU). Axis-aligned so the cleared rect is exact.
6. **Pink allowed where it serves**: path ribbon, halo, lane dashes and slab outlines are pink; lime stays the corp colour (helix, gate, edge lines, beams).
7. Solace lime is a green lime (0.40, 1.0, 0.14); the earlier yellow-green clipped to yellow under HDR gain.
8. Street-look side effects while the set piece is up: the grade black point (`zr_black`) and the far-tower plum rule (`zr_far`) apply as in the staged street (`CityZoomStreet._post`), gated on `hq_net != null`; nothing changes otherwise.
9. Park lots under the cleared rects drop out of the chunk park meshes, and the Solace park mesh is filtered (restored on release).
10. The real wet-road car streaks are hidden while the set piece stands (they ran across the avenue's cross street as thin horizontal lines).

## Gaps / what is not at the plate yet
- **Light distribution**: no wide bright mid-frame band, bottom still too bright, upper frame too dark (see table). A taller, denser lit facade wall behind the flank rows and a dimmer foreground would move the brightest row from 83 % to the 55-70 % range.
- **Detail density**: the flank blocks and slabs are simple prisms with window dots; the plate has water tanks, stairs, wires, signage of every size and ground clutter. No cables, no vehicles, no people.
- **Road gloss**: wet look is faked with additive streaks and pools; no reflection of the helix or the gate (the real ZoomRoad reflection is not used on the avenue).
- **Helix**: reads as a glowing lime helix but the flat cel tones lose the glass pods' depth; the pods are cream (office / window roles) rather than the plate's lit lime and pink nuclei; no interior mapping. Halo is a thin ring plus a pink pole.
- **Node markers**: types are placeholders; the next node's column is tall (cyan) and sits close to the camera in the hero. No floor / "visible floor" logic is needed because all nodes are on the ground; the relay's mast is the only vertical one.
- **Alternates are camera angles only**; no time-of-night alternate (the sky, fog and grade come from the zoom-rule uniforms shared with the street; changing them here would change the street).
- **Highways** cross the avenue near the camera in `alt_far` (real city; a flyover is in front of the HQ approach from that direction).
- The helix top and the halo column sit about 3 degrees under the frame top in the hero; a wider fov would be needed for a taller helix.
- No game wiring: the game must call `set_hq_netrun(true)` with `hq_on` true when the HQ netrun starts and the T11 / T12 camera from `CityHqNet.fly_pose` / `pose`; the node path is art-only and not linked to `HqCompoundLayout` / the run graph.
- The tool's `--hide=` hides by node name only (Glow / Solid are the set piece's two meshes).
- Slips: I typed `python -` twice (a stdin form, once with `< /dev/null`); each hung until I stopped that task by id, nothing ran. No `taskkill`.
