class_name BloomLook
extends RefCounted
## LOOK Solace THE BLOOM A "Necrosis" (designer 2026-10-22): the look API of the Bloom. Pure, read-only: it turns the Bloom's rule figures
## (BloomState front / layer in thousandths of a layer, the band BloomRules gives) and a layout (the street's derive, the HQ compound's
## anchors) into a LOOK DICTIONARY the views draw: where the front stands, the keep-out boxes, the strength and the shader uniforms. It
## changes no game state and draws nothing by itself; `CityView3D.set_bloom` puts the dictionary on the materials. Same inputs, same
## dictionary: the preview and the result are one function of the front.
##
## The one call build adds (look only, no rules): on the street view `view.set_bloom(BloomLook.from_state(session.run.corp_theme.solace,
## BloomLook.street_layout(data.derive), config))` after each entry / fight end, on the HQ page `city.set_bloom(BloomLook.from_state(
## b, BloomLook.hq_layout(manifest, layout, at), config, &"decision"))`. At strength 0 (a disabled Bloom, another corporation) the
## views draw exactly as without it.
##
## A look dictionary: {"kind": &"street" | &"hq", "strength": float, "band": int (BloomRules.Band), "front": float (street frame x, or the
## HQ front's plate height), "uniforms": {StringName: Variant} (shader `bl_*`), "ribbons": {...} (street) / "haze": {...} (HQ),
## "roles": {material name: mode} (HQ)}.

const CONFIG_PATH := "res://addons/rc_look/config/look_bloom.tres"
const KIND_STREET := &"street"
const KIND_HQ := &"hq"
const VIEW_DECISION := &"decision"
## Band names in BloomRules.Band order (the config's street_bands keys).
const BAND_NAMES: Array[String] = ["DORMANT", "CREEPING", "CLOSE", "CATCHING", "CAUGHT"]
## The shader's keep-out array size (bloom_necrosis.gdshaderinc BL_BOXES).
const SHADER_BOXES := 128

static var _cfg: RcLookBloomConfig = null
static var _decls: Dictionary = {}


## The shipped config, loaded once.
static func config() -> RcLookBloomConfig:
	if _cfg == null:
		_cfg = load(CONFIG_PATH) as RcLookBloomConfig
	return _cfg


## The look of a Bloom that is not there: strength 0, nothing drawn.
static func off(kind: StringName = KIND_STREET) -> Dictionary:
	return {"kind": kind, "strength": 0.0, "band": 0, "front": 0.0, "uniforms": {&"bl_strength": 0.0}}


# --- The state -> look mapper ---------------------------------------------------------------------------------------------

## The look of `b` on `layout` (`street_layout` / `hq_layout`): strength 1 while the Bloom is enabled, 0 otherwise; the front from
## `b.front_milli` (layers), the band from the gap through BloomRules. `view` &"decision" lifts the HQ front by `hq.decision_lift`
## (the decision shot's +2 floors); any other value is the overview. `campaign_cfg` null reads the shipped campaign config.
static func from_state(b: BloomState, layout: Dictionary, campaign_cfg: CampaignConfigData = null, view: StringName = &"") -> Dictionary:
	var kind := StringName(layout.get("kind", KIND_STREET))
	if b == null or not b.enabled or layout.is_empty():
		return off(kind)
	var cc := campaign_cfg if campaign_cfg != null else load("res://content/config/campaign_config.tres") as CampaignConfigData
	var band := int(BloomRules.band_for_gap(BloomRules.gap_milli(b), cc))
	return at_front(float(b.front_milli) / 1000.0, band, layout, view, 1.0)


## The look at a front of `front_layers` (fractional, route layers: 1 = the first node layer) in `band` (BloomRules.Band). The mapper's
## core, also the labs' `--bloom=<front>`.
static func at_front(front_layers: float, band: int, layout: Dictionary, view: StringName = &"", strength: float = 1.0) -> Dictionary:
	if strength <= 0.0:
		return off(StringName(layout.get("kind", KIND_STREET)))
	if StringName(layout.get("kind", KIND_STREET)) == KIND_HQ:
		return _hq_look(front_layers, band, layout, view, strength)
	return _street_look(front_layers, band, layout, strength)


