class_name RaidBeaconLayer
extends Control
## ART-6 3A: the R3 class beacons on the raid map (bible §4.8 "station beacons", round 21
## `operators_r3`, round 22 class colours v2): over each node an operative is stationed on, the
## class-colour light cone opening from the node with the holo emblem above it and the class's
## idle loop. The art is the concept's own (`screens21.beacon`), baked unchanged by
## `tools/art_pipeline/raid/bake_beacons.py` into one strip per class in
## `assets/raid/beacons/`; the layer only picks the frame (the loop runs on `raid_beacon_idle`;
## the first frame stands still when motion is off). A child of a CityMapOverlay (it pans and
## zooms with the city); it reads the "beacon" (class id) of the overlay's socket nodes. View only.

const IDLE := &"raid_beacon_idle"
const DIR := "res://assets/raid/beacons/"
## The strip's frames, a frame's size and the pad's pixel in it (manifest.json).
const FRAMES := 16
const FRAME_PX := Vector2(220, 260)
const PAD_PX := Vector2(110, 210)
## The concept draws the beacon at map scale over a socket about SOCKET_ART_PX wide (its
## with_beacon frame); the cone's foot sits on the node, scaled to the node's socket.
const SOCKET_ART_PX := 80.0

var overlay: CityMapOverlay
var _t := 0.0
static var _strips: Dictionary = {}


func _init(p_overlay: CityMapOverlay = null) -> void:
	overlay = p_overlay
	name = "RaidBeacons"
	mouse_filter = Control.MOUSE_FILTER_IGNORE
	set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)


## The baked strip of class `class_id` (null when it was not baked).
static func strip(class_id: StringName) -> Texture2D:
	var p := DIR + String(class_id) + ".png"
	if not _strips.has(p):
		_strips[p] = load(p) if ResourceLoader.exists(p) else null
	return _strips[p]


## The frame shown `t` seconds into the loop (0 when the idle is off).
static func frame_at(t: float) -> int:
	if not Motion.live(IDLE):
		return 0
	var period := maxf(0.001, Motion.seconds(IDLE))
	return int(fposmod(t / period, 1.0) * FRAMES) % FRAMES


## The beacons shown now: [{site, class}] (tests).
func shown() -> Array[Dictionary]:
	var out: Array[Dictionary] = []
	if overlay == null:
		return out
	for n: Dictionary in overlay.nodes:
		var s: Variant = n.get("socket")
		if s is Dictionary and StringName((s as Dictionary).get("beacon", &"")) != &"":
			out.append({"site": n["id"], "class": (s as Dictionary)["beacon"]})
	return out


func _process(delta: float) -> void:
	_t += delta
	if is_visible_in_tree():
		queue_redraw()


func _draw() -> void:
	if overlay == null:
		return
	var f := frame_at(_t)
	var inv := get_global_transform().affine_inverse()
	for b in shown():
		var tex := strip(StringName(b["class"]))
		if tex == null:
			continue
		var site := StringName(b["site"])
		var at := RaidMapAnchor.site(overlay, site)
		if at.x == INF:
			continue
		# the socket's width in this layer's px (the overlay's local px, the layer's own transform)
		var r := overlay.icon_radius(overlay._node_dict(site)) * RaidMapAnchor.scale(overlay) / get_global_transform().get_scale().x
		var socket_px := RaidSocket.HALF.x * 2.0 * r
		var k := socket_px / SOCKET_ART_PX
		var foot := inv * at
		var box := Rect2(foot - PAD_PX * k, FRAME_PX * k)
		draw_texture_rect_region(tex, box, Rect2(Vector2(FRAME_PX.x * f, 0), FRAME_PX))
