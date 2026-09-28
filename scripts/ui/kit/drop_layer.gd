class_name DropLayer
extends Control
## Drag and drop between places (Animation pass ANIM-4): the HQ, the City Grid, the raid
## setup and the loadout view move items (defence assets, operatives, recruits, boosts,
## ring segments) onto targets; since ANIM-4b the netrun too (Modem purchases, deck cards
## onto the shredder, loot, event rewards, raid assets). A full-screen layer over its screen: it knows the
## screen's drop targets, draws their pulses, the pad reticle and the no-entry mark, and
## flies copies of the items (land, glide home). View only: a drop is an intent; the layer
## emits `dropped` and the screen applies it with the same call its buttons make (Signal
## Up, Call Down). Whether a target takes an item comes from the screen's `check`, which
## asks the rules themselves (never a copy of them).
##
## Three ways to move an item, all ending in the same `dropped` / `refused`:
## - Mouse drag: Godot's drag from a source (DragGhost preview, as ANIM-3's cards); the
##   layer takes the drop while a drag is on.
## - Carry (keys, pad, and click-select-click): pick the item up (the pick-up key on a
##   focused source, A on an item that only moves, a click on one), aim with the arrows or
##   D-pad (a reticle glides between the targets; the item follows), drop with accept or a
##   click, cancel with cancel / right click / the pick-up key again.
## - Buttons stay as they were (they are the button path each drop mirrors).
## Under reduce effects and headless every motion shows its end state at once.

## A valid drop: the screen applies `payload` to `target` ({id, kind, value, ...}).
signal dropped(payload: Dictionary, target: Dictionary)
## A drop on a target that doesn't take the item: nothing changes; `reason` says why.
signal refused(payload: Dictionary, target: Dictionary, reason: String)
## Carry mode began (true) or ended (false): the screen swaps its pad prompts.
signal carry_changed(carrying: bool)

enum Mode { IDLE, DRAG, CARRY }

## Node meta holding a source's payload (its focus owner or an ancestor carries it).
const SOURCE_META := &"drop_source"
## check() result for a target that is not offered for this item (not lit, not aimed: a
## drop there is a drop on nothing).
const SKIP := "-"
## The source dims while its item is away (alpha).
const SOURCE_DIM := 0.4
## Target brackets: arm length and line width (px), and how far out from the target.
const BRACKET := 12.0
const BRACKET_W := 3.0
const BRACKET_OUT := 4.0
## Pad reticle: least radius, room beyond the target's half size, arc half-width (rad).
const RETICLE_MIN := 18.0
const RETICLE_PAD := 6.0
const RETICLE_ARC := 0.35
const RETICLE_W := 2.5
## The no-entry mark: radius and line width (px).
const MARK_RADIUS := 14.0
const MARK_W := 4.0
## The stamp ring's line width and its starting radius share of the landing copy.
const STAMP_W := 3.0
const STAMP_START := 0.35
## Shred strips (ANIM-4b): how many, their width, share of the card's width they span,
## each one's share of the full length, their slant (px per strip from the middle) and how
## much longer than the feed they stay (they fade over the rest).
const STRIP_COUNT := 6
const STRIP_W := 3.0
const STRIP_SPAN := 0.6
const STRIP_LENGTHS: Array[float] = [0.8, 1.0, 0.7, 0.95, 0.75, 0.9]
const STRIP_SLANT := 0.8
const STRIP_HOLD := 1.6
## The carried item sits this far up-right of the aimed target's corner (px).
const CARRY_OFFSET := Vector2(6, -6)

## (payload, target) -> "" (takes it), a reason (refuses), or SKIP (not offered).
var check: Callable = Callable()
## (payload, source) -> a fresh Control showing the item (ghosts and flying copies).
var ghost_maker: Callable = Callable()

## The screen's targets: {id, accepts: Array[String], kind, value, locate: Callable ->
## Rect2 (global; empty = not on screen), aimable: bool}.
var targets: Array[Dictionary] = []
var mode: int = Mode.IDLE
var payload: Dictionary = {}
var source: Control = null
## Target id -> check() result for the item in hand.
var reasons: Dictionary = {}
## The target under the pointer (or aimed), "" for none.
var hover_id: String = ""
## Carry: the aimable offered targets in screen order, and the aimed one.
var aim_list: Array[String] = []
var aim_index: int = -1
## Unhovered valid targets pulse between 1 and `drop_zone_pulse`'s amplitude.
var pulse: float = 1.0
var reticle_visible: bool = false
var reticle_pos: Vector2 = Vector2.ZERO
var reticle_r: float = RETICLE_MIN
var reticle_pop: float = 0.0
## Flights in the air: {node, tween, kind ("land", "home", "buy"), on_done, reveal}.
var flights: Array[Dictionary] = []
## No-entry marks and stamp rings: {kind, at (global), age, dur, ...}.
var sprites: Array[Dictionary] = []
## The last drop's outcome ("dropped", "refused", "cancel"), for tests.
var last_outcome: String = ""
## The last landing flight ({} when motion didn't play): the screen holds the real item
## back until it lands (`reveal_on_land`).
var last_flight: Dictionary = {}

