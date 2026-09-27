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
	&"wheel_spin": ["view", "turn"], &"wheel_spin_blur": ["view", "turn"], &"wheel_nudge": ["view", "nudge"],
	&"precision_perfect": ["flash", "wheel"], &"precision_good_ring": ["view", "good"],
	&"precision_partial": ["shake", "wheel"], &"precision_blink": ["blink", "wheel"], &"precision_miss_static": ["view", "miss"],
	&"card_hover": ["view", "hover"], &"card_play": ["scene", "play"], &"card_draw": ["scene", "deal"], &"card_exhaust": ["scene", "exhaust"],
	&"send_it_press": ["view", "press"], &"send_it_drips": ["view", "press"], &"resolve_pass": ["scene", "send"], &"resolve_pulse": ["view", "pulse"],
	&"number_float": ["scene", "numbers"], &"number_crit": ["scene", "numbers"], &"hp_lag": ["view", "hp"],
	&"intent_flip": ["view", "tag"], &"rewind_scrub": ["scene", "rewind"],
	&"pointer_flicker": ["pulse_pointer", "wheel"], &"orbit_trail": ["view", "orbit"],
	&"enemy_break": ["scene", "break"], &"hub_shatter": ["scene", "shatter"],
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
	&"ice_lock_ring": ["fade_in", "sticker"], &"decoy_fire": ["shake", "sticker"], &"raid_hit_effect": ["pop", "sticker"],
	&"node_damage_number": ["lift", "number"], &"forecast_stamp_resolve": ["pop", "panel"],
	&"card_pickup": ["scene", "aim"], &"drag_ghost_follow": ["scene", "drag"], &"drop_zone_pulse": ["scene", "aim"],
	&"aim_line_draw": ["scene", "aim"], &"target_snap": ["scene", "aim"], &"drag_cancel_return": ["scene", "cancel"],
	&"card_stamp": ["scene", "play"], &"effect_burst": ["scene", "play"], &"card_discard": ["scene", "send"],
	&"resolve_beat": ["scene", "send"], &"block_number": ["scene", "numbers"], &"heal_number": ["scene", "numbers"],
	&"hp_drain": ["view", "hp"], &"status_stamp": ["scene", "send"], &"last_turn_reveal": ["scene", "send"],
	&"wheel_respin": ["view", "respin"], &"inner_ring_turn": ["view", "nudge_inner"], &"pointer_migrate": ["view", "migrate"],
	&"pointer_orbit": ["view", "orbit"], &"enemy_turn_spin": ["view", "respin"],
	&"drag_pickup": ["pop", "sticker"], &"drag_follow": ["slide_x", "sticker"], &"drop_settle": ["drop", "sticker"],
	&"drop_reject": ["shake", "sticker"], &"loadout_swap": ["fly", "card"], &"crew_assign": ["pop", "card"],
	&"influence_crossfade": ["fade_in", "panel"], &"influence_spread": ["fade_in", "panel"],
	# ANIM-2 / ANIM-3 (combat): "view" plays on the lab's wheel / card / SEND IT; "scene"
	# plays in a live combat scene over the whole lab (1280x720).
	&"resolve_sequence": ["scene", "send"], &"hit_line": ["scene", "send"], &"victory_stamp": ["scene", "victory"],
	&"combat_end_hold": ["scene", "victory"], &"wheel_flip": ["view", "flip"], &"dead_wheel_fade": ["scene", "break"],
	&"drag_ghost_tilt": ["scene", "drag"], &"card_pile": ["scene", "deal"], &"hand_reflow": ["scene", "play"],
	&"ram_tick": ["scene", "ram"], &"ram_pending_blink": ["scene", "aim"],
	# ANIM-5 (map, raid, jack and Heat):
	&"jack_scanlines": ["blink", "stage"], &"raid_step_gap": ["blink", "sticker"], &"home_lag": ["roll", "number"],
	&"minimap_pulse": ["pop", "sticker"], &"select_ring_ease": ["pop", "sticker"], &"legend_fold": ["drop", "panel"],
	# ANIM-4 (HQ drag and drop; in context: hq_scene --demo-anim=drag_*):
	&"drop_stamp": ["pop", "sticker"], &"market_fly": ["fly", "card"],
}

## Scene demos: the fight they run, and what the wheel demos turn and shift.
const SCENE_ENEMY := &"collections_agent"
const SCENE_SEED := 5
## Frames a fresh scene fight lays out before its motion starts.
const SCENE_SETTLE := 3
const DEMO_SPIN_TICKS := 9.0
const DEMO_RESPIN_TICKS := 70.0
const DEMO_POINTER_SHIFT := 5
const DEMO_HP_LOSS := 12
## Drag demo: the ghost's path (from, to) over DRAG_FRAMES frames, in 1280x720 space.
const DRAG_FROM := Vector2(260, 620)
const DRAG_TO := Vector2(820, 300)
const DRAG_FRAMES := 18
## Aim demo: frames between aim steps; the numbers demo's values [text, crit].
const AIM_STEP_FRAMES := 8
const DEMO_NUMBERS := [["-7", false], ["-14", true], ["+5 BLOCK", false]]
## The cancel demo lets go here.
const CANCEL_AT := Vector2(760, 330)
## A number rises at most this share of its hub (as in the combat scene).
const NUMBER_RISE_SHARE := 0.7

