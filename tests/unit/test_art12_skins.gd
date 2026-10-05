extends GutTest
## ART-12 12s (the M12 box "Skins"): procedural palette skins on the v2 tokens. Every skin
## resolves every chrome token; a skin changes chrome token values only (semantic tokens and
## their greyscale pairings stay v2); 1A's contrast checks hold on every skin's panels; the
## Heat bands, harm / gain and the corp kits stay apart from the skin's chrome; the Options
## picker round-trips and defaults to v2; switching skins never changes game state.

const NETRUN := "res://scenes/netrun_map/netrun_scene.tscn"
const SLOT := "gut_test_art12_skins"
## OKLab distance a meaningful colour keeps from a skin's chrome accent and fills.
const MIN_DELTA_E := 0.1
## The v2 tokens that already equal the Cell's cyan edge (they mean PROTECT where drawn).
const SAME_AS_V2_EDGE: Array[StringName] = [&"PROTECT", &"DAEMON_TURN", &"RARITY_UNCOMMON", &"NET_CYAN"]

var _saved: Dictionary = {}


func before_each() -> void:
	_saved = Settings.snapshot()


func after_each() -> void:
	Settings.restore(_saved)


func _glass(skin: StringName) -> Color:
	return Palette.over(Palette.NIGHT_SKY, PaletteSkins.resolve(skin, &"TERMINAL_BG"))


## Every meaningful token (Palette.PAIRED_WITH, the wildcard rows expanded) -> its v2 value.
func _meaningful() -> Dictionary:
	var consts := (Palette as Script).get_script_constant_map()
	var out := {}
	for key in Palette.PAIRED_WITH:
		var k := String(key)
		if k.ends_with("_*"):
			var prefix := k.trim_suffix("*")
			for name in consts:
				if String(name).begins_with(prefix) and consts[name] is Color:
					out[StringName(name)] = consts[name]
		elif consts.has(key) and consts[key] is Color:
			out[key] = consts[key]
	return out


func test_v2_is_the_default_and_first() -> void:
	assert_eq(PaletteSkins.IDS[0], &"v2", "the default v2 skin first")
	assert_eq(PaletteSkins.DEFAULT, &"v2")
	assert_eq(Settings.PALETTE_SKINS, PaletteSkins.IDS, "Settings offers every skin")
	assert_eq(PaletteSkins.WORDS.size(), PaletteSkins.IDS.size(), "one picker word per skin")
	assert_eq(PaletteSkins.RECIPES.size(), PaletteSkins.IDS.size(), "one recipe per skin")
	assert_gt(PaletteSkins.IDS.size(), 2, "a small set beside v2")
	var fresh: Node = load("res://scripts/autoload/settings.gd").new()
	assert_eq(fresh.palette_skin, &"v2", "a new player starts on v2")
	fresh.free()


func test_every_skin_resolves_every_token() -> void:
	for skin in PaletteSkins.IDS:
		for token in PaletteSkins.TOKENS:
			var v2 := PaletteSkins.v2_value(token)
			assert_ne(v2, Palette.AUTO, "%s is a Palette token" % token)
			var c := PaletteSkins.resolve(skin, token)
			assert_almost_eq(c.a, v2.a, 0.001, "%s %s keeps the token's alpha" % [skin, token])
			for ch in [c.r, c.g, c.b]:
				assert_true(ch >= 0.0 and ch <= 1.0, "%s %s is a real colour" % [skin, token])
			if skin == PaletteSkins.DEFAULT:
				assert_eq(c, v2, "v2 %s is the bible's value" % token)
	assert_eq(PaletteSkins.resolve(&"nope", &"TERMINAL_BG"), Palette.TERMINAL_BG, "an unknown skin is v2")
	assert_eq(PaletteSkins.resolve(&"cobalt", &"HARM"), Palette.HARM, "a token outside the skin keeps v2")
	for skin in PaletteSkins.IDS.slice(1):
		assert_ne(PaletteSkins.resolve(skin, &"TERMINAL_EDGE"), Palette.TERMINAL_EDGE, "%s re-values the edge" % skin)
		# A skin value never lands on another chrome token's v2 value (re-skinning is a no-op).
		for token in PaletteSkins.TOKENS:
			var c := PaletteSkins.resolve(skin, token)
			assert_eq(PaletteSkins.chrome(c, skin), c, "%s %s is not re-mapped twice" % [skin, token])


