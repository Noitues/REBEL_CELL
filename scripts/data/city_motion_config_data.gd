class_name CityMotionConfigData
extends Resource
## ART-5 5c: every number the unified city's motion layers read (ART_BIBLE v2 §4.1 car LOD,
## §4.2 city motion, §4.3 Heat on maps, §5.4 reduce effects / reduce motion, §6.1 traffic
## and sky lanes; concept recipes art-concepts-r43 round 24 `make_heat.py`, round 26
## `roads.py`, round 37 calm Heat B, round 40 `cars_lod`). Read-only at runtime; the shipped
## values live in `content/config/city_motion_config.tres`. Lengths are world units (BU;
## 1D: a lot is 6 BU), heights BU above the street. Timings of each motion (period, blink
## share, sweep angle) live in `ui_motion.tres` under the layer's motion id
## (CityMotionLayers.MOTION_IDS); this file holds the counts, sizes, colours and shapes.

## Where the shipped config lives.
const CONFIG_PATH := "res://content/config/city_motion_config.tres"
## Heat bands (ART_BIBLE 2.8): COOL, NOTICED, FLAGGED, HUNTED; PURGE uses HUNTED's look.
const BAND_LOOKS := 4

@export_group("Sky lanes (round 26 v4: 16 road shapes, no decks)")
## Deck heights of the roads on the district's busiest avenues (round 26 `roads.py`):
## A lower / upper deck, B, C, F, D, E.
@export var deck_a_low: float = 18.0
@export var deck_a_high: float = 34.0
@export var deck_b: float = 52.0
@export var deck_c: float = 26.0
@export var deck_f: float = 44.0
@export var deck_d: float = 20.0
@export var deck_e: float = 40.0
## Four-level stack ramps: the tight pair's and the wide pair's peak heights and radii (lots).
@export var stack_tight_peak: float = 58.0
@export var stack_wide_peak: float = 74.0
@export var stack_tight_radius: float = 2.6
@export var stack_wide_radius: float = 4.2
## Cloverleaf loop radius (lots): four 270-degree loops between A's lower deck and F.
@export var clover_radius: float = 2.1
## C's spiral ramp: radius (lots), turns, the street height it lands at.
@export var spiral_radius: float = 2.4
@export var spiral_turns: float = 1.75
@export var spiral_floor: float = 3.0
## Lots a straight road takes to ramp down to `ramp_floor` at its ends.
@export var ramp_lots: float = 6.0
@export var ramp_floor: float = 3.0
## Least lots between two parallel roads, and the least span (lots) a road needs.
@export var road_min_spacing: int = 6
@export var road_min_span: int = 16
## Path sample step (lots) before the arc-length bake, and texels per baked lane row.
@export var path_step_lots: float = 0.5
@export var bake_samples: int = 512
## The two directions of a two-way road sit this far either side of its centre line.
@export var lane_side: float = 0.9
## Faint lane-guide dots (round 26 v3: every 9 px at the Grid): spacing, size, alpha.
@export var guide_spacing: float = 4.0
@export var guide_size: float = 0.32
@export var guide_alpha: float = 0.45

@export_group("Sky-lane cars (round 26 v4, round 40 cars_lod)")
## The six lane colours (pink, cyan, amber, violet, mint, orange): each car picks one from
## the seeded `city_traffic` stream, day and night.
@export var lane_colors: Array[Color] = [Color(1.0, 0.27, 0.75), Color(0.31, 0.86, 1.0), Color(1.0, 0.77, 0.24),
	Color(0.67, 0.47, 1.0), Color(0.35, 1.0, 0.78), Color(1.0, 0.47, 0.24)]
## Car gap (BU; round 26 v3: 1.4x wider), whole gaps a car travels per loop (14-20), the
## share of slots left empty, the speed line's length range (BU).
@export var car_gap: float = 16.0
@export var gaps_per_loop: Vector2i = Vector2i(14, 20)
@export var car_skip: float = 0.22
@export var streak_length: Vector2 = Vector2(6.0, 12.0)
## Share of a lane's ends where a car fades in / out (it wraps there).
@export var end_fade: float = 0.04
## FAR: head dot size and line width (BU); MEDIUM: box size (BU) and alpha (~35 %
## translucent); CLOSE: model length (BU) and the thick speed line's width.
@export var far_dot: float = 1.1
@export var far_line: float = 0.5
@export var medium_box: Vector3 = Vector3(2.6, 0.7, 1.3)
@export var medium_alpha: float = 0.65
@export var medium_line: float = 0.35
@export var close_length: float = 4.4
@export var close_line: float = 0.32
## The CLOSE model's body (round 40 cars_lod: a light silver-violet wedge, toon-lit).
@export var close_body_color: Color = Color(0.66, 0.64, 0.78)
## Night: the white headlight at the nose (round 26 v4) and its gain; day: the dot takes
## the lane colour.
@export var headlight: Color = Color(1.0, 0.97, 0.9)
@export var headlight_gain: float = 1.6
@export var body_color: Color = Color(0.10, 0.09, 0.14)

