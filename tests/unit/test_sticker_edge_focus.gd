extends GutTest
## M14 parity STICKER_EDGE (designer 2026-10-05): (1) the die-cut edge of every lettered sticker is
## proportional to its lettering and inside the concept's range (round 33 ui31.sticker: border 12 px on
## the 1920 board; edge / body height 0.08 for the title's hero verbs up to 0.27 for CANCEL at 28 px);
## (2) focus on EVERY sticker kind is the PEEL-BACK only (lift and corner curl), the sticker keeping its
## fill, no lime halo or brackets and NO rainbow (designer 2026-10-06, B1d: the rainbow sweep is the one
## scheduled sweep, see test_sticker_sweep_scheduler); under reduce effects the curl is the end state.

## The concept's edge / body-height range for lettered stickers.
const CONCEPT_MIN := 0.07
const CONCEPT_MAX := 0.28
## Round 33's baked stickers (tools/art/bake_menus_r33.py): the board border and the lettering sizes
## the concept drew them at (BREACH 60, CANCEL 50, BURN IT / DELETE 58, the title words 54 / 66).
const BAKED_BORDER := 12.0
const BAKED_SIZES: Array[float] = [50.0, 54.0, 58.0, 60.0, 66.0]
const CAP_SHARE := 0.74
## Lettering steps a sticker is built at (menu size to hero) and the text scales.
const STEPS: Array[int] = [14, 20, 28, 40, 64, 96]
const SCALES: Array[float] = [1.0, 1.6, 2.0]

var _saved: Dictionary


func before_each() -> void:
	_saved = Settings.to_dict()


func after_each() -> void:
	Settings.restore(_saved)


func _frames(n: int = 3) -> void:
	for i in n:
		await get_tree().process_frame


func _ratio(v: VinylSticker) -> float:
	return v.edge() / maxf(1.0, v.body_rect.size.y)


func test_the_lettered_vinyl_edge_is_proportional_and_in_the_concept_range() -> void:
	for scale in SCALES:
		Settings.set_text_scale(scale)
		for step in STEPS:
			var v := VinylSticker.new()
			v.shape = VinylSticker.Shape.WORD
			v.text = "OPTIONS"
			v.font_step = step
			add_child_autofree(v)
			await _frames(1)
			var r := _ratio(v)
			assert_between(r, CONCEPT_MIN, CONCEPT_MAX, "step %d at x%s: edge %.1f / body %.1f = %.3f" % [step, scale, v.edge(), v.body_rect.size.y, r])
			if step <= 28:
				assert_lte(v.edge(), float(v.font_step) * scale * VinylSticker.EDGE_SHARE + 1.0, "a menu sticker's edge follows its lettering")


func test_every_drawn_sticker_kind_uses_the_proportional_edge() -> void:
	var kinds := {}
	var h := HoloSticker.word("QUIT", VinylSticker.Fill.WHITE, 1.0, 22)
	add_child_autofree(h)
	kinds["HoloSticker.word"] = h.sticker
	var vs := VerbSticker.new("RESUME", VerbSticker.Fill.PINK, 34.0)
	add_child_autofree(vs)
	kinds["VerbSticker (kit)"] = vs
	var rs := RaidSticker.new("START DEFENSE")
	add_child_autofree(rs)
	kinds["RaidSticker"] = rs
	await _frames(3)
	for k in kinds:
		var node: Node = kinds[k]
		var v: VinylSticker = node as VinylSticker if node is VinylSticker else (node.get("vinyl") as VinylSticker)
		assert_not_null(v, "%s draws the kit's vinyl" % k)
		if v != null and v.is_inside_tree():
			assert_lt(v.border_px, 0.0, "%s: no fixed edge (automatic: proportional)" % k)
			assert_between(_ratio(v), CONCEPT_MIN, CONCEPT_MAX, "%s: edge / height %.3f" % [k, _ratio(v)])


func test_the_baked_stickers_have_the_thin_proportional_edge() -> void:
	# tools/art/bake_menus_r33.py: border = EDGE_SHARE x the lettering (board px, capped at the concept's 12), the
	# same share as the drawn stickers' (VinylSticker.EDGE_SHARE).
	for size in BAKED_SIZES:
		var edge := minf(roundf(VinylSticker.EDGE_SHARE * size), BAKED_BORDER)
		var r := edge / (size * CAP_SHARE + edge * 2.0)
		assert_between(r, CONCEPT_MIN, CONCEPT_MAX, "the bake at lettering %d: edge %.0f, ratio %.3f" % [int(size), edge, r])
		assert_lt(edge, BAKED_BORDER, "thinner than the concept's fixed 12 at lettering %d" % int(size))
	# The files really are the thin bakes: the opaque body of a baked sticker (2x board px) is its lettering block
	# (measured: base 120 for CANCEL at 50, 138 for BREACH at 60) plus 4 x the border (both sides, at 2x).
	var cases := {"dialog_cancel": [50.0, 120.0], "breach": [60.0, 138.0], "dialog_burn_it": [58.0, 134.0]}
	for key in cases:
		var size: float = cases[key][0]
		var base_h: float = cases[key][1]
		var tex := load(VerbSticker.ART_DIR + key + ".png") as Texture2D
		assert_not_null(tex, "%s is baked" % key)
		var img := tex.get_image()
		var top := -1
		var bottom := -1
		for y in img.get_height():
			for x in range(0, img.get_width(), 2):
				if img.get_pixel(x, y).a > 0.78:
					if top < 0:
						top = y
					bottom = y
					break
		var edge := minf(roundf(VinylSticker.EDGE_SHARE * size), BAKED_BORDER)
		assert_almost_eq(float(bottom - top + 1), base_h + 4.0 * edge, 8.0, "%s: the body is the thin bake's height (edge %.0f)" % [key, edge])
	for key in ["overthrow", "simulate", "title_options", "title_paused", "title_campaign_slots", "dialog_delete"]:
		assert_true(ResourceLoader.exists(VerbSticker.ART_DIR + key + ".png"), "%s is baked" % key)