var _source_rect: Rect2 = Rect2()
var _source_alpha: float = 1.0
var _pulse_tween: Tween = null
var _reticle_tween: Tween = null
var _carry_ghost: DragGhost = null


func _init() -> void:
	name = "DropLayer"
	set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	mouse_filter = Control.MOUSE_FILTER_IGNORE
	focus_mode = Control.FOCUS_NONE
	set_process(false)


# --- The screen's side --------------------------------------------------------------------

## Adds a drop target (see `targets`). `accepts` lists the payload kinds it takes. With
## `lands` false the screen plays the landing itself (a raid node's asset drop), so no
## copy flies there.
func add_target(id: String, accepts: Array, kind: String, value: Variant, locate: Callable, aimable: bool = true, lands: bool = true) -> void:
	targets.append({"id": id, "accepts": accepts, "kind": kind, "value": value, "locate": locate, "aimable": aimable, "lands": lands})


## A target locator for `control`: its global rect while it is on screen, cut to the part
## its scroll containers show.
static func rect_of(control: Control) -> Callable:
	var ref: WeakRef = weakref(control)
	return func() -> Rect2:
		var c: Control = ref.get_ref()
		if c == null or not c.is_inside_tree() or c.is_queued_for_deletion() or not c.is_visible_in_tree():
			return Rect2()
		var r := c.get_global_rect()
		var up := c.get_parent()
		while up != null:
			if up is ScrollContainer:
				r = r.intersection((up as Control).get_global_rect())
			up = up.get_parent()
		return r


## Makes `handle` a drag source of `payload` (a dictionary with at least "kind"): a mouse
## drag from it picks the item up. `meta_on` (default `handle`) is the control whose focus
## (or a focused control inside it) lets the pick-up key take the item. With
## `press_carries`, a press of `handle` (a button) or a click on it picks the item up too.
func add_source(handle: Control, p_payload: Dictionary, press_carries: bool = false, meta_on: Control = null) -> void:
	var holder := meta_on if meta_on != null else handle
	var entry := p_payload.duplicate()
	entry["layer"] = get_instance_id()
	holder.set_meta(SOURCE_META, entry)
	handle.set_drag_forwarding(func(_at: Vector2) -> Variant: return begin_drag(holder, entry), Callable(), Callable())
	if press_carries:
		if handle is BaseButton:
			(handle as BaseButton).pressed.connect(func() -> void: start_carry(holder))
		else:
			handle.gui_input.connect(func(ev: InputEvent) -> void:
				if ev is InputEventMouseButton and not ev.pressed and (ev as InputEventMouseButton).button_index == MOUSE_BUTTON_LEFT and mode == Mode.IDLE:
					start_carry(holder))


## Forgets the screen's targets and ends any drag or carry (a page rebuilt). Flights in
## the air keep going.
func reset() -> void:
	if mode != Mode.IDLE:
		_restore_source(source)
		_end()
	targets.clear()


# --- Picking up ---------------------------------------------------------------------------

## A mouse drag leaves `holder` with `p_payload` (the drag forwarding calls this; `home` is
## where a cancelled item glides back to, the holder's rect by default). Returns the drag
## data, or null when nothing can be dragged now.
func begin_drag(holder: Control, p_payload: Dictionary, home: Rect2 = Rect2(), preview_from: Control = null) -> Variant:
	if p_payload.is_empty():
		return null
	finish_all()
	if mode != Mode.IDLE:
		_end()
	var from := preview_from if preview_from != null else holder
	# The preview exists only inside Godot's own drag (tests and demos start one directly).
	if from != null and from.is_inside_tree() and from.get_viewport().gui_is_dragging():
		var ghost := _ghost(p_payload, holder)
		if ghost != null:
			from.set_drag_preview(DragGhost.new(ghost))
	_begin(holder, p_payload, Mode.DRAG, home)
	return {"drop_layer": get_instance_id(), "payload": p_payload}


## Picks up the item of source `holder` for keys, pad or clicks (carry mode). The aim
## starts on the target whose value is the payload's "prefer" when it takes the item, else
## on the first valid one; without `aim` nothing is aimed until the pointer moves (the
## frame-capture demos drive a pointer with `point_at`).
func start_carry(holder: Control, aim: bool = true) -> void:
	if holder == null or not holder.has_meta(SOURCE_META):
		return
	finish_all()
	if mode != Mode.IDLE:
		_end()
	var p: Dictionary = holder.get_meta(SOURCE_META)
	_begin(holder, p, Mode.CARRY)
	var start := -1
	for i in aim_list.size():
		var t := target(aim_list[i])
		if String(reasons.get(t["id"], "")) != "":
			continue
		if p.has("prefer") and t["value"] == p["prefer"]:
			start = i
			break
		if start < 0:
			start = i
	var ghost := _ghost(p, holder)
	if ghost != null:
		_carry_ghost = DragGhost.new(ghost)
		add_child(_carry_ghost)
		_carry_ghost.global_position = _source_rect.get_center()
	carry_changed.emit(true)
	if aim:
		_aim(start if start >= 0 else (0 if not aim_list.is_empty() else -1), true)


