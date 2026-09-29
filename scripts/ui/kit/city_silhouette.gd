class_name CitySilhouette
extends RefCounted
## The city's silhouette pre-render (art pass W7, ART_BIBLE §9.4; ANIM-R3 B4): while a view's
## bake runs, the city is drawn as skyline masses from its known placement, never as flat
## blocks: each building stands at its real height (the placement's own roof, worked out lot
## by lot within a frame budget; a hashed height until then), with two shaded walls, its roof
## rimmed faintly in one of the five inks, and a few lit windows. The layer it draws on takes
## the context grade (city_live mode 2), and the bake fades in over it (`city_bake_fade`).
## Deterministic (hashes of the lot). Static: nothing moves, so reduce effects changes nothing.

## Main-thread time a frame may spend working out lots and roofs (µs).
const BUDGET_USEC := 8000
## Lots beyond the view's corners it also covers (a tall roof leans in).
const MARGIN := 3
## Window grid on a wall (px): row pitch, column pitch, pane size.
const WINDOW_ROW := 7.0
const WINDOW_COL := 6.0
const WINDOW_SIZE := Vector2(2.0, 3.0)
## A wall's lit side (facing the light, right) and dark side.
const SALT_HEIGHT := 611
const SALT_WINDOW := 613
const SALT_INK := 617
## Roof rim alpha.
const RIM_ALPHA := 0.55
## The old placeholder's lift (px): a mass at least this tall is a building, not a flat block.
const FLAT_LIFT := 10.0

## What the last pass drew (tests and the lab): masses, masses taller than FLAT_LIFT, lit
## windows, and masses at the placement's real height.
static var last_masses: int = 0
static var last_tall: int = 0
static var last_windows: int = 0
static var last_real: int = 0


## Draws the silhouette of `city`'s view on `ci` (city-local px). Updates the city's
## `silhouette_roofs` (masses drawn) and, on its own layer, `silhouette_done` (every lot and
## roof in view known). Returns the masses drawn.
static func draw(city: NeonCity, ci: CanvasItem) -> int:
	var cfg := CityLookData.shipped()
	var size := city.size
	var look := city.look_key()
	if look != city._silhouette_look:
		city._silhouette.clear()
		city._silhouette_look = look
	var corners: Array[Vector2] = [city._grid_of(Vector2.ZERO), city._grid_of(Vector2(size.x, 0)), city._grid_of(Vector2(0, size.y)), city._grid_of(size)]
	var lo := corners[0]
	var hi := corners[0]
	for c in corners:
		lo = lo.min(c)
		hi = hi.max(c)
	var box := Rect2i(floori(lo.x) - MARGIN, floori(lo.y) - MARGIN, ceili(hi.x) - floori(lo.x) + MARGIN * 2 + 1, ceili(hi.y) - floori(lo.y) + MARGIN * 2 + 1)
	var t0 := Time.get_ticks_usec()
	var place := city._placement()
	var done := true
	var fronts: Array[Vector2i] = []
	var seen := {}
	# From the view's middle outward (the part a map frames is known first), ring by ring.
	var mid := city._grid_of(size * 0.5)
	var c0 := Vector2i(clampi(roundi(mid.x), box.position.x, box.end.x - 1), clampi(roundi(mid.y), box.position.y, box.end.y - 1))
	var reach := maxi(maxi(c0.x - box.position.x, box.end.x - 1 - c0.x), maxi(c0.y - box.position.y, box.end.y - 1 - c0.y))
	for ring in reach + 1:
		for l: Vector2i in NeonCity._ring_lots(c0, ring, box):
			if not city._silhouette.has(l):
				if Time.get_ticks_usec() - t0 > BUDGET_USEC:
					done = false
					continue
				city._silhouette[l] = place._front_of(l)
			var f: Vector2i = city._silhouette[l]
			if f == NeonCity.NO_LOT or seen.has(f):
				continue
			seen[f] = true
			fronts.append(f)
	# Back to front (the build's draw order), so nearer masses cover farther ones.
	fronts.sort_custom(func(a: Vector2i, b: Vector2i) -> bool: return a.x + a.y < b.x + b.y or (a.x + a.y == b.x + b.y and a.x < b.x))
	var off := Vector2(city._ox, city._oy)
	var view := Rect2(Vector2.ZERO, size).grow(NeonCity.TILE_A * 3.0)
	var drawn := 0
	last_tall = 0
	last_windows = 0
	last_real = 0
	for f in fronts:
		var roof := PackedVector2Array()
		var h := 0.0
		if place._fronts.has(f) or Time.get_ticks_usec() - t0 <= BUDGET_USEC:
			var rec := place.placed_roof(f)
			if not rec.is_empty():
				roof = Transform2D(0.0, off) * (rec["roof"] as PackedVector2Array)
				h = float(rec["height"])
				last_real += 1
		else:
			done = false
		if roof.is_empty():
			var cell := place._cell_of(f.x, f.y)
			h = cfg.silhouette_height_px * lerpf(0.4, 1.4, city._h(f.x, f.y, SALT_HEIGHT))
			var up := Vector2(0, -h)
			roof = PackedVector2Array([city._iso(cell.position.x, cell.position.y) + up, city._iso(cell.end.x, cell.position.y) + up,
				city._iso(cell.end.x, cell.end.y) + up, city._iso(cell.position.x, cell.end.y) + up])
		if roof.size() < 3 or not view.intersects(_bounds(roof).grow(h)):
			continue
		_mass(city, ci, roof, h, f, cfg)
		drawn += 1
		if h > FLAT_LIFT:
			last_tall += 1
	city.silhouette_roofs = drawn
	last_masses = drawn
	if ci == city._sil:
		# The rest next frame when the budget ran out (NeonCity._step_silhouette).
		city.silhouette_done = done
	return drawn