# --- Street ----------------------------------------------------------------------------------------------------------------

## The street layout from a street derive (`StreetRouteData.derive`): the street frame, the layer columns' positions along it and the
## keep-out boxes (route rooms +10 %, jamb, frame ring; the links), all in the street frame (x = frame0.x - along, y = frame0.y + across).
static func street_layout(derive: Dictionary) -> Dictionary:
	var cfg := config()
	var fr: Dictionary = cfg.street_frame
	var st: Dictionary = derive["street"]
	var a := Vector2(float(st["a"][0]), float(st["a"][1]))
	var c := Vector2(float(st["c"][0]), float(st["c"][1]))
	# the street's axis is the derive's own `nrm` turned a quarter (the frontage runs straight along it; the a -> c chord may slant)
	var nrm := Vector2(float(derive["nrm"][0]), float(derive["nrm"][1])).normalized()
	var dir := Vector2(nrm.y, -nrm.x)
	if dir.dot(c - a) < 0.0:
		dir = -dir
	var perp := Vector2(dir.y, -dir.x)
	# The across axis points toward the frontage: the side the route rooms are on.
	var rooms: Dictionary = derive["rooms"]
	var ids: Array = rooms.keys()
	IdSort.sort_ids(ids)
	var side := 0.0
	var n := 0
	for id: String in ids:
		for p: Array in (rooms[id] as Dictionary)["front"]:
			side += (Vector2(float(p[0]), float(p[1])) - a).dot(perp)
			n += 1
	if n > 0 and side < 0.0:
		perp = -perp
	var x0 := float(fr["x0"])
	var y0 := float(fr["y0"])
	var layer_x := {}
	for ci: Dictionary in derive["col_info"]:
		layer_x[int(ci["layer"])] = x0 - 0.5 * (float(ci["u0"]) + float(ci["u1"]))
	var boxes: Array = []
	var face_t := 0.0
	var face_n := 0
	var kinds: Dictionary = {}
	for id: String in ids:
		var room: Dictionary = rooms[id]
		var lo := Vector3(INF, INF, INF)
		var hi := Vector3(-INF, -INF, -INF)
		for key: String in ["front", "back"]:
			for p: Array in room[key]:
				var q := _to_frame(Vector2(float(p[0]), float(p[1])), float(p[2]), a, dir, perp, x0, y0)
				lo = Vector3(minf(lo.x, q.x), minf(lo.y, q.y), minf(lo.z, q.z))
				hi = Vector3(maxf(hi.x, q.x), maxf(hi.y, q.y), maxf(hi.z, q.z))
		for p: Array in room["front"]:
			face_t += _to_frame(Vector2(float(p[0]), float(p[1])), 0.0, a, dir, perp, x0, y0).y
			face_n += 1
		var mx := float(fr["room_mx"]) * (hi.x - lo.x)
		var mz := float(fr["room_mz"]) * (hi.z - lo.z)
		boxes.append([Vector3(lo.x - mx, lo.y - float(fr["room_y0"]), lo.z - mz - float(fr["room_z"])),
			Vector3(hi.x + mx, hi.y + float(fr["room_y1"]), hi.z + mz + float(fr["room_z"]))])
		kinds[id] = int(room.get("layer", 0))
	# links: the Bloom runs beside a link, never on it (axis-aligned segments plus a margin)
	var seen := {}
	for e: Dictionary in derive["edges"]:
		var path: Array = e["path"]
		for i in range(path.size() - 1):
			var p0 := _to_frame(Vector2(float(path[i][0]), float(path[i][1])), float(path[i][2]), a, dir, perp, x0, y0)
			var p1 := _to_frame(Vector2(float(path[i + 1][0]), float(path[i + 1][1])), float(path[i + 1][2]), a, dir, perp, x0, y0)
			var lo := Vector3(minf(p0.x, p1.x), minf(p0.y, p1.y), minf(p0.z, p1.z)) - Vector3(float(fr["link_x"]), float(fr["link_y"]), float(fr["link_z"]))
			var hi := Vector3(maxf(p0.x, p1.x), maxf(p0.y, p1.y), maxf(p0.z, p1.z)) + Vector3(float(fr["link_x"]), float(fr["link_y"]), float(fr["link_z"]))
			var key := "%.2f,%.2f,%.2f,%.2f,%.2f,%.2f" % [lo.x, lo.y, lo.z, hi.x, hi.y, hi.z]
			if not seen.has(key):
				seen[key] = true
				boxes.append([lo, hi])
	boxes.sort_custom(_box_less)
	return {"kind": KIND_STREET, "origin": a, "dir": dir, "perp": perp, "x0": x0, "y0": y0, "layer_x": layer_x, "boxes": boxes,
		"facade_y": (face_t / float(maxi(face_n, 1))) + float(fr["facade_off"]) if face_n > 0 else y0 + 3.4}


