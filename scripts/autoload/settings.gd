extends Node
## Settings autoload: accessibility (GDD 9.6, STYLE_GUIDE 6), display, audio, key
## bindings, language and onboarding flags, persisted to user://settings.json. Views
## read these and listen to `changed`; nothing here touches game state.

signal changed
## The on-screen key hints changed: a setting changed, or the player switched between the
## keyboard/mouse and a pad (hints then name pad buttons).
signal hints_changed

const PATH := "user://settings.json"
## Where settings live this session: PATH, or under a GUT run a file of this process's own
## (deleted on exit), so test runs never read or write the player's settings and parallel
## runs never leak text scale or keybinds into each other (H24).
var path: String = PATH
const TEXT_SCALE_MIN := 0.8
## ART_BIBLE §12 (Q5): text scale runs 0.8-2.0.
const TEXT_SCALE_MAX := 2.0
enum WindowMode { WINDOWED, FULLSCREEN, BORDERLESS }
const RESOLUTIONS: Array[Vector2i] = [Vector2i(1280, 720), Vector2i(1600, 900), Vector2i(1920, 1080), Vector2i(2560, 1440)]
## Actions the player may rebind (GDD 9.5); the card keys stay 1-9. H20: cards are aimed
## by dragging or by picking a target, so toggle_card_target, toggle_direction and
## cycle_slot no longer do anything (their input-map entries stay in project.godot).
const REBINDABLE: Array[StringName] = [&"nudge_left", &"nudge_right", &"cycle_target", &"end_turn", &"rewind",
	&"toggle_ring", &"toggle_nudge_wheel", &"respin", &"open_settings"]

## Disables scanlines, flicker, chromatic aberration and the distortion pulse everywhere.
var reduce_effects: bool = false
## Never more than 3 flashes per second (on by default).
var flash_limiter: bool = true
var text_scale: float = 1.0
## Subtitles with speaker names for voiced lines (story beats, events, DISPATCH).
var subtitles: bool = true
## Subtitles and DISPATCH text type in (Animation pass ANIM-6); off shows each line whole
## at once.
var subtitle_typing: bool = true
var master_volume: float = 1.0
var music_volume: float = 0.6
var sfx_volume: float = 0.8
## Locale code ("en"); applied to the TranslationServer (GDD 10 localisation pipeline).
var language: String = "en"
var window_mode: int = WindowMode.WINDOWED
var resolution: Vector2i = Vector2i(1280, 720)
var vsync: bool = true
var show_fps: bool = false
## Map views on the city show a legend (claimed / cleared / corporate, glyphs).
var map_legend: bool = true
## The scrolling system log strip at the foot of the HQ and netrun screens (off by
## default: DISPATCH and the notes carry the story; the log is a record for players who
## want it).
var system_log: bool = false
## action name (String) -> physical keycode (int) for rebound actions.
var keybinds: Dictionary = {}
## The guided first netrun has been completed or skipped.
var tutorial_done: bool = false
## Colour-blind correction (ART_BIBLE §12, art pass W9): one of COLORBLIND_MODES. Not off
## puts a full-screen daltonize pass on top (the ColorblindFilter autoload); the patterns
## and glyphs stay the main cue.
var colorblind_mode: StringName = &"off"
const COLORBLIND_MODES: Array[StringName] = [&"off", &"deutan", &"protan", &"tritan"]
## Assist mode (GAP_ANALYSIS P2 13): new campaigns get config.assist_free_nudges extra free
## nudges a turn and config.assist_hp_multiplier operative HP; they set no ICE records and
## earn no campaign achievements.
var assist_mode: bool = false
## Controller defaults (GAP_ANALYSIS P2 11), added to every action at startup next to the
## keyboard keys (Xbox layout; Godot maps other pads onto it). ui_* navigation keeps
## Godot's own pad bindings.
const CONTROLLER_BINDS := {
	&"nudge_left": JOY_BUTTON_LEFT_SHOULDER, &"nudge_right": JOY_BUTTON_RIGHT_SHOULDER,
	&"cycle_target": JOY_BUTTON_Y, &"end_turn": JOY_BUTTON_X, &"rewind": JOY_BUTTON_BACK,
	&"inspect": JOY_BUTTON_LEFT_STICK, &"respin": JOY_BUTTON_RIGHT_STICK, &"open_settings": JOY_BUTTON_START,
}
## The triggers switch which wheel (LT) and which ring (RT) the pad's nudges drive (H21:
## the on-screen pickers are gone since cards are aimed by dragging; the nudge arrows are
## mouse targets).
const CONTROLLER_AXIS_BINDS := {&"toggle_nudge_wheel": JOY_AXIS_TRIGGER_LEFT, &"toggle_ring": JOY_AXIS_TRIGGER_RIGHT}
const PAD_AXIS_NAMES := {JOY_AXIS_TRIGGER_LEFT: "LT", JOY_AXIS_TRIGGER_RIGHT: "RT"}
## Menu and focus navigation on the pad (the D-pad moves focus, A presses, B backs out).
const UI_PAD_BINDS := {
	&"ui_accept": JOY_BUTTON_A, &"ui_cancel": JOY_BUTTON_B,
	&"ui_up": JOY_BUTTON_DPAD_UP, &"ui_down": JOY_BUTTON_DPAD_DOWN,
	&"ui_left": JOY_BUTTON_DPAD_LEFT, &"ui_right": JOY_BUTTON_DPAD_RIGHT,
}


