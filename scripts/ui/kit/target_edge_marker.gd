class_name TargetEdgeMarker
extends Control
## ART-5 5e (round 39 `city_grid`, bible 4.5): the off-screen TARGET. When the corporation's
## Central Server (the overlay's boss marker, `CityMapOverlay.icon_pos`) is outside the map
## area this control covers, a red grease-pencil arrow sits on the area's edge pointing at it,
## with the scrawled word TARGET behind it. The arrow is the pan affordance: clicking it asks
## the host to bring the target into view (`pan_requested`, Signal Up). Nothing shows while
## the target is on screen. The clamp is pure (`edge_point`, tested headless). A view only.

## The host should centre the map on lot point `lot` (the Central Server's lot).
signal pan_requested(lot: Vector2)

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
## Controls along the area's foot (the map key, the minimap): the arrow keeps above them.
var avoid: Array[Control] = []
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
	_boss = {}
	for n: Dictionary in overlay.nodes:
		if n.has("marker") and n["marker"].get("kind") == SiteMarker.KIND_CENTRAL_SERVER:
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
	var e := edge_point(free_rect(), local, EDGE_MARGIN)
	if bool(e["inside"]):
		_show(false)
		return
	var at: Vector2 = e["at"]
	var dir: Vector2 = e["dir"]
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


## B4: the chip under the word (or over it when the word is low), kept inside the free area and
## off the arrow's box.
func _place_chip(wsize: Vector2) -> void:
	_chip.text = chip_text
	_chip.reset_size()
	var cs := _chip.get_combined_minimum_size()
	var area := free_rect()
	var word_box := Rect2(_word.position, wsize)
	var p := Vector2(word_box.get_center().x - cs.x * 0.5, word_box.end.y + CHIP_GAP)
	if p.y + cs.y > area.end.y:
		p.y = word_box.position.y - CHIP_GAP - cs.y
	var arrow_box := Rect2(_hit.position, _hit.size)
	if Rect2(p, cs).intersects(arrow_box):
		p.y = arrow_box.end.y + CHIP_GAP
	p.x = clampf(p.x, area.position.x + CHIP_GAP, maxf(area.position.x + CHIP_GAP, area.end.x - cs.x - CHIP_GAP))
	p.y = clampf(p.y, area.position.y + CHIP_GAP, maxf(area.position.y + CHIP_GAP, area.end.y - cs.y - CHIP_GAP))
	_chip.position = p
	_chip.size = cs


## B4: the chip's rect (local; empty while it does not show).
func chip_rect() -> Rect2:
	return Rect2(_chip.position, _chip.size) if _chip.visible else Rect2()


## The part of this area the arrow may sit in: above the `avoid` controls on its foot.
func free_rect() -> Rect2:
	var r := Rect2(Vector2.ZERO, size)
	var inv := get_global_transform().affine_inverse()
	for c in avoid:
		if c == null or not is_instance_valid(c) or not c.is_visible_in_tree():
			continue
		var b := inv * c.get_global_rect()
		if b.end.y >= size.y - 1.0 and b.position.y > size.y * 0.5 and b.position.y < r.end.y:
			r.size.y = b.position.y
	return r


func _show(on: bool) -> void:
	if _mark.visible == on:
		return
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
