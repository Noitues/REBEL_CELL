class_name CombatFxLayer
extends Control
## The combat scene's motion overlay (Animation pass ANIM-2 / ANIM-3): short-lived drawn
## effects over the arena (floating numbers, hit lines, bursts, rings, status stamps, the
## pieces of a broken wheel, hub glass, VHS rewind lines, the VICTORY / DEFEAT stamp, the
## deck and discard piles, the aim reticle) and card copies that fly (play, discard,
## exhaust, a cancelled drag's return). Every timing comes from ui_motion.tres through
## `Motion`; nothing is added when motion doesn't play (reduce effects, headless), so the
## end state never waits on it. View only: it draws, it never touches game state, and its
## scatter comes from hashes, never from an RNG. It takes no input.

## Floating number lettering at text scale 1.0 (px) and its white outline.
const NUMBER_FONT := 24
const NUMBER_OUTLINE := 6
## Star burst: spikes round a crit, and their inner radius share.
const BURST_SPIKES := 10
const BURST_INNER := 0.35
## Hit line arrowhead (px).
const ARROW_HEAD := 9.0
## A number's rise shape: it grows over this share of its life, then holds, and fades
## over the last FADE_SHARE.
const GROW_SHARE := 0.25
const FADE_SHARE := 0.35
## Status stamp lettering (px at text scale 1.0) and its disc.
const STAMP_FONT := 16
const STAMP_DISC := 11.0
## Glass shards of a breached hub, and ember flecks of an exhausted card.
const GLASS_SHARDS := 12
const EMBERS := 9
## VHS rewind bands across the arena.
const VHS_BANDS := 7
const VHS_BAND_PX := 3.0
## VICTORY / DEFEAT lettering at text scale 1.0 (px).
const WORD_FONT := 64
## Pile marks: a small stack of card backs (px at text scale 1.0).
const PILE_SIZE := Vector2(34, 46)
const PILE_LAYERS := 3
## Reticle brackets round the aimed zone (px).
const RETICLE_RADIUS := 16.0
const RETICLE_ARC := 0.45
## A discarded card shrinks to this scale and loses this much alpha on its way.
const DISCARD_SCALE := 0.4
const DISCARD_FADE := 0.6

## Live sprites: each {kind, age, dur, ...}; drawn and aged in _process.
var sprites: Array[Dictionary] = []
## Card copies in flight: {node, tween, to, kind}.
var flights: Array[Dictionary] = []
## The aim reticle (global), shown while a card is aimed; `reticle_visible` false = none.
var reticle_pos: Vector2 = Vector2.ZERO
var reticle_visible: bool = false
var reticle_pop: float = 0.0
var _reticle_tween: Tween = null
var _serial: int = 0


func _init() -> void:
	mouse_filter = Control.MOUSE_FILTER_IGNORE
	set_process(false)


func _ready() -> void:
	set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)


## True while any effect or flight is still playing.
func busy() -> bool:
	return not sprites.is_empty() or not flights.is_empty()


## Ends every effect at once (skip): sprites vanish, flying cards land where they were
## going (their `on_done` runs) and are freed.
func clear() -> void:
	sprites.clear()
	for f in flights.duplicate():
		_end_flight(f)
	flights.clear()
	set_process(false)
	queue_redraw()


func _process(delta: float) -> void:
	var keep: Array[Dictionary] = []
	var arrived: Array[Callable] = []
	for s in sprites:
		s["age"] = float(s["age"]) + delta
		if float(s["age"]) < float(s["dur"]) + float(s.get("delay", 0.0)):
			keep.append(s)
		elif String(s["kind"]) == "travel" and (s["on_arrive"] as Callable).is_valid():
			arrived.append(s["on_arrive"])
	sprites = keep
	for c in arrived:
		c.call()
	queue_redraw()
	if sprites.is_empty() and flights.is_empty():
		set_process(false)


func _add(s: Dictionary) -> void:
	_serial += 1
	s["serial"] = _serial
	s["age"] = 0.0
	sprites.append(s)
	set_process(true)
	queue_redraw()


## A sprite's progress 0..1 (0 before its delay has run).
static func _p(s: Dictionary) -> float:
	var d := float(s["dur"])
	var a := float(s["age"]) - float(s.get("delay", 0.0))
	return clampf(a / d, 0.0, 1.0) if d > 0.0 else 1.0


static func _ease(s: Dictionary) -> float:
	return Tween.interpolate_value(0.0, 1.0, _p(s), 1.0, int(s.get("trans", Tween.TRANS_LINEAR)), int(s.get("ease", Tween.EASE_OUT)))


## Hash noise 0..1 (decoration only).
static func _h(a: int, b: int, c: int = 0) -> float:
	return float(hash(Vector3i(a, b, c)) & 0xFFFF) / 65535.0


