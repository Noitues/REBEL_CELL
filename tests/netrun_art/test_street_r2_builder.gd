extends GutTest
## Street r2 renderer (P2 step 2): the builder is deterministic (same seed -> same node / mesh summary), the planned frontage is a continuous
## row along the street (a gap is at most one lot: a cross street), every sign word fits its texture in the Godot font metrics, and the
## old hero blade bars are gone from the street dressing when the r2 frontage is on.

const WORLDS: Array[String] = ["101", "105"]

static var _cache: Dictionary = {}


func _world(sn: String) -> Dictionary:
	if not _cache.has(sn):
		var w := NaFixture.load_inputs(sn)
		var d := NetrunArtDeriver.derive_street(w["city"], w["net"], w["run_graph"], w["site"], w["partial_street"])
		_cache[sn] = {"w": w, "d": d, "b": StreetR2Builder.build(w["city"], d, w["seed"])}
	return _cache[sn]


func after_all() -> void:
	for sn: String in _cache:
		((_cache[sn] as Dictionary)["b"] as StreetR2Builder).root.free()
	_cache.clear()


func test_build_is_deterministic() -> void:
	for sn in WORLDS:
		var c := _world(sn)
		var again := StreetR2Builder.build(c["w"]["city"], c["d"], c["w"]["seed"])
		var first: StreetR2Builder = c["b"]
		assert_eq(again.summary["digest"], first.summary["digest"], "seed %s: same digest" % sn)
		assert_eq(again.root.get_child_count(), first.root.get_child_count(), "seed %s: same node count" % sn)
		var names_a: Array = []
		var names_b: Array = []
		for n in first.root.get_children():
			names_a.append(String(n.name))
		for n in again.root.get_children():
			names_b.append(String(n.name))
		assert_eq(names_b, names_a, "seed %s: same nodes in the same order" % sn)
		again.root.free()


func test_street_has_facades_signs_props_and_lamps() -> void:
	for sn in WORLDS:
		var b: StreetR2Builder = _world(sn)["b"]
		assert_gt(int(b.summary["facades"]), 50, "seed %s: facades near the street" % sn)
		assert_gt(int(b.summary["signs"]["count"]), 6, "seed %s: planned signs" % sn)
		assert_gt(int(b.summary["lamps"]), 10, "seed %s: kerb lamps" % sn)
		assert_gt((b.summary["props"] as Dictionary).size(), 3, "seed %s: several prop kinds from the street kit" % sn)
		assert_gt(int(b.summary["tris"]["win"]), 0, "seed %s: lit windows" % sn)


func test_frontage_row_is_continuous() -> void:
	var allow := StreetR2OneCity.lot_u() + 0.01
	for sn in WORLDS:
		var b: StreetR2Builder = _world(sn)["b"]
		var sp: Array = b.spans.duplicate()
		assert_gt(sp.size(), 4, "seed %s: a row of frontage faces" % sn)
		sp.sort_custom(func(x: Array, y: Array) -> bool: return float(x[0]) < float(y[0]) if float(x[0]) != float(y[0]) else String(x[2]) < String(y[2]))
		for i in range(1, sp.size()):
			var gap := float(sp[i][0]) - float(sp[i - 1][1])
			assert_lt(gap, allow, "seed %s: gap %.2f between %s and %s is no more than a cross street" % [sn, gap, sp[i - 1][2], sp[i][2]])


func test_every_sign_word_fits_its_texture() -> void:
	var fonts := StreetR2SignCanvas.load_fonts()
	var measure := StreetR2SignCanvas.make_measure(fonts)
	for sn in WORLDS:
		var b: StreetR2Builder = _world(sn)["b"]
		var checked := 0
		for id: String in b.specs:
			var sp: Dictionary = b.specs[id]
			if sp["w"] == null:
				continue
			for op: Dictionary in sp["ops"]:
				if op["op"] != "text":
					continue
				var bb: Array = measure.call(op["font"], int(op["size"]), op["s"])
				assert_lte(int(bb[0]), int(sp["w"]), "seed %s sign %s: '%s' wider than its texture" % [sn, id, op["s"]])
				assert_lte(int(bb[1]), int(sp["h"]), "seed %s sign %s: '%s' taller than its texture" % [sn, id, op["s"]])
				checked += 1
		assert_gt(checked, 5, "seed %s: texts were measured" % sn)


func test_old_hero_bars_are_cut_with_the_r2_frontage() -> void:
	var c := _world("101")
	var old := StreetDressing.build(c["d"], c["w"]["city"])
	var cut := StreetDressing.build(c["d"], c["w"]["city"], {}, true)
	assert_gt(old.items.get("hero_neon", []).size(), 0, "the old dressing has hero blades")
	assert_eq(cut.items.get("hero_neon", []).size(), 0, "r2 frontage: no old hero blades")
	assert_eq(cut.items.get("sign_neon", []).size(), 0, "r2 frontage: no old city signs")
	old.root.free()
	cut.root.free()


func test_render_config_is_sound() -> void:
	var cfg := StreetR2RenderConfigData.shipped()
	assert_eq(cfg.validate().size(), 0, "no problems: %s" % ",".join(cfg.validate()))
