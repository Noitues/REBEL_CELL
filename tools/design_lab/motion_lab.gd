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
	&"precision_perfect": ["burst", "perfect"], &"precision_good_ring": ["view", "good"],
	&"precision_partial": ["shake", "wheel"], &"precision_blink": ["blink", "wheel"], &"precision_miss_static": ["view", "miss"],
	&"card_hover": ["view", "hover"], &"card_play": ["scene", "play"], &"card_draw": ["scene", "deal"], &"card_exhaust": ["scene", "exhaust"],
	&"send_it_press": ["view", "press"], &"send_it_drips": ["view", "press"], &"resolve_pass": ["scene", "send"], &"resolve_pulse": ["view", "pulse"],
	&"number_float": ["scene", "numbers"], &"number_crit": ["scene", "numbers"], &"hp_lag": ["view", "hp"],
	&"intent_flip": ["view", "tag"], &"rewind_scrub": ["scene", "rewind"],
	&"pointer_flicker": ["pulse_pointer", "wheel"], &"orbit_trail": ["view", "orbit"],
	&"enemy_break": ["scene", "send_kill"], &"hub_shatter": ["scene", "shatter"],
	&"heat_pulse": ["heat", "stage"], &"heat_letters_shake": ["shake", "number"], &"poster_stamp": ["pop", "panel"],
	&"hq_crt_hum": ["screen", "hum"], &"radio_type": ["screen", "radio"], &"jack_ring_breathe": ["screen", "jack"], &"polaroid_tilt": ["screen", "dossier"],
	&"site_outline_draw": ["fade_in", "panel"], &"map_camera_ease": ["slide_x", "panel"], &"route_crawl": ["slide_x", "sticker"], &"asset_drop": ["drop", "card"],
	&"raid_move": ["slide_x", "sticker"], &"turret_trace": ["blink", "sticker"], &"raid_flip": ["tilt", "sticker"],
	&"route_pulse": ["blink", "sticker"], &"node_pop": ["pop", "sticker"], &"visited_dim": ["fade_to", "sticker"],
	&"panel_in": ["screen", "glass"], &"panel_crt_roll": ["screen", "glass"], &"panel_drop": ["screen", "paper"],
	&"menu_cursor_blink": ["screen", "menu"], &"menu_type": ["screen", "menu"], &"menu_highlight": ["screen", "menu"],
	&"modem_sign_warmup": ["screen", "modem"], &"modem_trace": ["screen", "modem"], &"buy_fly": ["screen", "buy"], &"note_flap": ["screen", "flap"],
	&"loot_fan": ["screen", "loot"], &"loot_pick": ["screen", "pick"], &"count_up": ["screen", "hud"],
	&"dispatch_type": ["screen", "subtitle"], &"subtitle_bar_in": ["screen", "subtitle"],
	&"drip_grow": ["screen", "drip"], &"drip_halo": ["screen", "halo"],
	&"beacon_blink": ["pulse", "sticker"], &"city_traffic": ["screen", "city"], &"hq_sign_flicker": ["screen", "city"],
	&"sticky_bump": ["screen", "hud"], &"number_roll": ["screen", "hud"],
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
	&"resolve_sequence": ["scene", "send_hit"], &"hit_line": ["scene", "send_hit"], &"victory_stamp": ["scene", "victory"],
	&"combat_end_hold": ["scene", "victory"], &"wheel_flip": ["view", "flip"], &"dead_wheel_fade": ["scene", "break"],
	&"drag_ghost_tilt": ["scene", "drag"], &"card_pile": ["scene", "deal"], &"hand_reflow": ["scene", "play"],
	&"ram_tick": ["scene", "ram"], &"ram_pending_blink": ["scene", "aim"],
	# ANIM-5 (map, raid, jack and Heat):
	&"jack_scanlines": ["blink", "stage"], &"raid_step_gap": ["blink", "sticker"], &"home_lag": ["roll", "number"],
	&"minimap_pulse": ["pop", "sticker"], &"select_ring_ease": ["pop", "sticker"], &"legend_fold": ["drop", "panel"],
	# ANIM-4 (HQ drag and drop; in context: hq_scene --demo-anim=drag_*):
	&"drop_stamp": ["pop", "sticker"], &"market_fly": ["fly", "card"],
	# ANIM-6 (screens): "screen" builds a fresh piece on the stage (a menu, the Modem sign, a
	# loot row, the top bar, a dossier...) and plays the real motion on it.
	&"saved_stamp_in": ["screen", "saved"], &"pad_prompts_in": ["fade_in", "sticker"], &"focus_tip_in": ["fade_in", "panel"],
	&"event_outcome_pop": ["pop", "sticker"], &"event_choice_stamp": ["screen", "stamp"], &"sold_stamp": ["screen", "buy"],
	&"caption_crossfade": ["screen", "caption"], &"city_sign_pick": ["screen", "city"],
	# ANIM-4b (drag and drop in the run; in context: netrun_scene --demo-shop / --demo-loot
	# --demo-anim=drag_*):
	&"drop_buy": ["fly", "card"], &"shred_feed": ["drop", "sticker"],
	# ANIM-R1 (the first fix batch; in context: hq_scene / netrun_scene --demo-anim=<id>):
	&"jack_arrive": ["jack_in", "stage"], &"jack_arrival_wait": ["blink", "stage"],
	&"select_ring_pulse": ["pulse", "sticker"], &"loot_reject": ["drop_away", "card"], &"home_number_fly": ["fly", "number"], &"influence_mark": ["pop", "panel"], &"heat_number_pop": ["pop", "number"], &"heat_banner": ["pop", "panel"],
	# ANIM-R1 (combat and input): the SEND IT replay's pieces play in a live SEND IT.
	&"resolve_landing_hold": ["scene", "send"], &"landing_pulse": ["scene", "send"], &"resolve_result_hold": ["scene", "send"],
	&"result_caption": ["scene", "send"], &"result_stamp": ["scene", "send"], &"number_to_hp": ["scene", "numbers"],
	&"hit_flash": ["scene", "send"], &"hit_shake": ["scene", "send"], &"enemy_enter": ["scene", "enter"],
	&"victory_flash": ["scene", "victory"], &"boss_phase_flash": ["burst", "phase"],
	&"ram_refusal": ["scene", "refuse"], &"ram_refusal_pop": ["scene", "refuse"], &"send_it_ready": ["view", "ready"],
	&"send_it_drips_share": ["view", "press"], &"drag_ghost_tilt_speed": ["scene", "drag"],
	&"toast_note_hold": ["fade_out", "sticker"], &"stamp_fade_in": ["screen", "stamp"],
	# ANIM-R2 (city, maps and transitions; in context: hq_scene / netrun_scene --demo-anim=<id>):
	&"city_bake_fade": ["fade_in", "panel"], &"jack_connect": ["fade_in", "panel"], &"raid_outcome_stagger": ["pop", "sticker"], &"raid_result_banner": ["pop", "panel"], &"asset_drop_stamp": ["pop", "sticker"], &"influence_tint": ["fade_in", "panel"], &"route_target_pulse": ["pulse", "sticker"],
	# ANIM-R2 (combat, events and screens):
	&"hit_absorb": ["scene", "send_hit"], &"ram_spend_float": ["scene", "ram"], &"price_refusal": ["pulse", "sticker"],
	# ANIM-R3 (city, raid, jack, heat and route; in context: hq_scene --demo-raid --demo-anim=asset_drop):
	&"asset_drop_wait": ["blink", "sticker"], &"asset_drop_grow": ["pop", "sticker"], &"forecast_change": ["lift", "number"], &"jack_dissolve": ["jack_in", "stage"],
	# ANIM-R3 (combat, input and screens): each plays in a live SEND IT.
	&"impact_mark": ["scene", "send_block"], &"forecast_tick": ["scene", "send_hit"], &"forecast_fade": ["scene", "send_hit"],
	&"status_mark": ["scene", "send_hit"],
	# ANIM-R4 (city, raid, Heat, route and HQ):
	&"forecast_change_fade": ["lift", "number"], &"raid_incoming_hold": ["fade_in", "panel"], &"forecast_road_pulse": ["pulse", "sticker"],
	# ANIM-R4 (combat, input and screens): the shares that were inline play where they act (a
	# live SEND IT, the break, the MODEM sign); the two sides one after the other in a SEND IT
	# where both hit; the RAM refill in the RAM demo.
	&"hit_line_flight": ["scene", "send_hit"], &"ride_swap": ["scene", "send_hit"], &"ride_shrink": ["scene", "send_hit"],
	&"ride_perfect": ["scene", "send_hit"], &"break_crack": ["scene", "send_kill"], &"modem_sign_strike": ["screen", "modem"],
	&"modem_sign_flicker": ["screen", "modem"], &"resolve_side_gap": ["scene", "send_both"], &"resolve_attacker_gap": ["scene", "send_both"],
	&"ram_refill_float": ["scene", "ram"], &"event_type": ["screen", "radio"],
	# ANIM-R5 combat: the lost fight's DEFEAT stamp (a SEND IT the operative does not survive).
	&"defeat_stamp": ["scene", "send_lose"],
	# Art pass W6 (ART_BIBLE 8): the wheel-local T3 bursts (Perfect and a boss phase: the
	# full-screen flashes are retired) play on the lab's wheel through a CombatFxLayer.
	&"wheel_burst_perfect": ["burst", "perfect"], &"wheel_burst_phase": ["burst", "phase"],
	# Art pass W6: each slice type's hit shape on the lab's wheel (--demo-hits-row plays all
	# seven side by side, named, for the greyscale sheet).
	&"hit_vfx_crit": ["hit_vfx", "crit"], &"hit_vfx_attack": ["hit_vfx", "attack"], &"hit_vfx_shield": ["hit_vfx", "shield"],
	&"hit_vfx_evade": ["hit_vfx", "evade"], &"hit_vfx_afflict": ["hit_vfx", "afflict"], &"hit_vfx_heal": ["hit_vfx", "heal"],
	&"hit_vfx_miss": ["hit_vfx", "miss"],
	# Art pass W2 (ART_BIBLE 6): the component kit's motion; every component state is shown
	# side by side in tools/design_lab/components_lab.tscn.
	&"focus_scale": ["pop", "sticker"], &"button_refused": ["blink", "sticker"], &"toast_in": ["drop", "sticker"],
	&"toast_hold": ["fade_out", "sticker"], &"toast_out": ["fade_out", "sticker"], &"stamp_hold": ["screen", "stamp"],
	&"zine_stamp_in": ["pop", "sticker"], &"banner_gap": ["fade_in", "panel"], &"toggle_slide": ["slide_x", "sticker"],
	&"wheel_respin_settle": ["scene", "send"],  # art pass W3
	&"hub_clear": ["scene", "send"],  # art pass W3
	&"boss_intro": ["scene", "enter"],  # art pass W3
	&"needle_draw": ["scene", "send"],  # art pass W3
	&"hp_heartbeat": ["scene", "send"],  # art pass W3
	&"bezel_ambient": ["scene", "enter"],  # art pass W3
	# Art pass W5 (ART_BIBLE 7.2): the boss hologram on the stage: its idle drift, its intro
	# reveal and (--demo-reduce) the reduce-effects cross-fade.
	&"hologram_idle": ["hologram", "idle"], &"hologram_intro": ["hologram", "intro"], &"hologram_intro_fade": ["hologram", "intro"],
	# Art pass W8a (ART_BIBLE 10): a modal opens and closes; the logo's idle drip.
	&"modal_in": ["pop", "panel"], &"modal_out": ["fade_out", "panel"], &"logo_drip": ["drop", "sticker"],
	# Art pass W8c (ART_BIBLE 11 Run failed): the run's end (the full sequence runs on the
	# netrun page, `--demo-end=died`; the lab shows its stamp's slam).
	&"run_end_flatline": ["pop", "sticker"],
	# Art pass W8d (ART_BIBLE 11 Campaign end): the campaign's end (the full sequences run on the
	# HQ page, tools/design_lab/campaign_end_lab.tscn; the lab shows the stamp's slam).
	&"campaign_end_won": ["pop", "sticker"], &"campaign_end_lost": ["pop", "sticker"],
}
## Art pass W6: the hit shapes' row (--demo-hits-row): its height and first spot and the
## step between shapes (px, 1280x720), and the names' lettering.
const HITS_ROW_Y := 360.0
const HITS_ROW_X := 440.0
const HITS_ROW_STEP := 120.0
const HITS_ROW_FONT := 15