func _local(global: Vector2) -> Vector2:
	return global - get_global_rect().position


# --- Effects -----------------------------------------------------------------------------

## A number that pops at `at` (global) and drifts `rise` px along `dir` (`id` = its motion
## entry: amplitude = the drift unless `rise` >= 0). Crits grow by `number_crit` and get
## a star burst. Returns the rect it covers at its biggest (global), for layout checks.
func number(at: Vector2, text: String, color: Color, id: StringName, dir: Vector2 = Vector2.UP, crit: bool = false, rise: float = -1.0,
		font_size: int = -1, band: String = "") -> Rect2:
	var fs := number_font(crit) if font_size <= 0 else font_size
	var drift := Motion.amplitude(id) if rise < 0.0 else rise
	var rect := number_rect(at, text, crit, dir * drift, fs)
	if not Motion.live(id):
		return rect
	_hurry(band)
	var e := Motion.entry(id)
	_add({"kind": "number", "at": at, "text": text, "color": color, "dur": Motion.seconds(id), "delay": Motion.delay_of(id),
		"dir": dir, "rise": drift, "fs": fs, "crit": crit, "ease": e.ease, "trans": e.trans, "band": band})
	if crit and Motion.live(&"number_crit"):
		burst(at, color, &"number_crit")
	return rect


## ANIM-R1: a number that pops at `at` (global), holds (`number_to_hp`'s delay), then
## travels into `to` (the victim's HP counter) shrinking to `number_to_hp`'s amplitude;
## `on_arrive` runs as it gets there (the HP rolls down then). A skip drops it (the end
## state shows anyway). `band` names the hub band it sits in: a new number in the same
## band sends the one resting there on its way at once, so two never rest on each other.
func travel_number(at: Vector2, to: Vector2, text: String, color: Color, crit: bool, font_size: int, band: String,
		on_arrive: Callable = Callable()) -> void:
	if not Motion.live(&"number_to_hp"):
		if on_arrive.is_valid():
			on_arrive.call()
		return
	_hurry(band)
	var e := Motion.entry(&"number_to_hp")
	_add({"kind": "travel", "at": at, "to": to, "text": text, "color": color, "fs": font_size, "crit": crit,
		"hold": Motion.delay_of(&"number_to_hp"), "dur": Motion.delay_of(&"number_to_hp") + Motion.seconds(&"number_to_hp"),
		"shrink": Motion.amplitude(&"number_to_hp"), "ease": e.ease, "trans": e.trans, "band": band, "on_arrive": on_arrive})
	if crit and Motion.live(&"number_crit"):
		burst(at, color, &"number_crit")


## The numbers resting in `band` move on: a travelling one sets off now, a floating one
## goes (ANIM-R1: numbers never rest on each other).
func _hurry(band: String) -> void:
	if band == "":
		return
	for s in sprites.duplicate():
		if String(s.get("band", "")) != band:
			continue
		if String(s["kind"]) == "travel":
			s["age"] = maxf(float(s["age"]), float(s["hold"]))
		elif String(s["kind"]) == "number":
			sprites.erase(s)


## Numbers resting in their band now (not yet travelling): [{rect (global), band}], for
## the layout checks.
func resting_numbers() -> Array:
	var out: Array = []
	for s in sprites:
		var k := String(s["kind"])
		if k == "number" or (k == "travel" and float(s["age"]) < float(s["hold"])):
			out.append({"rect": number_rect(s["at"], String(s["text"]), bool(s["crit"]), Vector2.ZERO, int(s["fs"])), "band": String(s.get("band", ""))})
	return out


## Font size of a floating number (crits bigger by `number_crit`'s amplitude).
static func number_font(crit: bool) -> int:
	var fs := NUMBER_FONT * Settings.text_scale
	if crit:
		fs *= maxf(1.0, Motion.amplitude(&"number_crit"))
	return roundi(fs)


## Everything a number covers on its way (global): its start and end boxes merged.
static func number_rect(at: Vector2, text: String, crit: bool, travel: Vector2, font_size: int = -1) -> Rect2:
	var fs := number_font(crit) if font_size <= 0 else font_size
	var w := Palette.display().get_string_size(text, HORIZONTAL_ALIGNMENT_LEFT, -1, fs).x + NUMBER_OUTLINE
	var box := Rect2(at - Vector2(w * 0.5, fs * 0.5), Vector2(w, fs))
	return box.merge(Rect2(box.position + travel, box.size))


## A star burst at `at` (global) growing to `id`'s amplitude px (or x its scale when the
## amplitude is a scale below 4).
func burst(at: Vector2, color: Color, id: StringName) -> void:
	if not Motion.live(id):
		return
	var amp := Motion.amplitude(id)
	var radius := amp if amp >= 4.0 else NUMBER_FONT * Settings.text_scale * amp
	_add({"kind": "burst", "at": at, "color": color, "dur": Motion.seconds(id), "radius": radius})


