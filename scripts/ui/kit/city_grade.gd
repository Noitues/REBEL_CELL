class_name CityGrade
extends RefCounted
## The city's colour grade (art pass W7, ART_BIBLE §9.1, §9.3, §9.5): what a CityState asks
## of the picture, worked out from content/config/city_look.tres as plain numbers. Pure and
## headless-testable; CityAtmosphere hands the result to the city's shaders (city_live) and
## multiplies its light layers by `brightness`.
##
## - Per context (§9.1): HQ warm and dirty, the net cool and high-contrast, combat raises
##   contrast and dims the city; the title is the reference look.
## - Campaign progress (§9.3): the grade leans 0 -> `progress_max_shift` (20%) toward the
##   target corporation's hue.
## - HUNTED (§9.3): saturation drops by `hunted_desaturate` (25%), the haze thickens.
## - Map mode (§9.5): the city dims by `map_dim` (40%) and blurs a little.
## - Calm zones (§2): behind text the city dims and loses saturation; more under high contrast.

## The grade for `state` from `cfg`. `base_dim` is the city's own veil (NeonCity.dim, which
## screens set): a context's `dim` is the total darkening it asks for, so only what the veil
## doesn't already give is added. `high_contrast` deepens the calm zones (§12).
static func params(state: CityState, cfg: CityLookData, base_dim: float = 0.0, high_contrast: bool = false) -> Dictionary:
	var g := blended(state, cfg)
	var sat: float = g["saturation"]
	var haze := 1.0
	if state.hunted():
		sat *= 1.0 - cfg.hunted_desaturate
		haze = cfg.hunted_haze_gain
	var target: float = g["dim"]
	var extra := 0.0
	if target > base_dim:
		extra = 1.0 - (1.0 - target) / maxf(0.001, 1.0 - base_dim)
	var tint_amount := 0.0
	var tint := Palette.NET_CYAN
	if state.corp_id != &"":
		tint = Palette.corp_color(state.corp_id)
		tint_amount = clampf(state.progress, 0.0, 1.0) * cfg.progress_max_shift * float(g[CityLookData.LEAN_KEY])
	return {
		"contrast": float(g["contrast"]),
		"saturation": sat,
		"warmth": float(g["warmth"]),
		"lift": float(g["lift"]),
		"dim": clampf(extra, 0.0, 1.0),
		"map_dim": cfg.map_dim if state.map_mode else 0.0,
		"blur_px": cfg.map_blur_px if state.map_mode else 0.0,
		"tint": tint,
		"tint_amount": tint_amount,
		"haze_gain": haze,
		"calm_dim": clampf(cfg.calm_dim + (cfg.high_contrast_calm_dim if high_contrast else 0.0), 0.0, 1.0),
		"calm_desaturate": cfg.calm_desaturate,
	}


## Art pass W9F: the context's grade values, blended from `context_from`'s while a blend
## runs (CityAtmosphere.blend_context: the flatline's grey grading in over T4).
static func blended(state: CityState, cfg: CityLookData) -> Dictionary:
	var g := cfg.grade_of(state.context)
	if state.context_from == &"" or state.context_mix >= 1.0:
		return g
	var a := cfg.grade_of(state.context_from)
	var t := clampf(state.context_mix, 0.0, 1.0)
	for k in g.keys():
		g[k] = lerpf(float(a[k]), float(g[k]), t)
	return g


## The factor the city's light layers (window lights, beacons, traffic, life) are multiplied
## by under grade `p`: the context's extra dim and map mode's dim.
static func brightness(p: Dictionary) -> float:
	return (1.0 - float(p["dim"])) * (1.0 - float(p["map_dim"]))


## `c` graded by `p` on the CPU (the same maths as city_live.gdshader's `grade()`, without
## the calm zones): tests and the silhouette's lit windows use it.
static func apply(c: Color, p: Dictionary) -> Color:
	var v := Vector3(c.r, c.g, c.b)
	var lift: float = p["lift"]
	v = v * (1.0 - lift) + Vector3(lift, lift * 0.85, lift * 0.6)
	var w: float = p["warmth"]
	v = Vector3(v.x * (1.0 + WARM_R * w), v.y * (1.0 + WARM_G * w), v.z * (1.0 - WARM_B * w))
	var k: float = p["contrast"]
	v = (v - Vector3.ONE * PIVOT) * k + Vector3.ONE * PIVOT
	var l := _luma(v)
	v = Vector3.ONE * l + (v - Vector3.ONE * l) * float(p["saturation"])
	var t: Color = p["tint"]
	var tl := maxf(_luma(Vector3(t.r, t.g, t.b)), 0.01)
	var hue := Vector3(t.r, t.g, t.b) * (_luma(v) / tl)
	v = v.lerp(hue, float(p["tint_amount"]))
	v *= brightness(p)
	return Color(clampf(v.x, 0.0, 1.0), clampf(v.y, 0.0, 1.0), clampf(v.z, 0.0, 1.0), c.a)


## Warmth's pull per channel at warmth 1 (red and a little green up, blue down) and the
## contrast pivot: shared with city_live.gdshader (keep them equal).
const WARM_R := 0.14
const WARM_G := 0.03
const WARM_B := 0.16
const PIVOT := 0.3


static func _luma(v: Vector3) -> float:
	return v.x * 0.299 + v.y * 0.587 + v.z * 0.114
