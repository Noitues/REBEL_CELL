extends RefCounted
## LOOK-TOOLBOX module 10 sheet (b), lab only: draws the street r2 plan's megastructure (`plan.mega`, dressing.signs) that the Godot
## frontage plans but does not build. A port of art-pass street_r2 r2_build.py "the megastructure" (globe: a wire sphere on a post with a
## tilted orbit ring; arch: a curved textured board on two legs; holo: a flat textured panel), with the plate's emission
## (mega_emit x signs emit_k x signs mega_k, r2_cycles.py:207-215). Not game code: na23_lab --mega=1 only.

const POST_COL := [0.22, 0.22, 0.28]
const LEG_COL := [0.2, 0.2, 0.25]


## Adds the megastructure of `fr` (a built `StreetR2Builder`) under its root, facing the street normal `nrm` (plan [x, y]).
## Returns a one-line description, or "" when the plan has none.
static func draw(fr: StreetR2Builder, nrm: Array) -> String:
	var mg: Variant = fr.plan.get("mega")
	if mg == null:
		return ""
	var g: Dictionary = mg
	var pos: Array = g["pos"]
	var mx := float(pos[0])
	var my := float(pos[1])
	var mz := float(pos[2])
	var s := float(g["size"])
	var col: Array = g["col"]
	var ox := -float(nrm[0])
	var oy := -float(nrm[1])
	var rx := -oy
	var ry := ox
	var b := StreetR2Geometry.new_bucket()
	var cfg := StreetR2RenderConfigData.shipped()
	var emit := float(g["emit"]) * float(cfg.signs["emit_k"]) * float(cfg.signs["mega_k"])
	if String(g["kind"]) == "globe":
		var r := s * 0.5
		var cz := mz + r * 0.4 + r
		StreetR2Geometry.add(b, "solid", StreetR2Geometry.beam_faces([mx, my, mz], [mx, my, cz - r * 0.6], 0.5, POST_COL))
		for lat: float in [-0.66, -0.33, 0.0, 0.33, 0.66]:
			var rr := r * cos(lat * PI / 2.0)
			var zz := cz + r * sin(lat * PI / 2.0)
			for m in 24:
				var a0 := TAU * m / 24.0
				var a1 := TAU * (m + 1) / 24.0
				StreetR2Geometry.add(b, "neon", StreetR2Geometry.beam_faces([mx + rr * cos(a0), my + rr * sin(a0), zz], [mx + rr * cos(a1), my + rr * sin(a1), zz], 0.14, col))
		for mer in 8:
			var ph := PI * mer / 8.0
			for m in 24:
				var a0 := TAU * m / 24.0
				var a1 := TAU * (m + 1) / 24.0
				StreetR2Geometry.add(b, "neon", StreetR2Geometry.beam_faces(
						[mx + r * cos(a0) * cos(ph), my + r * cos(a0) * sin(ph), cz + r * sin(a0)],
						[mx + r * cos(a1) * cos(ph), my + r * cos(a1) * sin(ph), cz + r * sin(a1)], 0.12, col))
		var tilt := deg_to_rad(22.0)
		var rc: Array = []
		for v: float in col:
			rc.append(minf(1.0, v * 0.6 + 0.4))
		for m in 48:
			var p0 := _ring(TAU * m / 48.0, r, mx, my, cz, rx, ry, ox, oy, tilt)
			var p1 := _ring(TAU * (m + 1) / 48.0, r, mx, my, cz, rx, ry, ox, oy, tilt)
			StreetR2Geometry.add(b, "neon", StreetR2Geometry.beam_faces(p0, p1, 0.18, rc))
	else:
		var arch := String(g["kind"]) == "arch"
		var wv := s
		var hv := wv / (2.4 if arch else 1.78)
		var zb := mz + 1.6
		for t: float in [-0.42, 0.42]:
			var lx := mx + rx * wv * t
			var ly := my + ry * wv * t
			StreetR2Geometry.add(b, "solid", StreetR2Geometry.beam_faces([lx, ly, mz], [lx, ly, zb + hv * 0.2], 0.35, LEG_COL))
		var nseg := 16 if arch else 1
		var bulge := wv * 0.10 if arch else 0.0
		var vs: Array = []
		var verts := PackedVector3Array()
		var uvs := PackedVector2Array()
		for k in nseg + 1:
			var t := float(k) / nseg - 0.5
			var off := bulge * (1.0 - pow(2.0 * t, 2.0))
			var arc := hv * 0.18 * (1.0 - pow(2.0 * t, 2.0))
			var x := mx + rx * wv * t + ox * off
			var y := my + ry * wv * t + oy * off
			vs.append([x, y, zb + arc])
			vs.append([x, y, zb + hv + arc])
			verts.append(StreetR2Geometry.world([x, y, zb + arc]))
			verts.append(StreetR2Geometry.world([x, y, zb + hv + arc]))
			uvs.append(Vector2(float(k) / nseg, 1.0))
			uvs.append(Vector2(float(k) / nseg, 0.0))
		var idx := PackedInt32Array()
		for k in nseg:
			idx.append_array([2 * k, 2 * k + 2, 2 * k + 3, 2 * k, 2 * k + 3, 2 * k + 1])
		for k in nseg:
			for e in 2:
				StreetR2Geometry.add(b, "neon", StreetR2Geometry.beam_faces(vs[2 * k + e], vs[2 * k + 2 + e], 0.16, col))
		var spec: Dictionary = fr.specs["mega"]
		var px := StreetR2SignCanvas.size_of(spec, 2.4 if arch else 16.0 / 9.0)
		var vp := SubViewport.new()
		vp.name = "tex_mega"
		vp.size = px
		vp.disable_3d = true
		vp.transparent_bg = false
		vp.render_target_update_mode = SubViewport.UPDATE_ONCE
		var canvas := StreetR2SignCanvas.new()
		canvas.setup(spec, StreetR2SignCanvas.load_fonts(), px)
		vp.add_child(canvas)
		fr.root.add_child(vp)
		var arr: Array = []
		arr.resize(Mesh.ARRAY_MAX)
		arr[Mesh.ARRAY_VERTEX] = verts
		arr[Mesh.ARRAY_TEX_UV] = uvs
		arr[Mesh.ARRAY_INDEX] = idx
		var st := SurfaceTool.new()
		st.create_from_arrays(arr)
		st.generate_normals()
		var am := st.commit()
		am.surface_set_material(0, fr._mats.sign_board(vp.get_texture(), emit))
		var mi := MeshInstance3D.new()
		mi.name = "mega_board"
		mi.mesh = am
		fr.root.add_child(mi)
	fr._add_mesh("mega", b, Vector3.ZERO)
	return "%s size %.1f at (%.1f, %.1f, %.1f) emit %.2f key %s" % [g["kind"], s, mx, my, mz, emit, g["key"]]