func _begin(holder: Control, p: Dictionary, p_mode: int, home: Rect2 = Rect2()) -> void:
	payload = p
	source = holder
	mode = p_mode
	last_outcome = ""
	_source_rect = home if home.has_area() else (holder.get_global_rect() if holder != null and holder.is_inside_tree() else Rect2())
	reasons.clear()
	for t in targets:
		if (t["accepts"] as Array).has(String(p.get("kind", ""))):
			reasons[t["id"]] = String(check.call(p, t)) if check.is_valid() else ""
	aim_list = _aim_order()
	aim_index = -1
	hover_id = ""
	if holder != null and is_instance_valid(holder):
		_source_alpha = holder.modulate.a
		Motion.pop(holder, &"drag_pickup")
		holder.modulate.a = SOURCE_DIM
	_start_pulse()
	mouse_filter = Control.MOUSE_FILTER_STOP if mode == Mode.DRAG else Control.MOUSE_FILTER_IGNORE
	set_process(true)
	queue_redraw()


## The aimable offered targets on screen, left to right then top to bottom (ties by id).
func _aim_order() -> Array[String]:
	var keyed: Array = []
	for t in targets:
		if not reasons.has(t["id"]) or String(reasons[t["id"]]) == SKIP or not bool(t["aimable"]):
			continue
		var r := locate(t)
		if not r.has_area():
			continue
		keyed.append([r.get_center(), String(t["id"])])
	keyed.sort_custom(func(a: Array, b: Array) -> bool:
		var pa: Vector2 = a[0]
		var pb: Vector2 = b[0]
		if not is_equal_approx(pa.x, pb.x):
			return pa.x < pb.x
		if not is_equal_approx(pa.y, pb.y):
			return pa.y < pb.y
		return String(a[1]) < String(b[1]))
	var out: Array[String] = []
	for k in keyed:
		out.append(String(k[1]))
	return out


# --- Aiming and letting go ----------------------------------------------------------------

## Target `id`, or {}.
func target(id: String) -> Dictionary:
	for t in targets:
		if t["id"] == id:
			return t
	return {}


## Where target `t` is on screen now (global; empty when it is not).
func locate(t: Dictionary) -> Rect2:
	var f: Callable = t.get("locate", Callable())
	return f.call() if f.is_valid() else Rect2()


## True when target `id` is offered for the item in hand (lit or refusing).
func offered(id: String) -> bool:
	return reasons.has(id) and String(reasons[id]) != SKIP


## True when target `id` takes the item in hand.
func takes(id: String) -> bool:
	return reasons.has(id) and String(reasons[id]) == ""


## The offered target under global point `at` (the smallest when they nest), or {}.
func target_at(at: Vector2) -> Dictionary:
	var best := {}
	var best_area := INF
	for t in targets:
		if not offered(t["id"]):
			continue
		var r := locate(t)
		if r.has_area() and r.has_point(at) and r.get_area() < best_area:
			best = t
			best_area = r.get_area()
	return best


## Carry with a pointer: the item follows `at` (global) and the target under it is aimed
## (the reticle glides to it; off every target, nothing is aimed).
func point_at(at: Vector2) -> void:
	if mode != Mode.CARRY:
		return
	if _carry_ghost != null:
		_carry_ghost.global_position = at
	var t := target_at(at)
	var id := String(t.get("id", ""))
	if id != hover_id:
		hover_id = id
		aim_index = aim_list.find(id)
		if t.is_empty():
			reticle_visible = false
		else:
			_reticle_to(locate(t), false)
	queue_redraw()


## Carry: aims the next (+1) or previous (-1) target in screen order.
func step_aim(step: int) -> void:
	if mode != Mode.CARRY or aim_list.is_empty():
		return
	_aim(posmod(aim_index + step, aim_list.size()))


## The aimed target in carry mode, or {}.
func aimed() -> Dictionary:
	return target(aim_list[aim_index]) if aim_index >= 0 and aim_index < aim_list.size() else {}


func _aim(index: int, instant: bool = false) -> void:
	aim_index = index
	var t := aimed()
	hover_id = String(t.get("id", ""))
	var r := locate(t) if not t.is_empty() else Rect2()
	if r.has_area():
		_reticle_to(r, instant)
		if _carry_ghost != null:
			var at := r.position + Vector2(r.size.x, 0) + CARRY_OFFSET
			if instant:
				_carry_ghost.global_position = at
			else:
				Motion.run(&"drag_follow", _carry_ghost, ^"global_position", at)
	queue_redraw()


func _reticle_to(r: Rect2, instant: bool) -> void:
	if _reticle_tween != null and _reticle_tween.is_valid():
		_reticle_tween.kill()
	var to := r.get_center()
	var to_r := maxf(RETICLE_MIN, minf(r.size.x, r.size.y) * 0.5 + RETICLE_PAD)
	var was := reticle_visible
	reticle_visible = true
	if instant or not was or not Motion.live(&"target_snap"):
		reticle_pos = to
		reticle_r = to_r
		reticle_pop = 0.0
		queue_redraw()
		return
	var e := Motion.entry(&"target_snap")
	var from := reticle_pos
	var from_r := reticle_r
	_reticle_tween = create_tween()
	_reticle_tween.tween_method(func(p: float) -> void:
		reticle_pos = from.lerp(to, p)
		reticle_r = lerpf(from_r, to_r, p)
		reticle_pop = 1.0 - p
		queue_redraw(), 0.0, 1.0, Motion.seconds(&"target_snap")).set_ease(e.ease).set_trans(e.trans)


