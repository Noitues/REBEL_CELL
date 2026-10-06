class_name RaidDragPencil
extends Control
## ART-6 3A: the raid setup's card drag in grease pencil (ART_BIBLE v2 §4.8 "Card drag model";
## round 23 `02_drag_dock_preview`, `06_swap_one_motion`): the defence sticker peels and parks
## just above its hand slot (the slot stays empty), a yellow pencil arrow draws from it to the
## pointer; within reach of a node the arrow stops just outside the node's circle and the circle
## draws: yellow where it can go (with the IF PLACED terminal), red with an X where it can't
## (NO SLOT, the rules' own refusal); off the node the circle is erased and the arrow snaps back
## to the pointer. A placed defence dragged off its node (the swap) parks the same way.
##
## A layer over the DropLayer (it draws above every panel: no UI covers grease pencil). It
## only reads the DropLayer (its mode, payload, source, the target under the pointer and the
## rules' answers): every drop still goes through the DropLayer and the screen's own calls
## (ANIM-4's drag behaviour is unchanged). View only.

const ARROW := &"raid_drag_arrow"
const DOCK := &"raid_dock_circle"
const IF_PLACED := "IF PLACED" # TR
const NO_SLOT := "NO SLOT" # TR
## The parked sticker's lift above its slot (x its height) and tilt (degrees); the arrow's
## width and its bow; the dock circle's radius (x the node's rect) and width.
const PARK_LIFT := 0.62
const PARK_TILT := -3.0
const PARK_BORDER := 6.0  # the parked sticker's white border round the card (px)
const ARROW_W := 6.0
const ARROW_BOW := 0.18
const DOCK_R := 1.9
const DOCK_W := 6.0
## The IF PLACED terminal's width and its gap from the node (px at 1.0).
const TERM_W := 230.0
const TERM_GAP := 26.0

var drops: DropLayer
## Is the raid setup showing (the HQ's page)?
var active: Callable = Callable()
## (payload, site id) -> [line, ...] the IF PLACED terminal shows (the forecast's changes).
var forecast: Callable = Callable()
var _parked: VinylSticker = null
var _source: Control = null
var _dock_id: String = ""
var _dock_t: float = 0.0
var _arrow_t: float = 0.0
var _lines: Array = []
var _term: RaidTerminal = null


func _init(p_drops: DropLayer = null) -> void:
	drops = p_drops
	name = "RaidDragPencil"
	mouse_filter = Control.MOUSE_FILTER_IGNORE
	set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	MotionSkip.register_passive(self)


func _carrying() -> bool:
	if drops == null or drops.mode == DropLayer.Mode.IDLE or (active.is_valid() and not bool(active.call())):
		return false
	return String(drops.payload.get("kind", "")) in ["asset", "placed"]


## MotionSkip: the arrow or the dock circle is drawing on.
func motion_running() -> bool:
	return _carrying() and (_arrow_t < 1.0 or (_dock_id != "" and _dock_t < 1.0))


## MotionSkip: drawn.
func complete_motion() -> void:
	_arrow_t = 1.0
	_dock_t = 1.0


func _process(delta: float) -> void:
	if not _carrying():
		if _parked != null:
			_unpark()
		if _dock_id != "" or _arrow_t > 0.0:
			_dock_id = ""
			_arrow_t = 0.0
			_drop_term()
			_lay()
		return
	if _parked == null or drops.source != _source:
		_park()
	_arrow_t = _advance(_arrow_t, ARROW, delta)
	var id := drops.hover_id
	if id != _dock_id:
		_dock_id = id
		_dock_t = 0.0
		_lines = []
		_drop_term()
		if id != "" and forecast.is_valid():
			var t := drops.target(id)
			if t.get("kind", "") == "node":
				_lines = forecast.call(drops.payload, t["value"])
		_show_term()
	_dock_t = _advance(_dock_t, DOCK, delta)
	_hide_ghosts()
	_lay()


func _advance(u: float, id: StringName, delta: float) -> float:
	if not Motion.live(id):
		return 1.0
	return minf(1.0, u + delta / maxf(Motion.seconds(id), 0.001))


## The sticker peels off its slot (or its node, for a swap) and parks above the slot: 1B's
## vinyl sticker round a copy of the card (die-cut, gloss, shadow); it slaps into its spot.
func _park() -> void:
	_unpark()
	_source = drops.source
	if _source == null or not is_instance_valid(_source) or not _source.is_inside_tree():
		return
	var copy := drops.ghost_maker.call(drops.payload, _source) as Control if drops.ghost_maker.is_valid() else null
	if copy == null:
		return
	copy.mouse_filter = Control.MOUSE_FILTER_IGNORE
	copy.size = copy.get_combined_minimum_size().max(copy.size)
	var vinyl := VinylSticker.new()
	vinyl.name = "Parked"
	vinyl.shape = VinylSticker.Shape.RECT
	vinyl.stock = VinylSticker.Stock.GLOSS
	vinyl.border_px = PARK_BORDER
	vinyl.body_size = copy.size + Vector2(PARK_BORDER, PARK_BORDER) * 2.0
	vinyl.tilt_deg = PARK_TILT
	vinyl.lifted_corner = VinylSticker.Lift.TOP_RIGHT
	add_child(vinyl)
	vinyl.content_root.add_child(copy)
	copy.position = Vector2.ZERO
	vinyl.refresh()
	var slot := _source.get_global_rect()
	vinyl.global_position = Vector2(slot.get_center().x, slot.position.y - vinyl.body_rect.size.y * PARK_LIFT) - vinyl.pivot_offset
	vinyl.slap()
	_parked = vinyl


