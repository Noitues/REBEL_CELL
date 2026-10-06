class_name CityConfig
extends Resource
## The unified city's config (ART-5 5a, from ART-1 1D's spike config): every number the 3D
## city reads (bible §4.1, §4.2, §6.1; concept recipes art-concepts-r43 round 36-40
## `layout36.py`, `unified40.py`, `target_corps.py`, `post40.py`). Read-only at runtime.
## The game's values live in `content/config/city_config.tres` (the whole city); the
## render spike keeps its district in `tools/spike/city/city_spike_config.tres`.

@export_group("World")
## World units (BU) per lot (layout36.U).
@export var lot_bu: float = 6.0
## The game's iso height px -> BU (unified40.KH = U / 41.64 * 1.15).
@export var height_px_bu: float = 0.16571
## The district: centre (lots) and radius (lots) of the game's layout that is built.
@export var district_centre: Vector2 = Vector2(34, 22)
@export var district_radius: float = 50.0
## The layout's look seed (NeonCity.city_seed).
@export var city_seed: int = 7

## HQ stand-in (the five locked heroes are ART-5): a stepped tower on the HQ lot, tiers,
## tier height (BU), inset per tier (lots), first inset (lots).
@export var hq_tiers: int = 9
@export var hq_tier_bu: float = 7.0
@export var hq_tier_inset: float = 0.42
@export var hq_inset: float = 1.2

@export_group("Camera")
@export var yaw_deg: float = 135.0
@export var pitch_deg: float = 40.0
## Camera distance from its target along the view axis (BU; orthographic, only for clipping).
@export var camera_distance: float = 2600.0
@export var camera_far: float = 6000.0
## The views: name -> [target lot x, target lot y, ortho width BU].
@export var views: Dictionary = {
	"grid": [34.0, 24.0, 440.0],
	"raid": [32.0, 30.0, 380.0],
	"netrun": [30.0, 27.0, 190.0],
	"close": [27.0, 27.0, 60.0],
}
## Ortho clamp for a raid fitted to the network (bible Appendix C #13) and its margin (BU).
@export var raid_fit_min: float = 220.0
## ART-3 6w: the widest raid is 640 (round 39's 380 framed the x1 layout; 5e's x2 Site spread
## doubles the network, which needs ~540-600 on the setup's map part at text 1.0).
@export var raid_fit_max: float = 640.0
@export var raid_fit_margin: float = 40.0
## ART-3 6w uplink pads (unified40 lines 404-434): the pad's half-size as a share of its roof's
## shorter side, and the lowest roof (BU) that carries one.
@export var uplink_pad_share: float = 0.32
@export var uplink_min_top: float = 3.0

@export_group("LOD")
## post40.lod_of anchors: lod 2 = city (ortho 820), 1 = raid (176), 0 = transit (88).
@export var lod_ortho_city: float = 820.0
@export var lod_ortho_raid: float = 176.0
@export var lod_ortho_transit: float = 88.0
## View band where buildings go see-through (lod), and the see-through look (v3).
@export var see_through_lod_from: float = 1.50
@export var see_through_lod_to: float = 1.595
@export var see_through_opacity: float = 0.68
@export var see_through_dark: float = 0.86
@export var see_through_chroma: float = 1.35
@export var see_through_window_gain: float = 0.15
## Street lane glow at management zooms (raid / netrun) and sky lanes there.
@export var lane_glow_management: float = 0.28
@export var sky_lane_management: float = 0.35
## Car LOD (ortho): FAR above car_far_above, CLOSE below car_close_below; hysteresis share.
@export var car_far_above: float = 400.0
@export var car_close_below: float = 150.0
@export var lod_hysteresis: float = 0.06
## Building detail tiers (ortho): raid detail (ledges, facet ink) at or below, transit
## detail (shopfronts) at or below.
@export var detail_raid_below: float = 420.0
@export var detail_transit_below: float = 200.0