func _ready() -> void:
	if is_test_run():
		path = TEST_PATH_FORMAT % OS.get_process_id()
		DirAccess.remove_absolute(path)
	load_settings()
	apply_keybinds()
	apply_controller_bindings()
	apply_display()


func set_reduce_effects(value: bool) -> void:
	reduce_effects = value
	_apply()


func set_flash_limiter(value: bool) -> void:
	flash_limiter = value
	_apply()


## Whether the last input came from a pad: hints then name pad buttons (H20).
var pad_active: bool = false
## Stick motion below this doesn't count as switching to the pad.
const PAD_SWITCH_DEADZONE := 0.5
## Xbox-layout button names for hints (Godot maps other pads onto this layout).
const PAD_NAMES := {
	JOY_BUTTON_A: "A", JOY_BUTTON_B: "B", JOY_BUTTON_X: "X", JOY_BUTTON_Y: "Y",
	JOY_BUTTON_LEFT_SHOULDER: "LB", JOY_BUTTON_RIGHT_SHOULDER: "RB", JOY_BUTTON_BACK: "View",
	JOY_BUTTON_START: "Menu", JOY_BUTTON_LEFT_STICK: "L3", JOY_BUTTON_RIGHT_STICK: "R3",
	JOY_BUTTON_DPAD_UP: "D-pad up", JOY_BUTTON_DPAD_DOWN: "D-pad down",
	JOY_BUTTON_DPAD_LEFT: "D-pad left", JOY_BUTTON_DPAD_RIGHT: "D-pad right",
}
## Short names for long key names in hints.
const SHORT_KEY_NAMES := {"Escape": "Esc", "Backspace": "Bksp", "Delete": "Del"}


func _input(event: InputEvent) -> void:
	observe_device(event)


## Switches the hints to the device `event` came from (a pad button or a firm stick push:
## the pad; a key or a mouse button: keys). ANIM-R3 A4: MotionSkip.consume calls it too, so
## a pad press that ends a motion (and never reaches this node) still switches the prompts.
func observe_device(event: InputEvent) -> void:
	var pad := pad_active
	if event is InputEventJoypadButton:
		pad = true
	elif event is InputEventJoypadMotion:
		if absf((event as InputEventJoypadMotion).axis_value) >= PAD_SWITCH_DEADZONE:
			pad = true
	elif event is InputEventKey or event is InputEventMouseButton:
		pad = false
	if pad != pad_active:
		set_pad_active(pad)


## Switches the hints between keyboard keys and pad buttons.
func set_pad_active(value: bool) -> void:
	if value == pad_active:
		return
	pad_active = value
	hints_changed.emit()


## The name of a physical key as the player's keyboard layout prints it (the Controls grid,
## the hints and the rebind refusals all use this, so they agree on AZERTY too).
static func key_name(physical: int) -> String:
	if physical <= 0:
		return "-"
	var code := physical
	if DisplayServer.get_name() != "headless":
		code = DisplayServer.keyboard_get_keycode_from_physical(physical)
	var name := OS.get_keycode_string(code)
	return String(SHORT_KEY_NAMES.get(name, name))


## What to press for `action` on the device in use: a pad button name when the pad is in
## use, else the bound key ("" when the action has none on that device).
func key_text(action: StringName) -> String:
	if not InputMap.has_action(action):
		return ""
	for ev in InputMap.action_get_events(action):
		if pad_active and ev is InputEventJoypadButton:
			return String(PAD_NAMES.get((ev as InputEventJoypadButton).button_index, "Pad %d" % (ev as InputEventJoypadButton).button_index))
		if pad_active and ev is InputEventJoypadMotion:
			return String(PAD_AXIS_NAMES.get((ev as InputEventJoypadMotion).axis, "Stick"))
		if not pad_active and ev is InputEventKey:
			var k := ev as InputEventKey
			return key_name(k.physical_keycode if k.physical_keycode != KEY_NONE else k.keycode)
		if not pad_active and ev is InputEventMouseButton:
			return MOUSE_NAMES.get((ev as InputEventMouseButton).button_index, "Mouse")
	return ""


