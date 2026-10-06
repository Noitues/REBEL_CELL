extends GutTest
## ART-9 4A (DECISIONS "Art direction — ART-9 4A shop, rewards, events"): the MAINFRAME on its
## F1b facade with the sign v4 and its takeovers, layout v5 (pegboard, foam, cartridges, kraft
## tags, the stock wheel, the recycle bin, the LEAVE sticker), the loot sheet and the events as
## drawn. Behaviour stays the current rules: these tests check the new pieces say and do what the
## rules do, and that their motion keeps the ANIM rules (MotionSkip, reduce effects = end state).

const NETRUN := "res://scenes/netrun_map/netrun_scene.tscn"
const SCREEN := Rect2(0, 0, 1280, 720)

var _scale: float = 1.0
var _reduce: bool = false


func before_all() -> void:
	_scale = Settings.text_scale
	_reduce = Settings.reduce_effects


func before_each() -> void:
	AudioDirector.muted = true
	RunManager.save_slot = "gut_art9_4a"
	RunManager.scene_switching_enabled = false
	RunManager.delete_save()
	RunManager.reset()
	Motion.force_live = false


func after_each() -> void:
	Motion.force_live = false
	Motion.set_speed(1.0)
	Motion.use_config(null)
	CityBakeCache.simulate = false
	CityBakeCache.clear()
	if Settings.reduce_effects != _reduce:
		Settings.set_reduce_effects(_reduce)
	Fx.apply_settings()
	if not is_equal_approx(Settings.text_scale, _scale):
		Settings.set_text_scale(_scale)
	Dialogue.clear()
	Dialogue.dock_default()
	AudioDirector.muted = false
	RunManager.delete_save()
	DirAccess.remove_absolute(RunManager.profile_path())
	RunManager.save_slot = RunManager.DEFAULT_SLOT
	RunManager.reset()
	RunManager.scene_switching_enabled = true


func _frames(n: int = 3) -> void:
	for i in n:
		await get_tree().process_frame


func _netrun(scale: float = 1.0) -> Control:
	Settings.set_text_scale(scale)
	var holder: Control = add_child_autofree(Control.new())
	holder.size = SCREEN.size
	var scene: Control = load(NETRUN).instantiate()
	holder.add_child(scene)
	scene.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	scene.new_campaign(1)
	scene.start_run(1)
	await _frames()
	return scene


func _close(scene: Control) -> void:
	if is_instance_valid(scene) and scene.get_parent() != null:
		scene.get_parent().queue_free()
	await _frames(2)


func _shop(scene: Control, cycles: int = 400) -> void:
	DemoSetup.open_shop(RunManager.netrun, cycles)
	scene._show_current()
	await _frames(4)


# --- shop ---------------------------------------------------------------------------------------

func test_the_mainframe_stands_on_its_facade_with_the_sign_and_its_stock_wheel() -> void:
	var scene := await _netrun()
	await _shop(scene)
	var facade := scene.find_child("MainframeFacade", true, false) as MainframeFacade
	assert_not_null(facade, "the F1b facade behind the Mainframe")
	assert_false(scene.background.visible, "the city hides behind the facade")
	assert_not_null(facade.sign, "the sign on its plate")
	var plate := facade.plate_rect()
	var sign_plate := Rect2(facade.sign.position + MainframeSign.plate_rect().position * facade.sign.size.x / MainframeSign.canvas_size().x,
		MainframeSign.plate_rect().size * facade.sign.size.x / MainframeSign.canvas_size().x)
	assert_almost_eq(sign_plate.position.x, plate.position.x, 1.0, "the sign's plate lands on the facade's plate")
	assert_almost_eq(sign_plate.size.y, plate.size.y, 2.0, "as tall as it")
	var wheel := scene._panel.find_child("Slices", true, false) as SliceStockWheel
	assert_not_null(wheel, "the slice stock is a wheel")
	var stock: Array = RunManager.netrun.run.shop.get("slices", [])
	assert_eq(wheel.items.size(), stock.size(), "a wedge for sale per slice in stock")
	for it in wheel.items:
		assert_not_null(it.buy_button, "%s has its kraft tag" % it.card_title)
	await _close(scene)
	assert_eq(get_tree().root.find_child("MainframeFacade", true, false), null, "the facade goes with the screen")


