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
##   --demo-check=<frames> (ANIM-R5) prints, that many frames after the demo starts, which
##   scripts read the id ("motion_lab: <id> read by [...]"; the lab alone means no real piece).
##
## ANIM-R5: every demo shows its id's real motion. A motion the game plays with a Motion
## helper on a piece (a pop, a fade, a slide) plays with that helper on a lab piece; every
## other motion plays on the real piece that reads it: a live combat scene ("scene"), a
## fresh kit piece ("screen": the drop layer, the Heat poster, a toast, the top bar), Fx
## (the flash, the jack and its CONNECTING bar and RAID INCOMING stamp), the HQ scene on a
## demo campaign in the lab's own save slot ("hq": its city map's selection, a defence
## dropping, a raid, the influence spreading) or the netrun scene ("netrun": a route move).
## test_motion_lab_demos.gd plays every demo with Motion.recording on and checks it.

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
	&"screen_flash": ["fx_flash", "stage"], &"hit_freeze": ["freeze", "wheel"],
	&"saved_stamp": ["screen", "saved"], &"toast": ["screen", "toast"],
	&"jack_in": ["jack_in", "stage"], &"jack_out": ["jack_out", "stage"], &"jack_fade_reduced": ["jack_reduced", "stage"],
	&"wheel_spin": ["view", "turn"], &"wheel_spin_blur": ["view", "turn"], &"wheel_nudge": ["view", "nudge"],
	&"precision_perfect": ["scene", "perfect"], &"precision_good_ring": ["view", "good"],
	&"precision_weak": ["shake", "wheel"], &"precision_blink": ["blink", "wheel"], &"precision_null_static": ["view", "null"],
	&"card_hover": ["view", "hover"], &"card_play": ["scene", "play"], &"card_draw": ["scene", "deal"], &"card_exhaust": ["scene", "exhaust"],
	&"send_it_press": ["view", "press"], &"send_it_drips": ["view", "press"], &"resolve_pass": ["scene", "send_hit"], &"resolve_pulse": ["view", "pulse"],
	&"number_float": ["scene", "numbers"], &"number_crit": ["scene", "numbers"], &"hp_lag": ["view", "hp"],
	&"intent_flip": ["view", "tag"], &"rewind_scrub": ["scene", "rewind"],
	&"pointer_flicker": ["pulse_pointer", "wheel"], &"orbit_trail": ["view", "orbit"],
	&"enemy_break": ["scene", "send_kill"], &"hub_shatter": ["scene", "shatter"],
	&"heat_pulse": ["heat", "stage"], &"heat_letters_shake": ["shake", "number"], &"poster_stamp": ["screen", "poster"],
	&"hq_crt_hum": ["screen", "hum"], &"radio_type": ["screen", "radio"], &"jack_ring_breathe": ["screen", "jack"], &"polaroid_tilt": ["screen", "dossier"],
	&"site_outline_draw": ["hq", "select"], &"map_camera_ease": ["hq", "select"], &"route_crawl": ["netrun", "route"], &"asset_drop": ["hq", "drop"],
	&"raid_move": ["hq", "raid"], &"turret_trace": ["hq", "raid"], &"raid_flip": ["hq", "raid"],
	&"route_pulse": ["netrun", "route"], &"node_pop": ["netrun", "route"], &"visited_dim": ["netrun", "route"],
	&"panel_in": ["screen", "glass"], &"panel_crt_roll": ["screen", "glass"], &"panel_drop": ["screen", "paper"],
	&"menu_cursor_blink": ["screen", "menu"], &"menu_type": ["screen", "menu"], &"menu_highlight": ["screen", "menu"],
	&"mainframe_sign_warmup": ["screen", "mainframe"], &"mainframe_trace": ["screen", "mainframe"], &"buy_fly": ["screen", "buy"], &"note_flap": ["screen", "flap"],
	&"loot_fan": ["screen", "loot"], &"loot_pick": ["screen", "pick"], &"count_up": ["screen", "hud"],
	&"dispatch_type": ["screen", "subtitle"], &"subtitle_bar_in": ["screen", "subtitle"],
	&"drip_grow": ["screen", "drip"], &"drip_halo": ["screen", "halo"],
	&"beacon_blink": ["screen", "city"], &"city_traffic": ["screen", "city"], &"hq_sign_flicker": ["screen", "city"],
	&"sticky_bump": ["screen", "hud"], &"number_roll": ["screen", "hud"],
	&"ice_lock_ring": ["hq", "raid_ice"], &"decoy_fire": ["hq", "raid"], &"raid_hit_effect": ["hq", "raid"],
	&"node_damage_number": ["hq", "raid"], &"forecast_stamp_resolve": ["pop", "panel"],
	&"card_pickup": ["pop", "card"], &"drag_ghost_follow": ["scene", "drag"], &"drop_zone_pulse": ["scene", "aim"],
	&"aim_line_draw": ["scene", "aim"], &"target_snap": ["scene", "aim"], &"drag_cancel_return": ["scene", "cancel"],
	&"card_stamp": ["scene", "play_fx"], &"effect_burst": ["scene", "play_fx"], &"card_discard": ["scene", "send"],
	&"resolve_beat": ["scene", "send"], &"block_number": ["scene", "beat_block"], &"heal_number": ["scene", "beat_heal"],
	&"hp_drain": ["view", "hp"], &"status_stamp": ["scene", "send"], &"last_turn_reveal": ["scene", "send"],
	&"wheel_respin": ["view", "respin"], &"inner_ring_turn": ["view", "nudge_inner"], &"pointer_migrate": ["view", "migrate"],
	&"pointer_orbit": ["view", "orbit"], &"enemy_turn_spin": ["view", "respin"],
	&"drag_pickup": ["pop", "sticker"], &"drag_follow": ["screen", "drop_carry"], &"drop_settle": ["screen", "drop_land"],
	&"drop_reject": ["screen", "drop_refuse"], &"loadout_swap": ["screen", "drop_land"], &"crew_assign": ["pop", "card"],
	&"influence_crossfade": ["hq", "influence"], &"influence_spread": ["hq", "influence"],
	# ANIM-2 / ANIM-3 (combat): "view" plays on the lab's wheel / card / SEND IT; "scene"
	# plays in a live combat scene over the whole lab (1280x720).
	&"resolve_sequence": ["scene", "send_hit"], &"hit_line": ["scene", "send_hit"], &"victory_stamp": ["scene", "victory"],
	&"combat_end_hold": ["netrun", "fight_won"], &"wheel_flip": ["view", "flip"], &"dead_wheel_fade": ["scene", "break"],
	&"drag_ghost_tilt": ["scene", "drag"], &"card_pile": ["scene", "deal"], &"hand_reflow": ["scene", "play"],
	&"ram_tick": ["scene", "ram"], &"ram_pending_blink": ["scene", "aim"],
	# ANIM-5 (map, raid, jack and Heat):
	&"jack_scanlines": ["jack_in", "stage"], &"raid_step_gap": ["hq", "raid"], &"home_lag": ["hq", "raid"],
	&"minimap_pulse": ["hq", "grid"], &"select_ring_ease": ["hq", "select"], &"legend_fold": ["hq", "legend"],
	# ANIM-4 (HQ drag and drop; in context: hq_scene --demo-anim=drag_*):
	&"drop_stamp": ["screen", "drop_land"], &"market_fly": ["screen", "market"],
	# ANIM-6 (screens): "screen" builds a fresh piece on the stage (a menu, the Mainframe sign, a
	# loot row, the top bar, a dossier...) and plays the real motion on it.
	&"saved_stamp_in": ["screen", "saved"], &"pad_prompts_in": ["fade_in", "sticker"], &"focus_tip_in": ["fade_in", "panel"],
	&"event_outcome_pop": ["pop", "sticker"], &"event_choice_stamp": ["screen", "stamp"], &"sold_stamp": ["screen", "buy"],
	&"caption_crossfade": ["screen", "caption"], &"city_sign_pick": ["screen", "city"],
	# ANIM-4b (drag and drop in the run; in context: netrun_scene --demo-shop / --demo-loot
	# --demo-anim=drag_*):
	&"drop_buy": ["screen", "drop_buy"], &"shred_feed": ["screen", "drop_shred"],
	# ANIM-R1 (the first fix batch; in context: hq_scene / netrun_scene --demo-anim=<id>):
	&"jack_arrive": ["jack_in", "stage"], &"jack_arrival_wait": ["jack_in", "stage"],
	&"select_ring_pulse": ["hq", "select"], &"loot_reject": ["screen", "reject"], &"home_number_fly": ["hq", "raid_ice"], &"influence_mark": ["hq", "influence"], &"heat_number_pop": ["screen", "poster"], &"heat_banner": ["screen", "poster"],
	# ANIM-R1 (combat and input): the SEND IT replay's pieces play in a live SEND IT.
	&"resolve_landing_hold": ["scene", "send"], &"landing_pulse": ["scene", "send"], &"resolve_result_hold": ["scene", "send"],
	&"result_caption": ["scene", "send"], &"result_stamp": ["scene", "send"], &"number_to_hp": ["scene", "numbers"],
	&"hit_flash": ["scene", "beat_hit"], &"hit_shake": ["scene", "beat_hit"], &"enemy_enter": ["scene", "enter"],
	&"victory_flash": ["scene", "victory"], &"boss_phase_flash": ["scene", "boss_phase"],
	&"ram_refusal": ["scene", "refuse"], &"ram_refusal_pop": ["scene", "refuse"], &"send_it_ready": ["view", "ready"],
	&"send_it_drips_share": ["view", "press"], &"drag_ghost_tilt_speed": ["scene", "drag"],
	&"toast_note_hold": ["screen", "toast_note"], &"stamp_fade_in": ["screen", "stamp"],
	# ANIM-R2 (city, maps and transitions; in context: hq_scene / netrun_scene --demo-anim=<id>):
	&"city_bake_fade": ["hq", "influence"], &"jack_connect": ["jack_in", "stage"], &"raid_outcome_stagger": ["hq", "raid"], &"raid_result_banner": ["hq", "raid"], &"asset_drop_stamp": ["hq", "drop"], &"influence_tint": ["hq", "influence"], &"route_target_pulse": ["netrun", "route"],
	# ANIM-R2 (combat, events and screens):
	&"hit_absorb": ["scene", "send_hit"], &"ram_spend_float": ["scene", "ram_spend"], &"price_refusal": ["screen", "refusal"],
	# ANIM-R3 (city, raid, jack, heat and route; in context: hq_scene --demo-raid --demo-anim=asset_drop):
	&"asset_drop_wait": ["hq", "drop_wait"], &"asset_drop_grow": ["hq", "drop"], &"forecast_change": ["hq", "drop"], &"jack_dissolve": ["jack_in", "stage"],
	# ANIM-R3 (combat, input and screens): each plays in a live SEND IT.
	&"impact_mark": ["scene", "send_block"], &"forecast_tick": ["scene", "send_hit"], &"forecast_fade": ["scene", "send_hit"],
	&"status_mark": ["scene", "beat_status"],
	# ANIM-R4 (city, raid, Heat, route and HQ):
	&"forecast_change_fade": ["hq", "drop"], &"raid_incoming_hold": ["jack_in", "stage"], &"forecast_road_pulse": ["hq", "drop"],
	# ANIM-R4 (combat, input and screens): the shares that were inline play where they act (a
	# live SEND IT, the break, the MAINFRAME sign); the two sides one after the other in a SEND IT
	# where both hit; the RAM refill in the RAM demo.
	&"hit_line_flight": ["scene", "send_hit"], &"ride_swap": ["scene", "send_hit"], &"ride_shrink": ["scene", "send_hit"],
	&"ride_perfect": ["scene", "beat_hit"], &"break_crack": ["scene", "send_kill"], &"mainframe_sign_strike": ["screen", "mainframe"],
	&"mainframe_sign_flicker": ["screen", "mainframe"], &"resolve_side_gap": ["scene", "send_both"], &"resolve_attacker_gap": ["scene", "send_both"],
	&"ram_refill_float": ["scene", "ram"], &"event_type": ["screen", "radio"],
	# ANIM-R5 combat: the lost fight's DEFEAT stamp (a SEND IT the operative does not survive).
	&"defeat_stamp": ["scene", "send_lose"],
	# ANIM-R5 (netrun screens; in context: netrun_scene --demo-shop --demo-buy): the top bar
	# CARDS tag a flight lands on (HudStats.land_pulse).
	&"flight_land_pulse": ["screen", "land_pulse"],
	# ANIM-R6 rules: the flight's and the stamp's shares, on the real flight and stamp.
	&"flight_lift_share": ["screen", "pick"], &"flight_fade_share": ["screen", "buy"],
	&"choice_stamp_down_share": ["screen", "stamp"], &"choice_stamp_hold_share": ["screen", "stamp"],
	# ANIM-R6 city: the raid volley's stagger (a raid with two guns) and the Heat pulse's rise.
	&"raid_shot_stagger": ["hq", "raid"], &"heat_pulse_rise": ["heat", "stage"], &"raid_threat_withdraw": ["hq", "raid"],
	# ANIM-R6 combat: the tutorial's Next (TutorialOverlay plays it with Motion.loop_pulse).
	&"tutorial_next_pulse": ["pulse", "sticker"],
	# ART-0 E (ported from art-pass W6): the wheel-local T3 bursts on the fight's wheels (the
	# Perfect's on the operative's, a boss phase's on an enemy's in the corp hue).
	&"wheel_burst_perfect": ["scene", "perfect"], &"wheel_burst_phase": ["scene", "phase_burst"],
	# ART-0 F (ported from art-pass W2 / W8a): kit behaviour on the real pieces (a native
	# button's pad focus, a refused sticker, a confirm opened and closed as a modal).
	&"focus_scale": ["screen", "kit_focus"], &"button_refused": ["screen", "kit_refused"],
	&"modal_in": ["screen", "modal_open"], &"modal_out": ["screen", "modal_close"],
	# ART-9 4B: the portrait feeds (idle, talking, stationed) and DISPATCH's voice trace.
	&"portrait_feed": ["screen", "feed"], &"portrait_blink": ["screen", "feed"], &"portrait_talk": ["screen", "feed"],
	&"dispatch_trace": ["screen", "feed"],
}