## A ring at `at` (global) growing from `radius` by `id`'s amplitude px as it fades.
func ring(at: Vector2, radius: float, color: Color, id: StringName) -> void:
	if not Motion.live(id):
		return
	_add({"kind": "ring", "at": at, "r0": radius, "grow": Motion.amplitude(id), "color": color, "dur": Motion.seconds(id)})


## A hit line from `from` to `to` (global): draws in over the first half, fades over the
## second, an arrowhead at the victim.
func hit_line(from: Vector2, to: Vector2, color: Color) -> void:
	if not Motion.live(&"hit_line") or from.distance_to(to) < 1.0:
		return
	_add({"kind": "line", "from": from, "to": to, "color": color, "dur": Motion.seconds(&"hit_line"), "width": Motion.amplitude(&"hit_line")})


## ANIM-R1: a word stamped at `at` (global) in a tilted box (BLOCKED, EVADED, NO DAMAGE,
## PHASE 2...): lands from `result_stamp`'s amplitude scale, holds `hold` seconds, fades.
## Its lettering fits `max_w` px (the hub it sits in). Returns the box it covers (global).
func word_stamp(at: Vector2, text: String, color: Color, hold: float, max_w: float) -> Rect2:
	var fs := word_stamp_font(text, max_w)
	var w := Palette.marker().get_string_size(text, HORIZONTAL_ALIGNMENT_LEFT, -1, fs).x + fs * WORD_BOX_PAD * 2.0
	var box := Rect2(at - Vector2(w * 0.5, fs * WORD_BOX_H * 0.5), Vector2(w, fs * WORD_BOX_H))
	if not Motion.live(&"result_stamp"):
		return box
	_add({"kind": "tag", "at": at, "text": text, "color": color, "fs": fs, "dur": Motion.seconds(&"result_stamp") + hold,
		"land": Motion.seconds(&"result_stamp"), "from": Motion.amplitude(&"result_stamp")})
	return box


## The stamp's font size: WORD_STAMP_FONT at the text scale, smaller until it fits `max_w`.
static func word_stamp_font(text: String, max_w: float) -> int:
	var fs := roundi(WORD_STAMP_FONT * Settings.text_scale)
	while fs > WORD_STAMP_MIN and Palette.marker().get_string_size(text, HORIZONTAL_ALIGNMENT_LEFT, -1, fs).x + fs * WORD_BOX_PAD * 2.0 > max_w:
		fs -= 1
	return fs


## Word stamps (ANIM-R1): lettering at text scale 1.0 and its floor (px), the box's side
## padding and height (shares of the font size) and its tilt (rad).
const WORD_STAMP_FONT := 20
const WORD_STAMP_MIN := 9
const WORD_BOX_PAD := 0.3
const WORD_BOX_H := 1.4
const WORD_TILT := -0.2
## A projectile's head: its radius as a share of the line's width.
const PROJECTILE_HEAD := 1.3


## A status glyph stamped at `at` (global): lands from `status_stamp`'s amplitude scale,
## holds `hold` seconds (the wheel then shows the status itself) and fades.
func stamp(at: Vector2, glyph: String, color: Color, hold: float) -> void:
	if not Motion.live(&"status_stamp"):
		return
	_add({"kind": "stamp", "at": at, "glyph": glyph, "color": color, "dur": Motion.seconds(&"status_stamp") + hold,
		"land": Motion.seconds(&"status_stamp"), "from": Motion.amplitude(&"status_stamp")})


## A broken wheel: `pieces` ([polygon (global), colour]) fall `enemy_break`'s amplitude px
## with a spin each, fading out.
func shards(pieces: Array) -> void:
	if not Motion.live(&"enemy_break") or pieces.is_empty():
		return
	_add({"kind": "shards", "pieces": pieces, "dur": Motion.seconds(&"enemy_break"), "fall": Motion.amplitude(&"enemy_break"),
		"ease": Motion.entry(&"enemy_break").ease, "trans": Motion.entry(&"enemy_break").trans})


## Hub glass shattering at `at` (global) out of a hub `radius` px across.
func glass(at: Vector2, radius: float, color: Color) -> void:
	if not Motion.live(&"hub_shatter"):
		return
	_add({"kind": "glass", "at": at, "r": radius, "color": color, "dur": Motion.seconds(&"hub_shatter"), "fly": Motion.amplitude(&"hub_shatter"),
		"ease": Motion.entry(&"hub_shatter").ease, "trans": Motion.entry(&"hub_shatter").trans})


## VHS rewind lines over `area` (global) for `rewind_scrub`'s duration (jitter px).
func vhs(area: Rect2) -> void:
	if not Motion.live(&"rewind_scrub"):
		return
	_add({"kind": "vhs", "rect": area, "dur": Motion.seconds(&"rewind_scrub"), "jitter": Motion.amplitude(&"rewind_scrub")})


