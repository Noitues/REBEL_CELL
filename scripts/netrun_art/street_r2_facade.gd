class_name StreetR2Facade
extends RefCounted
## Street r2 facade rhythm and facade props (twin of `tools/netrun_art/r2/facade.py`, the plate's `repetition.guard` and `props.facade`):
## bay rhythm, mixed window modules, varied floors, setbacks, balconies, and the AC / pipe / awning / small sign / lit room props with
## their keep-clear rule for route-room openings. Every draw comes from the stream handed in, in the order the Python draws it.


static func _pick(r: StreetR2Rng, items: Array, weights: Variant = null) -> Variant:
	if weights != null:
		return r.choices(items, weights)
	return items[r.randrange(items.size())]


static func _span(r: StreetR2Rng, p: Array) -> int:
	return r.randint(int(p[0]), int(p[1]))


static func _uni(r: StreetR2Rng, p: Array) -> float:
	return r.uniform(float(p[0]), float(p[1]))


## The rhythm record of one building. `wdt` = its street face width, `h` its height (BU), `rigid_top` = the top of the highest route
## room when it is a route column (null otherwise; floors below it stay at the 1.9 BU pitch). `cfg` is the `repetition_guard` block.
static func make_rhythm(r: StreetR2Rng, kit: String, wdt: float, h: float, cfg: Dictionary, pal: Array, rigid_top: Variant = null, fl: float = 1.9) -> Dictionary:
	var nfl := maxi(1, StreetR2Util.py_round0(h / fl))
	var bm: Array = cfg["bay_mults"]
	var mot: Array = []
	var n_mot := _span(r, cfg["motif_len"])
	for _i in n_mot:
		mot.append(_pick(r, bm))
	if float(StreetR2Util.amax(mot)) / float(StreetR2Util.amin(mot)) < 1.9:       # a motif needs contrast, else it is a uniform grid
		var low: Array = []
		var high: Array = []
		for m: float in bm:
			if m <= 0.85:
				low.append(m)
			if m >= 1.6:
				high.append(m)
		var first: Variant = _pick(r, low)
		var last: Variant = _pick(r, high)
		mot[0] = first
		mot[mot.size() - 1] = last
	var nb := int(wdt / 0.9) + 6
	var bays: Array = []
	var jit := float(cfg["bay_jitter"])
	for i in nb:
		var m: float = float(mot[i % mot.size()]) * (1.0 + r.uniform(-jit, jit))
		if r.random() < float(cfg["feature_bay_p"]):
			m = float(StreetR2Util.amax(bm)) * r.uniform(1.0, 1.25)
		bays.append(StreetR2Util.py_round(m, 3))
	var fm: Array = []
	for j in nfl:
		var m: float = float(_pick(r, cfg["floor_mults"]))
		var rr := r.random()
		if rr < float(cfg["p_double"]) and 0 < j and j < nfl - 1:
			m = float(cfg["double_mult"])
		fm.append(m)
	if rigid_top == null:
		fm[0] = _uni(r, cfg["ground_mult"])
	if nfl > 3 and rigid_top == null:
		fm[fm.size() - 1] = _uni(r, cfg["top_mult"])
	# mixed window modules: a module per floor band of 2-4 floors, never the same as the band below
	var mods: Array = []
	var band := 0
	var mprev := r.randrange(3)
	var j := 0
	while j < nfl:
		var ln := _span(r, cfg["band_floors"])
		var m: int
		if band == 0:
			m = mprev
		else:
			var opts: Array = []
			for x in 3:
				if x != mprev:
					opts.append(x)
			m = _pick(r, opts)
		if r.random() > float(cfg["p_mixed_modules"]):
			m = mprev
		for _k in ln:
			mods.append(m)
		mprev = m
		band += 1
		j += ln
	# setback: above a floor, the facade steps back
	var setback: Variant = null
	var rt0 := _truthy_float(rigid_top)
	if nfl >= int(cfg["setback_min_floors"]):
		var rs := r.random()
		if rs < float(cfg["p_setback"]) and kit != "lit_atrium":
			var sf: Array = cfg["setback_from"]
			var lo := maxi(int(nfl * float(sf[0])), int(rt0 / fl) + 1)
			var hi := maxi(lo, int(nfl * float(sf[1])))
			var fl_i := r.randint(lo, hi)
			setback = {"floor": fl_i, "d": StreetR2Util.py_round(_uni(r, cfg["setback_depth"]), 2)}
	# balconies: floor, centre (face fraction), span (BU); not on concrete_band nor on rooms
	var balc: Array = []
	if kit != "concrete_band":
		var lo_f := maxi(2, int(rt0 / fl) + 1)
		for jj in range(lo_f, nfl - 1):
			if r.random() < float(cfg["p_balcony_floor"]):
				var bw := _uni(r, cfg["balcony_w"])
				var c := r.uniform(0.15, 0.85)
				var wv := StreetR2Util.py_round(minf(bw, maxf(0.9, wdt * 0.6)), 2)
				var dp := StreetR2Util.py_round(_uni(r, cfg["balcony_depth"]), 2)
				var lit := r.random() < 0.55
				balc.append({"floor": jj, "c": StreetR2Util.py_round(c, 3), "w": wv, "depth": dp, "lit": lit})
	var phase := r.randrange(bays.size())
	var fmr: Array = []
	for x: float in fm:
		fmr.append(StreetR2Util.py_round(x, 3))
	var acc: Array = (pal[r.randrange(pal.size())] as Array).duplicate()
	var pool: Array = cfg["window_tone_pool"]
	var tones: Array = []
	for t: Array in r.sample(pool, int(cfg["window_tones"])):
		tones.append(t.duplicate())
	return {"bays": bays, "phase": phase, "fm": fmr, "mods": mods, "setback": setback, "balc": balc, "rigid_top": rigid_top, "acc": acc,
		"tone": (cfg["cell_tone"] as Array).duplicate(), "relief": cfg["cell_relief"], "tones": tones}