@export_group("Quality tiers (Settings.city_quality; Deck = 1)")
## Index = tier. -1 (renderer default) reads quality_default.
@export var quality_default: int = 2
@export var quality_render_scale: Array[float] = [0.6, 0.75, 1.0]
@export var quality_shadows: Array[bool] = [false, true, true]
@export var quality_shadow_size: Array[int] = [1024, 2048, 2048]
@export var quality_msaa: Array[int] = [0, 0, 0]
@export var quality_ink: Array[bool] = [true, true, true]
@export var quality_fog: Array[bool] = [false, true, true]
@export var quality_rain: Array[bool] = [false, true, true]
## Resolution share of the ground-only pass under see-through buildings (it shows at
## 1 - opacity = 32 %, so half resolution reads the same and saves ~55 MB at 1080p).
@export var ground_pass_scale: float = 0.5
## Frame budget for the city (ms, plan §5.2).
@export var budget_ms: float = 8.0

@export_group("Combat backdrop (D17 on the city, ART-8 8w)")
## Per quality tier: the combat backdrop is a close-up of this city (true) or the baked
## still (false; the cheaper fallback below the tier).
@export var backdrop_city_tiers: Array[bool] = [false, true, true]
## A boss fight's HQ close-up: ortho width (BU) and the camera target's height on the HQ
## lot (BU); the HQ fills the gap between the wheels.
@export var backdrop_hq_ortho: float = 140.0
@export var backdrop_hq_lift: float = 30.0
## A regular fight's Site close-up: ortho width (BU) and target height (BU).
@export var backdrop_site_ortho: float = 90.0
@export var backdrop_site_lift: float = 8.0
## The DISPATCH canyon's close-up: share of the HQ-run framing's ortho.
@export var backdrop_canyon_share: float = 0.7
## Fight won without a won mask: the target's kept (undimmed) ellipse, share of the view's
## width, round the target's point.
@export var backdrop_keep_radius: float = 0.16

@export_group("Buildings")
## Facet cell (BU) the walls are split into, and the jitter (share of a cell / BU).
@export var facet_cell: float = 1.7
@export var facet_jitter: float = 0.28
@export var facet_normal_jitter: float = 0.12
## Unit-mesh height classes (BU upper bounds) for the facet rows.
@export var height_classes: Array[float] = [8.0, 20.0, 45.0, 1000.0]
@export var height_class_rows: Array[int] = [3, 8, 18, 30]
@export var wall_columns: int = 4
## Tone jitter per triangle (toon colour multiplier range).
@export var tone_min: float = 0.86
@export var tone_max: float = 1.12
## Building families (unified40.FAMS_C), the territory tint share, roof lift.
@export var families: Array[Color] = [Color(0.42, 0.40, 0.52), Color(0.38, 0.44, 0.52), Color(0.52, 0.42, 0.40),
	Color(0.36, 0.42, 0.40), Color(0.48, 0.44, 0.36), Color(0.40, 0.38, 0.46)]
@export var territory_tint: float = 0.28
@export var roof_gain: float = 1.08
## Neon roof trim share and width (BU).
@export var roof_trim_share: float = 0.42
@export var roof_trim_bu: float = 0.22
## Window grid (BU): pitch, size, first floor, lit share, brightness floor.
@export var window_pitch: Vector2 = Vector2(1.6, 1.9)
@export var window_size: Vector2 = Vector2(0.8, 0.7)
@export var window_first: float = 1.6
@export var window_share: float = 0.3
@export var window_dim_min: float = 0.5
@export var window_colors: Array[Color] = [Color(1.0, 0.68, 0.28), Color(1.0, 0.68, 0.28), Color(1.0, 0.8, 0.5),
	Color(0.45, 0.9, 1.0), Color(1.0, 0.42, 0.72), Color(0.9, 0.9, 1.0)]
## Window emission gain (night).
@export var window_gain: float = 1.4
## Ledge every N BU (the ink catches it at raid zoom).
@export var ledge_every: float = 6.0
@export var ledge_bu: float = 0.16

@export_group("Light (target_corps night mode)")
## 3-band toon ramp: shadow / mid / lit colours, band edges on N.L.
@export var ramp: Array[Color] = [Color(0.09, 0.08, 0.21), Color(0.20, 0.17, 0.36), Color(0.36, 0.30, 0.54)]
@export var ramp_edges: Vector2 = Vector2(0.118, 0.363)
## Direction toward the key light (Godot world; target_corps sun 48/-28/-38).
@export var to_light: Vector3 = Vector3(-0.705, 0.591, 0.392)
@export var sky: Color = Color(0.03, 0.025, 0.06)
@export var neon_gain: float = 1.2
@export var ground: Color = Color(0.20, 0.20, 0.25)
@export var street: Color = Color(0.13, 0.13, 0.16)
@export var plaza: Color = Color(0.26, 0.25, 0.30)