## The VICTORY / DEFEAT stamp at `at` (global).
func word(at: Vector2, text: String, color: Color, hold: float) -> void:
	if not Motion.live(&"victory_stamp"):
		return
	_add({"kind": "word", "at": at, "text": text, "color": color, "delay": Motion.delay_of(&"victory_stamp"),
		"dur": Motion.seconds(&"victory_stamp") + hold, "land": Motion.seconds(&"victory_stamp"), "from": Motion.amplitude(&"victory_stamp")})


## A deck or discard pile mark at `at` (global) for `seconds` (fading in and out).
func pile(at: Vector2, seconds: float) -> void:
	if not Motion.live(&"card_pile"):
		return
	_add({"kind": "pile", "at": at, "dur": seconds + Motion.seconds(&"card_pile") * 2.0, "fade": Motion.seconds(&"card_pile"),
		"alpha": Motion.amplitude(&"card_pile")})


## Embers rising off a burnt card at `rect` (global).
func embers(rect: Rect2) -> void:
	if not Motion.live(&"card_exhaust"):
		return
	_add({"kind": "embers", "rect": rect, "dur": Motion.seconds(&"card_exhaust")})


## Shows the aim reticle at `at` (global): it glides there from where it was with
## `target_snap` (a pop of amplitude px on arrival); `instant` puts it there at once.
func aim_reticle(at: Vector2, instant: bool = false) -> void:
	if _reticle_tween != null and _reticle_tween.is_valid():
		_reticle_tween.kill()
	var was_visible := reticle_visible
	reticle_visible = true
	if instant or not was_visible or not Motion.live(&"target_snap"):
		reticle_pos = at
		reticle_pop = 0.0
		queue_redraw()
		return
	var e := Motion.entry(&"target_snap")
	var from := reticle_pos
	_reticle_tween = create_tween()
	_reticle_tween.tween_method(_reticle_step.bind(from, at), 0.0, 1.0, Motion.seconds(&"target_snap")).set_ease(e.ease).set_trans(e.trans)


func _reticle_step(p: float, from: Vector2, at: Vector2) -> void:
	reticle_pos = from.lerp(at, p)
	reticle_pop = 1.0 - p
	queue_redraw()


func hide_reticle() -> void:
	if _reticle_tween != null and _reticle_tween.is_valid():
		_reticle_tween.kill()
	reticle_visible = false
	queue_redraw()


# --- Card flights -------------------------------------------------------------------------

## Flies `card` (a copy the layer now owns) from `from` (global rect, the hand slot or
## where the drag let go) to `to` (global, the zone's centre): `card_play` travel, a
## `card_stamp` landing, then it dissolves (`effect_burst`) or, when `exhaust`, burns
## (`card_exhaust`: curls up with embers). Returns the seconds until the effect may play
## (travel + stamp). `on_done` runs when it lands or is skipped.
func play_card(card: ZineCard, from: Rect2, from_rotation: float, to: Vector2, exhaust: bool, on_done: Callable = Callable()) -> float:
	if not Motion.live(&"card_play"):
		card.free()
		if on_done.is_valid():
			on_done.call()
		return 0.0
	_adopt(card, from, from_rotation)
	var fly := Motion.seconds(&"card_play")
	var land := Motion.seconds(&"card_stamp")
	var gone := Motion.seconds(&"card_exhaust") if exhaust else Motion.seconds(&"effect_burst")
	var fe := Motion.entry(&"card_play")
	var se := Motion.entry(&"card_stamp")
	var end_pos := to - card.size * 0.5
	var tw := card.create_tween()
	tw.tween_property(card, "position", end_pos, fly).set_ease(fe.ease).set_trans(fe.trans)
	tw.parallel().tween_property(card, "rotation", 0.0, fly).set_ease(fe.ease).set_trans(fe.trans)
	tw.parallel().tween_property(card, "scale", Vector2.ONE * Motion.amplitude(&"card_play"), fly * 0.5).set_ease(Tween.EASE_OUT)
	# The stamp: from a size up, down onto the target.
	tw.tween_property(card, "scale", Vector2.ONE * (1.0 / maxf(0.01, Motion.amplitude(&"card_stamp"))), land).set_ease(se.ease).set_trans(se.trans)
	var f := {"node": card, "tween": tw, "to": to, "kind": "exhaust" if exhaust else "play", "on_done": on_done}
	if exhaust:
		tw.tween_callback(func() -> void: embers(Rect2(card.global_position, card.size)))
		tw.tween_property(card, "scale:y", 0.0, gone).set_ease(Motion.entry(&"card_exhaust").ease).set_trans(Motion.entry(&"card_exhaust").trans)
		tw.parallel().tween_property(card, "modulate", Color(Palette.CELL_PINK.darkened(0.6), 0.0), gone)
	else:
		tw.tween_callback(func() -> void: burst(to, Palette.CELL_ACID, &"effect_burst"))
		tw.tween_property(card, "modulate:a", 0.0, gone).set_ease(Tween.EASE_OUT)
		tw.parallel().tween_property(card, "scale", Vector2.ZERO, gone).set_ease(Tween.EASE_IN)
	tw.tween_callback(func() -> void: _end_flight(f))
	flights.append(f)
	set_process(true)
	return fly + land


