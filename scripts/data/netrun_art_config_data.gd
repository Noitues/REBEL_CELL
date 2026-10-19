class_name NetrunArtConfigData
extends Resource
## NA-21: every tuning number of the netrun-art GDScript twins (camera rig, HQ orbit, framing solver, dive,
## occlusion, LOD bands, section cut, street rules, HQ slots, reveal tiers). The shipped values live in
## `content/config/netrun_art.tres`, generated from the Python oracle (`tools/netrun_art/gen_twin_config.py`), so the
## twin and the oracle read the same numbers. Read-only at runtime. Each Dictionary mirrors the Python constant named in
## its doc line; the keys are the Python keys.

## Where the shipped config lives.
const CONFIG_PATH := "res://content/config/netrun_art.tres"

static var _shipped: NetrunArtConfigData = null

## Unit factors (`units.py`): `floor_bu` BU per storey, `kit_storey` HQ-kit units per storey, `k_fit` HQ scene factor.
@export var units: Dictionary = {}
## Street rig (`rig.RIG`): yaw, pitch, lens, fill, look bias, hover, timings (`t_step` 0.9 s, `t_zoom` 1.0 s), frame, solver.
@export var rig: Dictionary = {}
## The DECISION look-bias sign (`rig.LOOK_BIAS_SIGN`, +1 confirmed by art-pass).
@export var look_bias_sign: float = 1.0
## Dive path (`rig.DIVE`): duration, HQ lens, HQ yaw (layout36), HQ pitch, pitch lag.
@export var dive: Dictionary = {}
## Mainline HQ page camera fit (`rig.HQ_PAGE`).
@export var hq_page: Dictionary = {}
## HQ orbit rig (`orbit.HQ_RIG`); `dmin_kit` is the minimum distance in kit units (the rig's `dmin` = kit(dmin_kit)).
@export var hq_rig: Dictionary = {}
## Occlusion numbers (`occlusion.OCC`) plus `front_fade_kit`, `clutter_kit`, `ease_s`, `min_span` and the face band
## spacing (`occlusion.BAND`: `hq_step_deg`, `street_step_bu`).
@export var occlusion: Dictionary = {}
## LOD (`lod.py`): `d0`, `d1`, `bands` {name: [a, b]}, `floors`, `ramps`, `ramp_levels`.
@export var lod: Dictionary = {}
## Section cut (`section.py`): `zcut`, `look_blend`, `no_cut`, `poche`, `edge_col`, kit-unit pads.
@export var section: Dictionary = {}
## Street derivation rules (`derive.street.RULES`, without the keys that come from `units`/`layout`).
@export var street_rules: Dictionary = {}
## Layout numbers the street derivation reads (`layout.py`): front_band, extend, base_tol, axis_tol.
@export var layout: Dictionary = {}
## NA-11 layout rules (`layout.LAYOUT_RULES` + `layout.R2_RULES`): frontage_min_floors, border_street_width, base_street_width,
## hero_sign_rule, silhouette {...}, horizon {...}.
@export var layout_rules: Dictionary = {}
## HQ slot parameters (`hq.slots.SLOT_PARAMS`).
@export var slot_params: Dictionary = {}
## Art-pass landmark entrance anchors (`hq.slots.LANDMARK_ENTRIES`), provisional except Meridian.
@export var landmark_entries: Dictionary = {}
## Art-pass landmark face outlines (`hq.face_outlines.FACE_OUTLINES`, d591aa84): {corp: [[x, y], ...]}, BU relative to the HQ
## lot centre, closed, counter-clockwise. The HQ occlusion face band samples these.
@export var face_outlines: Dictionary = {}
## Reveal tiers per asset (PIPELINE_SPEC 5.2b): {asset: [[tier, d_far, d_near], ...]}, camera-to-asset BU. Placeholder
## defaults until the art-pass calibrates (open number N1).
@export var reveal: Dictionary = {}
## Frustum-offset parity tolerance, as a fraction of the frame width (AD item 5; `Camera3D.frustum_offset` against
## `shift_x` / `shift_y`).
@export var frustum_tolerance: float = 1.0e-4


## Keys each Dictionary field must hold (what the twins read).
const REQUIRED: Dictionary = {
	"units": ["floor_bu", "kit_storey", "k_fit"],
	"rig": ["yaw_max", "pitch_d", "lens_d", "fill_w", "fill_h", "look_bias", "hover_pull", "hover_yaw", "hover_dolly", "ov_yaw_k",
		"pitch_o", "lens_o", "fill_ow", "fill_oh", "ov_base_frac", "t_step", "t_hover_in", "t_hover_out", "t_zoom", "sensor_mm",
		"ref_w", "ref_h", "use", "solver_iters", "solver_bracket"],
	"dive": ["duration_s", "hq_lens", "hq_yaw_l36", "hq_pitch", "lag_k", "lag_pow"],
	"hq_page": ["fit_margin", "fit_share", "anchor", "ortho_clamp", "grid_ortho", "free"],
	"hq_rig": ["dmin_kit", "look_ahead", "pitch_lo", "pitch_hi", "lens_d", "fill_w", "fill_h", "hover_pull", "hover_yaw",
		"hover_dolly", "pitch_o", "lens_o", "fill_ow", "fill_oh", "vis_margin"],
	"occlusion": ["cone_margin", "stub", "ghost", "edge", "tsoft", "vsoft", "front_fade_kit", "clutter_kit", "ease_s", "min_span",
		"hq_step_deg", "street_step_bu"],
	"lod": ["d0", "d1", "bands", "floors", "ramps", "ramp_levels"],
	"section": ["zcut", "look_blend", "no_cut", "poche", "edge_col", "band_overview_kit", "band_rooms_kit", "zref_margin_kit",
		"plinth_kit", "widen"],
	"street_rules": ["base_floor", "room_inset", "room_depth", "room_px_target", "min_width", "max_setback", "room_z_inset",
		"link_offset", "link_stub"],
	"layout": ["front_band", "extend", "base_tol", "axis_tol"],
	"layout_rules": ["frontage_min_floors", "border_street_width", "base_street_width", "hero_sign_rule", "silhouette", "horizon"],
	"slot_params": ["lot_margin", "top_share", "min_half", "corner_pad", "room_w_max", "room_fill", "room_depth", "tier_floors",
		"link_out"],
}


## Problems of this config: a missing key, a reveal tier with `d_far <= d_near`, a bad tolerance. Empty when sound.
func validate() -> PackedStringArray:
	var errs := PackedStringArray()
	for field: String in REQUIRED:
		var d: Dictionary = get(field)
		for key: String in REQUIRED[field]:
			if not d.has(key):
				errs.append("%s.%s missing" % [field, key])
	for asset: String in reveal:
		for row: Array in reveal[asset]:
			if row.size() != 3 or float(row[1]) <= float(row[2]):
				errs.append("reveal.%s has a tier whose far edge is not beyond its near edge" % asset)
	if frustum_tolerance <= 0.0:
		errs.append("frustum_tolerance must be above 0")
	return errs


## The shipped config (loaded once, then cached).
static func shipped() -> NetrunArtConfigData:
	if _shipped == null:
		_shipped = load(CONFIG_PATH) as NetrunArtConfigData
	return _shipped