static func _ring(a: float, r: float, mx: float, my: float, cz: float, rx: float, ry: float, ox: float, oy: float, tilt: float) -> Array:
	var x := r * 1.45 * cos(a)
	var y := r * 1.45 * sin(a)
	return [mx + x * rx + y * ox * cos(tilt), my + x * ry + y * oy * cos(tilt), cz + y * sin(tilt) + x * 0.18]


## Lab only: when the plan has no megastructure, re-runs plan_pass's candidate loop (street_r2_rules.gd "megastructure") counting the
## first test each building fails, then places one on the tallest building that passes the far band and the central 2/3 (no height, y, DECISION-frame or headroom test)
## (the rule's kind / colour / ad streams). Writes it into fr.plan.mega and fr.specs.mega. Returns the report line.
static func diagnose(fr: StreetR2Builder, city: Dictionary, derive: Dictionary, layout_seed: Variant) -> String:
	if fr.plan.get("mega") != null:
		return "plan has one"
	var x := StreetR2Adapter.r2_input(city, derive, layout_seed)
	var D: Dictionary = x["D"]
	var B: Array = x["merged"]
	var seed: Variant = x["seed"]
	var ov: Dictionary = D["overview"]
	var dec: Dictionary = D["decision"]
	var nrm: Array = D["nrm"]
	var sa: Array = D["a"]
	var axis := 0 if absf(float(sa[1]) - float((D["c"] as Array)[1])) < 1e-6 else 1
	var line := float(sa[1 - axis])
	var rset := {}
	for u: String in D["column_uids"]:
		rset[u] = true
	var W_ := StreetR2OneCity.frame_w()
	var H_ := StreetR2OneCity.frame_h()
	var front: Array = StreetR2OneCity.frontage(B, sa, D["c"], int(D["side"]))
	var front_top := float(front[0]["h"])
	for b: Dictionary in front:
		front_top = maxf(front_top, float(b["h"]))
	var loc: Array = ov["persp"]["loc"]
	var lens := float(ov["persp"]["lens"])
	var S: Dictionary = StreetR2ConfigData.shipped().dressing_signs
	var why := {"route/raised": 0, "far 24..170": 0, "h < 0.8 front_top": 0, "x off central 2/3": 0, "y >= 0.45": 0, "in DECISION": 0, "headroom": 0, "pass": 0}
	var relaxed: Array = []
	for b: Dictionary in B:
		if rset.has(b["uid"]) or float(b["z0"]) > StreetR2Rules.NEAR_BASE:
			why["route/raised"] += 1
			continue
		var far := StreetR2Rules._far_of(b, axis, line, nrm)
		if not (24.0 < far and far < 170.0):
			why["far 24..170"] += 1
			continue
		var short := float(b["h"]) < front_top * 0.8
		var cx := (float(b["x0"]) + float(b["x1"])) / 2
		var cy := (float(b["y0"]) + float(b["y1"])) / 2
		var p1 := StreetR2OneCity.proj(ov, [cx, cy, b["h"]])
		var px := float(p1[0]) / W_
		var py := float(p1[1]) / H_
		if not (1.0 / 6.0 < px and px < 5.0 / 6.0):
			why["x off central 2/3"] += 1
			continue
		relaxed.append([float(b["h"]), String(b["uid"]), b, cx, cy])
		if py >= 0.45:
			why["y >= 0.45"] += 1
			continue
		if short:
			why["h < 0.8 front_top"] += 1
			continue
		var p2 := StreetR2OneCity.proj(dec, [cx, cy, b["h"]])
		if 0.0 < float(p2[0]) / W_ and float(p2[0]) / W_ < 1.0 and 0.0 < float(p2[1]) / H_ and float(p2[1]) / H_ < 1.0:
			why["in DECISION"] += 1
			continue
		var sz := StreetR2Rules._mega_size(loc, lens, W_, cx, cy, float(b["h"]))
		var p3 := StreetR2OneCity.proj(ov, [cx, cy, float(b["h"]) + 1.6 + sz * 0.75])
		if float(p3[1]) / H_ <= float(S["mega_headroom"]):
			why["headroom"] += 1
			continue
		why["pass"] += 1
	var rep := "front_top %.1f, first failing test per building: %s" % [front_top, str(why)]
	if relaxed.is_empty():
		return rep + "; no relaxed spot either"
	relaxed.sort_custom(func(a: Array, c: Array) -> bool: return a[0] > c[0] or (a[0] == c[0] and String(a[1]) < String(c[1])))
	var best: Array = relaxed[0]
	var key: String = best[1]
	var r_ := StreetR2Rng.stream(seed, "mega", [key])
	var mk: Array = S["mega_kinds"]
	var kind: String = mk[r_.randrange(mk.size())]
	var mcols: Array = [[0.35, 0.9, 1.0], [1.0, 0.25, 0.65], [1.0, 0.65, 0.2]]
	var col: Array = (mcols[r_.randrange(3)] as Array).duplicate()
	var h := float(best[0])
	var size := StreetR2Rules._mega_size(loc, lens, W_, float(best[3]), float(best[4]), h)
	var ads: Array = StreetR2ConfigData.shipped().ads["mega"]
	var ad: String = ads[r_.randrange(ads.size())]
	fr.plan["mega"] = {"kind": kind, "key": key, "pos": [best[3], best[4], h], "size": size, "col": col, "district": "",
		"tex": {"style": "ad", "ad": ad, "word": "", "sub": "", "seed": StreetR2Rng.art_seed(seed, "tex", [key, "mega"])}, "emit": S["mega_emit"]}
	fr.specs["mega"] = StreetR2Signs.ad(ad, 2.4 if kind == "arch" else 16.0 / 9.0)
	return rep + "; lab fallback on %s (h %.1f, %d relaxed spots)" % [key, h, relaxed.size()]