func test_a_skin_changes_chrome_only_and_keeps_every_pairing() -> void:
	var meaningful := _meaningful()
	assert_gt(meaningful.size(), 30, "the paired tokens are found")
	for token in PaletteSkins.TOKENS:
		# SELECTED is the one paired chrome token: its pair is the ON / selected word, kept.
		if token != &"SELECTED":
			assert_false(Palette.PAIRED_WITH.has(token), "%s carries no meaning of its own" % token)
	for skin in PaletteSkins.IDS:
		for token in meaningful:
			if token in PaletteSkins.TOKENS:
				continue
			assert_eq(PaletteSkins.resolve(skin, token), meaningful[token], "%s keeps %s at v2" % [skin, token])
		# The pairing list itself is untouched by a skin (a constant): every entry still names its cue.
		for key in Palette.PAIRED_WITH:
			assert_gt(String(Palette.PAIRED_WITH[key]).length(), 4, "%s still names its pair" % key)
		# Colours that are not chrome pass through a skin as they are (a corp edge, a Heat word).
		for c: Color in [Palette.HARM, Palette.GAIN, Palette.HEAT_FLAGGED, Palette.CORP_HALCYON, Palette.FOCUS, Palette.STICKER_COMMIT]:
			assert_eq(PaletteSkins.chrome(c, skin), c, "%s leaves %s alone" % [skin, c.to_html(false)])


func test_every_skin_passes_the_1a_contrast_checks() -> void:
	for skin in PaletteSkins.IDS:
		var r := func(t: StringName) -> Color: return PaletteSkins.resolve(skin, t)
		var glass := _glass(skin)
		var hot := Palette.over(Palette.NIGHT_SKY, r.call(&"TERMINAL_BG_HOT"))
		assert_gt(Palette.contrast(r.call(&"TEXT_HI"), glass), 9.0, "%s TEXT_HI on glass" % skin)
		assert_gt(Palette.contrast(r.call(&"TERMINAL_TEXT"), glass), 9.0, "%s TERMINAL_TEXT on glass" % skin)
		assert_gt(Palette.contrast(Color(r.call(&"TERMINAL_EDGE"), 1.0), glass), 9.0, "%s edge colour on glass" % skin)
		assert_gt(Palette.contrast(r.call(&"TEXT_MID"), glass), 4.5, "%s TEXT_MID on glass" % skin)
		assert_gt(Palette.contrast(r.call(&"TEXT_LO"), glass), 4.5, "%s TEXT_LO (disabled words) on glass" % skin)
		assert_gt(Palette.contrast(r.call(&"TEXT_HI"), hot), 7.0, "%s TEXT_HI on hover glass" % skin)
		assert_gt(Palette.contrast(Palette.FOCUS, glass), 7.0, "%s focus lime on glass" % skin)
		assert_gt(Palette.contrast(r.call(&"ON_SELECTED"), r.call(&"SELECTED")), 7.0, "%s words on the selected fill" % skin)
		for c: Color in Palette.HEAT_BAND_COLORS + [Palette.HARM, Palette.GAIN, Palette.WARN]:
			assert_gt(Palette.contrast(c, glass), 4.5, "%s: %s reads on the panel" % [skin, c.to_html(false)])


