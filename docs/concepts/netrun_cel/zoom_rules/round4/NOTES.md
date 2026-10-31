# Zoom rules, round 4: one target street, value and mood

Godot: `D:/rc_art/godot_look_tide`, branch `art/netrun-zoom` (round-4 commit at the end of this file).

## 1. Fix: one target street (the dolly swing)
Cause: the dolly's district camera was built on the prototype block (lot -37,-24.5) while the street camera was chosen by eye at (34.5,-9) N, so the target slid hundreds of BU sideways. New `CityZoomTarget` (pure): centre lot (34.5,-7.5), the camera look N across it, 3 rows, heading X; `frontage_lot()` = (34.5,-9.0), `end_lots()`, `angle_to`, `yaw_step`. `nr_zoom --target` derives the plan frame (recentred on the segment: the city-view highlight position), the district camera, the dolly and the street camera from it; the street camera and the staged rows come from the same lots. The dolly interpolates yaw by the shortest arc (135 to 90 degrees, 45 degrees total, monotone).
Proof (`zoom_track.jpg`, `logs/track_stats.txt`, TRACK lines in `logs/dolly_track.log`; the target centre is projected with the real Camera3D into all 75 frames; green = centre, magenta = end lots): **max heading change 1.52 deg/frame = 18.2 deg/s at 12 fps; target centre x drift at most 45 px from the frame centre; its y goes 540 to 753 px (the designed lens shift: the road centre sits at 70 % down); the camera looks at the centre within 4.6 degrees in every frame.** Tests: `every dolly pose looks at the target` (within 14 degrees), `heading changes smoothly by the shortest arc` (under 3 degrees per frame, monotone, ends at 90), target defines frontage and axis. Not done: a visible city-view highlight on the segment (only its position is derived).

## 2. Value and mood (config values in `zr_*`)
- Facades: near-black plum shaft (`zr_plum_color` 0.7 share over the body above the shop zone, then `zr_body_dim` 0.45 albedo / 0.3 lit emission); signs lean magenta/pink (`zr_pink_share` 0.5) with cyan (0.15), corp colour for the rest.
- Road: asphalt albedo 0.0065 (linear; the display adds the sRGB curve, 0.022 had shown as 16 % value), road mean value **0.165** (80-100 % rows incl. markings and streaks; plain asphalt about 8-12 %); the mirrored reflection of the band and signs is in (gain 2.6, gloss 0.6+), plus a mirror bug fixed (below). Car streaks per the traffic-corp rule: head = corp hue at V 0.55 at gain 5, tail = corp hue at V 0.38, 110 cars of 14-50 BU.
- Lamps: 0.2 BU poles (4 px minimum), warm-white heads, compact strong pools (radius 4.2 BU, gain 2.6). Markers: antenna masts (the diamonds on poles) are dropped in the staged street; 4 ground discs and a ribbon on the middle road row, the selected one a pole-less larger glow with a faint column.
- Mood: three searchlight beams at alpha 1.0 (they read), ground mist 2 BU at 0.14, plum fog (colour 0.21/0.075/0.25, D 105 BU), haze cards halved.
- Not effective: the grade black point (`zr_black`, set on `g1_black`) changed no pixel; the street path does not use it. Left in config, harmless.
Measured (`street_frame.png`): **brightest-row ratio 2.20** (round 3 2.24, plate 2.72, target 2.5) at 80 % down (y 862, the shop band and kerb line); frame mean 0.20 (plate 0.20); road mean 0.165. The ratio did not improve: the facade got darker but so did the band's neighbours. Target 2.5 and 70-75 % not reached.

## Bugs found on the way
1. Dolly end frames had a pink floor: the reflection camera kept KEEP_WIDTH from the dolly's perspective branch with a height-sized frustum (1.8x zoomed reflection). Now the frustum branch sets KEEP_HEIGHT itself. 2. The road mesh was not rebuilt when the staged road appeared after the road was built (dolly arriving at the street band); the rebuild key now includes the staged cells. 3. Mirror idle beat: 12 frames of grace.

## Perf, city viewport p95, 500 frames
Clean GPU (before the last two fixes): 3.5 ms. After them, runs measured **10.4-14.3 ms** with road on or off (a third-party GPU load; the same build with the road off shows the same), so the road is not the cost; I could not re-measure on a quiet GPU. One run is above the 12.57 limit (14.26); treat the number as unverified under contention. `logs/perf*.log`.

## City band
Stage 1 ON vs OFF: 0 differing pixels.

## Tests
Round-3 list plus stage tests: first full run 298 tests with 1 failing (the car light test written for the old head rule, rewritten to the round-4 rule), then the zoom/neon/shader/model/motion subset re-run: **121 tests, 0 failing** (`logs/targeted_rerun.log`; the first run is `logs/targeted_full_run1.log`). New tests: 3 for the target street; car light rule updated; mirror beat updated.

Godot commit: bf1e5737
