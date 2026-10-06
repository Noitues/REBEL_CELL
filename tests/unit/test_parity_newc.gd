extends GutTest
## Parity NEWC-01..04 (designer 2026-10-05; DECISIONS "Parity fix — new campaign page
## (designer decisions)"): the new campaign page's pickers are tiles with every choice shown,
## locked ones with their unlock cost and refused when picked; ICE is a big `- n +` stepper;
## START is the one verb sticker at the head's right end; the seed, today's run and the share
## codes stay (cyan terminals, the code row folded); pad focus reaches every tile and START;
## the page fits at text scale 1.0 / 1.6 / 2.0. Ported in part from art-m13-final
## tests/unit/test_art_w8b_screens.gd (`test_the_new_campaign_is_a_planning_table_with_one_primary`,
## `test_planning_tiles_fit_their_words_at_every_scale`) and test_art_w2_components.gd
## (`test_the_tile_picker_moves_its_cursor_with_the_keys`).

const HQ := preload("res://scenes/hq/hq_scene.tscn")
const SCALES: Array[float] = [1.0, 1.6, 2.0]
const SCREEN := Vector2(1280, 720)
const PICKERS: Array[String] = ["CorporationPicker", "HomePicker", "ClassPicker"]

var _scale_before := 1.0


func before_each() -> void:
	_scale_before = Settings.text_scale
	RunManager.save_slot = "gut_test_parity_newc"
	RunManager.scene_switching_enabled = false
	RunManager.delete_save()
	RunManager.reset()
	RunManager.profile.unlocks.clear()
	RunManager.profile.best_ice_by_corp.clear()


func after_each() -> void:
	if not is_equal_approx(Settings.text_scale, _scale_before):
		Settings.set_text_scale(_scale_before)
	RunManager.delete_save()
	DirAccess.remove_absolute(RunManager.profile_path())
	RunManager.save_slot = RunManager.DEFAULT_SLOT
	RunManager.reset()
	RunManager.scene_switching_enabled = true


func _frames(n: int = 3) -> void:
	for i in n:
		await get_tree().process_frame


func _open() -> Control:
	var hq: Control = add_child_autofree(HQ.instantiate())
	hq.show_start()
	await _frames()
	return hq


func _pick(hq: Control, pick_name: String) -> PlanningPicker:
	return hq._panel.find_child(pick_name, true, false) as PlanningPicker


func _all(root: Node) -> Array[Node]:
	var out: Array[Node] = []
	for c in root.get_children():
		out.append(c)
		out.append_array(_all(c))
	return out


func _index_of(p: TilePicker, key: String, id: StringName) -> int:
	for i in p.tiles.size():
		if StringName(p.tiles[i].get(key, &"")) == id:
			return i
	return -1


# --- NEWC-01 / NEWC-04: tiles, every choice shown, locked ones with their costs ---------------