func test_every_skin_theme_text_reads_on_its_own_boxes() -> void:
	for skin in PaletteSkins.IDS:
		Settings.palette_skin = skin
		var t := UiTheme.build(1.0)
		var night := Palette.NIGHT_SKY
		for pair in [[&"Button", &"normal", &"font_color", 7.0], [&"Button", &"hover", &"font_hover_color", 7.0],
				[&"Button", &"pressed", &"font_pressed_color", 7.0], [&"Button", &"disabled", &"font_disabled_color", 4.5],
				[UiTheme.TERMINAL_BUTTON, &"pressed", &"font_pressed_color", 7.0], [&"HotButton", &"normal", &"font_color", 4.5],
				[&"MenuItem", &"pressed", &"font_pressed_color", 7.0], [&"TooltipLabel", &"", &"font_color", 7.0]]:
			var bg := night
			if pair[1] != &"":
				bg = Palette.over(night, (t.get_stylebox(pair[1], pair[0]) as StyleBoxFlat).bg_color)
			else:
				bg = Palette.over(night, (t.get_stylebox(&"panel", &"TooltipPanel") as StyleBoxFlat).bg_color)
			assert_gt(Palette.contrast(t.get_color(pair[2], pair[0]), bg), float(pair[3]), "%s: %s %s words on their box" % [skin, pair[0], pair[1]])
		var tab := t.get_stylebox(&"tab_selected", &"TabBar") as StyleBoxFlat
		assert_gt(Palette.contrast(t.get_color(&"font_selected_color", &"TabBar"), tab.bg_color), 7.0, "%s the selected tab" % skin)
		var panel := t.get_stylebox(&"panel", &"PanelContainer") as StyleBoxFlat
		if panel != null:
			assert_eq(Color(panel.bg_color, 1.0), Color(PaletteSkins.resolve(skin, &"TERMINAL_BG"), 1.0), "%s panels take its glass" % skin)
		# The kit's own terminal boxes follow the skin; a corp edge stays the corp's.
		var tb := UiTheme.terminal_box()
		assert_eq(Color(tb.border_color, 1.0), Color(PaletteSkins.resolve(skin, &"TERMINAL_EDGE"), 1.0), "%s terminal edge" % skin)
		assert_eq(UiTheme.terminal_box(Palette.CORP_MERIDIAN).border_color, Palette.CORP_MERIDIAN, "%s keeps a corp edge" % skin)
		# Focus, the stickers and disabled vinyl keep their v2 look.
		assert_eq((t.get_stylebox(&"normal", &"HotButton") as StyleBoxFlat).bg_color, Palette.STICKER_COMMIT, "%s pink verb" % skin)
		assert_eq(t.get_color(&"font_focus_color", &"Button"), Palette.FOCUS, "%s lime focus" % skin)


func test_heat_harm_gain_and_corps_stay_apart_from_every_skin() -> void:
	var keep := [Palette.HARM, Palette.GAIN, Palette.HEAT_NOTICED, Palette.HEAT_FLAGGED, Palette.HEAT_HUNTED,
		Palette.FOCUS, Palette.STICKER_COMMIT, Palette.STICKER_SAFE, Palette.CORP_MERIDIAN, Palette.CORP_SOLACE,
		Palette.CORP_HALCYON, Palette.CORP_REBEL_CELL, Palette.CORP_MERIDIAN_2, Palette.CORP_SOLACE_2, Palette.CORP_HALCYON_2]
	for skin in PaletteSkins.IDS:
		var accent := Color(PaletteSkins.resolve(skin, &"TERMINAL_EDGE"), 1.0)
		var fill := PaletteSkins.resolve(skin, &"SELECTED")
		for c: Color in keep:
			assert_gt(PaletteSkins.delta_e(accent, c), MIN_DELTA_E, "%s edge vs %s" % [skin, c.to_html(false)])
			assert_gt(PaletteSkins.delta_e(fill, c), MIN_DELTA_E, "%s selected fill vs %s" % [skin, c.to_html(false)])
		# Bands, harm / gain and the corps among themselves are untouched constants: the same
		# distances as v2 on every skin, and their order of brightness on the panel holds.
		var glass := _glass(skin)
		var bands: Array[Color] = [Palette.HEAT_NOTICED, Palette.HEAT_FLAGGED, Palette.HEAT_HUNTED]
		for i in bands.size() - 1:
			assert_gt(PaletteSkins.delta_e(bands[i], bands[i + 1]), 0.05, "%s band %d vs %d" % [skin, i, i + 1])
		assert_gt(PaletteSkins.delta_e(Palette.HARM, Palette.GAIN), MIN_DELTA_E, "harm vs gain")
		assert_gt(Palette.contrast(Palette.HEAT_COOL, glass), 4.5, "%s COOL word reads" % skin)
	for skin in PaletteSkins.IDS.slice(1):
		# The skins are distinct from each other and from v2.
		for other in PaletteSkins.IDS:
			if other != skin:
				assert_gt(PaletteSkins.delta_e(PaletteSkins.resolve(skin, &"TERMINAL_EDGE"), PaletteSkins.resolve(other, &"TERMINAL_EDGE")),
					MIN_DELTA_E, "%s edge vs %s edge" % [skin, other])
	for token in SAME_AS_V2_EDGE:
		for skin in PaletteSkins.IDS:
			assert_eq(PaletteSkins.resolve(skin, token), PaletteSkins.v2_value(token), "%s keeps %s (PROTECT cyan)" % [skin, token])