## Screen demos (ANIM-6): the top bar's values before and after a change, the text a
## subtitle demo says, and how long the frames between a menu's focus moves are (s).
const HUD_BEFORE := [["HEAT", "12", "/100"], ["SCHEMATICS", "40", ""], ["CYCLES", "85", ""], ["CARDS", "10", ""]]
const HUD_AFTER := [["HEAT", "12", "/100"], ["SCHEMATICS", "40", ""], ["CYCLES", "140", ""], ["CARDS", "11", ""]]
const SUBTITLE_TEXT := "Jacking you in. The rack is two hops out: keep your Heat down."
const MENU_STEP := 0.45
## How long a screen demo holds before it loops (s).
const SCREEN_LOOP := 2.5

## Scene demos: the fight they run, and what the wheel demos turn and shift.
const SCENE_ENEMY := &"collections_agent"
const SCENE_SEED := 5
## Frames a fresh scene fight lays out before its motion starts.
const SCENE_SETTLE := 3
const DEMO_SPIN_TICKS := 9.0
const DEMO_RESPIN_TICKS := 70.0
const DEMO_POINTER_SHIFT := 5
const DEMO_HP_LOSS := 12
## ANIM-R1 captures: nudges tried to make the SEND IT land a hit, and the enemy HP the
## kill capture starts from.
const DEMO_NUDGE_TRIES := 12
const DEMO_KILL_HP := 3
## ANIM-R3 "send_block": fights tried until the enemy's forecast hits the operative, and
## the guard the operative is given so the hit is soaked whole (lab only).
const DEMO_BLOCK_SEEDS := 24
const DEMO_BLOCK := 99
## Drag demo: the ghost's path (from, to) over DRAG_FRAMES frames, in 1280x720 space.
const DRAG_FROM := Vector2(260, 620)
const DRAG_TO := Vector2(820, 300)
const DRAG_FRAMES := 18
## Aim demo: frames between aim steps.
const AIM_STEP_FRAMES := 8
## ANIM-R4 C6e: the number demo gives the enemy a guard of this fraction (1/N) of the hit.
const DEMO_GUARD_SHARE := 3
## The cancel demo lets go here.
const CANCEL_AT := Vector2(760, 330)
## A number rises at most this share of its hub (as in the combat scene).
const NUMBER_RISE_SHARE := 0.7

