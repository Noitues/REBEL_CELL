extends GutTest
## LOOK Solace S1 (DIRECTION_REVIEW 2026-10-20): the Solace building kits (CitySolaceKit). The kit of a prism is a deterministic
## function of the layout seed and its lot (bundles of neighbouring lots, one kit each, touching bundles differ); only Solace
## buildings draw as kits (every other prism keeps its family key); footprints, heights, picking are the model's and unchanged;
## the kit meshes are well-formed unit meshes.

const CONFIG := preload("res://content/config/city_config.tres")

var cfg: CityConfig = CONFIG
var model: CityModel
var part: Rect2i


func before_all() -> void:
	var hq := Vector2i(CityPlan.for_seed(7).hq_of(&"solace"))
	part = Rect2i(hq - Vector2i(24, 24), Vector2i(56, 56))
	model = CityModel.build(cfg, 7, part)


func _eligible() -> Array[int]:
	var out: Array[int] = []
	for n in model.prisms.size():
		if CitySolaceKit.eligible(cfg, model.prisms[n]):
			out.append(n)
	return out


func test_only_solace_buildings_are_kits() -> void:
	var elig := _eligible()
	assert_gt(elig.size(), 15, "the Solace district has buildings (A-070: blocks of 2-3 lots, about 24 a district)")
	for n in model.prisms.size():
		var pr := model.prisms[n]
		var kv := CitySolaceKit.kit_of(cfg, pr, 7)
		if StringName(pr["terr"]) == &"solace" and not bool(pr["hq"]) and (pr["poly"] as PackedVector2Array).size() == 4 and float(pr["h"]) >= cfg.solace_kit_min_h:
			assert_true(kv.x >= 0 and kv.x <= 2, "a Solace building takes a kit")
		else:
			assert_eq(kv, Vector2i(-1, 0), "not Solace: no kit")
			assert_eq(CitySolaceKit.family_key(cfg, pr, 7), -1)


func test_the_kit_choice_is_deterministic_and_seed_stable() -> void:
	var again := CityModel.build(cfg, 7, part)
	assert_eq(again.prisms.size(), model.prisms.size())
	for n in model.prisms.size():
		assert_eq(CitySolaceKit.kit_of(cfg, again.prisms[n], 7), CitySolaceKit.kit_of(cfg, model.prisms[n], 7), "same seed, same kit %d" % n)
	# The base and the setback prism of one building share lot, kit and variant.
	var by_cell := {}
	for n in _eligible():
		var cell: Rect2i = model.prisms[n]["cell"]
		var kv := CitySolaceKit.kit_of(cfg, model.prisms[n], 7)
		if by_cell.has(cell):
			assert_eq(by_cell[cell], kv, "one building, one kit")
		by_cell[cell] = kv
	# Another layout seed moves the lattice and permutes the kits.
	var moved := 0
	for n in _eligible():
		if CitySolaceKit.kit_of(cfg, model.prisms[n], 8) != CitySolaceKit.kit_of(cfg, model.prisms[n], 7):
			moved += 1
	assert_gt(moved, _eligible().size() / 4, "a new seed re-deals the bundles")


func test_all_three_kits_are_used_and_balanced() -> void:
	var count := [0, 0, 0]
	var lots := {}
	for n in _eligible():
		var cell: Rect2i = model.prisms[n]["cell"]
		if lots.has(cell):
			continue
		lots[cell] = true
		count[CitySolaceKit.kit_of(cfg, model.prisms[n], 7).x] += 1
	for k in 3:
		assert_gt(count[k], lots.size() / 6, "kit %d is a real share of the lots (%s)" % [k, str(count)])


func test_bundles_are_small_and_neighbouring_bundles_differ() -> void:
	var by_bundle := {}
	var cells := {}
	for n in _eligible():
		var cell: Rect2i = model.prisms[n]["cell"]
		cells[cell.position] = CitySolaceKit.bundle_of(cfg, cell, 7)
	for p: Vector2i in cells:
		var b: Vector2i = cells[p]
		by_bundle[b] = int(by_bundle.get(b, 0)) + 1
	var total := 0
	for b: Vector2i in by_bundle:
		total += int(by_bundle[b])
	var mean := float(total) / by_bundle.size()
	# A-070 (Solace district layout): blocks are 2-3 lots a side on a ring round the park, about 24-31 a district; the bundle lattice
	# (pitch 15 lots, retuned for them) makes bundles of 3-8 blocks on average (measured over seeds 1, 7, 42, 2026: 92 % of the
	# blocks sit in bundles of 3-8).
	assert_between(mean, 3.0, 8.0, "a bundle holds 3-8 blocks (mean %.2f buildings)" % mean)
	var checked := 0
	var near: Array[Vector2i] = []
	for p: Vector2i in cells:
		near.append(p)
	near.sort_custom(func(a: Vector2i, b: Vector2i) -> bool: return a.y < b.y if a.y != b.y else a.x < b.x)
	var lattice_neighbours: Array[Vector2i] = [Vector2i(1, 0), Vector2i(-1, 0), Vector2i(0, 1), Vector2i(0, -1), Vector2i(1, -1), Vector2i(-1, 1)]
	for p in near:
		for q in near:
			if q == p or maxi(absi(p.x - q.x), absi(p.y - q.y)) > 4 or cells[q] == cells[p]:
				continue
			# Blocks across a lawn gap whose bundles are neighbours on the lattice never share a kit.
			if not lattice_neighbours.has((cells[q] as Vector2i) - (cells[p] as Vector2i)):
				continue
			checked += 1
			assert_ne(CitySolaceKit.kit_of_bundle(cfg, cells[p], 7), CitySolaceKit.kit_of_bundle(cfg, cells[q], 7),
				"touching bundles %s and %s differ" % [str(cells[p]), str(cells[q])])
	assert_gt(checked, 4, "bundle borders were checked")