## Screen demos (ANIM-6): the top bar's values before and after a change, the text a
## subtitle demo says, and how long the frames between a menu's focus moves are (s).
const HUD_BEFORE := [["HEAT", "12", "/100"], ["SCHEMATICS", "40", ""], ["CYCLES", "85", ""], ["CARDS", "10", ""]]
const HUD_AFTER := [["HEAT", "12", "/100"], ["SCHEMATICS", "40", ""], ["CYCLES", "140", ""], ["CARDS", "11", ""]]
const SUBTITLE_TEXT := "Jacking you in. The rack is two hops out: keep your Heat down."
const MENU_STEP := 0.45
## How long a screen demo holds before it loops (s).
const SCREEN_LOOP := 2.5
## ANIM-R5 context demos: the scenes, the lab's own save slot (never the player's), the
## frames a scene lays out (and its city's camera eases) before its motion plays, how long
## a context demo holds before it loops (s), and the demo campaign's seed.
const HQ_SCENE := "res://scenes/hq/hq_scene.tscn"
const NETRUN_SCENE := "res://scenes/netrun_map/netrun_scene.tscn"
const LAB_SLOT := "motion_lab"
const CONTEXT_SETTLE := 20
const CONTEXT_BAKE_FRAMES := 240
const CONTEXT_LOOP := 6.0
const DEMO_CAMPAIGN_SEED := 1
## The jack demos' destination line and the raid interlude's stamp (translated).
const JACK_DESTINATION := "SOLACE // THE RACK"
## ANIM-R6 C14: the words the game stamps (RunManager.jack_note: "RAID INCOMING" over the
## raiding corporation), for the demo campaign's corporation.
const RAID_NOTE := "RAID INCOMING\n%s"
const RAID_CORP := &"solace"


