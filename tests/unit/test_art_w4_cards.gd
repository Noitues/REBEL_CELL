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


# --- 2. Rarity by stock (6.3) -------------------------------------------------------------------

func test_each_rarity_has_a_distinct_stock_readable_in_greyscale() -> void:
	var seen := {}
	var pips := {}
	var edges := {}
	for r in [RC.Rarity.COMMON, RC.Rarity.UNCOMMON, RC.Rarity.RARE]:
		var st := ZineCard.stock_of(r)
		seen[st] = true
		var marks := ZineCard.stock_marks(st)
		pips[marks["pip"]] = true
		edges[marks["edge"]] = true
	assert_eq(seen.size(), 3, "photocopy, glossy and foil")
	assert_eq(pips.size(), 3, "a distinct pip glyph per rarity (greyscale)")
	assert_eq(edges.size(), 3, "a distinct edge per rarity (greyscale)")
	assert_eq(ZineCard.stock_of(RC.Rarity.COMMON), ZineCard.Stock.PHOTOCOPY)
	assert_eq(ZineCard.stock_of(RC.Rarity.UNCOMMON), ZineCard.Stock.GLOSSY)
	assert_eq(ZineCard.stock_of(RC.Rarity.RARE), ZineCard.Stock.FOIL)
	assert_eq(ZineCard.stock_of(RC.Rarity.BOSS), ZineCard.Stock.FOIL, "boss rarity is foil too")
	assert_true(bool(ZineCard.stock_marks(ZineCard.Stock.PHOTOCOPY)["grain"]), "common is photocopy grain")
	assert_true(bool(ZineCard.stock_marks(ZineCard.Stock.GLOSSY)["gloss"]), "uncommon is a glossy sticker")
	assert_true(bool(ZineCard.stock_marks(ZineCard.Stock.FOIL)["foil"]), "rare is foil")


func test_only_rare_cards_run_the_foil() -> void:
	var rare := _sticker(_card(&"short_circuit"))
	var common := _sticker(_card(&"jolt"))
	assert_true(rare.is_foil())
	assert_false(common.is_foil())
	rare.free()
	common.free()


func test_foil_is_static_under_reduce_effects() -> void:
	var was := Settings.reduce_effects
	Settings.reduce_effects = true
	for p in [Vector2(-1, -1), Vector2(0.3, 0.9), Vector2(1, 0)]:
		assert_eq(ZineCard.foil_target(p), ZineCard.FOIL_STATIC, "the foil ignores the pointer (%s)" % p)
	var z := _sticker(_card(&"short_circuit"))
	add_child_autofree(z)
	z.foil_tilt = Vector2(0.9, 0.9)
	z._process(0.1)
	assert_eq(z.foil_tilt, ZineCard.FOIL_STATIC, "a static sheen at once")
	Settings.reduce_effects = was
	assert_ne(ZineCard.foil_target(Vector2(0.3, 0.9)), ZineCard.FOIL_STATIC, "with effects on it follows the pointer")
	var src := FileAccess.get_file_as_string("res://shaders/foil.gdshader")
	assert_true(src.contains("#include \"res://shaders/lib/rc_common.gdshaderinc\""), "the library include (W6)")
	assert_true(src.contains("rc_live()") and src.contains("rc_time(TIME)"), "the shader goes static under the global reduce_effects")


# --- 3. Illustration stand-ins (7.3, Q1) --------------------------------------------------------

func test_every_card_maps_to_an_effect_family() -> void:
	var used := {}
	for card in _cards():
		var fam := CardArt.family_of(card)
		assert_true(fam in CardArt.FAMILIES, "%s: family %s is listed" % [card.id, fam])
		assert_ne(fam, &"chip", "%s maps to an effect family, not the fallback" % card.id)
		used[fam] = true
	assert_between(CardArt.FAMILIES.size(), 25, 40, "about 30 base illustrations (Q1)")
	assert_eq(used.size(), CardArt.FAMILIES.size() - 1, "every family but the chip fallback has a card")


func test_unique_art_for_rares_and_class_cards_only() -> void:
	for card in _cards():
		var unique := card.rarity >= RC.Rarity.RARE or card.class_id != &""
		assert_eq(CardArt.is_unique(card), unique, "%s unique art" % card.id)
		assert_eq(CardArt.art_key(card).begins_with("id:"), unique, "%s keyed by %s" % [card.id, "its id" if unique else "its family"])


func test_card_art_is_deterministic() -> void:
	for id in [&"jolt", &"short_circuit", &"ghost_step"]:
		var card := _card(id)
		var key := CardArt.art_key(card)
		var a := CardArt.render_image(CardArt.family_of(card), key, 0, 96)
		var b := CardArt.render_image(CardArt.family_of(card), key, 0, 96)
		assert_eq(hash(a.get_data()), hash(b.get_data()), "%s: same id, same image" % id)
		assert_eq(a.get_size(), Vector2i(144, 96), "3:2 master aspect")
	var x := CardArt.render_image(&"ghost_step", CardArt.art_key(_card(&"ghost_step")), 0, 96)
	var y := CardArt.render_image(&"jam", CardArt.art_key(_card(&"jam")), 0, 96)
	assert_ne(hash(x.get_data()), hash(y.get_data()), "a class card's art differs from its family's base")


