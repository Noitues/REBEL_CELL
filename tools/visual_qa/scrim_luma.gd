extends RefCounted
## B1a b (art director's review of B1a, 2026-10-06): the luma measures of the UI scrim's pools and
## bands on a screen's world (dev tool; the perf pack's `scrim_luma_*` probes and
## tests/unit/test_b1a_ui_scrim_pools.gd read it). Luma = Rec. 709 weights on the encoded colour
## (the scrim's own desaturation keeps it). Regions, in the scrim layer's px (UiScrimPools.sources):
##   ring    — round each wheel, from its disc's edge out to the pool's held radius (the pool you see)
##   between — the backdrop between the wheels, clear of every pool and band
##   margin  — round each pooled panel, out to its pool's margin (clear of other panels and bands)
##   foot    — the city past a bottom bar, out to its band's reach (clear of every pool)
##   open    — the world clear of every pool, band, panel and bar
## `measure(raw, on, src)`: `raw` the world with the scrim hidden, `on` with its pools and bands
## shown (null: the scrim's maths, UiScrimPools.apply_shapes, applied to `raw`). Both images cover
## the layer's whole rect. Returns each region's mean luma ({<region>_raw, <region>_on, n_<region>})
## and the ratios the art director asked for: ring_vs_between (on), margin_same / foot_same
## (on / raw over the same pixels), margin_vs_open and foot_vs_open (on).

const STEP := 2


static func luma(c: Color) -> float:
	return Vector3(c.r, c.g, c.b).dot(UiScrimPools.LUMA)


## The JSON-safe form of UiScrimPools.sources() (fixtures).
static func to_json(src: Dictionary) -> Dictionary:
	var wheels: Array = []
	for w: Dictionary in src["wheels"]:
		var c: Vector2 = w["centre"]
		wheels.append([c.x, c.y, float(w["radius"])])
	var panels: Array = []
	for r: Rect2 in src["panels"]:
		panels.append([r.position.x, r.position.y, r.size.x, r.size.y])
	var bands: Array = []
	for b: Dictionary in src["bands"]:
		var r: Rect2 = b["rect"]
		bands.append([r.position.x, r.position.y, r.size.x, r.size.y, bool(b["top"])])
	var sz: Vector2 = src["size"]
	return {"size": [sz.x, sz.y], "scale": float(src["scale"]), "wheels": wheels, "panels": panels, "bands": bands}


static func from_json(d: Dictionary) -> Dictionary:
	var wheels: Array[Dictionary] = []
	for w: Array in d["wheels"]:
		wheels.append({"centre": Vector2(w[0], w[1]), "radius": float(w[2])})
	var panels: Array[Rect2] = []
	for r: Array in d["panels"]:
		panels.append(Rect2(r[0], r[1], r[2], r[3]))
	var bands: Array[Dictionary] = []
	for b: Array in d["bands"]:
		bands.append({"rect": Rect2(b[0], b[1], b[2], b[3]), "top": bool(b[4])})
	return {"size": Vector2(d["size"][0], d["size"][1]), "scale": float(d["scale"]), "wheels": wheels, "panels": panels, "bands": bands}