## ANIM-R6 C14: the RAID INCOMING stamp as the game words it (translated, the corporation's
## name from its content).
static func _raid_note() -> String:
	var corp := RunManager.lookup().get_content(RAID_CORP)
	return TranslationServer.translate(RAID_NOTE) % (TextDb.t(corp, "display_name") if corp != null else "")
## Screen demos: the RAM a spend float shows, the Heat before and after a crossing and its
## thresholds, the refusal's words, the toast's words.
const DEMO_RAM_SPEND := 2
const HEAT_FROM := 20
const HEAT_TO := 30
const HEAT_MAX := 100
const HEAT_MARKS: Array[int] = [25, 50, 75]
const REFUSAL_TAG := "CYCLES"
const REFUSAL_TEXT := "NEED 40 CYCLES"
const TOAST_TEXT := "NOT ENOUGH RAM"
## Beat demos: the amount a made beat carries.
const DEMO_BEAT_AMOUNT := 6

## ANIM-R5 HQ demos: the demo campaign's Schematics and the raid demo's defences (a turret
## shoots, a decoy draws fire, an ICE lock holds).
const DEMO_SCHEMATICS := 400
const DEMO_DEFENCES: Array[StringName] = [&"turret", &"decoy"]
## The ICE raid: an ICE lock holds a link and home, undefended, is hit.
const DEMO_ICE_DEFENCES: Array[StringName] = [&"ice_lock"]
## The drop demo's forecast change at CORE (a defence lowers the damage home takes).
const DEMO_FORECAST_FROM := 50
const DEMO_FORECAST_TO := 45

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
## ANIM-R5: the HQ or netrun scene a context demo plays in (and its host).
var _context: Control = null
var _context_host: Control = null
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
## ANIM-R5 --demo-check: the frame the readers are printed on (-1: no check).
var _check_at := -1

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
		elif arg.begins_with("--demo-check="):
			_check_at = DEMO_START_FRAME + int(arg.trim_prefix("--demo-check="))
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
	_clear_context()


