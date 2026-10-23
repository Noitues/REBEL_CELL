class_name StreetR2Builder
extends RefCounted
## Street look parity P2 step 2: the renderer of the street r2 frontage. Takes the plan of `StreetR2Adapter.plan_street` (the plate's rules on the
## game's city) and builds the Godot street from it: procedural facade meshes from the `kit_face` / `roof_clutter` records of every building
## near the street, the planned signs (draw lists rasterized with the Godot fonts), facade props, kerb lamps and crowns from the street kit glb.
## Deterministic: the same city, derive and seed give the same `summary`. The shaders carry flat world colours only (the scene look is applied
## on top by the netrun environment).

## The plan of `StreetR2Adapter.plan_street`.
var plan: Dictionary = {}
## The Node3D holding everything built (meshes, sign viewports, kit MultiMeshes).
var root: Node3D = null
## Counts for tests and reports: facades, faces / triangles per material, signs, props, lamps, crowns, digest.
var summary: Dictionary = {}
## Sign id -> draw list (`StreetR2Signs`).
var specs: Dictionary = {}
## `[u0, u1, uid]` of the planned frontage faces along the street, in text order of the uid.
var spans: Array = []
## Sign id -> texture pixel size.
var sign_px: Dictionary = {}

var _cfg: StreetR2RenderConfigData = null
var _seed: int = 0
var _mats: StreetR2Materials = null
var _push: Dictionary = {}
var _tris: Dictionary = {}
var _faces: Dictionary = {}
var _facades: int = 0
## Module 19 (a): the buildings whose walls take the face wash (the far frontage row away from the route).
var _face: Dictionary = {}


## Builds the street of derive `derive` on `city` for the art seed `layout_seed`. `measure` is the glyph-box Callable of the sign rules
## (empty: the Godot fonts, `StreetR2SignCanvas.make_measure`).
static func build(city: Dictionary, derive: Dictionary, layout_seed: Variant, measure: Callable = Callable()) -> StreetR2Builder:
	var b := StreetR2Builder.new()
	b._build(city, derive, layout_seed, measure)
	return b


func _build(city: Dictionary, derive: Dictionary, layout_seed: Variant, measure_in: Callable) -> void:
	_cfg = StreetR2RenderConfigData.shipped()
	_seed = StreetR2Adapter.seed_of(layout_seed)
	_mats = StreetR2Materials.new()
	plan = StreetR2Adapter.plan_street(city, derive, layout_seed)
	_face = face_uids(plan, int(_cfg.facade["face_route_gap"]))
	var fonts := StreetR2SignCanvas.load_fonts()
	var measure := measure_in if measure_in.is_valid() else StreetR2SignCanvas.make_measure(fonts)
	root = Node3D.new()
	root.name = "StreetR2"
	for m: String in StreetR2Geometry.MATS:
		_tris[m] = 0
		_faces[m] = 0
	var street: Dictionary = derive["street"]
	var sa: Array = street["a"]
	var sc: Array = street["c"]
	var mid := [(float(sa[0]) + float(sc[0])) * 0.5, (float(sa[1]) + float(sc[1])) * 0.5]
	var terr := {}
	for cb: Dictionary in city["buildings"]:
		terr[cb["bid"]] = cb.get("terr", "")
	var merged := StreetR2Adapter.buildings(city)
	var radius := float(_cfg.facade["radius"])
	var near: Array = []
	for b: Dictionary in merged:
		var cx := (float(b["x0"]) + float(b["x1"])) * 0.5
		var cy := (float(b["y0"]) + float(b["y1"])) * 0.5
		if Vector2(cx - float(mid[0]), cy - float(mid[1])).length() <= radius:
			near.append(b)
	for b: Dictionary in near:
		var uid := String(b["uid"])
		if String((plan["kits"] as Dictionary).get(uid, "concrete_band")) != "concrete_band":
			_push[uid] = float(_cfg.facade["push"])
	for b: Dictionary in near:
		_facade(b, String(terr.get(b["uid"], "")), mid)
	_signs(measure, fonts)
	_props()
	for f: Dictionary in plan["front_faces"]:
		spans.append([minf(float(f["u0"]), float(f["u1"])), maxf(float(f["u0"]), float(f["u1"])), String(f["uid"])])
	summary["facades"] = _facades
	summary["faces"] = _faces
	summary["tris"] = _tris
	summary["digest"] = StreetR2Util.digest({"f": _faces, "t": _tris, "s": summary.get("signs"), "p": summary.get("props"), "c": summary.get("crowns")})


