class_name SpinnerMini
extends Control
## The running operative's spinner in small (Animation pass ANIM-4b): its slots as wedges
## in their slice colours with the slice icons, a cyan square where a Firmware chip is
## socketed, and SPINNER under it. Each slot has a pad (`pad(k)`) with the slot's name as
## its tooltip: the drop targets of a Firmware chip or a slice upgrade dragged in the Mainframe,
## and of a Firmware chip taken from the loot. Not a focus stop (the pad's carry reticle
## reaches the slots); view only: it shows the slots, never changes them.

## Wheel radii and the slot pads' size at scale 1 (px); SPINNER's lettering (px, grows with
## the text size up to CAPTION_MAX).
const RADIUS := 50.0
const INNER := 22.0
const PAD := 28.0
const ICON := 7.0
const FW_MARK := 7.0
const GAP := 0.04
const CAPTION_SIZE := 12
const CAPTION_MAX := 16
const CAPTION_GAP := 2.0
## The word under the wheel (a key, translated where drawn).
const CAPTION := "SPINNER" # TR

var slices: Array[StringName] = []
var firmware: Array[StringName] = []
var lookup: ContentLookup
var _pads: Array[Control] = []


func _init(p_slices: Array[StringName], p_firmware: Array[StringName], p_lookup: ContentLookup, tips: Array = []) -> void:
	name = "SpinnerMini"
	slices = p_slices
	firmware = p_firmware
	lookup = p_lookup
	mouse_filter = Control.MOUSE_FILTER_IGNORE
	focus_mode = Control.FOCUS_NONE
	custom_minimum_size = Vector2(RADIUS * 2.0, RADIUS * 2.0 + CAPTION_GAP + _caption_height())
	for k in slices.size():
		var pad := Control.new()
		pad.name = "SlotPad%d" % k
		pad.size = Vector2(PAD, PAD)
		pad.custom_minimum_size = Vector2(PAD, PAD)
		pad.mouse_filter = Control.MOUSE_FILTER_PASS
		pad.focus_mode = Control.FOCUS_NONE
		pad.tooltip_text = String(tips[k]) if k < tips.size() else ""
		add_child(pad)
		_pads.append(pad)
	_place()


## Slot `k`'s pad (null when there is no such slot).
func pad(k: int) -> Control:
	return _pads[k] if k >= 0 and k < _pads.size() else null


## The wheel's centre (local).
func centre() -> Vector2:
	return Vector2(size.x * 0.5 if size.x > 0.0 else RADIUS, RADIUS)


## Middle angle of slot `k` (slot order as the spinner view and combat: +1 anticlockwise).
func angle(k: int) -> float:
	return -PI * 0.5 - TAU * k / maxf(1.0, slices.size())


func _notification(what: int) -> void:
	if what == NOTIFICATION_RESIZED:
		_place()


func _place() -> void:
	var mid := (RADIUS + INNER) * 0.5
	for k in _pads.size():
		_pads[k].position = centre() + Vector2(cos(angle(k)), sin(angle(k))) * mid - _pads[k].size * 0.5
	queue_redraw()


func _caption_height() -> float:
	return Palette.mono().get_height(_caption_size())


func _caption_size() -> int:
	return mini(CAPTION_MAX, roundi(CAPTION_SIZE * Settings.text_scale))


func _draw() -> void:
	var c := centre()
	var n := slices.size()
	draw_circle(c, RADIUS + 3.0, Color(0, 0, 0, 0.55))
	for k in n:
		var sd := lookup.get_content(slices[k]) as SliceData if lookup != null else null
		var type := sd.slice_type if sd != null else RC.SliceType.MISS
		var col := Palette.slice_color(type)
		var a0 := angle(k) - PI / n + GAP
		var a1 := angle(k) + PI / n - GAP
		var pts := PackedVector2Array()
		for q in 9:
			var a := lerpf(a0, a1, q / 8.0)
			pts.append(c + Vector2(cos(a), sin(a)) * RADIUS)
		for q in 9:
			var a := lerpf(a1, a0, q / 8.0)
			pts.append(c + Vector2(cos(a), sin(a)) * INNER)
		draw_colored_polygon(pts, Color(col, 0.55) if type != RC.SliceType.MISS else Color(col, 0.22))
		pts.append(pts[0])
		draw_polyline(pts, col.lightened(0.3), 1.2, true)
		var am := angle(k)
		SliceIcon.draw_on_slice(self, c + Vector2(cos(am), sin(am)) * (RADIUS + INNER) * 0.5, ICON, type, col)
		if k < firmware.size() and firmware[k] != &"":
			var at := c + Vector2(cos(am), sin(am)) * (INNER + FW_MARK * 0.5)
			draw_rect(Rect2(at - Vector2.ONE * FW_MARK * 0.5, Vector2.ONE * FW_MARK), Palette.NET_CYAN)
	draw_circle(c, INNER - 3.0, Palette.NIGHT_SKY)
	var fs := _caption_size()
	var font := Palette.mono()
	draw_string(font, Vector2(0, RADIUS * 2.0 + CAPTION_GAP + font.get_ascent(fs)), tr(CAPTION), HORIZONTAL_ALIGNMENT_CENTER, size.x, fs, Palette.TERMINAL_TEXT)