## Carry: drops on the aimed target (a cancel when none is aimed). Returns the outcome.
func confirm() -> String:
	if mode != Mode.CARRY:
		return ""
	var t := aimed() if aim_index >= 0 else target(hover_id)
	return _let_go(t, _held_at())


## Lets go at global point `at`: on a target that takes the item it lands ("dropped"), on
## one that doesn't it is refused ("refused"), on nothing it glides home ("cancel").
func release_at(at: Vector2) -> String:
	if mode == Mode.IDLE:
		return ""
	return _let_go(target_at(at), at)


## Lets go over target `id` (as a release on its centre; demos and tests): the same
## outcomes as `release_at`. A target not offered for the item is nothing (a cancel).
func drop_on(id: String) -> String:
	if mode == Mode.IDLE:
		return ""
	var t := target(id)
	if t.is_empty() or not offered(id):
		return cancel()
	var r := locate(t)
	return _let_go(t, r.get_center() if r.has_area() else _held_at())


## Puts the item back (it glides home). Returns "cancel", or "" when nothing is held.
func cancel() -> String:
	if mode == Mode.IDLE:
		return ""
	return _let_go({}, _held_at())


## Where the held item is drawn now (global): the carried copy, else the pointer.
func _held_at() -> Vector2:
	if _carry_ghost != null and is_instance_valid(_carry_ghost):
		return _carry_ghost.card_center() if _carry_ghost.is_inside_tree() else _carry_ghost.global_position
	return get_global_mouse_position() if is_inside_tree() else _source_rect.get_center()


func _let_go(t: Dictionary, at: Vector2) -> String:
	last_flight = {}
	var p := payload
	var holder := source
	var home := _source_rect
	var reason := String(reasons.get(t.get("id", ""), "")) if not t.is_empty() else ""
	var to := locate(t) if not t.is_empty() else Rect2()
	_end()
	if t.is_empty():
		_fly_home(p, holder, at, home)
		last_outcome = "cancel"
		return last_outcome
	if reason != "":
		_mark(to.get_center() if to.has_area() else at)
		_fly_home(p, holder, at, home)
		last_outcome = "refused"
		refused.emit(p, t, reason)
		return last_outcome
	_restore_source(holder)
	if bool(t.get("lands", true)):
		var land_p := p
		if LAND_BESIDE_KINDS.has(String(t.get("kind", ""))) and to.has_area():
			# ANIM-R2 E9: a drop that only picks (a crew chip on JACK IN) lands beside the
			# button, never on its words.
			land_p = p.duplicate()
			land_p["beside"] = to
		_fly_land(land_p, holder, at, to.get_center() if to.has_area() else at)
	last_outcome = "dropped"
	dropped.emit(p, t)
	return last_outcome


func _end() -> void:
	var was_carry := mode == Mode.CARRY
	mode = Mode.IDLE
	mouse_filter = Control.MOUSE_FILTER_IGNORE
	if _pulse_tween != null and _pulse_tween.is_valid():
		_pulse_tween.kill()
	_pulse_tween = null
	pulse = 1.0
	if _reticle_tween != null and _reticle_tween.is_valid():
		_reticle_tween.kill()
	reticle_visible = false
	hover_id = ""
	aim_index = -1
	if _carry_ghost != null and is_instance_valid(_carry_ghost):
		_carry_ghost.queue_free()
	_carry_ghost = null
	source = null
	payload = {}
	queue_redraw()
	if was_carry:
		carry_changed.emit(false)


func _restore_source(holder: Control) -> void:
	if holder != null and is_instance_valid(holder):
		holder.modulate.a = _source_alpha


func _start_pulse() -> void:
	pulse = 1.0
	if not Motion.live(&"drop_zone_pulse"):
		return
	var e := Motion.entry(&"drop_zone_pulse")
	var d := Motion.seconds(&"drop_zone_pulse")
	var a := Motion.amplitude(&"drop_zone_pulse")
	_pulse_tween = create_tween().set_loops()
	_pulse_tween.tween_method(func(v: float) -> void: pulse = v; queue_redraw(), 1.0, a, d).set_ease(e.ease).set_trans(e.trans)
	_pulse_tween.tween_method(func(v: float) -> void: pulse = v; queue_redraw(), a, 1.0, d).set_ease(e.ease).set_trans(e.trans)


func _ghost(p: Dictionary, holder: Control) -> Control:
	if not ghost_maker.is_valid():
		return null
	var g: Control = ghost_maker.call(p, holder)
	if g != null:
		g.size = g.get_combined_minimum_size().max(g.size)
	return g


# --- Flights ------------------------------------------------------------------------------

