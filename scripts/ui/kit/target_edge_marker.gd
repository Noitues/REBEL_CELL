class_name TargetEdgeMarker
extends Control
## ART-5 5e (round 39 `city_grid`, bible 4.5): the off-screen TARGET. When the corporation's
## Central Server (the overlay's boss marker, `CityMapOverlay.icon_pos`; B3 b: on the netrun
## route, the node marked `target`, the run's final Rack) is outside the map
## area this control covers, a red grease-pencil arrow sits on the area's edge pointing at it,
## with the scrawled word TARGET behind it. The arrow is the pan affordance: clicking it asks
## the host to bring the target into view (`pan_requested`, Signal Up). Nothing shows while
## the target is on screen. The clamp is pure (`edge_point`, tested headless). A view only.

## The host should centre the map on lot point `lot` (the Central Server's lot).
signal pan_requested(lot: Vector2)
## B3 c: the arrow showed (`on`) or hid: the host hides the TARGET's own circle while it shows.
signal showing_changed(on: bool)

## The arrow's tip keeps this far inside the area's edge (px); its shaft and head (px).
const EDGE_MARGIN := 46.0
const SHAFT_PX := 64.0
const HEAD_PX := 20.0
const SEED := 352
## Where the word sits behind the arrow's tail (px along the arrow, back from the tail) and
## the clickable box round the arrow (px).
const WORD_BACK := 30.0
const HIT_PX := 96.0
## Points move this far (px) before the strokes are drawn again.
const MOVE_EPS := 1.0

var overlay: CityMapOverlay = null
## B4 (round 44 `hq_idle.png`): the boss chip's words beside the off-screen arrow ("CENTRAL
## SERVER // EXPLOITS 1/3", translated; "" = no chip), set by the page. It sits under the
## scrawled word, clear of the pencil, kept inside the area.
var chip_text: String = "":
	set(v):
		chip_text = v
		if _chip != null:
			_chip.text = v
var _chip: Label = null
## B4: the chip's gap under the word (px).
const CHIP_GAP := 8.0
## G2R-2: room kept round a Site marker (px), and the arrow's swing off the boss's line.
const MARKER_CLEAR := 6.0
const SWING_STEP_DEG := 6.0
const SWING_STEPS := 12
## Controls along the area's foot (the map key, the minimap): the arrow keeps above them.
var avoid: Array[Control] = []
## G2R-2: the part of the screen the arrow, word and chip keep inside: func() -> Rect2 (global px;
## empty: no limit).
var limit: Callable = Callable()
## B3 c: controls drawn over the area (the top bar): the TARGET counts as off frame when any part
## of it sits under one, and the arrow keeps off them.
var covers: Array[Control] = []
## G2R2-1 (standing rule: no UI over grease pencil): the page's panels (hand, tabs, card column,
## work order, verb, key, minimap). The TARGET's pencil (circle, word) counts as off frame when
## any part of it sits under one, and the edge arrow shows instead.
var panels: Array[Control] = []
var _mark: GreasePencilMark
var _word: GreasePencilWord
var _hit: Control
var _drawn: Array = []
var _boss: Dictionary = {}


## A marker over the area of `p_overlay`'s map it is added to (full rect of its parent).
static func make(p_overlay: CityMapOverlay) -> TargetEdgeMarker:
	var m := TargetEdgeMarker.new()
	m.name = "TargetEdgeMarker"
	m.overlay = p_overlay
	return m


## Where the off-screen arrow sits for a target at `p` seen from inside `rect`: {"inside"
## (true when `p` is in `rect`: the target shows, no arrow), "at" (the arrow's tip, on the
## shrunk rect's edge, on the line from its centre to `p`), "dir" (unit, the tip's heading)}.
static func edge_point(rect: Rect2, p: Vector2, margin: float) -> Dictionary:
	var inner := rect.grow(-margin)
	if inner.size.x <= 0.0 or inner.size.y <= 0.0:
		inner = Rect2(rect.get_center(), Vector2.ZERO)
	if rect.has_point(p) or not p.is_finite():
		return {"inside": true, "at": p, "dir": Vector2.ZERO}
	var c := inner.get_center()
	var d := p - c
	var half := inner.size * 0.5
	var t := INF
	if absf(d.x) > 0.0:
		t = minf(t, half.x / absf(d.x))
	if absf(d.y) > 0.0:
		t = minf(t, half.y / absf(d.y))
	t = minf(t, 1.0)
	return {"inside": false, "at": c + d * t, "dir": d.normalized()}


