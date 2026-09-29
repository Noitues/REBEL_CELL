extends GutTest
## H24 city: the Grid at big text keeps room for its map (K1: the key folds to a line, the
## steps go icon-only, labels stay under the top bar and within reach); the step row stays
## in the column in a long language (K2); the doc says the code's GRID_FITS_MAX (K3); run
## rows say what clearing gives and risks and light their node (K4); no two map kinds
## share an icon, and the key draws the map's icons (K5); Grid icons never overlap (K6);
## map words are translated once (K7); mini-map labels keep off the Site blocks (K8).
## The K1/K6 Grid sweep runs in test_city_map_sweeps.gd (Test suite optimization,
## docs/TEST_SUITE.md).

const HQ := "res://scenes/hq/hq_scene.tscn"
const CORPS: Array[StringName] = [&"solace", &"meridian", &"halcyon", &"orbital", &"rebel_cell"]
const SCALES: Array[float] = [1.0, 1.3, 1.6]
const SCREEN := Rect2(0, 0, 1280, 720)
const MINI_SIZE := Vector2(420, 170)
const SETTLE := 12
## Runs completed for the "late" Grid state.
const LATE_RUNS := 6
const PSEUDO_SETTINGS := ["replace_with_accents", "double_vowels", "fake_bidi", "override"]

var _text_scale_before: float = 1.0
var _legend_before: bool = true
var _pseudo_before: bool = false
var _pseudo_settings_before: Dictionary = {}


func before_all() -> void:
	_text_scale_before = Settings.text_scale
	_legend_before = Settings.map_legend
	_pseudo_before = TranslationServer.pseudolocalization_enabled
	for k in PSEUDO_SETTINGS:
		_pseudo_settings_before[k] = ProjectSettings.get_setting("internationalization/pseudolocalization/" + k)


func before_each() -> void:
	AudioDirector.muted = true
	RunManager.save_slot = "gut_c24_city"
	RunManager.scene_switching_enabled = false
	RunManager.delete_save()
	RunManager.reset()


func after_each() -> void:
	_pseudo(false)
	if not is_equal_approx(Settings.text_scale, _text_scale_before):
		Settings.set_text_scale(_text_scale_before)
	if Settings.map_legend != _legend_before:
		Settings.set_map_legend(_legend_before)
	Dialogue.clear()
	AudioDirector.muted = false
	RunManager.delete_save()
	DirAccess.remove_absolute(RunManager.profile_path())
	RunManager.save_slot = RunManager.DEFAULT_SLOT
	RunManager.reset()
	RunManager.scene_switching_enabled = true


func after_all() -> void:
	for k in PSEUDO_SETTINGS:
		ProjectSettings.set_setting("internationalization/pseudolocalization/" + k, _pseudo_settings_before[k])
	TranslationServer.pseudolocalization_enabled = _pseudo_before
	TranslationServer.reload_pseudolocalization()


## Pseudolocalisation as the scrambled storyboard runs it (on), or as it was (off).
func _pseudo(on: bool) -> void:
	if on:
		for k in PSEUDO_SETTINGS:
			ProjectSettings.set_setting("internationalization/pseudolocalization/" + k, true)
		TranslationServer.pseudolocalization_enabled = true
		TranslationServer.reload_pseudolocalization()
	elif TranslationServer.pseudolocalization_enabled != _pseudo_before or _pseudo_settings_changed():
		for k in PSEUDO_SETTINGS:
			ProjectSettings.set_setting("internationalization/pseudolocalization/" + k, _pseudo_settings_before[k])
		TranslationServer.pseudolocalization_enabled = _pseudo_before
		TranslationServer.reload_pseudolocalization()


func _pseudo_settings_changed() -> bool:
	for k in PSEUDO_SETTINGS:
		if ProjectSettings.get_setting("internationalization/pseudolocalization/" + k) != _pseudo_settings_before[k]:
			return true
	return false


