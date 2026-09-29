class_name DeckFrame
extends Control
## The HQ's cyberdeck frame (ART_BIBLE §2 DECK, §11 HQ; designer ruling Q4: the full DECK
## frame): a worn-metal monitor bezel round the page, screws in its corners, a keyboard
## edge along the bottom and two cables drooping over it. The city shows through the middle
## as the rain-streaked window (CyberdeckBackground draws the city and its rain). The frame
## never sits under a control: the page is inset by `INSET_SIDE` at the sides, and the
## keyboard edge is drawn in a row of its own under the page's scroll view (`keys_row`, a
## KEYBOARD_H strip hq_scene lays out; the "more below" tag sits between them). It follows
## `target`'s rect (the page's scroll view). DECK material only: DESK_DARK / DESK_METAL, INK
## keylines, the Cell's pink power light. Deterministic (scuffs from fixed offsets, no RNG);
## static (nothing to reduce); high contrast drops the scuffs and draws heavy ink edges.
## Draws only; clicks pass.

## The bezel's width at the sides and the top, the keyboard edge's height, and the room the
## page keeps from them (px; hardware, not text: it doesn't follow the text scale).
const BEZEL := 12.0
const BEZEL_TOP := 4.0
const KEYBOARD_H := 22.0
const INSET_SIDE := 16
const INSET_BOTTOM := 6
## The metal lip inside the bezel, the corner radius and the screws (px).
const LIP := 2.0
const CORNER := 10.0
const SCREW_R := 3.5
const SCREW_INSET := 7.0
const SCREW_SLOT := 2.5
## Keyboard edge: key caps' size, gap and the lip over them (px).
const KEY := Vector2(26, 9)
const KEY_GAP := 4.0
const KEY_TOP := 7.0
## Cables: stroke width, how far they sag below their ends (px) and their sleeve length
## (a share of the cable), and the pink power light's radius.
const CABLE_W := 5.0
const CABLE_SAG := 16.0
const CABLE_STEPS := 16
const SLEEVE_SHARE := 0.12
const POWER_R := 3.0
## Scuffs on the bezel: [x share along the edge, length px] (fixed, never random).
const SCUFFS: Array[Vector2] = [Vector2(0.12, 14), Vector2(0.31, 8), Vector2(0.47, 20), Vector2(0.66, 10), Vector2(0.83, 16)]
const SCUFF_ALPHA := 0.55
## The high-contrast ink edge (px).
const HC_EDGE := 3.0

## The control whose rect the frame surrounds (the page's scroll view).
var target: Control = null:
	set(v):
		_follow(target, v)
		target = v
## The keyboard edge's own row under the page (null: the foot of `target`).
var keys_row: Control = null:
	set(v):
		_follow(keys_row, v)
		keys_row = v


func _follow(old: Control, now: Control) -> void:
	if old != null and is_instance_valid(old) and old.item_rect_changed.is_connected(queue_redraw):
		old.item_rect_changed.disconnect(queue_redraw)
	if now != null:
		now.item_rect_changed.connect(queue_redraw)
		now.visibility_changed.connect(queue_redraw)
	queue_redraw()


func _init() -> void:
	name = "DeckFrame"
	mouse_filter = Control.MOUSE_FILTER_IGNORE
	focus_mode = Control.FOCUS_NONE
	set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)


func _ready() -> void:
	Settings.changed.connect(queue_redraw)


func _local(c: Control) -> Rect2:
	return get_global_transform().affine_inverse() * c.get_global_rect()


func _keys_shown() -> bool:
	return keys_row != null and is_instance_valid(keys_row) and keys_row.is_visible_in_tree()


## The frame's outer rect (local px): the target's rect and the keyboard row under it, or
## the whole control.
func frame_rect() -> Rect2:
	if target != null and is_instance_valid(target) and target.is_inside_tree():
		var r := _local(target)
		if _keys_shown():
			r = r.merge(_local(keys_row))
		return r
	return Rect2(Vector2.ZERO, size)


## The keyboard edge's rect (local px).
func keyboard_rect() -> Rect2:
	if _keys_shown():
		return _local(keys_row)
	var r := frame_rect()
	return Rect2(r.position.x, r.end.y - KEYBOARD_H, r.size.x, KEYBOARD_H)


func _draw() -> void:
	var r := frame_rect()
	if r.size.x <= BEZEL * 4.0 or r.size.y <= KEYBOARD_H * 2.0:
		return
	var hc := Settings.high_contrast
	_draw_bezel(r, hc)
	_draw_keyboard(keyboard_rect(), hc)
	_draw_cables(r, hc)


