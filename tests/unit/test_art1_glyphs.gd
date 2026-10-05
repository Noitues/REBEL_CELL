extends GutTest
## ART-1 1C: the glyph atlas and its id -> glyph table (ART_BIBLE 3.5, 5.2, 6.2): every slice
## type, status, pictogram, hub, inner-ring segment, Firmware, Daemon and Exploit the game has
## maps to a glyph; ids without art map to the stand-in and are listed for the designer; the
## 16 px rule holds over the whole atlas; the shader takes its colours from Palette.

const MANIFEST := "res://assets/glyphs/glyph_atlas_manifest.json"
const ATLAS_PNG := "res://assets/glyphs/glyph_atlas.png"

var _t: GlyphTableData


func before_all() -> void:
	_t = GlyphTableData.shipped()


func _content_of(class_name_: StringName) -> Array[Resource]:
	var out: Array[Resource] = []
	for id in ContentRegistry.all_ids():
		var r: Resource = ContentRegistry.get_content(id)
		if r != null and r.get_script() != null and r.get_script().get_global_name() == class_name_:
			out.append(r)
	return out


## Asserts `key` maps to a real glyph (the stand-in counts only where `pending_ok`).
func _assert_mapped(key: StringName, pending_ok: bool = false) -> void:
	var g := _t.glyph_for(key)
	assert_ne(g, &"", "%s has a glyph" % key)
	assert_true(_t.cell_of(g) >= 0, "%s -> %s is an atlas cell" % [key, g])
	if not pending_ok:
		assert_ne(g, GlyphTableData.PENDING, "%s has real art" % key)


func test_the_shipped_table_validates() -> void:
	assert_not_null(_t)
	assert_eq(_t.validate(), PackedStringArray())


func test_the_table_matches_the_atlas_build_manifest() -> void:
	var m: Dictionary = JSON.parse_string(FileAccess.get_file_as_string(MANIFEST))
	var names := PackedStringArray()
	for g in m["glyphs"]:
		names.append(String(g["name"]))
	assert_eq(_t.glyph_names, names, "the table lists the atlas cells in build order")
	assert_eq(_t.cell_px, int(m["cell_px"]))
	assert_eq(_t.box_px, int(m["box_px"]))
	assert_eq(_t.spread_px, int(m["spread_px"]))
	assert_eq(_t.columns, int(m["columns"]))
	assert_eq(String(m["source_tag"]), "art-concepts-r43")


func test_cells_follow_the_round_17_index_with_program_names_and_no_placeholders() -> void:
	var first := PackedStringArray(["slice_shim", "slice_overflow", "slice_defrag", "slice_sandbox", "slice_detour",
		"slice_hotfix", "slice_infect", "slice_trojan", "slice_null", "special_priority"])
	assert_eq(_t.glyph_names.slice(0, first.size()), first)
	for n in _t.glyph_names:
		assert_false(n.begins_with("placeholder"), n)
		for old in ["exploit_slice", "zero_day", "firewall", "proxy", "patch", "virus", "judge" + "ment"]:
			assert_false(n.begins_with("slice_" + old) or n == "special_" + old, "%s carries an old program name" % n)


func test_every_slice_type_has_a_glyph() -> void:
	for t in RC.SliceType.values():
		_assert_mapped(GlyphTableData.key_for_slice_type(t))
	assert_eq(_t.glyph_for(GlyphTableData.key_for_slice_type(RC.SliceType.SANDBOX)), &"slice_sandbox")
	assert_eq(_t.glyph_for(GlyphTableData.key_for_slice_type(RC.SliceType.NULL)), &"slice_null")


func test_every_slice_in_content_has_a_glyph_and_specials_have_their_own() -> void:
	var slices := _content_of(&"SliceData")
	assert_true(slices.size() > 20)
	for s in slices:
		var g := _t.glyph_for_slice(s as SliceData)
		assert_true(_t.cell_of(g) >= 0, "slice %s has a glyph" % s.id)
	var own := {&"priority": &"special_priority", &"citation": &"special_citation", &"dose": &"special_dose",
		&"solar_flare": &"special_solar_flare", &"shim_8_weight": &"special_weight"}
	for id in own:
		assert_eq(_t.glyph_for_slice(ContentRegistry.get_content(id) as SliceData), own[id], String(id))
	# Drain variants keep their type glyph (bible 3.4).
	assert_eq(_t.glyph_for_slice(ContentRegistry.get_content(&"overflow_12_drain") as SliceData), &"slice_overflow")


