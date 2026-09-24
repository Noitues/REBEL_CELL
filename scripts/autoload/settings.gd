extends Node
## Settings autoload: accessibility options (GDD 9.6, STYLE_GUIDE 6) persisted to
## user://settings.json. Views read these and listen to `changed`; nothing here touches
## game state.

signal changed

const PATH := "user://settings.json"
const TEXT_SCALE_MIN := 0.8
const TEXT_SCALE_MAX := 1.6

## Disables scanlines, flicker, chromatic aberration and the distortion pulse everywhere.
var reduce_effects: bool = false
## Never more than 3 flashes per second (on by default).
var flash_limiter: bool = true
var text_scale: float = 1.0
## Subtitles with speaker names for voiced lines (story beats, events, DISPATCH).
var subtitles: bool = true
var music_volume: float = 0.6
var sfx_volume: float = 0.8


func _ready() -> void:
	load_settings()


func set_reduce_effects(value: bool) -> void:
	reduce_effects = value
	_apply()


func set_flash_limiter(value: bool) -> void:
	flash_limiter = value
	_apply()


func set_text_scale(value: float) -> void:
	text_scale = clampf(value, TEXT_SCALE_MIN, TEXT_SCALE_MAX)
	_apply()


func set_subtitles(value: bool) -> void:
	subtitles = value
	_apply()


func set_music_volume(value: float) -> void:
	music_volume = clampf(value, 0.0, 1.0)
	_apply()


func set_sfx_volume(value: float) -> void:
	sfx_volume = clampf(value, 0.0, 1.0)
	_apply()


func to_dict() -> Dictionary:
	return {"reduce_effects": reduce_effects, "flash_limiter": flash_limiter, "text_scale": text_scale,
		"subtitles": subtitles, "music_volume": music_volume, "sfx_volume": sfx_volume}


func from_dict(d: Dictionary) -> void:
	reduce_effects = bool(d.get("reduce_effects", false))
	flash_limiter = bool(d.get("flash_limiter", true))
	text_scale = clampf(float(d.get("text_scale", 1.0)), TEXT_SCALE_MIN, TEXT_SCALE_MAX)
	subtitles = bool(d.get("subtitles", true))
	music_volume = clampf(float(d.get("music_volume", 0.6)), 0.0, 1.0)
	sfx_volume = clampf(float(d.get("sfx_volume", 0.8)), 0.0, 1.0)


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
