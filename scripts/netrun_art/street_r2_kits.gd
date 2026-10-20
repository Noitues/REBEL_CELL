class_name StreetR2Kits
extends RefCounted
## Street r2 facade kits (twin of `tools/netrun_art/r2/kits.py`, the plate's per-cell generators): glass_curtain, panel_grille,
## lit_atrium and the roof clutter. A face is split into cells; the generators write records into `StreetR2Faces` accumulators by material
## (conc, glass, panel, win, neon). Draws come from the stream passed in, in the order the Python draws them.

static var _k: Dictionary = {}


static func _cfg() -> Dictionary:
	if _k.is_empty():
		_k = StreetR2ConfigData.shipped().kits
	return _k


## One accumulator per material.
static func new_accs() -> Dictionary:
	var d := {}
	for m: String in ["conc", "glass", "panel", "win", "neon"]:
		d[m] = StreetR2Faces.new()
	return d


static func _scale(col: Array, k: float) -> Array:
	var out: Array = []
	for v: float in col:
		out.append(v * k)
	return out


static func _cell_pts(a: Array, c: Array, z0: float, z1: float, u0: float, u1: float, nx: float, ny: float, off: float) -> Array:
	var ax := float(a[0])
	var ay := float(a[1])
	var dx := float(c[0]) - ax
	var dy := float(c[1]) - ay
	var p0x := ax + dx * u0 + nx * off
	var p0y := ay + dy * u0 + ny * off
	var p1x := ax + dx * u1 + nx * off
	var p1y := ay + dy * u1 + ny * off
	return [[p0x, p0y, z0], [p1x, p1y, z0], [p1x, p1y, z1], [p0x, p0y, z1]]


static func _boxq(acc: StreetR2Faces, a: Array, c: Array, z0: float, z1: float, u0: float, u1: float, nx: float, ny: float, d0: float, d1: float, col: Array, bid: Variant) -> void:
	var f := _cell_pts(a, c, z0, z1, u0, u1, nx, ny, d1)
	var b := _cell_pts(a, c, z0, z1, u0, u1, nx, ny, d0)
	acc.face(f, col, bid, 0.5)
	acc.face([b[1], b[0], f[0], f[1]], col, bid, 0.45)     # bottom
	acc.face([f[3], f[2], b[2], b[3]], col, bid, 0.55)     # top