static func _to_frame(plan: Vector2, h: float, a: Vector2, dir: Vector2, perp: Vector2, x0: float, y0: float) -> Vector3:
	var r := plan - a
	return Vector3(x0 - r.dot(dir), y0 + r.dot(perp), h)


static func _box_less(p: Array, q: Array) -> bool:
	var a := p[0] as Vector3
	var b := q[0] as Vector3
	if not is_equal_approx(a.x, b.x):
		return a.x < b.x
	if not is_equal_approx(a.y, b.y):
		return a.y < b.y
	if not is_equal_approx(a.z, b.z):
		return a.z < b.z
	var c := p[1] as Vector3
	var d := q[1] as Vector3
	if not is_equal_approx(c.x, d.x):
		return c.x < d.x
	if not is_equal_approx(c.y, d.y):
		return c.y < d.y
	return c.z < d.z


## The mean distance between neighbouring layer columns (BU; the config's floor when the layout gives fewer than two).
static func layer_spacing(layout: Dictionary) -> float:
	var lx: Dictionary = layout["layer_x"]
	var ids: Array = lx.keys()
	ids.sort()
	if ids.size() < 2:
		return float(config().street_frame["layer_spacing_min"])
	return maxf(absf(float(lx[ids[ids.size() - 1]]) - float(lx[ids[0]])) / float(ids[ids.size() - 1] - ids[0]), float(config().street_frame["layer_spacing_min"]))


## The street frame x of route layer `f` (fractional): linear between the layer columns, extended past either end at the end slope.
static func layer_x_at(layout: Dictionary, f: float) -> float:
	var lx: Dictionary = layout["layer_x"]
	var ids: Array = lx.keys()
	ids.sort()
	if ids.is_empty():
		return float(layout["x0"])
	if ids.size() == 1:
		return float(lx[ids[0]]) - 6.0 * (f - float(ids[0]))
	var i0 := 0
	if f >= float(ids[ids.size() - 1]):
		i0 = ids.size() - 2
	elif f > float(ids[0]):
		while i0 < ids.size() - 2 and f >= float(ids[i0 + 1]):
			i0 += 1
	var l0 := float(ids[i0])
	var l1 := float(ids[i0 + 1])
	var x0 := float(lx[ids[i0]])
	var x1 := float(lx[ids[i0 + 1]])
	return x0 + (x1 - x0) * (f - l0) / (l1 - l0)


