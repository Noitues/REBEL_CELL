class_name CityMapCamera
extends RefCounted
## ART-5 5a: the City Grid's player camera on the unified city (bible §4.1 "City Grid ≈ ortho
## 440 with panning: minimap terminal, DRAG / WASD"), as pure maths on a NeonCity frame
## (`focus` grid point at screen fraction `anchor`, zoom `scale`, the ground's row step
## `tile_b`; screen = the map's own rect in its parent's px). Continuous log-linear zoom
## about the cursor, clamped to the config's ortho range; pan in screen px, the frame's
## centre kept inside the city. The page applies the result (`_frame_city`); a view: the
## camera is view state, never game state.

## Grid point (lots) under screen point `p`.
static func grid_at(p: Vector2, screen: Vector2, focus: Vector2, anchor: Vector2, scale: float, tile_b: float) -> Vector2:
	var d := (p - anchor * screen) / maxf(scale, 0.0001)
	var dd := d.x / NeonCity.TILE_A
	var ss := d.y / tile_b
	return focus + Vector2((ss + dd) * 0.5, (ss - dd) * 0.5)


## Screen point of grid point `g`.
static func screen_of(g: Vector2, screen: Vector2, focus: Vector2, anchor: Vector2, scale: float, tile_b: float) -> Vector2:
	var r := g - focus
	return anchor * screen + Vector2((r.x - r.y) * NeonCity.TILE_A, (r.x + r.y) * tile_b) * scale


## The zoom (NeonCity scale) whose frame is `ortho` BU wide on a screen `width` px wide.
static func scale_for_ortho(width: float, ortho: float) -> float:
	return width / (maxf(ortho, 0.001) * NeonCity.px_per_bu())


## The ortho (BU) of zoom `scale` on a screen `width` px wide.
static func ortho_of(width: float, scale: float) -> float:
	return width / (maxf(scale, 0.0001) * NeonCity.px_per_bu())


## The frame after one zoom step: ortho x `factor` (log-linear), clamped to the config's
## range, the ground under `p` kept under it. Returns {"scale", "focus", "anchor"}.
static func zoom_about(cfg: CityConfig, p: Vector2, factor: float, screen: Vector2, focus: Vector2, anchor: Vector2,
		scale: float, tile_b: float) -> Dictionary:
	var ortho := clampf(ortho_of(screen.x, scale) * factor, cfg.zoom_ortho_min, cfg.zoom_ortho_max)
	var g := grid_at(p, screen, focus, anchor, scale, tile_b)
	return {"scale": scale_for_ortho(screen.x, ortho), "focus": g, "anchor": p / screen.max(Vector2.ONE)}


## The frame after a pan by `delta` screen px (the city follows the drag), recentred: the
## focus is the ground at the screen's centre, kept inside the city rect.
static func pan(cfg: CityConfig, delta: Vector2, screen: Vector2, focus: Vector2, anchor: Vector2, scale: float,
		tile_b: float) -> Dictionary:
	var c := grid_at(screen * 0.5 - delta, screen, focus, anchor, scale, tile_b)
	var r := Rect2(cfg.city_rect)
	c = c.clamp(r.position, r.end)
	return {"scale": scale, "focus": c, "anchor": Vector2(0.5, 0.5)}


## The frame centred on grid point `g` (the minimap's click), same zoom.
static func centre_on(cfg: CityConfig, g: Vector2, scale: float) -> Dictionary:
	var r := Rect2(cfg.city_rect)
	return {"scale": scale, "focus": g.clamp(r.position, r.end), "anchor": Vector2(0.5, 0.5)}


## The four ground corners (grid points) of the frame, clockwise from the top left: the
## minimap's view box.
static func view_quad(screen: Vector2, focus: Vector2, anchor: Vector2, scale: float, tile_b: float) -> PackedVector2Array:
	var out := PackedVector2Array()
	for p in [Vector2.ZERO, Vector2(screen.x, 0), screen, Vector2(0, screen.y)]:
		out.append(grid_at(p, screen, focus, anchor, scale, tile_b))
	return out


## G2R-1: the grid-space box the frame's four corners span.
static func view_box(screen: Vector2, focus: Vector2, anchor: Vector2, scale: float, tile_b: float) -> Rect2:
	var q := view_quad(screen, focus, anchor, scale, tile_b)
	var box := Rect2(q[0], Vector2.ZERO)
	for p in q:
		box = box.expand(p)
	return box


## G2R-1: the focus shifted the least way that puts the frame's corners inside the city rect (the
## frame never shows past the city's edge). A frame wider than the city on an axis is centred on
## it there (nothing to shift to). Zoom and anchor are untouched.
static func clamp_focus(cfg: CityConfig, screen: Vector2, focus: Vector2, anchor: Vector2, scale: float,
		tile_b: float) -> Vector2:
	var r := Rect2(cfg.city_rect)
	var box := view_box(screen, focus, anchor, scale, tile_b)
	var d := Vector2.ZERO
	for axis in 2:
		if box.size[axis] >= r.size[axis]:
			d[axis] = (r.position[axis] + r.size[axis] * 0.5) - (box.position[axis] + box.size[axis] * 0.5)
		elif box.position[axis] < r.position[axis]:
			d[axis] = r.position[axis] - box.position[axis]
		elif box.end[axis] > r.end[axis]:
			d[axis] = r.end[axis] - box.end[axis]
	return focus + d