## The item lands on `to` (global): a copy travels from `from` (`loadout_swap`, or the
## payload's "motion" such as `crew_assign`), settles into place (`drop_settle`: it dips its
## amplitude px and springs back) and stamps (`drop_stamp`: a ring grows its amplitude px
## as the copy fades). Returns the flight ({} when motion doesn't play).
##
## ANIM-4b payload keys: "land" = "buy" shrinks the copy to its travel's amplitude as it
## arrives (a purchase going into a small top bar tag or slot, `drop_buy`); "shred" feeds
## it into the target's mouth instead of settling (`shred_feed`); "stamp" = a word (SOLD)
## stamped on the copy as it travels (`sold_stamp`, as ANIM-6's click purchases).
func _fly_land(p: Dictionary, holder: Control, from: Vector2, to: Vector2) -> Dictionary:
	last_flight = {}
	var travel := StringName(String(p.get("motion", "loadout_swap")))
	if not Motion.live(travel):
		return {}
	var copy := _ghost(p, holder)
	if copy == null:
		return {}
	var f := _adopt(copy, from, "land", p)
	last_flight = f
	f["to"] = to
	var tw: Tween = f["tween"]
	var e := Motion.entry(travel)
	var land := String(p.get("land", ""))
	var end := to - Vector2(0, copy.size.y * 0.5) if land == "shred" else to
	if p.has("beside"):
		end = beside_spot(p["beside"], copy.size, get_viewport_rect().size if is_inside_tree() else Vector2.INF)
		f["to"] = end
	tw.tween_method(_place.bind(copy, from, end), 0.0, 1.0, Motion.seconds(travel)).set_ease(e.ease).set_trans(e.trans)
	if land == "buy":
		tw.parallel().tween_property(copy, "scale", Vector2.ONE * Motion.amplitude(travel), Motion.seconds(travel)).set_ease(e.ease).set_trans(e.trans)
	var word := String(p.get("stamp", ""))
	if word != "" and Motion.live(&"sold_stamp"):
		var se := Motion.entry(&"sold_stamp")
		var mark := FlightFx.stamp_mark(copy, Rect2(Vector2.ZERO, copy.size), word)
		mark.scale = Vector2.ONE * Motion.amplitude(&"sold_stamp")
		tw.parallel().tween_property(mark, "scale", Vector2.ONE, Motion.seconds(&"sold_stamp")).set_ease(se.ease).set_trans(se.trans)
	if land == "shred":
		_feed(tw, copy, f)
	else:
		_settle_and_stamp(tw, copy, f)
	tw.tween_callback(_end_flight.bind(f))
	return f


## Target kinds whose drop only picks something (the press acts): the item lands beside
## the target, never over its words (ANIM-R2 E9).
const LAND_BESIDE_KINDS: Array[String] = ["jack"]
## The gap between such a target and the item landing beside it (px).
const LAND_BESIDE_GAP := 8.0


## Where an item of `item` size lands beside `rect` (global centre): to its left, else to
## its right when the left runs off `screen`.
static func beside_spot(rect: Rect2, item: Vector2, screen: Vector2 = Vector2.INF) -> Vector2:
	var left := Vector2(rect.position.x - LAND_BESIDE_GAP - item.x * 0.5, rect.get_center().y)
	if left.x - item.x * 0.5 >= 0.0:
		return left
	var right := Vector2(rect.end.x + LAND_BESIDE_GAP + item.x * 0.5, rect.get_center().y)
	return right if screen == Vector2.INF or right.x + item.x * 0.5 <= screen.x else left


## Shredded (ANIM-4b): the copy, its foot on the target's middle (the shredder's mouth),
## squashes down into it (`shred_feed`) while paper strips run out under the mouth
## (the entry's amplitude = the strips' length, px).
func _feed(tw: Tween, copy: Control, f: Dictionary) -> void:
	var fe := Motion.entry(&"shred_feed")
	var d := Motion.seconds(&"shred_feed")
	tw.tween_callback(func() -> void:
		if is_instance_valid(copy):
			var at := copy.global_position + copy.size * 0.5
			copy.pivot_offset = Vector2(copy.size.x * 0.5, copy.size.y)
			copy.global_position = at - copy.size * 0.5
			_strips(f["to"], copy.size.x))
	tw.tween_property(copy, "scale:y", 0.0, d).set_ease(fe.ease).set_trans(fe.trans)
	tw.parallel().tween_property(copy, "modulate:a", 0.0, d).set_ease(Tween.EASE_IN)
	tw.tween_callback(_reveal.bind(f))


## A purchase made with a click flies from `from` (global rect: the button) to wherever
## `to` says (a locator: the target may move while the page rebuilds) along an arc of
## `market_fly`'s amplitude px, then settles and stamps like a drop. Returns the flight.
func buy_flight(p: Dictionary, from: Rect2, to: Callable) -> Dictionary:
	if not Motion.live(&"market_fly"):
		return {}
	var copy := _ghost(p, null)
	if copy == null:
		return {}
	var f := _adopt(copy, from.get_center(), "buy", p)
	var tw: Tween = f["tween"]
	var e := Motion.entry(&"market_fly")
	var start := from.get_center()
	var lift := Motion.amplitude(&"market_fly")
	tw.tween_method(func(q: float) -> void:
		if not is_instance_valid(copy):
			return
		var r: Rect2 = to.call()
		var end := r.get_center() if r.has_area() else start
		var k: float = Tween.interpolate_value(0.0, 1.0, q, 1.0, e.trans, e.ease)
		copy.global_position = start.lerp(end, k) - Vector2(0, lift * sin(PI * k)) - copy.size * 0.5, 0.0, 1.0, Motion.seconds(&"market_fly"))
	tw.tween_callback(func() -> void:
		var r: Rect2 = to.call()
		f["to"] = r.get_center() if r.has_area() else start)
	_settle_and_stamp(tw, copy, f)
	tw.tween_callback(_end_flight.bind(f))
	return f


