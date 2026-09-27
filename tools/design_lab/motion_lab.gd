extends Control
## Motion lab (dev tool, not exported; ANIMATION_HANDOFF 3): loops any animation id from
## content/config/ui_motion.tres on real UI pieces (a ZineCard, a WheelView with a live
## combatant, a StickerButton, SEND IT, a ZinePanel, a number) with sliders for duration,
## delay and amplitude, ease/trans pickers, enabled, and a 0.25x-2x speed control. "Copy
## values" prints the entry's .tres lines (and puts them on the clipboard) to paste back.
## The lab tunes a duplicate of the table (Motion.use_config); the file never changes.
##
## Run:      godot --path . res://tools/design_lab/motion_lab.tscn
## Capture:  godot --path . res://tools/design_lab/motion_lab.tscn -- --demo-anim=card_hover
##   --demo-anim=<id> selects <id> and plays it once, DEMO_START_FRAME frames in, then
##   holds; --demo-speed=<x> sets the speed. See ANIMATION_HANDOFF 6 for Movie Maker.

## The frame (from the first processed frame, 0-based) a --demo-anim capture starts on.
const DEMO_START_FRAME := 6
## Seconds between loop replays after a motion ends.
const LOOP_GAP := 0.6
## Stand-in length for motions that have no duration of their own (Fx freeze, loops).
const LOOP_HOLD := 1.2
## Travel for demos whose amplitude isn't a distance (flights to an icon), px.
const DEMO_TRAVEL := 160.0
## The number a roll counts up to.
const ROLL_TO := 1250
## Text typed by the per-character demos.
const TYPE_TEXT := "> PIRATE RADIO: the grid is listening"
## Control column width and the stage's left edge (px).
const PANEL_W := 380.0
## Slider ranges: duration and delay seconds; amplitude runs to 3x the entry (at least 2).
const DURATION_MAX := 3.0
const DELAY_MAX := 2.0
const AMP_MIN_RANGE := 2.0
const AMP_RANGE_MULT := 3.0
const SLIDER_STEP := 0.005

const EASES := ["IN", "OUT", "IN_OUT", "OUT_IN"]
const TRANSES := ["LINEAR", "SINE", "QUINT", "QUART", "QUAD", "EXPO", "ELASTIC", "CUBIC", "CIRC", "BOUNCE", "BACK", "SPRING"]