func test_card_tags_hang_under_the_cards_and_the_notes_cover_no_tag() -> void:
	for scale in [1.0, 1.6, Settings.TEXT_SCALE_MAX]:
		var scene := await _netrun(scale)
		await _shop(scene)
		var tags: Array[Rect2] = []
		var wheel_tags: Array[Rect2] = []
		for n in scene._panel.find_children("*", "ShopItem", true, false):
			var it := n as ShopItem
			if it.buy_button == null:
				continue
			tags.append(it.buy_button.get_global_rect())
			if it.shelf == ShopItem.Shelf.SLICE:
				wheel_tags.append(it.buy_button.get_global_rect())
				# the turned tag as drawn (its corners through its transform) never on the spinner
				var xf := it.buy_button.get_global_transform()
				var sz := it.buy_button.size
				var drawn := PackedVector2Array([xf * Vector2.ZERO, xf * Vector2(sz.x, 0), xf * sz, xf * Vector2(0, sz.y)])
				var mini := scene._panel.find_child("SpinnerMini", true, false) as Control
				if mini != null:
					var m := mini.get_global_rect()
					var box := PackedVector2Array([m.position, Vector2(m.end.x, m.position.y), m.end, Vector2(m.position.x, m.end.y)])
					assert_true(Geometry2D.intersect_polygons(drawn, box).is_empty(), "%s's tag at %.1f clear of the spinner (%s, %s)" % [it.card_title, scale, drawn, m])
			if it.shelf == ShopItem.Shelf.CARD:
				var r := it.get_global_rect()
				assert_true(it.get_meta(BuyButton.TAG_BELOW, false), "%s: its tag hangs under it (shop_v5)" % it.card_title)
				assert_gt(it.buy_button.get_global_rect().end.y, r.end.y, "%s at %.1f: the tag below the card" % [it.card_title, scale])
				assert_true(it.text_whole(), "%s at %.1f: the whole text on the card" % [it.card_title, scale])
		for n in scene._panel.find_children("*", "ShopItem", true, false):
			var it := n as ShopItem
			if it.buy_button != null and it.shelf != ShopItem.Shelf.SLICE:
				for w in wheel_tags:
					assert_false(it.buy_button.get_global_rect().intersects(w), "%s's tag at %.1f clear of the wheel's tags (%s, %s)" % [it.card_title, scale, it.buy_button.get_global_rect(), w])
		var wallet := scene._panel.find_child("Wallet", true, false) as Control
		if wallet != null and wallet.is_visible_in_tree():
			for t in tags:
				assert_false(wallet.get_global_rect().intersects(t), "the wallet at %.1f under no tag (%s, %s)" % [scale, wallet.get_global_rect(), t])
			tags.append(wallet.get_global_rect())
		for name in ["TopNote", "BinNote"]:
			var note := scene._panel.find_child(name, true, false) as Control
			assert_not_null(note, name)
			if note == null or not note.visible:
				continue
			for t in tags:
				assert_false(note.get_global_rect().intersects(t), "%s at %.1f covers no tag or the wallet (%s, %s)" % [name, scale, note.get_global_rect(), t])
		await _close(scene)