var _scene: Control = null
var _scene_host: Control = null
var _screen_host: Control = null
var _hud: HudStats = null
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
## Art pass W6: the lab's own combat effects layer over the stage (bursts, hit shapes).
var _lab_fx: CombatFxLayer
var _hits_row := false

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
	_lab_fx = CombatFxLayer.new()
	add_child(_lab_fx)
	_record_rest()
	_build_panel()
	for arg in OS.get_cmdline_user_args():
		if arg.begins_with("--demo-anim="):
			_id = StringName(arg.trim_prefix("--demo-anim="))
			_demo = true
			_loop = false
		elif arg.begins_with("--demo-speed="):
			Motion.set_speed(float(arg.trim_prefix("--demo-speed=")))
		elif arg == "--demo-hits-row":
			_hits_row = true
		elif arg == "--demo-reduce":
			# Art pass W6 captures: reduce effects for this run only (never saved).
			Settings.reduce_effects = true
			Settings.changed.emit()
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
	_typed.autowrap_mode = TextServer.AUTOWRAP_WORD
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


## Takes a screen demo's piece away (the stage's own pieces show again).
func _clear_screen() -> void:
	if _screen_host != null:
		_screen_host.queue_free()
	_screen_host = null
	_hud = null


func _reset_stage() -> void:
	_clear_screen()
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
	if _lab_fx != null:
		_lab_fx.clear()
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
			# Art pass W6: a full-screen flash is T4 only (screen_flash).
			Fx.flash(Color.WHITE, amp, Motion.seconds(_id), VfxTier.T4)
		"hit_vfx":
			# Art pass W6: the hit shape on the wheel's hub (or the whole row, named).
			if _hits_row:
				_stage.visible = false
				for k in CombatFxLayer.HIT_KINDS.size():
					var at := Vector2(HITS_ROW_X + k * HITS_ROW_STEP, HITS_ROW_Y)
					_lab_fx.hit_vfx(at, CombatFxLayer.HIT_KINDS[k])
					var name_tag := Label.new()
					name_tag.text = String(CombatFxLayer.HIT_KINDS[k]).to_upper()
					name_tag.add_theme_font_override("font", Palette.mono())
					name_tag.add_theme_font_size_override("font_size", HITS_ROW_FONT)
					name_tag.position = at + Vector2(-HITS_ROW_STEP * 0.3, HITS_ROW_STEP * 0.45)
					_lab_fx.add_child(name_tag)
			else:
				_lab_fx.hit_vfx(_wheel.global_center(), StringName(demo[1]))
		"hologram":
			# Art pass W5: a boss hologram over the stage (the lab's pieces hide).
			length = _play_hologram(String(demo[1]))
		"burst":
			# Art pass W6: the wheel-local T3 burst on the lab's wheel (the phase in a corp hue).
			var hue := Palette.CORP_SOLACE if demo[1] == "phase" else Color(0, 0, 0, 0)
			_lab_fx.wheel_burst(_wheel.global_center(), _wheel.disc_radius(), StringName(demo[1]), hue)
			length = maxf(length, Motion.seconds(CombatFxLayer.BURST_MOTION[StringName(demo[1])]))
		"heat":
			# ANIM-R2 R8 / ANIM-R3 B9: a Heat crossing distorts round the poster only.
			Fx.heat_pulse_at(target.get_global_rect())
		"freeze":
			Fx.freeze_frames()
			length = LOOP_HOLD
		"jack_in":
			Fx.jack_in(func() -> void: pass)
		"jack_out":
			Fx.jack_out(func() -> void: pass)
		"view":
			length = _play_view(String(demo[1]))
		"screen":
			_play_screen(String(demo[1]))
			length = SCREEN_LOOP
		"scene":
			_play_scene(String(demo[1]))
			length = maxf(LOOP_HOLD, Motion.seconds(&"resolve_sequence"))
	_show_values()
	if _loop:
		_replay_later(maxf(length, 0.0) + LOOP_GAP)


