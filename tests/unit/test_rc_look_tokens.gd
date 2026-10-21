extends GutTest
## LOOK-TOOLBOX module 1 (fast tier): the rc_look colour tokens never drift. Every entry of look_tokens.tres is a
## Palette colour; project.godot [shader_globals] holds exactly those values under rc_ names; the generated include
## declares exactly those globals; the sync's text edit is idempotent and leaves everything else in the file alone.

const INCLUDE := "res://addons/rc_look/shaders/rc_tokens.gdshaderinc"
const LIB := "res://addons/rc_look/shaders/rc_look.gdshaderinc"

var _tokens: RcLookTokens


func before_all() -> void:
	_tokens = load(RcLookTokens.DEFAULT_PATH)


func test_every_token_is_a_palette_colour_with_a_unique_name() -> void:
	assert_eq(_tokens.validate(), PackedStringArray(), "look_tokens.tres validates")
	assert_gt(_tokens.globals.size(), 50, "the §2 set is there")


func test_bible_section_2_tokens_are_exported() -> void:
	var v := _tokens.values()
	for n: String in ["rc_pencil_plan", "rc_pencil_threat", "rc_pencil_shadow", "rc_pencil_plan_netrun", "rc_harm",
			"rc_corp_solace", "rc_corp_meridian", "rc_heat_flagged", "rc_class_ghost", "rc_terminal_bg"]:
		assert_true(v.has(n), "%s exported" % n)
	assert_eq(v["rc_pencil_plan"], Palette.PENCIL_PLAN)
	assert_eq(v["rc_pencil_plan_netrun"], Palette.PENCIL_PLAN_NETRUN)
	assert_eq(v["rc_class_ghost"], Palette.class_accent(&"ghost"))


func test_project_shader_globals_equal_palette() -> void:
	var v := _tokens.values()
	for n: String in v:
		var g: Variant = ProjectSettings.get_setting("shader_globals/" + n, null)
		assert_true(g is Dictionary, "%s is declared in project.godot (run addons/rc_look/tools/sync_tokens.gd)" % n)
		if g is Dictionary:
			assert_eq(String((g as Dictionary).get("type", "")), "color", "%s is a color global" % n)
			assert_true(((g as Dictionary).get("value", Color()) as Color).is_equal_approx(v[n]), "%s equals Palette" % n)
	for p: Dictionary in ProjectSettings.get_property_list():
		var name := String(p["name"])
		if name.begins_with("shader_globals/" + RcLookTokens.PREFIX):
			assert_true(v.has(name.trim_prefix("shader_globals/")), "%s is in look_tokens.tres (no stale rc_ global)" % name)


func test_include_declares_exactly_the_set() -> void:
	assert_eq(FileAccess.get_file_as_string(INCLUDE), _tokens.include_source(), "rc_tokens.gdshaderinc is current")
	var lib := FileAccess.get_file_as_string(LIB)
	assert_true(lib.contains("rc_common.gdshaderinc"), "the library brings rc_common (reduce_effects)")
	assert_true(lib.contains("rc_tokens.gdshaderinc"), "the library brings the tokens")


func test_sync_text_edit_is_idempotent_and_local() -> void:
	var src := "[application]\n\nconfig/name=\"X\"\n\n[shader_globals]\n\nreduce_effects={\n\"type\": \"float\",\n\"value\": 0.0\n}\nrc_old={\n\"type\": \"color\",\n\"value\": Color(0, 0, 0, 1)\n}\n\n[rendering]\n\nfoo=1\n"
	var g := {"rc_a": Color(1, 0, 0, 1), "rc_b": Color(0, 0.5, 1, 1)}
	var once := RcLookTokenSync.with_globals(src, g)
	assert_eq(RcLookTokenSync.with_globals(once, g), once, "a second sync changes nothing")
	assert_true(once.begins_with("[application]\n\nconfig/name=\"X\"\n"), "sections before stay")
	assert_true(once.ends_with("[rendering]\n\nfoo=1\n"), "sections after stay")
	assert_true(once.contains("reduce_effects={\n\"type\": \"float\",\n\"value\": 0.0\n}"), "other globals stay")
	assert_false(once.contains("rc_old"), "stale rc_ globals leave")
	assert_true(once.contains("rc_b={\n\"type\": \"color\",\n\"value\": Color(0, 0.5, 1, 1)\n}"), "new globals in the editor's format")
	var none := RcLookTokenSync.with_globals("[application]\n\nx=1\n", g)
	assert_true(none.contains("[shader_globals]\n\nrc_a={"), "the section is added when missing")
