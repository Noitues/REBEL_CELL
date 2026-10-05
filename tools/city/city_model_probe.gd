extends Node
## ART-5 5a: headless timing of the whole-city model (build, buffers, picking). Run:
## godot --headless --path . res://tools/city/city_model_probe.tscn


func _ready() -> void:
	var cfg: CityConfig = load("res://content/config/city_config.tres")
	var t0 := Time.get_ticks_msec()
	var m := CityModel.build(cfg, 7)
	var t1 := Time.get_ticks_msec()
	print("PROBE prisms=%d buildings=%d streets=%d plazas=%d chunks=%d hqs=%s ms=%d" % [m.prisms.size(), m.buildings,
		m.streets.size(), m.plazas.size(), m.chunks.size(), str(m.hqs.keys()), t1 - t0])
	var inks := CityMeshKit.ink_palette(m.prisms)
	print("PROBE inks=%d" % inks.size())
	var fams := {}
	for pr in m.prisms:
		var k := CityMeshKit.family_of(cfg, pr)
		fams[k] = int(fams.get(k, 0)) + 1
	print("PROBE fams=%s" % str(fams))
	var t2 := Time.get_ticks_msec()
	for key in m.keys():
		var ch: Dictionary = m.chunks[key]
		var f := CityMeshKit.families_of(cfg, m.prisms, ch["prisms"])
		for fk: int in f:
			CityMeshKit.instance_buffer(cfg, m.prisms, f[fk], inks)
	print("PROBE buffers ms=%d" % (Time.get_ticks_msec() - t2))
	var t3 := Time.get_ticks_msec()
	var cam := CityIsoCamera.make(cfg, Vector3.ZERO, 440.0, Vector2(1920, 1080))
	for k in 20:
		m.pick(cam, Vector2(100 + k * 80, 300 + k * 20))
	print("PROBE pick20 ms=%d" % (Time.get_ticks_msec() - t3))
	get_tree().quit()