static func _street_look(front_layers: float, band: int, layout: Dictionary, strength: float) -> Dictionary:
	var cfg := config()
	var s: Dictionary = cfg.street.duplicate(true)
	var bn: String = BAND_NAMES[clampi(band, 0, BAND_NAMES.size() - 1)]
	var tune: Dictionary = cfg.street_bands.get(bn, cfg.street_bands["CLOSE"])
	for k: String in tune:
		if k != "ribbons_strength":
			s[k] = tune[k]
	var fx := layer_x_at(layout, front_layers)
	var spacing := layer_spacing(layout)
	var boxes: Array = []
	var cull := float(cfg.street_frame["cull_ahead"])
	for bx: Array in layout["boxes"]:
		if (bx[1] as Vector3).x > fx - cull:
			boxes.append(bx)
	var cap := mini(int(cfg.street_frame["max_boxes"]), SHADER_BOXES)
	if boxes.size() > cap:
		boxes = boxes.slice(0, cap)
	var lo := PackedVector3Array()
	var hi := PackedVector3Array()
	lo.resize(SHADER_BOXES)
	hi.resize(SHADER_BOXES)
	for i in boxes.size():
		lo[i] = boxes[i][0]
		hi[i] = boxes[i][1]
	var u := {
		&"bl_strength": strength,
		&"bl_pink": _v3(s["pink"]), &"bl_plum": _v3(s["plum"]), &"bl_rough": float(s["rough"]), &"bl_seed": float(s["seed"]),
		&"bl_cover_k": float(s["cover_k"]), &"bl_veins": float(s["veins"]), &"bl_edge_k": float(s["edge_k"]), &"bl_hatch_k": float(s["hatch_k"]), &"bl_body_emit": float(s.get("body_emit", 0.0)), &"bl_vein_dens": float(s.get("vein_dens", 0.0)),
		&"bl_vscale": float(s["vscale"]), &"bl_vw": float(s["vw"]), &"bl_ew": float(s["ew"]), &"bl_hatch_scale": float(s["hatch_scale"]),
		&"bl_tend": float(s["tend_layers"]) * spacing, &"bl_len_k": spacing / float(cfg.street_frame["layer_spacing_ref"]), &"bl_lean": float(s["lean"]),
		&"bl_wall_vw": float(s["wall_vw"]), &"bl_wall_veins": float(s["wall_veins"]), &"bl_wall_hatch": float(s["wall_hatch"]), &"bl_edge_px": float(s.get("edge_px", 0.0)), &"bl_tend_h": float(s["tend_h"]),
		&"bl_origin": layout["origin"], &"bl_dir": layout["dir"], &"bl_perp": layout["perp"],
		&"bl_frame0": Vector2(float(layout["x0"]), float(layout["y0"])), &"bl_front": fx,
		&"bl_box_n": boxes.size(), &"bl_box_lo": lo, &"bl_box_hi": hi,
	}
	var rb: Dictionary = cfg.ribbons.duplicate(true)
	rb["strength"] = float(tune.get("ribbons_strength", rb["strength"])) * strength
	rb["reach"] = float(rb["reach_layers"]) * spacing  # the reach is in layers: the same layers on any street
	rb["len_min"] = float(rb["len_min_share"]) * float(rb["reach"])
	rb["front"] = fx
	rb["facade_y"] = float(layout["facade_y"])
	rb["boxes"] = boxes
	return {"kind": KIND_STREET, "strength": strength, "band": band, "front": fx, "uniforms": u, "ribbons": rb,
		"frame": {"origin": layout["origin"], "dir": layout["dir"], "perp": layout["perp"], "x0": layout["x0"], "y0": layout["y0"]}}


## Lab tuning: `look` with shader uniforms overridden from `spec` ("bl_veins=2.0,bl_plum=0.3;0.12;0.23": floats, or three numbers joined by
## ";" for a colour / vector). Returns a copy; used by the labs' `--bloom-u=` only.
static func with_uniforms(look: Dictionary, spec: String) -> Dictionary:
	var out := look.duplicate(true)
	var u: Dictionary = out["uniforms"]
	for pair in spec.split(",", false):
		var kv := pair.split("=", true, 1)
		if kv.size() != 2:
			continue
		var parts := kv[1].split(";")
		if parts.size() == 3:
			u[StringName(kv[0])] = Vector3(float(parts[0]), float(parts[1]), float(parts[2]))
		else:
			u[StringName(kv[0])] = float(kv[1])
	return out