func test_focus_on_the_kit_sticker_is_the_peel_back_and_no_rainbow() -> void:
	for fill in [VinylSticker.Fill.PINK, VinylSticker.Fill.RED, VinylSticker.Fill.YELLOW, VinylSticker.Fill.WHITE, VinylSticker.Fill.INK, VinylSticker.Fill.HOLO]:
		var v := VinylSticker.new()
		v.shape = VinylSticker.Shape.WORD
		v.text = "GO"
		v.fill = fill
		add_child_autofree(v)
		await _frames(1)
		assert_eq(v.rainbow, 0.0, "fill %d at rest: the plain gloss" % fill)
		v.set_state(VinylSticker.State.HOVER)
		v.complete_motion()
		assert_eq(v.rainbow, 0.0, "fill %d focused: no rainbow" % fill)
		assert_eq(v.gloss_k, VinylSticker.GLOSS_REST, "fill %d focused: the rest gloss, no sweep" % fill)
		assert_false(v.sweep_running(), "focus starts no sweep")
		assert_eq(v.peel_back, 1.0, "fill %d focused: the corner curls" % fill)
		assert_eq(v.fill, fill, "the sticker keeps its own fill")
		assert_eq((v._mat.get_shader_parameter(&"rainbow") as float), 0.0, "the shader gets none")
		v.set_state(VinylSticker.State.REST)
		v.complete_motion()
		assert_eq(v.rainbow, 0.0, "back to the plain gloss at rest")
		assert_eq(v.fold, 0.0)
		assert_eq(v.peel_back, 0.0, "the peel-back lets go")


func test_the_curl_end_state_under_reduce_effects() -> void:
	Settings.set_reduce_effects(true)
	var v := VinylSticker.new()
	v.shape = VinylSticker.Shape.WORD
	v.text = "GO"
	add_child_autofree(v)
	await _frames(1)
	v.set_state(VinylSticker.State.HOVER)
	assert_eq(v.rainbow, 0.0)
	assert_eq(v.gloss_k, VinylSticker.GLOSS_REST, "the rest gloss is the static sheen")
	assert_eq(v.peel_back, 1.0, "the curl: focus reads without colour")
	assert_false(v.motion_running(), "nothing moves")


func test_focus_on_every_sticker_wrapper_reaches_the_vinyl_or_the_shader() -> void:
	# HoloSticker (pause rows, LEAVE ...): focus -> the vinyl's HOVER.
	var h := HoloSticker.word("OPTIONS", VinylSticker.Fill.YELLOW, 1.0, 22)
	add_child_autofree(h)
	# VerbSticker: kit (PINK), baked art, drawn (BLUE).
	var kit := VerbSticker.new("RESUME", VerbSticker.Fill.PINK, 34.0)
	add_child_autofree(kit)
	var art := VerbSticker.new("CANCEL", VerbSticker.Fill.YELLOW, 50.0, 0.0, "")
	art.art_key = "dialog_cancel"
	art._load_art()
	art._fit()
	add_child_autofree(art)
	var drawn := VerbSticker.new("OVERTHROW", VerbSticker.Fill.BLUE, 40.0)
	add_child_autofree(drawn)
	var raid := RaidSticker.new("START DEFENSE")
	add_child_autofree(raid)
	await _frames(3)
	for b: Button in [h, kit, art, drawn, raid]:
		b.grab_focus()
		await _frames(2)
		assert_true(b.has_focus(), "%s takes focus" % b.name)
	for b: Button in [h, kit, art, drawn, raid]:
		b.grab_focus()
		await _frames(2)
		var v: VinylSticker = b.get("vinyl") as VinylSticker
		if b is HoloSticker:
			v = (b as HoloSticker).sticker
		if v != null:
			assert_eq(v.state, VinylSticker.State.HOVER, "%s: focus puts the vinyl in HOVER (the peel-back)" % b.get_class())
			assert_eq(v.rainbow, 0.0)
		else:
			assert_ne((b.get("_mat") as ShaderMaterial).get_shader_parameter(&"rainbow"), 1.0, "%s: the drawn sticker's shader runs no rainbow on focus" % b.get("art_key"))
			assert_true(bool(b.get("_focused")), "and the curl is drawn")
	art.release_focus()
	await _frames(2)
	assert_not_null(art.vinyl, "B5 follow-up 1: the baked art is shown by a kit sticker")
	assert_eq(art.vinyl.state, VinylSticker.State.REST, "off focus: no curl")