func _unpark() -> void:
	if _parked != null and is_instance_valid(_parked):
		_parked.queue_free()
	_parked = null
	_source = null


## The pointer's own sticker ghost hides while the sticker is parked (the pencil points).
func _hide_ghosts() -> void:
	for g in get_tree().root.find_children("*", "DragGhost", true, false):
		(g as CanvasItem).modulate.a = 0.0


## The parked sticker (tests).
func parked() -> Control:
	return _parked


## Where the arrow points now (global): the pointer, or the aimed target in carry.
func pointer() -> Vector2:
	if drops.mode == DropLayer.Mode.CARRY and drops.reticle_visible:
		return drops.reticle_pos
	return get_global_mouse_position()


## Lays the drag's pencil on 1B's grease pencil (RaidPencilPool, above every panel): the
## yellow arrow from the parked sticker to the pointer, and the dock circle (yellow; red with
## an X where the defence can't go) round the node in reach.
func _lay() -> void:
	if _pool == null:
		_pool = RaidPencilPool.make(self)
	_pool.begin()
	if _carrying() and _parked != null and is_instance_valid(_parked):
		var body := Rect2(_parked.global_position + _parked.body_rect.position, _parked.body_rect.size)
		var start := body.get_center() + Vector2(0, -body.size.y * 0.5)
		var end := pointer()
		var circle := Rect2()
		var valid := true
		if _dock_id != "":
			var r := drops.locate(drops.target(_dock_id))
			if r.has_area():
				circle = r
				valid = String(drops.reasons.get(_dock_id, "")) == ""
				var c := circle.get_center()
				var rad := maxf(circle.size.x, circle.size.y) * 0.5 * DOCK_R
				end = c + (start - c).normalized() * rad * 1.08
		var mid := (start + end) * 0.5 + (end - start).orthogonal() * ARROW_BOW
		var shaft := PencilShapes.bezier(start, mid, end, 24)
		_pool.stroke("arrow", PencilShapes.arrow(shaft, ARROW_W * RaidPencil.HEAD_LEN, 17), GreasePencilMark.Ink.PLAN, ARROW_W, _arrow_t, 0.0, false, 17)
		if circle.has_area():
			var c := circle.get_center()
			var rad := maxf(circle.size.x, circle.size.y) * 0.5 * DOCK_R
			var ink := GreasePencilMark.Ink.PLAN if valid else GreasePencilMark.Ink.THREAT
			var seed := _dock_id.hash()
			_pool.stroke("dock", [PencilShapes.hand_circle(c, Vector2(rad, rad * 0.68), seed)], ink, DOCK_W, _dock_t, 0.0, false, seed)
			if not valid:
				var a := rad * 0.45
				_pool.stroke("x", [PackedVector2Array([c + Vector2(-a, -a * 0.85), c + Vector2(a, a * 0.8)]),
					PackedVector2Array([c + Vector2(a, -a * 0.85), c + Vector2(-a * 0.95, a * 0.9)])], GreasePencilMark.Ink.THREAT, DOCK_W, _dock_t, 0.0, false, seed + 3)
	_pool.end()


func _exit_tree() -> void:
	if _pool != null and is_instance_valid(_pool):
		_pool.release()
	_pool = null


var _pool: RaidPencilPool = null

## The IF PLACED terminal beside a valid node (NO SLOT and the reason beside an invalid one).
func _show_term() -> void:
	if _dock_id == "":
		return
	var t := drops.target(_dock_id)
	var r := drops.locate(t)
	if not r.has_area():
		return
	var valid := String(drops.reasons.get(_dock_id, "")) == ""
	_term = RaidTerminal.new(tr(IF_PLACED) if valid else tr(NO_SLOT), Palette.GAIN if valid else Palette.HARM)
	_term.name = "IfPlaced"
	_term.mouse_filter = Control.MOUSE_FILTER_IGNORE
	_term.custom_minimum_size.x = TERM_W * Settings.text_scale
	var lines: Array = _lines if valid else [String(drops.reasons.get(_dock_id, ""))]
	for line in lines:
		var l := Label.new()
		l.text = String(line)
		l.add_theme_font_override("font", Palette.mono_arrows())
		l.add_theme_font_size_override("font_size", UiTheme.font_px(UiTheme.CAPTION))
		l.add_theme_color_override("font_color", Palette.TERMINAL_TEXT if valid else Palette.HARM)
		l.custom_minimum_size.x = (TERM_W - CrtTerminalPanel.PAD.x * 2.0) * Settings.text_scale
		UiWrap.whole_words(l)
		_term.body.add_child(l)
	add_child(_term)
	_term.size = _term.get_combined_minimum_size()
	var view := get_viewport_rect().size
	var at := r.position + Vector2(r.size.x + TERM_GAP * Settings.text_scale, -_term.size.y)
	if at.x + _term.size.x > view.x:
		at.x = r.position.x - TERM_GAP * Settings.text_scale - _term.size.x
	_term.global_position = at.clamp(Vector2.ZERO, (view - _term.size).max(Vector2.ZERO))


func _drop_term() -> void:
	if _term != null and is_instance_valid(_term):
		_term.queue_free()
	_term = null