static func measure(raw: Image, on: Image, src: Dictionary) -> Dictionary:
	var shapes := UiScrimPools.shapes_for(src)
	var sz: Vector2 = src["size"]
	var k := Vector2(sz.x / float(raw.get_width()), sz.y / float(raw.get_height()))
	var wheels: Array = src["wheels"]
	var panels: Array = src["panels"]
	var bars: Array[Rect2] = []
	var feet: Array[Rect2] = []
	for b: Dictionary in src["bands"]:
		bars.append(b["rect"])
		if not bool(b["top"]):
			feet.append(b["rect"])
	var margin := UiScrimPools.LOOK.panel_pool_margin_px * float(src["scale"])
	var foot_reach := UiScrimPools.LOOK.band_reach_bottom_px * float(src["scale"])
	# Between the wheels: right of the leftmost wheel's whole pool, left of the rightmost's.
	var x0 := INF
	var x1 := -INF
	if wheels.size() >= 2:
		var ws := wheels.duplicate()
		ws.sort_custom(func(a: Dictionary, b: Dictionary) -> bool: return (a["centre"] as Vector2).x < (b["centre"] as Vector2).x)
		var reach := UiScrimPools.LOOK.wheel_pool_reach + UiScrimPools.LOOK.wheel_pool_fade
		x0 = (ws[0]["centre"] as Vector2).x + float(ws[0]["radius"]) * reach
		x1 = (ws[ws.size() - 1]["centre"] as Vector2).x - float(ws[ws.size() - 1]["radius"]) * reach
	var sums := {}
	for region in ["ring", "between", "margin", "foot", "open"]:
		sums[region] = [0.0, 0.0, 0]
	for y in range(0, raw.get_height(), STEP):
		for x in range(0, raw.get_width(), STEP):
			var p := Vector2((x + 0.5) * k.x, (y + 0.5) * k.y)
			var under := false
			for r: Rect2 in panels:
				under = under or r.has_point(p)
			for r: Rect2 in bars:
				under = under or r.has_point(p)
			if under:
				continue
			var m := UiScrimPools.masks_at(shapes, p)
			var rc := raw.get_pixel(x, y)
			var oc := on.get_pixel(x, y) if on != null else UiScrimPools.apply_shapes(shapes, p, rc)
			var regions: Array[String] = []
			var in_disc := false
			var in_ring := false
			for w: Dictionary in wheels:
				var d := p.distance_to(w["centre"])
				var r := float(w["radius"])
				in_disc = in_disc or d <= r
				in_ring = in_ring or (d > r and d <= r * UiScrimPools.LOOK.wheel_pool_reach)
			if in_disc:
				continue
			if in_ring and m.y < 0.01:
				regions.append("ring")
			if p.x > x0 and p.x < x1 and m.x < 0.005 and m.y < 0.005:
				regions.append("between")
			if m.y < 0.01 and not in_ring:
				for r: Rect2 in panels:
					var d := UiScrimPools.sd_box(p - r.get_center(), r.size * 0.5, 0.0)
					if d > 0.0 and d <= margin:
						regions.append("margin")
						break
			if m.x < 0.01:
				for r: Rect2 in feet:
					if p.y < r.position.y and p.y >= r.position.y - foot_reach and p.x >= r.position.x and p.x <= r.end.x:
						regions.append("foot")
						break
			if m.x < 0.005 and m.y < 0.005:
				regions.append("open")
			for region in regions:
				var s: Array = sums[region]
				s[0] = float(s[0]) + luma(rc)
				s[1] = float(s[1]) + luma(oc)
				s[2] = int(s[2]) + 1
	var out := {}
	for region in sums:
		var s: Array = sums[region]
		var n := maxi(int(s[2]), 1)
		out[region + "_raw"] = float(s[0]) / n
		out[region + "_on"] = float(s[1]) / n
		out["n_" + region] = int(s[2])
	out["ring_vs_between"] = _ratio(out["ring_on"], out["between_on"])
	out["ring_same"] = _ratio(out["ring_on"], out["ring_raw"])
	out["margin_same"] = _ratio(out["margin_on"], out["margin_raw"])
	out["foot_same"] = _ratio(out["foot_on"], out["foot_raw"])
	out["margin_vs_open"] = _ratio(out["margin_on"], out["open_on"])
	out["foot_vs_open"] = _ratio(out["foot_on"], out["open_on"])
	return out


static func _ratio(a: float, b: float) -> float:
	return a / b if b > 0.0001 else 0.0


## One line of the numbers (the probe's PROBE line and the sheet's caption).
static func line(m: Dictionary) -> String:
	return "ring/between %.2f (n %d/%d) ring same %.2f | margin same %.2f vs open %.2f (n %d) | foot same %.2f vs open %.2f (n %d)" % [
		m["ring_vs_between"], m["n_ring"], m["n_between"], m["ring_same"], m["margin_same"], m["margin_vs_open"], m["n_margin"],
		m["foot_same"], m["foot_vs_open"], m["n_foot"]]
