extends GutTest
## M14 12Q-MAIN (DECISIONS "M14 12Q-MAIN: the Mainframe, the loadout spinner, the Daemon tray and the
## hover zoom fit at big text"; audit docs/handoff/m14_12q/qa_matrix_audit.md L35 / L37 / L44 / L50 / L63):
## at text 1.0 / 1.6 / 2.0 the Mainframe's stock wheel shows its wedges' read blocks and the info strip
## its whole text; the REMOVE A CARD viewer shows whole cards; the loadout's spinner tab keeps its swap
## chips' words whole and its window on screen; the Daemon tray stands beside the ROUTE window; the
## hovered hand card's zoom keeps the player's HP readable.

const NETRUN := "res://scenes/netrun_map/netrun_scene.tscn"
const COMBAT := "res://scenes/combat/combat_scene.tscn"
const SCREEN := Rect2(0, 0, 1280, 720)
const SCALES: Array[float] = [1.0, 1.6, 2.0]

var _scale: float = 1.0


func before_all() -> void:
	_scale = Settings.text_scale


func before_each() -> void:
	AudioDirector.muted = true
	RunManager.save_slot = "gut_m14_12q_main"
	RunManager.scene_switching_enabled = false
	RunManager.delete_save()
	RunManager.reset()


func after_each() -> void:
	if not is_equal_approx(Settings.text_scale, _scale):
		Settings.set_text_scale(_scale)
	Dialogue.clear()
	AudioDirector.muted = false
	RunManager.delete_save()
	DirAccess.remove_absolute(RunManager.profile_path())
	RunManager.save_slot = RunManager.DEFAULT_SLOT
	RunManager.reset()
	RunManager.scene_switching_enabled = true


func _frames(n: int = 3) -> void:
	for i in n:
		await get_tree().process_frame


func _holder() -> Control:
	var holder: Control = add_child_autofree(Control.new())
	holder.size = SCREEN.size
	return holder


func _netrun(scale: float) -> Control:
	Settings.set_text_scale(scale)
	var scene: Control = load(NETRUN).instantiate()
	_holder().add_child(scene)
	scene.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	scene.new_campaign(1)
	scene.start_run(1)
	await _frames()
	return scene


func _close(scene: Control) -> void:
	if is_instance_valid(scene) and scene.get_parent() != null:
		scene.get_parent().queue_free()
	await _frames(2)


func _mainframe(scale: float) -> Control:
	var scene := await _netrun(scale)
	DemoSetup.open_shop(RunManager.netrun, 400)
	scene._show_current()
	await _frames(6)
	return scene


# --- L37: the Mainframe's stock wheel and info strip -----------------------------------------------

func test_the_stock_wheel_shows_its_read_blocks_on_screen_at_every_text_size() -> void:
	for scale in SCALES:
		var scene := await _mainframe(scale)
		var wheel := scene._panel.find_child("Slices", true, false) as SliceStockWheel
		assert_false(wheel.items.is_empty(), "at %.1f: slices for sale" % scale)
		var hub := wheel.get_global_transform() * wheel.hub
		var foot := hub.y - SliceStockWheel.R_OUT * SliceStockWheel.READ_FOOT
		assert_true(foot <= SCREEN.end.y, "at %.1f: the wedges' glyphs and values stand above the screen's foot (%.0f)" % [scale, foot])
		assert_true(hub.y >= SCREEN.end.y, "at %.1f: the hub stays below the screen (%.0f)" % [scale, hub.y])
		var board := scene._panel.find_child("Pegboard", true, false) as Control
		var info := board.find_child("ShopInfo", true, false) as Control
		for it in wheel.items:
			var tag := it.buy_button.get_global_rect()
			assert_true(SCREEN.encloses(tag), "at %.1f: %s's tag on screen (%s)" % [scale, it.card_title, tag])
			# the tags hang over the board's foot: at most graze the strip's frame, never its words
			var label := info.find_child("ShopInfoText", true, false) as Control
			var t := label.get_global_transform()  # on the scaled board: the drawn rect
			var words := Rect2(t.origin, t.basis_xform(label.size))
			assert_false(tag.intersects(words), "at %.1f: %s's tag (%s) clear of the info strip's words (%s)" % [scale, it.card_title, tag, words])
		await _close(scene)