## The kerb lamps of the plan as light sources `[{pos, col}]` (world position at lamp head height `height`), for the street light rig.
func lamp_lights(height: float) -> Array:
	var out: Array = []
	for l: Dictionary in plan["lamps"]:
		var p: Array = l["pos"]
		out.append({"pos": Vector3(float(p[0]), height, -float(p[1])), "col": Color(float(l["col"][0]), float(l["col"][1]), float(l["col"][2]))})
	return out


## The facade push (BU) of building `uid`: kit facades stand this far out of the city's own wall.
func push_of(uid: String) -> float:
	return float(_push.get(uid, 0.0))


# --- Facades -----------------------------------------------------------------------------------------

func _wall_col(b: Dictionary, terr: String) -> Array:
	var fam: Array = _cfg.facade["families"]
	var base: Array = fam[absi(int(b["key"])) % fam.size()]
	var hue: Variant = (StreetR2ConfigData.shipped().palette_districts["hues"] as Dictionary).get(terr)
	if terr == "" or hue == null:
		return base.duplicate()
	var k := float(_cfg.facade["terr_mix"])
	var out: Array = []
	for i in 3:
		out.append(float(base[i]) * (1.0 - k) + float((hue as Array)[i]) * k)
	return out


func _facade(b: Dictionary, terr: String, mid: Array) -> void:
	var fc: Dictionary = _cfg.facade
	var uid := String(b["uid"])
	var z0 := float(b["z0"])
	var h := float(b["h"]) - z0
	if h < float(fc["min_h"]) or float(b["ts"]) < 0.99:
		return
	var kit := String((plan["kits"] as Dictionary).get(uid, "concrete_band"))
	var rh: Variant = (plan["rhythm"] as Dictionary).get(uid)
	var module := int((plan["modules"] as Dictionary).get(uid, 0))
	var nrm: Array = plan["nrm"]
	var q: Array = b["q"]
	var n := q.size()
	var cx := 0.0
	var cy := 0.0
	for p: Array in q:
		cx += float(p[0])
		cy += float(p[1])
	cx /= float(n)
	cy /= float(n)
	var rk := StreetR2Rng.stream(_seed, "facade_kit", [uid])
	var col := _wall_col(b, terr)
	var push := push_of(uid)
	var fl := StreetR2OneCity.floor_bu()
	var lite := Vector2(cx - float(mid[0]), cy - float(mid[1])).length() > float(fc["lite_radius"])
	var accs := StreetR2Kits.new_accs()
	accs["solid"] = StreetR2Faces.new()
	var ids: Array = [0]
	var trim: Variant = (plan["trims"] as Dictionary).get(uid)
	var any := false
	for i in n:
		var a: Array = q[i]
		var c: Array = q[(i + 1) % n]
		var dx := float(c[0]) - float(a[0])
		var dy := float(c[1]) - float(a[1])
		var flen := sqrt(dx * dx + dy * dy)
		if flen < float(fc["min_face"]):
			continue
		var ux := dx / flen
		var uy := dy / flen
		var nx := uy
		var ny := -ux
		if nx * (float(a[0]) - cx) + ny * (float(a[1]) - cy) < 0.0:
			nx = -nx
			ny = -ny
		if nx * -float(nrm[0]) + ny * -float(nrm[1]) <= float(fc["seen_dot"]):
			continue
		any = true
		var ap := [float(a[0]) + nx * push, float(a[1]) + ny * push]
		var cp := [float(c[0]) + nx * push, float(c[1]) + ny * push]
		if kit != "concrete_band":
			StreetR2Kits.kit_face(kit, ap, cp, z0, z0 + h, nx, ny, col, rk, accs, module, fl, null, lite, rh, ids)
		else:
			_concrete_windows(accs, a, c, flen, z0, h, nx, ny, rk, rh, fl)
		if trim != null:
			_trims(accs, trim, a, c, flen, z0, h, nx, ny, push, rk, fl)
	if not any:
		return
	var zt := z0 + h
	if kit != "concrete_band":
		var kinds := {}
		var ants: Array = []
		StreetR2Kits.roof_clutter(kit, q, zt, rk, accs["solid"], accs["neon"], kinds, ants, ids)
	if trim != null and bool((trim as Dictionary).get("roof", false)):
		_roof_rim(accs, trim, q, zt)
	_emit_building(uid, accs, Vector3(cx, zt * 0.5, -cy))
	_facades += 1


