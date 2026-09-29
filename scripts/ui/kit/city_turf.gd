class_name CityTurf
extends Control
## The Cell's territory on the city (art pass W7, ART_BIBLE §9.3, §3.2 CELL_TURF; critique
## gifs/16): each claimed Site's buildings carry a CELL_TURF hatch clipped to their roofs and
## spray tags sprayed on them (a squiggle with drips, the Cell's hand), and the district's
## light leaks into the haze (city_live's `leaks`, set by CityAtmosphere). This replaces the
## flat khaki tint: the lasting wash is a hatch too (influence_reveal). Static (no motion):
## the same under reduce effects. Deterministic: tags come from hashes of the Site's lot.

const SALT_TAG := 503
## Squiggle points per tag and its drips.
const TAG_POINTS := 7
const TAG_DRIPS := 2
## The hatch's direction (45 degrees, screen space) and how far past a roof a line is cut.
const HATCH_DIR := Vector2(1, -1)

var city: NeonCity
var cfg: CityLookData
## Claimed Sites (grid lots).
var claims: PackedVector2Array = PackedVector2Array()
## Roofs to hatch and tag spots, in world px ({"roofs": Array[PackedVector2Array],
## "tags": Array[Dictionary]}), worked out when the claims or the look change.
var _plan: Dictionary = {}
var _plan_key: String = ""
## Roofs hatched and tags sprayed by the last draw (tests and the lab).
var hatched_roofs: int = 0
var tags_drawn: int = 0


func _init() -> void:
	name = "CityTurf"
	mouse_filter = Control.MOUSE_FILTER_IGNORE
	set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)


## Sets the claimed Sites (grid lots); redraws when they changed.
func set_claims(p_claims: PackedVector2Array) -> void:
	if p_claims == claims:
		return
	claims = p_claims
	_plan_key = ""
	queue_redraw()


## The roofs and tag spots for the claims (world px): the buildings within
## `hatch_reach_lots` of each Site, and `tags_per_site` of the nearest ones for tags.
func plan() -> Dictionary:
	var key := str(claims) + "|" + city.look_key() if city != null else ""
	if key == _plan_key and not _plan.is_empty():
		return _plan
	_plan_key = key
	var roofs: Array[PackedVector2Array] = []
	var tags: Array[Dictionary] = []
	var off := Vector2(city._ox, city._oy)
	var seen := {}
	for c in claims:
		var reach := ceili(cfg.hatch_reach_lots)
		var near: Array[Dictionary] = []
		for di in range(-reach, reach + 1):
			for dj in range(-reach, reach + 1):
				var l := Vector2i(roundi(c.x) + di, roundi(c.y) + dj)
				if Vector2(l).distance_to(c) > cfg.hatch_reach_lots:
					continue
				var rec := city.roof_of(l.x, l.y)
				if rec.is_empty():
					continue
				var roof: PackedVector2Array = rec["roof"]
				var key_roof := var_to_str(Vector2i((roof[0] - off).round()))
				if seen.has(key_roof):
					continue
				seen[key_roof] = true
				var world := Transform2D(0.0, -off) * roof
				roofs.append(world)
				near.append({"d": Vector2(l).distance_to(c), "at": _centre(world), "l": l})
		near.sort_custom(func(a: Dictionary, b: Dictionary) -> bool: return a["d"] < b["d"] or (a["d"] == b["d"] and String(var_to_str(a["l"])) < String(var_to_str(b["l"]))))
		for k in mini(cfg.tags_per_site, near.size()):
			tags.append({"at": near[k]["at"], "seed": hash(near[k]["l"])})
	_plan = {"roofs": roofs, "tags": tags}
	return _plan


static func _centre(pts: PackedVector2Array) -> Vector2:
	var s := Vector2.ZERO
	for p in pts:
		s += p
	return s / maxf(1.0, pts.size())


func _draw() -> void:
	hatched_roofs = 0
	tags_drawn = 0
	if city == null or cfg == null or claims.is_empty():
		return
	var p := plan()
	var off := Vector2(city._ox, city._oy)
	var col := Palette.CELL_TURF
	var step := cfg.hatch_spacing_px
	for world: PackedVector2Array in p["roofs"]:
		var roof := Transform2D(0.0, off) * world
		var box := Rect2(roof[0], Vector2.ZERO)
		for q in roof:
			box = box.expand(q)
		# 45-degree lines across the roof's box, clipped to the roof.
		var n := ceili((box.size.x + box.size.y) / step) + 1
		var segs := PackedVector2Array()
		for k in n:
			var a := Vector2(box.position.x + k * step, box.end.y)
			var line := PackedVector2Array([a - HATCH_DIR * box.size.length(), a + HATCH_DIR * box.size.length()])
			for piece in Geometry2D.intersect_polyline_with_polygon(line, roof):
				if piece.size() >= 2:
					segs.append(piece[0])
					segs.append(piece[piece.size() - 1])
		if not segs.is_empty():
			draw_multiline(segs, Color(col, cfg.hatch_alpha), cfg.hatch_width_px)
		draw_polyline(roof + PackedVector2Array([roof[0]]), Color(col, cfg.hatch_alpha * 1.4), 1.0)
		hatched_roofs += 1
	for tg: Dictionary in p["tags"]:
		_tag((tg["at"] as Vector2) + off, int(tg["seed"]))
		tags_drawn += 1


## A spray tag: a squiggle with a soft overspray and drips, sized `tag_size_px`.
func _tag(at: Vector2, seed_n: int) -> void:
	var s := cfg.tag_size_px
	var pts := PackedVector2Array()
	for k in TAG_POINTS:
		var u := float(k) / (TAG_POINTS - 1)
		var y := (CityLife.hash01(seed_n, SALT_TAG, k) - 0.5) * s * 0.55
		pts.append(at + Vector2((u - 0.5) * s, y))
	var col := Palette.CELL_TURF
	draw_polyline(pts, Color(col, 0.18 * cfg.tag_alpha), 7.0, true)
	draw_polyline(pts, Color(col, cfg.tag_alpha), 2.2, true)
	for d in TAG_DRIPS:
		var from := pts[1 + d * 3]
		var drip := s * lerpf(0.2, 0.5, CityLife.hash01(seed_n, SALT_TAG, 40 + d))
		draw_line(from, from + Vector2(0, drip), Color(col, 0.8 * cfg.tag_alpha), 1.4)
		draw_circle(from + Vector2(0, drip), 1.6, Color(col, 0.8 * cfg.tag_alpha))
