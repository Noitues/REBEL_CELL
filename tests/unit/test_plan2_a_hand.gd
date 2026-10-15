extends GutTest
## Plan 2 A-HAND (PB-PT-003b C2 / B4, PB-PT-002 C6): every card in content shows all its rules text on the
## resting hand face at text 1.0 (no ellipsis), the hand's hit areas never overlap, and the raised card
## clears the DECK / DISCARD counters.

const COMBAT := "res://scenes/combat/combat_scene.tscn"
const SCREEN := Rect2(0, 0, 1280, 720)

var _settings: Dictionary = {}


func before_all() -> void:
	_settings = Settings.snapshot()


func after_all() -> void:
	Settings.restore(_settings)


func before_each() -> void:
	AudioDirector.muted = true
	RunManager.save_slot = "gut_plan2_a_hand"
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


func _hand_card(c: CardData, scale: float) -> ZineCard:
	var z := ZineCard.new(TextDb.t(c, "display_name"), c.ram_cost, FaceText.card_text(c), 0).scaled(scale).with_card(c)
	z.fit_whole = true
	z.body_floor = ZineCard.HAND_REST_FLOOR
	z.grown_floor = ZineCard.BODY_FLOOR
	z.pictos_give_way = true
	z.size = z.custom_minimum_size
	return z


func test_every_card_shows_all_its_words_on_the_resting_hand_face_at_1_0() -> void:
	var lookup := RunManager.lookup()
	var bad: Array[String] = []
	for id in lookup.ids_of_class(&"CardData"):
		var c := lookup.get_content(id) as CardData
		var z := _hand_card(c, 1.0)
		add_child_autofree(z)
		if not z.text_whole():
			bad.append("%s [%s]" % [id, z.description])
	assert_eq(bad.size(), 0, "resting faces with clipped text: %s" % [bad])


func _scene_with_hand() -> Control:
	Settings.set_text_scale(1.0)
	RunManager.new_campaign(1)
	var holder: Control = add_child_autofree(Control.new())
	holder.size = SCREEN.size
	var scene: Control = load(COMBAT).instantiate()
	scene.auto_start = false
	holder.add_child(scene)
	scene.start_fight(&"collections_agent", 5)
	await get_tree().process_frame
	await get_tree().process_frame
	await get_tree().process_frame
	return scene


func _hand_cards(scene: Control) -> Array[ZineCard]:
	var out: Array[ZineCard] = []
	for c in scene._hand_box.get_children():
		if c is ZineCard:
			out.append(c as ZineCard)
	return out


func test_hand_hit_areas_never_overlap() -> void:
	var scene := await _scene_with_hand()
	var cards := _hand_cards(scene)
	assert_gt(cards.size(), 2, "a hand to test")
	for i in cards.size():
		var a := Rect2(cards[i].global_position + cards[i].hit_rect().position, cards[i].hit_rect().size)
		assert_gt(a.size.x, 0.0, "card %d has a hit area" % i)
		for j in range(i + 1, cards.size()):
			var b := Rect2(cards[j].global_position + cards[j].hit_rect().position, cards[j].hit_rect().size)
			assert_false(a.intersects(b), "hit areas of cards %d and %d overlap: %s vs %s" % [i, j, a, b])
		# the point just inside a card's right edge belongs to it alone
		var p := a.end - Vector2(1.0, a.size.y * 0.5)
		for j in cards.size():
			assert_eq(cards[j].hit_has_point(p - cards[j].global_position), j == i, "card %d's point belongs to card %d only (asked %d)" % [i, i, j])
	scene.skip_motion()


func test_a_grown_card_takes_the_pointer_where_it_is_drawn() -> void:
	var scene := await _scene_with_hand()
	var cards := _hand_cards(scene)
	var z := cards[cards.size() / 2]
	z.hover_scale = z.hover_to
	z.fan_turn = 0.0
	var foot := z.get_global_transform() * Vector2(z.size.x * 0.5, z.size.y)
	var above := foot + Vector2(z.grown_shift(), -z.size.y * z.hover_scale * 0.6)
	assert_true(z.hit_has_point(above - z.global_position), "a point on the grown face is on the card")
	z.hover_scale = 1.0
	scene.skip_motion()


func test_the_raised_card_clears_the_deck_and_discard_counters() -> void:
	var scene := await _scene_with_hand()
	var piles: Rect2 = scene._piles.get_global_rect()
	for z in _hand_cards(scene):
		z.hover_scale = z.hover_to
		z.fan_turn = 0.0
		var k := 0.5 + CardFace.FACE_AT.x / CardFace.FACE.x
		var foot := z.get_global_transform() * Vector2(z.size.x * 0.5, z.size.y)
		var at := foot.x + z.grown_shift()
		var half := z.size.x * z.hover_scale * k
		assert_gte(at - half, piles.end.x - 0.5, "%s: the raised card's left edge %.1f clears the piles (right edge %.1f)" % [z.card_title, at - half, piles.end.x])
		z.hover_scale = 1.0
	scene.skip_motion()