## Draw one face (a -> c along the bottom, z0..z1) in `kit` into `accs`. `rh` = the building's rhythm record (null = the uniform grid),
## `ids` = a counter Array [n] for part ids.
static func kit_face(kit: String, a: Array, c: Array, z0: float, z1: float, nx: float, ny: float, col: Array, r: StreetR2Rng, accs: Dictionary,
		module: int = 0, fl: float = 1.9, lit_low: Variant = null, lite: bool = false, rh: Variant = null, ids: Array = [0]) -> void:
	var kc := _cfg()
	var kit_w: Array = kc["kit_w"][kit]
	var glass_col: Array = kc["glass_col"]
	var metal: Array = kc["metal_col"]
	var dx := float(c[0]) - float(a[0])
	var dy := float(c[1]) - float(a[1])
	var L := sqrt(dx * dx + dy * dy)
	var h := z1 - z0
	if L < 0.5 or h < 0.5:
		return
	var zs := StreetR2Facade.floor_bounds(rh, z0, h, fl)
	var nf := zs.size() - 1
	var mods: Array = []
	for j in nf:
		mods.append(StreetR2Facade.floor_module(rh, j, module))
	var edges: Array = []
	for j in nf:
		if j > 0 and mods[j] == mods[j - 1]:
			edges.append(edges[edges.size() - 1])
		else:
			edges.append(StreetR2Facade.bay_edges(L, float(kit_w[int(mods[j]) % 3]), rh, j))
	var ins: Array = []
	for j in nf:
		ins.append(StreetR2Facade.floor_inset(rh, j))
	ids[0] = int(ids[0]) + 1
	var bid: int = ids[0]
	var floor0 := StreetR2Util.py_round0(z0 / fl)
	var ac_: Array = (rh["acc"] as Array).duplicate() if rh != null else [0.4, 0.8, 1.0]
	var wt: Array = kc["win_cols"]
	if rh != null and rh.get("tones") != null and not (rh["tones"] as Array).is_empty():       # at most 2 window tones per building
		wt = rh["tones"]
	var rel := float(rh.get("relief", 0.0)) if rh != null else 0.0                 # per-cell depth relief (geometry, not colour)
	var tlo := 1.0
	var thi := 1.0
	if rh != null and rh.get("tone") != null and not (rh["tone"] as Array).is_empty():
		tlo = float(rh["tone"][0])
		thi = float(rh["tone"][1])
	var lit_floor: Array = []
	if kit == "glass_curtain":
		for _j in nf:
			lit_floor.append(r.random() < 0.22)
	var lit_pal: Array = []
	var low := 0
	var win: StreetR2Faces = accs["win"]
	var panel: StreetR2Faces = accs["panel"]
	var conc: StreetR2Faces = accs["conc"]
	var glass: StreetR2Faces = accs["glass"]
	var zero3: Array = [0, 0, 0]
	for j in nf:
		var za := float(zs[j])
		var zb := float(zs[j + 1])
		var ij := float(ins[j])
		var ed: Array = edges[j]
		for i in ed.size():
			var u0 := float(ed[i][0])
			var u1 := float(ed[i][1])
			var du := u1 - u0
			var m := int(mods[j])
			if kit == "glass_curtain":
				var k1 := r.uniform(tlo, thi)
				glass.face(_cell_pts(a, c, za, zb, u0, u1, nx, ny, 0.0 - ij), [minf(1.0, float(glass_col[0]) * k1), minf(1.0, float(glass_col[1]) * k1), minf(1.0, float(glass_col[2]) * k1)], bid, 0.5)
				var mw := 0.06 / maxf(L, 1e-3)
				if not lite and (m != 1 or i % 2 == 0) and r.random() > 0.3:       # mullions are not on every bay edge
					var wm: float = float(r.choice([1, 1, 2, 3]))
					panel.face(_cell_pts(a, c, za, zb, u0, u0 + mw * wm, nx, ny, 0.05 - ij), metal, bid, 0.5)
				if not lite and r.random() > 0.2:
					var zt2 := minf(zb, za + r.uniform(0.08, 0.36))
					panel.face(_cell_pts(a, c, za, zt2, u0, u1, nx, ny, 0.04 - ij), metal, bid, 0.5)
				if bool(lit_floor[j]) and r.random() < 0.85:
					var sv := 0.5 + 0.5 * r.random()
					var wc: Array = [0.78, 0.9, 1.0] if r.random() < 0.7 else [0.55, 1.0, 0.9]
					win.face(_cell_pts(a, c, za + 0.35, zb - 0.3, u0 + 0.06 * du, u1 - 0.06 * du, nx, ny, 0.02 - ij), _scale(wc, sv), zero3, 0.5)
				elif r.random() < 0.08:
					var tone: Array = r.choice(wt)
					var cc: Array = []
					for v: float in tone:
						cc.append(v * (0.4 + 0.4 * r.random()))
					win.face(_cell_pts(a, c, za + 0.4, zb - 0.35, u0 + 0.12 * du, u1 - 0.12 * du, nx, ny, 0.02 - ij), cc, zero3, 0.5)
			elif kit == "panel_grille":
				var slats := 2 + m
				var pc := _scale(col, 0.9)
				var dk := _scale(col, 0.55)
				var off := r.uniform(0.0, rel)
				var cellp := _cell_pts(a, c, za, zb, u0, u1, nx, ny, off - ij)
				var k2 := r.uniform(tlo, thi)
				var fjv := 0.4 + 0.2 * r.random()
				panel.face(cellp, [minf(1.0, float(pc[0]) * k2), minf(1.0, float(pc[1]) * k2), minf(1.0, float(pc[2]) * k2)], bid, fjv)
				var zz := zb - r.uniform(0.08, 0.2)
				var n_slats := 0 if lite else slats
				for _k in n_slats:               # slats at irregular pitch and thickness (a periodic louvre repeats)
					var th := r.uniform(0.04, 0.1)
					if zz - th > za:
						_boxq(panel, a, c, zz - th, zz, u0, u1, nx, ny, 0.0 - ij, r.uniform(0.12, 0.26) - ij, dk, bid)
					zz -= r.uniform(0.14, 0.32)
				if r.random() < 0.35:
					var sv := 0.7 + 0.3 * r.random()
					var um := (u0 + u1) / 2
					var hw := minf(0.3 / maxf(L, 1e-3), du * 0.4)
					var tone: Array = r.choice(wt)
					win.face(_cell_pts(a, c, za + 0.45, minf(zb - 0.1, za + 1.0), um - hw, um + hw, nx, ny, 0.03 - ij), _scale(tone, sv), zero3, 0.5)
				if r.random() < 0.05 and j > 0:
					var um := (u0 + u1) / 2
					var hw := minf(0.35 / maxf(L, 1e-3), du * 0.4)
					_boxq(conc, a, c, za + 0.05, za + 0.5, um - hw, um + hw, nx, ny, 0.0 - ij, 0.45 - ij, [0.32, 0.32, 0.35], bid)
			elif kit == "lit_atrium":
				if j == 0 and i == 0:
					var warm := r.random() < 0.55
					var lit_a: Array = [1.0, 0.74, 0.46] if warm else [0.45, 0.95, 1.0]
					var pals: Array = [[1.0, 0.3, 0.7], [0.3, 0.85, 1.0], [1.0, 0.6, 0.2], [0.7, 0.45, 1.0]]
					var lit_b: Array = r.choice(pals)
					lit_pal = [lit_a, lit_b]
					low = int(lit_low) if lit_low != null else 2 + r.randrange(2)
				var lc: Array = lit_pal[0]
				var sc: Array = lit_pal[1]
				var every := 2 + m
				if floor0 + j < low:
					var cc: Array = []
					for v: float in lc:
						cc.append(v * (0.55 + 0.25 * r.random()))
					win.face(_cell_pts(a, c, za + 0.08, zb - 0.08, u0 + 0.03 * du, u1 - 0.03 * du, nx, ny, 0.0 - ij), cc, zero3, 0.5)
					panel.face(_cell_pts(a, c, za, zb, u0, minf(u1, u0 + 0.07 / maxf(L, 1e-3)), nx, ny, 0.04 - ij), metal, bid, 0.5)
					panel.face(_cell_pts(a, c, zb - 0.1, zb, u0, u1, nx, ny, 0.04 - ij), metal, bid, 0.5)
				else:
					var off := r.uniform(0.0, rel)
					var cellp := _cell_pts(a, c, za, zb, u0, u1, nx, ny, off - ij)
					var k3 := r.uniform(tlo, thi)
					var fjv := 0.45 + 0.1 * r.random()
					conc.face(cellp, [minf(1.0, float(col[0]) * k3), minf(1.0, float(col[1]) * k3), minf(1.0, float(col[2]) * k3)], bid, fjv)
					if i % every == 0:
						var hw := minf(0.11 / maxf(L, 1e-3), du * 0.4)
						win.face(_cell_pts(a, c, za, zb, (u0 + u1) / 2 - hw, (u0 + u1) / 2 + hw, nx, ny, 0.03 - ij), _scale(sc, 0.75), zero3, 0.5)
					elif r.random() < 0.1:
						var tone: Array = r.choice(wt)
						win.face(_cell_pts(a, c, za + 0.5, zb - 0.4, u0 + 0.2 * du, u1 - 0.2 * du, nx, ny, 0.02 - ij), _scale(tone, 0.6), zero3, 0.5)
	if rh != null and not lite:
		# setback ledge: a slab and a lit lip where the facade steps back
		var sb: Variant = rh.get("setback")
		if sb != null and 0 < int(sb["floor"]) and int(sb["floor"]) < nf:
			var zl := float(zs[int(sb["floor"])])
			var d := float(sb["d"])
			var q0 := _cell_pts(a, c, zl, zl, 0.0, 1.0, nx, ny, 0.0)
			var q1 := _cell_pts(a, c, zl, zl, 0.0, 1.0, nx, ny, -d)
			conc.face([q0[0], q0[1], q1[1], q1[0]], _scale(col, 0.8), bid, 0.5)
			var ln := _cell_pts(a, c, zl - 0.06, zl + 0.02, 0.0, 1.0, nx, ny, 0.04)
			(accs["neon"] as StreetR2Faces).face(ln, ac_, zero3, 0.5)
		# balconies: slab, rail, a lit door behind
		for bc: Dictionary in rh.get("balc", []):
			var j := int(bc["floor"])
			if j >= nf or int(bc["floor"]) < 1:
				continue
			var wf := minf(0.9, float(bc["w"]) / L)
			var u0 := maxf(0.02, float(bc["c"]) - wf / 2)
			var u1 := minf(0.98, u0 + wf)
			var zf := float(zs[j])
			var dp := float(bc["depth"])
			var ij := float(ins[j])
			_boxq(conc, a, c, zf, zf + 0.14, u0, u1, nx, ny, -ij, dp - ij, _scale(col, 0.85), bid)
			var rz := zf + 0.14 + 0.85
			panel.face(_cell_pts(a, c, rz, rz + 0.05, u0, u1, nx, ny, dp - ij), metal, bid, 0.5)
			for pu: float in [u0, u1]:
				panel.face(_cell_pts(a, c, zf + 0.14, rz, pu, pu + 0.04 / maxf(L, 1e-3), nx, ny, dp - ij), metal, bid, 0.5)
			if bool(bc["lit"]) and float(zs[j + 1]) - zf > 1.2:
				win.face(_cell_pts(a, c, zf + 0.15, minf(float(zs[j + 1]) - 0.2, zf + 1.6), u0 + wf * 0.25, u1 - wf * 0.25, nx, ny, 0.045 - ij), _scale(ac_, 0.7), zero3, 0.5)