## Art pass W5: a fresh boss Hologram centred on the stage; "intro" plays its reveal (a
## cross-fade under reduce effects), "idle" shows its T0 drift. Returns its length (s).
func _play_hologram(what: String) -> float:
	_show_scene(false)
	var holo := Hologram.new(PortraitArt.enemy_subject(&"the_manifest", "The Manifest", &"meridian", true), Hologram.Mode.BOSS)
	holo.name = "LabHologram"
	holo.size = holo.custom_minimum_size
	_clear_screen()
	_screen_host = Control.new()
	_screen_host.name = "ScreenDemo"
	_screen_host.position = Vector2(PANEL_W, 0)
	_screen_host.size = Vector2(1280 - PANEL_W, 720)
	add_child(_screen_host)
	holo.position = (_screen_host.size - holo.size) * 0.5
	_screen_host.add_child(holo)
	if what == "intro":
		holo.play_intro()
		return Motion.seconds(_id)
	return LOOP_HOLD * 2.0


func _replay_later(seconds: float) -> void:
	var gen := _generation
	get_tree().create_timer(seconds).timeout.connect(func() -> void:
		if is_inside_tree() and gen == _generation and _loop:
			_play())


# --- Combat demos (ANIM-2 / ANIM-3) --------------------------------------------------------

