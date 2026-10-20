class_name StreetLightRig
extends RefCounted
## AAA-2 (A-022 / MATERIAL_SPEC 9): the street's real coloured local lights as Godot OmniLight3D / SpotLight3D nodes within a budget
## (`CityShaderConfigData.aaa.lights` caps): kerb lamps (60 W warm / cool), street-level glows (20 W), the route column washes and one
## facade wash per frontage column, and the fog-mostly city glow and beam spots (their fog energy is the volumetric multiplier at its
## cap, so the energy that lights surfaces is 1/16 of what lights the fog; Godot's fog also honours the cull mask, so a mask cannot make a
## light fog-only). Watts become Godot energy through `omni_k` / `spot_k`; the range is where the inverse-square
## falloff is gone (`range_k` x sqrt(watts), at most `range_max`). View glue: it builds nodes from `StreetDressing.light_sources`.

## Godot's cap on `light_volumetric_fog_energy`.
const FOG_ENERGY_CAP := 16.0

var root: Node3D = null
## Light count by kind ("lamp", "glow", "wash", "facade", "fog", "beam").
var counts: Dictionary = {}


## Builds the rig from `sources` (`StreetDressing.light_sources`).
static func build(sources: Dictionary) -> StreetLightRig:
	var r := StreetLightRig.new()
	r._build(sources)
	return r


func _build(src: Dictionary) -> void:
	var lc: Dictionary = CityShaderConfigData.shipped().aaa["lights"]
	root = Node3D.new()
	root.name = "StreetLights"
	var lamp: Dictionary = lc["lamp"]
	for i: int in _pick(src["lamps"], int(lamp["cap"])):
		var s: Dictionary = src["lamps"][i]
		_omni("lamp", s["pos"], s["col"], float(lamp["watts"]), lc)
	var glow: Dictionary = lc["glow"]
	for i: int in _pick(src["glows"], int(glow["cap"])):
		var s: Dictionary = src["glows"][i]
		_omni("glow", s["pos"], s["col"], float(glow["watts"]) * float(s["k"]), lc)
	var wash: Dictionary = lc["wash"]
	var rw: Array = src["washes"]
	for s: Dictionary in rw:
		_spot("wash", s["pos"], s["dir"], s["col"], float(lc["route_wash"]["watts"]), float(lc["route_wash"]["cone_deg"]), float(lc["route_wash"]["blend"]), lc, 0)
	for i: int in _pick(src["facades"], int(wash["cap"])):
		var s: Dictionary = src["facades"][i]
		_spot("facade", s["pos"], s["dir"], s["col"], float(wash["watts"]), float(wash["cone_deg"]), float(wash["blend"]), lc, 0)
	var cg: Dictionary = lc["city_glow"]
	for s: Dictionary in src["city_glow"]:
		var l := _omni("fog", s["pos"], s["col"], float(cg["watts"]), lc)
		l.omni_range = float(cg["range"])
		l.light_volumetric_fog_energy = FOG_ENERGY_CAP
		l.light_energy = float(cg["energy"]) / FOG_ENERGY_CAP
	for s: Dictionary in src["city_glow_high"]:
		var l := _omni("haze", s["pos"], s["col"], float(cg["watts"]), lc)
		l.omni_range = float(cg["high_range"])
		l.light_volumetric_fog_energy = FOG_ENERGY_CAP
		l.light_energy = float(cg["high_energy"]) / FOG_ENERGY_CAP
	var bm: Dictionary = lc["beam"]
	for i: int in mini(src["beams"].size(), int(bm["cap"])):
		var s: Dictionary = src["beams"][i]
		var l := _spot("beam", s["pos"], s["dir"], s["col"], float(bm["watts"]), float(bm["cone_deg"]), 1.0, lc, 0)
		l.spot_range = float(bm["range"])
		l.light_volumetric_fog_energy = FOG_ENERGY_CAP
		l.light_energy = float(bm["energy"]) / FOG_ENERGY_CAP


## `cap` indices evenly spread over `list` (all of them when it is shorter), in list order.
static func _pick(list: Array, cap: int) -> Array[int]:
	var out: Array[int] = []
	var n: int = list.size()
	if n <= cap:
		for i in n:
			out.append(i)
		return out
	for i in cap:
		out.append(int(floor(float(i) * float(n) / float(cap))))
	return out


func _count(kind: String) -> void:
	counts[kind] = int(counts.get(kind, 0)) + 1
	root.set_meta(&"count_" + StringName(kind), int(counts[kind]))


func _omni(kind: String, pos: Vector3, col: Color, watts: float, lc: Dictionary) -> OmniLight3D:
	var l := OmniLight3D.new()
	l.name = "%s_%d" % [kind, int(counts.get(kind, 0))]
	l.position = pos
	l.light_color = col
	l.light_energy = watts * float(lc["omni_k"])
	l.omni_attenuation = 2.0
	l.omni_range = minf(float(lc["range_max"]), float(lc["range_k"]) * sqrt(watts))
	l.shadow_enabled = false
	l.light_specular = 1.0
	l.light_volumetric_fog_energy = float(lc["fog_k"])
	root.add_child(l)
	_count(kind)
	return l


func _spot(kind: String, pos: Vector3, dir: Vector3, col: Color, watts: float, cone_deg: float, blend: float, lc: Dictionary, mask: int) -> SpotLight3D:
	var l := SpotLight3D.new()
	l.name = "%s_%d" % [kind, int(counts.get(kind, 0))]
	l.light_color = col
	l.light_energy = watts * float(lc["spot_k"])
	l.spot_angle = cone_deg * 0.5
	l.spot_angle_attenuation = lerpf(2.0, 0.5, clampf(blend, 0.0, 1.0))
	l.spot_attenuation = 2.0
	l.spot_range = minf(float(lc["range_max"]), float(lc["range_k"]) * sqrt(watts) * 0.5)
	l.shadow_enabled = false
	l.light_volumetric_fog_energy = float(lc["fog_k"])
	if mask != 0:
		l.light_cull_mask = mask
	var up := Vector3.UP if absf(dir.y) < 0.99 else Vector3.RIGHT
	l.transform = Transform3D(Basis.looking_at(dir.normalized(), up), pos)
	root.add_child(l)
	_count(kind)
	return l