func _init() -> void:
	mouse_filter = Control.MOUSE_FILTER_IGNORE
	set_anchors_preset(Control.PRESET_FULL_RECT)
	_mark = GreasePencilMark.new()
	_mark.name = "Arrow"
	_mark.ink = GreasePencilMark.Ink.THREAT
	_mark.seed = SEED
	add_child(_mark)
	_word = GreasePencilWord.new()
	_word.name = "Word"
	_word.ink = GreasePencilMark.Ink.THREAT
	add_child(_word)
	_hit = Control.new()
	_hit.name = "Hit"
	_hit.size = Vector2(HIT_PX, HIT_PX)
	_hit.mouse_filter = Control.MOUSE_FILTER_STOP
	_hit.mouse_default_cursor_shape = Control.CURSOR_POINTING_HAND
	_hit.gui_input.connect(_on_hit_input)
	add_child(_hit)
	_chip = Label.new()
	_chip.name = "Chip"
	_chip.auto_translate_mode = Node.AUTO_TRANSLATE_MODE_DISABLED
	_chip.mouse_filter = Control.MOUSE_FILTER_IGNORE
	_chip.add_theme_font_override("font", Palette.mono())
	_chip.add_theme_font_size_override("font_size", UiTheme.font_px(UiTheme.CAPTION))
	_chip.add_theme_color_override("font_color", Palette.RESIST_GOLD)
	_chip.add_theme_stylebox_override("normal", UiTheme.box(Color(Palette.NIGHT_SKY, 0.92), Palette.RESIST_GOLD, 1, 8, 3))
	add_child(_chip)
	_show(false)


func _ready() -> void:
	_word.text = CityMapOverlay.tr_word("TARGET")
	_hit.tooltip_text = CityMapOverlay.tr_word("Central Server: the corporation's core")


## True while the arrow shows (the target is off this area).
func showing() -> bool:
	return _mark.visible


## The arrow's tip (local px) when it shows.
func tip() -> Vector2:
	return _drawn[0] if not _drawn.is_empty() else Vector2(INF, INF)


func _process(_delta: float) -> void:
	refresh()


## Works out the boss's place and shows, moves or hides the arrow.
func refresh() -> void:
	if overlay == null or not is_instance_valid(overlay) or overlay.city == null:
		_show(false)
		return
	if overlay.raid_lens:
		_show(false)  # RAID-FIX C1: no player-target red during a raid
		return
	_boss = {}
	for n: Dictionary in overlay.nodes:
		if (n.has("marker") and n["marker"].get("kind") == SiteMarker.KIND_CENTRAL_SERVER) or bool(n.get("target", false)):
			_boss = n
			break
	if _boss.is_empty():
		_show(false)
		return
	var p := overlay.icon_pos(_boss)
	if not p.is_finite():
		_show(false)
		return
	var g := overlay.get_global_transform() * p
	var local := get_global_transform().affine_inverse() * g
	var free := free_rect()
	var seen := free_rect(false)  # the TARGET shows where the map does; the arrow stands in `free`
	# B3 c: the whole TARGET (its pencil circle, `target_reach` on the overlay) must be in frame.
	var reach := 0.0
	if overlay.has_method(&"target_reach"):
		reach = float(overlay.call(&"target_reach", _boss)) * overlay.get_global_transform().get_scale().x / maxf(get_global_transform().get_scale().x, 0.001)
	if seen.grow(-reach).has_point(local) and not _pencil_under_panel(local, reach):
		_show(false)
		return
	var e := edge_point(free, local, EDGE_MARGIN)
	if bool(e["inside"]):
		# Partly under a cover or past the edge: the arrow stands just inside, pointing out.
		var c := free.get_center()
		var d := (local - c).normalized() if local != c else Vector2.UP
		var t := edge_point(free, c + d * (free.size.length() + reach), EDGE_MARGIN)
		e = t
	var at: Vector2 = e["at"]
	var dir: Vector2 = e["dir"]
	# G2R-2: the arrow (and its word and chip) never stand on a Site marker: it swings round
	# the area's centre, off the boss's own line, to the nearest edge spot clear of them.
	var spot := _clear_spot(free, local, at, dir, reach)
	at = spot["at"]
	dir = spot["dir"]
	if _drawn.is_empty() or (_drawn[0] as Vector2).distance_to(at) > MOVE_EPS or (_drawn[1] as Vector2).distance_to(dir) > 0.01:
		_drawn = [at, dir]
		_mark.clear()
		var tail := at - dir * SHAFT_PX
		for s in PencilShapes.arrow(PackedVector2Array([tail, tail.lerp(at, 0.5), at]), HEAD_PX, SEED):
			_mark.add_stroke(s)
		var wsize := _word.global_rect().size
		_word.position = tail - dir * WORD_BACK - wsize * 0.5
		_hit.position = at - dir * SHAFT_PX * 0.5 - _hit.size * 0.5
		_place_chip(wsize)
	_show(true)
	_publish_pencil()


