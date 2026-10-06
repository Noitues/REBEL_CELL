extends GutTest
## M14 B1c (integration review D17, D23; ART_BIBLE v2 §1.2): the finished CRT terminal and
## decrypted holo materials, as shader and kit defaults. The faint scrolling hex dump at 6 %
## is on every terminal glass (the kit's CrtTerminalPanel and the shared crt_panel material);
## the holo has its 78 % tint, 4 px scanlines at 12 %, three slow bands at 6 s, the +-2 px edge
## split, a 0.88 scrim right behind it and the cracked seal under the DECRYPTED stamp; words
## keep their contrast on both, with the dump and the bands at their brightest, on every skin.

const CRT_PANEL := "res://shaders/crt_panel.gdshader"
const CRT_TERMINAL := "res://shaders/kit/crt_terminal.gdshader"
const HEX_INC := "res://shaders/kit/hex_dump.gdshaderinc"
const HOLO := "res://shaders/kit/decrypted_holo.gdshader"
const CORPS: Array[StringName] = [&"halcyon", &"meridian", &"solace", &"orbital"]
## The holo's glass grade toward its foot (decrypted_holo.gdshader: the tint share falls to 70 %).

var _saved: Dictionary = {}


func before_each() -> void:
	_saved = Settings.snapshot()


func after_each() -> void:
	Settings.restore(_saved)
	Motion.force_live = false


func _src(path: String) -> String:
	return FileAccess.get_file_as_string(path)


# --- D23: the hex dump on every terminal ----------------------------------------------------

func test_the_shared_hex_dump_defaults_to_6_percent_in_both_terminal_shaders() -> void:
	assert_string_contains(_src(HEX_INC), "uniform float hexdump : hint_range(0.0, 1.0) = 0.06;", "hexdump = 0.06 by default")
	for path in [CRT_PANEL, CRT_TERMINAL]:
		assert_string_contains(_src(path), "#include \"%s\"" % HEX_INC, "%s shares the dump" % path)
		assert_string_contains(_src(path), "rc_hex_dump(", "%s draws it" % path)
	assert_string_contains(_src(HEX_INC), "rc_time(TIME)", "it scrolls on rc_time: reduce effects hold it still")


func test_the_kit_crt_panel_has_the_dump_on_by_default() -> void:
	var p := CrtTerminalPanel.new()
	p.size = Vector2(300, 120)
	add_child_autofree(p)
	var mat := p.material as ShaderMaterial
	assert_almost_eq(p.hex_alpha(), 0.06, 0.0001, "hex dump at 6 %")
	assert_eq(mat.get_shader_parameter(&"hex_atlas"), CrtTerminalPanel.HEX_ATLAS, "the baked mono 0-F atlas")
	var cell := mat.get_shader_parameter(&"hex_cell") as Vector2
	var k := CrtTerminalPanel.HEX_GLYPH_PX / 64.0
	assert_almost_eq(cell.y, Palette.mono().get_height(64) * k, 0.01, "rows one HEX_GLYPH_PX line high")
	assert_almost_eq(cell.x, Palette.mono().get_char_size(ord("0"), 64).x * k, 0.01, "one mono advance per character")
	assert_eq(mat.get_shader_parameter(&"hex_tint"), p.accent(), "in the accent colour")
	p.hex_dump = false
	assert_almost_eq(p.hex_alpha(), 0.0, 0.0001, "a panel may still switch it off")


func test_every_terminal_glass_carries_the_dump_by_default() -> void:
	var owner := Control.new()
	add_child_autofree(owner)
	assert_true(HudSkin.crt_backing(owner).hex_dump, "HudSkin.crt_backing (chips, gauges)")
	var w: CrtWindow = add_child_autofree(CrtWindow.new("X"))
	assert_true(w.glass.hex_dump, "CrtWindow")
	var t: CrtText = add_child_autofree(CrtText.new("CODEX"))
	assert_true(t.glass.hex_dump, "CrtText (codex, stats, history)")
	var strip: RaidSpeedStrip = add_child_autofree(RaidSpeedStrip.new())
	assert_true(strip.crt.hex_dump, "the raid's speed strip")
	var mat := UiTheme.crt_material()
	assert_almost_eq(float(mat.get_shader_parameter(&"hexdump")), 0.06, 0.0001, "the shared crt_panel material")
	assert_eq(mat.get_shader_parameter(&"hex_atlas"), CrtTerminalPanel.HEX_ATLAS)


