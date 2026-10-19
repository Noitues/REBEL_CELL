class_name StreetDressing
extends RefCounted
## NA-24: the street dressing layer of the netrun view. From the dress lists of `NetrunArtDress` (signs, lamps, washes, glows, beams,
## streak lanes) and the route-side frontage rules (`DressFrontage`: city signs, shopfronts, billboards, plumes) it builds the nodes,
## one MultiMesh group per reveal tier (`DressReveal`: `visibility_range` from config) with colours from the district palettes
## (`DressDistricts`). Placement depends only on the layout seed and the derive; nothing here draws a random number.
## `root` holds the nodes (add it to the view's props layer); `clock_mats` are the materials on the netrun clock.

var root: Node3D = null
## Materials on the netrun clock (`NetrunShaderKit.set_clock`).
var clock_mats: Array = []
## Group id -> instance count of the group.
var counts: Dictionary = {}
## Group id -> nodes of the group (chunks, or the single mesh node of a lane / beam).
var nodes: Dictionary = {}
var dress: Dictionary = {}
var plan: Dictionary = {}
var districts: DressDistricts = null
var _f: Dictionary = {}
var _cfg: DressingConfigData = null
var _items: Dictionary = {}
var _mats: Dictionary = {}


## Builds the dressing of the street `derive` over `city`. `dress_in` is the dress v1 dict (empty: `NetrunArtDress.dress_street`).
static func build(derive: Dictionary, city: Dictionary, dress_in: Dictionary = {}) -> StreetDressing:
	var s := StreetDressing.new()
	s._build(derive, city, dress_in)
	return s


func _build(derive: Dictionary, city: Dictionary, dress_in: Dictionary) -> void:
	_cfg = DressingConfigData.shipped()
	_f = NetrunArtDress.frame(derive)
	dress = dress_in if not dress_in.is_empty() else NetrunArtDress.dress_street(derive, city)
	districts = DressDistricts.new(city)
	plan = DressFrontage.plan(derive, city, districts)
	root = Node3D.new()
	root.name = "StreetDressing"
	var col_by_bid: Dictionary = {}
	for ci: Dictionary in derive["col_info"]:
		col_by_bid[String(ci["bid"])] = ci
	_hero_signs(dress["signs"], col_by_bid)
	_city_signs(plan["signs"])
	_shops(plan["shops"])
	_billboards(plan["billboards"])
	_lamps(dress["lamps"])
	_discs("glow", dress["glows"], false)
	_discs("wash", dress["washes"], true)
	_plumes(plan["plumes"])
	_flush()
	var built: Array = NetrunArtDress.building_tops(city)
	var h_front: float = float(NetrunArtDress.heights(derive, built, NetrunArtDress.PRESET)["h_front"])
	_beams(dress["beams"], h_front)
	_lanes(dress["streak_lanes"])


# --- Collecting ----------------------------------------------------------------------------------

func _eu() -> Array:
	return [float(_f["sgn"]), 0.0] if int(_f["ax"]) == 0 else [0.0, float(_f["sgn"])]


func _out() -> Array:
	var n: Array = _f["nrm"]
	return [-float(n[0]), -float(n[1])]


func _add(group: String, it: Dictionary) -> void:
	if not _items.has(group):
		_items[group] = []
	(_items[group] as Array).append(it)


func _col(id: String, p: Array) -> Color:
	return districts.color(id, float(p[0]), float(p[1]))


func _sign_pieces(prefix: String, s: Dictionary, full: bool) -> void:
	var sg: Dictionary = _cfg.sign
	var p: Array = s["pos"]
	var eu: Array = _eu()
	var ev: Array = _out()
	var w: float = float(s["w"])
	var h: float = float(s["h"])
	var gain: float = float(s.get("emit_mul", 1.0))
	var seed01: float = float(s.get("seed", DressDistricts.hash01("sign_s", String(s["bid"]))))
	var phase: float = float(s.get("phase", DressDistricts.hash01("sign_p", String(s["bid"]))))
	var base: Color = _col(String(s["pal"]), p)
	var depth: float = float(sg["depth"])
	_add(prefix + "_neon", DressKit.item(DressKit.piece(p, eu, ev, 0.0, w, 0.0, depth, 0.0, h), base, seed01, phase, gain))
	_add(prefix + "_flicker", DressKit.item(DressKit.piece(p, eu, ev, 0.0, w, 0.0, depth * 1.2, 0.0, h), base, seed01, phase, gain))
	if not full:
		return
	var n: int = int(s["panels"])
	var gap: float = float(sg["gap"])
	var ph: float = (h - float(n - 1) * gap) / float(n)
	for i in n:
		var z0: float = float(i) * (ph + gap)
		var out: float = depth + 0.8 * fposmod(float(i) * 0.37, 1.0)
		var c: Color = DressKit.lighten(base) if i % 3 == 2 else base
		_add(prefix + "_full", DressKit.item(DressKit.piece(p, eu, ev, 0.0, w, 0.0, out, z0, z0 + ph), c, seed01, phase, gain))
	var pole: float = float(sg["pole"])
	_add(prefix + "_full", DressKit.item(DressKit.piece(p, eu, ev, w * 0.5 - pole * 0.5, w * 0.5 + pole * 0.5, 0.0, depth, 0.0, h), base * 0.6, seed01, phase, gain))


