class_name StreetR2Signs
extends RefCounted
## Street r2 sign textures as draw lists (twin of `tools/netrun_art/r2/signs.py`): box, blade, wall, ad, holo and shop styles. Each style
## returns `{w, h, ops}`, the plate's draw calls in order as data (grad, text, rect, ellipse, line, glow, holo_shift, fill, ad); the
## renderer replays them. The fit-to-sign text rule takes a `measure(font, size, text) -> [w, h]` Callable (the glyph box of the word at
## that size) and picks the largest size whose box is inside the field: a word never clips. Fonts are "anton" and "mono".

static var _t: Dictionary = {}


static func _cfg() -> Dictionary:
	if _t.is_empty():
		_t = StreetR2ConfigData.shipped().sign_tex
	return _t


## A `measure` Callable over recorded rows `[font, size, text, w, h]` (the glyph boxes of the plate's fonts); an unknown query is an error.
static func table_measure(rows: Array) -> Callable:
	var table := {}
	for r: Array in rows:
		table["%s|%d|%s" % [r[0], int(r[1]), r[2]]] = [int(r[3]), int(r[4])]
	return func(font: String, size: int, text: String) -> Array:
		var key := "%s|%d|%s" % [font, size, text]
		if not table.has(key):
			push_error("StreetR2Signs: no glyph box recorded for %s" % key)
			return [1 << 30, 1 << 30]
		return table[key]


## Colour 0..1 to ints 0..255, scaled by k.
static func c8(col: Array, k: float = 1.0) -> Array:
	var out: Array = []
	for v: float in col:
		out.append(int(maxf(0.0, minf(255.0, v * 255.0 * k))))
	return out


## The largest font size (fit_lo..fit_hi) whose glyph box for `s` is inside w x h.
static func fit_font(measure: Callable, s: String, font: String, w: int, h: int) -> int:
	var lo := int(_cfg()["fit_lo"])
	var hi := int(_cfg()["fit_hi"])
	while hi - lo > 1:
		var m := (lo + hi) / 2
		var bb: Array = measure.call(font, m, s)
		if int(bb[0]) <= w and int(bb[1]) <= h:
			lo = m
		else:
			hi = m
	return lo


## Texture size by the sign's aspect: the long side is `long_px`.
static func size_for(aspect: float, long_px: int = -1) -> Array:
	var lp := int(_cfg()["long_px"]) if long_px < 0 else long_px
	var mn := int(_cfg()["min_px"])
	if aspect >= 1.0:
		return [lp, maxi(mn, int(lp / aspect))]
	return [maxi(mn, int(lp * aspect)), lp]


static func _new(w: Variant, h: Variant) -> Dictionary:
	return {"w": w, "h": h, "ops": []}


static func _grad(d: Dictionary, top: Array, bot: Array) -> void:
	(d["ops"] as Array).append({"op": "grad", "w": d["w"], "h": d["h"], "top": top, "bot": bot})


static func _text(d: Dictionary, xy: Array, s: String, font: String, size: int, fill: Array, anchor: String) -> void:
	(d["ops"] as Array).append({"op": "text", "xy": xy, "s": s, "font": font, "size": size, "fill": fill, "anchor": anchor})


static func _rect(d: Dictionary, box: Array, fill: Variant = null, outline: Variant = null, width: int = 1) -> void:
	(d["ops"] as Array).append({"op": "rect", "box": box, "fill": fill, "outline": outline, "width": width})


static func _line(d: Dictionary, pts: Array, fill: Array, width: int = 0) -> void:
	(d["ops"] as Array).append({"op": "line", "pts": pts, "fill": fill, "width": width})


static func _glow(d: Dictionary, k: float = 0.55, r: int = 8) -> void:
	(d["ops"] as Array).append({"op": "glow", "k": k, "r": r})


static func _pale() -> Array:
	return (_cfg()["pale"] as Array).duplicate()


## Shop / secondary box sign.
static func box(word: String, sub: String, col: Array, aspect: float, _r: StreetR2Rng, measure: Callable) -> Dictionary:
	var sz := size_for(aspect)
	var w: int = sz[0]
	var h: int = sz[1]
	var d := _new(w, h)
	_grad(d, c8(col, 0.10), [6, 4, 12])
	var f := fit_font(measure, word, "anton", int(w * 0.84), int(h * (0.50 if sub != "" else 0.62)))
	_text(d, [w / 2, int(h * (0.42 if sub != "" else 0.5))], word, "anton", f, c8(col), "mm")
	if sub != "":
		var f2 := fit_font(measure, sub, "mono", int(w * 0.6), int(h * 0.16))
		_text(d, [w / 2, int(h * 0.80)], sub, "mono", f2, _pale(), "mm")
	var t := maxi(4, h / 18)
	_rect(d, [t, t, w - t, h - t], null, c8(col, 0.9), t)
	_glow(d)
	return d


