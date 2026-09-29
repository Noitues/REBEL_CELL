class_name Motion
extends RefCounted
## Motion kit (ANIMATION_HANDOFF 3, STYLE_GUIDE 5): builds UI tweens from the timings in
## `content/config/ui_motion.tres`, looked up by animation id, so no duration, ease or
## amplitude lives inline. View only: it moves nodes and never touches game state, game
## RNG or content. Under reduce effects, in headless runs (tests) and for a disabled entry
## every helper applies the end state at once and returns null, so nothing ever waits on a
## tween. Never `await` a Motion tween inside a rule path.

const CONFIG_PATH := "res://content/config/ui_motion.tres"
## Playback speed range: the motion lab offers SPEED_MIN..LAB_SPEED_MAX; raid playback
## runs 1x/2x/4x (hq_scene), so the kit accepts up to SPEED_MAX.
const SPEED_MIN := 0.25
const SPEED_MAX := 4.0
const LAB_SPEED_MAX := 2.0
## A shake is this many steps across its duration: out, across, out, home.
const SHAKE_STEPS := 4
## A blink spends this share of its duration dipping and the rest coming back.
const BLINK_DIP_SHARE := 1.0 / 3.0
## A pop spends this share of its duration growing and the rest settling.
const POP_GROW_SHARE := 0.4
## Node meta holding a running helper tween and the value it returns to (so a helper
## started again mid-motion settles on the true rest value, not a mid-way one).
const META_PREFIX := "motion_"

## Multiplies every speed: 2.0 plays twice as fast (half the seconds). Clamped to
## SPEED_MIN..SPEED_MAX by set_speed().
static var speed: float = 1.0
## Tests and frame capture: animate even under a headless display server. Reduce effects
## and disabled entries still win.
static var force_live: bool = false

static var _config: UiMotionData = null
static var _index: Dictionary = {}


## The motion table in use (loaded from CONFIG_PATH on first use).
static func config() -> UiMotionData:
	if _config == null:
		use_config(load(CONFIG_PATH) as UiMotionData)
	return _config


## Uses `cfg` instead of the file (the motion lab tunes a duplicate, never the loaded
## resource); null goes back to the file.
static func use_config(cfg: UiMotionData) -> void:
	_config = cfg
	_index.clear()
	if cfg == null:
		return
	for e in cfg.entries:
		if e != null and not _index.has(e.id):
			_index[e.id] = e


## Sets the playback speed multiplier, clamped to SPEED_MIN..SPEED_MAX.
static func set_speed(value: float) -> void:
	speed = clampf(value, SPEED_MIN, SPEED_MAX)


## The entry for `id`, or null (with an error) when the table has none.
static func entry(id: StringName) -> UiMotionEntryData:
	config()
	if not _index.has(id):
		push_error("Motion: no entry '%s' in %s." % [id, CONFIG_PATH])
		return null
	return _index[id]


## True when `id` has an entry.
static func has(id: StringName) -> bool:
	config()
	return _index.has(id)


## Seconds for `id` at the current speed (0 when unknown).
static func seconds(id: StringName) -> float:
	var e := entry(id)
	return e.duration / maxf(speed, SPEED_MIN) if e != null else 0.0


## Delay seconds for `id` at the current speed (0 when unknown).
static func delay_of(id: StringName) -> float:
	var e := entry(id)
	return e.delay / maxf(speed, SPEED_MIN) if e != null else 0.0


## Amplitude of `id` (px, scale, alpha or degrees as its entry says; 0 when unknown).
static func amplitude(id: StringName) -> float:
	var e := entry(id)
	return e.amplitude if e != null else 0.0


## True when animated effects may play at all: effects on (not reduce effects) and a
## real display (or force_live).
static func animating() -> bool:
	if not Fx.effects_enabled():
		return false
	return force_live or DisplayServer.get_name() != "headless"


## True when `id` animates now (animating() and its entry is enabled).
static func live(id: StringName) -> bool:
	var e := entry(id)
	return e != null and e.enabled and animating()


## Tweens `property` of `node` to `to` with `id`'s timing. Returns the tween, or null
## with `to` applied at once when the motion doesn't play.
static func run(id: StringName, node: Node, property: NodePath, to: Variant) -> Tween:
	_settle(node, property)
	if not live(id):
		node.set_indexed(property, to)
		_redraw(node)
		return null
	var e := entry(id)
	var tw := node.create_tween()
	tw.tween_method(_setter(node, property), node.get_indexed(property), to, seconds(id)) \
		.set_delay(delay_of(id)).set_ease(e.ease).set_trans(e.trans)
	_hold(node, property, tw, to)
	return tw


## Fades `node`'s modulate alpha to `to_alpha`.
static func fade(node: CanvasItem, to_alpha: float, id: StringName) -> Tween:
	return run(id, node, ^"modulate:a", to_alpha)


