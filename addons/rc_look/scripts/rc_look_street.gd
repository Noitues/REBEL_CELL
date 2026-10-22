class_name RcLookStreet
extends RefCounted
## LOOK-TOOLBOX module 10: the street netrun's look numbers in one place, read from where they already live (no copies):
## StreetRouteConfigData (lane, rooms, hover cut, haze / exposure / frame pairs, fog density), CityShaderConfigData (the
## emission hierarchy aaa.emit). StreetR2ConfigData keeps its own copy of the sign emission tiers because the r2 plan is the
## Python generator's twin (tools/netrun_art/gen_street_r2_config.py writes street_r2.tres); `emit_pairs` lists those
## pairs so a test holds them equal. Pure: no Node, no Settings.

## The r2 plan's sign tier (street_r2.tres dressing_signs) -> its key in the emission hierarchy (city_shaders aaa.emit).
const EMIT_PAIRS := {
	"hero_emit": "hero",
	"sec_emit": "secondary",
	"shop_emit": "shop",
	"backdrop_emit": "backdrop",
	"mega_emit": "mega",
}


## One radiance of the emission hierarchy (aaa.emit), e.g. &"hero".
static func emit(key: String) -> float:
	return float(CityShaderConfigData.shipped().aaa["emit"][key])


## The lane lines' gain and saturation (route_lane's street_gain, lane_sat).
static func lane() -> Dictionary:
	var l: Dictionary = StreetRouteConfigData.shipped().look["lane"]
	return {"gain": float(l["gain"]), "sat": float(l["sat"])}


## The route rooms' energy idle and lit (route_room's energy).
static func room_energy() -> Vector2:
	var r: Dictionary = StreetRouteConfigData.shipped().rooms
	return Vector2(float(r["energy_idle"]), float(r["energy_lit"]))


## The hover power cut (route_grade): level, desaturation, branch boost.
static func hover_cut() -> Vector3:
	var h: Dictionary = StreetRouteConfigData.shipped().hover
	return Vector3(float(h["cut_level"]), float(h["cut_desat"]), float(h["branch_boost"]))


## An OVERVIEW -> DECISION pair of look.* (&"haze", &"exposure", &"frame") at zoom_detail zd.
static func look_at(key: String, zd: float) -> float:
	var p: Array = StreetRouteConfigData.shipped().look[key]
	return lerpf(float(p[0]), float(p[1]), zd)


## The street fog's density multiplier at zoom_detail zd (atmosphere density_overview -> density_decision).
static func fog_density(zd: float) -> float:
	var a: Dictionary = StreetRouteConfigData.shipped().atmosphere
	return lerpf(float(a["density_overview"]), float(a["density_decision"]), zd)


## Every (r2 plan tier, its value, the hierarchy's value): the two copies a test holds equal.
static func emit_pairs() -> Array:
	var s: Dictionary = StreetR2ConfigData.shipped().dressing_signs
	var out: Array = []
	var keys: Array = EMIT_PAIRS.keys()
	keys.sort()
	for k: String in keys:
		out.append([k, float(s[k]), emit(String(EMIT_PAIRS[k]))])
	return out