## B4: the chip under the word (or over it when the word is low), kept inside the free area and
## off the arrow's box.
func _place_chip(wsize: Vector2) -> void:
	_chip.text = chip_text
	_chip.reset_size()
	var cs := _chip.get_combined_minimum_size()
	_chip.position = _chip_spot(cs, Rect2(_word.position, wsize), Rect2(_hit.position, _hit.size))
	_chip.size = cs


## The chip's position for size `cs` under `word_box` (see `_place_chip`), off `arrow_box`.
func _chip_spot(cs: Vector2, word_box: Rect2, arrow_box: Rect2) -> Vector2:
	var area := free_rect()
	var p := Vector2(word_box.get_center().x - cs.x * 0.5, word_box.end.y + CHIP_GAP)
	if p.y + cs.y > area.end.y:
		p.y = word_box.position.y - CHIP_GAP - cs.y
	if Rect2(p, cs).intersects(arrow_box):
		p.y = arrow_box.end.y + CHIP_GAP
	p.x = clampf(p.x, area.position.x + CHIP_GAP, maxf(area.position.x + CHIP_GAP, area.end.x - cs.x - CHIP_GAP))
	p.y = clampf(p.y, area.position.y + CHIP_GAP, maxf(area.position.y + CHIP_GAP, area.end.y - cs.y - CHIP_GAP))
	return p


## G2R-2: the Site markers' rects (icons and tier pips; the name labels yield to the pencil, G2R2-1; local px, MARKER_CLEAR
## round) the arrow, its word and its chip keep off.
func _marker_rects() -> Array[Rect2]:
	var out: Array[Rect2] = []
	var inv := get_global_transform().affine_inverse()
	for r in LegendSpot.node_rects(overlay, false):
		out.append((inv * r).grow(MARKER_CLEAR))
	return out


## G2R-2: where the arrow stands: {"at", "dir"} for the boss at `local`. The line from the area's
## centre to the boss gives the first spot (`at`, `dir`); when the arrow, its word or its chip
## would cover a Site marker, the line swings away by SWING_STEP_DEG steps (either way, up to
## SWING_STEPS) to the first spot clear of them, the arrow pointing from there at the boss.
func _clear_spot(free: Rect2, local: Vector2, at: Vector2, dir: Vector2, reach: float) -> Dictionary:
	var markers := _marker_rects()
	if markers.is_empty() or not _covers(markers, at, dir):
		return {"at": at, "dir": dir}
	var c := free.get_center()
	var d0 := (local - c).normalized() if local != c else Vector2.UP
	for i in range(1, SWING_STEPS + 1):
		for sign in [1.0, -1.0]:
			var d := d0.rotated(deg_to_rad(SWING_STEP_DEG * i) * sign)
			var t := edge_point(free, c + d * (free.size.length() + reach), EDGE_MARGIN)
			var p: Vector2 = t["at"]
			var heading := (local - p).normalized() if local != p else d
			if not _covers(markers, p, heading):
				return {"at": p, "dir": heading}
	return {"at": at, "dir": dir}


## True when the arrow ending at `tip` heading `heading` (shaft, head, word and chip) touches any of `rects`.
func _covers(rects: Array[Rect2], tip: Vector2, heading: Vector2) -> bool:
	var tail := tip - heading * SHAFT_PX
	var arrow := Rect2(tail, Vector2.ZERO).expand(tip).grow(HEAD_PX)
	var wsize := _word.global_rect().size
	var word := Rect2(tail - heading * WORD_BACK - wsize * 0.5, wsize)
	var chip_box := Rect2()
	if chip_text != "":
		var cs := _chip.get_combined_minimum_size()
		chip_box = Rect2(_chip_spot(cs, word, arrow), cs)
	for r in rects:
		if r.intersects(arrow) or r.intersects(word) or (chip_box.has_area() and r.intersects(chip_box)):
			return true
	return false