func test_the_sign_takeovers_light_the_locked_words() -> void:
	# NO -> MoRE -> MAN: N3 A6(o) / M0 A1(o) R5 E8 / M0 A1 N3 (bible v2 §4.10, round 33).
	var no := MainframeSign.word_state(&"no_more_man", 0)
	assert_eq(no.get("red_3", 0.0), 1.0, "NO lights N")
	assert_eq(no.get("red_6o", 0.0), 1.0, "and the second A as an o")
	assert_false(no.has("red_6"), "whose legs stay dark")
	var more := MainframeSign.word_state(&"no_more_man", 1)
	for k in ["red_0", "red_1o", "red_5", "red_8"]:
		assert_eq(more.get(k, 0.0), 1.0, "MoRE lights %s" % k)
	assert_eq(MainframeSign.dead_letters(&"no_more_man"), [2, 4, 7] as Array[int], "I, F and the second M never light: snapped")
	assert_eq(MainframeSign.dead_letters(&"i_am_ai"), [0, 3, 4, 5, 8] as Array[int])
	for seq in MainframeSign.SEQUENCE_ORDER:
		var frames := MainframeSign.takeover_frames(seq)
		assert_gt(frames.size(), 0, "%s has frames" % seq)
		assert_eq(frames, MainframeSign.takeover_frames(seq), "%s is the same every time (no RNG)" % seq)
	var spill := MainframeSign.spill_of(MainframeSign.word_state(&"no_more_man", 2))
	assert_lte(spill.y, MainframeSign.WORD_SPILL, "the words keep about a tenth of the spill")
	assert_eq(MainframeSign.spill_of(MainframeSign.blue_state(1.0)), Vector2(1, 0), "the normal sign spills full blue")


func test_headless_and_reduce_effects_show_the_lit_sign_and_the_stopped_wheel() -> void:
	var scene := await _netrun()
	await _shop(scene)
	var facade := scene.find_child("MainframeFacade", true, false) as MainframeFacade
	assert_false(facade.sign.warming(), "headless: lit at once")
	assert_false(facade.sign.taking_over(), "no takeover headless")
	assert_eq(facade.sign.shown_state(), MainframeSign.blue_state(1.0), "the blue sign")
	var wheel := scene._panel.find_child("Slices", true, false) as SliceStockWheel
	assert_false(wheel.motion_running(), "the wheel stands still")
	assert_eq(wheel.turn, 0.0, "the stock for sale on top")
	await _close(scene)


func test_the_wheel_spin_is_a_motion_one_press_lands() -> void:
	var scene := await _netrun()
	Motion.force_live = true
	if Settings.reduce_effects:
		Settings.set_reduce_effects(false)
	Fx.apply_settings()
	await _shop(scene)
	scene._shown_screen = ""
	scene._show_current()
	await BoundedWait.frozen_frames(get_tree(), 2)
	var wheel := scene._panel.find_child("Slices", true, false) as SliceStockWheel
	assert_true(wheel.motion_running(), "the stock wheel spins in")
	assert_true(MotionSkip.running(scene).has(wheel), "registered with MotionSkip")
	wheel.complete_motion()
	assert_eq(wheel.turn, 0.0, "landed")
	Motion.force_live = false
	await _close(scene)


func test_shop_sweep_items_out_of_reach_say_so_twice() -> void:
	# Affordability holds: an item is out of reach exactly when its price is over the Cycles,
	# and then its kraft tag prints red, struck, with a padlock (never colour alone).
	for cycles in [0, 60, 120, 400]:
		var scene := await _netrun()
		await _shop(scene, cycles)
		var s := RunManager.netrun
		for row in ["Stickers", "Chips", "Daemons", "Slices"]:
			var holder: Node = scene._panel.find_child(row, true, false)
			if holder == null:
				continue
			for c in holder.get_children():
				var it := c as ShopItem
				if it == null or it.sold_stub or not it.has_meta(scene.STOCK_META):
					continue
				assert_not_null(it.buy_button, "%s has its tag" % it.card_title)
				if row != "Slices":
					assert_eq(it.disabled, it.price > s.run.cycles, "%s at %d Cycles: out of reach iff price %d > Cycles" % [it.card_title, cycles, it.price])
		var bin := scene._panel.find_child("RemoveCard", true, false) as ShopItem
		assert_eq(bin.disabled, s.run.cycles < s.card_removal_price() or s.run.operative.deck.is_empty(), "the bin is the current removal rule")
		await _close(scene)