func test_the_info_strip_shows_every_text_whole_at_every_text_size() -> void:
	var NetrunScript := load("res://scripts/ui/netrun_scene.gd")
	for scale in SCALES:
		var scene := await _mainframe(scale)
		var board := scene._panel.find_child("Pegboard", true, false) as Control
		var info := board.find_child("ShopInfo", true, false) as Control
		var label := info.find_child("ShopInfoText", true, false) as Label
		assert_eq(label.text_overrun_behavior, TextServer.OVERRUN_NO_TRIMMING, "at %.1f: no ellipsis" % scale)
		assert_eq(label.max_lines_visible, -1, "at %.1f: no line cap" % scale)
		var texts: PackedStringArray = label.get_meta(NetrunScript.INFO_TEXTS_META, PackedStringArray())
		assert_true(texts.size() > 3, "at %.1f: the idle line and each item's text are listed (%d)" % [scale, texts.size()])
		var size0 := info.size
		for t in texts:
			label.text = t
			await _frames(1)
			assert_true(label.get_line_count() <= label.get_visible_line_count(), "at %.1f: whole: %s (%d of %d lines)" % [scale, t, label.get_visible_line_count(), label.get_line_count()])
			assert_almost_eq(info.size.y, size0.y, 0.5, "at %.1f: the strip keeps its size between items" % scale)
		assert_true(SCREEN.grow(0.5).encloses(info.get_global_rect()), "at %.1f: the strip whole on screen (%s)" % [scale, info.get_global_rect()])
		assert_true(board.scale.x >= NetrunScript.SHOP_BOARD_FIT_FLOOR - 0.001, "at %.1f: the board keeps its floor (%.2f)" % [scale, board.scale.x])
		var mini := board.find_child("SpinnerMini", true, false) as Control
		assert_false(mini.get_global_rect().intersects(info.get_global_rect()), "at %.1f: the spinner beside the strip, not on it" % scale)
		await _close(scene)


# --- L63: the REMOVE A CARD viewer -----------------------------------------------------------------

func test_the_remove_viewer_shows_whole_cards_and_keeps_on_the_canvas() -> void:
	for scale in SCALES:
		var scene := await _mainframe(scale)
		scene.open_remove()
		await _frames(6)
		var view := scene.get_node_or_null("DeckView") as DeckView
		assert_not_null(view, "at %.1f: the viewer opens" % scale)
		var win := view.window.get_global_rect()
		assert_true(SCREEN.grow(0.5).encloses(win), "at %.1f: the window on the canvas (%s)" % [scale, win])
		var head := view.window.find_child("TerminalTitle", true, false) as Label
		assert_eq(head.get_line_count(), 1, "at %.1f: the title on one line" % scale)
		var scroll := view.find_child("DeckGridRoom", true, false).get_parent() as ScrollContainer
		var glass := scroll.get_global_rect()
		var first := view.card(0)
		assert_true(first.text_scale >= DeckView.card_scale_at(1.0) - 0.001, "at %.1f: the cards never smaller than at text 1.0 (%.2f)" % [scale, first.text_scale])
		var card := first.get_global_rect()
		assert_true(glass.grow(0.5).encloses(card), "at %.1f: a whole card in the glass (%s in %s)" % [scale, card, glass])
		assert_true(SCREEN.grow(0.5).encloses(view.close_button.get_global_rect()), "at %.1f: Close on screen" % scale)
		await _close(scene)


# --- L35: the loadout's spinner tab ------------------------------------------------------------------

func _loadout_spinner(scale: float) -> LoadoutView:
	Settings.set_text_scale(scale)
	RunManager.new_campaign(7)
	var op: OperativeState = RunManager.campaign.living_operatives()[0]
	DemoSetup.set_rank(op, 3)
	var view := LoadoutView.new(op, RunManager.lookup(), [], RunManager.campaign.living_operatives())
	_holder().add_child(view)
	await _frames(2)
	view.show_spinner()
	await _frames(6)
	return view


