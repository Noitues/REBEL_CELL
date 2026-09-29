extends GutTest
## Art pass W4 (ART_BIBLE 6.3, 7.3, 4.3): cards as premium PAPER objects. The frame, the
## card type colour, rarity by stock, the illustration stand-ins, no truncation at any
## text scale, the detail view, the drag ghost and the hover API.

const SCALES: Array[float] = [1.0, 1.6, 2.0]


func _cards() -> Array[CardData]:
	var out: Array[CardData] = []
	var names := DirAccess.get_files_at("res://content/cards")
	names.sort()
	for f in names:
		if f.ends_with(".tres"):
			out.append(load("res://content/cards/" + f) as CardData)
	return out


func _card(id: StringName) -> CardData:
	return load("res://content/cards/%s.tres" % id) as CardData


## A sticker for `card` at scale `s`, sized as a container would size it.
func _sticker(card: CardData, s: float = 1.0, full: bool = false) -> ZineCard:
	var z := ZineCard.new(TextDb.t(card, "display_name"), card.ram_cost, TextDb.t(card, "description"), 0).scaled(s).with_card(card)
	z.fit_whole = full
	z.size = z.custom_minimum_size
	return z


# --- 1. The frame (6.3) -------------------------------------------------------------------------

func test_the_hand_size_contract_is_unchanged() -> void:
	assert_eq(ZineCard.STICKER_SIZE, Vector2(112, 148), "callers lay the hand out with it (W3)")
	var z := ZineCard.new("JOLT", 1, "Spin a wheel 3 ticks.", 0).scaled(1.6)
	assert_eq(z.custom_minimum_size, ZineCard.STICKER_SIZE * 1.6)
	z.free()


func test_the_frame_has_gem_title_art_band_in_order() -> void:
	for card in _cards():
		var z := _sticker(card)
		var L := z.face_layout()
		var art: Rect2 = L["art"]
		var band: Rect2 = L["band"]
		var title: Rect2 = L["title"]
		var gem_c: Vector2 = L["gem_c"]
		assert_true(gem_c.x < z.size.x * 0.25 and gem_c.y < z.size.y * 0.2, "%s: the cost gem sits top-left" % card.id)
		assert_true(title.end.y <= art.position.y + 0.5, "%s: the title above the art" % card.id)
		assert_almost_eq(art.size.y, z.size.y * ZineCard.ART_SHARE, 0.5, "%s: the art window is 60%% of the height" % card.id)
		assert_true(band.position.y >= art.get_center().y, "%s: the effect band at the foot" % card.id)
		assert_true(Rect2(Vector2.ZERO, z.size).encloses(band), "%s: the band inside the card" % card.id)
		z.free()


func test_frame_type_sizes_come_from_the_scale() -> void:
	var steps := {}
	for st in [UiTheme.CAPTION, UiTheme.BODY, UiTheme.LABEL, UiTheme.TITLE, UiTheme.HEADING]:
		steps[st] = true
	for s in SCALES:
		for card in _cards():
			var z := _sticker(card, s, true)
			var L := z.face_layout()
			assert_true(steps.has(int(L["title_step"])), "the title is on a type step")
			assert_eq(int(L["title_fs"]), UiTheme.font_px_at(int(L["title_step"]), s), "the title size is its step x scale")
			assert_eq(int(L["rules_fs"]), UiTheme.font_px_at(int(L["rules_step"]), s), "the rules size is its step x scale")
			assert_true(int(L["rules_step"]) in ZineCard.RULES_STEPS, "rules at body or caption")
			assert_true(int(L["band_fs"]) >= UiTheme.font_px_at(UiTheme.CAPTION, s), "the band's number is caption or larger")
			z.free()


func test_the_title_starts_at_label_and_rules_at_body_when_they_fit() -> void:
	var z := _sticker(_card(&"jolt"), 1.0, true)
	z.size = ZineCard.DETAIL_SIZE
	var L := z.face_layout()
	assert_eq(int(L["title_step"]), UiTheme.LABEL, "a short title in Anton at label")
	assert_eq(int(L["rules_step"]), UiTheme.BODY, "rules in Plex at body")
	z.free()


func test_card_colour_means_card_type() -> void:
	var expect := {&"jolt": CardArt.Type.WHEEL, &"feather_touch": CardArt.Type.WHEEL, &"freeze": CardArt.Type.WHEEL,
		&"firewall": CardArt.Type.SYSTEM, &"patch_up": CardArt.Type.SYSTEM, &"cache": CardArt.Type.SYSTEM, &"overdrive": CardArt.Type.SYSTEM,
		&"static_shock": CardArt.Type.HACK, &"corrupt_packet": CardArt.Type.HACK, &"strip": CardArt.Type.HACK, &"bug": CardArt.Type.HACK}
	for id in expect:
		assert_eq(CardArt.type_of(_card(id)), expect[id], "%s is %s" % [id, CardArt.TYPE_WORDS[expect[id]]])
	for card in _cards():
		var z := _sticker(card)
		assert_eq(z.variant, int(CardArt.TYPE_VARIANT[CardArt.type_of(card)]), "%s's stock is its type's" % card.id)
		z.free()


func test_the_other_looks_still_draw_their_parts() -> void:
	for lk in [ZineCard.Look.CHIP, ZineCard.Look.CARD_TILE, ZineCard.Look.SLICE_TILE]:
		var z := ZineCard.new("OVERCLOCK CHIP", 45, "Firmware: your ATTACK slices deal +1.", 0).as_tile(lk, Palette.NET_CYAN)
		z.size = z.custom_minimum_size
		var p := z.tile_parts()
		assert_false((p["names"] as Array).is_empty(), "look %d shows its name" % lk)
		assert_true(int(p["fs"]) >= UiTheme.CAPTION, "look %d: the name is caption or larger" % lk)
		z.free()