## B4: the chip's rect (local; empty while it does not show).
func chip_rect() -> Rect2:
	return Rect2(_chip.position, _chip.size) if _chip.visible else Rect2()


## The part of this area the arrow may sit in: above the `avoid` controls on its foot, and (with
## `limited`) inside `limit` (G2R-2: the HQ's free part, so the chip never runs under the Site card).
func free_rect(limited: bool = true) -> Rect2:
	var r := Rect2(Vector2.ZERO, size)
	var inv := get_global_transform().affine_inverse()
	if limited and limit.is_valid():
		var g: Rect2 = limit.call()
		var l := inv * g
		if g.has_area() and r.intersection(l).has_area():
			r = r.intersection(l)
	for c in covers:
		if c == null or not is_instance_valid(c) or not c.is_visible_in_tree():
			continue
		var b := inv * c.get_global_rect()
		if b.position.y <= r.position.y + 1.0 and b.end.y > r.position.y and b.end.y < size.y * 0.5:
			r = Rect2(Vector2(r.position.x, b.end.y), Vector2(r.size.x, r.end.y - b.end.y))
	for c in avoid:
		if c == null or not is_instance_valid(c) or not c.is_visible_in_tree():
			continue
		var b := inv * c.get_global_rect()
		if b.end.y >= size.y - 1.0 and b.position.y > size.y * 0.5 and b.position.y < r.end.y:
			r.size.y = b.position.y
	return r


## G2R2-1: true when the TARGET's circle (radius `reach` round `local`) or its word sits under
## any of the `panels` (local px).
func _pencil_under_panel(local: Vector2, reach: float) -> bool:
	var inv := get_global_transform().affine_inverse()
	var boxes: Array[Rect2] = [Rect2(local - Vector2(reach, reach), Vector2(reach, reach) * 2.0)]
	if overlay != null and not _boss.is_empty():
		var l: Dictionary = overlay.boss_layout(_boss)
		if not l.is_empty():
			var ox := overlay.get_global_transform()
			boxes.append(inv * (ox * (l["word"] as Rect2)))
			boxes.append(inv * (ox * (l["circle"] as Rect2)))
	for c in panels:
		if c == null or not is_instance_valid(c) or not c.is_visible_in_tree() or c.size == Vector2.ZERO:
			continue
		var b := inv * c.get_global_rect()
		for r in boxes:
			if b.intersects(r):
				return true
	return false


## G2R2-1: the arrow, its word and its chip as drawn (global px; empty while the arrow hides).
func pencil_rects() -> Array[Rect2]:
	var rects: Array[Rect2] = []
	if _drawn.is_empty() or not _mark.visible:
		return rects
	var at: Vector2 = _drawn[0]
	var dir: Vector2 = _drawn[1]
	var tail := at - dir * SHAFT_PX
	var x := get_global_transform()
	rects.append(x * Rect2(tail, Vector2.ZERO).expand(at).grow(HEAD_PX))
	rects.append(_word.global_rect())  # the word's origin is its baseline: its own rect, as drawn
	if _chip.visible and _chip.size.x > 0.0:
		rects.append(x * Rect2(_chip.position, _chip.size))
	return rects


## G2R2-1: the arrow, its word and its chip are pencil too: the overlay's Site name labels make way
## for them, and take their places back when the arrow hides.
func _publish_pencil() -> void:
	if overlay != null and is_instance_valid(overlay):
		overlay.set_pencil_rects(pencil_rects())


func _show(on: bool) -> void:
	if _mark.visible == on:
		return
	if not on and overlay != null and is_instance_valid(overlay):
		overlay.set_pencil_rects([] as Array[Rect2])
	showing_changed.emit(on)
	if overlay != null and is_instance_valid(overlay):
		overlay.target_hidden = on  # G2R2-1: the arrow speaks for the TARGET: its circle, word and chip hide
	_mark.visible = on
	_word.visible = on
	_hit.visible = on
	_chip.visible = on and chip_text != ""
	if not on:
		_drawn = []


func _on_hit_input(event: InputEvent) -> void:
	var mb := event as InputEventMouseButton
	if mb != null and mb.pressed and mb.button_index == MOUSE_BUTTON_LEFT and not _boss.is_empty():
		pan_requested.emit(Vector2(overlay.lot_of(_boss["id"])) + Vector2(0.5, 0.5))
		accept_event()
