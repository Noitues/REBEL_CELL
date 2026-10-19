class_name CityShaderConfigData
extends Resource
## NA-22: every tuning number of the netrun city shaders (`city_building` section / occlusion / look blend,
## `city_fog`, `beam_shaft`, `wet_street`, `streak_lane`) and the reduce-effects values. The shipped values live in
## `content/config/city_shaders.tres`; the occlusion colours (`poche`, `edge_col`), the ghost opacity and the LOD bands
## come from `NetrunArtConfigData` (one copy). Read-only at runtime; the uniform table is
## `docs/handoff/plan2/drafts/NA22_SHADER_PARAMS.md`.

## Where the shipped config lives.
const CONFIG_PATH := "res://content/config/city_shaders.tres"

static var _shipped: CityShaderConfigData = null

## Look blend: `ink_fade` (share of the ink pass removed at look_blend 1), `ink_floor` (lowest ink alpha factor), `exposure`
## (the Environment tonemap exposure at look_blend 1; 1 at 0; calibrated with `fog.peak` against the golden plate, 12.1).
@export var look: Dictionary = {}
## Reduce effects (ruling W1 NA-22 Q1): the clock stops at the plate's recorded `anim_t`; `anim_t_default` is used when the
## view gives none, `ease_s` is the ghost / cut ease (0 = the end state at once).
@export var reduce: Dictionary = {}
## `city_building` section and occlusion: corridor pad, side test, plinth colour and switch-on range, edge band and boost.
@export var building: Dictionary = {}
## `wet_street`: puddle noise, roughness ranges, specular, albedo multiplier.
@export var wet: Dictionary = {}
## `beam_shaft`: radial / axial profile, breakup, hot core, emission, sweep period.
@export var beam: Dictionary = {}
## `streak_lane`: loop seconds, emission, brightness profile, width, streak table size.
@export var streak: Dictionary = {}
## `city_fog` (PIPELINE_SPEC 4.1 and the calibration of 12.1): every term of the scatter volume.
@export var fog: Dictionary = {}
## The night sky at look_blend 1 (NA-22b, `city_sky`): zenith, horizon (the warm city glow) and ground colours (linear) and
## `glow_k`, the falloff of the glow band with sin(elevation); mixed from the mainline `sky` colour as look_blend rises.
@export var sky: Dictionary = {}

## Keys each Dictionary field must hold (what the shaders and the kit read).
const REQUIRED: Dictionary = {
	"look": ["ink_fade", "ink_floor", "exposure"],
	"reduce": ["anim_t_default", "ease_s"],
	"building": ["corridor_pad", "side_test", "plinth_albedo", "plinth_blue", "plinth_on", "plinth_off_bu", "edge_band_bu",
		"edge_alpha_boost", "window_dim", "facade_albedo", "facade_light", "win_share", "win_floor", "win_pow", "win_emit",
		"trim_emit", "landmark_dim", "haze_col", "haze_k", "haze_h", "haze_hi", "wash_floors", "wash_a", "wash_b", "wash_gain",
		"edge_share", "edge_a", "edge_b", "edge_emit", "edge_bu", "edge_blend", "beam_fade", "wash_floor_bu", "landmark_wash_gain"],
	"sky": ["top", "horizon", "ground", "glow_k"],
	"wet": ["noise_scale", "noise_octaves", "rough_noise", "rough_wet", "specular", "albedo_mul", "pbr_fade"],
	"beam": ["core_sigma", "core_w", "skirt_sigma", "skirt_w", "efold", "fade", "fade_from", "fade_in", "noise_scale",
		"noise_lo", "noise_hi", "hot", "emit", "period_s", "pitch_share", "start_radius", "length_front", "half_deg"],
	"streak": ["loop_s", "emit", "floor", "power", "width", "max_streaks", "z_lo", "z_hi"],
	"fog": ["peak", "h_front", "h_sky_k", "strata_k", "warp_k", "tilt", "bank_freq", "wisp_freq", "bank_mix", "remap_oct",
		"clump_freq", "remap_clump", "wisp_at", "wisp_half", "wisp_k", "front", "floor", "gb_off", "gb_top", "ground_bank",
		"mid_range", "mid_remap", "mid_bank", "haze", "haze_efold", "scatter", "anisotropy", "underlight_k", "ground_glow",
		"mid_glow", "emit_gain", "wind", "box", "length", "tint_a", "tint_b", "tint_c"],
}


## Problems of this config: a missing key, a bad range. Empty when sound.
func validate() -> PackedStringArray:
	var errs := PackedStringArray()
	for field: String in REQUIRED:
		var d: Dictionary = get(field)
		for key: String in REQUIRED[field]:
			if not d.has(key):
				errs.append("%s.%s missing" % [field, key])
	if errs.is_empty():
		if float(streak["loop_s"]) <= 0.0:
			errs.append("streak.loop_s must be above 0")
		if float(beam["period_s"]) <= 0.0:
			errs.append("beam.period_s must be above 0")
		if int(streak["max_streaks"]) < 1:
			errs.append("streak.max_streaks must be at least 1")
		if float(look["ink_fade"]) < 0.0 or float(look["ink_fade"]) > 1.0:
			errs.append("look.ink_fade must be within 0..1")
	return errs


## The shipped config (loaded once, then cached).
static func shipped() -> CityShaderConfigData:
	if _shipped == null:
		_shipped = load(CONFIG_PATH) as CityShaderConfigData
	return _shipped