## How each id is shown (kind) and on what (target). Unlisted ids pop the sticker.
const DEMOS := {
	&"screen_flash": ["flash", "stage"], &"hit_freeze": ["freeze", "wheel"],
	&"saved_stamp": ["fade_out", "number"], &"toast": ["fade_out", "sticker"],
	&"jack_in": ["jack_in", "stage"], &"jack_out": ["jack_out", "stage"], &"jack_fade_reduced": ["fade_out", "panel"],
	&"wheel_spin": ["spin", "wheel"], &"wheel_spin_blur": ["fade_out", "wheel"], &"wheel_nudge": ["shake", "wheel"],
	&"precision_perfect": ["flash", "wheel"], &"precision_good_ring": ["pop", "wheel"],
	&"precision_partial": ["shake", "wheel"], &"precision_blink": ["blink", "wheel"], &"precision_miss_static": ["blink", "wheel"],
	&"card_hover": ["lift", "card"], &"card_play": ["pop", "card"], &"card_draw": ["slide_x", "card"], &"card_exhaust": ["fade_out", "card"],
	&"send_it_press": ["pop", "send"], &"send_it_drips": ["drop", "send"], &"resolve_pass": ["blink", "wheel"], &"resolve_pulse": ["pop", "wheel"],
	&"number_float": ["lift", "number"], &"number_crit": ["pop", "number"], &"hp_lag": ["fade_out", "wheel"],
	&"intent_flip": ["tilt", "sticker"], &"rewind_scrub": ["shake", "wheel"],
	&"pointer_flicker": ["pulse_pointer", "wheel"], &"orbit_trail": ["fade_out", "wheel"],
	&"enemy_break": ["drop_away", "wheel"], &"hub_shatter": ["shake", "wheel"],
	&"heat_pulse": ["heat", "stage"], &"heat_letters_shake": ["shake", "number"], &"poster_stamp": ["pop", "panel"], &"net_creep": ["fade_out", "panel"],
	&"hq_crt_hum": ["pulse", "panel"], &"radio_type": ["type", "panel"], &"jack_ring_breathe": ["pulse_scale", "sticker"], &"polaroid_tilt": ["tilt", "card"],
	&"site_outline_draw": ["fade_in", "panel"], &"map_camera_ease": ["slide_x", "panel"], &"route_crawl": ["slide_x", "sticker"], &"asset_drop": ["drop", "card"],
	&"raid_move": ["slide_x", "sticker"], &"turret_trace": ["blink", "sticker"], &"raid_flip": ["tilt", "sticker"],
	&"route_pulse": ["blink", "sticker"], &"node_pop": ["pop", "sticker"], &"visited_dim": ["fade_to", "sticker"],
	&"panel_in": ["slide_x", "panel"], &"panel_crt_roll": ["drop", "panel"], &"panel_drop": ["drop", "panel"],
	&"menu_cursor_blink": ["pulse", "number"], &"menu_type": ["type", "panel"], &"menu_highlight": ["slide_x", "sticker"],
	&"modem_sign_warmup": ["blink", "send"], &"modem_trace": ["fade_in", "panel"], &"buy_fly": ["fly", "card"], &"note_flap": ["tilt", "sticker"],
	&"loot_fan": ["slide_x", "card"], &"loot_pick": ["fly", "card"], &"count_up": ["roll", "number"],
	&"dispatch_type": ["type", "panel"], &"subtitle_bar_in": ["drop", "panel"],
	&"drip_grow": ["fade_in", "send"], &"drip_halo": ["pulse", "send"],
	&"beacon_blink": ["pulse", "sticker"], &"city_traffic": ["slide_x", "sticker"], &"hq_sign_flicker": ["blink", "send"],
	&"sticky_bump": ["pop", "sticker"], &"number_roll": ["roll", "number"],
}

var _cfg: UiMotionData
var _id: StringName = &"card_hover"
var _loop := true
var _demo := false
var _frames := 0
var _generation := 0

var _pieces: Dictionary = {}  # target name -> Control
var _rest: Dictionary = {}    # target name -> {position, scale, rotation, modulate}
var _engine: CombatEngine
var _wheel: WheelView
var _number: Label
var _typed: Label
var _stage: Control

var _ids: OptionButton
var _dur: HSlider
var _delay: HSlider
var _amp: HSlider
var _ease: OptionButton
var _trans: OptionButton
var _enabled: CheckBox
var _speed: HSlider
var _loop_box: CheckBox
var _values: Label
var _syncing := false


func _ready() -> void:
	UiTheme.apply(self)
	# Tune a duplicate: the loaded table is never modified (CLAUDE.md rule 3).
	_cfg = (load(Motion.CONFIG_PATH) as UiMotionData).duplicate(true)
	Motion.use_config(_cfg)
	var bg := ColorRect.new()
	bg.color = Palette.NIGHT_SKY
	bg.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	add_child(bg)
	_build_stage()
	_record_rest()
	_build_panel()
	for arg in OS.get_cmdline_user_args():
		if arg.begins_with("--demo-anim="):
			_id = StringName(arg.trim_prefix("--demo-anim="))
			_demo = true
			_loop = false
		elif arg.begins_with("--demo-speed="):
			Motion.set_speed(float(arg.trim_prefix("--demo-speed=")))
	if not Motion.has(_id):
		push_error("motion_lab: no motion id '%s'." % _id)
		_id = &"card_hover"
	_speed.value = Motion.speed
	_loop_box.set_pressed_no_signal(_loop)
	_select(_id)


func _exit_tree() -> void:
	Motion.use_config(null)
	Motion.set_speed(1.0)


