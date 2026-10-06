extends GutTest
## Parity fix S-CARDFACE (designer group ruling 2026-10-05; DECISIONS "Parity fix — one card face"):
## LOOT-01, SHOP-02..05, SHOP-07, SHOP-08, DECK-01, DECK-02, CMB-04 (card part), HQ-08. One card face
## (CardFace, the art pass's own exported C-C sticker) for every card view; the whole rules text on
## the face at text scale 1.0 (loot, Mainframe, deck viewer, detail; the hand's grown card); the DECK
## and DISCARD piles beside the hand with their counts.

const COMBAT := "res://scenes/combat/combat_scene.tscn"
const NETRUN := "res://scenes/netrun_map/netrun_scene.tscn"
const SCREEN := Rect2(0, 0, 1280, 720)
const SCALES: Array[float] = [1.0, 1.6, 2.0]
## The two longest rules texts (92 characters) need the inspect at 1.0 in the hand even grown (DECISIONS
## open question: a bigger hand card or a lower floor would hold them).
const HAND_GROWN_LONG: Array[StringName] = [&"hot_patch", &"overdrive"]

var _settings: Dictionary = {}


func before_all() -> void:
	_settings = Settings.snapshot()


func after_all() -> void:
	Settings.restore(_settings)


func before_each() -> void:
	AudioDirector.muted = true
	RunManager.save_slot = "gut_parity_cardface"
	RunManager.scene_switching_enabled = false
	RunManager.delete_save()
	RunManager.reset()
	Motion.force_live = false


func after_each() -> void:
	Motion.force_live = false
	Settings.restore(_settings)
	Dialogue.clear()
	AudioDirector.muted = false
	RunManager.delete_save()
	RunManager.save_slot = RunManager.DEFAULT_SLOT
	RunManager.reset()
	RunManager.scene_switching_enabled = true


func _frames(n: int = 3) -> void:
	for i in n:
		await get_tree().process_frame


## Every card in content, by id.
func _cards() -> Dictionary:
	var out := {}
	var lookup := RunManager.lookup()
	for id in lookup.ids_of_class(&"CardData"):
		out[id] = lookup.get_content(id) as CardData
	return out


func _card(c: CardData, at: Vector2, floor_px: int, give_way: bool) -> ZineCard:
	var z := ZineCard.new(TextDb.t(c, "display_name"), c.ram_cost, TextDb.t(c, "description"), 0).with_card(c)
	z.size = at
	z.fit_whole = true
	z.body_floor = floor_px
	z.pictos_give_way = give_way
	return autofree(z)


# --- one face ---------------------------------------------------------------------------------------

func test_every_sticker_card_is_drawn_by_the_one_face() -> void:
	var src := FileAccess.get_file_as_string("res://scripts/ui/kit/zine_card.gd")
	assert_true(src.contains("CardFace.draw(self)"), "a sticker card draws CardFace")
	for gone in ["func _draw_sticker(", "func sticker_color(", "func with_face_art(", "var face_art"]:
		assert_false(src.contains(gone), "no second card face (%s)" % gone)
	var z: ZineCard = autofree(ZineCard.new("JOLT", 1, "Spin a wheel 3 ticks.", 0))
	for kind in CardFace.KINDS:
		for r in CardFace.RARITY_NAMES.size():
			assert_not_null(CardFace.face(kind, r), "the exported face %s / %d is there" % [kind, r])
	assert_eq(z.look, ZineCard.Look.STICKER)


func test_the_hand_loot_shop_and_deck_views_show_sticker_cards() -> void:
	# the hand
	Settings.set_text_scale(1.0)
	RunManager.new_campaign(1)
	var holder: Control = add_child_autofree(Control.new())
	holder.size = SCREEN.size
	var scene: Control = load(COMBAT).instantiate()
	scene.auto_start = false
	holder.add_child(scene)
	scene.start_fight(&"collections_agent", 5)
	await _frames()
	for c in scene._hand_box.get_children():
		if c is ZineCard:
			assert_eq((c as ZineCard).look, ZineCard.Look.STICKER, "a hand card wears the face")
			assert_false((c as ZineCard).pictos_give_way, "the hand keeps its pictograms at rest")
	scene.skip_motion()
	holder.queue_free()
	await _frames(2)
	# the deck viewer (the loadout's DECK tab is the same view)
	var lookup := RunManager.lookup()
	var deck: Array[StringName] = []
	for id in (_cards().keys() as Array).slice(0, 10):
		deck.append(StringName(id))
	var view: DeckView = add_child_autofree(DeckView.new(deck, lookup))
	await _frames()
	for i in deck.size():
		assert_eq(view.card(i).look, ZineCard.Look.STICKER, "a deck card wears the face")
		assert_true(view.card(i).text_whole(), "%s: the whole text in the viewer" % view.card(i).card_title)