func test_the_pickers_are_tiles_showing_locked_choices_with_their_costs() -> void:
	var hq := await _open()
	var lookup := RunManager.lookup()
	for n in _all(hq._panel):
		assert_false(n is OptionButton or n is PopupMenu, "NEWC-04: no dropdown or popup list: %s" % n.name)
	var counts := {"CorporationPicker": &"CorporationData", "HomePicker": &"HomeServerVariantData", "ClassPicker": &"ClassData"}
	for pick_name in PICKERS:
		var p := _pick(hq, pick_name)
		assert_not_null(p, "%s is a tile picker" % pick_name)
		assert_eq(p.tiles.size(), lookup.ids_of_class(counts[pick_name]).size(), "%s shows every choice" % pick_name)
		var locked := 0
		for i in p.tiles.size():
			if p.is_locked(i):
				locked += 1
				assert_ne(p.shown_meta(i), "", "%s tile %d says how it unlocks" % [pick_name, i])
		assert_true(locked > 0, "%s: a fresh profile sees its locked choices" % pick_name)
		assert_false(p.is_locked(p.selected()), "%s starts on an open choice" % pick_name)
	# The Black Market's price on each bought unlock ("UNLOCKS · 120").
	var corps := _pick(hq, "CorporationPicker")
	var meridian := _index_of(corps, "corp", &"meridian")
	var u := CampaignRules.unlock_for(lookup, lookup.get_content(&"meridian"))
	assert_true(corps.is_locked(meridian))
	assert_true(corps.shown_meta(meridian).contains(str(u.schematic_cost)), "Meridian's tile shows its price: %s" % corps.shown_meta(meridian))
	var homes := _pick(hq, "HomePicker")
	for i in homes.tiles.size():
		assert_eq(StringName(homes.tiles[i]["icon"]), StatIcon.HOME, "every home tile wears the house")
	var classes := _pick(hq, "ClassPicker")
	var ghost := _index_of(classes, "class", &"ghost")
	assert_true(classes.is_locked(ghost))
	var gu := CampaignRules.unlock_for(lookup, lookup.get_content(&"ghost"))
	assert_true(classes.shown_meta(ghost).contains(str(gu.schematic_cost)), "Ghost's tile shows its price")
	# REBEL_CELL stays a secret while locked (no spoiler, as the ICE records).
	var rc := _index_of(corps, "corp", &"rebel_cell")
	assert_true(rc >= 0 and corps.is_locked(rc))
	assert_true(bool(corps.tiles[rc].get("redacted", false)))
	assert_false(corps.shown_name(rc).contains("REBEL"), "the locked REBEL_CELL is not named")


func test_the_defaults_and_an_unlock_open_their_tiles() -> void:
	RunManager.profile.add_unlock(&"unlock_ghost")
	RunManager.profile.add_unlock(&"unlock_home_bunker")
	var hq := await _open()
	var classes := _pick(hq, "ClassPicker")
	var homes := _pick(hq, "HomePicker")
	assert_eq(StringName(classes.tiles[classes.selected()]["class"]), RunManager.DEFAULT_CLASS, "the crew starts on the default class")
	assert_eq(homes.tiles[homes.selected()]["name"], TextDb.t(RunManager.lookup().get_content(RunManager.DEFAULT_HOME), "display_name"), "the home starts on the default server")
	assert_false(classes.is_locked(_index_of(classes, "class", &"ghost")), "a bought class is open")


# --- A locked tile can't be picked; a pick flows through to the campaign -----------------------

func test_a_locked_tile_is_refused_and_an_open_pick_starts_the_campaign() -> void:
	RunManager.profile.add_unlock(&"unlock_ghost")
	var hq := await _open()
	var corps := _pick(hq, "CorporationPicker")
	var before := corps.selected()
	watch_signals(corps)
	corps.choose(_index_of(corps, "corp", &"meridian"))
	assert_signal_emitted(corps, "refused", "a locked corporation is refused")
	assert_signal_not_emitted(corps, "tile_chosen")
	assert_eq(corps.selected(), before, "the pick is unchanged")
	assert_true(corps.has_meta(KitState.META_REFUSED), "the refusal shows (KitState's refused state)")
	var classes := _pick(hq, "ClassPicker")
	classes.choose(_index_of(classes, "class", &"ghost"))
	(hq._panel.find_child("SeedSpin", true, false) as SpinBox).value = 77
	(hq._panel.find_child("IceUp", true, false) as Button).pressed.emit()
	var start := hq._panel.find_child("StartCampaign", true, false) as Button
	assert_true(start is VerbSticker, "START is a vinyl sticker")
	start.pressed.emit()
	assert_eq(RunManager.campaign.campaign_seed, 77, "START starts the planned campaign")
	assert_eq(RunManager.campaign.ice_level, 1)
	assert_eq(RunManager.campaign.start_class_id, &"ghost", "the picked crew")
	assert_eq(RunManager.corporation.id, RunManager.DEFAULT_CORPORATION, "the refused corp never became the target")