## Python truthiness of an optional number as a float (null and 0 give 0.0): `rigid_top or 0.0`.
static func _truthy_float(v: Variant) -> float:
	if v == null:
		return 0.0
	return float(v)


## Floor boundary heights (absolute z, nf + 1 values) of a face of height h starting at z0. Without a rhythm the floors are uniform; the
## floors under `rigid_top` keep the 1.9 BU pitch.
static func floor_bounds(rh: Variant, z0: float, h: float, fl: float = 1.9) -> Array:
	var nf := maxi(1, StreetR2Util.py_round0(h / fl))
	var zs: Array = []
	if rh == null or not (rh as Dictionary).has("fm") or (rh["fm"] as Array).is_empty():
		for j in nf + 1:
			zs.append(z0 + h * float(j) / float(nf))
		return zs
	var rt: Variant = rh.get("rigid_top")
	var nrig := 0
	if rt != null and float(rt) != 0.0 and float(rt) > z0:
		nrig = mini(nf - 1, int(ceilf((float(rt) - z0) / fl - 1e-6)))
	var hr := nrig * fl
	var fm: Array = rh["fm"]
	var total := 0.0
	var free: Array = []
	for k in nf - nrig:
		free.append(fm[(nrig + k) % fm.size()])
	for m: float in free:
		total += m
	var sc := (h - hr) / maxf(1e-6, total)
	for j in nrig + 1:
		zs.append(z0 + fl * j)
	for m: float in free:
		zs.append(float(zs[zs.size() - 1]) + m * sc)
	zs[zs.size() - 1] = z0 + h
	return zs


## The bay edges (along-face fractions) of one floor band: widths cw x the rhythm's multipliers, phase shifted per band, scaled so
## they close at the face end. Returns [[u0, u1], ...].
static func bay_edges(L: float, cw: float, rh: Variant, band: int) -> Array:
	var out: Array = []
	if rh == null:
		var nu := maxi(1, StreetR2Util.py_round0(L / cw))
		for i in nu:
			out.append([float(i) / float(nu), float(i + 1) / float(nu)])
		return out
	var bays: Array = rh["bays"]
	var ph := int(rh["phase"]) + band * 3
	var w: Array = []
	var tot := 0.0
	var i := 0
	while tot < L - 0.05:
		var v: float = cw * float(bays[(ph + i) % bays.size()])
		w.append(v)
		tot += v
		i += 1
	if w.size() > 1 and (L - (tot - float(w[w.size() - 1]))) < 0.45 * cw:       # a sliver at the end joins the previous bay
		w.pop_back()
	var sw := 0.0
	for v: float in w:
		sw += v
	var s := L / sw
	var u := 0.0
	for v: float in w:
		out.append([u / L, minf(1.0, (u + v * s) / L)])
		u += v * s
	return out