# --- Screen demos (ANIM-6) -------------------------------------------------------------------

## A screen motion on a fresh piece over the stage (the stage's own pieces hide). Returns
## its length (s).
func _play_screen(what: String) -> void:
	_show_scene(false)
	if _screen_host != null:
		_screen_host.queue_free()
	_screen_host = Control.new()
	_screen_host.name = "ScreenDemo"
	_screen_host.position = Vector2(PANEL_W, 0)
	_screen_host.size = Vector2(1280 - PANEL_W, 720)
	add_child(_screen_host)
	var bg := ColorRect.new()
	bg.color = Palette.NIGHT_SKY
	bg.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	_screen_host.add_child(bg)
	_hud = HudStats.new()
	_hud.position = Vector2(30, 16)
	_hud.size = Vector2(820, 60)
	_screen_host.add_child(_hud)
	_hud.items = HUD_BEFORE.duplicate(true)
	var length := LOOP_HOLD
	match what:
		"glass", "paper":
			var page: Control = TerminalWindow.new("CITY GRID // SOLACE") if what == "glass" else ZinePanel.new("TERMINAL EVENT", -1.0)
			page.position = Vector2(120, 160)
			page.size = Vector2(560, 300)
			var words := Label.new()
			words.text = "%s\n%s\n> JACK IN" % [TYPE_TEXT, SUBTITLE_TEXT]
			words.autowrap_mode = TextServer.AUTOWRAP_WORD
			words.add_theme_color_override("font_color", Palette.TERMINAL_TEXT if what == "glass" else Palette.INK)
			(page.body if page is TerminalWindow else (page as ZinePanel).content).add_child(words)
			_screen_host.add_child(page)
			PageTransition.enter(page, PageTransition.Look.GLASS if what == "glass" else PageTransition.Look.PAPER)
		"menu":
			var win := TerminalWindow.new("REBEL_CELL // MAIN MENU")
			win.position = Vector2(120, 140)
			win.custom_minimum_size = Vector2(420, 0)
			_screen_host.add_child(win)
			for t in ["Continue", "Campaigns", "Tutorial", "Codex", "Options"]:
				var b := Button.new()
				b.text = t
				b.theme_type_variation = &"MenuItem"
				b.alignment = HORIZONTAL_ALIGNMENT_LEFT
				win.body.add_child(b)
			MenuMotion.attach(win.body)
			(win.body.get_child(0) as Button).grab_focus()
			for k in 3:
				var at := MENU_STEP * (k + 1)
				get_tree().create_timer(at).timeout.connect(func() -> void:
					if is_instance_valid(win):
						(win.body.get_child(k + 1) as Button).grab_focus())
			length = MENU_STEP * 4.0
		"modem":
			var sign := ModemSign.new()
			sign.position = Vector2(300, 90)
			sign.size = Vector2(230, 560)
			_screen_host.add_child(sign)
			sign.warm_up()
			length = Motion.delay_of(&"modem_trace") + Motion.seconds(&"modem_trace")
		"buy", "pick", "loot", "flap":
			var row := HBoxContainer.new()
			row.position = Vector2(160, 300)
			row.add_theme_constant_override("separation", 14)
			_screen_host.add_child(row)
			for i in 3:
				var card := ZineCard.new(["OVERCLOCK", "JAM", "CACHE"][i], i + 1, "Deal 8. Nudge +1.", i)
				card.hotkey = ""
				if what in ["buy", "flap"]:
					card.with_price(45 + i * 20)
					card.with_buy("BUY")
				row.add_child(card)
			await get_tree().process_frame
			await get_tree().process_frame
			var first := row.get_child(1) as ZineCard
			match what:
				"loot":
					var r := row.get_global_rect()
					for i in 3:
						(row.get_child(i) as ZineCard).fan_in(Vector2(r.get_center().x, r.end.y + 74.0), Motion.amplitude(&"loot_fan") * (i - 1.0), Motion.delay_of(&"loot_fan") * i)
				"flap":
					first.buy_button.flap(true)
				"buy":
					FlightFx.fly(self, first, _hud.icon_point(StatIcon.CARDS), &"buy_fly", "SOLD")
					first.visible = false
					_hud.items = HUD_AFTER.duplicate(true)
				"pick":
					FlightFx.fly(self, first, _hud.icon_point(StatIcon.CARDS), &"loot_pick", "", Motion.amplitude(&"loot_pick"))
					first.visible = false
					_hud.items = HUD_AFTER.duplicate(true)
			length = 1.0
		"stamp":
			var b := Button.new()
			b.text = "Pay them off (-20 Cycles)"
			b.theme_type_variation = &"NoteButton"
			b.position = Vector2(180, 300)
			_screen_host.add_child(b)
			await get_tree().process_frame
			await get_tree().process_frame
			FlightFx.stamp_on(self, b, "")
			b.visible = false
		"hud":
			await get_tree().process_frame
			_hud.items = HUD_AFTER.duplicate(true)
			length = Motion.seconds(&"count_up")
		"caption":
			_hud.captions = [[0, "CAMPAIGN"]]
			await get_tree().process_frame
			_hud.captions = [[0, "CAMPAIGN"], [2, "THIS RUN"]]
		"subtitle":
			Dialogue.clear()
			Dialogue.dock_at(Rect2(PANEL_W + 30, 90, 820, 60), 2)
			Dialogue.say(RC.Voice.DISPATCH, SUBTITLE_TEXT)
			length = SUBTITLE_TEXT.length() * Motion.seconds(&"dispatch_type")
		"drip", "halo":
			DripButton.reset_growth()
			var send := DripButton.new("SEND IT", "[Space]", DripButton.DRIP_PINK, 44, DripButton.SEND_IT_DRIPS)
			send.position = Vector2(260, 280)
			send.size = send.custom_minimum_size
			_screen_host.add_child(send)
			if what == "halo":
				send.settle_motion()
				send._set_hot(true)
			length = Motion.seconds(&"drip_grow")
		"saved":
			Fx.show_saved()
			length = Motion.delay_of(&"saved_stamp") + Motion.seconds(&"saved_stamp")
		"hum", "radio", "jack", "dossier":
			match what:
				"hum":
					var mon := TerminalWindow.new("CITY GRID // SOLACE")
					mon.position = Vector2(120, 140)
					mon.custom_minimum_size = Vector2(520, 260)
					_screen_host.add_child(mon)
					CrtHum.attach(mon)
					length = Motion.entry(&"hq_crt_hum").duration * 2.0
				"radio":
					var radio := ZineNote.new("PIRATE RADIO", Vector2(300, 150))
					radio.position = Vector2(200, 200)
					_screen_host.add_child(radio)
					radio.append(TYPE_TEXT)
					radio.append("vs Solace Collections | ICE 0")
					await get_tree().process_frame
					length = Typing.type_in(radio.label, _id if _id == &"event_type" else &"radio_type")
				"jack":
					var jack := ZineStamp.new("JACK IN", Palette.CELL_PINK)
					jack.icon_kind = StatIcon.JACK_IN
					jack.position = Vector2(300, 240)
					jack.size = Vector2(160, 160)
					_screen_host.add_child(jack)
					jack.breathe()
					length = Motion.entry(&"jack_ring_breathe").duration * 2.0
				"dossier":
					var card := CrewCard.new("VEX", "BREAKER", 1, 30, 40, "HP 30/40 · DECK 10", -1.5)
					card.position = Vector2(300, 150)
					_screen_host.add_child(card)
					await get_tree().process_frame
					card.tilt_polaroid(true)
		"city":
			var city := NeonCity.new()
			city.size = _screen_host.size
			city.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
			city.district = &"solace"
			_screen_host.add_child(city)
			_screen_host.move_child(_hud, -1)
			length = Motion.entry(&"hq_sign_flicker").duration
	print("motion_lab: screen demo %s, %.2f s" % [what, length])