## The windows a concrete-band facade gets (the city keeps its own wall): lit panes on the rhythm's bays and floors, MATERIAL_SPEC section 3.
func _concrete_windows(accs: Dictionary, a: Array, c: Array, flen: float, z0: float, h: float, nx: float, ny: float, rk: StreetR2Rng, rh: Variant,
		fl: float) -> void:
	if rh == null or h <= 2.4:
		return
	var fc: Dictionary = _cfg.facade
	var cells: Array = fc["concrete_cells"]
	var zs := StreetR2Facade.floor_bounds(rh, z0, h, fl)
	var tones: Array = (rh as Dictionary).get("tones", [])
	var win: StreetR2Faces = accs["win"]
	var out := float(fc["win_outset"])
	var ux := (float(c[0]) - float(a[0])) / flen
	var uy := (float(c[1]) - float(a[1])) / flen
	for jf in range(1, zs.size() - 1):
		var mj := StreetR2Facade.floor_module(rh, jf, 0)
		for e: Array in StreetR2Facade.bay_edges(flen, float(cells[mj % cells.size()]), rh, jf):
			if rk.random() > float(fc["win_p"]):
				continue
			var bw := (float(e[1]) - float(e[0])) * flen
			var ww := maxf(float(fc["win_w_min"]), minf(bw * (float(fc["win_w_lo"]) + float(fc["win_w_span"]) * rk.random()), float(fc["win_w_max"])))
			var hh := minf(float(fc["win_h_lo"]) + float(fc["win_h_span"]) * rk.random(), (float(zs[jf + 1]) - float(zs[jf])) * float(fc["win_h_cap"]))
			var t0 := (float(e[0]) + float(e[1])) * flen * 0.5 - ww * 0.5
			var zw := float(zs[jf]) + float(fc["win_z"])
			var wc: Array = rk.choice(tones) if not tones.is_empty() else fc["fallback_win"]
			var s := float(fc["win_tone_lo"]) + float(fc["win_tone_span"]) * rk.random()
			var p0x := float(a[0]) + ux * t0 + nx * out
			var p0y := float(a[1]) + uy * t0 + ny * out
			var p1x := p0x + ux * ww
			var p1y := p0y + uy * ww
			win.face([[p0x, p0y, zw], [p1x, p1y, zw], [p1x, p1y, zw + hh], [p0x, p0y, zw + hh]], [float(wc[0]) * s, float(wc[1]) * s, float(wc[2]) * s], [0, 0, 0])


## The lit silhouette trims of a frontage building's street face (`frontage.silhouette`): floor bands every `band_every` floors broken by
## `band_gap_p`, and lit corner strips.
func _trims(accs: Dictionary, tr: Dictionary, a: Array, c: Array, flen: float, z0: float, h: float, nx: float, ny: float, push: float, rk: StreetR2Rng,
		fl: float) -> void:
	var fc: Dictionary = _cfg.facade
	var neon: StreetR2Faces = accs["neon"]
	var off := push + float(fc["trim_outset"])
	var ux := (float(c[0]) - float(a[0])) / flen
	var uy := (float(c[1]) - float(a[1])) / flen
	var seg := float(fc["trim_seg"])
	var nseg := maxi(1, int(ceil(flen / seg)))
	var every := int(tr["band_every"])
	var k := 1
	while z0 + float(k * every) * fl < z0 + h - 1.0:
		var z := z0 + float(k * every) * fl - 0.05
		for sg in nseg:
			if rk.random() < float(tr["gap_p"]):
				continue
			var u0 := float(sg) * seg
			var u1 := minf(flen, u0 + seg)
			neon.face(_strip(a, ux, uy, nx, ny, off, u0, u1, z, z + float(fc["trim_band_h"])), tr["col"], [0, 0, 0])
		k += 1
	if bool(tr.get("corner", false)):
		var cw := float(fc["trim_corner_w"])
		neon.face(_strip(a, ux, uy, nx, ny, off, 0.0, cw, z0, z0 + h), tr["col2"], [0, 0, 0])
		neon.face(_strip(a, ux, uy, nx, ny, off, flen - cw, flen, z0, z0 + h), tr["col2"], [0, 0, 0])


