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
