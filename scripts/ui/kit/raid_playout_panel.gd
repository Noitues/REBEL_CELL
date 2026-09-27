class_name RaidPlayoutPanel
extends VBoxContainer
## Raid playout (GDD 7.2, 9.3): plays a resolved raid's events step by step with 1x / 2x /
## 4x speed and Skip, drives the map's threat markers (a GridMapView or a CityMapOverlay,
## both expose `threat_markers`) and reports the step log in a zine note. The result is
## precomputed and deterministic; this panel is presentation only. Emits finished when
## the last step has played.
##
## Animation pass ANIM-5 (raid execution): on a CityMapOverlay the raid plays as motion
## (`attach_fx`: a RaidFxLayer on the map). Each step's beats and length come from
## RaidBeats, built from the resolver's events (never recomputed); the panel's clock runs
## at Motion.speed, which the speed buttons set (1x / 2x / 4x, back to 1x when the playout
## ends) so every beat scales. Skip jumps every beat to its end and emits `skipped` (the
## screens go straight to the summary); a click or accept press ends the current step's
## motion. Instant (tests, headless, reduce effects): every step and beat at once.

signal finished
## Skip was pressed: the playout jumped to its end (screens show the summary).
signal skipped

## The map the threats are shown on: a GridMapView or a CityMapOverlay (both expose
## `threat_markers`).
var grid_view: Control = null
var log_note: ZineNote
var step_label: Label
var speed: float = 1.0
## The motion layer on a CityMapOverlay (null on a GridMapView or with no map).
var fx: RaidFxLayer = null
var _steps: Array = []  # Array[Array[Dictionary]] grouped by step (RaidBeats.group)
var _threat_sites: Dictionary = {}  # threat id -> site
var _threat_names: Dictionary = {}
var _dead: Dictionary = {}
var _index: int = 0
var _done: bool = false
var _instant: bool = false
## The playout clock (seconds at 1x; advances at Motion.speed) and when the next step
## starts on it.
var _clock: float = 0.0
var _next_at: float = 0.0
var _set_speed: bool = false


func _init(p_grid_view: Control = null, log_size: Vector2 = Vector2(600, 120)) -> void:
	grid_view = p_grid_view
	TextDb.shown_as_given(self)  # H24 S4: its words translated here, shown as given
	var controls := HBoxContainer.new()
	add_child(controls)
	step_label = Label.new()
	step_label.text = tr("Setup")
	step_label.custom_minimum_size.x = 90
	step_label.add_theme_font_override("font", Palette.display())
	step_label.add_theme_font_size_override("font_size", 22)
	step_label.add_theme_color_override("font_color", Palette.CELL_ACID)
	controls.add_child(step_label)
	for s in [1.0, 2.0, 4.0]:
		var b := Button.new()
		b.text = "%dx" % int(s)
		var value: float = s
		b.pressed.connect(func() -> void: set_speed(value))
		controls.add_child(b)
	var skip := Button.new()
	skip.name = "Skip"
	skip.text = tr("Skip")
	skip.pressed.connect(skip_pressed)
	controls.add_child(skip)
	log_note = ZineNote.new(tr("PLAYOUT"), log_size)
	log_note.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	add_child(log_note)


func _exit_tree() -> void:
	_restore_speed()


## Puts the raid's motion on the map (a CityMapOverlay): `results` is the resolved raid
## (campaign.last_raid / RaidResult.to_dict), `home` the home Site, `home_max` its full
## integrity, `color` the threats' colour. Call before `play`.
func attach_fx(results: Dictionary, home: StringName, home_max: int, color: Color) -> RaidFxLayer:
	if not (grid_view is CityMapOverlay):
		return null
	var overlay := grid_view as CityMapOverlay
	if fx == null or not is_instance_valid(fx):
		fx = RaidFxLayer.new(overlay)
		overlay.add_child(fx)
	fx.setup(results, home, home_max, color)
	overlay.draw_markers = false
	return fx