## The monitor bezel: a DESK_DARK ring with a DESK_METAL lip, round corners, screws.
func _draw_bezel(r: Rect2, hc: bool) -> void:
	var inner := Rect2(r.position + Vector2(BEZEL, BEZEL_TOP), r.size - Vector2(BEZEL * 2.0, BEZEL_TOP + KEYBOARD_H))
	# The ring as four slabs (the middle stays open: the window on the city).
	draw_rect(Rect2(r.position, Vector2(BEZEL, r.size.y)), Palette.DESK_DARK)
	draw_rect(Rect2(Vector2(r.end.x - BEZEL, r.position.y), Vector2(BEZEL, r.size.y)), Palette.DESK_DARK)
	draw_rect(Rect2(r.position, Vector2(r.size.x, BEZEL_TOP)), Palette.DESK_DARK)
	# Round inner corners: the bezel's metal fills the corner outside a quarter circle.
	for c in [inner.position, Vector2(inner.end.x, inner.position.y)]:
		_corner(c, c == inner.position)
	var lip := Palette.INK if hc else Palette.DESK_METAL
	draw_rect(inner.grow(LIP * 0.5), lip, false, HC_EDGE if hc else LIP)
	if not hc:
		for sc in SCUFFS:
			var x := r.position.x + BEZEL * 0.5
			var y := r.position.y + r.size.y * sc.x
			draw_line(Vector2(x - 2.0, y), Vector2(x + 2.0, y + sc.y), Color(Palette.DESK_METAL, SCUFF_ALPHA), 1.0)
			draw_line(Vector2(r.end.x - x + r.position.x, y), Vector2(r.end.x - x + r.position.x - 2.0, y + sc.y), Color(Palette.DESK_METAL, SCUFF_ALPHA), 1.0)
	for p in [Vector2(r.position.x + SCREW_INSET, r.position.y + SCREW_INSET + BEZEL_TOP), Vector2(r.end.x - SCREW_INSET, r.position.y + SCREW_INSET + BEZEL_TOP),
			Vector2(r.position.x + SCREW_INSET, r.end.y - KEYBOARD_H - SCREW_INSET), Vector2(r.end.x - SCREW_INSET, r.end.y - KEYBOARD_H - SCREW_INSET)]:
		draw_circle(p, SCREW_R, Palette.DESK_METAL)
		draw_line(p - Vector2(SCREW_SLOT, SCREW_SLOT * 0.4), p + Vector2(SCREW_SLOT, SCREW_SLOT * 0.4), Palette.INK, 1.0)


## A rounded inner corner at `c` (top left when `left`): metal outside a quarter circle.
func _corner(c: Vector2, left: bool) -> void:
	var pts := PackedVector2Array([c])
	var sx := 1.0 if left else -1.0
	var centre := c + Vector2(CORNER * sx, CORNER)
	for k in 9:
		var a := PI + (PI * 0.5) * k / 8.0 if left else -PI * 0.5 + (PI * 0.5) * k / 8.0
		pts.append(centre + Vector2(cos(a), sin(a)) * CORNER)
	draw_colored_polygon(pts, Palette.DESK_DARK)


## The keyboard edge: a DESK_DARK slab, its metal lip, a row of key caps, the power light.
func _draw_keyboard(k: Rect2, hc: bool) -> void:
	draw_rect(k, Palette.DESK_DARK)
	draw_rect(Rect2(k.position, Vector2(k.size.x, LIP)), Palette.INK if hc else Palette.DESK_METAL)
	var n := floori((k.size.x - BEZEL * 2.0 + KEY_GAP) / (KEY.x + KEY_GAP))
	var x0 := k.position.x + (k.size.x - n * (KEY.x + KEY_GAP) + KEY_GAP) * 0.5
	for i in n:
		var key := Rect2(Vector2(x0 + i * (KEY.x + KEY_GAP), k.position.y + KEY_TOP), KEY)
		draw_rect(key, Palette.DESK_METAL)
		draw_rect(key, Palette.INK, false, HC_EDGE if hc else 1.0)
	draw_circle(Vector2(k.end.x - BEZEL - POWER_R * 2.0, k.position.y + KEY_TOP * 0.5 + LIP), POWER_R, Palette.CELL_PINK)


## Two cables sagging over the keyboard edge from the bezel's bottom corners.
func _draw_cables(r: Rect2, hc: bool) -> void:
	var y := r.end.y - KEYBOARD_H
	for side in [0, 1]:
		var a := Vector2(r.position.x + BEZEL * 0.5, y) if side == 0 else Vector2(r.end.x - BEZEL * 0.5, y)
		var b := a + Vector2((1.0 if side == 0 else -1.0) * r.size.x * 0.18, KEYBOARD_H * 0.5)
		var pts := PackedVector2Array()
		for i in CABLE_STEPS + 1:
			var t := float(i) / CABLE_STEPS
			pts.append(a.lerp(b, t) + Vector2(0, sin(t * PI) * CABLE_SAG * 0.5))
		draw_polyline(pts, Palette.INK, CABLE_W + 2.0, true)
		draw_polyline(pts, Palette.DESK_METAL if not hc else Palette.DESK_DARK, CABLE_W, true)
		var sleeve := pts.slice(0, maxi(2, roundi(CABLE_STEPS * SLEEVE_SHARE)))
		draw_polyline(sleeve, Palette.CELL_PINK, CABLE_W, true)