# --- whole text ---------------------------------------------------------------------------------------

func test_loot_cards_keep_the_face_aspect_and_show_every_word() -> void:
	var loot: Vector2 = load("res://scripts/ui/netrun_scene.gd").LOOT_CARD
	assert_almost_eq(loot.x / loot.y, CardFace.UNIT.x / CardFace.UNIT.y, 0.02, "the loot card is the face's 3:4 (never stretched)")
	var cards := _cards()
	for scale in SCALES:
		for id in cards:
			var z := _card(cards[id], loot * scale, ZineCard.FIT_MIN_TEXT, true)
			assert_true(z.text_whole(), "loot x%.1f %s: every word on the face" % [scale, id])


func test_mainframe_cards_show_every_word_above_their_hanging_tag() -> void:
	var cards := _cards()
	for scale in SCALES:
		for id in cards:
			var c: CardData = cards[id]
			var item := ShopItem.new(TextDb.t(c, "display_name"), c.ram_cost, TextDb.t(c, "description"), 0)
			item.fit_whole = true
			item.hotkey = ""
			item.with_price(50)
			item.scaled(scale).with_card(c)
			item.set_meta(BuyButton.TAG_BELOW, true)
			add_child_autofree(item)
			item.size = item.custom_minimum_size
			item.with_buy("BUY")
			assert_true(item.text_whole(), "shop x%.1f %s: every word on the face" % [scale, id])
			var parts := item.sticker_parts()
			var buy: Rect2 = parts["buy"]
			for r in parts["body"]:
				assert_false((r as Rect2).intersects(buy), "shop x%.1f %s: a line %s under the tag %s" % [scale, id, r, buy])
				assert_true(Rect2(Vector2.ZERO, item.size).grow(0.5).encloses(r), "shop x%.1f %s: a line inside the card" % [scale, id])
		await _frames(1)


func test_hand_cards_keep_the_floor_at_rest_and_show_every_word_grown() -> void:
	var cards := _cards()
	for scale in SCALES:
		for id in cards:
			var z := _card(cards[id], ZineCard.STICKER_SIZE * scale, ZineCard.BODY_FLOOR, false)
			var rest := CardFace.text_fit(z)
			assert_gte(int(rest["fs"]), ZineCard.BODY_FLOOR, "hand x%.1f %s: never under the floor at rest" % [scale, id])
			assert_true(bool(rest["pictos"]), "hand x%.1f %s: glyph and value at rest" % [scale, id])
			z.hover_scale = ZineCard.HOVER_SCALE
			var grown := CardFace.text_fit(z)
			assert_gte(int(grown["fs"]) * ZineCard.HOVER_SCALE, float(ZineCard.BODY_FLOOR), "hand x%.1f %s: the grown card's words never under the floor on screen" % [scale, id])
			if scale > 1.0 or not HAND_GROWN_LONG.has(StringName(id)):
				assert_true((grown["lines"] as PackedStringArray).size() <= int(grown["rows"]), "hand x%.1f %s: every word on the grown card" % [scale, id])


func test_no_rules_line_runs_under_the_rarity_pips_or_off_the_face() -> void:
	var cards := _cards()
	for id in cards:
		var z := _card(cards[id], ZineCard.STICKER_SIZE, ZineCard.FIT_MIN_TEXT, true)
		var parts := CardFace.parts(z)
		var pips := Rect2(Vector2(CardFace.PIPS_LEFT, CardFace.PIPS_TOP) * z.size / CardFace.UNIT, (CardFace.UNIT - Vector2(CardFace.PIPS_LEFT, CardFace.PIPS_TOP)) * z.size / CardFace.UNIT)
		for r in parts["body"]:
			assert_false((r as Rect2).intersects(pips), "%s: a line %s over the pips %s" % [id, r, pips])
			assert_true(Rect2(Vector2.ZERO, z.size).grow(0.5).encloses(r), "%s: a line inside the face" % id)
		if parts.has("pictos"):
			for r in parts["body"]:
				assert_false((r as Rect2).intersects(parts["pictos"]), "%s: a line over the pictograms" % id)


# --- the detail ---------------------------------------------------------------------------------------

