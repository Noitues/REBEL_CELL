class_name RevealTiers
extends RefCounted
## NA-21 twin of `tools/netrun_art/lod.py` (atmosphere detail bands by camera distance, zoom converters) plus per-asset reveal tiers.

## Guard against a zero distance in the log (the Python source writes 1e-3 inline).
const MIN_DIST := 1e-3
## Floor of the smoothstep span (the Python source writes 1e-6 inline).
const MIN_SPAN := 1e-6


## Camera distance of `zoom_dive` value `z` at the anchors: `d0 * (d1 / d0) ** z` (NaN anchors = config).
static func band_distance(z: float, d0: float = NAN, d1: float = NAN) -> float:
	var lod: Dictionary = NetrunArtConfigData.shipped().lod
	var a0: float = float(lod["d0"]) if is_nan(d0) else d0
	var a1: float = float(lod["d1"]) if is_nan(d1) else d1
	return a0 * pow(a1 / a0, z)


## `zoom_dive` (0 = HQ page distance d0, 1 = street OVERVIEW distance d1), clamped.
static func zoom_dive(d: float, d0: float, d1: float) -> float:
	return maxf(0.0, minf(1.0, log(d0 / maxf(d, MIN_DIST)) / log(d0 / d1)))


## `zoom_detail` (0 = OVERVIEW distance, 1 = DECISION distance), clamped.
static func zoom_detail(d: float, d_ov: float, d_dec: float) -> float:
	return maxf(0.0, minf(1.0, log(d_ov / maxf(d, MIN_DIST)) / log(d_ov / d_dec)))


## Spec 5.1 relation `zoom_dive = 1 + zoom_detail * ln(d_ov / d_dec) / ln(d0 / d_ov)` (saturates at 1).
static func dive_from_detail(zd: float, d_ov: float, d_dec: float, d0: float) -> float:
	return minf(1.0, 1.0 + zd * log(d_ov / d_dec) / log(d0 / d_ov))


## Smoothstep of `x` over `a..b` (`b - a` floored at 1e-6).
static func sstep(x: float, a: float, b: float) -> float:
	return NetrunArtUnits.smoothstep01((x - a) / maxf(MIN_SPAN, b - a))


## `[d_far, d_near]` in BU of a zoom pair at the anchors.
static func band_edges(ab: Array, d0: float = NAN, d1: float = NAN) -> Array:
	return [band_distance(float(ab[0]), d0, d1), band_distance(float(ab[1]), d0, d1)]


## Band weight 0..1 at camera distance `d` (empty `bands` = config bands).
static func band(d: float, name: String, bands: Dictionary = {}) -> float:
	var src: Dictionary = bands if not bands.is_empty() else NetrunArtConfigData.shipped().lod["bands"]
	var e: Array = band_edges(src[name])
	var far: float = e[0]
	var near: float = e[1]
	var t: float = maxf(0.0, minf(1.0, log(far / maxf(d, MIN_DIST)) / log(far / near)))
	return NetrunArtUnits.smoothstep01(t)


## `{band: weight}` at camera distance `d`; a band with floor f gives `f + (1 - f) * w`. Empty `floors` = config floors.
static func weights(d: float, bands: Dictionary = {}, floors: Dictionary = {}) -> Dictionary:
	var lod: Dictionary = NetrunArtConfigData.shipped().lod
	var fl: Dictionary = floors if not floors.is_empty() else lod["floors"]
	var src: Dictionary = bands if not bands.is_empty() else lod["bands"]
	var names: Array = src.keys()
	IdSort.sort_ids(names)
	var out: Dictionary = {}
	for k: String in names:
		var f: float = float(fl[k]) if fl.has(k) else 0.0
		out[k] = f + (1.0 - f) * band(d, k, bands)
	return out


## The `lod` block of poses_<run>.json: anchors, zoom pairs, computed distances, floors.
static func lod_block() -> Dictionary:
	var lod: Dictionary = NetrunArtConfigData.shipped().lod
	var all: Dictionary = {}
	for k: String in lod["bands"]:
		all[k] = lod["bands"][k]
	for k: String in lod["ramps"]:
		all[k] = lod["ramps"][k]
	var names: Array = all.keys()
	IdSort.sort_ids(names)
	var bands: Dictionary = {}
	for k: String in names:
		var ab: Array = all[k]
		var e: Array = band_edges(ab)
		bands[k] = {"a": ab[0], "b": ab[1], "d_far": e[0], "d_near": e[1]}
	var fnames: Array = lod["floors"].keys()
	IdSort.sort_ids(fnames)
	var floors: Dictionary = {}
	for k: String in fnames:
		floors[k] = lod["floors"][k]
	var lnames: Array = lod["ramp_levels"].keys()
	IdSort.sort_ids(lnames)
	var levels: Dictionary = {}
	for k: String in lnames:
		levels[k] = lod["ramp_levels"][k]
	var bnames: Array = lod["bands"].keys()
	IdSort.sort_ids(bnames)
	return {"d0": lod["d0"], "d1": lod["d1"], "bands": bands, "floors": floors, "ramp_levels": levels,
		"lod_bands": bnames}


## Sorted asset names that have reveal tiers.
static func reveal_assets() -> Array:
	var names: Array = NetrunArtConfigData.shipped().reveal.keys()
	IdSort.sort_ids(names)
	return names


## Weight of `tier` of `asset` at camera-to-asset distance `d` (smoothstep in ln d); unknown asset or tier = 1.0.
static func tier_weight(asset: String, tier: int, d: float) -> float:
	var rv: Dictionary = NetrunArtConfigData.shipped().reveal
	if not rv.has(asset):
		return 1.0
	for row: Array in rv[asset]:
		if int(row[0]) == tier:
			var far: float = row[1]
			var near: float = row[2]
			var t: float = maxf(0.0, minf(1.0, log(far / maxf(d, MIN_DIST)) / log(far / near)))
			return NetrunArtUnits.smoothstep01(t)
	return 1.0


## `{tier: weight}` of every listed tier of `asset` at distance `d` (empty for an unknown asset).
static func tier_weights(asset: String, d: float) -> Dictionary:
	var rv: Dictionary = NetrunArtConfigData.shipped().reveal
	var out: Dictionary = {}
	if not rv.has(asset):
		return out
	for row: Array in rv[asset]:
		var tier: int = int(row[0])
		out[tier] = tier_weight(asset, tier, d)
	return out


## Highest listed tier whose weight is above 0 at `d`; 0 when none or the asset is unknown.
static func visible_tier(asset: String, d: float) -> int:
	var rv: Dictionary = NetrunArtConfigData.shipped().reveal
	if not rv.has(asset):
		return 0
	var best: int = 0
	var found: bool = false
	for row: Array in rv[asset]:
		var tier: int = int(row[0])
		if tier_weight(asset, tier, d) > 0.0 and (not found or tier > best):
			best = tier
			found = true
	return best