## Setback depth in force on floor j.
static func floor_inset(rh: Variant, j: int) -> float:
	var sb: Variant = rh.get("setback") if rh != null else null
	if sb != null and j >= int(sb["floor"]):
		return float(sb["d"])
	return 0.0


## Window module of floor j.
static func floor_module(rh: Variant, j: int, module: int) -> int:
	if rh == null or not (rh as Dictionary).has("mods") or (rh["mods"] as Array).is_empty():
		return module
	var mods: Array = rh["mods"]
	return int(mods[j % mods.size()])


static func _hit(a: Array, b: Array, pad: float) -> bool:
	return float(a[0]) < float(b[2]) + pad and float(a[2]) > float(b[0]) - pad and float(a[1]) < float(b[3]) + pad and float(a[3]) > float(b[1]) - pad


## A prop is blocked when it overlaps a route-room opening laterally within `margin`, overlaps it vertically, and stands between the
## opening's plane and the kerb. `rooms` = {id: {front: [4 points], ...}}.
static func prop_hits_opening(p: Dictionary, rooms: Dictionary, axis: int, line: float, margin: float) -> bool:
	var sd := absf(float(p["face"]) + float(p["out"]) * float(p["depth"]) - line)
	for room: Dictionary in rooms.values():
		var front: Array = room["front"]
		var us: Array = []
		var zs: Array = []
		for q: Array in front:
			us.append(q[axis])
			zs.append(q[2])
		var fplane: float = front[0][1 - axis]
		if float(p["u0"]) < float(StreetR2Util.amax(us)) + margin and float(p["u1"]) > float(StreetR2Util.amin(us)) - margin \
				and float(p["z0"]) < float(StreetR2Util.amax(zs)) and float(p["z1"]) > float(StreetR2Util.amin(zs)):
			if sd <= absf(fplane - line) + 0.25:
				return true
	return false