func _process(_delta: float) -> void:
	if _demo and _frames == DEMO_START_FRAME:
		print("motion_lab: %s starts on frame %d (speed %.2fx)" % [_id, _frames, Motion.speed])
		_play()
	_frames += 1


# --- Stage ------------------------------------------------------------------------------

func _build_stage() -> void:
	_stage = Control.new()
	_stage.position = Vector2(PANEL_W, 0)
	_stage.size = Vector2(1280 - PANEL_W, 720)
	add_child(_stage)
	var sticker := StickerButton.new("SITE T1", Palette.NOTE_YELLOW, -3.0)
	sticker.position = Vector2(40, 40)
	_add_piece("sticker", sticker)
	var panel := ZinePanel.new("DISPATCH", 1.5)
	panel.position = Vector2(40, 140)
	panel.size = Vector2(260, 150)
	_typed = Label.new()
	_typed.autowrap_mode = TextServer.AUTOWRAP_WORD_SMART
	_typed.text = TYPE_TEXT
	panel.content.add_child(_typed)
	_add_piece("panel", panel)
	var card := ZineCard.new("OVERCLOCK", 2, "Deal 8. Nudge +1.", 0)
	card.position = Vector2(60, 400)
	card.size = card.custom_minimum_size
	_add_piece("card", card)
	_number = Label.new()
	_number.text = "HEAT 42"
	_number.add_theme_font_override("font", Palette.marker())
	_number.add_theme_font_size_override("font_size", 40)
	_number.add_theme_color_override("font_color", Palette.CELL_PINK)
	_number.position = Vector2(620, 40)
	_add_piece("number", _number)
	var send := DripButton.new("SEND IT", "[Space]", DripButton.DRIP_PINK, 44, DripButton.SEND_IT_DRIPS)
	send.position = Vector2(600, 540)
	send.size = send.custom_minimum_size
	_add_piece("send", send)
	_wheel = WheelView.new()
	_wheel.position = Vector2(300, 120)
	_wheel.size = Vector2(380, 380)
	_add_piece("wheel", _wheel)
	_engine = CombatEngine.new()
	add_child(_engine)
	var enemies: Array[StringName] = [&"collections_agent"]
	_engine.start_fight(&"breaker", enemies, 1, &"rank:1")
	var player := _engine.state().player
	var sats: Array[CombatantState] = []
	_wheel.show_combatant(player, sats, _engine.readouts(player), _engine.resolver.lookup)
	_pieces["stage"] = _stage


func _add_piece(key: String, c: Control) -> void:
	_stage.add_child(c)
	_pieces[key] = c


func _record_rest() -> void:
	for key in _pieces:
		var c: Control = _pieces[key]
		_rest[key] = {"position": c.position, "scale": c.scale, "rotation": c.rotation, "modulate": c.modulate}


func _reset_stage() -> void:
	for key in _pieces:
		var c: Control = _pieces[key]
		Motion.stop(c)
		if _rest.has(key):
			var r: Dictionary = _rest[key]
			c.position = r["position"]
			c.scale = r["scale"]
			c.rotation = r["rotation"]
			c.modulate = r["modulate"]
		c.pivot_offset = c.size * 0.5
	_wheel.shake = Vector2.ZERO
	_wheel.pointer_alpha = 1.0
	_wheel.queue_redraw()
	_number.text = "HEAT 42"
	_typed.visible_ratio = 1.0


# --- Playback ---------------------------------------------------------------------------

