class_name RaidPlayoutPanel
extends VBoxContainer
## Raid playout (GDD 7.2, 9.3): steps through a resolved raid's events with 1x / 2x / 4x
## speed and skip, drives a GridMapView's threat markers so the threat paths animate, and
## reports the step log in a zine note. The result is precomputed and deterministic; this
## panel is presentation only. Emits finished when the last step has been shown.

signal finished

const STEP_SECONDS := 0.9

## The map the threats are shown on: a GridMapView or a CityMapOverlay (both expose
## `threat_markers`).
var grid_view: Control = null
var log_note: ZineNote
var step_label: Label
var speed: float = 1.0
var _steps: Array = []  # Array[Array[Dictionary]] grouped by step, index 0 = setup
var _threat_sites: Dictionary = {}  # threat id -> site
var _threat_names: Dictionary = {}
var _dead: Dictionary = {}
var _index: int = 0
var _timer: SceneTreeTimer = null
var _done: bool = false
var _instant: bool = false


func _init(p_grid_view: Control = null, log_size: Vector2 = Vector2(600, 120)) -> void:
	grid_view = p_grid_view
	var controls := HBoxContainer.new()
	add_child(controls)
	step_label = Label.new()
	step_label.text = "Setup"
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
	skip.text = "Skip"
	skip.pressed.connect(skip_to_end)
	controls.add_child(skip)
	log_note = ZineNote.new("PLAYOUT", log_size)
	log_note.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	add_child(log_note)


## Loads a raid's events and starts playing. `instant` (tests, reduce-effects) shows all.
func play(events: Array[Dictionary], instant: bool = false) -> void:
	_steps = []
	_threat_sites.clear()
	_threat_names.clear()
	_dead.clear()
	_index = 0
	_done = false
	_instant = instant
	var by_step := {}
	var max_step := 0
	for e in events:
		var step := int(e.get("step", 0))
		if e.get("type", "") == "raid_end":
			step = -1
		by_step.get_or_add(step, []).append(e)
		max_step = maxi(max_step, step)
	for s in max_step + 1:
		_steps.append(by_step.get(s, []))
	if by_step.has(-1):
		_steps.append(by_step[-1])
	log_note.clear()
	if _instant:
		skip_to_end()
	else:
		_show_step()


func set_speed(value: float) -> void:
	speed = maxf(0.25, value)


func steps_total() -> int:
	return _steps.size()


func current_step() -> int:
	return _index


func is_done() -> bool:
	return _done


func skip_to_end() -> void:
	if _timer != null:
		_timer = null
	while _index < _steps.size():
		_apply_step(_steps[_index])
		_index += 1
	_finish()


func _show_step() -> void:
	if _index >= _steps.size():
		_finish()
		return
	_apply_step(_steps[_index])
	_index += 1
	if _index >= _steps.size():
		_finish()
		return
	if not is_inside_tree():
		skip_to_end()
		return
	_timer = get_tree().create_timer(STEP_SECONDS / speed)
	var t := _timer
	_timer.timeout.connect(func() -> void:
		if _timer == t and not _done:
			_show_step())


func _apply_step(events: Array) -> void:
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
			step_label.text = "Raid over"
		elif e.has("step"):
			step_label.text = "Step %d" % int(e["step"]) if int(e["step"]) > 0 else "Setup"
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
	finished.emit()
