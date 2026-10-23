class_name StreetR2RenderConfigData
extends Resource
## Street look parity P2 step 2: the numbers of the Godot renderer of the street r2 frontage (`StreetR2Builder`): which buildings get a
## facade, how far a kit facade is pushed out of the city's own wall, the surface material numbers (MATERIAL_SPEC section 4), the prop and
## crown glb of the street kit, sign emission, lamp numbers. The plate's own rule numbers stay in `StreetR2ConfigData`. Read-only at runtime.

## Where the shipped config lives.
const CONFIG_PATH := "res://content/config/street_r2_render.tres"

static var _shipped: StreetR2RenderConfigData = null

## Facade selection and the concrete-band window rule: radius, lite radius, push, seen dot, minimum face / height, window numbers, wall families.
@export var facade: Dictionary = {}
## Surface material numbers per accumulator (`conc`, `glass`, `panel`, `solid`, `win`, `neon`): albedo, roughness, metal, emit.
@export var materials: Dictionary = {}
## Street kit files (`assets/street_kit/<file>.glb`) by prop kind / crown kind / lamp, and the prop tint numbers.
@export var props: Dictionary = {}
## Sign boards: emission gain, frame, texture cap, glyph-box height factor of the Godot fonts, font files.
@export var signs: Dictionary = {}
## Kerb lamps: head emission and the reference pole height of the glb; the street kit car lights (`headlight_emit`,
## `taillight_emit` slots): colour (linear rgb) and emission.
@export var lamps: Dictionary = {}

## Keys each field must hold.
const REQUIRED: Dictionary = {
	"facade": ["radius", "lite_radius", "push", "seen_dot", "min_face", "min_h", "win_p", "win_w_min", "win_w_max", "win_w_lo", "win_w_span",
		"win_h_lo", "win_h_span", "win_h_cap", "win_z", "win_tone_lo", "win_tone_span", "win_outset", "concrete_cells", "families", "terr_mix",
		"fallback_win", "wall_skin", "trim_band_h", "trim_corner_w", "trim_outset", "trim_seg", "rim_w", "rim_lift", "prism_sides", "wash_k", "face_share", "face_gain", "face_top", "face_fade0", "face_var"],
	"materials": ["conc", "glass", "panel", "solid", "win", "neon"],
	"props": ["kits", "emit_k", "lamp", "crowns", "crown_floors_k", "tint_mix"],
	"signs": ["emit_k", "frame_w", "frame_col", "frame_off", "measure_h_k", "font_anton", "font_mono", "ad_col_k"],
	"lamps": ["head_emit", "pole_scale_from", "car_head_color", "car_head_emit", "car_tail_color", "car_tail_emit"],
}


## Problems of this config: a missing key or a material without its numbers. Empty when sound.
func validate() -> PackedStringArray:
	var errs := PackedStringArray()
	for field: String in REQUIRED:
		var d: Dictionary = get(field)
		for key: String in REQUIRED[field]:
			if not d.has(key):
				errs.append("%s.%s missing" % [field, key])
	var fam: Array = facade.get("families", [])
	if fam.size() != 6:
		errs.append("facade.families needs six colours")
	for m: String in ["conc", "glass", "panel", "solid", "win", "neon"]:
		var row: Dictionary = materials.get(m, {})
		for k: String in ["albedo", "rough", "metal", "emit"]:
			if not row.has(k):
				errs.append("materials.%s.%s missing" % [m, k])
	return errs


## The shipped config (loaded once, then cached).
static func shipped() -> StreetR2RenderConfigData:
	if _shipped == null:
		_shipped = load(CONFIG_PATH) as StreetR2RenderConfigData
	return _shipped