## Plays the selected motion once on its piece; loops (after LOOP_GAP) when looping.
func _play() -> void:
	_generation += 1
	_reset_stage()
	var e := Motion.entry(_id)
	if e == null:
		return
	var demo: Array = DEMOS.get(_id, ["pop", "sticker"])
	var target: Control = _pieces[demo[1]]
	var amp := e.amplitude
	var length := Motion.delay_of(_id) + Motion.seconds(_id)
	match String(demo[0]):
		"pop":
			Motion.pop(target, _id)
		"pulse_scale":
			Motion.pop(target, _id)
		"lift":
			Motion.run(_id, target, ^"position:y", target.position.y - amp)
		"drop":
			Motion.slide_in(target, Vector2(0, -amp), _id)
		"drop_away":
			Motion.run(_id, target, ^"position:y", target.position.y + amp)
		"slide_x":
			Motion.slide_in(target, Vector2(-(amp if amp > 1.0 else DEMO_TRAVEL), 0), _id)
		"fly":
			Motion.run(_id, target, ^"position", target.position + Vector2(DEMO_TRAVEL * 2.0, -DEMO_TRAVEL))
		"shake":
			Motion.shake(target, _id, ^"shake" if target is WheelView else ^"position")
		"blink":
			Motion.blink(target, _id)
		"pulse":
			Motion.loop_pulse(target, ^"modulate:a", _id)
			length = LOOP_HOLD * 2.0
		"pulse_pointer":
			Motion.loop_pulse(target, ^"pointer_alpha", _id)
			length = LOOP_HOLD * 2.0
		"fade_out":
			Motion.fade(target, 0.0, _id)
		"fade_to":
			Motion.fade(target, amp, _id)
		"fade_in":
			target.modulate.a = 0.0
			Motion.fade(target, 1.0, _id)
		"tilt":
			Motion.run(_id, target, ^"rotation_degrees", target.rotation_degrees + amp)
		"spin":
			Motion.run(_id, target, ^"rotation", target.rotation + PI)
		"roll":
			Motion.number_roll(_number, 0, ROLL_TO, _id)
		"type":
			_typed.visible_ratio = 0.0
			var per_char := Motion.seconds(_id)
			length = per_char * TYPE_TEXT.length()
			if Motion.live(_id):
				create_tween().tween_property(_typed, "visible_ratio", 1.0, length)
			else:
				_typed.visible_ratio = 1.0
		"flash":
			Fx.flash(Palette.CELL_PINK if _id == &"precision_perfect" else Color.WHITE, amp, Motion.seconds(_id))
		"heat":
			Fx.heat_pulse()
		"freeze":
			Fx.freeze_frames()
			length = LOOP_HOLD
		"jack_in":
			Fx.jack_in(func() -> void: pass)
		"jack_out":
			Fx.jack_out(func() -> void: pass)
	_show_values()
	if _loop:
		_replay_later(maxf(length, 0.0) + LOOP_GAP)


func _replay_later(seconds: float) -> void:
	var gen := _generation
	get_tree().create_timer(seconds).timeout.connect(func() -> void:
		if is_inside_tree() and gen == _generation and _loop:
			_play())


# --- Controls ---------------------------------------------------------------------------