func test_the_ice_stepper_steps_within_its_cap_and_follows_the_target() -> void:
	for id in [&"unlock_meridian"]:
		RunManager.profile.add_unlock(id)
	RunManager.profile.best_ice_by_corp["meridian"] = 9
	var hq := await _open()
	var spin := hq._panel.find_child("IceSpin", true, false) as SpinBox
	var up := hq._panel.find_child("IceUp", true, false) as Button
	var down := hq._panel.find_child("IceDown", true, false) as Button
	var number := hq._panel.find_child("IceValue", true, false) as Label
	assert_false(spin.visible, "the spin box is the stepper's value, not shown")
	down.pressed.emit()
	assert_eq(int(spin.value), 0, "never below 0")
	assert_true(down.has_meta(KitState.META_REFUSED), "a step past the end is refused")
	for i in int(spin.max_value) + 2:
		up.pressed.emit()
	assert_eq(int(spin.value), RunManager.ice_cap(RunManager.DEFAULT_CORPORATION), "never past the cap")
	assert_eq(number.text, str(int(spin.value)), "the big number follows")
	var corps := _pick(hq, "CorporationPicker")
	corps.choose(_index_of(corps, "corp", &"meridian"))
	assert_eq(int(spin.max_value), RunManager.ice_cap(&"meridian"), "each corporation has its own ICE ladder")


# --- Pad focus reaches every tile and the start verb -------------------------------------------

func _reachable() -> Dictionary:
	var start := get_viewport().gui_get_focus_owner()
	var seen := {}
	if start == null:
		return seen
	seen[start] = true
	var queue: Array = [start]
	while not queue.is_empty():
		var c: Control = queue.pop_front()
		for side in [SIDE_LEFT, SIDE_RIGHT, SIDE_TOP, SIDE_BOTTOM]:
			var n := c.find_valid_focus_neighbor(side)
			if n != null and not seen.has(n):
				seen[n] = true
				queue.append(n)
	return seen


func _action(action: StringName) -> InputEventAction:
	var e := InputEventAction.new()
	e.action = action
	e.pressed = true
	return e


func test_pad_focus_reaches_every_tile_and_the_start_verb() -> void:
	var hq := await _open()
	var owner := get_viewport().gui_get_focus_owner()
	assert_not_null(owner, "the page focuses a control")
	var seen := _reachable()
	for n in PICKERS + ["StartCampaign", "IceDown", "IceUp", "SeedNext", "DailyRunButton", "CodesToggle"]:
		var c := hq._panel.find_child(n, true, false) as Control
		assert_true(seen.has(c), "%s is reachable by pad" % n)
	# Inside a picker the D-pad walks its cursor over every tile (locked ones too: their
	# words say how they open); at an edge the move is left to the focus.
	for pick_name in PICKERS:
		var p := _pick(hq, pick_name)
		p.grab_focus()
		await _frames(1)
		p.cursor = 0
		var visited := {0: true}
		var queue: Array = [0]
		while not queue.is_empty():
			var at: int = queue.pop_front()
			for a in [&"ui_left", &"ui_right", &"ui_up", &"ui_down"]:
				var to := p.move_target(at, _action(a))
				if not visited.has(to):
					visited[to] = true
					queue.append(to)
		assert_eq(visited.size(), p.tiles.size(), "%s: the cursor reaches every tile" % pick_name)
		p.cursor = p.tiles.size() - 1
		p._gui_input(_action(&"ui_right"))
		assert_eq(p.cursor, p.tiles.size() - 1, "%s: the last tile leaves the move to the focus" % pick_name)
		assert_eq(p.tile_state(p.cursor), KitState.FOCUS, "%s: the cursor's tile shows focus, locked or not" % pick_name)
	# A pad press on a locked tile is refused, on an open one picks it.
	var corps := _pick(hq, "CorporationPicker")
	corps.grab_focus()
	await _frames(1)
	corps.cursor = _index_of(corps, "corp", &"meridian")
	watch_signals(corps)
	corps._gui_input(_action(&"ui_accept"))
	assert_signal_emitted(corps, "refused")