## A pop: scale grows to its rest scale x amplitude and settles back. Controls pop about
## their centre.
static func pop(node: CanvasItem, id: StringName) -> Tween:
	var base: Vector2 = _settle(node, ^"scale")
	if node is Control:
		(node as Control).pivot_offset = (node as Control).size * 0.5
	if not live(id):
		node.set(&"scale", base)
		return null
	var e := entry(id)
	var d := seconds(id)
	var tw := node.create_tween()
	tw.tween_interval(delay_of(id))
	tw.tween_method(_setter(node, ^"scale"), base, base * amplitude(id), d * POP_GROW_SHARE).set_ease(Tween.EASE_OUT).set_trans(e.trans)
	tw.tween_method(_setter(node, ^"scale"), base * amplitude(id), base, d * (1.0 - POP_GROW_SHARE)).set_ease(e.ease).set_trans(e.trans)
	_hold(node, ^"scale", tw, base)
	return tw


## Slides `node` in: it starts at its rest position + `from` and eases home.
static func slide_in(node: CanvasItem, from: Vector2, id: StringName) -> Tween:
	var base: Vector2 = _settle(node, ^"position")
	if not live(id):
		node.set(&"position", base)
		return null
	var e := entry(id)
	node.set(&"position", base + from)
	var tw := node.create_tween()
	tw.tween_method(_setter(node, ^"position"), base + from, base, seconds(id)).set_delay(delay_of(id)).set_ease(e.ease).set_trans(e.trans)
	_hold(node, ^"position", tw, base)
	return tw


## A horizontal shake of `amplitude` px on a Vector2 `property` (position, or a view's
## own `shake` offset) in SHAKE_STEPS steps, ending where it started.
static func shake(node: CanvasItem, id: StringName, property: NodePath = ^"position") -> Tween:
	var base: Vector2 = _settle(node, property)
	if not live(id):
		node.set_indexed(property, base)
		_redraw(node)
		return null
	var e := entry(id)
	var step := seconds(id) / SHAKE_STEPS
	var a := Vector2(amplitude(id), 0.0)
	var tw := node.create_tween()
	tw.tween_interval(delay_of(id))
	var at := base
	for i in SHAKE_STEPS:
		var to := base if i == SHAKE_STEPS - 1 else base + (a if i % 2 == 0 else -a)
		tw.tween_method(_setter(node, property), at, to, step).set_ease(e.ease).set_trans(e.trans)
		at = to
	_hold(node, property, tw, base)
	return tw


## A blink: modulate alpha dips to `amplitude` and comes back to 1.
static func blink(node: CanvasItem, id: StringName) -> Tween:
	_settle(node, ^"modulate:a")
	node.modulate.a = 1.0
	if not live(id):
		return null
	var e := entry(id)
	var d := seconds(id)
	var tw := node.create_tween()
	tw.tween_interval(delay_of(id))
	tw.tween_property(node, ^"modulate:a", amplitude(id), d * BLINK_DIP_SHARE).set_ease(e.ease).set_trans(e.trans)
	tw.tween_property(node, ^"modulate:a", 1.0, d * (1.0 - BLINK_DIP_SHARE)).set_ease(e.ease).set_trans(e.trans)
	_hold(node, ^"modulate:a", tw, 1.0)
	return tw


## A looping pulse of a float `property` between 1.0 and `amplitude`, `duration` per half
## (migration flicker, breathing rings). Null when the motion doesn't play; the caller
## shows its static state then. Kill the returned tween to stop it.
static func loop_pulse(node: CanvasItem, property: NodePath, id: StringName) -> Tween:
	_settle(node, property)
	if not live(id):
		return null
	var e := entry(id)
	var d := seconds(id)
	var tw := node.create_tween().set_loops()
	tw.tween_method(_setter(node, property), 1.0, amplitude(id), d).set_ease(e.ease).set_trans(e.trans)
	tw.tween_method(_setter(node, property), amplitude(id), 1.0, d).set_ease(e.ease).set_trans(e.trans)
	_hold(node, property, tw, 1.0)
	return tw


## Rolls `label`'s number from `from` to `to`, formatted with `fmt`.
static func number_roll(label: Control, from: int, to: int, id: StringName, fmt: String = "%d") -> Tween:
	_settle(label, ^"text")
	if not live(id) or from == to:
		label.set(&"text", fmt % to)
		return null
	var e := entry(id)
	var tw := label.create_tween()
	tw.tween_method(func(v: float) -> void: label.set(&"text", fmt % roundi(v)), float(from), float(to), seconds(id)) \
		.set_delay(delay_of(id)).set_ease(e.ease).set_trans(e.trans)
	_hold(label, ^"text", tw, fmt % to)
	return tw


## Stops every helper tween still running on `node` and puts each property back at the
## value its motion rests at (e.g. before replaying, or when a view is reused).
static func stop(node: Node) -> void:
	for key in node.get_meta_list():
		if not String(key).begins_with(META_PREFIX):
			continue
		var held: Array = node.get_meta(key)
		node.remove_meta(key)
		var tw: Tween = held[0]
		if tw != null and tw.is_valid():
			tw.kill()
		node.set_indexed(held[2], held[1])
	_redraw(node)


