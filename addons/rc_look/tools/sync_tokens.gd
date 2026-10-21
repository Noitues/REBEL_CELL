extends SceneTree
## LOOK-TOOLBOX module 1: writes the rc_look colour tokens (addons/rc_look/config/look_tokens.tres, values from
## Palette) into project.godot [shader_globals] and the generated include addons/rc_look/shaders/rc_tokens.gdshaderinc.
## Run after any Palette token or look_tokens.tres change:
##   godot --headless --path . -s addons/rc_look/tools/sync_tokens.gd            (writes)
##   godot --headless --path . -s addons/rc_look/tools/sync_tokens.gd -- --check  (exit 1 on drift, writes nothing)
## Only the [shader_globals] section is rewritten, as text (ProjectSettings.save() would drop default-valued settings
## elsewhere in the file). Other globals (e.g. `reduce_effects`) are kept as they are; rc_ globals leave with the set.

const PROJECT := "res://project.godot"
const INCLUDE_PATH := "res://addons/rc_look/shaders/rc_tokens.gdshaderinc"


func _init() -> void:
	var check := OS.get_cmdline_user_args().has("--check")
	var tokens: RcLookTokens = load(RcLookTokens.DEFAULT_PATH)
	var errs := tokens.validate()
	if not errs.is_empty():
		for e in errs:
			printerr("sync_tokens: ", e)
		quit(1)
		return
	var text := FileAccess.get_file_as_string(PROJECT)
	var new_text := RcLookTokenSync.with_globals(text, tokens.values())
	var src := tokens.include_source()
	var old_inc := FileAccess.get_file_as_string(INCLUDE_PATH) if FileAccess.file_exists(INCLUDE_PATH) else ""
	var drift := PackedStringArray()
	if new_text != text:
		drift.append("project.godot")
	if old_inc != src:
		drift.append("include")
	if check:
		print("sync_tokens: drift: [%s]" % ", ".join(drift))
		quit(0 if drift.is_empty() else 1)
		return
	if new_text != text:
		var f := FileAccess.open(PROJECT, FileAccess.WRITE)
		f.store_string(new_text)
		f.close()
	if old_inc != src:
		var g := FileAccess.open(INCLUDE_PATH, FileAccess.WRITE)
		g.store_string(src)
		g.close()
	print("sync_tokens: %d globals; wrote [%s]" % [tokens.values().size(), ", ".join(drift)])
	quit(0)