func test_every_corporation_program_word_has_a_glyph() -> void:
	for corp in Palette.CORP_SLICE_WORDS:
		var words: Dictionary = Palette.CORP_SLICE_WORDS[corp]
		for type in words:
			var key := GlyphTableData.key_for_word(String(words[type]))
			_assert_mapped(key)
			# Round 18 kits: the corporation's program keeps its type's glyph; the screen differs.
			assert_eq(_t.glyph_for(key), _t.glyph_for(GlyphTableData.key_for_slice_type(type)), String(key))
	_assert_mapped(&"satellite")


func test_every_status_has_a_glyph() -> void:
	for s in RC.Status.values():
		if s != RC.Status.NONE:
			_assert_mapped(GlyphTableData.key_for_status(s))


func test_every_card_pictogram_has_a_glyph_or_is_listed_for_the_designer() -> void:
	var decisions := FileAccess.get_file_as_string("res://docs/DECISIONS.md")
	var open_q := decisions.substr(decisions.find("## Open questions for the designer"))
	for e in RC.EffectType.values():
		var key := GlyphTableData.key_for_effect(e)
		_assert_mapped(key, true)
		if _t.is_pending(key):
			assert_true(open_q.contains("`%s`" % key), "%s (no art yet) is listed under the open questions" % key)
	_assert_mapped(&"effect_spin_ccw")
	_assert_mapped(&"effect_nudge_inner")


func test_only_the_listed_ids_wait_for_art() -> void:
	var pending: Array[String] = []
	for k in _t.ids:
		if _t.is_pending(k):
			pending.append(String(k))
	pending.sort()
	assert_eq(pending, ["effect_custom", "effect_gain_cycles", "effect_gain_schematics", "effect_modify_heat"] as Array[String])


func test_every_hub_core_has_a_glyph() -> void:
	var hubs := _content_of(&"HubCoreData")
	assert_true(hubs.size() >= 22, "player cores, Mk2s and enemy hubs (%d)" % hubs.size())
	for h in hubs:
		_assert_mapped(StringName("hub_" + String(h.id)))
	# Mk2 = the same emblem (bible 3.3: the second rim and MK2 tab are drawn by the hub).
	assert_eq(_t.glyph_for(&"hub_rig_core_mk2"), _t.glyph_for(&"hub_rig_core"))


func test_every_inner_ring_segment_has_a_glyph() -> void:
	var segs := _content_of(&"RingSegmentData")
	assert_eq(segs.size(), 7)
	for s in segs:
		_assert_mapped(StringName(s.id))


func test_every_firmware_and_daemon_has_a_glyph() -> void:
	var fws := _content_of(&"FirmwareData")
	var ds := _content_of(&"DaemonData")
	assert_eq(fws.size(), 18)
	assert_eq(ds.size(), 24)
	for f in fws:
		_assert_mapped(StringName("firmware_" + String(f.id)))
	for d in ds:
		_assert_mapped(StringName("daemon_" + String(d.id)))


func test_every_exploit_type_has_a_glyph() -> void:
	for x in RC.ExploitType.values():
		if x != RC.ExploitType.NONE:
			_assert_mapped(GlyphTableData.key_for_exploit(x))
	assert_eq(_t.glyph_for(&"exploit_virus"), &"status_corrupted", "VIRUS shows the CORRUPTED glitch (round 38)")