func _process(_delta: float) -> void:
	if _demo and _frames == DEMO_START_FRAME:
		print("motion_lab: %s starts on frame %d (speed %.2fx)" % [_id, _frames, Motion.speed])
		if _check_at >= 0:
			Motion.start_recording()
		_play()
	if _frames == _check_at:
		print("motion_lab: %s read by %s" % [_id, Motion.readers(_id)])
		Motion.stop_recording()
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


## ANIM-R5: takes a context demo's scene away and forgets its campaign (the lab's own slot;
## the player's save is never touched).
func _clear_context() -> void:
	if _context_host != null and is_instance_valid(_context_host):
		_context_host.queue_free()
	_context_host = null
	_context = null
	if RunManager.save_slot == LAB_SLOT:
		RunManager.delete_save()
		RunManager.save_slot = RunManager.DEFAULT_SLOT
		RunManager.reset()


## Takes a screen demo's piece away (the stage's own pieces show again).
func _clear_screen() -> void:
	if _screen_host != null:
		_screen_host.queue_free()
	_screen_host = null
	_hud = null


func _reset_stage() -> void:
	_clear_screen()
	_clear_context()
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
			# ART-0 E: a full-screen flash is T4 only (ART_BIBLE v2 5.3).
			Fx.flash(Color.WHITE, amp, Motion.seconds(_id), VfxTier.T4)
		"fx_flash":
			# ANIM-R5: Fx's own flash (its strength and time from `screen_flash`; T4).
			Fx.flash(Color.WHITE, -1.0, -1.0, VfxTier.T4)
		"heat":
			# ANIM-R2 R8 / ANIM-R3 B9: a Heat crossing distorts round the poster only.
			Fx.heat_pulse_at(target.get_global_rect())
		"freeze":
			Fx.freeze_frames()
			length = LOOP_HOLD
		"jack_in":
			# ANIM-R5: with its CONNECTING line (and the raid interlude's stamp for its id).
			Fx.jack_in(func() -> void: pass, -1.0, JACK_DESTINATION, _raid_note() if _id == &"raid_incoming_hold" else "")
		"jack_out":
			Fx.jack_out(func() -> void: pass, -1.0, JACK_DESTINATION)
		"jack_reduced":
			_play_jack_reduced()
		"view":
			length = _play_view(String(demo[1]))
		"screen":
			_play_screen(String(demo[1]))
			length = SCREEN_LOOP
		"scene":
			_play_scene(String(demo[1]))
			length = maxf(LOOP_HOLD, Motion.seconds(&"resolve_sequence"))
		"hq", "netrun":
			_play_context(String(demo[0]), String(demo[1]))
			length = CONTEXT_LOOP
	_show_values()
	if _loop:
		_replay_later(maxf(length, 0.0) + LOOP_GAP)


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
			words.autowrap_mode = TextServer.AUTOWRAP_WORD_SMART
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
			# ANIM-R5: the window held weakly (the next demo may free it before a step).
			var win_ref: WeakRef = weakref(win)
			for k in 3:
				var at := MENU_STEP * (k + 1)
				get_tree().create_timer(at).timeout.connect(func() -> void:
					var w := win_ref.get_ref() as TerminalWindow
					if w != null:
						(w.body.get_child(k + 1) as Button).grab_focus())
			length = MENU_STEP * 4.0
		"mainframe":
			var sign := MainframeSign.new()
			sign.position = Vector2(300, 90)
			sign.size = Vector2(230, 560)
			_screen_host.add_child(sign)
			sign.warm_up()
			length = Motion.delay_of(&"mainframe_trace") + Motion.seconds(&"mainframe_trace")
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
			if not is_instance_valid(row):
				return
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
		"land_pulse":
			# ANIM-R6 B7: the real top bar (HudBar.land_pulse, as the netrun plays it): a card's
			# landing pulses CARDS, a Daemon's pops the DAEMONS icon, a chip's pops VIEW LOADOUT.
			_hud.visible = false
			var bar := HudBar.new()
			bar.name = "LandBar"
			bar.position = Vector2(20, 12)
			bar.size = Vector2(1280 - PANEL_W - 40, HudBar.BAND_HEIGHT)
			_screen_host.add_child(bar)
			bar.set_stats(HUD_BEFORE.duplicate(true))
			bar.set_daemons([&"twin_pointer"] as Array[StringName])
			bar.loadout_button.visible = true
			await get_tree().process_frame
			if not is_instance_valid(bar):
				return
			for kind in ["card", "daemon", "chip"]:
				bar.land_pulse(kind)
			length = Motion.delay_of(&"flight_land_pulse") + Motion.seconds(&"flight_land_pulse")
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
		"feed":
			# ART-9 4B: a live feed, a talking one, a stationed one and DISPATCH's trace.
			var modes := [PortraitFeed.Mode.IDLE, PortraitFeed.Mode.TALK, PortraitFeed.Mode.STATIONED, PortraitFeed.Mode.VOICE]
			for i in modes.size():
				var f := PortraitFeed.dispatch() if modes[i] == PortraitFeed.Mode.VOICE else PortraitFeed.new(&"rigger", &"op_1", "SPROCKET", modes[i])
				f.site = "LANE 15 RELAY"
				f.position = Vector2(30 + i * 210, 160)
				f.size = Vector2(196, 218)
				_screen_host.add_child(f)
			length = maxf(Motion.amplitude(&"portrait_blink"), Motion.entry(&"portrait_feed").duration)
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
		"toast":
			var t := Toast.new()
			_screen_host.add_child(t)
			t.show_text(TOAST_TEXT, Vector2(300, 300))
		"toast_note":
			ToastNote.show_on(_screen_host, TOAST_TEXT)
		"poster":
			var poster := HeatPoster.new()
			poster.position = Vector2(200, 110)
			_screen_host.add_child(poster)
			await get_tree().process_frame
			if not is_instance_valid(poster):
				return
			poster.set_heat(HEAT_FROM, HEAT_MAX, HEAT_MARKS)
			poster.set_heat(HEAT_TO, HEAT_MAX, HEAT_MARKS)
		"refusal":
			await get_tree().process_frame
			if is_instance_valid(_hud):
				_hud.flash_refusal(REFUSAL_TAG, REFUSAL_TEXT)
		"reject":
			var card := ZineCard.new("JAM", 1, "Deal 8. Nudge +1.", 0)
			card.hotkey = ""
			card.position = Vector2(260, 260)
			_screen_host.add_child(card)
			await get_tree().process_frame
			await get_tree().process_frame
			if is_instance_valid(card):
				FlightFx.fly(self, card, card.get_global_rect().get_center() + Vector2(0.0, Motion.amplitude(&"loot_reject")), &"loot_reject")
				card.visible = false
		"drop_land", "drop_buy", "drop_shred", "drop_refuse", "drop_carry", "market":
			await _play_drop(what)
			length = 1.5
		"kit_focus":
			# ART-0 F: a pad player's focus on a native button grows it about its centre
			# (UiFocus, `focus_scale`); the pad is in use for this focus move only.
			var b := Button.new()
			b.text = "JACK IN"
			b.position = Vector2(260, 300)
			_screen_host.add_child(b)
			UiFocus.install_on(b)
			await get_tree().process_frame
			if not is_instance_valid(b):
				return
			var pad_was := Settings.pad_active
			Settings.pad_active = true
			b.grab_focus()
			Settings.pad_active = pad_was
		"kit_refused":
			# ART-0 F: a refused sticker (KitState: HARM outline flash, no-entry mark).
			var s := StickerButton.new("RESPIN")
			s.position = Vector2(260, 300)
			_screen_host.add_child(s)
			await get_tree().process_frame
			if is_instance_valid(s):
				s.refuse()
			length = Motion.seconds(KitState.REFUSED_MOTION)
		"modal_open", "modal_close":
			# ART-0 F: a modal opens (fade and grow, `modal_in`), then closes (`modal_out`).
			var m := ConfirmDialog.new(TYPE_TEXT)
			m.position = Vector2(220, 240)
			_screen_host.add_child(m)
			PageTransition.open_modal(m)
			if what == "modal_close":
				await get_tree().create_timer(Motion.seconds(&"modal_in") + LOOP_GAP).timeout
				if is_instance_valid(m):
					PageTransition.close_modal(m)
		"city":
			var city := NeonCity.new()
			city.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
			city.district = &"solace"
			_screen_host.add_child(city)
			_screen_host.move_child(_hud, -1)
			length = Motion.entry(&"hq_sign_flicker").duration
	print("motion_lab: screen demo %s, %.2f s" % [what, length])