## The .tres lines for `e` (the motion lab's "copy values").
static func tres_lines(e: UiMotionEntryData) -> String:
	return "id = &\"%s\"\nduration = %s\ndelay = %s\nease = %d\ntrans = %d\namplitude = %s\n%s" % [
		e.id, _num(e.duration), _num(e.delay), e.ease, e.trans, _num(e.amplitude),
		"" if e.enabled else "enabled = false\n"]


static func _num(v: float) -> String:
	var s := String.num(v, 4)
	return s if s.contains(".") else s + ".0"


## A setter for tween_method that also redraws custom-drawn views.
static func _setter(node: Node, property: NodePath) -> Callable:
	return func(v: Variant) -> void:
		if is_instance_valid(node):
			node.set_indexed(property, v)
			_redraw(node)


static func _redraw(node: Node) -> void:
	if node is CanvasItem:
		(node as CanvasItem).queue_redraw()


## Stops a helper tween still running on `node`'s `property` and returns the value that
## motion rests at (the property's current value when none runs).
static func _settle(node: Node, property: NodePath) -> Variant:
	var key := META_PREFIX + String(property).replace(":", "_")
	if node.has_meta(key):
		var held: Array = node.get_meta(key)
		node.remove_meta(key)
		var tw: Tween = held[0]
		if tw != null and tw.is_valid():
			tw.kill()
		node.set_indexed(property, held[1])
		return held[1]
	return node.get_indexed(property)


static func _hold(node: Node, property: NodePath, tw: Tween, rest: Variant) -> void:
	var key := META_PREFIX + String(property).replace(":", "_")
	node.set_meta(key, [tw, rest, property])
	# Captures the tween's id, not the tween: a lambda holding its own tween is a cycle.
	var tw_id := tw.get_instance_id()
	tw.finished.connect(func() -> void:
		if is_instance_valid(node) and node.has_meta(key):
			var held: Array = node.get_meta(key)
			if held[0] != null and (held[0] as Tween).get_instance_id() == tw_id:
				node.remove_meta(key))


# --- Art pass W9: reduce motion and resolve speed (ART_BIBLE §12, §10) ----------------
# Settings-only questions; the helpers above are unchanged. Reduce motion is separate
# from reduce effects: a caller that also animates checks `live(id)` as before.

## page_transition_style(): pages slide in (the material's direction, §10).
const PAGE_SLIDE := &"slide"
## page_transition_style(): pages cross-fade (reduce motion).
const PAGE_FADE := &"fade"
## Settings.resolve_speed -> the factor on the SEND IT resolve's seconds (0 = instant:
## the end state at once, as the headless path shows it).
const RESOLVE_TIME_SCALES := {&"x1": 1.0, &"x2": 0.5, &"instant": 0.0}
## The input action held to fast-forward the resolve (project.godot, rebindable).
const FAST_FORWARD_ACTION := &"resolve_fast_forward"
## The resolve's time factor while fast-forward is held (4x, the kit's SPEED_MAX).
const FAST_FORWARD_TIME_SCALE := 1.0 / SPEED_MAX


## False under reduce motion: city and map cameras cut to their end framing (no pans,
## leans, zoom travels or jack pushes).
static func camera_moves_allowed() -> bool:
	return not _reduce_motion()


## False under reduce motion: no parallax layers or pointer leans.
static func parallax_allowed() -> bool:
	return not _reduce_motion()


## How pages change: PAGE_SLIDE, or PAGE_FADE (cross-fades only) under reduce motion.
static func page_transition_style() -> StringName:
	return PAGE_FADE if _reduce_motion() else PAGE_SLIDE


## The factor on the SEND IT resolve's durations from Settings.resolve_speed: 1.0 (1x),
## 0.5 (2x) or 0.0 (instant). Multiply seconds by it; 0 means show the end state at once.
static func resolve_time_scale() -> float:
	return float(RESOLVE_TIME_SCALES.get(_setting(&"resolve_speed", &"x1"), 1.0))


## True when the resolve speed is instant (the end state at once, no tween).
static func resolve_instant() -> bool:
	return resolve_time_scale() <= 0.0


## True while the player holds the fast-forward action (key or pad).
static func fast_forward_held() -> bool:
	return InputMap.has_action(FAST_FORWARD_ACTION) and Input.is_action_pressed(FAST_FORWARD_ACTION)


## The resolve's time factor this frame: resolve_time_scale(), cut to at most
## FAST_FORWARD_TIME_SCALE while fast-forward is held (instant stays 0).
static func resolve_time_scale_now() -> float:
	var k := resolve_time_scale()
	return minf(k, FAST_FORWARD_TIME_SCALE) if fast_forward_held() else k


static func _reduce_motion() -> bool:
	return bool(_setting(&"reduce_motion", false))


## A Settings value read defensively (tools that run without the autoload get `fallback`).
static func _setting(key: StringName, fallback: Variant) -> Variant:
	var loop := Engine.get_main_loop() as SceneTree
	if loop == null or not loop.root.has_node(^"Settings"):
		return fallback
	var v: Variant = loop.root.get_node(^"Settings").get(key)
	return fallback if v == null else v