func _frames(n: int = 3) -> void:
	for i in n:
		await get_tree().process_frame


func _scene(path: String) -> Control:
	var holder: Control = add_child_autofree(Control.new())
	holder.size = SCREEN.size
	var scene: Control = load(path).instantiate()
	holder.add_child(scene)
	scene.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	return scene


func _open_all() -> void:
	for u in [&"unlock_halcyon", &"unlock_meridian", &"unlock_orbital"]:
		RunManager.profile.add_unlock(u)
	for id in ["solace", "meridian", "halcyon", "orbital"]:
		RunManager.profile.best_ice_by_corp[id] = 10


## Completes the first `n` runs open now (in id order), as the real rules do.
func _advance(n: int) -> void:
	for i in n:
		var open := RunManager.launchable_sites().filter(func(s: SiteData) -> bool: return s.objective != RC.SiteObjective.BOSS)
		if open.is_empty():
			return
		var run := RunState.new()
		run.site_id = open[0].id
		run.kind = CampaignRules.run_kind_for(RunManager.campaign, open[0])
		CampaignRules.on_run_completed(RunManager.campaign, RunManager.corporation, RunManager.config(), run, RunManager.lookup())


## The HQ on `corp`'s Grid at `scale` (`late`: some runs done), settled.
func _hq_grid(corp: StringName, scale: float, late: bool = false) -> Control:
	RunManager.reset()
	Settings.set_text_scale(scale)
	var hq := _scene(HQ)
	_open_all()
	hq.new_campaign(1, 0, RunManager.DEFAULT_HOME, RunManager.DEFAULT_CLASS, corp)
	if late:
		_advance(LATE_RUNS)
	hq.selected_site = &""
	hq.show_grid()
	await _frames(SETTLE)
	return hq


func _close(hq: Control) -> void:
	hq.get_parent().queue_free()
	await _frames(1)


# --- K1 / K6: the Grid at 1.0, 1.3 and 1.6, early and late, every corporation ----------------

# (The K1 / K6 sweep itself: test_city_map_sweeps.gd.)


func test_the_folded_key_opens_on_hover_press_and_pad_and_does_not_refit() -> void:
	Settings.set_map_legend(true)
	var hq: Control = await _hq_grid(&"solace", 1.6)
	var legend: MapLegend = hq.grid_legend
	assert_true(legend.is_folded())
	var zoom: float = hq.city_overlay.city.scale.x
	var folded := legend.size
	legend.fold_button.mouse_entered.emit()
	await _frames(4)
	assert_true(legend.opened, "pointing at MAP KEY opens it")
	assert_gt(legend.size.y, folded.y, "its rows show")
	assert_true(SCREEN.encloses(legend.get_global_rect()), "open, it stays on screen")
	assert_almost_eq(hq.city_overlay.city.scale.x, zoom, 0.0001, "opening it never reframes the map")
	legend.notification(Control.NOTIFICATION_MOUSE_EXIT)
	await _frames(2)
	assert_false(legend.opened, "leaving it folds it")
	legend.fold_button.pressed.emit()
	assert_true(legend.opened, "pressing it opens it")
	legend.fold_button.pressed.emit()
	assert_false(legend.opened, "and folds it")
	var ev := InputEventAction.new()
	ev.action = &"cycle_target"
	ev.pressed = true
	hq._unhandled_input(ev)
	assert_true(legend.opened, "the pad's key button opens it")
	hq._unhandled_input(ev)
	assert_false(legend.opened, "and folds it")
	Settings.set_pad_active(true)
	await _frames(2)
	hq.show_grid()
	await _frames(2)
	assert_string_contains(" | ".join((hq.pad_prompts as PadPrompts).texts()), "Key", "the pad prompt names the key button")
	Settings.set_pad_active(false)
	await _close(hq)


# --- K2 a long language ------------------------------------------------------------------------