## The street frame -> world transform of a street look (the ribbons' node transform): frame (x, y, z) to the world (plan x, height,
## -plan y).
static func frame_to_world(look: Dictionary) -> Transform3D:
	var f: Dictionary = look["frame"]
	var d: Vector2 = f["dir"]
	var p: Vector2 = f["perp"]
	var o: Vector2 = f["origin"]
	# the Basis columns are the frame's x (along, reversed), y (across) and z (up) in world axes
	var basis := Basis(Vector3(-d.x, 0.0, d.y), Vector3(p.x, 0.0, -p.y), Vector3(0.0, 1.0, 0.0))
	var plan0 := o + d * float(f["x0"]) - p * float(f["y0"])
	return Transform3D(basis, Vector3(plan0.x, 0.0, -plan0.y))


# --- HQ helix --------------------------------------------------------------------------------------------------------------

## The HQ layout: the compound `manifest` (unit_k), its layout table (the route nodes' places) and `at` (the compound's world transform).
## The layer heights and the route-room spheres are in plate units (Blender: x, y, z up), the world -> plate matrix too.
static func hq_layout(manifest: Dictionary, layout: HqCompoundLayoutData, at: Transform3D) -> Dictionary:
	var k := HqSolaceMaterials.unit_k(manifest)
	var layer_z := {}
	var rooms: Array = []
	var h: Dictionary = config().hq
	if layout != null:
		var rows := layout.layer_rows()
		for l in range(1, rows + 1):
			var z := 0.0
			for sl in layout.slots_per_layer:
				z += layout.slot_position(l, sl).y
			layer_z[l] = z / float(layout.slots_per_layer) / k
			# the route node of this layer is the inward window of its floor on both strands (hq_graph.py: phi_in, win_z): its lit
			# interior is the route room whose emission stays clean
			var f := roundf((float(layer_z[l]) - float(h["node_over_floor"]) - float(h["podium"])) / float(h["floor_h"]))
			for tw in 2:
				rooms.append(_tube_pt(h, tw, float(h["podium"]) + f * float(h["floor_h"]) + float(h["win_zc"]), _phi_in(h, tw), float(h["tube_r"])))
		var cs := layout.central_server
		rooms.append(Vector3(cs.x, -cs.z, cs.y) / k)
	# plate = M * (at^-1 * world): x_b = lx / k, y_b = -lz / k, z_b = ly / k
	var m := Transform3D(Basis(Vector3(1.0, 0.0, 0.0) / k, Vector3(0.0, 0.0, 1.0) / k, Vector3(0.0, -1.0, 0.0) / k), Vector3.ZERO)
	return {"kind": KIND_HQ, "unit_k": k, "at": at, "w2p": m * at.affine_inverse(), "layer_z": layer_z, "rooms": rooms}


## The plate-frame point on strand `tw` (0 = A, 1 = B) at height z, angle phi round the tube from its front normal, `r` from its centre
## line (hq_graph.tube_pt).
static func _tube_pt(h: Dictionary, tw: int, z: float, phi: float, r: float) -> Vector3:
	var f := (z - float(h["podium"])) / float(h["floor_h"])
	var th := deg_to_rad(float(h["theta0"]) + float(h["twist"]) * f)
	var rv := Vector2(sin(th), cos(th))
	if tw == 1:
		rv = -rv
	var c := rv * float(h["radius"])
	var n := Vector2(cos(th), -sin(th))
	var tx := Vector2(n.y, -n.x)
	var p := c + (n * cos(phi) + tx * sin(phi)) * r
	return Vector3(p.x, p.y, z)


## The angle round strand `tw`'s tube of its inward window (hq_graph.phi_in: toward the other strand, turned toward the floor front).
static func _phi_in(h: Dictionary, tw: int) -> float:
	var a := PI * 0.5 - deg_to_rad(float(h["face_front_deg"]))
	return a if tw == 0 else -a