## Flies `card` (a copy) from `from` to the discard pile at `to` (global) along an arc of
## `card_discard`'s amplitude px, after `delay` seconds.
func discard_card(card: ZineCard, from: Rect2, from_rotation: float, to: Vector2, delay: float) -> void:
	if not Motion.live(&"card_discard"):
		card.free()
		return
	_adopt(card, from, from_rotation)
	var e := Motion.entry(&"card_discard")
	var start := card.position
	var end_pos := to - card.size * 0.5
	var lift := Motion.amplitude(&"card_discard")
	var tw := card.create_tween()
	tw.tween_interval(delay)
	tw.tween_method(_discard_step.bind(card, start, end_pos, lift, e.trans, e.ease), 0.0, 1.0, Motion.seconds(&"card_discard"))
	var f := {"node": card, "tween": tw, "to": to, "kind": "discard", "on_done": Callable()}
	tw.tween_callback(func() -> void: _end_flight(f))
	flights.append(f)
	set_process(true)


## One step of a discard flight: along an arc, shrinking to DISCARD_SCALE and fading.
static func _discard_step(p: float, card: ZineCard, start: Vector2, end_pos: Vector2, lift: float, trans: int, ease: int) -> void:
	if not is_instance_valid(card):
		return
	var q: float = Tween.interpolate_value(0.0, 1.0, p, 1.0, trans, ease)
	card.position = start.lerp(end_pos, q) + Vector2(0, -lift * sin(PI * q))
	card.scale = Vector2.ONE * lerpf(1.0, DISCARD_SCALE, q)
	card.modulate.a = 1.0 - q * DISCARD_FADE


## A cancelled drag: `card` (a copy) glides from `from` (global, where it was let go) back
## to its hand slot `slot` (global rect), then `on_done` runs (the hand card shows again).
func return_card(card: ZineCard, from: Vector2, slot: Rect2, slot_rotation: float, on_done: Callable) -> void:
	if not Motion.live(&"drag_cancel_return"):
		card.free()
		on_done.call()
		return
	_adopt(card, Rect2(from - card.size * 0.5, card.size), 0.0)
	var e := Motion.entry(&"drag_cancel_return")
	var tw := card.create_tween()
	tw.tween_property(card, "position", _local(slot.position), Motion.seconds(&"drag_cancel_return")).set_ease(e.ease).set_trans(e.trans)
	tw.parallel().tween_property(card, "rotation", slot_rotation, Motion.seconds(&"drag_cancel_return")).set_ease(e.ease).set_trans(e.trans)
	var f := {"node": card, "tween": tw, "to": slot.get_center(), "kind": "return", "on_done": on_done}
	tw.tween_callback(func() -> void: _end_flight(f))
	flights.append(f)
	set_process(true)


## The last flight of `kind` ("play", "exhaust", "discard", "return"), or {}.
func last_flight(kind: String) -> Dictionary:
	for i in range(flights.size() - 1, -1, -1):
		if String(flights[i]["kind"]) == kind:
			return flights[i]
	return {}


func _adopt(card: ZineCard, from: Rect2, from_rotation: float) -> void:
	card.mouse_filter = Control.MOUSE_FILTER_IGNORE
	card.focus_mode = Control.FOCUS_NONE
	card.drag_index = -1
	add_child(card)
	card.size = from.size
	card.pivot_offset = card.size * 0.5
	card.position = _local(from.position)
	card.rotation = from_rotation


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
	var done: Callable = f.get("on_done", Callable())
	if done.is_valid():
		done.call()
	if sprites.is_empty() and flights.is_empty():
		set_process(false)


# --- Drawing ------------------------------------------------------------------------------

func _draw() -> void:
	for s in sprites:
		if float(s["age"]) < float(s.get("delay", 0.0)):
			continue
		match String(s["kind"]):
			"number":
				_draw_number(s)
			"travel":
				_draw_travel(s)
			"tag":
				_draw_tag(s)
			"burst":
				_draw_burst(s)
			"ring":
				var p := _p(s)
				draw_arc(_local(s["at"]), float(s["r0"]) + float(s["grow"]) * p, 0, TAU, 40, Color(s["color"], 1.0 - p), 3.0, true)
			"line":
				_draw_line(s)
			"stamp":
				_draw_stamp(s)
			"shards":
				_draw_shards(s)
			"glass":
				_draw_glass(s)
			"vhs":
				_draw_vhs(s)
			"word":
				_draw_word(s)
			"pile":
				_draw_pile(s)
			"embers":
				_draw_embers(s)
	if reticle_visible:
		var c := _local(reticle_pos)
		var r := RETICLE_RADIUS + Motion.amplitude(&"target_snap") * reticle_pop
		for k in 4:
			var a := PI * 0.25 + k * PI * 0.5
			draw_arc(c, r, a - RETICLE_ARC, a + RETICLE_ARC, 6, Palette.CELL_ACID, 2.5, true)


