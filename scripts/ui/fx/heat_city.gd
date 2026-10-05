class_name HeatCity
extends Control
## ART-2 2C (ART_BIBLE v2 §3.15, H1 "the city reacts", round 22 heat_city_v4): Heat on the
## combat screen, on the backdrop only (behind the wheels' darkened pools; never on the HUD
## or the wheels). Per band (COOL, NOTICED, FLAGGED, HUNTED, PURGE = HUNTED's look for now):
## NOTICED three slowly turning red/amber alarm beacons on side buildings, nothing on the
## target; FLAGGED two rooftop searchlights at the screen sides sweeping the sky away from
## the target, and two alarm beacons on the target; HUNTED police light clusters (13) and
## two searchlights on the target. Counts from campaign_config.tres (heat_city_*), periods
## from ui_motion.tres (`heat_city_beacon`, `heat_city_sweep`, T0). Reduce motion: the
## lights hold steady (no turn or strobe), the searchlights stand fixed. View only.

## Where things stand, as shares of the screen: side buildings' beacons (x from each edge,
## y), the side searchlights' feet, the street the police lights line, the target's roof
## offset above its point.
const SIDE_X := 0.08
const SIDE_Y := 0.34
const SIDE_STEP := 0.07
const SEARCH_FOOT_Y := 0.62
const STREET_Y := 0.79
const STREET_SPAN := 0.8
const TARGET_ROOF := 0.12
## A beacon's glow radius and its beam's length (px at text scale 1.0) and spread (rad).
const BEACON_R := 7.0
const BEAM_LEN := 46.0
const BEAM_SPREAD := 0.45
## A searchlight's cone: its length (share of the screen's height) and half-width (rad).
const CONE_LEN := 0.7
const CONE_HALF := 0.07
const CONE_ALPHA := 0.2
## Police lights: a cluster's two lamps (px apart), their glow, the strobe's rate (Hz,
## never above 3) and the spill's alpha.
const POLICE_GAP := 9.0
const POLICE_R := 4.0
const POLICE_HZ := 2.5
const SPILL_R := 24.0
const SPILL_ALPHA := 0.24
const SEGMENTS := 18

var band: int = 0
## The target building's point (global): beacons and searchlights on the target aim here.
var target: Vector2 = Vector2.INF
var _t: float = 0.0


func _init() -> void:
	mouse_filter = Control.MOUSE_FILTER_IGNORE
	set_process(false)


func _ready() -> void:
	set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)


## Shows Heat band `p_band` (0 COOL .. 4 PURGE) with the target at `p_target` (global).
func set_band(p_band: int, p_target: Vector2 = Vector2.INF) -> void:
	band = clampi(p_band, 0, 4)
	target = p_target
	set_process(band > 0 and _moving())
	queue_redraw()


## True when the lights turn and sweep (their T0 entries live and reduce motion off).
func _moving() -> bool:
	var turns := Motion.live(&"heat_city_beacon")
	var sweeps := Motion.live(&"heat_city_sweep")
	return (turns or sweeps) and not Settings.reduce_motion


func _process(delta: float) -> void:
	_t += delta
	queue_redraw()


## What band `b` shows, from the campaign config: {side_beacons, side_searchlights,
## target_beacons, police, target_searchlights}.
static func counts(b: int, cfg: CampaignConfigData = null) -> Dictionary:
	var c := cfg if cfg != null else RunManager.config()
	var i := clampi(b, 0, 4)
	return {"side_beacons": _at(c.heat_city_side_beacons, i), "side_searchlights": _at(c.heat_city_side_searchlights, i),
		"target_beacons": _at(c.heat_city_target_beacons, i), "police": _at(c.heat_city_police_lights, i),
		"target_searchlights": _at(c.heat_city_target_searchlights, i)}


static func _at(a: PackedInt32Array, i: int) -> int:
	return a[i] if i < a.size() else 0