## ANIM-R5: the jack under reduce effects (its fade, `jack_fade_reduced`): reduce effects
## on for this jack only (the setting's value, never saved), then back.
func _play_jack_reduced() -> void:
	var was := Settings.reduce_effects
	Settings.reduce_effects = true
	Fx.apply_settings()
	await Fx.jack_in(func() -> void: pass, -1.0, JACK_DESTINATION)
	Settings.reduce_effects = was
	Fx.apply_settings()


## ANIM-R5: the real DropLayer on a card and a slot: a landing (`loadout_swap`, its settle
## and stamp), a purchase (`drop_buy`), a shred (`shred_feed`), a refusal (`drop_reject`),
## a carry's aim (`drag_follow`) and the market's flight (`market_fly`).
func _play_drop(what: String) -> void:
	var layer := DropLayer.new()
	_screen_host.add_child(layer)
	var card := ZineCard.new("OVERCLOCK", 2, "Deal 8. Nudge +1.", 0)
	card.hotkey = ""
	card.position = Vector2(140, 280)
	_screen_host.add_child(card)
	var slot := Panel.new()
	slot.position = Vector2(560, 250)
	slot.size = Vector2(200, 260)
	_screen_host.add_child(slot)
	await get_tree().process_frame
	await get_tree().process_frame
	if not is_instance_valid(layer):
		return
	layer.ghost_maker = func(_p: Dictionary, _holder: Control) -> Control:
		var copy := ZineCard.new("OVERCLOCK", 2, "Deal 8. Nudge +1.", 0)
		copy.hotkey = ""
		return copy
	var refuse := what == "drop_refuse"
	layer.check = func(_p: Dictionary, _t: Dictionary) -> String:
		return "FULL" if refuse else ""
	var p := {"kind": "card"}
	if what == "drop_buy":
		p["motion"] = &"drop_buy"
		p["land"] = "buy"
	elif what == "drop_shred":
		p["land"] = "shred"
	layer.add_target("slot", ["card"], "slot", 0, DropLayer.rect_of(slot))
	layer.add_source(card, p)
	if what == "market":
		layer.buy_flight(p, card.get_global_rect(), DropLayer.rect_of(slot))
		return
	if what == "drop_carry":
		# The carried copy follows the aim from one target to the next (`drag_follow`).
		var other := Panel.new()
		other.position = Vector2(820, 250)
		other.size = slot.size
		_screen_host.add_child(other)
		layer.add_target("other", ["card"], "slot", 1, DropLayer.rect_of(other))
	layer.start_carry(card)
	if what == "drop_carry":
		layer.step_aim(1)
	else:
		layer.drop_on("slot")


