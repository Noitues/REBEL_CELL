extends GutTest
## LOOK Solace park (CitySolaceParkKit): the park of the layout (A-069 / A-070) is drawn deterministically from its own data: one mesh
## with the lawn, the paths, the ponds and the plinth; the plinth stands at the layout's centre with the layout's radius, the stairs
## follow the layout's N / E / S / W; no park, no mesh. The landmark glb's plinth is not drawn beside it.

const CONFIG := preload("res://content/config/city_config.tres")


func test_the_park_mesh_is_deterministic_and_has_every_part() -> void:
	var park := CitySolaceParkKit.data(7)
	assert_false(park.is_empty(), "seed 7 has a Solace park")
	var a := CitySolaceParkKit.mesh(CONFIG, park, null)
	var b := CitySolaceParkKit.mesh(CONFIG, park, null)
	assert_not_null(a)
	assert_eq(a.surface_get_arrays(0)[Mesh.ARRAY_VERTEX], b.surface_get_arrays(0)[Mesh.ARRAY_VERTEX], "same seed, same park")
	var parts := {}
	for c: Color in a.surface_get_arrays(0)[Mesh.ARRAY_COLOR]:
		parts[snappedf(c.a, 0.1)] = true
	for part in [CitySolaceParkKit.PART_LAWN, CitySolaceParkKit.PART_PATH, CitySolaceParkKit.PART_LIT, CitySolaceParkKit.PART_STONE]:
		assert_true(parts.has(snappedf(part, 0.1)), "part %.1f is drawn" % part)


func test_the_plinth_is_the_layouts_circle() -> void:
	var park := CitySolaceParkKit.data(7)
	var pl: Dictionary = park["plinth"]
	var m := CitySolaceParkKit.mesh(CONFIG, park, null)
	var c := CityIsoCamera.lot_to_world(CONFIG, pl["centre"], 0.0)
	var far := 0.0
	var top := 0.0
	var arr := m.surface_get_arrays(0)
	var verts: PackedVector3Array = arr[Mesh.ARRAY_VERTEX]
	var cols: PackedColorArray = arr[Mesh.ARRAY_COLOR]
	for i in verts.size():
		var v: Vector3 = verts[i]
		var col: Color = cols[i]
		if col.a > 0.95 and v.y > 0.5 and Vector2(v.x - c.x, v.z - c.z).length() < float(pl["radius_bu"]) * 1.1:
			far = maxf(far, Vector2(v.x - c.x, v.z - c.z).length())
			top = maxf(top, v.y)
	assert_gte(far, float(pl["radius_bu"]) - 0.01, "the lowest tier reaches the layout's radius")
	assert_almost_eq(top, CONFIG.solace_plinth_top, 0.05, "the top of the plinth is solace_plinth_top")


func test_no_park_no_mesh() -> void:
	assert_null(CitySolaceParkKit.mesh(CONFIG, {}, null))
