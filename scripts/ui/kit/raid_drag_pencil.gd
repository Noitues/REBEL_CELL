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
## bow; the dock circle's radius (x the node's rect). The wax's width is the kit's (B1b).
const PARK_LIFT := 0.62
const PARK_TILT := -3.0
const PARK_BORDER := 6.0  # the parked sticker's white border round the card (px)
const ARROW_BOW := 0.18
const DOCK_R := 1.9
## The IF PLACED terminal's width and its gap from the node (px at 1.0).
const TERM_W := 230.0
const TERM_GAP := 26.0
## Parity RAID-01 (round 40 `raid_view_v3`): the dashed PARKED zone round the parked card (its
## margin, px at 1.0; dash and gap, px; the line's width and ink) and its word.
const PARKED := "PARKED" # TR
const PARK_ZONE_MARGIN := 14.0
const PARK_ZONE_DASH := 7.0
const PARK_ZONE_W := 1.5
const PARK_ZONE_INK := Color(Palette.STICKER_DIE_CUT, 0.55)
## Parity RAID-07: the map's part, the box round the map's nodes grown by this share of its size
## each way; a pointer outside it (over a panel, the screen's corner) is off the map and the arrow
## ends on the nearest node that takes the defence instead. The map's node targets' id prefix.
const MAP_REACH_SHARE := 0.25
const MAP_NODE_PREFIX := "node:"

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
	if copy is AssetCard:
		# Parity RAID-01: the concept's card is its own die-cut sticker: the vinyl only carries its
		# motion (the slap), with no second border round it.
		vinyl.border_px = 0.0
		vinyl.corner_radius = (copy as AssetCard).die_cut_radius()
	vinyl.body_size = copy.size + Vector2(vinyl.border_px, vinyl.border_px) * 2.0
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


## Parity RAID-07: where the arrow ends with no node docked: the pointer while it is over the
## map (inside the map nodes' box grown by MAP_REACH_SHARE), else just outside the nearest map
## node that takes the defence (ties by target id), else the pointer. Returns [end, node id or ""].
func aim_end(start: Vector2, at: Vector2) -> Array:
	var box := Rect2()
	var first := true
	var best_id := ""
	var best_d := INF
	var best_r := Rect2()
	for t: Dictionary in drops.targets:
		var id := String(t["id"])
		if not id.begins_with(MAP_NODE_PREFIX):
			continue
		var r := drops.locate(t)
		if not r.has_area():
			continue
		box = r if first else box.merge(r)
		first = false
		if not drops.takes(id):
			continue
		var d := r.get_center().distance_to(at)
		if d < best_d - 0.001 or (absf(d - best_d) <= 0.001 and id < best_id):
			best_d = d
			best_id = id
			best_r = r
	if first or best_id == "" or box.grow_individual(box.size.x * MAP_REACH_SHARE, box.size.y * MAP_REACH_SHARE,
			box.size.x * MAP_REACH_SHARE, box.size.y * MAP_REACH_SHARE).has_point(at):
		return [at, ""]
	var c := best_r.get_center()
	var rad := maxf(best_r.size.x, best_r.size.y) * 0.5 * DOCK_R
	return [c + (start - c).normalized() * rad * 1.08, best_id]


## The dashed PARKED zone round the parked card (global; empty when nothing is parked).
func park_zone() -> Rect2:
	if _parked == null or not is_instance_valid(_parked):
		return Rect2()
	var body := Rect2(_parked.global_position + _parked.body_rect.position, _parked.body_rect.size)
	return body.grow(PARK_ZONE_MARGIN * Settings.text_scale)


func _draw() -> void:
	var zone := park_zone()
	if not _carrying() or not zone.has_area():
		return
	var xf := get_global_transform().affine_inverse()
	var r := Rect2(xf * zone.position, zone.size)
	var corners := [r.position, Vector2(r.end.x, r.position.y), r.end, Vector2(r.position.x, r.end.y)]
	var word := tr(PARKED)
	var font := Palette.mono()
	var fs := UiTheme.font_px(UiTheme.CAPTION)
	var ww := font.get_string_size(word, HORIZONTAL_ALIGNMENT_LEFT, -1, fs).x
	var gap := Vector2(r.get_center().x - ww * 0.5 - PARK_ZONE_DASH, r.get_center().x + ww * 0.5 + PARK_ZONE_DASH)
	for i in 4:
		var a: Vector2 = corners[i]
		var b: Vector2 = corners[(i + 1) % 4]
		if i == 0:
			# The top edge leaves room for the word.
			draw_dashed_line(a, Vector2(gap.x, a.y), PARK_ZONE_INK, PARK_ZONE_W, PARK_ZONE_DASH)
			draw_dashed_line(Vector2(gap.y, a.y), b, PARK_ZONE_INK, PARK_ZONE_W, PARK_ZONE_DASH)
		else:
			draw_dashed_line(a, b, PARK_ZONE_INK, PARK_ZONE_W, PARK_ZONE_DASH)
	draw_string(font, Vector2(r.get_center().x - ww * 0.5, r.position.y + font.get_ascent(fs) * 0.5 - font.get_descent(fs) * 0.5), word, HORIZONTAL_ALIGNMENT_LEFT, -1, fs, PARK_ZONE_INK)


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
		var aim := aim_end(start, pointer())
		var end: Vector2 = aim[0]
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
		_pool.stroke("arrow", PencilShapes.arrow(shaft, GreasePencilMark.stroke_width() * RaidPencil.HEAD_LEN, 17), GreasePencilMark.Ink.PLAN, _arrow_t, 0.0, false, 17)
		if circle.has_area():
			var c := circle.get_center()
			var rad := maxf(circle.size.x, circle.size.y) * 0.5 * DOCK_R
			var ink := GreasePencilMark.Ink.PLAN if valid else GreasePencilMark.Ink.THREAT
			var seed := _dock_id.hash()
			_pool.stroke("dock", [PencilShapes.hand_circle(c, Vector2(rad, rad * 0.68), seed)], ink, _dock_t, 0.0, false, seed)
			if not valid:
				var a := rad * 0.45
				_pool.stroke("x", [PackedVector2Array([c + Vector2(-a, -a * 0.85), c + Vector2(a, a * 0.8)]),
					PackedVector2Array([c + Vector2(a, -a * 0.85), c + Vector2(-a * 0.95, a * 0.9)])], GreasePencilMark.Ink.THREAT, _dock_t, 0.0, false, seed + 3)
	_pool.end()
	queue_redraw()


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