## Loads a raid's events and starts playing. `instant` (tests, reduce-effects) shows all.
func play(events: Array[Dictionary], instant: bool = false) -> void:
	_threat_sites.clear()
	_threat_names.clear()
	_dead.clear()
	_index = 0
	_done = false
	_instant = instant
	_clock = 0.0
	_next_at = 0.0
	_steps = RaidBeats.group(events)
	log_note.clear()
	if _instant:
		skip_to_end()
	else:
		_show_step()


## 1x / 2x / 4x: the playout and every motion it builds run this much faster.
func set_speed(value: float) -> void:
	speed = maxf(Motion.SPEED_MIN, value)
	Motion.set_speed(speed)
	_set_speed = true


func steps_total() -> int:
	return _steps.size()


func current_step() -> int:
	return _index


func is_done() -> bool:
	return _done


## The playout clock now (seconds at 1x).
func clock() -> float:
	return _clock


## The Skip button: every step and beat at its end, then `skipped` (the screen shows the
## summary).
func skip_pressed() -> void:
	skip_to_end()
	skipped.emit()


func skip_to_end() -> void:
	while _index < _steps.size():
		var tl := RaidBeats.timeline(_steps[_index])
		_apply_step(_steps[_index], _clock, tl)
		_clock += float(tl["seconds"])
		_index += 1
	_next_at = _clock
	if fx != null and is_instance_valid(fx):
		fx.clock = _clock
		fx.finish_all()
		_clock = fx.clock
	_finish()


func _process(delta: float) -> void:
	if _done or _instant or _steps.is_empty():
		return
	_clock += delta * Motion.speed
	if fx != null and is_instance_valid(fx):
		fx.clock = _clock
	if _clock >= _next_at:
		_show_step()


## A click or accept press ends the current step's motion (input skips to the end).
func _unhandled_input(event: InputEvent) -> void:
	if _done or _instant or not is_visible_in_tree():
		return
	var click: bool = event is InputEventMouseButton and event.pressed and (event as InputEventMouseButton).button_index == MOUSE_BUTTON_LEFT
	if click or event.is_action_pressed(&"ui_accept"):
		_clock = maxf(_clock, _next_at)
		if fx != null and is_instance_valid(fx):
			fx.clock = _clock
		get_viewport().set_input_as_handled()


func _show_step() -> void:
	if _index >= _steps.size():
		_finish()
		return
	var start := _clock
	var tl := RaidBeats.timeline(_steps[_index])
	_apply_step(_steps[_index], start, tl)
	_index += 1
	_next_at = start + float(tl["seconds"])
	if not is_inside_tree():
		skip_to_end()


func _apply_step(events: Array, start: float = 0.0, tl: Dictionary = {}) -> void:
	for e in events:
		var t: String = e.get("type", "")
		match t:
			"threat_enters":
				_threat_sites[e["threat"]] = e["site"]
				_threat_names[e["threat"]] = String(e["text"]).get_slice(": ", 1).get_slice(" enters", 0)
			"move":
				_threat_sites[e["threat"]] = e["to"]
			"threat_destroyed":
				_dead[e["threat"]] = true
			"home_hit":
				_dead[e["threat"]] = true
		if e.has("text"):
			log_note.append(String(e["text"]))
		if t == "raid_end":
			step_label.text = tr("Raid over")
		elif e.has("step"):
			step_label.text = tr("Step %d") % int(e["step"]) if int(e["step"]) > 0 else tr("Setup")
	if fx != null and is_instance_valid(fx):
		for b: Dictionary in tl.get("beats", []):
			fx.play_beat(b, start + float(b["t0"]))
	if grid_view != null:
		var markers := {}
		for id in _threat_sites:
			if _dead.has(id):
				continue
			markers.get_or_add(_threat_sites[id], []).append(_threat_names.get(id, String(id)))
		grid_view.set("threat_markers", markers)
		grid_view.queue_redraw()


func _finish() -> void:
	if _done:
		return
	_done = true
	_restore_speed()
	if fx != null and is_instance_valid(fx):
		fx.release()
	finished.emit()


func _restore_speed() -> void:
	if _set_speed:
		_set_speed = false
		Motion.set_speed(1.0)