## Vertical stacked letters on a dark board.
static func blade(word: String, sub: String, col: Array, aspect: float, _r: StreetR2Rng, measure: Callable) -> Dictionary:
	var sz := size_for(aspect)
	var w: int = sz[0]
	var h: int = sz[1]
	var d := _new(w, h)
	_grad(d, [16, 4, 24], [4, 2, 10])
	var ch: Array = []
	for i in word.length():
		if word[i] != " ":
			ch.append(word[i])
	var n := ch.size() + (1 if sub != "" else 0)
	var pitch := (h - 0.08 * h) / float(maxi(1, n))
	var f := fit_font(measure, "W", "anton", int(w * 0.78), int(pitch * 0.86))
	var y := 0.04 * h + pitch / 2
	for c: String in ch:
		_text(d, [w / 2, int(y)], c, "anton", f, c8(col), "mm")
		y += pitch
	if sub != "":
		var f2 := fit_font(measure, sub, "mono", int(w * 0.8), int(pitch * 0.4))
		_text(d, [w / 2, int(y)], sub, "mono", f2, _pale(), "mm")
	var t := maxi(4, w / 22)
	_rect(d, [t, t, w - t, h - t], null, c8(col, 0.9), t)
	_glow(d, 0.6)
	return d


## A hero poster: a hue field, a graphic (rings / bars / chevrons by seed), the word large, a sub line.
static func wall(word: String, sub: String, col: Array, aspect: float, r: StreetR2Rng, measure: Callable) -> Dictionary:
	var sz := size_for(aspect, int(_cfg()["long_px_big"]))
	var w: int = sz[0]
	var h: int = sz[1]
	var d := _new(w, h)
	_grad(d, c8(col, 0.30), c8(col, 0.05))
	var g := r.randrange(3)
	var acc := c8(col, 1.0)
	if g == 0:
		var cx := int(w * 0.78)
		var cy := int(h * 0.45)
		for k in 5:
			var rr := int(h * (0.12 + 0.08 * k))
			(d["ops"] as Array).append({"op": "ellipse", "box": [cx - rr, cy - rr, cx + rr, cy + rr], "outline": c8(col, 0.9 - 0.15 * k), "width": maxi(3, h / 70)})
	elif g == 1:
		for k in 7:
			var x := int(w * (0.62 + 0.05 * k))
			_rect(d, [x, int(h * (0.15 + 0.07 * (k % 3))), x + maxi(6, w / 60), int(h * 0.85)], c8(col, 0.9 - 0.08 * k))
	else:
		for k in 4:
			var y := int(h * (0.25 + 0.15 * k))
			_line(d, [[int(w * 0.62), y], [int(w * 0.78), y + int(h * 0.08)], [int(w * 0.94), y]], c8(col, 0.95 - 0.15 * k), maxi(4, h / 40))
	var f := fit_font(measure, word, "anton", int(w * 0.56), int(h * 0.42))
	_text(d, [int(w * 0.06), int(h * 0.42)], word, "anton", f, [250, 248, 255], "lm")
	_line(d, [[int(w * 0.06), int(h * 0.66)], [int(w * 0.5), int(h * 0.66)]], acc, maxi(3, h / 60))
	var sub_t := sub if sub != "" else "24 H"
	var f2 := fit_font(measure, sub_t, "mono", int(w * 0.4), int(h * 0.11))
	_text(d, [int(w * 0.06), int(h * 0.78)], sub_t, "mono", f2, _pale(), "lm")
	var t := maxi(6, h / 40)
	_rect(d, [t, t, w - t, h - t], null, acc, t)
	_glow(d, 0.45)
	return d


## An ad plate: the renderer crops the plate to `aspect` (centre crop) at render time.
static func ad(name: String, aspect: float) -> Dictionary:
	return {"w": null, "h": null, "ops": [{"op": "ad", "name": name, "aspect": aspect}]}