## A bracketed hint for labels ("[Q]", "[LB]"), or "" when the device has no button for it.
func hint(action: StringName) -> String:
	var t := key_text(action)
	return "[%s]" % t if t != "" else ""


const MOUSE_NAMES := {MOUSE_BUTTON_LEFT: "Click", MOUSE_BUTTON_RIGHT: "Right-click", MOUSE_BUTTON_MIDDLE: "Middle-click"}


func set_text_scale(value: float) -> void:
	text_scale = clampf(value, TEXT_SCALE_MIN, TEXT_SCALE_MAX)
	_apply()


## Sets the colour-blind correction (one of COLORBLIND_MODES; anything else is ignored).
func set_colorblind_mode(value: StringName) -> void:
	if not COLORBLIND_MODES.has(value):
		return
	colorblind_mode = value
	_apply()


func set_subtitles(value: bool) -> void:
	subtitles = value
	_apply()


func set_subtitle_typing(value: bool) -> void:
	subtitle_typing = value
	_apply()


func set_master_volume(value: float) -> void:
	master_volume = clampf(value, 0.0, 1.0)
	_apply()


func set_music_volume(value: float) -> void:
	music_volume = clampf(value, 0.0, 1.0)
	_apply()


func set_sfx_volume(value: float) -> void:
	sfx_volume = clampf(value, 0.0, 1.0)
	_apply()


func set_language(code: String) -> void:
	language = code if code != "" else "en"
	TranslationServer.set_locale(language)
	_apply()


## Locales with a translation loaded, "en" first.
func available_languages() -> PackedStringArray:
	var out := PackedStringArray(["en"])
	for l in TranslationServer.get_loaded_locales():
		if not out.has(l):
			out.append(l)
	return out


func set_window_mode(mode: int) -> void:
	window_mode = clampi(mode, 0, 2)
	apply_display()
	_apply()


func set_resolution(value: Vector2i) -> void:
	resolution = value
	apply_display()
	_apply()


func set_vsync(value: bool) -> void:
	vsync = value
	apply_display()
	_apply()


func set_show_fps(value: bool) -> void:
	show_fps = value
	_apply()


func set_map_legend(value: bool) -> void:
	map_legend = value
	_apply()


func set_system_log(value: bool) -> void:
	system_log = value
	_apply()


func set_tutorial_done(value: bool) -> void:
	tutorial_done = value
	_apply()


## Rebinds `action` to a physical keycode (replacing its first key event) and remembers it.
func rebind(action: StringName, physical_keycode: int) -> void:
	if not REBINDABLE.has(action) or physical_keycode <= 0:
		return
	keybinds[String(action)] = physical_keycode
	_apply_bind(action, physical_keycode)
	_apply()


## Keys a rebind may not take: the card keys (GDD 9.5), Enter (confirm) and Esc.
const RESERVED_KEYS: Array[int] = [KEY_1, KEY_2, KEY_3, KEY_4, KEY_5, KEY_6, KEY_7, KEY_8, KEY_9,
	KEY_ENTER, KEY_KP_ENTER, KEY_ESCAPE]


## Why `physical_keycode` can't be bound to `action` ("" when it can): reserved, or
## already held by another rebindable action.
func bind_error(action: StringName, physical_keycode: int) -> String:
	if RESERVED_KEYS.has(physical_keycode):
		return "%s is reserved" % key_name(physical_keycode)
	for other in REBINDABLE:
		if other != action and key_for(other) == physical_keycode:
			return "%s is used by %s" % [key_name(physical_keycode), String(other)]
	return ""


## Restores the project's default bindings.
func reset_keybinds() -> void:
	keybinds.clear()
	for action in REBINDABLE:
		InputMap.action_erase_events(action)
		for ev in ProjectSettings.get_setting("input/%s" % action, {}).get("events", []):
			InputMap.action_add_event(action, ev)
	apply_controller_bindings()  # the reset erased the pad buttons too (H18)
	_apply()


## The physical keycode bound to `action` (0 when none).
func key_for(action: StringName) -> int:
	for ev in InputMap.action_get_events(action):
		if ev is InputEventKey:
			return (ev as InputEventKey).physical_keycode
	return 0