var _scene: Control = null
var _scene_host: Control = null
var _drag_ghost: DragGhost = null
var _drag_frame: int = -1
var _aim_frame: int = -1

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
		elif arg.begins_with("--demo-set="):
			_apply_sets(arg.trim_prefix("--demo-set="))
	if not Motion.has(_id):
		push_error("motion_lab: no motion id '%s'." % _id)
		_id = &"card_hover"
	_speed.value = Motion.speed
	_loop_box.set_pressed_no_signal(_loop)
	_select(_id)


## Variant capture: `--demo-set=wheel_spin.duration=0.35,wheel_spin.amplitude=2` tunes the
## lab's copy of the table (the file never changes).
func _apply_sets(spec: String) -> void:
	for part in spec.split(",", false):
		var kv := part.split("=")
		var path := kv[0].split(".")
		if kv.size() != 2 or path.size() != 2 or _cfg.find(StringName(path[0])) == null:
			push_error("motion_lab: bad --demo-set part '%s'." % part)
			continue
		var e := _cfg.find(StringName(path[0]))
		var field := StringName(path[1])
		if field in [&"ease", &"trans"]:
			e.set(field, int(kv[1]))
		elif field == &"enabled":
			e.set(field, kv[1] == "true")
		else:
			e.set(field, float(kv[1]))
		print("motion_lab: %s.%s = %s" % [path[0], path[1], kv[1]])


func _exit_tree() -> void:
	Motion.use_config(null)
	Motion.set_speed(1.0)


func _process(_delta: float) -> void:
	if _demo and _frames == DEMO_START_FRAME:
		print("motion_lab: %s starts on frame %d (speed %.2fx)" % [_id, _frames, Motion.speed])
		_play()
	_frames += 1
	if _drag_frame >= 0 and is_instance_valid(_drag_ghost):
		_drag_frame += 1
		var t := clampf(float(_drag_frame) / DRAG_FRAMES, 0.0, 1.0)
		_drag_ghost.position = DRAG_FROM.lerp(DRAG_TO, t * t * (3.0 - 2.0 * t))
		if _drag_frame > DRAG_FRAMES * 2:
			_drag_frame = -1
	if _aim_frame >= 0 and _scene != null:
		_aim_frame += 1
		if _aim_frame % AIM_STEP_FRAMES == 0 and _aim_frame <= AIM_STEP_FRAMES * 3:
			_scene.step_selection(1)
		if _aim_frame > AIM_STEP_FRAMES * 3:
			_aim_frame = -1


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
	_wheel.stop_motion()
	_wheel.shake = Vector2.ZERO
	_wheel.pointer_alpha = 1.0
	_drag_frame = -1
	_aim_frame = -1
	if is_instance_valid(_drag_ghost):
		_drag_ghost.queue_free()
	_drag_ghost = null
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
	# "view" and "scene" demos name an action, not a piece.
	var target: Control = _pieces.get(demo[1], _wheel)
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
		"view":
			length = _play_view(String(demo[1]))
		"scene":
			_play_scene(String(demo[1]))
			length = maxf(LOOP_HOLD, Motion.seconds(&"resolve_sequence"))
	_show_values()
	if _loop:
		_replay_later(maxf(length, 0.0) + LOOP_GAP)


func _replay_later(seconds: float) -> void:
	var gen := _generation
	get_tree().create_timer(seconds).timeout.connect(func() -> void:
		if is_inside_tree() and gen == _generation and _loop:
			_play())


# --- Combat demos (ANIM-2 / ANIM-3) --------------------------------------------------------

