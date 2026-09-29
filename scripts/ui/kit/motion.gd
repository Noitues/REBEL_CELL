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
## A pop grows easing out (it springs up) and settles with its entry's ease and trans
## (ANIM-R6 D2: one named shape for every pop-like motion drawn by hand).
const POP_GROW_EASE := Tween.EASE_OUT
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
## ANIM-R5 (the motion lab's check that each demo exercises its own entry): while true,
## every entry read is noted in `reads` with the script that asked for it (the first
## caller outside this kit). Dev and test only; off in play.
static var recording: bool = false
## Entry reads while `recording`: {id: {script path: true}}.
static var reads: Dictionary = {}
## ANIM-R6 D3: `live` questions while `recording`, {id: {script path: true}}: which script
## asked whether the entry plays (the kit's helpers ask for their caller). A view that
## reads an entry's time to animate but never asks is a view that ignores the switch.
static var asks: Dictionary = {}


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
	if recording:
		_note_read(id)
	if not _index.has(id):
		push_error("Motion: no entry '%s' in %s." % [id, CONFIG_PATH])
		return null
	return _index[id]


## ANIM-R5: starts noting entry reads afresh (see `recording`).
static func start_recording() -> void:
	reads.clear()
	asks.clear()
	recording = true


## ANIM-R5: stops noting entry reads; returns what was read ({id: {script path: true}}).
static func stop_recording() -> Dictionary:
	recording = false
	return reads.duplicate(true)


## The scripts that read `id` while recording (paths), sorted.
static func readers(id: StringName) -> Array[String]:
	var out: Array[String] = []
	for p in reads.get(id, {}):
		out.append(String(p))
	out.sort()
	return out


## ANIM-R6 D3: the scripts that asked `live(id)` while recording (paths), sorted.
static func askers(id: StringName) -> Array[String]:
	var out: Array[String] = []
	for p in asks.get(id, {}):
		out.append(String(p))
	out.sort()
	return out


static func _note_read(id: StringName) -> void:
	_note(reads, id)


## Notes `id` in `into` for the first caller outside this kit.
static func _note(into: Dictionary, id: StringName) -> void:
	var own := (Motion as Script).resource_path
	for frame in get_stack():
		var src := String(frame.get("source", ""))
		if src != own:
			if not into.has(id):
				into[id] = {}
			into[id][src] = true
			return


## True when `id` has an entry.
static func has(id: StringName) -> bool:
	config()
	return _index.has(id)


## Seconds for `id` at the current speed (0 when unknown). ANIM-R5: 0 for a switched-off
## part of another motion (UiMotionData.OFF_PARTS: it takes no time).
static func seconds(id: StringName) -> float:
	var e := entry(id)
	if e == null or part_off(e):
		return 0.0
	return e.duration / maxf(speed, SPEED_MIN)


## Delay seconds for `id` at the current speed (0 when unknown, or a switched-off part).
static func delay_of(id: StringName) -> float:
	var e := entry(id)
	if e == null or part_off(e):
		return 0.0
	return e.delay / maxf(speed, SPEED_MIN)


## Amplitude of `id` (px, scale, alpha or degrees as its entry says; 0 when unknown).
## ANIM-R5: a switched-off part of another motion gives the value that shows no motion
## (UiMotionData.OFF_PARTS: 0 for a share, px or frames, 1 for a scale).
static func amplitude(id: StringName) -> float:
	var e := entry(id)
	if e == null:
		return 0.0
	if part_off(e):
		return float(UiMotionData.OFF_PARTS[e.id])
	return e.amplitude


## ANIM-R5: true when `e` is a part of another motion (UiMotionData.OFF_PARTS) switched off.
## Every other entry honours `enabled` through live() (its own motion shows its end state).
static func part_off(e: UiMotionEntryData) -> bool:
	return e != null and not e.enabled and UiMotionData.OFF_PARTS.has(e.id)


## True when animated effects may play at all: effects on (not reduce effects) and a
## real display (or force_live).
static func animating() -> bool:
	if not Fx.effects_enabled():
		return false
	return force_live or DisplayServer.get_name() != "headless"


## True when `id` animates now (animating() and its entry is enabled).
static func live(id: StringName) -> bool:
	if recording:
		_note(asks, id)
	var e := entry(id)
	return e != null and e.enabled and animating()


## ANIM-R6 D3: seconds of `id`'s motion when it plays now (`live`), else 0: for a view
## that builds a timed motion of its own (a drawn motion, a part of a tween chain) and must
## show its end state at once when the entry is switched off, under reduce effects or
## headless.
static func seconds_live(id: StringName) -> float:
	return seconds(id) if live(id) else 0.0


## ANIM-R6 D3: true when `id`'s entry is switched on (`enabled`), whatever reduce effects
## or the display say: for a piece that plays its own reduced form under reduce effects
## (the reduced jack) or a reading time that holds anyway. Noted as an ask while
## recording, as `live` is.
static func switched_on(id: StringName) -> bool:
	if recording:
		_note(asks, id)
	var e := entry(id)
	return e != null and e.enabled


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
	tw.tween_method(_setter(node, ^"scale"), base, base * amplitude(id), d * POP_GROW_SHARE).set_ease(POP_GROW_EASE).set_trans(e.trans)
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