func _draw_number(s: Dictionary) -> void:
	var p := _p(s)
	var fs := int(s["fs"])
	var grow := clampf(p / GROW_SHARE, 0.0, 1.0)
	var size := fs
	if bool(s["crit"]):
		# The crit overshoots its size and settles (a pop).
		size = roundi(fs * lerpf(1.35, 1.0, grow)) if p < GROW_SHARE else fs
	else:
		size = roundi(fs * lerpf(0.6, 1.0, grow))
	var at := _local(s["at"]) + (s["dir"] as Vector2) * float(s["rise"]) * _ease(s)
	var alpha := 1.0 - clampf((p - (1.0 - FADE_SHARE)) / FADE_SHARE, 0.0, 1.0)
	var text := String(s["text"])
	var f := Palette.display()
	var w := f.get_string_size(text, HORIZONTAL_ALIGNMENT_LEFT, -1, size).x
	var base := at + Vector2(-w * 0.5, size * 0.35)
	draw_string_outline(f, base, text, HORIZONTAL_ALIGNMENT_LEFT, -1, size, NUMBER_OUTLINE, Color(Palette.PAPER, alpha))
	draw_string(f, base, text, HORIZONTAL_ALIGNMENT_LEFT, -1, size, Color(s["color"], alpha))


func _draw_travel(s: Dictionary) -> void:
	var a := float(s["age"])
	var hold := float(s["hold"])
	var fs := int(s["fs"])
	var at := _local(s["at"])
	var size := float(fs)
	var alpha := 1.0
	if a < hold:
		var grow := clampf(a / maxf(0.001, hold * GROW_SHARE), 0.0, 1.0)
		size = fs * (lerpf(1.35, 1.0, grow) if bool(s["crit"]) else lerpf(0.6, 1.0, grow))
	else:
		var d := maxf(0.001, float(s["dur"]) - hold)
		var q: float = Tween.interpolate_value(0.0, 1.0, clampf((a - hold) / d, 0.0, 1.0), 1.0, int(s["trans"]), int(s["ease"]))
		at = at.lerp(_local(s["to"]), q)
		size = fs * lerpf(1.0, float(s["shrink"]), q)
		alpha = lerpf(1.0, 0.6, q)
	var isz := maxi(1, roundi(size))
	var text := String(s["text"])
	var f := Palette.display()
	var w := f.get_string_size(text, HORIZONTAL_ALIGNMENT_LEFT, -1, isz).x
	var base := at + Vector2(-w * 0.5, isz * 0.35)
	draw_string_outline(f, base, text, HORIZONTAL_ALIGNMENT_LEFT, -1, isz, NUMBER_OUTLINE, Color(Palette.PAPER, alpha))
	draw_string(f, base, text, HORIZONTAL_ALIGNMENT_LEFT, -1, isz, Color(s["color"], alpha))


func _draw_tag(s: Dictionary) -> void:
	var land := float(s["land"])
	var a := float(s["age"])
	var q := clampf(a / land, 0.0, 1.0) if land > 0.0 else 1.0
	var sc := lerpf(float(s["from"]), 1.0, Tween.interpolate_value(0.0, 1.0, q, 1.0, Tween.TRANS_BACK, Tween.EASE_OUT))
	var alpha := minf(1.0, q * 2.0) * (1.0 - clampf((_p(s) - (1.0 - FADE_SHARE)) / FADE_SHARE, 0.0, 1.0))
	var fs := int(s["fs"])
	var text := String(s["text"])
	var font := Palette.marker()
	var w := font.get_string_size(text, HORIZONTAL_ALIGNMENT_LEFT, -1, fs).x
	var box := Rect2(-w * 0.5 - fs * WORD_BOX_PAD, -fs * WORD_BOX_H * 0.5, w + fs * WORD_BOX_PAD * 2.0, fs * WORD_BOX_H)
	var col: Color = s["color"]
	draw_set_transform(_local(s["at"]), WORD_TILT, Vector2.ONE * sc)
	draw_rect(box, Color(Palette.NIGHT_SKY, 0.88 * alpha))
	draw_rect(box, Color(col, alpha), false, 3.0)
	draw_string(font, Vector2(-w * 0.5, fs * 0.35), text, HORIZONTAL_ALIGNMENT_LEFT, -1, fs, Color(col, alpha))
	draw_set_transform(Vector2.ZERO)


