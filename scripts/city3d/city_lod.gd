class_name CityLod
extends RefCounted
## ART-1 1D: LOD choices of the unified city, all from CitySpikeConfig (bible §4.1, §6.1;
## plan §5.2). Visibility by camera ortho, never distance; swaps with hysteresis.

enum CarTier { FAR, MEDIUM, CLOSE }
enum Detail { CITY, RAID, TRANSIT }


## Building opacity at zoom `lod` (round 37/40 v3): 1 at the city zoom, the see-through
## opacity below the view band.
static func opacity(cfg: CitySpikeConfig, lod: float) -> float:
	var k := clampf((lod - cfg.see_through_lod_from) / (cfg.see_through_lod_to - cfg.see_through_lod_from), 0.0, 1.0)
	return lerpf(cfg.see_through_opacity, 1.0, k)


## Share of the City Grid look (0 = management zoom, 1 = the city): lane and sky-lane
## glow follow it.
static func city_share(cfg: CitySpikeConfig, lod: float) -> float:
	return clampf((lod - cfg.see_through_lod_from) / (cfg.see_through_lod_to - cfg.see_through_lod_from), 0.0, 1.0)


## The car tier at `ortho`, keeping `current` inside the hysteresis band (-1 = none yet).
static func car_tier(cfg: CitySpikeConfig, ortho: float, current: int = -1) -> int:
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
static func detail(cfg: CitySpikeConfig, ortho: float, current: int = -1) -> int:
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


## The render settings of quality tier `tier` (Settings.city_quality; the Deck = 1).
static func quality(cfg: CitySpikeConfig, city_quality: int) -> Dictionary:
	var t := cfg.tier_for(city_quality)
	return {"tier": t, "render_scale": cfg.quality_render_scale[t], "shadows": cfg.quality_shadows[t],
		"shadow_size": cfg.quality_shadow_size[t], "msaa": cfg.quality_msaa[t], "ink": cfg.quality_ink[t],
		"fog": cfg.quality_fog[t], "rain": cfg.quality_rain[t]}