## Coverage of every cell at `px` (the round 17 catalogue's metric: box-filtered coverage of
## the glyph box, then a 0.6 px Gaussian), from the distance field.
func _coverage_maps(px: int) -> Dictionary:
	var img := Image.load_from_file(ProjectSettings.globalize_path(ATLAS_PNG))
	assert_not_null(img)
	if img.get_format() != Image.FORMAT_L8:
		img.convert(Image.FORMAT_L8)
	var data := img.get_data()
	var w := img.get_width()
	var step := _t.box_px / px
	var margin := (_t.cell_px - _t.box_px) / 2
	var kernel := PackedFloat32Array()
	var ks := 0.0
	for i in range(-2, 3):
		var k := exp(-float(i * i) / (2.0 * 0.6 * 0.6))
		kernel.append(k)
		ks += k
	for i in kernel.size():
		kernel[i] /= ks
	var out := {}
	for c in _t.glyph_names.size():
		var name := StringName(_t.glyph_names[c])
		if name == GlyphTableData.PENDING:
			continue
		var ox := (c % _t.columns) * _t.cell_px + margin
		var oy := (c / _t.columns) * _t.cell_px + margin
		var cov := PackedFloat32Array()
		cov.resize(px * px)
		for by in px:
			for bx in px:
				var s := 0.0
				for y in step:
					var row := (oy + by * step + y) * w + ox + bx * step
					for x in step:
						var v := float(data[row + x]) / 255.0
						s += clampf((v - 0.5) * 2.0 * _t.spread_px + 0.5, 0.0, 1.0)
				cov[by * px + bx] = s / float(step * step)
		var tmp := PackedFloat32Array()
		tmp.resize(px * px)
		for y in px:
			for x in px:
				var a := 0.0
				for i in kernel.size():
					a += kernel[i] * cov[y * px + clampi(x + i - 2, 0, px - 1)]
				tmp[y * px + x] = a
		for y in px:
			for x in px:
				var a := 0.0
				for i in kernel.size():
					a += kernel[i] * tmp[clampi(y + i - 2, 0, px - 1) * px + x]
				cov[y * px + x] = a
		out[name] = cov
	return out


func test_the_16_px_rule_holds_over_the_whole_atlas() -> void:
	var maps := _coverage_maps(_t.twin_px)
	var names: Array = maps.keys()
	var exempt := {}
	for p in _t.twin_exceptions:
		var ab := p.split("|")
		exempt[ab[0] + "|" + ab[1]] = true
		exempt[ab[1] + "|" + ab[0]] = true
	var twins: Array[String] = []
	var worst := 0.0
	for i in names.size():
		var a: PackedFloat32Array = maps[names[i]]
		for j in range(i + 1, names.size()):
			var b: PackedFloat32Array = maps[names[j]]
			var lo := 0.0
			var hi := 0.0
			for k in a.size():
				lo += minf(a[k], b[k])
				hi += maxf(a[k], b[k])
			var iou := lo / maxf(hi, 0.000001)
			var key := "%s|%s" % [names[i], names[j]]
			if exempt.has(key):
				continue
			worst = maxf(worst, iou)
			if iou >= _t.twin_max_iou:
				twins.append("%s %.3f" % [key, iou])
	gut.p("16 px rule: worst non-exempt soft IoU %.3f over %d glyphs" % [worst, names.size()])
	for tw in twins:
		gut.p("  twin " + tw)
	assert_eq(twins, [] as Array[String], "glyph pairs that read alike at %d px" % _t.twin_px)


func test_the_shader_takes_its_colours_from_palette_and_its_geometry_from_the_table() -> void:
	assert_eq(Palette.GLYPH_INK, Color("#0C0A16"))
	assert_eq(Palette.GLYPH_FILL, Color("#FFFFFF"))
	assert_almost_eq(_t.outline_width, 0.075, 0.0001)
	var m := GlyphIcon.material_for(Palette.GLYPH_FILL, Palette.GLYPH_INK)
	assert_eq(m.get_shader_parameter(&"fill_color"), Palette.GLYPH_FILL)
	assert_eq(m.get_shader_parameter(&"outline_color"), Palette.GLYPH_INK)
	assert_almost_eq(float(m.get_shader_parameter(&"outline_width")), _t.outline_width, 0.0001)
	assert_almost_eq(float(m.get_shader_parameter(&"box_px")), float(_t.box_px), 0.0001)
	assert_almost_eq(float(m.get_shader_parameter(&"spread_px")), float(_t.spread_px), 0.0001)
	# The outline fits inside the cell margin and inside the field's range.
	assert_true(_t.outline_width * _t.box_px <= (_t.cell_px - _t.box_px) * 0.5)
	assert_true(_t.outline_width * _t.box_px < _t.spread_px)


func test_a_glyph_icon_sizes_its_cell_from_the_box() -> void:
	var g := GlyphIcon.make(&"slice_shim", 16.0)
	add_child_autofree(g)
	assert_almost_eq(g.size.x, 16.0 * _t.cell_px / _t.box_px, 0.01)
	assert_eq(_t.cell_region(&"slice_shim"), Rect2(0, 0, _t.cell_px, _t.cell_px))
	assert_eq(_t.cell_region(&"no_such_glyph"), Rect2())
	assert_eq(g.material, GlyphIcon.material_for(Palette.GLYPH_FILL, Palette.GLYPH_INK), "icons share one material per colour pair")