func test_the_step_row_stays_in_the_column_pseudolocalised() -> void:
	for scale in [1.0, 1.6]:
		RunManager.reset()
		Settings.set_text_scale(scale)
		var hq := _scene(HQ)
		hq.new_campaign(1)
		CampaignRules.queue_raid(RunManager.campaign, RunManager.corporation, RC.RaidTriggerSource.STORY, &"", "test")
		_pseudo(true)
		hq.show_grid()
		await _frames(4)
		var card := (hq.find_child("SelectedSite", true, false) as Control).get_global_rect()
		var nav := hq.find_child("SiteNav", true, false) as Control
		var steps := 0
		for b in nav.get_children():
			if b is Button and (b as Control).visible:
				steps += 1
				var r := (b as Control).get_global_rect()
				assert_true(r.end.x <= card.end.x + 0.5 and r.position.x >= card.position.x - 0.5,
					"x%.1f: %s inside the column (%s vs %s)" % [scale, b.name, r, card])
		assert_eq(steps, 4 if not RunManager.campaign.pending_raids.is_empty() else 3, "x%.1f: every step shows" % scale)
		_pseudo(false)
		await _close(hq)


# --- K3 the doc says the code's number -----------------------------------------------------------

func test_the_decision_log_gives_the_grid_fit_passes_the_code_uses() -> void:
	var text := FileAccess.get_file_as_string("res://docs/DECISIONS.md")
	var hq_script: GDScript = load("res://scripts/ui/hq_scene.gd")
	var n := int(hq_script.get_script_constant_map()["GRID_FITS_MAX"])
	assert_string_contains(text, "GRID_FITS_MAX (%d)" % n, "DECISIONS names GRID_FITS_MAX as the code has it")
	assert_false(text.contains("GRID_FITS_MAX (%d)" % (n - 1)), "and never the old number")


# --- K4 run rows --------------------------------------------------------------------------------

func test_the_clear_preview_is_the_real_result() -> void:
	for corp in CORPS:
		RunManager.reset()
		_open_all()
		RunManager.new_campaign(1, corp)
		for late in [false, true]:
			if late:
				_advance(LATE_RUNS)
			var c := RunManager.campaign
			for s in RunManager.launchable_sites():
				var p := CampaignRules.clear_preview(c, RunManager.corporation, RunManager.config(), s, RunManager.lookup())
				var copy := c.duplicate_state()
				var before := copy.state_hash()
				assert_eq(c.state_hash(), before, "%s %s: the preview changes nothing" % [corp, s.id])
				var run := RunState.new()
				run.site_id = s.id
				run.kind = CampaignRules.run_kind_for(c, s)
				run.patrol = run.kind == "patrol"
				if run.patrol:
					run.kind = "netrun"
				CampaignRules.on_run_completed(copy, RunManager.corporation, RunManager.config(), run, RunManager.lookup())
				var what := "%s %s %s" % [corp, s.id, "late" if late else "early"]
				assert_eq(int(p["heat"]), copy.heat - c.heat, "%s: Heat as previewed" % what)
				assert_eq(int(p["exploit"]) >= 0, copy.exploits.size() > c.exploits.size(), "%s: Exploit as previewed" % what)
				assert_eq(bool(p["raid"]), copy.pending_raids.size() > c.pending_raids.size(), "%s: raid as previewed" % what)
				assert_eq(int(p["schematics"]), copy.schematics - c.schematics, "%s: Schematics as previewed" % what)
				for id in p["opens"]:
					assert_true(CampaignRules.launchable_sites(copy, RunManager.corporation, RunManager.config()).any(func(x: SiteData) -> bool: return x.id == id),
						"%s: %s opens" % [what, id])


