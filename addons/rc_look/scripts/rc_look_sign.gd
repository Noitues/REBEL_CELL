class_name RcLookSign
extends RefCounted
## LOOK-TOOLBOX module 11: signage and neon. The shader side is rc_sign.gdshaderinc; this is its exact GDScript mirror
## plus the presets (config/look_sign.tres: "flat" today's signs, "lighten" the tube lightened toward the core colour,
## "hot" a thin white-hot core). Pure: no Node, no Settings.

const DEFAULT_PATH := "res://addons/rc_look/config/look_sign.tres"
const REQUIRED: Array[StringName] = [&"flat", &"lighten", &"hot"]

static var _cfg: RcLookSignConfig


## The shipped presets, loaded once.
static func default_config() -> RcLookSignConfig:
	if _cfg == null:
		_cfg = load(DEFAULT_PATH) as RcLookSignConfig
	return _cfg


## A shipped preset by name (null when unknown).
static func preset(name: StringName) -> RcLookSignPreset:
	return default_config().presets.get(name) as RcLookSignPreset


## exp(-0.5 (r / sigma)^2), as rcl_gauss.
static func gauss(r: float, sigma: float) -> float:
	return exp(-0.5 * (r / sigma) * (r / sigma))


## Toward white by hot x core01, as rcl_hot.
static func hot(col: Color, core01: float, k_hot: float) -> Color:
	return hot_to(col, Color(1, 1, 1), k_hot * clampf(core01, 0.0, 1.0))


## Toward a core colour by k, as rcl_hot_to.
static func hot_to(col: Color, core_col: Color, k: float) -> Color:
	var t := clampf(k, 0.0, 1.0)
	return Color(lerpf(col.r, core_col.r, t), lerpf(col.g, core_col.g, t), lerpf(col.b, core_col.b, t))


## A tube's own core colour: core_col tinted toward the tube by tint, as rcl_neon_core.
static func neon_core(tube: Color, core_col: Color, tint: float) -> Color:
	return hot_to(core_col, tube, tint)


## The approved hot core at distance d from a tube's centre line (half width half_w, one pixel = pix, same units), as
## rcl_neon_hot.
static func neon_hot(tube: Color, d: float, half_w: float, pix: float, k_hot: float, share: float, min_px: float,
		core_col: Color, tint: float, thin_px: float, thin_hot: float) -> Color:
	var cw := maxf(share * half_w, min_px * pix)
	var w_px := 2.0 * half_w / maxf(pix, 1e-6)
	var k := lerpf(thin_hot, k_hot, clampf((w_px - min_px) / maxf(thin_px - min_px, 1e-5), 0.0, 1.0))
	return hot_to(tube, neon_core(tube, core_col, tint), k * tube_core(d, cw))


## A stroke's coverage at distance d from its centre line, as rcl_tube_cov.
static func tube_cov(d: float, half_w: float, pix: float) -> float:
	return clampf((half_w - d) / maxf(pix, 1e-5) + 0.5, 0.0, 1.0)


## 1 on the centre line falling to 0 at core_w, as rcl_tube_core.
static func tube_core(d: float, core_w: float) -> float:
	return 1.0 - smoothstep(0.0, maxf(core_w, 1e-5), d)


## dress_neon's flicker at t01 (0..1 through the loop), as rcl_flicker.
static func flicker(t01: float, bursts: float, seed: float, burst_len: float, hum_hz: float, hum_floor: float) -> float:
	var u := fposmod(t01 * bursts + seed, 1.0)
	var burst := 1.0 - smoothstep(0.0, burst_len, u)
	var hum := 0.5 + 0.5 * sin(TAU * (t01 * hum_hz + seed))
	return burst * (hum_floor + (1.0 - hum_floor) * hum)


## city_glow's blink, as rcl_blink.
static func blink(ph: float, duty: float, off: float) -> float:
	return 1.0 if ph < duty else off


## city_glow's beacon, as rcl_beacon.
static func beacon(ph: float) -> float:
	return 0.2 + 0.8 * pow(maxf(0.0, cos(ph * TAU)), 4.0)


## The colour at distance d from a tube's centre line under preset p (tube colour col): flat, lightened toward the core
## colour across the tube, or a hot core of width core_share x half width.
static func tube_color(p: RcLookSignPreset, col: Color, d: float) -> Color:
	match p.treatment:
		RcLookSignPreset.Treatment.LIGHTEN:
			return hot_to(col, neon_core(col, p.core_color, p.core_tint), p.hot)
		RcLookSignPreset.Treatment.HOT:
			return neon_hot(col, d, p.half_w_px, 1.0, p.hot, p.core_share, p.core_min_px, p.core_color, p.core_tint,
					p.core_thin_px, p.core_thin_hot)
	return col