func test_the_card_detail_is_the_face_at_twice_the_hand_with_its_notes() -> void:
	for scale in SCALES:
		Settings.set_text_scale(scale)
		var lookup := RunManager.lookup()
		var deck: Array[StringName] = [&"overdrive", &"jolt"]
		var view: DeckView = add_child_autofree(DeckView.new(deck, lookup))
		await _frames()
		view.open_card(0)
		await _frames()
		var pop := view.find_child("CardDetail", true, false) as Control
		assert_not_null(pop, "the detail opens")
		var big := pop.find_child("DetailCard", true, false) as ZineCard
		assert_eq(big.custom_minimum_size, ZineCard.STICKER_SIZE * InspectPopup.DETAIL_CARD, "x%.1f: the card at twice the hand's size" % scale)
		assert_true(big.text_whole(), "x%.1f: every word on the detail's face" % scale)
		var notes := InspectPopup.card_notes(lookup.get_content(&"overdrive") as CardData)
		assert_gte(notes.size(), 3, "kind, rarity and a keyword note")
		for n in notes:
			assert_false(n.contains(TextDb.t(lookup.get_content(&"overdrive"), "description")), "the notes never repeat the rules text")
		assert_true(SCREEN.grow(0.5).encloses(pop.get_global_rect()), "x%.1f: the detail %s on the screen" % [scale, pop.get_global_rect()])
		view.queue_free()
		await _frames(1)


func test_the_deck_viewer_fills_its_rows() -> void:
	Settings.set_text_scale(1.0)
	var lookup := RunManager.lookup()
	var deck: Array[StringName] = []
	for id in (_cards().keys() as Array).slice(0, 12):
		deck.append(StringName(id))
	var view: DeckView = add_child_autofree(DeckView.new(deck, lookup))
	await _frames(4)
	var per_row := 0
	var top := view.card(0).position.y
	for i in deck.size():
		if is_equal_approx(view.card(i).position.y, top):
			per_row += 1
	var used := per_row * view.card(0).size.x + DeckView.GRID_GAP * (per_row - 1)
	assert_gte(per_row, DeckView.CARDS_PER_ROW, "at least %d a row" % DeckView.CARDS_PER_ROW)
	assert_gt(used, DeckView.GRID_WIDTH * 0.9, "the row fills the grid (%.0f of %.0f px)" % [used, DeckView.GRID_WIDTH])


# --- the piles ----------------------------------------------------------------------------------------

func test_the_deck_and_discard_piles_show_their_counts_beside_the_hand() -> void:
	for scale in SCALES:
		Settings.set_text_scale(scale)
		RunManager.new_campaign(1)
		var holder: Control = add_child_autofree(Control.new())
		holder.size = SCREEN.size
		var scene: Control = load(COMBAT).instantiate()
		scene.auto_start = false
		holder.add_child(scene)
		scene.start_fight(&"collections_agent", 5)
		await _frames()
		var piles := scene.find_child("CardPiles", true, false) as CardPiles
		assert_not_null(piles, "x%.1f: the piles are there" % scale)
		var state: CombatState = scene.engine.state()
		assert_eq(piles.deck_count, state.draw_pile.size(), "the deck's count")
		assert_eq(piles.discard_count, state.discard_pile.size(), "the discard's count")
		assert_true(piles.is_visible_in_tree(), "x%.1f: shown" % scale)
		var hand: Rect2 = scene._hand_box.get_global_rect()
		assert_lte(piles.get_global_rect().end.x, hand.position.x + 0.5, "x%.1f: left of the hand" % scale)
		assert_true(SCREEN.grow(0.5).encloses(piles.get_global_rect()), "x%.1f: on the screen" % scale)
		scene.end_turn()
		scene.skip_motion()
		await _frames()
		state = scene.engine.state()
		assert_eq(piles.deck_count, state.draw_pile.size(), "x%.1f: the deck's count after a turn" % scale)
		assert_eq(piles.discard_count, state.discard_pile.size(), "x%.1f: the discard's count after a turn" % scale)
		scene.skip_motion()
		holder.queue_free()
		await _frames(2)


# --- loot offers that are not cards -------------------------------------------------------------------

func test_a_firmware_offer_wears_the_face_with_its_own_art_and_word() -> void:
	var z: ZineCard = autofree(ZineCard.new("OVERVOLT", -1, "x", 0).as_offer("firmware", "chip_overvolt"))
	assert_eq(z.offer_kind, "firmware")
	assert_true(MainframeArt.has(z.offer_art), "the chip's own concept art is in the bake")
	assert_eq(String(CardFace.OFFER_WORDS["firmware"]), "FIRMWARE")
	var g := z.ghost_copy()
	assert_eq(g.offer_art, z.offer_art, "a dragged copy keeps it")
	g.free()