## ANIM-R5: a motion in the HQ or the netrun scene (the real screen, on a demo campaign in
## the lab's own save slot): `what` names what it plays.
func _play_context(scene: String, what: String) -> void:
	_show_scene(false)
	_clear_screen()
	_clear_context()
	RunManager.scene_switching_enabled = false
	RunManager.save_slot = LAB_SLOT
	RunManager.delete_save()
	_context_host = Control.new()
	_context_host.size = Vector2(1280, 720)
	add_child(_context_host)
	var host := _context_host
	if scene == "netrun":
		_context = load(NETRUN_SCENE).instantiate()
		host.add_child(_context)
		_context.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
		_context.new_campaign(DEMO_CAMPAIGN_SEED)
		_context.start_run(1)
		var s := RunManager.netrun
		if what == "fight_won":
			# ANIM-R6 A15: the run's first node is a fight (as --demo-combat); it is won there.
			_context.enter_node(s.available_nodes()[0])
		else:
			var first: StringName = s.available_nodes()[0]
			s.run.current_node_id = first
			s.run.visited.append(first)
			_context._show_map()
	else:
		_demo_campaign(what)
		_context = load(HQ_SCENE).instantiate()
		host.add_child(_context)
		_context.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	for f in CONTEXT_SETTLE:
		await get_tree().process_frame
	# As the scenes' own captures: the city's look baked and its camera settled first (a
	# change then spreads from what was seen), at most CONTEXT_BAKE_FRAMES.
	for f in CONTEXT_BAKE_FRAMES:
		if not is_instance_valid(host) or host != _context_host:
			return
		var city: NeonCity = _context.background.city if scene == "netrun" or _context.background.visible else _context.wireframe.city
		if city.showing_current_look() and city.camera_settled() and city.bake_fade >= 1.0:
			break
		await get_tree().process_frame
	if not is_instance_valid(host) or host != _context_host:
		return
	var hq := _context
	var c := RunManager.campaign
	match what:
		"fight_won":
			# The fight is won by SEND IT; VICTORY stands until the netrun opens the loot after
			# `combat_end_hold`. The scene waits for its fight itself (the jack may still run).
			hq._demo_combat_end("win")
		"route":
			hq.enter_node(RunManager.netrun.available_nodes()[0])
		"select":
			hq.show_grid()
			await get_tree().process_frame
			if is_instance_valid(hq):
				hq.select_site(hq.stepped_site(1))
		"grid":
			# The HQ's minimap pulses a Site whose status changed since it was last seen.
			hq.show_hq()
			await get_tree().process_frame
			if not is_instance_valid(hq):
				return
			_claim_next(c)
			hq.show_hq()
		"legend":
			# The City Grid's key folds its rows away and opens them again.
			hq.show_grid()
			for f in CONTEXT_SETTLE:
				await get_tree().process_frame
			if is_instance_valid(hq) and hq.grid_legend != null:
				var legend: MapLegend = hq.grid_legend
				legend.set_opened(true)
				legend.set_opened(false)
				await get_tree().create_timer(Motion.delay_of(&"legend_fold") + Motion.seconds(&"legend_fold")).timeout
				if is_instance_valid(legend):
					legend.set_opened(true)
		"drop", "drop_wait":
			hq.show_raid()
			for f in CONTEXT_SETTLE:
				await get_tree().process_frame
			if not is_instance_valid(hq):
				return
			var site := _defended_site(c)
			c.armory = [&"turret"]
			hq.deploy_asset(0, site)
			await get_tree().process_frame
			if not is_instance_valid(hq):
				return
			if what == "drop_wait":
				# The drop waits for a camera that never settles, at most `asset_drop_wait`.
				hq.city_overlay.drop_asset(site, func() -> bool: return false, tr("TURRET"))
			else:
				# The drop as the raid setup plays it: CORE's forecast changes (its number rises
				# when the pulse along the threat road arrives).
				var core := c.grid.home_site_id
				hq.city_overlay.drop_asset(site, Callable(), tr("TURRET"),
					[{"site": core, "from": DEMO_FORECAST_FROM, "to": DEMO_FORECAST_TO}], hq.threat_road(site))
		"raid", "raid_ice":
			hq.show_raid()
			for f in CONTEXT_SETTLE:
				await get_tree().process_frame
			if is_instance_valid(hq):
				hq.fight_raid()
		"influence":
			# A second Site cleared and claimed: the tint spreads from it once its look bakes.
			_claim_next(c)
			var city: NeonCity = hq.background.city if hq.background.visible else hq.wireframe.city
			city.sync_influence()
	print("motion_lab: %s demo %s" % [scene, what])