func _draw_burst(s: Dictionary) -> void:
	var p := _p(s)
	var c := _local(s["at"])
	var r := float(s["radius"]) * (0.5 + 0.5 * p)
	var col := Color(s["color"], 1.0 - p)
	for k in BURST_SPIKES:
		var a := TAU * k / BURST_SPIKES + int(s["serial"]) * 0.37
		var d := Vector2(cos(a), sin(a))
		draw_line(c + d * r * BURST_INNER, c + d * r, col, 2.5)


func _draw_line(s: Dictionary) -> void:
	var p := _p(s)
	var from := _local(s["from"])
	var to := _local(s["to"])
	var head := from.lerp(to, clampf(p * 2.0, 0.0, 1.0))
	var tail := from.lerp(to, clampf(p * 2.0 - 1.0, 0.0, 1.0))
	var col := Color(s["color"], 1.0 - maxf(0.0, p - 0.5))
	draw_line(tail, head, Color(Palette.NIGHT_SKY, col.a * 0.6), float(s["width"]) + 3.0)
	draw_line(tail, head, col, float(s["width"]))
	if p < 0.5:
		# ANIM-R1: the projectile's head, bright, flying from the attacker's slice.
		var hr := float(s["width"]) * PROJECTILE_HEAD
		draw_circle(head, hr + 2.0, Color(Palette.NIGHT_SKY, 0.7))
		draw_circle(head, hr, col.lightened(0.35))
	if p >= 0.5:
		var d := (to - from).normalized()
		var n := d.orthogonal() * ARROW_HEAD * 0.6
		draw_colored_polygon(PackedVector2Array([to, to - d * ARROW_HEAD + n, to - d * ARROW_HEAD - n]), col)


func _draw_stamp(s: Dictionary) -> void:
	var land := float(s["land"])
	var a := float(s["age"])
	var q := clampf(a / land, 0.0, 1.0) if land > 0.0 else 1.0
	var sc := lerpf(float(s["from"]), 1.0, Tween.interpolate_value(0.0, 1.0, q, 1.0, Tween.TRANS_BACK, Tween.EASE_OUT))
	var alpha := 1.0 - clampf((_p(s) - (1.0 - FADE_SHARE)) / FADE_SHARE, 0.0, 1.0)
	var c := _local(s["at"])
	var fs := roundi(STAMP_FONT * Settings.text_scale * sc)
	draw_circle(c, STAMP_DISC * Settings.text_scale * sc, Color(Palette.NIGHT_SKY, 0.9 * alpha))
	draw_arc(c, STAMP_DISC * Settings.text_scale * sc, 0, TAU, 20, Color(s["color"], alpha), 2.0)
	var w := Palette.mono().get_string_size(String(s["glyph"]), HORIZONTAL_ALIGNMENT_LEFT, -1, fs).x
	draw_string(Palette.mono(), c + Vector2(-w * 0.5, fs * 0.35), String(s["glyph"]), HORIZONTAL_ALIGNMENT_LEFT, -1, fs, Color(s["color"], alpha))


func _draw_shards(s: Dictionary) -> void:
	var q := _ease(s)
	var fall := float(s["fall"])
	var origin := get_global_rect().position
	var pieces: Array = s["pieces"]
	for k in pieces.size():
		var poly: PackedVector2Array = pieces[k][0]
		if poly.is_empty():
			continue
		var centre := Vector2.ZERO
		for v in poly:
			centre += v
		centre /= poly.size()
		# Each piece drifts off along its own crack, falls and turns (hash scatter).
		var side := (_h(int(s["serial"]), k) - 0.5) * 2.0
		var spin := side * PI * 0.5 * q
		var shift := Vector2(side * fall * 0.3, fall * (0.4 + 0.6 * _h(k, int(s["serial"]), 1))) * q
		var xf := Transform2D(spin, centre + shift - origin) * Transform2D(0.0, -centre)
		var out := PackedVector2Array()
		for v in poly:
			out.append(xf * v)
		var col: Color = pieces[k][1]
		draw_colored_polygon(out, Color(col, col.a * (1.0 - q)))
		var closed := out.duplicate()
		closed.append(out[0])
		draw_polyline(closed, Color(Palette.PAPER, 0.8 * (1.0 - q)), 1.2)