## One building mass: its walls (the roof's edges that face the viewer, dropped by `h`),
## lit windows on them, the roof and its faint ink rim.
static func _mass(city: NeonCity, ci: CanvasItem, roof: PackedVector2Array, h: float, f: Vector2i, cfg: CityLookData) -> void:
	var a := cfg.silhouette_alpha
	var down := Vector2(0, h)
	var n := roof.size()
	var centre := Vector2.ZERO
	for p in roof:
		centre += p
	centre /= n
	for k in n:
		var p0 := roof[k]
		var p1 := roof[(k + 1) % n]
		var mid := (p0 + p1) * 0.5
		# Keep the edges on the viewer's side of the roof (below its centre on screen).
		if mid.y < centre.y:
			continue
		var lit_side := (p1 - p0).x * (p1 - p0).y < 0.0
		var face := PackedVector2Array([p0, p1, p1 + down, p0 + down])
		ci.draw_colored_polygon(face, Color(CityPalette.SIL_FACE_LIT if lit_side else CityPalette.SIL_FACE_DARK, a))
		_windows(city, ci, p0, p1, h, f, k, cfg)
	ci.draw_colored_polygon(roof, Color(CityPalette.SIL_ROOF, a))
	var ink: Color = CityPalette.INKS[int(city._h(f.x, f.y, SALT_INK) * CityPalette.INKS.size()) % CityPalette.INKS.size()]
	ci.draw_polyline(roof + PackedVector2Array([roof[0]]), Color(ink, RIM_ALPHA), 1.0)


## A few lit windows on the wall from `p0` to `p1` (`h` tall): a pane per cell of the grid
## whose hash falls under `silhouette_window_share`.
static func _windows(city: NeonCity, ci: CanvasItem, p0: Vector2, p1: Vector2, h: float, f: Vector2i, side: int, cfg: CityLookData) -> void:
	var cols := int((p1 - p0).length() / WINDOW_COL)
	var rows := int(h / WINDOW_ROW) - 1
	for r in rows:
		for c in cols:
			if city._h(f.x * 31 + c + side * 97, f.y * 17 + r, SALT_WINDOW) >= cfg.silhouette_window_share:
				continue
			var u := (c + 0.5) / maxf(1.0, cols)
			var at := p0.lerp(p1, u) + Vector2(0, WINDOW_ROW * (r + 1))
			ci.draw_rect(Rect2(at - WINDOW_SIZE * 0.5, WINDOW_SIZE), CityPalette.SIL_WINDOW)
			last_windows += 1


static func _bounds(pts: PackedVector2Array) -> Rect2:
	var r := Rect2(pts[0], Vector2.ZERO)
	for p in pts:
		r = r.expand(p)
	return r