func test_the_loadout_spinner_keeps_its_swap_words_whole_and_its_window_on_screen() -> void:
	for scale in SCALES:
		var view := await _loadout_spinner(scale)
		var sv := view.find_child("SpinnerView", true, false) as SpinnerView
		var side := sv.find_child("Side", true, false) as Control
		assert_not_null(side, "at %.1f: the Rank 3 swaps beside the wheel" % scale)
		var chips := 0
		for b: Button in sv.find_children("Swap_*", "Button", true, false):
			chips += 1
			var f := b.get_theme_font(&"font")
			var fs := b.get_theme_font_size(&"font_size")
			var room := b.size.x - b.get_theme_stylebox(&"normal").get_minimum_size().x
			for word in b.text.split(" ", false):
				assert_true(f.get_string_size(word, HORIZONTAL_ALIGNMENT_LEFT, -1, fs).x <= room + 0.5, "at %.1f: \"%s\" whole on its chip (%.0f px room)" % [scale, word, room])
			for k in 6:
				var pad := sv.slot_pad(k)
				if pad != null:
					assert_false(pad.get_global_rect().intersects(b.get_global_rect()), "at %.1f: %s clear of slot %d's pad" % [scale, b.name, k])
		assert_gt(chips, 0, "at %.1f: swap chips listed" % scale)
		var win := sv.window.get_global_rect()
		assert_true(SCREEN.grow(0.5).encloses(win), "at %.1f: the window on screen (%s)" % [scale, win])
		assert_true(SCREEN.grow(0.5).encloses(sv.close_button.get_global_rect()), "at %.1f: Close [Esc] on screen" % scale)
		var hp: Rect2 = sv.d4.get_global_transform() * (sv.d4.hp_layout()["hp"] as Rect2)
		assert_true(win.grow(0.5).encloses(hp), "at %.1f: the HP gauge inside the window (%s)" % [scale, hp])
		view.get_parent().queue_free()
		await _frames(2)


# --- L44: the Daemon tray ----------------------------------------------------------------------------

func test_the_daemon_tray_stands_beside_the_route_window() -> void:
	for scale in SCALES:
		var scene := await _netrun(scale)
		var ids: Array = RunManager.lookup().ids_of_class(&"DaemonData")
		ids.sort()
		var first: Array[StringName] = [StringName(ids[0])]
		DemoSetup.add_daemons(RunManager.netrun, first)
		scene._show_current()
		await _frames(6)
		var route := scene.find_child("RouteWindow", true, false) as Control
		assert_true(route != null and route.is_visible_in_tree(), "at %.1f: the ROUTE window shows" % scale)
		scene.open_daemons()
		await _frames(3)
		var tray := scene.get_node("DaemonTray") as DaemonTray
		tray.show_card(first[0], false)
		await _frames(3)
		var r := route.get_global_rect()
		var strip := (tray.get_child(0) as Control).get_global_rect()
		var card := (tray._card as Control).get_global_rect()
		assert_false(strip.intersects(r), "at %.1f: the strip (%s) beside the ROUTE window (%s)" % [scale, strip, r])
		assert_false(card.intersects(r), "at %.1f: the card (%s) beside the ROUTE window (%s)" % [scale, card, r])
		assert_true(SCREEN.grow(0.5).encloses(strip) and SCREEN.grow(0.5).encloses(card), "at %.1f: the tray on screen" % scale)
		tray.close()
		await _close(scene)


# --- L50: the hovered hand card's zoom ----------------------------------------------------------------

func test_the_hover_zoom_keeps_the_players_hp_readable() -> void:
	for scale in SCALES:
		Settings.set_text_scale(scale)
		RunManager.new_campaign(1)
		var scene: Control = load(COMBAT).instantiate()
		scene.auto_start = false
		_holder().add_child(scene)
		scene.start_fight(&"collections_agent", 5)
		await _frames()
		var hp: Rect2 = scene.player_hp_rect()
		assert_true(hp.has_area(), "at %.1f: the HP readout is laid out" % scale)
		for c in scene._hand_box.get_children():
			var z := c as ZineCard
			if z == null:
				continue
			z.hover_scale = z.hover_to
			var k := 0.5 + CardFace.FACE_AT.x / CardFace.FACE.x
			var half := z.size.x * z.hover_scale * k
			var foot := z.get_global_transform() * Vector2(z.size.x * 0.5 + z.spread, z.size.y)
			var x := foot.x + z.grown_shift()
			var face := Rect2(x - half, foot.y - z.size.y * z.hover_scale - z.lift - z.fan_rise, half * 2.0, z.size.y * z.hover_scale)
			assert_false(face.intersects(hp), "at %.1f: %s grown (%s) clear of the HP (%s)" % [scale, z.card_title, face, hp])
			assert_true(face.position.x >= -0.5 and face.end.x <= SCREEN.end.x + 0.5, "at %.1f: %s grown stays on screen" % [scale, z.card_title])
			z.hover_scale = 1.0
		scene.skip_motion()
		scene.get_parent().queue_free()
		await _frames(2)