func test_the_bin_opens_the_deck_viewer_and_removes_one_card_at_the_current_price() -> void:
	var scene := await _netrun()
	await _shop(scene, 400)
	var s := RunManager.netrun
	var deck := s.run.operative.deck.size()
	var cycles := s.run.cycles
	var price := s.card_removal_price()
	(scene._panel.find_child("RemoveCard", true, false) as ShopItem).pressed.emit()
	await _frames(2)
	var view := scene.get_node_or_null("DeckView") as DeckView
	assert_not_null(view, "the recycle bin opens the deck viewer (the current removal)")
	assert_true(view.window is CrtWindow, "on the CRT terminal")
	view.select(0)
	view.confirm()
	await _frames(2)
	assert_eq(s.run.operative.deck.size(), deck - 1, "one card removed")
	assert_eq(s.run.cycles, cycles - price, "at the current price")
	await _close(scene)


func test_loot_is_a_sheet_and_the_pick_peels_into_the_deck() -> void:
	var scene := await _netrun()
	DemoSetup.offer_loot(RunManager.netrun, ["twist", "jam", "cache"])
	scene._show_current()
	await _frames(3)
	var sheet := scene._panel.find_child("LootSheet", true, false) as LootSheet
	assert_not_null(sheet, "the offers are on a loot sheet")
	assert_eq(sheet.row.name, &"Stickers")
	assert_eq(sheet.row.get_child_count(), 3)
	assert_eq(scene.loot_window_rect(sheet.row.get_child(0)), sheet.get_global_rect(), "a sticker's window is its sheet")
	var deck := RunManager.netrun.run.operative.deck.size()
	var note := scene._panel.find_child("DeckNote", true, false) as PencilNote
	assert_eq(note.text, tr("+1 = %d") % (deck + 1), "the pencil says what taking a card does")
	(sheet.row.get_child(1) as ZineCard).pressed.emit()
	await _frames(2)
	assert_eq(RunManager.netrun.run.operative.deck.size(), deck + 1, "the pencil was true")
	await _close(scene)


func test_event_outcome_chips_are_the_deltas_and_a_corp_story_is_a_memo() -> void:
	var scene := await _netrun()
	DemoSetup.open_event(RunManager.netrun, &"ev_continuum_memo")
	scene._show_current()
	await _frames(3)
	var memo := scene._panel.find_child("CorpMemo", true, false) as CorpMemo
	assert_not_null(memo, "a corp speaker's story is an intercepted memo")
	assert_true(memo.is_ancestor_of(scene._panel.find_child("EventText", true, false)), "the story is on the memo")
	assert_true(memo.sheet is CorpPaperPanel, "on corp paper")
	var s := RunManager.netrun
	var ev := s.current_event()
	for i in ev.choices.size():
		var b := scene._panel.find_child("Choice%d" % (i + 1), true, false) as Button
		assert_eq(b.theme_type_variation, ChoiceSticker.TYPE, "a sticker button")
		var row := b.find_child("OutcomeRow", false, false) as OutcomeRow
		var want := OutcomeRow.shown(OutcomeRow.of_choice(s, ev.choices[i]))
		assert_eq(row.items, want if not want.is_empty() else OutcomeRow.no_change(), "choice %d's chips are its deltas" % (i + 1))
	await _close(scene)
	scene = await _netrun()
	DemoSetup.open_event(RunManager.netrun, &"ev_leash_on_the_floor")
	scene._show_current()
	await _frames(3)
	assert_not_null(scene._panel.find_child("CamFeed", true, false), "a street story has its CAM feed")
	assert_null(scene._panel.find_child("CorpMemo", true, false))
	await _close(scene)
