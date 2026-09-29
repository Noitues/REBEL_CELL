extends RefCounted
## Review only (art pass W7): the pre-W7 silhouette NeonCity drew while a bake ran (ANIM-R3
## B4: every building's footprint as a dim block lifted 10 px), kept verbatim so the city lab
## can show the "before" of docs/art_review/W7/placeholder_before_after.jpg in the same
## build. Never used by the game.

const BUDGET_USEC := 8000
const FILL := 0.9
const EDGE := 0.4
const LIFT := 10.0
const MARGIN := 3


static func draw(city: NeonCity, ci: CanvasItem) -> void:
	var size := city.size
	var corners: Array[Vector2] = [city._grid_of(Vector2.ZERO), city._grid_of(Vector2(size.x, 0)), city._grid_of(Vector2(0, size.y)), city._grid_of(size)]
	var lo := corners[0]
	var hi := corners[0]
	for c in corners:
		lo = lo.min(c)
		hi = hi.max(c)
	var i0 := floori(lo.x) - MARGIN
	var i1 := ceili(hi.x) + MARGIN
	var j0 := floori(lo.y) - MARGIN
	var j1 := ceili(hi.y) + MARGIN
	var place := city._placement()
	var fill := Color(Palette.NIGHT_BLOCK_LIT, FILL)
	var side := Color(Palette.NIGHT_BLOCK, FILL)
	var edge := Color(Palette.NET_CYAN, EDGE)
	var seen := {}
	var view := Rect2(Vector2.ZERO, size).grow(NeonCity.TILE_A * 2.0)
	var up := Vector2(0, -LIFT)
	for i in range(i0, i1 + 1):
		for j in range(j0, j1 + 1):
			var f: Vector2i = place._front_of(Vector2i(i, j))
			if f == NeonCity.NO_LOT or seen.has(f):
				continue
			seen[f] = true
			var cell := place._cell_of(f.x, f.y)
			var a := city._iso(cell.position.x, cell.position.y)
			if not view.has_point(a):
				continue
			var b := city._iso(cell.end.x, cell.position.y)
			var c := city._iso(cell.end.x, cell.end.y)
			var d := city._iso(cell.position.x, cell.end.y)
			ci.draw_colored_polygon(PackedVector2Array([d, c, c + up, d + up]), side)
			ci.draw_colored_polygon(PackedVector2Array([c, b, b + up, c + up]), side)
			var top := PackedVector2Array([a + up, b + up, c + up, d + up])
			ci.draw_colored_polygon(top, fill)
			ci.draw_polyline(top + PackedVector2Array([a + up]), edge, 1.0)