## A motion on the lab's own wheel, card or SEND IT. Returns its length (s).
func _play_view(what: String) -> float:
	_show_scene(false)
	_clear_screen()
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
		"ready":
			var send := _pieces["send"] as DripButton
			send.glyph = true
			send.set_ready(false)
			send.set_ready(true)
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
	_clear_screen()
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
		"send_hit", "send_kill":
			# ANIM-R1 captures: a SEND IT whose hits land (the operative's wheel nudged until
			# the preview deals damage), and one that breaks the enemy (lab only: its HP set
			# low first, so the kill turn is the first one).
			for k in DEMO_NUDGE_TRIES:
				if _preview_hits(enemy):
					break
				_scene.nudge_wheel(&"player", 1)
			if what == "send_kill":
				_scene.engine.state().get_combatant(enemy).hp = DEMO_KILL_HP
				_scene._refresh(_scene.engine.state())
			_scene.skip_motion()
			await get_tree().process_frame
			_scene.end_turn()
		"send_lose":
			# ANIM-R5 combat: a SEND IT the operative does not survive (lab only: fights tried
			# until the enemy hits, the operative's HP set to 1): DEFEAT lands on its wheel and stays.
			for s in DEMO_BLOCK_SEEDS:
				if _enemy_hits_player():
					break
				_scene.start_fight(SCENE_ENEMY, SCENE_SEED + s + 1)
				_scene.skip_motion()
			_scene.engine.state().player.hp = 1
			_scene._refresh(_scene.engine.state())
			_scene.skip_motion()
			await get_tree().process_frame
			_scene.end_turn()
		"send_both":
			# ANIM-R4 C6a: a SEND IT where both sides land hits (fights and nudges tried until
			# the preview has the operative hitting the enemy and the enemy hitting back): the
			# operative's land in full, a gap, then the enemy's.
			var found := false
			for s in DEMO_BLOCK_SEEDS:
				for k in DEMO_NUDGE_TRIES:
					if _preview_hits(enemy) and _enemy_hits_player():
						found = true
						break
					_scene.nudge_wheel(&"player", 1)
				if found:
					break
				_scene.start_fight(SCENE_ENEMY, SCENE_SEED + s + 1)
				_scene.skip_motion()
				enemy = _scene.engine.state().enemies[0].id
			_scene.skip_motion()
			await get_tree().process_frame
			_scene.end_turn()
		"send_block":
			# ANIM-R3: a SEND IT where the enemy's hit reaches the operative and is soaked whole
			# (lab only: a fight whose enemy lands a hit, the operative given the guard for it):
			# the red projectile, 0 with a shield where it struck, ALL BLOCKED on impact.
			for s in DEMO_BLOCK_SEEDS:
				if _enemy_hits_player():
					break
				_scene.start_fight(SCENE_ENEMY, SCENE_SEED + s + 1)
				_scene.skip_motion()
			_scene.engine.state().player.block = DEMO_BLOCK
			_scene._refresh(_scene.engine.state())
			_scene.skip_motion()
			await get_tree().process_frame
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
			# ANIM-R4 C6e: a real SEND IT (the ANIM-R2 demo played made-up beats over the live
			# fight, so its tag read "MISS · half power" while a 14 flew). The operative's hits
			# pierce (its ring), so the guarded hit is the enemy's: fights tried until the enemy
			# hits the operative, who is given a block of a third of that hit (lab only), and the
			# forecast refreshed, so the tag says what then happens: the raw hit rides, meets
			# the guard where it strikes (sword - shield = through) and the rest pops and travels.
			var pl: StringName = _scene.engine.state().player.id
			for s in DEMO_BLOCK_SEEDS:
				var raw := _preview_raw_hit(pl)
				if raw > 1:
					_scene.engine.state().player.block = maxi(1, raw / DEMO_GUARD_SHARE)
					if _preview_guarded(pl):
						break
					_scene.engine.state().player.block = 0
				_scene.start_fight(SCENE_ENEMY, SCENE_SEED + s + 1)
				_scene.skip_motion()
				pl = _scene.engine.state().player.id
			_scene._refresh(_scene.engine.state())
			_scene.skip_motion()
			await get_tree().process_frame
			_scene.end_turn()
		"enter":
			ev.play_enter()
		"refuse":
			_scene.engine.state().ram = 0
			_scene._refresh(_scene.engine.state())
			# ANIM-R4 C6h: the lab set RAM to 0; that is no spend (no "-N RAM" float before the refusal).
			_scene.ram_note.finish_motion()
			_scene.select_card(0)
			_scene.respin()
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