func test_other_prisms_keep_their_family_keys_and_buffers() -> void:
	var inks := CityMeshKit.ink_palette(model.prisms)
	var idx := PackedInt32Array()
	for n in model.prisms.size():
		if not CitySolaceKit.eligible(cfg, model.prisms[n]):
			idx.append(n)
	var plain := CityMeshKit.families_of(cfg, model.prisms, idx)
	var seeded := CityMeshKit.families_of(cfg, model.prisms, idx, 7)
	assert_eq(seeded.keys(), plain.keys(), "the same families")
	for fk: int in plain:
		assert_lt(fk, CitySolaceKit.KEY_BASE, "a prism family")
		assert_eq(seeded[fk], plain[fk], "the same prisms")
		assert_eq(CityMeshKit.instance_buffer(cfg, model.prisms, seeded[fk], inks), CityMeshKit.instance_buffer(cfg, model.prisms, plain[fk], inks))
	# The Solace prisms leave their prism families for kit keys, one buffer layout (INSTANCE_FLOATS) as ever.
	var all := PackedInt32Array()
	for n in model.prisms.size():
		all.append(n)
	var kits := CityMeshKit.families_of(cfg, model.prisms, all, 7)
	var kit_total := 0
	for fk: int in kits:
		if CitySolaceKit.is_kit_key(fk):
			kit_total += (kits[fk] as PackedInt32Array).size()
			assert_eq(CityMeshKit.instance_buffer(cfg, model.prisms, kits[fk], inks).size(), (kits[fk] as PackedInt32Array).size() * CityMeshKit.INSTANCE_FLOATS)
	assert_eq(kit_total, _eligible().size(), "every eligible prism is in a kit family")


func test_the_model_and_picking_do_not_depend_on_the_kits() -> void:
	var off: CityConfig = cfg.duplicate()
	off.solace_kits = false
	var plain := CityModel.build(off, 7, part)
	assert_eq(plain.prisms.size(), model.prisms.size())
	for n in model.prisms.size():
		for k: String in ["poly", "y0", "h", "taper", "key", "terr", "cell", "building"]:
			assert_eq(plain.prisms[n][k], model.prisms[n][k], "prism %d %s" % [n, k])
	var c0: Vector2 = model.prisms[0]["centre"]
	var cam := CityIsoCamera.make(cfg, Vector3(c0.x, 0.0, c0.y), 120.0, Vector2(1920, 1080))
	for k in 12:
		var p := Vector2(160 + k * 130, 200 + k * 55)
		assert_eq(plain.pick(cam, p), model.pick(cam, p), "the same pick at %s" % str(p))


func test_kit_meshes_are_well_formed_unit_meshes() -> void:
	var made := 0
	for kit in 3:
		for v in cfg.solace_kit_variants[kit]:
			var key := CitySolaceKit.KEY_BASE + kit * 10 + v
			var m := CitySolaceKit.mesh(cfg, key, 0)
			assert_same(CitySolaceKit.mesh(cfg, key, 0), m, "cached")
			var arr := m.surface_get_arrays(0)
			var verts: PackedVector3Array = arr[Mesh.ARRAY_VERTEX]
			var uvs: PackedVector2Array = arr[Mesh.ARRAY_TEX_UV]
			var cust: PackedFloat32Array = arr[Mesh.ARRAY_CUSTOM0]
			assert_gt(verts.size(), 60)
			assert_eq(verts.size() % 3, 0)
			assert_eq(uvs.size(), verts.size())
			assert_eq(cust.size(), verts.size() * 4)
			for i in verts.size():
				var code := cust[i * 4 + 3]
				assert_between(code, 1.0, 8.0, "a part code")
				assert_lte(absf(verts[i].x), 0.5 + 0.001, "inside the lot (x)")
				assert_lte(absf(verts[i].z), 0.5 + 0.001, "inside the lot (z)")
				assert_between(uvs[i].y, 0.0, 1.0, "anchor")
				assert_eq(verts[i].y, uvs[i].y, "the unscaled height is the anchor")
			var far := CitySolaceKit.mesh(cfg, key, 2).surface_get_arrays(0)[Mesh.ARRAY_VERTEX] as PackedVector3Array
			assert_lte(far.size(), verts.size(), "the far LOD is no heavier")
			made += 1
	assert_eq(made, cfg.solace_kit_variants.x + cfg.solace_kit_variants.y + cfg.solace_kit_variants.z)
