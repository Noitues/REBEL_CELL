class_name CityLod
extends RefCounted
## ART-1 1D / ART-5 5a: LOD choices of the unified city, all from CityConfig (bible §4.1, §6.1;
## plan §5.2). Visibility by camera ortho, never distance; swaps with hysteresis.

enum CarTier { FAR, MEDIUM, CLOSE }
enum Detail { CITY, RAID, TRANSIT }


## Building opacity at zoom `lod` (round 37/40 v3): 1 at the city zoom, the see-through
## opacity below the view band.
static func opacity(cfg: CityConfig, lod: float) -> float:
	var k := clampf((lod - cfg.see_through_lod_from) / (cfg.see_through_lod_to - cfg.see_through_lod_from), 0.0, 1.0)
	return lerpf(cfg.see_through_opacity, 1.0, k)


## Share of the City Grid look (0 = management zoom, 1 = the city): lane and sky-lane
## glow follow it.
static func city_share(cfg: CityConfig, lod: float) -> float:
	return clampf((lod - cfg.see_through_lod_from) / (cfg.see_through_lod_to - cfg.see_through_lod_from), 0.0, 1.0)


## The car tier at `ortho`, keeping `current` inside the hysteresis band (-1 = none yet).
static func car_tier(cfg: CityConfig, ortho: float, current: int = -1) -> int:
	var h := cfg.lod_hysteresis
	var raw := CarTier.MEDIUM
	if ortho > cfg.car_far_above:
		raw = CarTier.FAR
	elif ortho < cfg.car_close_below:
		raw = CarTier.CLOSE
	if current < 0 or current == raw:
		return raw
	# Stay on the current tier until the zoom is past its edge by the hysteresis share.
	match current:
		CarTier.FAR:
			if ortho > cfg.car_far_above * (1.0 - h):
				return CarTier.FAR
		CarTier.CLOSE:
			if ortho < cfg.car_close_below * (1.0 + h):
				return CarTier.CLOSE
		CarTier.MEDIUM:
			if ortho <= cfg.car_far_above * (1.0 + h) and ortho >= cfg.car_close_below * (1.0 - h):
				return CarTier.MEDIUM
	return raw


## The building detail tier at `ortho` (same hysteresis rule).
static func detail(cfg: CityConfig, ortho: float, current: int = -1) -> int:
	var h := cfg.lod_hysteresis
	var raw := Detail.CITY
	if ortho <= cfg.detail_transit_below:
		raw = Detail.TRANSIT
	elif ortho <= cfg.detail_raid_below:
		raw = Detail.RAID
	if current < 0 or current == raw:
		return raw
	match current:
		Detail.CITY:
			if ortho > cfg.detail_raid_below * (1.0 - h):
				return Detail.CITY
		Detail.TRANSIT:
			if ortho < cfg.detail_transit_below * (1.0 + h):
				return Detail.TRANSIT
		Detail.RAID:
			if ortho <= cfg.detail_raid_below * (1.0 + h) and ortho > cfg.detail_transit_below * (1.0 - h):
				return Detail.RAID
	return raw


## ART-5 5a: the building LOD at `ortho` (0 full facet grid, 1 mass + windows, 2 plain
## extrusion; bible §6.1), keeping `current` inside the hysteresis band (-1 = none yet).
static func building_lod(cfg: CityConfig, ortho: float, current: int = -1) -> int:
	var h := cfg.lod_hysteresis
	var raw := 1
	if ortho <= cfg.lod0_below:
		raw = 0
	elif ortho > cfg.lod2_above:
		raw = 2
	if current < 0 or current == raw:
		return raw
	match current:
		0:
			if ortho <= cfg.lod0_below * (1.0 + h):
				return 0
		2:
			if ortho > cfg.lod2_above * (1.0 - h):
				return 2
		1:
			if ortho > cfg.lod0_below * (1.0 - h) and ortho <= cfg.lod2_above * (1.0 + h):
				return 1
	return raw


## ART-5 5a: the view band at `ortho` (the views the one city hosts by zoom, no scene
## change): Band.GRID at and above the see-through band's top (buildings solid), RAID down
## to band_netrun_below, NETRUN below it. Same hysteresis rule.
enum Band { NETRUN, RAID, GRID }


static func band(cfg: CityConfig, ortho: float, current: int = -1) -> int:
	var h := cfg.lod_hysteresis
	var grid_from := ortho_of_lod(cfg, cfg.see_through_lod_to)
	var raw := Band.RAID
	if ortho >= grid_from:
		raw = Band.GRID
	elif ortho < cfg.band_netrun_below:
		raw = Band.NETRUN
	if current < 0 or current == raw:
		return raw
	match current:
		Band.GRID:
			if ortho >= grid_from * (1.0 - h):
				return Band.GRID
		Band.NETRUN:
			if ortho < cfg.band_netrun_below * (1.0 + h):
				return Band.NETRUN
		Band.RAID:
			if ortho < grid_from * (1.0 + h) and ortho >= cfg.band_netrun_below * (1.0 - h):
				return Band.RAID
	return raw