func test_the_picker_round_trips_and_defaults_to_v2() -> void:
	var panel: SettingsPanel = add_child_autofree(SettingsPanel.new())
	panel.show_section("Display")
	var option := panel.find_child("SkinOption", true, false) as OptionButton
	assert_not_null(option, "Options > Display has the skin row")
	assert_eq(option.item_count, PaletteSkins.IDS.size(), "one entry per skin")
	assert_true(panel.skin_option.is_inside_tree(), "the row is shown in Display")
	for i in PaletteSkins.IDS.size():
		option.select(i)
		option.item_selected.emit(i)
		assert_eq(Settings.palette_skin, PaletteSkins.IDS[i], "picking %d sets the skin" % i)
		var d := Settings.to_dict()
		assert_eq(d["palette_skin"], String(PaletteSkins.IDS[i]), "saved")
		var back: Node = load("res://scripts/autoload/settings.gd").new()
		back.from_dict(JSON.parse_string(JSON.stringify(d)))
		assert_eq(back.palette_skin, PaletteSkins.IDS[i], "the saved file loads the same skin")
		back.free()
	var old: Node = load("res://scripts/autoload/settings.gd").new()
	old.from_dict({"text_scale": 1.0})
	assert_eq(old.palette_skin, &"v2", "an old file without the key is v2")
	old.from_dict({"palette_skin": "chartreuse"})
	assert_eq(old.palette_skin, &"v2", "an unknown skin is v2")
	old.free()
	Settings.set_palette_skin(&"chartreuse")
	assert_eq(Settings.palette_skin, PaletteSkins.IDS[-1], "an unknown id is ignored")
	assert_true(Settings.snapshot().has("palette_skin"), "tests restore the skin (suite guard)")
	var csv := FileAccess.get_file_as_string("res://assets/text/strings.csv")
	for word in PaletteSkins.WORDS + [SettingsPanel.SKIN_HEADING]:
		assert_true(csv.contains(word), "strings.csv has '%s'" % word)


func test_a_live_theme_follows_the_skin_and_restore_puts_v2_back() -> void:
	var root: Control = add_child_autofree(Control.new())
	UiTheme.apply(root)
	Settings.set_palette_skin(&"cobalt")
	var sb := root.theme.get_stylebox(&"normal", &"Button") as StyleBoxFlat
	assert_eq(Color(sb.border_color, 1.0), Color(PaletteSkins.resolve(&"cobalt", &"TERMINAL_EDGE"), 1.0), "the theme rebuilt in cobalt")
	Settings.restore(_saved)
	sb = root.theme.get_stylebox(&"normal", &"Button") as StyleBoxFlat
	assert_eq(Color(sb.border_color, 1.0), Color(Palette.TERMINAL_EDGE, 1.0), "restore puts v2 back")


func test_switching_skins_never_changes_game_state() -> void:
	AudioDirector.muted = true
	RunManager.save_slot = SLOT
	RunManager.scene_switching_enabled = false
	RunManager.delete_save()
	RunManager.reset()
	var holder: Control = add_child_autofree(Control.new())
	holder.size = Vector2(1280, 720)
	var scene: Control = load(NETRUN).instantiate()
	holder.add_child(scene)
	scene.new_campaign(1)
	scene.start_run(1)
	await get_tree().process_frame
	var state := func() -> Array:
		return [RunManager.campaign.to_dict(), RunManager.netrun.run.to_dict(), RngService.to_dict()]
	var before: Array = state.call()
	for skin in PaletteSkins.IDS + [PaletteSkins.DEFAULT]:
		Settings.set_palette_skin(skin)
		await get_tree().process_frame
		assert_eq(state.call(), before, "%s: campaign, run and RNG untouched" % skin)
	for path in ["res://scripts/ui/kit/palette_skins.gd"]:
		var src := FileAccess.get_file_as_string(path)
		for banned in ["RunManager", "RngService", "SaveService", "randi(", "randf(", "randomize("]:
			assert_false(src.contains(banned), "%s never uses %s" % [path, banned])
	holder.queue_free()
	await get_tree().process_frame
	AudioDirector.muted = false
	RunManager.delete_save()
	DirAccess.remove_absolute(RunManager.profile_path())
	RunManager.save_slot = RunManager.DEFAULT_SLOT
	RunManager.reset()
	RunManager.scene_switching_enabled = true