## Adds CONTROLLER_BINDS to the input map (once per action; keyboard binds untouched).
func apply_controller_bindings() -> void:
	# Space is End Turn (GDD 9.5): it must not also press whatever button has focus.
	for ev in InputMap.action_get_events(&"ui_accept"):
		if ev is InputEventKey and ((ev as InputEventKey).keycode == KEY_SPACE or (ev as InputEventKey).physical_keycode == KEY_SPACE):
			InputMap.action_erase_event(&"ui_accept", ev)
	# Tab is Cycle target (GDD 9.5): it must not move focus off the hand either.
	for ev in InputMap.action_get_events(&"ui_focus_next"):
		if ev is InputEventKey and ((ev as InputEventKey).keycode == KEY_TAB or (ev as InputEventKey).physical_keycode == KEY_TAB) and not (ev as InputEventKey).shift_pressed:
			InputMap.action_erase_event(&"ui_focus_next", ev)
	for binds in [CONTROLLER_BINDS, UI_PAD_BINDS]:
		for action in binds:
			if not InputMap.has_action(action):
				continue
			var has_pad := false
			for ev in InputMap.action_get_events(action):
				if ev is InputEventJoypadButton and ev.button_index == binds[action]:
					has_pad = true
			if not has_pad:
				var pad := InputEventJoypadButton.new()
				pad.button_index = binds[action]
				pad.device = -1
				InputMap.action_add_event(action, pad)
	for action in CONTROLLER_AXIS_BINDS:
		if not InputMap.has_action(action):
			continue
		var has_axis := false
		for ev in InputMap.action_get_events(action):
			if ev is InputEventJoypadMotion and (ev as InputEventJoypadMotion).axis == CONTROLLER_AXIS_BINDS[action]:
				has_axis = true
		if not has_axis:
			var motion := InputEventJoypadMotion.new()
			motion.axis = CONTROLLER_AXIS_BINDS[action]
			motion.axis_value = 1.0
			motion.device = -1
			InputMap.action_add_event(action, motion)


func set_assist_mode(value: bool) -> void:
	assist_mode = value
	save_settings()
	changed.emit()
	hints_changed.emit()


func apply_keybinds() -> void:
	for action in keybinds:
		_apply_bind(StringName(action), int(keybinds[action]))


func _apply_bind(action: StringName, physical_keycode: int) -> void:
	var kept: Array[InputEvent] = []
	for ev in InputMap.action_get_events(action):
		if not (ev is InputEventKey):
			kept.append(ev)
	InputMap.action_erase_events(action)
	var key := InputEventKey.new()
	key.physical_keycode = physical_keycode
	InputMap.action_add_event(action, key)
	for ev in kept:
		InputMap.action_add_event(action, ev)


## Applies window mode, size and vsync (no-op headless). A quiet window (tools/run_windowed.py)
## stays windowed at `resolution`, off the screen and without focus.
func apply_display() -> void:
	if DisplayServer.get_name() == "headless":
		return
	if quiet_window():
		DisplayServer.window_set_mode(DisplayServer.WINDOW_MODE_WINDOWED)
		DisplayServer.window_set_flag(DisplayServer.WINDOW_FLAG_NO_FOCUS, true)
		DisplayServer.window_set_flag(DisplayServer.WINDOW_FLAG_BORDERLESS, false)
		DisplayServer.window_set_size(resolution)
		DisplayServer.window_set_position(QUIET_WINDOW_POSITION)
		DisplayServer.window_set_vsync_mode(DisplayServer.VSYNC_ENABLED if vsync else DisplayServer.VSYNC_DISABLED)
		return
	match window_mode:
		WindowMode.FULLSCREEN:
			DisplayServer.window_set_mode(DisplayServer.WINDOW_MODE_FULLSCREEN)
		WindowMode.BORDERLESS:
			DisplayServer.window_set_mode(DisplayServer.WINDOW_MODE_WINDOWED)
			DisplayServer.window_set_flag(DisplayServer.WINDOW_FLAG_BORDERLESS, true)
			DisplayServer.window_set_size(DisplayServer.screen_get_size())
			DisplayServer.window_set_position(Vector2i.ZERO)
		_:
			DisplayServer.window_set_mode(DisplayServer.WINDOW_MODE_WINDOWED)
			DisplayServer.window_set_flag(DisplayServer.WINDOW_FLAG_BORDERLESS, false)
			DisplayServer.window_set_size(resolution)
	DisplayServer.window_set_vsync_mode(DisplayServer.VSYNC_ENABLED if vsync else DisplayServer.VSYNC_DISABLED)