func test_no_view_switches_the_dump_off() -> void:
	var re := RegEx.create_from_string("hex_dump\\s*=\\s*false|^\\s*hex\\s*=\\s*false|crt_backing\\([^)]*,\\s*false")
	for path in _scripts("res://scripts"):
		for line in _src(path).split("\n"):
			assert_null(re.search(line), "%s: %s" % [path, line.strip_edges()])


func test_the_dump_scrolls_only_while_its_motion_is_live() -> void:
	var p := CrtTerminalPanel.new()
	add_child_autofree(p)
	var mat := p.material as ShaderMaterial
	assert_almost_eq(float(mat.get_shader_parameter(&"hex_scroll")), 0.0, 0.0001, "headless: still")
	Motion.force_live = true
	Settings.reduce_effects = false
	p._sync()
	assert_almost_eq(float(mat.get_shader_parameter(&"hex_scroll")), Motion.amplitude(CrtTerminalPanel.HEX), 0.0001, "crt_hex_scroll's px/s")
	Settings.reduce_effects = true
	p._sync()
	assert_almost_eq(float(mat.get_shader_parameter(&"hex_scroll")), 0.0, 0.0001, "reduce effects: it holds still")


# --- B1c-b: the dump reads as texture, never as text ------------------------------------------

func test_the_dump_glyphs_are_a_fixed_small_size_at_every_text_scale() -> void:
	assert_almost_eq(CrtTerminalPanel.HEX_GLYPH_PX * 1.5, 11.0, 0.01, "about 11 px on a 1080p screen")
	var cells: Array[Vector2] = []
	for scale in [1.0, 1.6, 2.0]:
		Settings.text_scale = scale
		var p := CrtTerminalPanel.new()
		add_child_autofree(p)
		cells.append((p.material as ShaderMaterial).get_shader_parameter(&"hex_cell"))
	assert_eq(cells[1], cells[0], "text 1.6 keeps the glyph size")
	assert_eq(cells[2], cells[0], "text 2.0 keeps the glyph size")
	assert_lt(cells[0].y, float(UiTheme.font_px_at(UiTheme.CAPTION, 1.0)), "smaller than the smallest words")


func test_the_dump_effective_alpha_is_6_percent_and_halves_under_words() -> void:
	var p := CrtTerminalPanel.new()
	p.size = Vector2(320, 120)
	add_child_autofree(p)
	var l := Label.new()
	l.text = "CAN BE YOUR NODE"
	l.position = Vector2(20, 30)
	l.size = Vector2(200, 20)
	p.content.add_child(l)
	p.refresh_text_mask()
	var mat := p.material as ShaderMaterial
	# effective alpha = hexdump x the glyph's coverage (at most 1): 6 % at a glyph's core
	assert_almost_eq(float(mat.get_shader_parameter(&"hexdump")), 0.06, 0.0001, "6 % effective at most")
	assert_almost_eq(float(mat.get_shader_parameter(&"hex_text_fade")), 0.5, 0.0001, "x0.5 under a line of words")
	assert_eq(int(mat.get_shader_parameter(&"hex_text_count")), 1, "the label's rect is handed to the shader")
	var r: Vector4 = (mat.get_shader_parameter(&"hex_text_rects") as PackedVector4Array)[0]
	assert_eq(r, Vector4(l.position.x, l.position.y, l.position.x + l.size.x, l.position.y + l.size.y), "panel-local, x0 y0 x1 y1")
	assert_string_contains(_src(HEX_INC), "fade = hex_text_fade;", "the shader fades the dump inside those rects")
	var w: CrtWindow = add_child_autofree(CrtWindow.new("SITE"))
	assert_eq(w.glass.text_scope, w, "a window's own words fade its glass's dump")


func test_the_dump_scrolls_slowly() -> void:
	assert_lte(Motion.entry(CrtTerminalPanel.HEX).amplitude, 6.0, "6 px/s at most")


# --- D17: the holo ----------------------------------------------------------------------------