@export_group("Streets")
## Lane glow strip (unified40 GLANE): base glow, traffic gain, stroke count.
@export var lane_glow_base: float = 0.10
@export var lane_glow_traffic: float = 0.16
@export var lane_stroke_bu: float = 0.18
@export var lane_bed_px: float = 38.0

@export_group("Post (post40.MODE night)")
@export var ink: Color = Color(0.05, 0.04, 0.09)
@export var ink_normal_edge: float = 0.42
@export var ink_depth_edge: float = 1.2
@export var ink_alpha_near: float = 0.85
@export var ink_alpha_far: float = 0.6
@export var ink_wobble_px: float = 1.4
## Edge sample radius (px at 1080p): lines come out about twice as wide.
@export var ink_width_px: float = 1.0
## Share of rain columns carrying a drop.
@export var rain_density: float = 0.06
@export var haze: Color = Color(0.08, 0.06, 0.16)
@export var haze_k: float = 0.34
@export var bloom: float = 0.75
## Godot has no emission-only buffer: the frame's bright part (display value over
## glow_threshold) stands in for post40's glow pass; glow_mip is the screen mip of post40's
## 8 px blur at 2880 (the 30 / 90 px blurs are 2 and 3.6 mips further).
@export var glow_threshold: float = 0.62
@export var glow_mip: float = 1.3
@export var spill: float = 0.5
@export var grime: float = 0.15
@export var fog: Color = Color(0.20, 0.17, 0.33)
@export var fog_amount: float = 0.22
@export var rain: Color = Color(0.75, 0.82, 1.0)
@export var rain_alpha: float = 0.11
@export var grade: Color = Color(0.94, 0.92, 1.04)

@export_group("Traffic (bible §4.2 sky lanes v4)")
## Lane colours (pink, cyan, amber, violet, mint, orange).
@export var lane_colors: Array[Color] = [Color(1.0, 0.27, 0.75), Color(0.31, 0.86, 1.0), Color(1.0, 0.77, 0.24),
	Color(0.67, 0.47, 1.0), Color(0.35, 1.0, 0.78), Color(1.0, 0.47, 0.24)]
## Sky lanes run over the district's busiest avenues (the game's street lines, busiest
## first, ties by line): one lane per height, two directions each (BU above the street).
@export var sky_lane_heights: Array[float] = [22.0, 34.0, 52.0, 28.0, 44.0, 40.0]
## Sideways offset of the two directions (BU).
@export var sky_lane_side: float = 0.9
## Car gap (BU), gaps travelled per loop, loop seconds, skip share, car length range (BU).
@export var car_gap: float = 14.0
@export var car_speed_gaps: float = 4.0
@export var car_loop_s: float = 3.84
@export var car_skip: float = 0.22
@export var car_length: Vector2 = Vector2(8.0, 14.0)
## Street cars on busy streets: share base + traffic gain.
@export var street_car_base: float = 0.08
@export var street_car_traffic: float = 0.25
## Medium-LOD box alpha.
@export var car_box_alpha: float = 0.65


@export_group("Whole city (ART-5 5a)")
## The whole city the model is built for (lots): every territory, HQ and the Sprawl round
## them (bible §4.1: ~14 100 extrusions).
@export var city_rect: Rect2i = Rect2i(-80, -80, 165, 165)
## Chunk size (lots): one MultiMesh per building family per chunk, so frustum culling
## drops what the camera does not see.
@export var chunk_lots: int = 24
## Building LOD by camera ortho (bible §6.1, never distance): LOD0 (full facet grid) at or
## below lod0_below, LOD2 (plain extrusion) above lod2_above, LOD1 between; the swap keeps
## lod_hysteresis.
@export var lod0_below: float = 400.0
@export var lod2_above: float = 760.0
## Facet rows per LOD (share of the height class's rows; 0 = one row) and wall columns.
@export var lod_rows_share: Array[float] = [1.0, 0.5, 0.0]
@export var lod_cols: Array[int] = [4, 2, 1]