func _draw_glass(s: Dictionary) -> void:
	var q := _ease(s)
	var c := _local(s["at"])
	var r := float(s["r"])
	for k in GLASS_SHARDS:
		var a := TAU * (k + _h(k, int(s["serial"]))) / GLASS_SHARDS
		var d := Vector2(cos(a), sin(a))
		var p := c + d * (r * 0.4 + float(s["fly"]) * q)
		var size := r * (0.18 + 0.12 * _h(k, 7, int(s["serial"])))
		var tri := PackedVector2Array([p + d * size, p + d.orthogonal() * size * 0.5, p - d.orthogonal() * size * 0.5])
		draw_colored_polygon(tri, Color(Palette.PAPER, 0.85 * (1.0 - q)))
		draw_polyline(PackedVector2Array([tri[0], tri[1], tri[2], tri[0]]), Color(s["color"], 1.0 - q), 1.0)
	# The crack star on the hub glass itself.
	for k in GLASS_SHARDS / 2:
		var a := TAU * k / (GLASS_SHARDS / 2.0) + 0.3
		draw_line(c, c + Vector2(cos(a), sin(a)) * r, Color(Palette.PAPER, 0.9 * (1.0 - q)), 1.5)


func _draw_vhs(s: Dictionary) -> void:
	var p := _p(s)
	var r: Rect2 = s["rect"]
	var o := _local(r.position)
	var frame := Engine.get_process_frames()
	for k in VHS_BANDS:
		var y := o.y + fmod((_h(k, frame >> 1) + p) * r.size.y, r.size.y)
		var x := (_h(frame, k, 3) - 0.5) * 2.0 * float(s["jitter"])
		draw_rect(Rect2(Vector2(o.x + x, y), Vector2(r.size.x, VHS_BAND_PX)), Color(Palette.PAPER, 0.22 * (1.0 - p)))
		draw_rect(Rect2(Vector2(o.x - x, y + VHS_BAND_PX), Vector2(r.size.x, 1.0)), Color(Palette.CELL_PINK, 0.25 * (1.0 - p)))
	# Tape-rewind marks: two left-pointing triangles in the corner.
	var m := o + Vector2(12, 12)
	for k in 2:
		var x0 := m.x + k * 12.0
		draw_colored_polygon(PackedVector2Array([Vector2(x0, m.y + 7), Vector2(x0 + 11, m.y), Vector2(x0 + 11, m.y + 14)]), Color(Palette.PAPER, 0.9 * (1.0 - p)))


func _draw_word(s: Dictionary) -> void:
	var a := float(s["age"]) - float(s.get("delay", 0.0))
	var land := float(s["land"])
	var q := clampf(a / land, 0.0, 1.0) if land > 0.0 else 1.0
	var sc := lerpf(float(s["from"]), 1.0, Tween.interpolate_value(0.0, 1.0, q, 1.0, Tween.TRANS_BACK, Tween.EASE_OUT))
	var alpha := minf(1.0, q * 2.0) * (1.0 - clampf((_p(s) - (1.0 - FADE_SHARE)) / FADE_SHARE, 0.0, 1.0))
	var fs := roundi(WORD_FONT * Settings.text_scale * sc)
	var text := String(s["text"])
	var w := Palette.marker().get_string_size(text, HORIZONTAL_ALIGNMENT_LEFT, -1, fs).x
	var base := _local(s["at"]) + Vector2(-w * 0.5, fs * 0.35)
	draw_string_outline(Palette.marker(), base, text, HORIZONTAL_ALIGNMENT_LEFT, -1, fs, NUMBER_OUTLINE + 2, Color(Palette.NIGHT_SKY, alpha))
	draw_string(Palette.marker(), base, text, HORIZONTAL_ALIGNMENT_LEFT, -1, fs, Color(s["color"], alpha))


func _draw_pile(s: Dictionary) -> void:
	var a := float(s["age"])
	var fade := float(s["fade"])
	var alpha := float(s["alpha"]) * minf(1.0, a / maxf(0.001, fade)) * minf(1.0, (float(s["dur"]) - a) / maxf(0.001, fade))
	var size := PILE_SIZE * Settings.text_scale
	var c := _local(s["at"])
	for k in PILE_LAYERS:
		var r := Rect2(c - size * 0.5 + Vector2(k * 2.0, -k * 2.0), size)
		draw_rect(r, Color(Palette.INK, alpha))
		draw_rect(r, Color(Palette.PAPER, alpha), false, 1.5)
	draw_rect(Rect2(c - size * 0.5 + Vector2(size.x * 0.3, -6.0), Vector2(size.x * 0.4, 6.0)), Color(Palette.TAPE, alpha))


func _draw_embers(s: Dictionary) -> void:
	var p := _p(s)
	var r: Rect2 = s["rect"]
	var o := _local(r.position)
	for k in EMBERS:
		var x := o.x + r.size.x * _h(k, int(s["serial"]))
		var y := o.y + r.size.y * (1.0 - p * (0.6 + 0.8 * _h(k, 5, int(s["serial"]))))
		var col := Palette.CELL_ACID if k % 3 == 0 else Palette.CELL_PINK
		draw_circle(Vector2(x, y), 2.0 + 2.0 * (1.0 - p), Color(col, 1.0 - p))