## True when SEND IT would have the enemy hit the operative now (the engine's own preview).
func _enemy_hits_player() -> bool:
	var result: CombatResult = _scene.engine.preview_end_turn()
	if result == null:
		return false
	for e in result.events:
		if String(e.get("type", "")) == "damage" and StringName(String(e.get("target", ""))) == _scene.engine.state().player.id:
			return true
	return false


## The biggest raw hit SEND IT would land on `enemy` (any combatant) now that a guard can
## meet (no pierce; 0 when none), from the preview.
func _preview_raw_hit(enemy: StringName) -> int:
	var best := 0
	for e in _scene.engine.preview_end_turn().events:
		if String(e.get("type", "")) == "damage" and StringName(String(e.get("target", ""))) == enemy and not bool(e.get("pierce", false)):
			best = maxi(best, int(e.get("amount", 0)))
	return best


## True when SEND IT would land a hit on `enemy` (any combatant) that its guard partly
## takes (the preview).
func _preview_guarded(enemy: StringName) -> bool:
	for e in _scene.engine.preview_end_turn().events:
		if String(e.get("type", "")) == "damage" and StringName(String(e.get("target", ""))) == enemy and int(e.get("blocked", 0)) + int(e.get("shielded", 0)) > 0 and int(e.get("hp_damage", 0)) > 0:
			return true
	return false


## True when SEND IT would take HP off `enemy` now (the engine's own preview).
func _preview_hits(enemy: StringName) -> bool:
	for e in _scene.engine.preview_end_turn().events:
		if String(e.get("type", "")) == "damage" and StringName(String(e.get("target", ""))) == enemy and int(e.get("hp_damage", 0)) > 0:
			return true
	return false


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