func _draw() -> void:
	if band <= 0:
		return
	var n := counts(band)
	var sz := size
	var s := Settings.text_scale
	var moving := _moving()
	var beacon_period := maxf(VfxTier.T0_MIN_PERIOD, Motion.seconds(&"heat_city_beacon"))
	var sweep_period := maxf(VfxTier.T0_MIN_PERIOD, Motion.seconds(&"heat_city_sweep"))
	var turn := TAU * _t / beacon_period if moving and Motion.live(&"heat_city_beacon") else 0.0
	var tgt := target - global_position if target != Vector2.INF else Vector2(sz.x * 0.62, sz.y * 0.3)
	var roof := tgt - Vector2(0, sz.y * TARGET_ROOF)
	var glow := Motion.amplitude(&"heat_city_beacon")
	# NOTICED: alarm beacons on the side buildings (left, right, left ...).
	for k in int(n["side_beacons"]):
		var left := k % 2 == 0
		var x := sz.x * (SIDE_X + SIDE_STEP * (k >> 1)) if left else sz.x * (1.0 - SIDE_X - SIDE_STEP * (k >> 1))
		_beacon(Vector2(x, sz.y * (SIDE_Y + 0.05 * (k % 3))), turn + k * 1.7, Palette.HARM if k % 2 == 0 else Palette.CRT_AMBER, glow, s)
	# FLAGGED: searchlights at the screen sides sweeping the sky away from the target.
	var half := Motion.amplitude(&"heat_city_sweep")
	var sweep := sin(TAU * _t / sweep_period) * half if moving and Motion.live(&"heat_city_sweep") else 0.0
	for k in int(n["side_searchlights"]):
		var left := k % 2 == 0
		var foot := Vector2(sz.x * (0.02 if left else 0.98), sz.y * SEARCH_FOOT_Y)
		var away := -PI * 0.5 + (-0.45 if left else 0.45)
		_cone(foot, away + sweep * (1.0 if left else -1.0), sz.y * CONE_LEN)
	for k in int(n["target_beacons"]):
		_beacon(roof + Vector2((k - 0.5) * 60.0 * s, 0), turn + k * 2.3, Palette.HARM, glow, s)
	# HUNTED: police light clusters along the street, two searchlights on the target.
	for k in int(n["police"]):
		var x := sz.x * (0.5 - STREET_SPAN * 0.5 + STREET_SPAN * (k + 0.5) / maxf(1.0, float(n["police"])))
		_police(Vector2(x, sz.y * (STREET_Y + 0.03 * ((k * 7) % 3 - 1))), k, moving, s)
	for k in int(n["target_searchlights"]):
		var foot := Vector2(tgt.x + (k - 0.5) * sz.x * 0.5, sz.y * SEARCH_FOOT_Y + sz.y * 0.2)
		var aim := (roof - foot).angle() + (sweep * 0.25 if moving else 0.0)
		_cone(foot, aim, foot.distance_to(roof) * 1.05)


func _beacon(at: Vector2, turn: float, col: Color, glow: float, s: float) -> void:
	draw_circle(at, BEACON_R * s * 2.2, Color(col, glow * 0.25))
	draw_circle(at, BEACON_R * s, Color(col, glow))
	var d := Vector2(cos(turn), sin(turn) * 0.35)
	var tip := at + d * BEAM_LEN * s
	var side := d.orthogonal() * tan(BEAM_SPREAD * 0.5) * BEAM_LEN * s
	draw_colored_polygon(PackedVector2Array([at, tip + side, tip - side]), Color(col, glow * 0.35))


func _cone(foot: Vector2, angle: float, length: float) -> void:
	var d := Vector2(cos(angle), sin(angle))
	var tip := foot + d * length
	var side := d.orthogonal() * tan(CONE_HALF) * length
	draw_colored_polygon(PackedVector2Array([foot, tip + side, tip - side]), Color(Palette.PAPER, CONE_ALPHA))


func _police(at: Vector2, k: int, moving: bool, s: float) -> void:
	# Red and blue swap at POLICE_HZ (under 3 Hz); steady under reduce motion.
	var phase := int(floor(_t * POLICE_HZ * 2.0 + k)) % 2 if moving else 0
	var red := Color(Palette.HARM, 1.0 if phase == 0 else 0.35)
	var blue := Color(Palette.NET_CYAN, 0.35 if phase == 0 else 1.0)
	var gap := POLICE_GAP * s * 0.5
	draw_circle(at - Vector2(gap, 0), SPILL_R * s, Color(red, SPILL_ALPHA * red.a))
	draw_circle(at + Vector2(gap, 0), SPILL_R * s, Color(blue, SPILL_ALPHA * blue.a))
	draw_circle(at - Vector2(gap, 0), POLICE_R * s, red)
	draw_circle(at + Vector2(gap, 0), POLICE_R * s, blue)