## The plate height of the node row of route layer `f` (fractional): linear between the layers, past either end at the end slope.
static func hq_layer_z(layout: Dictionary, f: float) -> float:
	var lz: Dictionary = layout["layer_z"]
	var ids: Array = lz.keys()
	ids.sort()
	if ids.size() < 2:
		return 0.0
	var i0 := 0
	if f >= float(ids[ids.size() - 1]):
		i0 = ids.size() - 2
	elif f > float(ids[0]):
		while i0 < ids.size() - 2 and f >= float(ids[i0 + 1]):
			i0 += 1
	var l0 := float(ids[i0])
	var l1 := float(ids[i0 + 1])
	var z0 := float(lz[ids[i0]])
	var z1 := float(lz[ids[i0 + 1]])
	return z0 + (z1 - z0) * (f - l0) / (l1 - l0)


static func _hq_look(front_layers: float, band: int, layout: Dictionary, view: StringName, strength: float) -> Dictionary:
	var cfg := config()
	var h: Dictionary = cfg.hq
	var zf := hq_layer_z(layout, front_layers) + float(h["front_over_node"])
	if view == VIEW_DECISION:
		zf += float(h["decision_lift"])
	var rooms := PackedVector4Array()
	rooms.resize(SHADER_BOXES)
	var n := 0
	var rr := float(h["room_r"])
	for r: Vector3 in layout["rooms"]:
		if n < SHADER_BOXES:
			rooms[n] = Vector4(r.x, r.y, r.z, rr)
			n += 1
	var sd := deg_to_rad(float(h["stair_deg"]))
	var u := {
		&"bl_strength": strength,
		&"bl_pink": _v3(h["pink"]), &"bl_plum": _v3(h["plum"]), &"bl_rough": float(h["rough"]), &"bl_seed": float(h["seed"]),
		&"bl_cover_k": float(h["cover_k"]), &"bl_veins": float(h["veins"]), &"bl_edge_k": float(h["edge_k"]), &"bl_hatch_k": float(h["hatch_k"]), &"bl_vein_dens": float(h.get("vein_dens", 0.0)),
		&"bl_vscale": float(h["vscale"]), &"bl_vw": float(h["vw"]), &"bl_ew": float(h["ew"]), &"bl_hatch_scale": float(h["hatch_scale"]),
		&"bl_w2p": Projection(layout["w2p"]), &"bl_zfront": zf, &"bl_swell": float(h["swell"]), &"bl_tongue": float(h["tongue"]),
		&"bl_reach": float(h["reach"]), &"bl_ahead_k": float(h["ahead_k"]), &"bl_tube_r": float(h["tube_r"]),
		&"bl_helix": Vector4(float(h["radius"]), float(h["floor_h"]), float(h["theta0"]), float(h["twist"])), &"bl_podium": float(h["podium"]),
		&"bl_stair": Vector2(-sd, sd), &"bl_stair_w": float(h["stair_w"]), &"bl_win_dim": float(h["win_dim"]), &"bl_win_r": float(h["win_r"]),
		&"bl_room_n": n, &"bl_room": rooms,
	}
	var hz: Dictionary = cfg.haze.duplicate(true)
	hz["z0"] = zf - float(hz["below"])
	hz["unit_k"] = float(layout["unit_k"])
	hz["strength"] = strength * (float(hz["decision_share"]) if view == VIEW_DECISION else 1.0)
	hz["at"] = layout["at"]
	return {"kind": KIND_HQ, "strength": strength, "band": band, "front": zf, "uniforms": u, "haze": hz, "roles": h["roles"]}