## The ortho whose zoom level (CityIsoCamera.lod_of) is `lod` (its inverse, lod 0..2).
static func ortho_of_lod(cfg: CityConfig, lod: float) -> float:
	if lod >= 1.0:
		return cfg.lod_ortho_raid * pow(cfg.lod_ortho_city / cfg.lod_ortho_raid, lod - 1.0)
	return cfg.lod_ortho_transit * pow(cfg.lod_ortho_raid / cfg.lod_ortho_transit, lod)


## M14 perf slice: keep rect `r` (world X/Z) snapped outward to the config's grid
## (`far_lod_snap_bu`), so the same world rect read with float noise snaps to the same rect.
## A rect with no area stays empty (far LOD off).
static func snap_keep(cfg: CityConfig, r: Rect2) -> Rect2:
	if not r.has_area():
		return Rect2()
	var s := maxf(cfg.far_lod_snap_bu, 0.001)
	var lo := Vector2(floorf(r.position.x / s), floorf(r.position.y / s)) * s
	var hi := Vector2(ceilf(r.end.x / s), ceilf(r.end.y / s)) * s
	return Rect2(lo, hi - lo)


## M14 perf slice: the keep rect to hold next when the view asks for raw rect `raw` while it
## holds `current` (the hysteresis): `current` stays while it still holds `raw` and is no more
## than two snap steps wider on any side than `raw` grown by one, so a drifting or panning camera
## (the same world rect read again with noise) keeps the same rect; otherwise `raw` grown by one
## snap step, snapped (CityLod.snap_keep). No area: off.
static func keep_next(cfg: CityConfig, current: Rect2, raw: Rect2) -> Rect2:
	if not raw.has_area():
		return Rect2()
	var s := maxf(cfg.far_lod_snap_bu, 0.001)
	if current.has_area() and current.encloses(raw) and raw.grow(s * 3.0).encloses(current):
		return current
	return snap_keep(cfg, raw.grow(s))


## M14 perf slice: true when prism `pr` (a CityModel prism) stands outside keep rect `keep`
## (world X/Z) and takes the far LOD: its footprint box, grown by its top's lean on screen
## (`lean` BU per BU of height: 1 / tan(pitch) for the iso view, 0 for a distance rule),
## misses the rect. Always false with no keep rect (far LOD off) or with `far_lod_on` off.
static func prism_far(cfg: CityConfig, pr: Dictionary, keep: Rect2, lean: float) -> bool:
	if not cfg.far_lod_on or not keep.has_area():
		return false
	var poly: PackedVector2Array = pr["poly"]
	if poly.is_empty():
		return false
	var lo := poly[0]
	var hi := poly[0]
	for q in poly:
		lo = lo.min(q)
		hi = hi.max(q)
	var top := float(pr["y0"]) + float(pr["h"])
	return not Rect2(lo, hi - lo).grow(maxf(0.0, top * lean)).intersects(keep, true)


## M14 perf slice: prisms `idx` of `prisms` split by `prism_far`: {"near": PackedInt32Array,
## "far": PackedInt32Array}, each in `idx`'s order.
static func split_far(cfg: CityConfig, prisms: Array[Dictionary], idx: PackedInt32Array, keep: Rect2, lean: float) -> Dictionary:
	var near := PackedInt32Array()
	var far := PackedInt32Array()
	for n in idx:
		if prism_far(cfg, prisms[n], keep, lean):
			far.append(n)
		else:
			near.append(n)
	return {"near": near, "far": far}


## M14 perf slice: the building LOD a far prism draws at while the view's LOD is `lod`.
static func far_level(cfg: CityConfig, lod: int) -> int:
	return maxi(maxi(0, lod), cfg.far_lod_level)


## M14 perf slice: the screen lean of a building's top for the iso view at `pitch_deg` (BU of
## ground per BU of height; 0 for a near-horizontal or perspective close-up, which keeps by distance).
static func lean_of(pitch_deg: float) -> float:
	return 1.0 / tan(deg_to_rad(clampf(pitch_deg, 1.0, 89.0)))


## The render settings of quality tier `tier` (Settings.city_quality; the Deck = 1).
static func quality(cfg: CityConfig, city_quality: int) -> Dictionary:
	var t := cfg.tier_for(city_quality)
	return {"tier": t, "render_scale": cfg.quality_render_scale[t], "shadows": cfg.quality_shadows[t],
		"shadow_size": cfg.quality_shadow_size[t], "msaa": cfg.quality_msaa[t], "ink": cfg.quality_ink[t],
		"fog": cfg.quality_fog[t], "rain": cfg.quality_rain[t]}