static func _strip(a: Array, ux: float, uy: float, nx: float, ny: float, off: float, u0: float, u1: float, z0: float, z1: float) -> Array:
	var p0x := float(a[0]) + ux * u0 + nx * off
	var p0y := float(a[1]) + uy * u0 + ny * off
	var p1x := float(a[0]) + ux * u1 + nx * off
	var p1y := float(a[1]) + uy * u1 + ny * off
	return [[p0x, p0y, z0], [p1x, p1y, z0], [p1x, p1y, z1], [p0x, p0y, z1]]


func _roof_rim(accs: Dictionary, tr: Dictionary, q: Array, zt: float) -> void:
	var fc: Dictionary = _cfg.facade
	var neon: StreetR2Faces = accs["neon"]
	var z := zt + float(fc["rim_lift"])
	for i in q.size():
		var p: Array = q[i]
		var r: Array = q[(i + 1) % q.size()]
		neon.faces.append_array(StreetR2Geometry.beam_faces([p[0], p[1], z], [r[0], r[1], z], float(fc["rim_w"]), tr["col"]))


## Merges the accumulators of one building into a mesh node (one surface per material).
func _emit_building(uid: String, accs: Dictionary, centre: Vector3) -> void:
	var bucket := StreetR2Geometry.new_bucket()
	for m: String in ["conc", "glass", "panel", "win", "neon"]:
		StreetR2Geometry.add(bucket, m, (accs[m] as StreetR2Faces).faces)
	var solid: StreetR2Faces = accs["solid"]
	StreetR2Geometry.add(bucket, "solid", solid.faces)
	var sides := int(_cfg.facade["prism_sides"])
	for pr: Array in solid.prims:
		StreetR2Geometry.add(bucket, "solid", StreetR2Geometry.prim_faces(pr, sides))
	_add_mesh("bld_" + uid, bucket, centre, not _face.has(uid))


## Module 19 (a): the buildings that take the face wash: the far frontage row (plan.front, the plate's lit slabs across the street)
## minus the route columns (plan.route) and their `gap` neighbours either side, so the route UI never sits on a lit sheet; the
## near side and the blocks behind never take it.
static func face_uids(p: Dictionary, gap: int) -> Dictionary:
	var front: Array = p.get("front", [])
	var out: Dictionary = {}
	for uid: Variant in front:
		out[String(uid)] = true
	for uid: Variant in p.get("route", []):
		out.erase(String(uid))
		var i := front.find(uid)
		if i < 0:
			continue
		for k in range(maxi(0, i - gap), mini(front.size(), i + gap + 1)):
			out.erase(String(front[k]))
	return out


func _add_mesh(node_name: String, bucket: Dictionary, centre: Vector3, plain: bool = false) -> void:
	var surf := {}
	var mesh := StreetR2Geometry.mesh(bucket, centre, surf)
	if mesh == null:
		return
	for m: String in StreetR2Geometry.MATS:
		_faces[m] = int(_faces[m]) + (bucket[m] as Array).size()
		_tris[m] = int(_tris[m]) + StreetR2Geometry.tri_count(bucket[m])
	for m: String in surf:
		mesh.surface_set_material(int(surf[m]), _mats.surface_plain(m) if plain else _mats.surface(m))
	var mi := MeshInstance3D.new()
	mi.name = node_name
	mi.mesh = mesh
	root.add_child(mi)


# --- Signs, props, lamps, crowns ---------------------------------------------------------------------