## The spore haze of an HQ look: a FogVolume box (a child of the compound node, whose frame is the plate's times unit_k) carrying
## `bloom_haze`; null when the look has none or no strength. The page's volumetric fog must be on (HqSolaceMaterials.add_fog).
static func haze_volume(look: Dictionary) -> FogVolume:
	var hz: Dictionary = look.get("haze", {})
	if hz.is_empty() or float(hz.get("strength", 0.0)) <= 0.0 or float(hz["h"]) <= 0.0:
		return null
	var k := float(hz["unit_k"])
	var at: Transform3D = hz["at"]
	var fv := FogVolume.new()
	fv.name = "BloomHaze"
	fv.shape = RenderingServer.FOG_VOLUME_SHAPE_BOX
	fv.size = Vector3(2.0 * float(hz["r"]), float(hz["h"]), 2.0 * float(hz["r"])) * k
	fv.position = Vector3(0.0, (float(hz["z0"]) + 0.5 * float(hz["h"])) * k, 0.0)
	var m := ShaderMaterial.new()
	m.shader = load("res://shaders/city/bloom_haze.gdshader") as Shader
	m.set_shader_parameter(&"pink", (look["uniforms"] as Dictionary)[&"bl_pink"])
	m.set_shader_parameter(&"centre", at.origin)
	m.set_shader_parameter(&"unit_k", k)
	m.set_shader_parameter(&"z0", float(hz["z0"]))
	m.set_shader_parameter(&"h", float(hz["h"]))
	m.set_shader_parameter(&"k", float(hz["k"]))
	m.set_shader_parameter(&"emission", float(hz["emission"]))
	m.set_shader_parameter(&"noise_scale", float(hz["scale"]))
	m.set_shader_parameter(&"strength", float(hz["strength"]))
	fv.material = m
	return fv


# --- Applying a look to materials (view glue) ------------------------------------------------------------------------------

## Puts `look` on every ShaderMaterial under `root` whose shader declares `bl_strength`: the uniforms the shader declares, and for the
## HQ roles `bl_mode` by the material's name. Returns the number of materials touched. A look of strength 0 puts the strength 0 back.
static func apply(root: Node, look: Dictionary) -> int:
	var n := 0
	var seen := {}
	var stack: Array[Node] = [root]
	while not stack.is_empty():
		var node: Node = stack.pop_back()
		for c in node.get_children():
			stack.append(c)
		if not node is GeometryInstance3D:
			continue
		var gi := node as GeometryInstance3D
		var mats: Array[Material] = [gi.material_override, gi.material_overlay]
		if node is MeshInstance3D:
			var mi := node as MeshInstance3D
			if mi.mesh != null:
				for s in mi.mesh.get_surface_count():
					mats.append(mi.get_surface_override_material(s))
					mats.append(mi.mesh.surface_get_material(s))
		elif node is MultiMeshInstance3D:
			var mm := (node as MultiMeshInstance3D).multimesh
			if mm != null and mm.mesh != null:
				for s in mm.mesh.get_surface_count():
					mats.append(mm.mesh.surface_get_material(s))
		for m in mats:
			if m is ShaderMaterial and not seen.has(m):
				seen[m] = true
				if apply_to_material(m as ShaderMaterial, look):
					n += 1
	return n


## `look` on one material (false when its shader does not carry the Bloom).
static func apply_to_material(m: ShaderMaterial, look: Dictionary) -> bool:
	if m.shader == null:
		return false
	var names := _declared(m.shader)
	if not names.has(&"bl_strength"):
		return false
	# a street look goes on the street shaders (they declare bl_front), an HQ look on the helix shaders (bl_w2p); the others stay off
	var hq := StringName(look.get("kind", &"")) == KIND_HQ
	if not names.has(&"bl_w2p" if hq else &"bl_front"):
		m.set_shader_parameter(&"bl_strength", 0.0)
		if names.has(&"bl_mode"):
			m.set_shader_parameter(&"bl_mode", 0)
		return true
	var u: Dictionary = look.get("uniforms", {})
	for k: StringName in u:
		if names.has(k):
			m.set_shader_parameter(k, u[k])
	if names.has(&"bl_mode"):
		var roles: Dictionary = look.get("roles", config().hq["roles"])
		m.set_shader_parameter(&"bl_mode", int(roles.get(String(m.resource_name), 0)) if hq else 0)
	return true


static func _declared(sh: Shader) -> Dictionary:
	if not _decls.has(sh):
		var names := {}
		for d: Dictionary in sh.get_shader_uniform_list():
			names[StringName(d["name"])] = true
		_decls[sh] = names
	return _decls[sh]


static func _v3(a: Array) -> Vector3:
	return Vector3(float(a[0]), float(a[1]), float(a[2]))