@export_group("Car LOD (ART_BIBLE 4.1, by camera ortho, with hysteresis)")
@export var car_far_above: float = 400.0
@export var car_close_below: float = 150.0
## Share past a tier's edge the zoom must go before the tier swaps.
@export var lod_hysteresis: float = 0.04
## Sky lanes at management zooms (raid, netrun) draw at this share (bible 4.1: 35 %).
@export var management_gain: float = 0.35

@export_group("Street traffic (round 24 layer 1)")
## Avenues carrying cars: the least mean traffic, the gap (BU), the height (BU), the dot and
## streak sizes (BU), the night head / tail colours.
@export var street_min_traffic: float = 0.3
@export var street_gap: float = 9.0
## A street car's place in its slot wanders by up to this share of a gap.
@export var street_jitter: float = 0.3
@export var street_height: float = 0.5
@export var street_dot: float = 0.55
@export var street_streak: float = 2.4
@export var street_head: Color = Color(1.0, 0.93, 0.78)
@export var street_tail: Color = Color(1.0, 0.18, 0.14)
## ART-5 5e (bible 5.4): under reduce motion street traffic keeps moving at this share of its
## speed, without streaks (0..1).
@export var reduce_motion_street_rate: float = 0.4

@export_group("Holo billboards (round 24 layer 3)")
@export var billboard_count: int = 16
## Size (BU, width x height), height above the roof, the least roof height that carries one.
@export var billboard_size: Vector2 = Vector2(6.0, 3.6)
@export var billboard_lift: float = 2.0
@export var billboard_min_roof: float = 16.0
## Emission gain night / day, scanline count, panels in the cycle.
@export var billboard_gain_night: float = 1.7
@export var billboard_gain_day: float = 0.9
@export var billboard_scanlines: float = 22.0
@export var billboard_panels: int = 4
## Spill light a billboard throws (LightSpill.uniforms_3d): radius (BU) and intensity.
@export var billboard_spill_radius: float = 14.0
@export var billboard_spill: float = 0.8

@export_group("Aviation lights (round 24 layer 3)")
## Blinking red lights on the tallest roofs: how many, size (BU), colour, gain night / day.
@export var aviation_count: int = 48
@export var aviation_size: float = 0.9
@export var aviation_color: Color = Color(1.0, 0.14, 0.12)
@export var aviation_gain_night: float = 2.2
@export var aviation_gain_day: float = 1.2
## A blinking light's brightness between blinks (a red dot still reads in a still frame).
@export var blink_off_level: float = 0.3

@export_group("Searchlights (round 24 FLAGGED, round 37 calm Heat B)")
## Beam length and end radius (BU), the beam's lean from vertical (deg), colour.
@export var searchlight_length: float = 110.0
@export var searchlight_radius: float = 9.0
@export var searchlight_lean: float = 34.0
@export var searchlight_color: Color = Color(0.85, 0.91, 1.0)
## Least roof height for a searchlight and its spill (radius, intensity).
@export var searchlight_min_roof: float = 14.0
@export var searchlight_spill_radius: float = 18.0
@export var searchlight_spill: float = 0.6

@export_group("Helicopters and drones (round 6 suspicion, round 24 HUNTED)")
## Choppers circle at `chopper_altitude` on orbits of `chopper_orbit` (BU) round their
## centre, spotlight cone radius on the ground; body length (BU).
@export var chopper_altitude: float = 40.0
@export var chopper_orbit: float = 30.0
@export var chopper_spot_radius: float = 6.0
@export var chopper_length: float = 4.2
@export var chopper_color: Color = Color(0.38, 0.45, 0.56)
## Drones: altitude, orbit, spot radius, size.
@export var drone_altitude: float = 22.0
@export var drone_orbit: float = 7.0
@export var drone_spot_radius: float = 2.4
@export var drone_size: float = 1.2
@export var drone_color: Color = Color(0.24, 0.26, 0.34)
## Spot beam colour and alpha (cone) and ground pool alpha.
@export var spot_color: Color = Color(0.85, 0.91, 1.0)
@export var spot_alpha: float = 0.16
@export var pool_alpha: float = 0.35