func test_run_rows_say_what_clearing_gives_and_light_their_node() -> void:
	var hq: Control = await _hq_grid(&"solace", 1.0)
	var rows := hq.find_child("RunRows", true, false) as VBoxContainer
	var sets := {}
	var buttons: Array[Button] = []
	for b in rows.get_children():
		if not (b is Button and String(b.name).begins_with("Run_")):
			continue
		buttons.append(b)
		var id := StringName(String(b.name).trim_prefix("Run_"))
		var gains := rows.get_node_or_null("Gains_%s" % id) as Control
		assert_not_null(gains, "%s: its gains under it" % id)
		var icons := PackedStringArray()
		for g in gains.get_children():
			if g.name == &"GainsCaption":
				# ANIM-R5 P8: the row opens with its caption (IF CLEARED:), then the badges.
				assert_eq(gains.get_child(0), g, "%s: the caption comes first" % id)
				continue
			assert_true(g is Badge, "%s: gains are badges" % id)
			assert_ne((g as Badge).icon_kind, &"", "%s: each gain has its icon" % id)
			assert_ne((g as Badge).tooltip_text, "", "%s: and says it in words" % id)
			icons.append("%s %s" % [(g as Badge).icon_kind, (g as Badge).text])
			assert_string_contains((b as Button).tooltip_text.replace("\n", " "), (g as Badge).tooltip_text.replace("\n", " ").left(20), "%s: the row's tip says it too" % id)
		assert_false(icons.is_empty(), "%s: something to say" % id)
		sets[" ".join(icons)] = true
	assert_gt(buttons.size(), 3)
	assert_gt(sets.size(), 1, "the rows no longer all look the same: %s" % [sets.keys()])
	# A row hovered or focused lights its node; the node hovered lights its row.
	var overlay: CityMapOverlay = hq.city_overlay
	var b0 := buttons[1]
	var id0 := StringName(String(b0.name).trim_prefix("Run_"))
	b0.mouse_entered.emit()
	assert_eq(overlay.hover_id, id0, "hovering a row lights its node")
	assert_ne(overlay.hover_centre().x, INF, "with a ring round its icon")
	assert_true(overlay.label_rects().has(String(id0)), "and its label")
	b0.mouse_exited.emit()
	assert_eq(overlay.hover_id, &"", "leaving it unlights it")
	b0.focus_entered.emit()
	assert_eq(overlay.hover_id, id0, "the pad's focus lights it too")
	b0.focus_exited.emit()
	var n := overlay._node_dict(id0)
	var at := overlay.icon_pos(n)
	var ev := InputEventMouseMotion.new()
	ev.position = at
	overlay._gui_input(ev)
	assert_true(bool(b0.get_meta(&"lit", false)), "pointing at the node lights its row")
	assert_false(bool(buttons[0].get_meta(&"lit", false)), "and no other")
	overlay.notification(Control.NOTIFICATION_MOUSE_EXIT)
	assert_false(bool(b0.get_meta(&"lit", false)), "leaving the map unlights it")
	await _close(hq)


# --- K5 icons -----------------------------------------------------------------------------------