func test_the_holo_uniforms_are_the_reviews() -> void:
	Settings.reduce_effects = false
	var h := DecryptedHoloPanel.new()
	h.corp_color = Palette.CORP_MERIDIAN  # B4: the measured shares are round 44's Meridian file's
	h.size = Vector2(300, 200)
	add_child_autofree(h)
	var mat := h.get_child(1, true).material as ShaderMaterial
	assert_almost_eq(float(mat.get_shader_parameter(&"tint_share")), 0.78, 0.0001, "corp tint at 78 % on the words and edge")
	assert_almost_eq(float(mat.get_shader_parameter(&"fill_share")), 0.15, 0.0001, "the body: the tint at 15 % over the dark glass (measured on round 44)")
	assert_almost_eq(float(mat.get_shader_parameter(&"glass_alpha")), 0.88, 0.0001, "the body's dark glass at 0.88")
	assert_string_contains(_src(HOLO), "vec3 e = vec3(er, eg, eb) * tint.rgb;", "the full tint on the edge")
	assert_string_contains(_src(HOLO), "col = vec4(tint.rgb, scan_strength * line);", "the full tint on the scanlines")
	assert_eq(DecryptedHoloPanel.ink(Palette.CORP_MERIDIAN), Palette.TEXT_HI.lerp(Palette.CORP_MERIDIAN, 0.78), "the words: the tint at 78 %")
	assert_almost_eq(float(mat.get_shader_parameter(&"scan_px")), 4.0, 0.0001, "4 px scanlines")
	assert_almost_eq(float(mat.get_shader_parameter(&"scan_strength")), 0.12, 0.0001, "at 12 %")
	assert_almost_eq(float(mat.get_shader_parameter(&"band_count")), 3.0, 0.0001, "three bands")
	assert_almost_eq(Motion.entry(DecryptedHoloPanel.BANDS).duration, 6.0, 0.0001, "one slow pass in 6 s")
	assert_almost_eq(float(mat.get_shader_parameter(&"band_seconds")), Motion.seconds(DecryptedHoloPanel.BANDS), 0.0001)
	assert_almost_eq(float(mat.get_shader_parameter(&"split_px")), 2.0, 0.0001, "+-2 px RGB split")
	assert_string_contains(_src(HOLO), "// the edge in three channels, split +-split_px horizontally (edge only)", "the split is on the edge only")
	assert_almost_eq(Palette.HOLO_SCRIM.a, 0.88, 0.0001, "the scrim at 0.88")
	assert_true(h.backing, "the 0.88 scrim right behind the plate by default")
	for k in ["scan_strength : hint_range(0.0, 1.0) = 0.12", "band_count = 3.0", "band_seconds = 6.0", "tint_share : hint_range(0.0, 1.0) = 0.78", "fill_share : hint_range(0.0, 1.0) = 0.15", "glass_alpha : hint_range(0.0, 1.0) = 0.88"]:
		assert_string_contains(_src(HOLO), k, "shader default %s" % k)


func test_the_cracked_seal_sits_under_the_decrypted_stamp() -> void:
	var h := DecryptedHoloPanel.new()
	h.size = Vector2(320, 220)
	h.corporation = &"halcyon"
	add_child_autofree(h)
	assert_eq(h.seal_center(), h.stamp_slot.size * 0.5, "the seal is centred under the stamp")
	assert_not_null(CorpSeal.emblem(&"halcyon"), "the corp's own emblem (art-pass export)")
	assert_eq(DecryptedHoloPanel.FRACTURE.size(), 5, "ui21 seal_overlay's fracture")
	assert_eq(DecryptedHoloPanel.STAMP_COLOR, Palette.CELL_ACID, "the concepts' green DECRYPTED: the Cell's acid")
	assert_eq(DecryptedHoloPanel.STAMP_SHADOW_OFFSET, Vector2(2, 2), "a 2 px under-shadow")
	assert_eq(DecryptedHoloPanel.stamp_shadow_color(), Color(Palette.INK, 0.7), "dark ink at 70 %")
	for corp in CORPS:
		var tint := RaidSkin.of(corp).hue
		var body := _holo_body(tint, 0.0)
		var under := body.lerp(Palette.INK, 0.7)
		assert_gt(Palette.contrast(Palette.CELL_ACID, under), Palette.contrast(Palette.CELL_ACID, body) - 0.001, "%s: the shadow only adds contrast" % corp)
		assert_gt(Palette.contrast(Palette.CELL_ACID, under), 7.0, "%s: the acid stamp reads on its shadow" % corp)
	var holo := RaidHolo.new(&"meridian", "THREAT INTEL // SCAN", "7F-A2")
	add_child_autofree(holo)
	assert_eq(holo.holo.corporation, &"meridian", "THREAT INTEL's seal is the raiding corp's")


func test_the_holo_bands_hold_still_under_reduce_effects() -> void:
	Motion.force_live = true
	Settings.reduce_effects = true
	var h := DecryptedHoloPanel.new()
	add_child_autofree(h)
	var mat := h.get_child(1, true).material as ShaderMaterial
	assert_almost_eq(float(mat.get_shader_parameter(&"split_px")), 0.0, 0.0001, "no RGB split")
	assert_string_contains(_src(HOLO), "rc_time(TIME)", "the bands roll on rc_time (frozen under reduce effects)")