@export_group("Zoom and pan (ART-5 5a)")
## The City Grid's own zoom (bible §4.1: ortho ~440) and the continuous zoom's range.
@export var grid_ortho: float = 440.0
@export var zoom_ortho_min: float = 60.0
@export var zoom_ortho_max: float = 1400.0
## Ortho factor per wheel notch / zoom key press (log-linear: equal steps in log ortho).
@export var zoom_step: float = 1.18
## Pan speed of the keys / stick (screen widths per second).
@export var pan_screens_s: float = 0.6
## View bands the views live in (ortho): the netrun transit below band_netrun_below, the
## raid between it and the see-through band's top, the City Grid above.
@export var band_netrun_below: float = 200.0
## Minimap: its size (px at text scale 1), the share of the city it shows, the view box
## and marker colours come from the palette.
@export var minimap_size: Vector2 = Vector2(232, 148)

@export_group("Network decal (bible §6.1; ART-5 5a)")
## Nodes and link points the decal's buffers hold (data texture rows).
@export var net_nodes_max: int = 64
@export var net_points_max: int = 1024
## City-zoom trace: core width and halo (screen px), node disc and tier ring radius (px).
@export var net_trace_px: float = 3.0
@export var net_halo_px: float = 12.0
@export var net_node_px: float = 13.0
@export var net_ring_px: float = 3.0
## Management zooms: the 3-trace bus spacing (px) and the packets' speed (BU / s) and gap.
@export var net_bus_gap_px: float = 4.0
@export var net_packet_speed: float = 24.0
@export var net_packet_gap: float = 30.0
## Dash length / gap (BU) of border and not-yet links.
@export var net_dash_bu: Vector2 = Vector2(4.0, 3.0)
## Strengths: the ground decal, the halo, and the x-ray pass through buildings at the City
## Grid zoom (solid at city lod).
@export var net_gain: float = 1.6
@export var net_halo: float = 0.25
@export var net_xray: float = 0.85

@export_group("City integration (ART-5 5e)")
## The Site layout's spread round each corporation's Grid origin (CityLayout.site_points):
## 1 = 5a's +/-7.5 x 5 lots; 2 frames the Grid at ortho ~440 as round 39 (presentation only).
@export var site_spread: float = 2.0
## The heading (degrees, lot space) each corporation's Site layout is turned round its HQ so
## the spread layout stays in its own territory (0 = 5a's: the boss end to the Grid's right).
@export var site_aim_deg: Dictionary = {}
## Corporations whose Site layout is mirrored across its run axis (true), for the same reason.
@export var site_mirror: Dictionary = {}
## The Site that stands in 5b's `<corp>_site.glb` per corporation (content id), until the
## designer names them (DECISIONS "ART-5 5e", open question).
@export var site_landmarks: Dictionary = {&"solace": &"t1_c", &"halcyon": &"lose_the_case_file", &"orbital": &"o1_d"}
## Roof props (the concept's AC units, water tanks, antennas, roof billboards; bible 4.1:
## from raid zoom): shown at and below this ortho.
@export var roof_props_below: float = 420.0
## Where the roof props stand (unified40.py's own rules, round 40): flat roofs only (top
## scale at least this), both footprint sides over this (BU); AC units 0..roof_ac_max per
## roof; a water tank on this share; an antenna on roofs over this top (BU) at this share;
## a holo billboard on roofs over this top at this share.
@export var roof_prop_min_top_scale: float = 0.99
@export var roof_prop_min_side: float = 2.0
@export var roof_ac_max: int = 2
@export var roof_tank_share: float = 0.18
@export var roof_antenna_above: float = 22.0
@export var roof_antenna_share: float = 0.45
@export var roof_billboard_above: float = 14.0
@export var roof_billboard_share: float = 0.16


## The quality tier for a Settings.city_quality value (-1 = default).
func tier_for(city_quality: int) -> int:
	if city_quality < 0:
		return quality_default
	return clampi(city_quality, 0, quality_render_scale.size() - 1)