func _build_panel() -> void:
	var back := ColorRect.new()
	back.color = Color(Palette.INK, 0.92)
	back.position = Vector2.ZERO
	back.size = Vector2(PANEL_W, 720)
	add_child(back)
	var box := VBoxContainer.new()
	box.position = Vector2(12, 10)
	box.size = Vector2(PANEL_W - 24, 700)
	box.add_theme_constant_override("separation", 4)
	add_child(box)
	box.add_child(_caption("MOTION LAB  (ui_motion.tres)"))
	_ids = OptionButton.new()
	for id in _cfg.ids():
		_ids.add_item(String(id))
	_ids.item_selected.connect(func(i: int) -> void: _select(StringName(_ids.get_item_text(i))))
	box.add_child(_ids)
	_dur = _slider(box, "duration (s)", 0.0, DURATION_MAX, &"duration")
	_delay = _slider(box, "delay (s)", 0.0, DELAY_MAX, &"delay")
	_amp = _slider(box, "amplitude", 0.0, AMP_MIN_RANGE, &"amplitude")
	box.add_child(_caption("ease"))
	_ease = OptionButton.new()
	for n in EASES:
		_ease.add_item(n)
	_ease.item_selected.connect(func(i: int) -> void: _set_field(&"ease", i))
	box.add_child(_ease)
	box.add_child(_caption("trans"))
	_trans = OptionButton.new()
	for n in TRANSES:
		_trans.add_item(n)
	_trans.item_selected.connect(func(i: int) -> void: _set_field(&"trans", i))
	box.add_child(_trans)
	_enabled = CheckBox.new()
	_enabled.text = "enabled"
	_enabled.toggled.connect(func(on: bool) -> void: _set_field(&"enabled", on))
	box.add_child(_enabled)
	box.add_child(_caption("speed (x)"))
	_speed = HSlider.new()
	_speed.min_value = Motion.SPEED_MIN
	_speed.max_value = Motion.LAB_SPEED_MAX
	_speed.step = Motion.SPEED_MIN / 5.0
	_speed.value_changed.connect(func(v: float) -> void:
		Motion.set_speed(v)
		_show_values())
	box.add_child(_speed)
	_loop_box = CheckBox.new()
	_loop_box.text = "loop"
	_loop_box.toggled.connect(func(on: bool) -> void:
		_loop = on
		if on:
			_play())
	box.add_child(_loop_box)
	var row := HBoxContainer.new()
	box.add_child(row)
	var play := Button.new()
	play.text = "Play"
	play.pressed.connect(_play)
	row.add_child(play)
	var copy := Button.new()
	copy.text = "Copy values"
	copy.pressed.connect(_copy_values)
	row.add_child(copy)
	var reset := Button.new()
	reset.text = "Reset id"
	reset.pressed.connect(_reset_entry)
	row.add_child(reset)
	_values = Label.new()
	_values.add_theme_font_override("font", Palette.mono())
	_values.add_theme_font_size_override("font_size", 13)
	_values.add_theme_color_override("font_color", Palette.CELL_ACID)
	box.add_child(_values)


func _caption(text: String) -> Label:
	var l := Label.new()
	l.text = text
	l.add_theme_font_override("font", Palette.mono())
	l.add_theme_font_size_override("font_size", 13)
	l.add_theme_color_override("font_color", Palette.PAPER)
	return l


func _slider(box: VBoxContainer, caption: String, lo: float, hi: float, field: StringName) -> HSlider:
	box.add_child(_caption(caption))
	var s := HSlider.new()
	s.min_value = lo
	s.max_value = hi
	s.step = SLIDER_STEP
	s.allow_greater = true
	s.value_changed.connect(func(v: float) -> void: _set_field(field, v))
	box.add_child(s)
	return s


func _select(id: StringName) -> void:
	_id = id
	var e := _cfg.find(id)
	_syncing = true
	for i in _ids.item_count:
		if _ids.get_item_text(i) == String(id):
			_ids.select(i)
	_amp.max_value = maxf(AMP_MIN_RANGE, absf(e.amplitude) * AMP_RANGE_MULT)
	_dur.value = e.duration
	_delay.value = e.delay
	_amp.value = e.amplitude
	_ease.select(e.ease)
	_trans.select(e.trans)
	_enabled.button_pressed = e.enabled
	_syncing = false
	_show_values()
	if not _demo:
		_play()


func _set_field(field: StringName, value: Variant) -> void:
	if _syncing:
		return
	var e := _cfg.find(_id)
	e.set(field, value)
	_show_values()


func _reset_entry() -> void:
	var file: UiMotionData = load(Motion.CONFIG_PATH)
	var src := file.find(_id)
	var e := _cfg.find(_id)
	for f in [&"duration", &"delay", &"ease", &"trans", &"amplitude", &"enabled"]:
		e.set(f, src.get(f))
	_select(_id)


func _show_values() -> void:
	if _values == null:
		return
	var e := _cfg.find(_id)
	_values.text = "%s\n%s %s  x%.2f" % [Motion.tres_lines(e), EASES[e.ease], TRANSES[e.trans], Motion.speed]


## Prints the selected entry's .tres lines and copies them to the clipboard.
func _copy_values() -> void:
	var lines := Motion.tres_lines(_cfg.find(_id))
	print("; ui_motion.tres  [sub_resource id=\"m_%s\"]\n%s" % [_id, lines])
	DisplayServer.clipboard_set(lines)