func test_shared_family_art_is_tinted_per_type() -> void:
	var p := CardArt.render_image(&"spin", "family:spin", 0, 96)
	var k := CardArt.render_image(&"spin", "family:spin", 1, 96)
	assert_ne(hash(p.get_data()), hash(k.get_data()), "paper and black prints of one base differ")
	assert_eq(CardArt.inks(0)[1], Palette.INK, "the key ink is INK on paper")
	assert_eq(CardArt.inks(1)[1], Palette.PAPER, "and paper-white on black stock")


func test_an_illustration_texture_replaces_the_stand_in() -> void:
	var card := _card(&"jolt").duplicate() as CardData
	var img := Image.create(768, 512, false, Image.FORMAT_RGB8)
	var tex := ImageTexture.create_from_image(img)
	card.art = tex
	var z := _sticker(card)
	assert_eq(z.art_texture(88.0), tex, "CardData.art is drawn instead of the stand-in")
	z.free()
	var plain := _sticker(_card(&"jolt"))
	var t2 := plain.art_texture(88.0)
	assert_ne(t2, tex, "no art: the stand-in")
	plain.free()


func test_stand_ins_are_cached() -> void:
	CardArt.clear_cache()
	var card := _card(&"heavy_spin")
	await get_tree().process_frame
	var a := CardArt.texture_for(card, 0, 88.0)
	var b := CardArt.texture_for(card, 0, 90.0)
	assert_not_null(a)
	assert_eq(a, b, "one render per card key and height bucket")
	assert_eq(CardArt.texture_for(_card(&"whirl"), 0, 88.0), a, "cards of a family share the base print")


# --- 4. No truncation (6.3, 4.3.3) ----------------------------------------------------------------

## The words of `text` in order (a line break is a space).
func _words(text: String) -> PackedStringArray:
	return text.replace("\n", " ").split(" ", false)


## Asserts `lines` hold exactly `text`'s words, whole, with no ellipsis.
func _whole(lines: PackedStringArray, text: String, what: String) -> void:
	for l in lines:
		assert_false(l.contains("…"), "%s: no ellipsis in '%s'" % [what, l])
	assert_eq(" ".join(lines).split(" ", false), _words(text), "%s: every word, whole (no mid-word break)" % what)


func test_no_ellipsis_and_no_mid_word_break_on_any_card_at_any_scale() -> void:
	var src := FileAccess.get_file_as_string("res://scripts/ui/kit/zine_card.gd")
	assert_false(src.contains("\"…\""), "no ellipsis path left in zine_card.gd")
	for s in SCALES:
		for card in _cards():
			for full in [false, true]:
				var z := _sticker(card, s, full)
				z.size.y = z.needed_height()  # the tall mode, as _refit_tall grows it
				var L := z.face_layout()
				var what := "%s x%.1f %s" % [card.id, s, "full" if full else "compact"]
				_whole(L["title_lines"], TextDb.t(card, "display_name").to_upper(), what + " title")
				assert_true(ZineCard.lines_fit(Palette.display(), L["title_lines"], (L["title"] as Rect2).size.x, int(L["title_fs"])), what + ": title inside the card")
				assert_true(int(L["title_fs"]) >= UiTheme.font_px_at(UiTheme.CAPTION, s), what + ": title never under caption")
				if full:
					assert_true(bool(L["fits"]), what + ": the whole face fits")
					_whole(L["rules_lines"], TextDb.t(card, "description"), what + " rules")
					assert_true(int(L["rules_fs"]) >= UiTheme.font_px_at(UiTheme.CAPTION, s), what + ": rules never under caption")
					assert_true((L["rules"] as Rect2).end.y <= z.size.y + 0.5, what + ": rules inside the card")
					assert_true(z.text_whole(), what + ": text_whole")
				z.free()


func test_the_detail_card_fits_every_card_without_growing_at_1_0() -> void:
	for card in _cards():
		var z := ZineCard.new(TextDb.t(card, "display_name"), card.ram_cost, TextDb.t(card, "description"), 0).with_card(card).as_detail(1.0)
		z.size = z.custom_minimum_size
		var L := z.face_layout()
		assert_true(bool(L["fits"]), "%s: the detail card holds every word" % card.id)
		assert_eq(int(L["rules_step"]), UiTheme.BODY, "%s: detail rules at body" % card.id)
		assert_almost_eq((L["art"] as Rect2).size.x / (L["art"] as Rect2).size.y, ZineCard.ART_ASPECT, 0.02, "%s: the whole 3:2 art" % card.id)
		z.free()


func test_the_deck_view_shows_whole_cards() -> void:
	var deck: Array[StringName] = [&"hot_patch", &"mirror_flip", &"overdrive", &"jolt"]
	var lookup := ContentLookup.new()
	for id in deck:
		lookup.add(_card(id))
	for s in [1.0, Settings.TEXT_SCALE_MAX]:
		Settings.set_text_scale(s)
		var view := DeckView.new(deck, lookup)
		add_child_autofree(view)
		await get_tree().process_frame
		await get_tree().process_frame
		await get_tree().process_frame
		for i in deck.size():
			var z := view.card(i)
			assert_true(z.fit_whole, "the deck view shows the full face")
			assert_true(z.text_whole(), "%s x%.1f: the whole text shows" % [deck[i], s])
	Settings.set_text_scale(1.0)
