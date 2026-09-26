extends Node
## Settings autoload: accessibility (GDD 9.6, STYLE_GUIDE 6), display, audio, key
## bindings, language and onboarding flags, persisted to user://settings.json. Views
## read these and listen to `changed`; nothing here touches game state.

signal changed

const PATH := "user://settings.json"
const TEXT_SCALE_MIN := 0.8
const TEXT_SCALE_MAX := 1.6
enum WindowMode { WINDOWED, FULLSCREEN, BORDERLESS }
const RESOLUTIONS: Array[Vector2i] = [Vector2i(1280, 720), Vector2i(1600, 900), Vector2i(1920, 1080), Vector2i(2560, 1440)]
## Actions the player may rebind (GDD 9.5); the card keys stay 1-9.
const REBINDABLE: Array[StringName] = [&"nudge_left", &"nudge_right", &"cycle_target", &"end_turn", &"rewind",
	&"toggle_card_target", &"toggle_ring", &"toggle_nudge_wheel", &"toggle_direction", &"cycle_slot", &"respin", &"open_settings"]

## Disables scanlines, flicker, chromatic aberration and the distortion pulse everywhere.
var reduce_effects: bool = false
## Never more than 3 flashes per second (on by default).
var flash_limiter: bool = true
var text_scale: float = 1.0
## Subtitles with speaker names for voiced lines (story beats, events, DISPATCH).
var subtitles: bool = true
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
## Menu and focus navigation on the pad (the D-pad moves focus, A presses, B backs out).
## The combat pickers (ring, direction, slot, card target, nudge wheel) are on-screen
## buttons reached by focus, so they need no pad button of their own.
const UI_PAD_BINDS := {
	&"ui_accept": JOY_BUTTON_A, &"ui_cancel": JOY_BUTTON_B,
	&"ui_up": JOY_BUTTON_DPAD_UP, &"ui_down": JOY_BUTTON_DPAD_DOWN,
	&"ui_left": JOY_BUTTON_DPAD_LEFT, &"ui_right": JOY_BUTTON_DPAD_RIGHT,
}


func _ready() -> void:
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


## The keyboard key bound to `action`, for on-screen hints ("?" when it has none).
func key_text(action: StringName) -> String:
	if not InputMap.has_action(action):
		return "?"
	for ev in InputMap.action_get_events(action):
		if ev is InputEventKey:
			var k := ev as InputEventKey
			var code := k.physical_keycode if k.physical_keycode != KEY_NONE else k.keycode
			return OS.get_keycode_string(code)
	return "?"


func set_text_scale(value: float) -> void:
	text_scale = clampf(value, TEXT_SCALE_MIN, TEXT_SCALE_MAX)
	_apply()


func set_subtitles(value: bool) -> void:
	subtitles = value
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
		return "%s is reserved" % OS.get_keycode_string(physical_keycode)
	for other in REBINDABLE:
		if other != action and key_for(other) == physical_keycode:
			return "%s is used by %s" % [OS.get_keycode_string(physical_keycode), String(other)]
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


func set_assist_mode(value: bool) -> void:
	assist_mode = value
	save_settings()
	changed.emit()


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


## Applies window mode, size and vsync (no-op headless).
func apply_display() -> void:
	if DisplayServer.get_name() == "headless":
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
		"subtitles": subtitles, "master_volume": master_volume, "music_volume": music_volume, "sfx_volume": sfx_volume,
		"language": language, "window_mode": window_mode, "resolution": [resolution.x, resolution.y], "vsync": vsync,
		"show_fps": show_fps, "map_legend": map_legend, "system_log": system_log, "keybinds": keybinds.duplicate(), "tutorial_done": tutorial_done, "assist_mode": assist_mode}


func from_dict(d: Dictionary) -> void:
	reduce_effects = bool(d.get("reduce_effects", false))
	flash_limiter = bool(d.get("flash_limiter", true))
	text_scale = clampf(float(d.get("text_scale", 1.0)), TEXT_SCALE_MIN, TEXT_SCALE_MAX)
	subtitles = bool(d.get("subtitles", true))
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
		keybinds[String(k)] = int(d["keybinds"][k])
	tutorial_done = bool(d.get("tutorial_done", false))
	assist_mode = bool(d.get("assist_mode", false))


func save_settings() -> Error:
	var file := FileAccess.open(PATH, FileAccess.WRITE)
	if file == null:
		return FileAccess.get_open_error()
	file.store_string(JSON.stringify(to_dict(), "\t"))
	file.close()
	return OK


func load_settings() -> void:
	if not FileAccess.file_exists(PATH):
		return
	var parsed: Variant = JSON.parse_string(FileAccess.get_file_as_string(PATH))
	if parsed is Dictionary:
		from_dict(parsed)


func _apply() -> void:
	save_settings()
	changed.emit()