## Roof clutter by kit: vent stacks, AC units, a dish, an antenna with a lamp. `kinds` collects the kinds (a Dictionary used as a set);
## solid pieces are primitive records in `acc_s`, the antenna lamp is a face in `acc_n`, `ants` collects the aircraft-light positions.
static func roof_clutter(kit: String, top: Array, zt: float, r: StreetR2Rng, acc_s: StreetR2Faces, acc_n: StreetR2Faces, kinds: Dictionary, ants: Array,
		ids: Array = [0]) -> void:
	var xs: Array = []
	var ys: Array = []
	for p: Array in top:
		xs.append(p[0])
		ys.append(p[1])
	var x0 := float(StreetR2Util.amin(xs))
	var x1 := float(StreetR2Util.amax(xs))
	var y0 := float(StreetR2Util.amin(ys))
	var y1 := float(StreetR2Util.amax(ys))
	if x1 - x0 < 2.2 or y1 - y0 < 2.2:
		return
	if kit == "glass_curtain" or kit == "panel_grille":
		for _i in r.randint(1, 3):                       # vent stacks
			var vx := r.uniform(x0 + 0.5, x1 - 0.5)
			var vy := r.uniform(y0 + 0.5, y1 - 0.5)
			var zz := zt + r.uniform(1.0, 2.4)
			var rad := r.uniform(0.25, 0.45)
			acc_s.prim("cyl36", [vx, vy, zt, zz, rad, [0.3, 0.3, 0.34]])
		kinds["vent_stack"] = true
	if kit == "panel_grille" or kit == "lit_atrium":
		for _i in r.randint(1, 3):                       # AC units
			var vx := r.uniform(x0 + 0.4, x1 - 1.3)
			var vy := r.uniform(y0 + 0.4, y1 - 1.1)
			acc_s.prim("box", [vx, vy, zt, vx + 0.9, vy + 0.7, zt + 0.55, [0.34, 0.34, 0.38]])
		kinds["ac"] = true
	if (kit == "lit_atrium" or kit == "glass_curtain") and r.random() < 0.6:   # dish on a stub
		var dx := r.uniform(x0 + 1.0, x1 - 1.0)
		var dy := r.uniform(y0 + 1.0, y1 - 1.0)
		acc_s.prim("beam", [[dx, dy, zt], [dx, dy, zt + 1.0], 0.14, [0.25, 0.25, 0.3]])
		var rr := r.uniform(0.6, 1.0)
		var pts: Array = []
		for k in 10:
			var ang := 2 * PI * k / 10
			pts.append([dx + rr * cos(ang), dy - 0.3, zt + 1.4 + rr * sin(ang)])
		ids[0] = int(ids[0]) + 1
		acc_s.face(pts, [0.55, 0.55, 0.6], ids[0])
		kinds["dish"] = true
	if r.random() < 0.35:                                     # antenna with a red light
		var ax := (x0 + x1) / 2 + r.uniform(-0.5, 0.5)
		var ay := (y0 + y1) / 2
		var hh := r.uniform(2.5, 5.5)
		acc_s.prim("beam", [[ax, ay, zt], [ax, ay, zt + hh], 0.12, [0.25, 0.25, 0.3]])
		acc_n.face([[ax - 0.22, ay, zt + hh], [ax + 0.22, ay, zt + hh], [ax + 0.22, ay, zt + hh + 0.35], [ax - 0.22, ay, zt + hh + 0.35]],
			_cfg()["red"], [0, 0, 0])
		ants.append([ax, ay, zt + hh + 0.2])
		kinds["antenna"] = true