## Keeps `node` hidden until flight `f` lands (the real item appears as its copy lands)
## and pops it then; with `hide` false it stays shown and only pops. Shown at once when
## there is no flight.
func reveal_on_land(f: Dictionary, node: CanvasItem, hide: bool = true) -> void:
	if node == null or not is_instance_valid(node):
		return
	if f.is_empty() or not flights.has(f):
		node.modulate.a = 1.0
		return
	if hide:
		node.modulate.a = 0.0
	(f["reveal"] as Array).append(weakref(node))


## The item goes back where it came from: a copy glides from `from` to `home`
## (`drag_cancel_return`, as ANIM-3's cancelled cards); the source shows again when it is
## back.
func _fly_home(p: Dictionary, holder: Control, from: Vector2, home: Rect2) -> void:
	if not Motion.live(&"drag_cancel_return") or not home.has_area():
		_restore_source(holder)
		return
	var copy := _ghost(p, holder)
	if copy == null:
		_restore_source(holder)
		return
	var f := _adopt(copy, from, "home", p)
	f["holder"] = weakref(holder) if holder != null else null
	var tw: Tween = f["tween"]
	var e := Motion.entry(&"drag_cancel_return")
	tw.tween_method(_place.bind(copy, from, home.get_center()), 0.0, 1.0, Motion.seconds(&"drag_cancel_return")).set_ease(e.ease).set_trans(e.trans)
	tw.tween_callback(_end_flight.bind(f))


## After the travel: the copy dips `drop_settle`'s amplitude px and springs back onto
## f["to"], the stamp ring grows there, the held real item shows, and the copy fades
## (`drop_stamp`).
func _settle_and_stamp(tw: Tween, copy: Control, f: Dictionary) -> void:
	var se := Motion.entry(&"drop_settle")
	var dip := Motion.amplitude(&"drop_settle")
	tw.tween_method(func(q: float) -> void:
		if is_instance_valid(copy):
			var to: Vector2 = f["to"]
			copy.global_position = to - copy.size * 0.5 + Vector2(0, dip * sin(PI * q)), 0.0, 1.0, Motion.seconds(&"drop_settle")).set_ease(se.ease).set_trans(se.trans)
	tw.tween_callback(func() -> void:
		if is_instance_valid(copy):
			_stamp(f["to"], maxf(copy.size.x, copy.size.y) * copy.scale.x * STAMP_START)
		_reveal(f))
	tw.tween_property(copy, "modulate:a", 0.0, Motion.seconds(&"drop_stamp")).set_ease(Tween.EASE_OUT)


func _place(q: float, copy: Control, from: Vector2, to: Vector2) -> void:
	if is_instance_valid(copy):
		copy.global_position = from.lerp(to, q) - copy.size * 0.5


func _adopt(copy: Control, at: Vector2, kind: String, p: Dictionary) -> Dictionary:
	copy.mouse_filter = Control.MOUSE_FILTER_IGNORE
	copy.focus_mode = Control.FOCUS_NONE
	add_child(copy)
	copy.size = copy.get_combined_minimum_size().max(copy.size)
	copy.pivot_offset = copy.size * 0.5
	copy.global_position = at - copy.size * 0.5
	copy.modulate.a = Motion.amplitude(&"drag_ghost_follow")
	var f := {"node": copy, "tween": copy.create_tween(), "kind": kind, "reveal": [], "to": at, "payload": p}
	flights.append(f)
	set_process(true)
	return f


## The real items a flight held back show as it lands; an operative's post pops
## (`crew_assign`), anything else settles with the pick-up pop.
func _reveal(f: Dictionary) -> void:
	for ref in f.get("reveal", []):
		var n: CanvasItem = (ref as WeakRef).get_ref()
		if n != null:
			n.modulate.a = 1.0
			Motion.pop(n, &"crew_assign" if String((f.get("payload", {}) as Dictionary).get("kind", "")) in ["crew", "recruit"] else &"drag_pickup")
	(f["reveal"] as Array).clear()


func _end_flight(f: Dictionary) -> void:
	if not flights.has(f):
		return
	flights.erase(f)
	var tw: Tween = f["tween"]
	if tw != null and tw.is_valid():
		tw.kill()
	var node: Node = f["node"]
	if is_instance_valid(node):
		node.queue_free()
	for ref in f.get("reveal", []):
		var n: CanvasItem = (ref as WeakRef).get_ref()
		if n != null:
			n.modulate.a = 1.0
	if f.get("holder") != null:
		_restore_source((f["holder"] as WeakRef).get_ref())
	# ANIM-4b: what the screen waits on (a viewer that closes once its landing has played).
	var done: Callable = f.get("on_done", Callable())
	if done.is_valid():
		done.call()
	queue_redraw()


## Ends every flight, mark and stamp at once (a skip: input during motion completes it).
func finish_all() -> void:
	for f in flights.duplicate():
		_end_flight(f)
	sprites.clear()
	queue_redraw()