## A motion on the lab's own wheel, card or SEND IT. Returns its length (s).
func _play_view(what: String) -> float:
	_show_scene(false)
	var c := _wheel.combatant
	var rot := float(c.wheel.rotation)
	match what:
		"turn":
			_wheel.play_turn(_id if _id != &"wheel_spin_blur" else &"wheel_spin", rot - DEMO_SPIN_TICKS, float(c.wheel.inner_rotation) - DEMO_SPIN_TICKS)
		"respin":
			_wheel.play_turn(_id, rot - DEMO_RESPIN_TICKS, float(c.wheel.inner_rotation) - DEMO_RESPIN_TICKS)
		"nudge":
			for k in 3:
				_wheel.play_nudge(RC.RingScope.OUTER, 1)
		"nudge_inner":
			_wheel.play_nudge(RC.RingScope.INNER, 1)
		"good":
			_wheel.play_good_ring()
		"miss":
			_wheel.play_miss_static(0)
		"pulse":
			_wheel.play_pulse(0)
		"hp":
			_wheel.anim_hp = float(c.hp)
			_wheel.play_hp(float(c.hp - DEMO_HP_LOSS))
		"migrate", "orbit":
			var from: Array = []
			for p in c.wheel.pointer_ticks:
				from.append(posmod(p - DEMO_POINTER_SHIFT, RC.TICKS))
			_wheel.play_pointers(from, _id if _id != &"orbit_trail" else &"pointer_orbit", what == "orbit")
		"flip":
			_wheel.play_flip()
		"tag":
			_wheel.intent = {"type": RC.SliceType.ATTACK, "text": "ATTACK · GOOD %d" % _generation, "chips": [{"text": "HITS 8", "color": Palette.CELL_PINK, "ink": Palette.INK}]}
			_wheel.queue_redraw()
		"hover":
			var card: ZineCard = _pieces["card"]
			card.grab_focus()
			get_tree().create_timer(Motion.seconds(_id) * 3.0).timeout.connect(card.release_focus)
		"press":
			(_pieces["send"] as DripButton).press_motion()
	return LOOP_HOLD


func _show_scene(on: bool) -> void:
	if on and _scene == null:
		_scene_host = Control.new()
		_scene_host.size = Vector2(1280, 720)
		add_child(_scene_host)
		_scene = load("res://scenes/combat/combat_scene.tscn").instantiate()
		_scene.auto_start = false
		_scene_host.add_child(_scene)
		_scene.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	if _scene_host != null:
		_scene_host.visible = on


## A motion in a live combat scene (a fresh fight each time, laid out for SCENE_SETTLE
## frames before the motion starts).
func _play_scene(what: String) -> void:
	_show_scene(true)
	_scene.skip_motion()
	_scene.cancel_selection()
	_scene.start_fight(SCENE_ENEMY, SCENE_SEED)
	_scene.skip_motion()
	for k in SCENE_SETTLE:
		await get_tree().process_frame
	print("motion_lab: scene %s, player view %s" % [_scene.size, _scene._player_view.size])
	var enemy: StringName = _scene.engine.state().enemies[0].id
	var ev: WheelView = _scene._view_of(enemy)
	match what:
		"send":
			_scene.end_turn()
		"play":
			_scene.select_card(0)
			if _scene.selecting >= 0:
				_scene.confirm_selection()
		"exhaust":
			var cap: Dictionary = _scene._card_copy(0)
			_scene.fx_layer.play_card(cap["copy"], cap["rect"], float(cap["rot"]), ev.global_center(), true)
		"deal":
			_scene._deal_hand(0)
		"aim", "drag", "cancel":
			var i := _multi_target_card()
			if what == "drag":
				_scene._dragging = true
			_scene._begin_targeting(i, CardTargeting.options(_scene.engine.resolver, _scene.engine.state(), i))
			if what == "aim":
				_aim_frame = 0
				var picked: ZineCard = _scene._card_node(i)
				if picked != null:
					Motion.pop(picked, &"card_pickup")
			elif what == "drag":
				var cap: Dictionary = _scene._card_copy(i)
				if is_instance_valid(_drag_ghost):
					_drag_ghost.queue_free()
				_drag_ghost = DragGhost.new(cap["copy"])
				_drag_ghost.position = DRAG_FROM
				_scene.add_child(_drag_ghost)
				_drag_frame = 0
			else:
				_scene._cancel_drag(i, CANCEL_AT)
		"numbers":
			var k := 0
			for n in DEMO_NUMBERS:
				var block := String(n[0]).contains("BLOCK")
				_scene.fx_layer.number(ev.number_anchor(k), String(n[0]), Palette.NET_CYAN if block else WheelView.LOSS_COLOR,
					&"block_number" if block else &"number_float", Vector2.UP, bool(n[1]), minf(Motion.amplitude(&"number_float"), ev.number_room() * NUMBER_RISE_SHARE))
				k += 1
		"break":
			_scene.demo_break(enemy)
		"shatter":
			_scene.fx_layer.glass(ev.global_center(), ev.hub_radius(), ev.wheel_color)
		"victory":
			_scene._end_beat(CombatState.Outcome.VICTORY)
		"rewind":
			_scene.nudge_wheel(&"player", 1)
			_scene.nudge_wheel(&"player", 1)
			_scene.skip_motion()
			_scene._player_view.stop_motion()
			_scene.rewind()
		"ram":
			_scene.ram_note.hold(0)
			_scene.ram_note.play_refill()



## The first hand card with several legal targets (else card 0).
func _multi_target_card() -> int:
	var s: CombatState = _scene.engine.state()
	for i in s.hand.size():
		if CardTargeting.options(_scene.engine.resolver, s, i).size() > 1:
			return i
	return 0


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