func _hero_signs(list: Array, col_by_bid: Dictionary) -> void:
	var pre: Dictionary = NetrunArtDress.PRESET
	var eu: Array = _eu()
	var ev: Array = _out()
	for s: Dictionary in list:
		var item: Dictionary = s.duplicate()
		item["seed"] = DressDistricts.hash01("hero_s", String(s["bid"]))
		item["phase"] = DressDistricts.hash01("hero_p", String(s["bid"]))
		_sign_pieces("hero", item, true)
		var ci: Dictionary = col_by_bid.get(String(s["bid"]), {})
		if ci.is_empty():
			continue
		var u0: float = float(ci["u0"]) + float(pre["band_inset"])
		var u1: float = float(ci["u1"]) - float(pre["band_inset"])
		var bp: Array = NetrunArtDress.world(_f, u0, float(ci["face"]) - 0.05 * float(_f["ncross"]), float(ci["top"]) - float(pre["band_drop"]))
		var c: Color = _col(String(s["band_pal"]), bp)
		_add("hero_full", DressKit.item(DressKit.piece(bp, eu, ev, 0.0, u1 - u0, 0.0, 0.12, 0.0, float(pre["band_h"])), c, 0.5, 0.0, float(_cfg.sign["band_emit"]) / float(_cfg.sign["panel_emit"])))


func _city_signs(list: Array) -> void:
	for s: Dictionary in list:
		_sign_pieces("sign", s, true)


func _shops(list: Array) -> void:
	var eu: Array = _eu()
	var ev: Array = _out()
	for s: Dictionary in list:
		var p: Array = NetrunArtDress.world(_f, float(s["u0"]), float(s["face"]) - 0.06 * float(_f["ncross"]), float(s["z"]))
		var len_: float = float(s["u1"]) - float(s["u0"])
		var c: Color = _col(String(s["pal"]), p)
		var g: float = float(s["emit_mul"])
		_add("shop_strip", DressKit.item(DressKit.piece(p, eu, ev, 0.0, len_, 0.0, 0.12, 0.0, float(s["h"])), c, 0.5, 0.0, g))
		_add("shop_awning", DressKit.item(DressKit.piece(p, eu, ev, 0.0, len_, 0.0, 0.9, -0.5, -0.38), c * 0.5, 0.5, 0.0, g))


func _billboards(list: Array) -> void:
	var eu: Array = _eu()
	var ev: Array = _out()
	for b: Dictionary in list:
		var p: Array = b["pos"]
		var w: float = float(b["w"])
		var h: float = float(b["h"])
		var c: Color = _col(String(b["pal"]), p)
		var g: float = float(b["emit_mul"])
		_add("billboard_panel", DressKit.item(DressKit.piece(p, eu, ev, -w * 0.5, w * 0.5, 0.0, 0.15, 0.0, h), c * 0.7, 0.5, float(b["phase"]), g))
		var accent: Color = _col("accent_cool", p)
		for i in 3:
			var z0: float = h * (0.15 + 0.28 * float(i))
			_add("billboard_content", DressKit.item(DressKit.piece(p, eu, ev, -w * 0.4, w * 0.4, 0.0, 0.2, z0, z0 + h * 0.14), accent, 0.5, float(b["phase"]), g))


func _lamps(list: Array) -> void:
	var lp: Dictionary = _cfg.lamp
	var eu: Array = _eu()
	var ev: Array = _out()
	var d: float = float(lp["dot"])
	for l: Dictionary in list:
		var p: Array = l["pos"]
		var c: Color = _col(String(l["pal"]), p)
		_add("lamp_dot", DressKit.item(DressKit.piece(p, eu, ev, -d * 0.5, d * 0.5, -d * 0.5, d * 0.5, -d * 0.5, d * 0.5), c, 0.5, 0.0, float(lp["dot_gain"])))
		var gp: Array = [p[0], p[1], 0.05]
		_add("lamp_spill", DressKit.item(DressKit.ground_disc(gp, float(lp["spill_radius"])), c, 0.5, 0.0, float(lp["spill_gain"])))