## Zoom-in steps `keep_on_city` tries between the frame's zoom and the closest raid fit.
const KEEP_ZOOM_STEPS := 16


## G2R-1: the frame (scale, focus, anchor) kept on the city and on its network. The focus is
## shifted onto the city (`clamp_focus`) as far as every `keep` grid point (the network) stays
## inside `keep_rect` (screen px). If the frame still shows past the city's edge, the zoom closes
## in step by step (about the anchor, never past the raid fit's closest ortho), the network kept
## in `keep_rect` throughout (each point drawn `keep_off` from its ground point), until the frame is off the edge; when none is, the network wins: the
## frame with the least ground past the edge (the earliest, least zoomed, on a tie).
## Returns {"scale", "focus", "anchor"}.
static func keep_on_city(cfg: CityConfig, screen: Vector2, focus: Vector2, anchor: Vector2, scale: float,
		tile_b: float, keep: PackedVector2Array, keep_rect: Rect2, keep_off: PackedVector2Array = PackedVector2Array()) -> Dictionary:
	var best := _settle(cfg, screen, focus, anchor, scale, scale, tile_b, keep, keep_rect, keep_off)
	if best.is_empty():
		best = {"scale": scale, "focus": focus, "anchor": anchor}  # the network is out already: as it is
	var best_void := void_area(cfg, screen, best, tile_b)
	if best_void <= VOID_EPS:
		return best
	var closest := maxf(scale, scale_for_ortho(screen.x, cfg.raid_fit_min))
	for i in range(1, KEEP_ZOOM_STEPS + 1):
		var s := scale * pow(closest / scale, float(i) / KEEP_ZOOM_STEPS)
		var cand := _settle(cfg, screen, focus, anchor, s, scale, tile_b, keep, keep_rect, keep_off)
		if cand.is_empty():
			continue
		var v := void_area(cfg, screen, cand, tile_b)
		if v < best_void - VOID_EPS:
			best = cand
			best_void = v
			if v <= VOID_EPS:
				break
	return best


## G2R-1: the ground (lots squared) frame `fr` ({"scale", "focus", "anchor"}) shows past the city's
## edge.
static func void_area(cfg: CityConfig, screen: Vector2, fr: Dictionary, tile_b: float) -> float:
	var q := view_quad(screen, fr["focus"], fr["anchor"], float(fr["scale"]), tile_b)
	var r := Rect2(cfg.city_rect)
	var rect := PackedVector2Array([r.position, Vector2(r.end.x, r.position.y), r.end, Vector2(r.position.x, r.end.y)])
	var inside := 0.0
	for poly in Geometry2D.intersect_polygons(q, rect):
		inside += _poly_area(poly)
	return maxf(0.0, _poly_area(q) - inside)


static func _poly_area(poly: PackedVector2Array) -> float:
	var a := 0.0
	for k in poly.size():
		var p := poly[k]
		var n := poly[(k + 1) % poly.size()]
		a += p.x * n.y - n.x * p.y
	return absf(a) * 0.5


## Ground (lots squared) of the edge a frame may still show and count as off it (rounding).
const VOID_EPS := 1.0


## The frame at `scale` with its focus shifted onto the city as far as the network allows; empty
## when the network is not wholly in `keep_rect` at this zoom.
static func _settle(cfg: CityConfig, screen: Vector2, focus: Vector2, anchor: Vector2, scale: float, base: float,
		tile_b: float, keep: PackedVector2Array, keep_rect: Rect2, keep_off: PackedVector2Array) -> Dictionary:
	var f := clamp_focus(cfg, screen, focus, anchor, scale, tile_b)
	var w := _largest_ok(func(v: float) -> bool:
		return _holds(keep, keep_rect, screen, focus.lerp(f, v), anchor, scale, tile_b, keep_off, scale / base))
	var at := focus.lerp(f, w)
	if not _holds(keep, keep_rect, screen, at, anchor, scale, tile_b, keep_off, scale / base):
		return {}
	return {"scale": scale, "focus": at, "anchor": anchor}


## True when every point of `keep` lies in `rect` (screen px) in the given frame. `off` (same
## size as `keep`, or empty) is each point's drawn offset from its ground point at the frame the
## caller measured (an icon floats over its lot), taken `ratio` times as long at this zoom.
static func _holds(keep: PackedVector2Array, rect: Rect2, screen: Vector2, focus: Vector2, anchor: Vector2,
		scale: float, tile_b: float, off: PackedVector2Array, ratio: float) -> bool:
	for k in keep.size():
		var at := screen_of(keep[k], screen, focus, anchor, scale, tile_b)
		if k < off.size():
			at += off[k] * ratio
		if not rect.has_point(at):
			return false
	return true


## The largest u in [0, 1] (12 bisection steps) for which `ok` holds, taking it to hold at 0
## (a frame whose network is out already is left as it is).
static func _largest_ok(ok: Callable) -> float:
	if ok.call(1.0):
		return 1.0
	var lo := 0.0
	var hi := 1.0
	for i in 12:
		var mid := (lo + hi) * 0.5
		if ok.call(mid):
			lo = mid
		else:
			hi = mid
	return lo