## True while a flight, mark or stamp still plays.
func busy() -> bool:
	return not flights.is_empty() or not sprites.is_empty()


# --- Marks --------------------------------------------------------------------------------

## The no-entry mark on a refused target at `at` (global): it shakes `drop_reject`'s
## amplitude px and fades over the item's way home.
func _mark(at: Vector2) -> void:
	if not Motion.live(&"drop_reject"):
		return
	sprites.append({"kind": "mark", "at": at, "age": 0.0, "shake": Motion.seconds(&"drop_reject"),
		"dur": Motion.seconds(&"drop_reject") + Motion.seconds(&"drag_cancel_return"), "amp": Motion.amplitude(&"drop_reject")})
	set_process(true)


## Paper strips running out of a shredder's mouth at `at` (global) under a card `width` px
## wide (ANIM-4b), for `shred_feed`'s duration.
func _strips(at: Vector2, width: float) -> void:
	if not Motion.live(&"shred_feed"):
		return
	sprites.append({"kind": "strips", "at": at, "age": 0.0, "dur": Motion.seconds(&"shred_feed") * STRIP_HOLD, "len": Motion.amplitude(&"shred_feed"), "w": width * STRIP_SPAN})
	set_process(true)


## The stamp ring where an item landed.
func _stamp(at: Vector2, r0: float) -> void:
	if not Motion.live(&"drop_stamp"):
		return
	sprites.append({"kind": "stamp", "at": at, "age": 0.0, "dur": Motion.seconds(&"drop_stamp"), "r0": r0, "grow": Motion.amplitude(&"drop_stamp")})
	set_process(true)


# --- Input --------------------------------------------------------------------------------

func _input(event: InputEvent) -> void:
	# ANIM-R1 (MotionSkip): a press during a flight, mark or stamp completes it and is
	# consumed (a B that ends a viewer's landing never also leaves the page behind it).
	# ANIM-R4 C2 (MotionSkip.verdict): a press that works the screen completes them and passes
	# on; an open pause menu keeps its presses.
	if busy():
		var v := MotionSkip.verdict(event, self)
		if v == MotionSkip.Verdict.CONSUME:
			finish_all()
			MotionSkip.consume(self, event)
			return
		if v == MotionSkip.Verdict.PASS:
			finish_all()
	if retiring:
		return
	if mode == Mode.CARRY:
		_carry_input(event)
		return
	if mode != Mode.IDLE or not is_visible_in_tree():
		return
	# The pick-up key on a focused source (or inside one) takes its item; accept does on a
	# source that is no button (a button's accept keeps its own meaning).
	var pick := event.is_action_pressed(&"end_turn") and not event.is_echo()
	var accept := event.is_action_pressed(&"ui_accept") and not event.is_echo()
	if not pick and not accept:
		return
	var holder := focused_source()
	if holder == null or (accept and not pick and _focus_is_button()):
		return
	start_carry(holder)
	get_viewport().set_input_as_handled()


## The source holding focus (the focus owner or its nearest ancestor with this layer's
## payload), or null.
func focused_source() -> Control:
	var vp := get_viewport()
	var n: Node = vp.gui_get_focus_owner() if vp != null else null
	while n != null:
		if n is Control and n.has_meta(SOURCE_META) and int((n.get_meta(SOURCE_META) as Dictionary).get("layer", 0)) == get_instance_id():
			return n as Control
		n = n.get_parent()
	return null


func _focus_is_button() -> bool:
	var vp := get_viewport()
	var owner: Control = vp.gui_get_focus_owner() if vp != null else null
	return owner is BaseButton


func _carry_input(event: InputEvent) -> void:
	if event is InputEventMouseMotion:
		point_at((event as InputEventMouseMotion).global_position)
		return
	if event is InputEventMouseButton:
		var mb := event as InputEventMouseButton
		if mb.pressed:
			if mb.button_index == MOUSE_BUTTON_LEFT:
				release_at(mb.global_position)
			elif mb.button_index == MOUSE_BUTTON_RIGHT:
				cancel()
			get_viewport().set_input_as_handled()
		return
	if event.is_echo() and not (event.is_action(&"ui_left") or event.is_action(&"ui_right") or event.is_action(&"ui_up") or event.is_action(&"ui_down")):
		return
	if event.is_action_pressed(&"ui_cancel") or event.is_action_pressed(&"end_turn"):
		cancel()
	elif event.is_action_pressed(&"ui_accept"):
		confirm()
	elif event.is_action_pressed(&"ui_left", true) or event.is_action_pressed(&"ui_up", true):
		step_aim(-1)
	elif event.is_action_pressed(&"ui_right", true) or event.is_action_pressed(&"ui_down", true):
		step_aim(1)
	elif not UiFocus.is_device_input(event):
		return
	get_viewport().set_input_as_handled()


# --- Godot drag: the layer takes the drop -------------------------------------------------

func _can_drop_data(at_position: Vector2, data: Variant) -> bool:
	if mode != Mode.DRAG or not _ours(data):
		return false
	var t := target_at(get_global_transform() * at_position)
	var id := String(t.get("id", ""))
	if id != hover_id:
		hover_id = id
		queue_redraw()
	return true