# --- NEWC-02 / NEWC-03: the head, the seed, today's run and the share codes --------------------

func test_the_head_ends_on_start_and_the_code_terminals_are_cyan() -> void:
	var hq := await _open()
	var head := hq._panel.find_child("PageHead", true, false) as HBoxContainer
	var kids := head.get_children()
	assert_eq(kids[0].name, &"TitleSticker", "main's NEW CAMPAIGN title sticker stays first")
	assert_eq(kids[kids.size() - 1].name, &"StartCampaign", "START ends the head (top right)")
	var stickers := 0
	for n in _all(hq._panel):
		if n is VerbSticker and (n as VerbSticker).fill == VerbSticker.Fill.PINK:
			stickers += 1
	assert_eq(stickers, 1, "one verb sticker")
	for n in ["DailyRun", "ShareCodes"]:
		var w := hq._panel.find_child(n, true, false) as CrtWindow
		assert_not_null(w, n)
		assert_ne(w.accent, Palette.CELL_ACID, "%s is no lime panel (lime is focus)" % n)
	assert_not_null(hq._panel.find_child("SeedSpin", true, false), "the city seed stays")
	var row := hq._panel.find_child("CodesRow", true, false) as Control
	assert_false(row.visible, "the share code row starts folded")
	(hq._panel.find_child("CodesToggle", true, false) as Button).pressed.emit()
	await _frames(2)
	assert_true(row.visible, "the toggle opens it")
	assert_eq(get_viewport().gui_get_focus_owner(), hq._panel.find_child("CodeEdit", true, false), "the code field takes the focus")


# --- Fits at every text scale -------------------------------------------------------------------

func test_the_page_fits_at_every_text_scale() -> void:
	for scale in SCALES:
		Settings.set_text_scale(scale)
		RunManager.reset()
		RunManager.profile.unlocks.clear()
		RunManager.profile.add_unlock(&"unlock_ghost")
		var hq := await _open()
		await _frames(2)
		assert_true(hq._panel.get_combined_minimum_size().x <= SCREEN.x, "the page fits the screen's width at %.1f" % scale)
		var start := hq._panel.find_child("StartCampaign", true, false) as Control
		assert_true(Rect2(Vector2.ZERO, SCREEN).encloses(start.get_global_rect()), "START on the first screen at %.1f: %s" % [scale, start.get_global_rect()])
		for pick_name in PICKERS:
			var p := _pick(hq, pick_name)
			assert_true(p.get_global_rect().end.x <= SCREEN.x + 0.5, "%s inside the screen at %.1f" % [pick_name, scale])
			assert_true(p.name_px() >= roundi(UiTheme.CAPTION * scale), "%s names at caption or larger at %.1f" % [pick_name, scale])
			var last := p.tile_rect(p.tiles.size() - 1)
			assert_true(last.end.x <= p.size.x + 0.5 and last.end.y <= p.size.y + 0.5, "%s: every tile inside the picker at %.1f" % [pick_name, scale])
			var nf := p.name_font()
			for i in p.tiles.size():
				var lines := p.name_lines(i)
				assert_true(lines.size() <= TilePicker.NAME_LINES, "%s tile %d: name in two lines at %.1f" % [pick_name, i, scale])
				for line in lines:
					assert_true(nf.get_string_size(line, HORIZONTAL_ALIGNMENT_LEFT, -1, p.name_px()).x <= p.name_room(i, p.tile_extent().x) + 0.5,
						"%s: '%s' fits its tile at %.1f" % [pick_name, line, scale])
				assert_true(p.meta_lines(i).size() <= TilePicker.META_LINES, "%s tile %d: meta in two lines at %.1f" % [pick_name, i, scale])
		hq.queue_free()
		await _frames(1)