func test_no_two_kinds_share_an_icon_and_the_keys_draw_the_map_icons() -> void:
	Settings.set_text_scale(1.0)  # the strip key shows its rows (it folds at big text)
	var kinds: Array = CityMapOverlay.KIND_SHAPES.keys()
	var ids := {}
	var shapes := {}
	for kind in kinds:
		ids[CityMapOverlay.icon_id(kind)] = kind
		shapes[str(CityMapOverlay.icon_shape(kind, Vector2.ZERO, 10.0))] = kind
	assert_eq(ids.size(), kinds.size(), "no two kinds share an icon id: %s" % [ids])
	assert_eq(shapes.size(), kinds.size(), "no two kinds share a silhouette")
	# The heat reduction Site is not ICE's snowflake, the shop not the Exploit's diamond.
	assert_ne(CityMapOverlay.KIND_SYMBOLS[CityMapOverlay.KIND_HEAT], String(StatIcon.ICE))
	assert_eq(CityMapOverlay.KIND_SYMBOLS[CityMapOverlay.KIND_HEAT], String(StatIcon.COOLING))
	assert_ne(CityMapOverlay.KIND_SHAPES[CityMapOverlay.KIND_SHOP], CityMapOverlay.KIND_SHAPES[CityMapOverlay.KIND_EXPLOIT])
	assert_ne(CityMapOverlay.KIND_SYMBOLS[CityMapOverlay.KIND_SHOP], CityMapOverlay.KIND_SYMBOLS[CityMapOverlay.KIND_EXPLOIT])
	assert_eq(CityMapOverlay.KIND_SYMBOLS[CityMapOverlay.KIND_EXPLOIT], String(StatIcon.EXPLOITS), "the Exploit's map icon is the top bar's")
	for k in [StatIcon.COOLING, StatIcon.CLAIM, StatIcon.LINKS]:
		assert_true(StatIcon.ALL.has(k), "%s is a StatIcon" % k)
	# The keys: each icon row names and draws the map's icon.
	RunManager.new_campaign(1)
	var grid_kinds := [CityMapOverlay.KIND_EXPLOIT, CityMapOverlay.KIND_HEAT, CityMapOverlay.KIND_BOSS, CityMapOverlay.KIND_HOME, CityMapOverlay.KIND_TIER]
	for strip in [false, true]:
		var legend: MapLegend = add_child_autofree(MapLegend.new(&"solace", strip, strip))
		await _frames(4)
		for kind in grid_kinds:
			var row := legend.body.find_child("Icon_%s" % kind, true, false) as Control
			assert_not_null(row, "key row for %s" % kind)
			assert_eq(String(row.get_meta(&"icon_id", "")), CityMapOverlay.icon_id(kind), "%s: the row names its icon" % kind)
			var swatch := row.get_node("Swatch") as Control
			assert_eq(String(swatch.get_meta(&"icon_id", "")), CityMapOverlay.icon_id(kind), "%s: the row draws the map's icon" % kind)
	var route: RouteLegend = add_child_autofree(RouteLegend.new(RouteLegend.ORDER))
	await _frames(4)
	for kind in RouteLegend.ORDER:
		var sw := route.body.get_node("Kind_%s/Swatch" % kind) as Control
		assert_eq(String(sw.get_meta(&"icon_id", "")), CityMapOverlay.icon_id(kind), "route key %s draws the map's icon" % kind)
	# The mini-map floats the map's icons over objective Sites and CORE.
	var mini: GridMapView = add_child_autofree(GridMapView.new())
	mini.size = MINI_SIZE
	mini.show_grid(RunManager.campaign, RunManager.corporation)
	await _frames(2)
	assert_false(mini.drawn_icons.is_empty())
	for id in mini.drawn_icons:
		var sd := CampaignRules.site_data(RunManager.corporation, id)
		assert_eq(mini.drawn_icons[id], CityLayout.site_kind(RunManager.campaign, sd), "%s: the mini-map shows its kind's icon" % id)
	# One name per concept: the map's words use the combat words, never SHD / shield.
	var words := PackedStringArray()
	for v in CityLayout.KIND_TIPS.values() + CityLayout.STATUS_TIPS.values() + MapLegend.STRIP_ROWS + MapLegend.STRIP_ICON_ROWS + RouteLegend.MEANINGS.values():
		words.append(String(v))
	for bad in ["SHD", "shield", "Shield", "SHIELD"]:
		assert_false(" ".join(words).contains(bad), "no '%s' on the map screens" % bad)
	assert_false(String(CityLayout.KIND_TIPS[CityMapOverlay.KIND_HEAT]).contains("snowflake"), "the tip names the new icon")


# --- K7 translated once --------------------------------------------------------------------------