# --- Contrast on both, every skin ---------------------------------------------------------------

func _brighter(a: Color, b: Color) -> Color:
	return a if Palette.luminance(a) >= Palette.luminance(b) else b


func test_terminal_words_read_over_the_hex_dump_on_every_skin() -> void:
	for skin in PaletteSkins.IDS:
		Settings.palette_skin = skin
		var night := Palette.NIGHT_SKY
		var kit_glass := Palette.over(night, _brighter(PaletteSkins.chrome(Palette.CRT_GLASS_TOP), PaletteSkins.chrome(Palette.CRT_GLASS_BOTTOM)))
		var old_glass := Palette.over(night, PaletteSkins.resolve(skin, &"TERMINAL_BG"))
		var p := CrtTerminalPanel.new()
		add_child_autofree(p)
		for kind in CrtTerminalPanel.Accent.values():
			p.accent_kind = kind
			var lit := kit_glass.lerp(p.accent(), CrtTerminalPanel.HEX_ALPHA)
			assert_gt(Palette.contrast(PaletteSkins.chrome(Palette.TERMINAL_TEXT), lit), 7.0, "%s kit glass, accent %d: terminal text over a dump glyph" % [skin, kind])
		var lit_old := old_glass.lerp(PaletteSkins.chrome(Palette.NET_CYAN), CrtTerminalPanel.HEX_ALPHA)
		assert_gt(Palette.contrast(PaletteSkins.resolve(skin, &"TEXT_HI"), lit_old), 7.0, "%s crt_panel glass: TEXT_HI over a dump glyph" % skin)
		assert_gt(Palette.contrast(PaletteSkins.resolve(skin, &"TERMINAL_TEXT"), lit_old), 7.0, "%s crt_panel glass: TERMINAL_TEXT over a dump glyph" % skin)
		assert_gt(Palette.contrast(PaletteSkins.resolve(skin, &"TEXT_MID"), lit_old), 4.5, "%s crt_panel glass: TEXT_MID over a dump glyph" % skin)


## The holo body's colour for `tint` with a band of strength `band` passing: the tint at
## FILL_SHARE over the deep (its top, the brightest) at 0.88 over the 0.88 scrim over the night.
func _holo_body(tint: Color, band: float) -> Color:
	var g := Palette.NET_BG_OUTER.lerp(tint, DecryptedHoloPanel.FILL_SHARE)
	var behind := Palette.over(Palette.NIGHT_SKY, Palette.HOLO_SCRIM)
	var glass := Palette.over(behind, Color(g, DecryptedHoloPanel.GLASS_ALPHA))
	return glass.lerp(tint, band)


func test_the_holo_body_is_dark_and_the_tint_is_on_the_words() -> void:
	for corp in CORPS:
		var tint := RaidSkin.of(corp).hue
		var body := _holo_body(tint, 0.0)
		assert_lt(Palette.luminance(body), 0.06, "%s: the body is dark glass" % corp)
		assert_gt(Palette.luminance(DecryptedHoloPanel.ink(RaidSkin.of(corp).holo)), Palette.luminance(body) * 5.0, "%s: the words carry the tint, bright" % corp)


func test_holo_words_read_on_the_holo_at_its_brightest_on_every_skin() -> void:
	var band := Motion.entry(DecryptedHoloPanel.BANDS).amplitude
	for skin in PaletteSkins.IDS:
		Settings.palette_skin = skin
		for corp in CORPS:
			var rs := RaidSkin.of(corp)
			var peak := _holo_body(rs.hue, band)  # a band passing, off the scanline
			var holo := RaidHolo.new(corp, "THREAT INTEL // SCAN", "7F-A2")
			add_child_autofree(holo)
			var line := holo.add_line("HAULER + COURIER")
			var words := line.get_theme_color(&"font_color")
			assert_gt(Palette.contrast(words, peak), 4.5, "%s %s: holo words under a band" % [skin, corp])
			assert_gt(Palette.contrast(Palette.TEXT_HI, peak), 7.0, "%s %s: TEXT_HI on the holo" % [skin, corp])


func _scripts(dir: String) -> Array[String]:
	var out: Array[String] = []
	var d := DirAccess.open(dir)
	if d == null:
		return out
	for f in d.get_files():
		if f.ends_with(".gd"):
			out.append(dir.path_join(f))
	for sub in d.get_directories():
		out.append_array(_scripts(dir.path_join(sub)))
	return out