func _drop_data(at_position: Vector2, data: Variant) -> void:
	if mode == Mode.DRAG and _ours(data):
		release_at(get_global_transform() * at_position)


func _ours(data: Variant) -> bool:
	return data is Dictionary and int((data as Dictionary).get("drop_layer", 0)) == get_instance_id()


func _notification(what: int) -> void:
	# A drag that ended anywhere else (outside the window, Esc) puts the item back.
	if what == NOTIFICATION_DRAG_END and mode == Mode.DRAG:
		cancel()


# --- Drawing ------------------------------------------------------------------------------

func _process(delta: float) -> void:
	for s in sprites.duplicate():
		s["age"] = float(s["age"]) + delta
		if float(s["age"]) >= float(s["dur"]):
			sprites.erase(s)
	if mode == Mode.IDLE and flights.is_empty() and sprites.is_empty():
		set_process(false)
		if retiring:
			queue_free()
	queue_redraw()


## ANIM-4b: a layer over a viewer that has closed: it takes nothing more and frees itself
## once its flights and marks have played (at once when none are left).
var retiring: bool = false


func retire() -> void:
	retiring = true
	reset()
	if mode == Mode.IDLE and not busy():
		queue_free()
	else:
		set_process(true)


func _local(p: Vector2) -> Vector2:
	return get_global_transform().affine_inverse() * p


func _draw() -> void:
	if mode != Mode.IDLE:
		for t in targets:
			var id := String(t["id"])
			if not offered(id):
				continue
			var r := locate(t)
			if not r.has_area():
				continue
			var lr := Rect2(_local(r.position), r.size)
			var hot := id == hover_id
			if takes(id):
				_bracket(lr, Color(Palette.CELL_ACID, 1.0 if hot else pulse))
			elif hot:
				_bracket(lr, Color(Palette.CELL_PINK, 0.8))
				_no_entry(_local(r.get_center()), 1.0, 0.0)
	if reticle_visible:
		var c := _local(reticle_pos)
		var rr := reticle_r + Motion.amplitude(&"target_snap") * reticle_pop
		var col := Palette.CELL_ACID if takes(hover_id) else Palette.CELL_PINK
		for k in 4:
			var a := PI * 0.25 + k * PI * 0.5
			draw_arc(c, rr, a - RETICLE_ARC, a + RETICLE_ARC, 6, col, RETICLE_W, true)
	for s in sprites:
		var p := clampf(float(s["age"]) / maxf(0.001, float(s["dur"])), 0.0, 1.0)
		match String(s["kind"]):
			"mark":
				var sp := clampf(float(s["age"]) / maxf(0.001, float(s["shake"])), 0.0, 1.0)
				var dx := float(s["amp"]) * sin(sp * TAU * 2.0) * (1.0 - sp)
				_no_entry(_local(s["at"]) + Vector2(dx, 0), 1.0 - p * p, dx)
			"stamp":
				draw_arc(_local(s["at"]), float(s["r0"]) + float(s["grow"]) * p, 0, TAU, 40, Color(Palette.CELL_ACID, 1.0 - p), STAMP_W, true)
			"strips":
				# They run out over the feed, then fade (fixed lengths per strip: no randomness).
				var mouth := _local(s["at"])
				var grow := clampf(p * STRIP_HOLD, 0.0, 1.0)
				var w := float(s["w"])
				for k in STRIP_COUNT:
					var x := mouth.x - w * 0.5 + w * (k + 0.5) / STRIP_COUNT
					var reach := float(s["len"]) * grow * STRIP_LENGTHS[k % STRIP_LENGTHS.size()]
					draw_line(Vector2(x, mouth.y), Vector2(x + STRIP_SLANT * (k - STRIP_COUNT * 0.5), mouth.y + reach), Color(Palette.NOTE_PAPER, 1.0 - p * p), STRIP_W, true)


## Corner brackets round `r` (local) in `col`.
func _bracket(r: Rect2, col: Color) -> void:
	var g := r.grow(BRACKET_OUT)
	var arm := minf(BRACKET, minf(g.size.x, g.size.y) * 0.5)
	for corner in [[g.position, Vector2(1, 0), Vector2(0, 1)], [Vector2(g.end.x, g.position.y), Vector2(-1, 0), Vector2(0, 1)],
			[Vector2(g.position.x, g.end.y), Vector2(1, 0), Vector2(0, -1)], [g.end, Vector2(-1, 0), Vector2(0, -1)]]:
		var at: Vector2 = corner[0]
		draw_line(at, at + (corner[1] as Vector2) * arm, col, BRACKET_W, true)
		draw_line(at, at + (corner[2] as Vector2) * arm, col, BRACKET_W, true)


## The drawn no-entry mark (a circle with a slash, as the refusal toast's) at `c` (local).
func _no_entry(c: Vector2, alpha: float, _dx: float) -> void:
	var col := Color(Palette.CELL_PINK, alpha)
	draw_circle(c, MARK_RADIUS + MARK_W, Color(Palette.NIGHT_SKY, 0.7 * alpha))
	draw_arc(c, MARK_RADIUS, 0, TAU, 24, col, MARK_W, true)
	var d := Vector2(MARK_RADIUS, -MARK_RADIUS) * 0.7
	draw_line(c - d, c + d, col, MARK_W, true)