func test_map_words_are_translated_once() -> void:
	_pseudo(true)
	var core := CityMapOverlay.tr_word(CityLayout.HOME_LABEL)
	assert_ne(core, CityLayout.HOME_LABEL, "pseudolocalisation is on")
	RunManager.new_campaign(1)
	var c := RunManager.campaign
	var g := CityLayout.grid_graph(c, RunManager.corporation, [])
	for n in g["nodes"]:
		if n["id"] == c.grid.home_site_id:
			assert_eq(n["label"], core, "CORE translated on the map")
		elif n["kind"] == CityMapOverlay.KIND_TIER:
			assert_eq(n["glyph"], CityMapOverlay.tier_text(int(n["tier"])), "the tier in the hexagon translated")
			assert_ne(n["glyph"], "T%d" % int(n["tier"]))
	assert_ne(CityMapOverlay.kind_word(CityMapOverlay.KIND_EXPLOIT), "Exploit", "kind words translated")
	var mini: GridMapView = add_child_autofree(GridMapView.new())
	mini.size = MINI_SIZE
	mini.show_grid(c, RunManager.corporation)
	await _frames(2)
	var texts := mini.drawn_labels.map(func(l: Dictionary) -> String: return String(l["text"]))
	assert_true(texts.has(core), "the mini-map says CORE translated: %s" % [texts])
	# The key's words are translated once: the Labels do not translate them again.
	var legend: MapLegend = add_child_autofree(MapLegend.new(&"solace", true, true))
	await _frames(1)
	for l in legend.body.find_children("*", "Label", true, false):
		assert_eq((l as Label).auto_translate_mode, Node.AUTO_TRANSLATE_MODE_DISABLED, "%s is translated once" % (l as Label).text)
	var corporate := legend.body.find_children("*", "Label", true, false).filter(func(l: Node) -> bool: return (l as Label).text == CityMapOverlay.tr_word("corporate"))
	assert_eq(corporate.size(), 1, "the 'corporate' row is translated")
	# The run rows and the Site card.
	_pseudo(false)
	var hq: Control = await _hq_grid(&"solace", 1.0)
	_pseudo(true)
	hq.show_grid()
	await _frames(2)
	for b in hq.find_child("RunRows", true, false).get_children():
		if b is Button:
			assert_eq((b as Button).auto_translate_mode, Node.AUTO_TRANSLATE_MODE_DISABLED)
			assert_true((b as Button).text.begins_with(CityMapOverlay.tier_text(1)) or (b as Button).text.begins_with(CityMapOverlay.tier_text(2)), "%s: the tier translated" % b.name)
	var card := hq.find_child("SelectedSite", true, false) as TerminalWindow
	assert_eq(card.tag_label.auto_translate_mode, Node.AUTO_TRANSLATE_MODE_DISABLED)
	assert_string_contains(card.tag_label.text, CityMapOverlay.tr_word("corporate").to_upper(), "the status word translated")
	var badge := card.find_child("StatusBadge", true, false) as Badge
	assert_eq(badge.text, CityMapOverlay.tr_word("corporate"), "the status badge translated")
	_pseudo(false)
	await _close(hq)


# --- K8 the HQ mini-map ---------------------------------------------------------------------------

func test_mini_map_labels_keep_off_every_site_block() -> void:
	for corp in CORPS:
		RunManager.reset()
		_open_all()
		RunManager.new_campaign(1, corp)
		for scale in SCALES:
			Settings.set_text_scale(scale)
			var mini: GridMapView = add_child_autofree(GridMapView.new())
			mini.size = MINI_SIZE
			mini.show_grid(RunManager.campaign, RunManager.corporation)
			await _frames(2)
			var what := "%s x%.1f" % [corp, scale]
			assert_false(mini.label_rects.is_empty(), "%s: some labels" % what)
			assert_true(mini.label_rects.has(RunManager.campaign.grid.home_site_id), "%s: CORE labelled" % what)
			for id in mini.label_rects:
				for other in mini.icon_rects:
					assert_false((mini.label_rects[id] as Rect2).intersects(mini.icon_rects[other]),
						"%s: %s's label clear of %s's block" % [what, id, other])
			mini.free()
