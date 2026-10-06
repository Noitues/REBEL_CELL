class_name RaidZoomFit
extends RefCounted
## ART-3 6w (bible §4.1 "raid fitted to the network", Appendix C #13, plan G10): the raid view's
## camera on the unified city. The raid frames the network (the Cell's nodes and the Sites the
## threats enter at and cross) plus `raid_fit_margin` BU round it inside the map's free part,
## its ortho clamped to [`raid_fit_min`, `raid_fit_max`] (CityConfig). The host (NeonCity in
## city-3D mode) zooms by its control scale: ortho = (screen width / zoom) / px per BU, so these
## convert both ways. Pure: presentation only, no rule reads it.


## The ortho (BU) a host `screen_w` px wide shows at control zoom `zoom`.
static func ortho_of(zoom: float, screen_w: float) -> float:
	return maxf(screen_w, 1.0) / (maxf(zoom, 0.0001) * NeonCity.px_per_bu())


## The control zoom at which a host `screen_w` px wide shows `ortho` BU.
static func zoom_of(ortho: float, screen_w: float) -> float:
	return maxf(screen_w, 1.0) / (maxf(ortho, 0.0001) * NeonCity.px_per_bu())


## The box (host px at zoom 1, the 3D camera's ground projection) round lot points `lots`.
static func box_of(cfg: CityConfig, lots: PackedVector2Array) -> Rect2:
	if lots.is_empty():
		return Rect2()
	var tb := NeonCity.TILE_A * sin(deg_to_rad(cfg.pitch_deg))
	var out := Rect2()
	for k in lots.size():
		var q := lots[k]
		var p := Vector2((q.x - q.y) * NeonCity.TILE_A, (q.x + q.y) * tb)
		out = Rect2(p, Vector2.ZERO) if k == 0 else out.expand(p)
	return out


## The raid's ortho: lot points `lots` (the network) and the margin fitted into a free part of
## `free` px of a host `screen_w` px wide, clamped to the config's raid range.
static func fit_ortho(cfg: CityConfig, lots: PackedVector2Array, free: Vector2, screen_w: float) -> float:
	if lots.is_empty() or free.x <= 1.0 or free.y <= 1.0:
		return cfg.raid_fit_max
	var m := cfg.raid_fit_margin * NeonCity.px_per_bu() * 2.0
	var box := box_of(cfg, lots)
	var z := minf(free.x / (box.size.x + m), free.y / (box.size.y + m))
	return clampf(ortho_of(z, screen_w), cfg.raid_fit_min, cfg.raid_fit_max)


## The raid's control zoom for the same inputs (see fit_ortho).
static func fit_zoom(cfg: CityConfig, lots: PackedVector2Array, free: Vector2, screen_w: float) -> float:
	return zoom_of(fit_ortho(cfg, lots, free, screen_w), screen_w)