## Props on one building's street face (dictionaries with u0 u1 z0 z1 along the face, depth out of the face, kind, colour). `rects`
## ([u0, z0, u1, z1]) are no-go areas on the face; accepted props are appended to it so props never overlap each other.
static func make_props(r: StreetR2Rng, uid: String, b: Dictionary, face_frame: Array, axis: int, line: float, pal: Array, rooms: Dictionary,
		rects: Array, cfg: Dictionary, floors_z: Array) -> Array:
	var bu0 := float(face_frame[0])
	var bu1 := float(face_frame[1])
	var face: float = face_frame[2]
	var out: float = face_frame[3]
	var wdt := bu1 - bu0
	var h := float(b["h"])
	var area := wdt * maxf(0.0, h - 2.0)
	var quiet := r.random() < float(cfg["p_quiet"])
	var n := StreetR2Util.py_round0(area * float(cfg["density"]) * (0.6 + 0.8 * r.random()) * (float(cfg["quiet_k"]) if quiet else 1.0))
	var floor_n: int = 1 if quiet else (int(cfg["min_per_face"]) if wdt > 3.0 else 1)
	n = maxi(floor_n, mini(n, int(cfg["max_per_face"])))
	var kinds: Array = (cfg["kinds"] as Dictionary).keys()
	var weights: Array = []
	for kn: String in kinds:
		weights.append(cfg["kinds"][kn])
	var props: Array = []
	var tries := 0
	var nfl := floors_z.size() - 1
	while props.size() < n and tries < n * 14:
		tries += 1
		var k: String = _pick(r, kinds, weights)
		var j := 0
		if nfl > 2:
			j = 1 + r.randbelow(maxi(2, nfl - 1) - 1)
		var zb := float(floors_z[j])
		var zt := float(floors_z[mini(j + 1, nfl)])
		if zt > h - 0.5 or zb < 1.5:
			continue
		var pc: Array = pal[r.randrange(pal.size())]
		var p: Dictionary
		if k == "ac":
			var w := r.uniform(0.7, 1.05)
			var u0 := bu0 + 0.25 + r.random() * maxf(0.01, wdt - w - 0.5)
			var z1 := zb + 0.28 + r.uniform(0.5, 0.68)
			var dep := r.uniform(0.38, 0.55)
			var led := r.random() < 0.45
			p = {"kind": k, "u0": u0, "u1": u0 + w, "z0": zb + 0.28, "z1": z1, "depth": dep, "col": [0.30, 0.30, 0.34], "led": led, "ledcol": pc.duplicate()}
		elif k == "pipe":
			var sel := 1.0 if r.random() < 0.5 else 0.0
			var u := bu0 + 0.2 + sel * maxf(0.01, wdt - 0.4)
			var za := r.uniform(0.3, maxf(0.5, h * 0.25))
			var zbb := minf(h - 0.4, za + r.uniform(3.0, 9.0))
			var elbow := r.random() < 0.6
			p = {"kind": k, "u0": u - 0.09, "u1": u + 0.09, "z0": za, "z1": zbb, "depth": 0.2, "col": [0.21, 0.21, 0.25], "elbow": elbow}
		elif k == "awning":
			var w := r.uniform(1.3, minf(3.4, maxf(1.4, wdt - 0.5)))
			var u0 := bu0 + 0.25 + r.random() * maxf(0.01, wdt - w - 0.5)
			var dep := r.uniform(0.6, 0.95)
			var col: Array = []
			for v: float in pc:
				col.append(v * 0.8)
			var trim := r.random() < 0.55
			p = {"kind": k, "u0": u0, "u1": u0 + w, "z0": zb + 1.0, "z1": zb + 1.35, "depth": dep, "col": col, "trim": trim, "trimcol": pc.duplicate()}
		elif k == "small_sign":
			var w := r.uniform(0.55, 1.35)
			var hh := w * r.uniform(0.42, 0.75)
			var blade := r.random() < 0.3
			if blade:
				w = r.uniform(0.28, 0.42)
				hh = r.uniform(1.0, 1.9)
			var u0 := bu0 + 0.2 + r.random() * maxf(0.01, wdt - w - 0.4)
			var z0 := zb + r.uniform(0.2, maxf(0.21, (zt - zb) - hh))
			var bars := r.randint(1, 3)
			p = {"kind": k, "u0": u0, "u1": u0 + w, "z0": z0, "z1": z0 + hh, "depth": 0.12 + (0.25 if blade else 0.0), "col": pc.duplicate(), "blade": blade, "bars": bars}
		elif k == "lit_room":
			var w := r.uniform(0.9, 2.0)
			var u0 := bu0 + 0.3 + r.random() * maxf(0.01, wdt - w - 0.6)
			var wcs: Array = [[1.0, 0.7, 0.35], [0.5, 0.92, 1.0], [1.0, 0.5, 0.8], [1.0, 0.85, 0.6]]
			var wc: Array = wcs[r.randrange(4)]
			var col: Array = []
			for v: float in wc:
				col.append(v * (0.8 + 0.2 * r.random()))
			var mull := r.random() < 0.6
			p = {"kind": k, "u0": u0, "u1": u0 + w, "z0": zb + 0.35, "z1": zb + 1.25, "depth": 0.05, "col": col, "mull": mull}
		else:
			continue
		var box: Array = [p["u0"], p["z0"], p["u1"], p["z1"]]
		var hit := false
		for q: Array in rects:
			if _hit(box, q, 0.2):
				hit = true
				break
		if hit:
			continue
		p["id"] = "%s_%s_%d" % [k, uid, props.size()]
		p["key"] = uid
		p["face"] = face
		p["out"] = out
		p["axis"] = axis
		p["solid"] = k == "ac" or k == "pipe" or k == "awning"
		if prop_hits_opening(p, rooms, axis, line, float(cfg["opening_margin"])):
			continue
		rects.append(box)
		props.append(p)
	return props