## Clears and claims the first launchable Site of `c` not yet claimed.
func _claim_next(c: CampaignState) -> void:
	var corp := RunManager.corporation
	for sd in RunManager.launchable_sites():
		if not c.grid.is_claimed(sd.id):
			var run := RunState.new()
			run.site_id = sd.id
			CampaignRules.on_run_completed(c, corp, RunManager.config(), run)
			CampaignRules.claim(c, corp, RunManager.config(), RunManager.lookup(), sd.id, &"firewall_relay")
			return


## A claimed Site of `c` that isn't home (the demo's defence goes there).
func _defended_site(c: CampaignState) -> StringName:
	for id in c.grid.claimed_ids():
		if id != c.grid.home_site_id:
			return id
	return c.grid.home_site_id


## ANIM-R5: the demo campaign the HQ demos play on (the lab's own slot): a Site next to home
## cleared and claimed, defended by a turret, a decoy and an ICE lock, and a raid queued.
func _demo_campaign(what: String) -> void:
	RunManager.new_campaign(DEMO_CAMPAIGN_SEED)
	var c := RunManager.campaign
	var corp := RunManager.corporation
	c.schematics = DEMO_SCHEMATICS
	var first: StringName = corp.city_grid.get_site(c.grid.home_site_id).links[0]
	var run := RunState.new()
	run.site_id = first
	CampaignRules.on_run_completed(c, corp, RunManager.config(), run)
	CampaignRules.claim(c, corp, RunManager.config(), RunManager.lookup(), first, &"firewall_relay")
	if what in ["raid", "raid_ice"]:
		var defences := DEMO_ICE_DEFENCES if what == "raid_ice" else DEMO_DEFENCES
		c.armory = defences.duplicate()
		for i in defences.size():
			CampaignRules.deploy_asset(c, RunManager.config(), RunManager.lookup(), 0, first)
	if c.pending_raids.is_empty():
		CampaignRules.queue_raid(c, corp, RC.RaidTriggerSource.STORY, &"", "motion lab")


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
		"null":
			_wheel.play_null_static(0)
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
			_wheel.intent = {"type": RC.SliceType.SHIM, "text": "SHIM · GOOD %d" % _generation, "chips": [{"text": "HITS 8", "color": Palette.CELL_PINK, "ink": Palette.INK}]}
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
			# ANIM-R6 A18: a deterministic fallback when no fight tried has the enemy hitting
			# (lab only): the enemy's wheel is turned tick by tick until SEND IT loses.
			var st: CombatState = _scene.engine.state()
			var foe: CombatantState = st.enemies[0]
			var base_rot := foe.wheel.rotation
			for k in RC.TICKS:
				if _scene.engine.preview_end_turn().state.outcome == CombatState.Outcome.DEFEAT:
					break
				foe.wheel.rotation = (base_rot + k + 1) % RC.TICKS
			if _scene.engine.preview_end_turn().state.outcome != CombatState.Outcome.DEFEAT:
				push_warning("motion_lab: send_lose found no losing SEND IT")
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
			# ANIM-R5: the first hand card that plays (card 0 may want RAM or a target it lacks).
			var n: int = _scene.engine.state().hand.size()
			for i in n:
				_scene.select_card(i)
				if _scene.selecting >= 0:
					_scene.confirm_selection()
				if _scene.engine.state().hand.size() < n:
					break
				_scene.cancel_selection()
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
			# fight, so its tag read "NULL · half power" while a 14 flew). The operative's hits
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
			_scene._victory_flash()
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
		"ram_spend":
			_scene.ram_note.float_spend(DEMO_RAM_SPEND)
		"perfect":
			_scene._perfect_feedback(_scene._player_view)
		"boss_phase":
			_scene._boss_phase_feedback(_scene.engine.state())
		"phase_burst":
			# ART-0 E: the burst a boss's phase plays on its wheel (the demo fight has no boss
			# in a later phase, so it plays on the enemy's wheel as _boss_phase_feedback does).
			_scene.fx_layer.wheel_burst(ev.global_center(), ev.disc_radius(), CombatFxLayer.BURST_PHASE, Palette.CORP_SOLACE)
		"play_fx":
			var cap: Dictionary = _scene._card_copy(0)
			_scene.fx_layer.play_card(cap["copy"], cap["rect"], float(cap["rot"]), ev.global_center(), false)
		"beat_block", "beat_heal", "beat_status", "beat_hit":
			# ANIM-R5: a beat as a SEND IT plays it (the scene's own _play_beat): the operative's
			# guard, a heal, a status landing on the enemy's slice, a PERFECT hit riding to it.
			var s: CombatState = _scene.engine.state()
			var pl: StringName = s.player.id
			var b := _beat(what.trim_prefix("beat_"), pl, pl if what in ["beat_block", "beat_heal"] else enemy)
			if what == "beat_heal":
				b["hp_after"] = s.player.hp
			elif what == "beat_hit":
				b["hp_after"] = maxi(0, s.get_combatant(enemy).hp - DEMO_BEAT_AMOUNT)
				b["source_tier"] = RC.PrecisionTier.PERFECT
			# The replay's own snapshot of each wheel (a status lands on the shown slice).
			for id in [pl, enemy]:
				var view: WheelView = _scene._view_of(id)
				if view != null:
					view.shown_state = s.get_combatant(id).duplicate_state()
			_scene._play_beat(b, s, s)



## ANIM-R5: a resolve beat of `kind` from `source` to `target` with every key a SEND IT's
## beat carries (ResolveBeats), for the scene's own _play_beat.
func _beat(kind: String, source: StringName, target: StringName) -> Dictionary:
	return {"kind": "block" if kind == "block" else ("heal" if kind == "heal" else ("status" if kind == "status" else "damage")),
		"event_index": 0, "phase": "resolve", "pass": "", "source": source, "pointer_index": 0, "target": target,
		"amount": DEMO_BEAT_AMOUNT, "crit": false, "hp_after": -1, "slot": 0, "status": RC.Status.CORRUPTED, "tier": -1,
		"soaked": 0, "host": &"", "source_slot": 0, "source_tier": -1, "raw": DEMO_BEAT_AMOUNT, "blocked": 0, "shielded": 0,
		"side": "player", "wheel_source": true}


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
