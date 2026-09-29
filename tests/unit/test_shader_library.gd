extends GutTest
## Art pass W6 (ART_BIBLE 13, 8, 12): the shader library's conventions. Every shader in
## res://shaders includes the shared `rc_common` include and so reads the one reduce-effects
## control (the `reduce_effects` global shader uniform, registered in project.godot and set by
## Fx from Settings); a shader that animates on TIME runs it through the include's frozen
## clock or live factor; the library shaders exist with doc comments; the unused glow shader
## is gone. Headless has no renderer, so these are source checks plus Fx's side of the
## uniform; the look is verified in the windowed shader lab.

const SHADER_DIR := "res://shaders"
const INCLUDE := "res://shaders/lib/rc_common.gdshaderinc"
## ART_BIBLE 13's library (foil belongs to W4 and joins when it lands).
const LIBRARY: Array[String] = ["glass_blur", "crt_overlay", "paper_burn", "glitch_dissolve", "marker_stroke", "halftone"]

var _reduce: bool


func before_each() -> void:
	_reduce = Settings.reduce_effects


func after_each() -> void:
	if Settings.reduce_effects != _reduce:
		Settings.set_reduce_effects(_reduce)
	Fx.apply_settings()


func _shaders() -> PackedStringArray:
	var out := PackedStringArray()
	for f in DirAccess.get_files_at(SHADER_DIR):
		if f.ends_with(".gdshader"):
			out.append(SHADER_DIR.path_join(f))
	return out


func test_the_include_declares_the_one_reduce_effects_control() -> void:
	var src := FileAccess.get_file_as_string(INCLUDE)
	assert_true(src.contains("global uniform float reduce_effects;"), "a global uniform, one control for every shader")
	for fn in ["float rc_live()", "float rc_time(float t)"]:
		assert_true(src.contains(fn), "the include offers %s" % fn)
	var project := FileAccess.get_file_as_string("res://project.godot")
	assert_true(project.contains("[shader_globals]") and project.contains("reduce_effects={"), "registered in project.godot")


func test_every_shader_reads_reduce_effects_and_freezes_its_clock() -> void:
	var files := _shaders()
	assert_gt(files.size(), 10, "the library and the existing shaders")
	for path in files:
		var src := FileAccess.get_file_as_string(path)
		assert_true(src.contains("#include \"%s\"" % INCLUDE), "%s includes rc_common" % path)
		assert_true(src.begins_with("//") or src.contains("\n//"), "%s carries doc comments" % path)
		var uses_time := false
		for line in src.split("\n"):
			var code := line.split("//")[0]
			if code.contains("TIME"):
				uses_time = true
				assert_true(code.contains("rc_time(") or code.contains("rc_live()") or code.contains("live_i"),
					"%s: an animated line goes static under reduce effects (%s)" % [path, line.strip_edges()])
		if uses_time:
			assert_true(src.contains("rc_live()") or src.contains("rc_time("), "%s reads reduce_effects" % path)


func test_the_library_shaders_exist() -> void:
	for name in LIBRARY:
		var path := SHADER_DIR.path_join(name + ".gdshader")
		assert_true(FileAccess.file_exists(path), "%s exists" % path)
		var sh := load(path) as Shader
		assert_not_null(sh, "%s loads" % path)


func test_the_unused_glow_shader_is_gone() -> void:
	assert_false(FileAccess.file_exists(SHADER_DIR.path_join("glow.gdshader")))


func test_fx_sets_the_global_from_the_setting() -> void:
	Settings.set_reduce_effects(true)
	assert_eq(Fx.shader_reduce, 1.0, "reduce effects on: 1")
	Settings.set_reduce_effects(false)
	assert_eq(Fx.shader_reduce, 0.0, "off: 0")


func test_script_side_zeroing_still_holds() -> void:
	# The scripts' own zeroing stays (nothing regresses if a shader is used without the global).
	var theme := FileAccess.get_file_as_string("res://scripts/ui/kit/ui_theme.gd")
	assert_true(theme.contains("\"flicker\", 0.0 if Settings.reduce_effects"), "glass flicker zeroed script-side")
	var city := FileAccess.get_file_as_string("res://scripts/ui/kit/neon_city.gd")
	assert_true(city.contains("\"animate\", 1.0 if live else 0.0"), "city lights stopped script-side")