func _signs(measure: Callable, fonts: Dictionary) -> void:
	specs = StreetR2Signs.make(plan, measure)
	var boards := StreetR2SignBoards.new(root, _mats, fonts)
	var frames := StreetR2Geometry.new_bucket()
	var kinds := {}
	for s: Dictionary in plan["signs"]:
		var push := push_of(String(s["key"]))
		boards.add(s, specs[s["id"]], push)
		kinds[s["kind"]] = int(kinds.get(s["kind"], 0)) + 1
		if s["kind"] != "shopfront":
			StreetR2Geometry.add(frames, "solid", StreetR2SignBoards.frame_faces(s, push))
	_add_mesh("sign_frames", frames, Vector3.ZERO)
	sign_px = boards.textures
	summary["signs"] = {"count": (plan["signs"] as Array).size(), "kinds": kinds}


func _props() -> void:
	var props := StreetR2Props.new(_mats)
	var counts := {}
	for p: Dictionary in plan["props"]:
		var file := props.add_facade_prop(p, push_of(String(p["key"])))
		if file != "":
			counts[file] = int(counts.get(file, 0)) + 1
	var post_h := float(StreetR2ConfigData.shipped().streets_light["lamp_post_h"])
	for l: Dictionary in plan["lamps"]:
		props.add_lamp(l, int(plan["axis"]), float(plan["line"]), post_h)
	summary["props"] = counts
	summary["lamps"] = (plan["lamps"] as Array).size()
	_crowns(props)
	props.flush(root)


func _crowns(props: StreetR2Props) -> void:
	var cfg: Dictionary = _cfg.props
	var crowns: Dictionary = cfg["crowns"]
	var floor_bu := StreetR2OneCity.floor_bu()
	var nrm: Array = plan["nrm"]
	var counts := {}
	for c: Dictionary in plan["crowns"]:
		var kind := String(c["kind"])
		var file := String(crowns[kind])
		var bb := props.aabb_of(file)
		var box: Array = c["box"]
		var x0 := float(box[0])
		var y0 := float(box[1])
		var x1 := float(box[2])
		var y1 := float(box[3])
		var w := x1 - x0
		var d := y1 - y0
		var top := float(c["top"])
		var cxp := (x0 + x1) * 0.5
		var cyp := (y0 + y1) * 0.5
		var sc := Vector3.ONE
		var basis := Basis()
		var pos := Vector3.ZERO
		var cen := bb.get_center()
		match kind:
			"spire":
				var k := float(c["h"]) / bb.size.y
				sc = Vector3(k, k, k)
				basis = Basis.from_scale(sc)
				pos = Vector3(cxp - cen.x * k, top, -cyp - cen.z * k)
			"setback":
				var fx := w * 0.6 / bb.size.x
				var fz := d * 0.6 / bb.size.z
				var fy := float(c["floors"]) * floor_bu * float(cfg["crown_floors_k"]) / bb.size.y
				basis = Basis.from_scale(Vector3(fx, fy, fz))
				pos = Vector3(cxp - cen.x * fx, top, -cyp - cen.z * fz)
			"roof_box":
				var fx := w * 0.45 / bb.size.x
				var fz := d * 0.45 / bb.size.z
				basis = Basis.from_scale(Vector3(fx, 1.0, fz))
				pos = Vector3(cxp - cen.x * fx, top, -cyp - cen.z * fz)
			_:
				var bw := minf(w, 7.0) * 0.85
				var k := bw / bb.size.x
				var out_x := -float(nrm[0])
				var out_y := -float(nrm[1])
				var axis := int(plan["axis"])
				var out := out_y if axis == 0 else out_x
				basis = StreetR2Props.wall_basis(axis, signf(out), Vector3(k, k, k))
				var edge := (y0 if out < 0.0 else y1) if axis == 0 else (x0 if out < 0.0 else x1)
				var along := cxp if axis == 0 else cyp
				pos = Vector3(along, top, -edge) if axis == 0 else Vector3(edge, top, -along)
		props.add(file, Transform3D(basis, pos), Color(0, 0, 0, 0))
		counts[kind] = int(counts.get(kind, 0)) + 1
	summary["crowns"] = counts
