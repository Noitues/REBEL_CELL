class_name RingSwapMark
extends Control
## Art pass W8b (ART_BIBLE §10.2 rule 2, critique gifs/10): a Rank 3 ring swap is seen, not
## only read. The swapped inner ring segment on the loadout's wheel fills and recolours
## (FOCUS: the thing that just changed) and pulses twice, then stays filled a little
## brighter than its neighbours while the view shows it. The fill runs on `loadout_swap`,
## the pulse on `landing_pulse` (T2). Reduce effects or headless: the end state at once.
## Drawn on the wheel's own canvas (the SpinnerView's wheel area), over its segment;
## clicks pass. View only.

const NODE_NAME := "RingSwapMark"
const FILL_MOTION := &"loadout_swap"
const PULSE_MOTION := &"landing_pulse"
## The fill's alpha at rest and at a pulse's peak, the pulses, the edge (px), the gap each
## side of the segment (rad, as SpinnerView draws them) and the arc steps.
const REST_ALPHA := 0.45
const PEAK_ALPHA := 0.9
const PULSES := 2.0
const EDGE := 2.5
const SEGMENT_GAP := 0.04
const STEPS := 12
## The ink label's outline (px) in the fill colour, so it reads over the wheel's own label.
const OUTLINE := 6

## The segment (its index), its middle angle and the ring's centre and radii (wheel px).
var index: int = -1
var mid: float = 0.0
var centre: Vector2 = Vector2.ZERO
var inner_r: float = SpinnerView.RING_INNER
var outer_r: float = SpinnerView.RING_OUTER
var count: int = 1
## The swapped segment's name, drawn in ink over the fill (the wheel's own label is under it).
var label: String = ""
## The segment's pad and the hub's (the wheel places them a frame late: read at draw time).
var _pad: Control = null
var _hub: Control = null
## 0..1: the fill (first part) then the pulses; 1 = at rest.
var t: float = 1.0:
	set(v):
		t = v
		queue_redraw()


## Plays the swap on segment `k` of `view`'s wheel (replacing an earlier mark); returns it
## (null when the wheel has no such segment).
static func play_on(view: SpinnerView, k: int) -> RingSwapMark:
	var pad := view.ring_pad(k)
	if pad == null:
		return null
	var wheel := pad.get_parent() as Control
	var old := wheel.get_node_or_null(NodePath(NODE_NAME))
	if old != null:
		old.free()
	var m := RingSwapMark.new()
	m.name = NODE_NAME
	m.index = k
	m.count = maxi(1, view.ring.size())
	var seg: RingSegmentData = view.ring[k] if k < view.ring.size() else null
	m.label = TextDb.t(seg, "display_name").to_upper() if seg != null else ""
	m._pad = pad
	m._hub = wheel.get_node_or_null(^"HubPad") as Control
	wheel.add_child(m)
	m.play()
	return m


func _init() -> void:
	mouse_filter = Control.MOUSE_FILTER_IGNORE
	focus_mode = Control.FOCUS_NONE
	set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)


## Runs the fill and the pulses (the end state at once when motion doesn't play).
func play() -> void:
	if is_inside_tree():
		get_tree().process_frame.connect(queue_redraw, CONNECT_ONE_SHOT)  # the pads are placed a frame late
	if not Motion.live(FILL_MOTION) or not is_inside_tree():
		t = 1.0
		return
	t = 0.0
	var total := Motion.seconds(FILL_MOTION) + Motion.seconds(PULSE_MOTION) * PULSES
	create_tween().tween_property(self, ^"t", 1.0, total)


## The fill's alpha now (tests): rising while it fills, pulsing, then REST_ALPHA.
func fill_alpha() -> float:
	var fill_share := Motion.seconds(FILL_MOTION) / maxf(0.001, Motion.seconds(FILL_MOTION) + Motion.seconds(PULSE_MOTION) * PULSES)
	if t < fill_share:
		return lerpf(0.0, PEAK_ALPHA, t / fill_share)
	if t >= 1.0:
		return REST_ALPHA
	var u := (t - fill_share) / (1.0 - fill_share)
	return lerpf(REST_ALPHA, PEAK_ALPHA, absf(cos(u * PI * PULSES)))


## Reads the ring's centre and the segment's angle from the wheel's pads (as placed now).
func _measure() -> void:
	if _hub != null and is_instance_valid(_hub):
		centre = _hub.position + _hub.size * 0.5
	elif get_parent() is Control:
		centre = (get_parent() as Control).custom_minimum_size * 0.5
	if _pad != null and is_instance_valid(_pad):
		mid = (_pad.position + _pad.size * 0.5 - centre).angle()


## The segment's outline (wheel px).
func segment_points() -> PackedVector2Array:
	_measure()
	var half := PI / count - SEGMENT_GAP
	var pts := PackedVector2Array()
	for q in STEPS + 1:
		var a := lerpf(mid - half, mid + half, float(q) / STEPS)
		pts.append(centre + Vector2(cos(a), sin(a)) * outer_r)
	for q in STEPS + 1:
		var a := lerpf(mid + half, mid - half, float(q) / STEPS)
		pts.append(centre + Vector2(cos(a), sin(a)) * inner_r)
	return pts


func _draw() -> void:
	var pts := segment_points()
	draw_colored_polygon(pts, Color(Palette.FOCUS, fill_alpha()))
	pts.append(pts[0])
	draw_polyline(pts, Palette.INK, EDGE + 2.0, true)
	draw_polyline(pts, Palette.FOCUS, EDGE, true)
	if label != "":
		var f := Palette.mono()
		var px := UiTheme.font_px(UiTheme.CAPTION)
		var at := centre + Vector2.from_angle(mid) * (inner_r + outer_r) * 0.5
		var w := f.get_string_size(label, HORIZONTAL_ALIGNMENT_LEFT, -1, px).x
		var base := at + Vector2(-w * 0.5, (f.get_ascent(px) - f.get_descent(px)) * 0.5)
		draw_string_outline(f, base, label, HORIZONTAL_ALIGNMENT_LEFT, -1, px, OUTLINE, Palette.FOCUS)
		draw_string(f, base, label, HORIZONTAL_ALIGNMENT_LEFT, -1, px, Palette.INK)