func _discs(group: String, list: Array, vertical: bool) -> void:
	var gl: Dictionary = _cfg.glow
	var eu: Array = _eu()
	var ev: Array = _out()
	for g: Dictionary in list:
		var p: Array = g["pos"]
		var c: Color = _col(String(g["pal"]), p)
		var pw: float = float(g["power"])
		if vertical:
			# A wash: a soft pool of light on the facade, `wash_back` in front of the column's face, lifted to the sign's heights.
			var face_c: float = float(p[1 - int(_f["ax"])]) + float(NetrunArtDress.PRESET["wash_back"]) * float(_f["ncross"])
			var wp: Array = NetrunArtDress.world(_f, float(g["u"]), face_c - 0.05 * float(_f["ncross"]), 3.0)
			_add(group, DressKit.item(DressKit.wall_disc(wp, eu, ev, float(gl["wash_radius"])), c, 0.5, 0.0, float(gl["wash_gain"]) * pw))
		else:
			var gp: Array = [p[0], p[1], 0.06]
			_add(group, DressKit.item(DressKit.ground_disc(gp, float(gl["radius"])), c, 0.5, 0.0, float(gl["gain"]) * pw))


func _plumes(list: Array) -> void:
	for p: Dictionary in list:
		_add("plume", DressKit.item(Transform3D(Basis.IDENTITY, DressKit.pos_w(p["pos"])), Color.WHITE, float(p["phase"]), 0.0, 1.0))


# --- Groups --------------------------------------------------------------------------------------

func _material(group: String) -> Material:
	if group == "plume":
		return DressKit.plume_material()
	var sg: Dictionary = _cfg.sign
	var shape: int = DressKit.SHAPE_SOLID
	var emit: float = float(sg["panel_emit"])
	if group.ends_with("_flicker"):
		shape = DressKit.SHAPE_FLICKER
		emit = float(sg["flicker_emit"])
	elif group.ends_with("_neon") or group == "shop_strip" or group == "billboard_panel":
		emit = float(sg["neon_emit"])
	elif group == "lamp_spill" or group == "glow" or group == "wash":
		shape = DressKit.SHAPE_DISC
		emit = 1.0
	elif group == "lamp_dot":
		emit = 1.0
	return DressKit.neon_material(shape, emit)


func _mesh_of(group: String) -> Mesh:
	if group == "plume":
		return DressKit.plume_mesh(int(_cfg.plume["puffs"]))
	if group == "lamp_spill" or group == "glow" or group == "wash":
		return DressKit.quad_mesh()
	return DressKit.box_mesh()


func _flush() -> void:
	var names: Array = _items.keys()
	IdSort.sort_ids(names)
	for g: String in names:
		var list: Array = _items[g]
		var mat := _material(g)
		clock_mats.append(mat)
		var ns: Array[MultiMeshInstance3D] = DressKit.group_nodes(g, _mesh_of(g), mat, list)
		nodes[g] = ns
		counts[g] = list.size()
		for n in ns:
			root.add_child(n)


func _beams(list: Array, h_front: float) -> void:
	var beams: Array = []
	for b: Dictionary in list:
		beams.append(b)
	var cap: int = int(_cfg.caps["beam_spots"])
	var ns: Array = []
	for i in mini(beams.size(), cap):
		var b: Dictionary = beams[i]
		var node := NetrunShaderKit.beam_node(b, _col(String(b["pal"]), b["pos"]), h_front)
		node.name = "beam_%d" % i
		DressReveal.apply(node, "beam")
		root.add_child(node)
		clock_mats.append(node.material_override)
		ns.append(node)
	nodes["beam"] = ns
	counts["beam"] = ns.size()


func _lanes(list: Array) -> void:
	var ns: Array = []
	for lane: Dictionary in list:
		var id := int(lane["lane_id"])
		var col: Color = DressDistricts.color_in(String(lane["pal"]), "common")
		var node := NetrunShaderKit.streak_node(lane, col, 1.0)
		node.name = "lane_%d" % id
		DressReveal.apply(node, "lane")
		root.add_child(node)
		clock_mats.append(node.material_override)
		ns.append(node)
	nodes["lane"] = ns
	counts["lane"] = ns.size()
