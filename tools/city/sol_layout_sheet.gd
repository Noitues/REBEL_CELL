class_name SolLayoutSheet
extends RefCounted
## Solace district layout (A-069 / A-070): a top-down before / after sheet of the Solace district, drawn from the lots
## (no window, no renderer): left the A2 grid (layout off), right the park (layout on). Lots 8 px; street grey, building by
## height (dark to white), lawn green, bare dark, water blue, HQ plaza amber, other territories dimmed; on the right the
## park outline (white), paths (orange), service lanes (yellow), stairs (red), ponds (cyan), the plinth circle (magenta).
## Run from a GUT script (autoloads needed): SolLayoutSheet.render(seed, "D:/rc_tmp/sol_layout/sheet.jpg").

const PX := 8


## Writes the sheet for city seed `s` to `path` (.jpg).
static func render(s: int, path: String) -> void:
	var plan := CityPlan.for_seed(s)
	var on_cfg: CampaignConfigData = CityPlan.plan_config()
	var off_cfg: CampaignConfigData = on_cfg.duplicate()
	off_cfg.city_sol_layout = false
	var a := CityA2Builder._subdivide(plan, off_cfg, NeonCity.HQ_LOTS, NeonCity.FIST_TERRITORY, 1.0)
	var b := CityA2Builder._subdivide(plan, on_cfg, NeonCity.HQ_LOTS, NeonCity.FIST_TERRITORY, 1.0)
	var R: Rect2i = a["rect"]
	var bb := Rect2i()
	var first := true
	for j in range(R.position.y, R.end.y):
		for i in range(R.position.x, R.end.x):
			if plan.a2.territory(i, j) == &"solace":
				bb = Rect2i(Vector2i(i, j), Vector2i.ONE) if first else bb.expand(Vector2i(i, j))
				first = false
	bb = bb.grow(3)
	var w := bb.size.x * PX
	var h := bb.size.y * PX
	var img := Image.create(w * 2 + 16, h, false, Image.FORMAT_RGB8)
	img.fill(Color(0.05, 0.05, 0.07))
	_draw(img, plan, a, bb, 0, {})
	_draw(img, plan, b, bb, w + 16, b.get("solace", {}))
	img.save_jpg(path, 0.9)


static func _draw(img: Image, plan: CityPlan, lots: Dictionary, bb: Rect2i, ox: int, park: Dictionary) -> void:
	var R: Rect2i = lots["rect"]
	var kind: PackedByteArray = lots["kind"]
	var top := {}
	for c: Dictionary in lots["cells"]:
		var cell: Rect2i = c["cell"]
		var t := 0.0
		for e: Dictionary in c["extrusions"]:
			t = maxf(t, float(e["z0"]) + float(e["h"]))
		for j in range(cell.position.y, cell.end.y):
			for i in range(cell.position.x, cell.end.x):
				top[Vector2i(i, j)] = t
	for j in range(bb.position.y, bb.end.y):
		for i in range(bb.position.x, bb.end.x):
			var l := Vector2i(i, j)
			var col := Color(0.04, 0.04, 0.05)
			if R.has_point(l):
				var kd := int(kind[(j - R.position.y) * R.size.x + (i - R.position.x)])
				match kd:
					CityA2Builder.K_STREET: col = Color(0.32, 0.32, 0.36)
					CityA2Builder.K_PLAZA: col = Color(0.85, 0.62, 0.15)
					CityA2Builder.K_BUILDING: col = Color(0.25, 0.3, 0.45).lerp(Color(0.95, 0.97, 1.0), clampf(float(top.get(l, 0.0)) / 40.0, 0.0, 1.0))
					CityA2Builder.K_PARK: col = Color(0.14, 0.42, 0.2)
					CityA2Builder.K_WATER: col = Color(0.08, 0.16, 0.38)
					CityA2Builder.K_BARE: col = Color(0.14, 0.12, 0.1)
					_: col = Color(0.1, 0.1, 0.11)
				if plan.a2.territory(i, j) != &"solace":
					col = col.darkened(0.55)
			var x0 := (i - bb.position.x) * PX + ox
			var y0 := (j - bb.position.y) * PX
			for y in PX:
				for x in PX:
					var edge := x == 0 or y == 0
					img.set_pixel(x0 + x, y0 + y, col.darkened(0.12) if edge else col)
	if park.is_empty():
		return
	var to_px := func(p: Vector2) -> Vector2: return (p - Vector2(bb.position)) * float(PX) + Vector2(ox, 0)
	for lp: Dictionary in park["outline"]:
		_poly(img, lp["points"], to_px, Color.WHITE, true)
	for p: Dictionary in park["paths"]:
		var c := Color(1.0, 0.55, 0.1)
		if p["kind"] == "lane":
			c = Color(1.0, 0.95, 0.2)
		elif p["kind"] == "stair":
			c = Color(1.0, 0.2, 0.2)
		_poly(img, p["points"], to_px, c, false)
	for po: Dictionary in park["ponds"]:
		_poly(img, po["points"], to_px, Color(0.3, 0.95, 1.0), true)
	var pl: Dictionary = park["plinth"]
	var ring := PackedVector2Array()
	var r_l := float(pl["radius_bu"]) / CityView3D.CONFIG.lot_bu
	for k in 48:
		var an := TAU * float(k) / 48.0
		ring.append((pl["centre"] as Vector2) + Vector2(cos(an), sin(an)) * r_l)
	_poly(img, ring, to_px, Color(1.0, 0.2, 0.9), true)


static func _poly(img: Image, pts: PackedVector2Array, to_px: Callable, col: Color, closed: bool) -> void:
	var n := pts.size()
	for i in (n if closed else n - 1):
		var a: Vector2 = to_px.call(pts[i])
		var b: Vector2 = to_px.call(pts[(i + 1) % n])
		var steps := int(maxf(absf(b.x - a.x), absf(b.y - a.y))) + 1
		for k in steps + 1:
			var p := a.lerp(b, float(k) / float(steps))
			for d: Vector2i in [Vector2i(0, 0), Vector2i(1, 0), Vector2i(0, 1)]:
				var q: Vector2i = Vector2i(p) + d
				if q.x >= 0 and q.y >= 0 and q.x < img.get_width() and q.y < img.get_height():
					img.set_pixelv(q, col)