@export_group("Heat lights (ART_BIBLE 4.3: calm, centred on hardened nodes)")
## Per band look (COOL, NOTICED, FLAGGED, HUNTED; PURGE uses HUNTED's): searchlights,
## alarm beacons, police strobes, choppers, drones, and the searchlights' alpha (calm Heat B:
## lower intensity).
@export var band_searchlights: Array[int] = [0, 0, 2, 2]
@export var band_alarms: Array[int] = [0, 3, 2, 2]
@export var band_police: Array[int] = [0, 0, 0, 13]
@export var band_choppers: Array[int] = [0, 0, 0, 2]
@export var band_drones: Array[int] = [0, 0, 0, 6]
@export var band_searchlight_alpha: Array[float] = [0.0, 0.0, 0.14, 0.22]
## Rig placement: lots round the rig's centre (the hardened nodes' centre, else home)
## where its roofs and streets are picked, and the least spacing (lots) between picks.
@export var rig_radius_lots: float = 18.0
@export var rig_spacing_lots: float = 4.0
## Each hardened node: a thin HEAT_B ring (radius, width BU) with one soft circling light
## (alternating red / blue by node) of this size at this height.
@export var node_ring_radius: float = 4.0
@export var node_ring_width: float = 0.35
@export var node_light_size: float = 2.2
@export var node_light_height: float = 1.5
## Police / alarm colours (round 6 strobes, round 24 alarm amber), strobe size (BU).
@export var police_red: Color = Color(1.0, 0.13, 0.22)
@export var police_blue: Color = Color(0.16, 0.42, 1.0)
@export var alarm_color: Color = Color(1.0, 0.77, 0.16)
@export var strobe_size: float = 2.4
@export var strobe_pool: float = 9.0

@export_group("Suspicion (round 6: local police, choppers and drones)")
@export var suspicion_police: int = 13
@export var suspicion_choppers: int = 3
@export var suspicion_drones: int = 5

@export_group("Day and night (round 6 day / night, round 26 day v4)")
## The city's day look for the host (the toon ramp shadow / mid / lit, sky, window gain,
## neon gain, haze); the host lerps its night look toward it by the night share.
## ART-5 5e (the day look's windowed review against round 26 `hq_*_close_day` and
## `city_ambient_day_v4`): the cool day of the references (blue-grey sky and haze, the
## territories' own colours), not a warm one (the warm ramp turned Solace's teal olive).
@export var day_ramp: Array[Color] = [Color(0.30, 0.33, 0.46), Color(0.56, 0.60, 0.70), Color(0.84, 0.86, 0.88)]
@export var day_sky: Color = Color(0.68, 0.72, 0.86)
@export var day_window_gain: float = 0.12
@export var day_neon_gain: float = 0.62
@export var day_haze: Color = Color(0.66, 0.70, 0.82)
@export var day_grade: Color = Color(0.98, 1.0, 1.03)
## ART-5 5e: the post's bloom by day (the night's CityConfig.bloom / glow_threshold bloom every
## lit wall by day and wash the landmarks out white).
@export var day_bloom: float = 0.2
@export var day_glow_threshold: float = 0.92
## Sky-lane car gain by day (streaks in the lane colour against the bright city).
@export var day_car_gain: float = 1.25

@export_group("Spill (LightSpill.uniforms_3d)")
## The spill sources nearest the camera target are sent (at most LightSpill.MAX_3D).
@export var spill_gain: float = 1.0


## Problems with this config (empty when valid).
func validate() -> PackedStringArray:
	var errors := PackedStringArray()
	if lane_colors.size() != 6:
		errors.append("City motion: lane_colors needs the six lane colours.")
	if gaps_per_loop.x < 1 or gaps_per_loop.y < gaps_per_loop.x:
		errors.append("City motion: gaps_per_loop must be 1 <= min <= max.")
	if car_gap <= 0.0 or street_gap <= 0.0 or guide_spacing <= 0.0 or path_step_lots <= 0.0:
		errors.append("City motion: gaps, spacings and the path step must be > 0.")
	if bake_samples < 16:
		errors.append("City motion: bake_samples must be >= 16.")
	if car_close_below >= car_far_above:
		errors.append("City motion: car_close_below must be below car_far_above.")
	if lod_hysteresis < 0.0 or lod_hysteresis >= 0.5:
		errors.append("City motion: lod_hysteresis must be in [0, 0.5).")
	for arr: Array in [band_searchlights, band_alarms, band_police, band_choppers, band_drones, band_searchlight_alpha]:
		if arr.size() != BAND_LOOKS:
			errors.append("City motion: every band array needs %d entries (COOL..HUNTED)." % BAND_LOOKS)
			break
	if day_ramp.size() != 3:
		errors.append("City motion: day_ramp needs shadow, mid and lit.")
	if car_skip < 0.0 or car_skip >= 1.0:
		errors.append("City motion: car_skip must be in [0, 1).")
	if day_bloom < 0.0 or day_glow_threshold < 0.0 or day_glow_threshold > 1.0:
		errors.append("City motion: day_bloom must be >= 0 and day_glow_threshold in [0, 1].")
	if reduce_motion_street_rate < 0.0 or reduce_motion_street_rate > 1.0:
		errors.append("City motion: reduce_motion_street_rate must be in [0, 1].")
	return errors


## The shipped config.
static func shipped() -> CityMotionConfigData:
	return load(CONFIG_PATH) as CityMotionConfigData