func to_dict() -> Dictionary:
	return {"reduce_effects": reduce_effects, "flash_limiter": flash_limiter, "text_scale": text_scale,
		"subtitles": subtitles, "subtitle_typing": subtitle_typing, "master_volume": master_volume, "music_volume": music_volume, "sfx_volume": sfx_volume,
		"language": language, "window_mode": window_mode, "resolution": [resolution.x, resolution.y], "vsync": vsync,
		"show_fps": show_fps, "map_legend": map_legend, "system_log": system_log, "keybinds": keybinds.duplicate(), "tutorial_done": tutorial_done, "assist_mode": assist_mode,
		"colorblind_mode": String(colorblind_mode)}


func from_dict(d: Dictionary) -> void:
	reduce_effects = bool(d.get("reduce_effects", false))
	flash_limiter = bool(d.get("flash_limiter", true))
	text_scale = clampf(float(d.get("text_scale", 1.0)), TEXT_SCALE_MIN, TEXT_SCALE_MAX)
	subtitles = bool(d.get("subtitles", true))
	subtitle_typing = bool(d.get("subtitle_typing", true))
	master_volume = clampf(float(d.get("master_volume", 1.0)), 0.0, 1.0)
	music_volume = clampf(float(d.get("music_volume", 0.6)), 0.0, 1.0)
	sfx_volume = clampf(float(d.get("sfx_volume", 0.8)), 0.0, 1.0)
	language = String(d.get("language", "en"))
	TranslationServer.set_locale(language)
	window_mode = clampi(int(d.get("window_mode", 0)), 0, 2)
	var r: Array = d.get("resolution", [1280, 720])
	resolution = Vector2i(int(r[0]), int(r[1])) if r.size() == 2 else Vector2i(1280, 720)
	vsync = bool(d.get("vsync", true))
	show_fps = bool(d.get("show_fps", false))
	map_legend = bool(d.get("map_legend", true))
	system_log = bool(d.get("system_log", false))
	keybinds = {}
	for k in d.get("keybinds", {}):
		# Only actions that can still be rebound (H20 retired the card-target, direction and
		# slice toggles; a key saved for them must not stay bound twice).
		if REBINDABLE.has(StringName(String(k))):
			keybinds[String(k)] = int(d["keybinds"][k])
	tutorial_done = bool(d.get("tutorial_done", false))
	assist_mode = bool(d.get("assist_mode", false))
	# Art pass W9: additive keys; a file without them (or with an unknown value) gets the
	# default.
	colorblind_mode = _pick(d.get("colorblind_mode", ""), COLORBLIND_MODES)


## `value` as one of `allowed` (a StringName), or `allowed[0]` (the default) when it isn't.
static func _pick(value: Variant, allowed: Array[StringName]) -> StringName:
	var v := StringName(str(value))
	return v if allowed.has(v) else allowed[0]


## Whether this process runs the GUT test suite.
static func is_test_run() -> bool:
	for a in OS.get_cmdline_args():
		if a.ends_with("gut_cmdln.gd"):
			return true
	return false


## Whether this process is a quiet windowed run (tools/run_windowed.py): no focus taken, no
## sound, the window off the screen. Set by the environment or a `--quiet-window` user arg.
static func quiet_window() -> bool:
	return quiet_window_from(OS.get_cmdline_user_args(), OS.get_environment(QUIET_WINDOW_ENV))


## `quiet_window` from given user args and environment value (testable).
static func quiet_window_from(user_args: PackedStringArray, env_value: String) -> bool:
	return user_args.has(QUIET_WINDOW_ARG) or env_value == "1"


const QUIET_WINDOW_ENV := "REBEL_CELL_QUIET_WINDOW"
const QUIET_WINDOW_ARG := "--quiet-window"
## Far off every screen: Godot keeps drawing a window there (a minimized one stops).
const QUIET_WINDOW_POSITION := Vector2i(-30000, -30000)


## A test run's own settings file (by process id).
const TEST_PATH_FORMAT := "user://gut_settings_%d.json"


func _notification(what: int) -> void:
	if what == NOTIFICATION_PREDELETE and path != PATH:
		DirAccess.remove_absolute(path)


func save_settings() -> Error:
	var file := FileAccess.open(path, FileAccess.WRITE)
	if file == null:
		return FileAccess.get_open_error()
	file.store_string(JSON.stringify(to_dict(), "\t"))
	file.close()
	return OK


func load_settings() -> void:
	if not FileAccess.file_exists(path):
		return
	var parsed: Variant = JSON.parse_string(FileAccess.get_file_as_string(path))
	if parsed is Dictionary:
		from_dict(parsed)


func _apply() -> void:
	save_settings()
	changed.emit()
	hints_changed.emit()