## Holo: black = additive, scanlines, red / blue channel shift.
static func holo(word: String, sub: String, col: Array, aspect: float, _r: StreetR2Rng, measure: Callable) -> Dictionary:
	var sz := size_for(aspect)
	var w: int = sz[0]
	var h: int = sz[1]
	var d := _new(w, h)
	(d["ops"] as Array).append({"op": "fill", "w": w, "h": h, "col": [0, 0, 0]})
	var f := fit_font(measure, word, "anton", int(w * 0.8), int(h * 0.5))
	_text(d, [w / 2, int(h * 0.42)], word, "anton", f, c8(col), "mm")
	if sub != "":
		var f2 := fit_font(measure, sub, "mono", int(w * 0.6), int(h * 0.14))
		_text(d, [w / 2, int(h * 0.78)], sub, "mono", f2, _pale(), "mm")
	_rect(d, [6, 6, w - 6, h - 6], null, c8(col), 5)
	for y in range(0, h, 4):
		_line(d, [[0, y], [w, y]], [0, 0, 0], 1)
	(d["ops"] as Array).append({"op": "holo_shift", "r": -3, "b": 3})
	return d


## Lit shopfront glazing: a warm / hue interior gradient, mullions, shelf silhouettes, a fascia band with a word.
static func shop(word: String, col: Array, aspect: float, r: StreetR2Rng, measure: Callable) -> Dictionary:
	var sz := size_for(aspect, int(_cfg()["long_px_big"]))
	var w: int = sz[0]
	var h: int = sz[1]
	var d := _new(w, h)
	var warm := r.random() < 0.5
	var top: Array = [255, 214, 160] if warm else c8(col, 0.95)
	var t0: Array = []
	var t1: Array = []
	for v: int in top:
		t0.append(int(v * 0.55))
		t1.append(int(v * 0.95))
	_grad(d, t0, t1)
	var fb := int(h * 0.26)
	_rect(d, [0, 0, w, fb], [14, 10, 20])
	var f := fit_font(measure, word, "anton", int(w * 0.35), int(fb * 0.7))
	_text(d, [int(w * 0.05), fb / 2], word, "anton", f, c8(col), "lm")
	# shelves with small lit goods, a dark door, mullions over all
	for k in 3:
		var y := int(fb + (h - fb) * (0.3 + 0.22 * k))
		_rect(d, [0, y, w, y + 4], [40, 30, 44])
		var x := r.randint(4, 30)
		while x < w - 20:
			var gw := r.randint(8, 22)
			var goods: Array = [c8(col), [255, 240, 220], [120, 220, 255], [255, 120, 190]]
			var gc: Array = r.choice(goods)
			var gh := r.randint(10, 26)
			var fillc: Array = []
			for v: int in gc:
				fillc.append(int(v * 0.8))
			_rect(d, [x, y - gh, x + gw, y], fillc)
			x += gw + r.randint(4, 28)
	var dx := int(w * r.uniform(0.15, 0.75))
	_rect(d, [dx, int(h * 0.38), dx + int(h * 0.38), h], [18, 14, 22])
	var n := maxi(2, int(aspect * 1.4))
	var xs: Array = []
	var xk := 0.0
	for _k in n:                       # irregular bays (repetition.guard): the mullion pitch varies by +-40 %
		xk += r.uniform(0.6, 1.4)
		xs.append(xk)
	for i in xs.size() - 1:
		var x := int(w * float(xs[i]) / float(xs[xs.size() - 1]))
		_rect(d, [x - 3, fb, x + 3, h], [20, 16, 26])
	return d


## The draw list of one planned sign (`{id, col, u0, u1, z0, z1, tex: {style, word, sub, seed, ad}}`).
static func sign_spec(s: Dictionary, measure: Callable) -> Dictionary:
	var t: Dictionary = s["tex"]
	var r := StreetR2Rng.from_seed(int(t["seed"]))
	var aspect := (float(s["u1"]) - float(s["u0"])) / maxf(0.05, float(s["z1"]) - float(s["z0"]))
	var st: String = t["style"]
	var sub: String = t.get("sub", "")
	var word: String = t.get("word", "")
	var col: Array = s["col"]
	match st:
		"box":
			return box(word, sub, col, aspect, r, measure)
		"blade":
			return blade(word, sub, col, aspect, r, measure)
		"wall":
			return wall(word, sub, col, aspect, r, measure)
		"ad":
			return ad(String(t["ad"]), aspect)
		"holo":
			return holo(word, sub, col, aspect, r, measure)
	return shop(word, col, aspect, r, measure)


## Draw lists of every sign of a plan by sign id, plus the megastructure plate (`mega`) when there is one.
static func make(plan: Dictionary, measure: Callable) -> Dictionary:
	var out := {}
	for s: Dictionary in plan["signs"]:
		out[s["id"]] = sign_spec(s, measure)
	var m: Variant = plan.get("mega")
	if m != null:
		out["mega"] = ad(String(m["tex"]["ad"]), 2.4 if m["kind"] == "arch" else 16.0 / 9.0)
	return out
