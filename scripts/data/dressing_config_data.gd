class_name DressingConfigData
extends Resource
## NA-24: every tuning number of the street dressing (reveal groups, fade, caps, palette sets, district languages, HQ-distance
## bands, city-signage rules, sign / plume sizes). The shipped values live in `content/config/dressing_config.tres`. Distances of
## the reveal tiers stay in `netrun_art.tres` (`reveal`, PIPELINE_SPEC 5.2b: "N1 calibration pending"). Read-only at runtime.

## Where the shipped config lives.
const CONFIG_PATH := "res://content/config/dressing_config.tres"

static var _shipped: DressingConfigData = null

## Reveal groups: group id -> `{asset, tier}`; `asset` "" or a tier the asset does not list = the big layer (always drawn).
@export var groups: Dictionary = {}
## Tier fade: `share` of the tier interval (far - near) used as the cross-fade margin, `min_share` the floor (spec 5.2b: at least 10 %).
@export var fade: Dictionary = {}
## Caps: `glow_lights`, `beam_spots`, `city_signs`, `shopfronts`, `billboards`, `plumes`, and `chunk_bu` (the MultiMesh cell along the street).
@export var caps: Dictionary = {}
## Palette sets: set id -> {palette id: [r, g, b]}; `common` holds the ids every district shares (lamps, lanes). Per-district sets
## `win_N` ids are the art-pass window colours (city_preset.py DISTRICTS); sets are the art-pass district hue (district_a) and second light (district_b).
@export var palettes: Dictionary = {}
## District languages: territory id (`sprawl` for the neutral city) -> `{palette}`.
@export var districts: Dictionary = {}
## HQ-distance bands, nearest first: `{max_bu, sign_mul, emit_mul, plume_mul}`.
@export var hq_bands: Array = []
## City signage rules (route side frontage): `along_pad`, `depth_max`, `min_top`, shares per class, sizes.
@export var frontage: Dictionary = {}
## Sign geometry and emission.
@export var sign: Dictionary = {}
## Lamps: dot size, spill radius and gain.
@export var lamp: Dictionary = {}
## Ground glows and washes: radii and gains.
@export var glow: Dictionary = {}
## Steam plumes: puffs, rise, size, alpha, emission.
@export var plume: Dictionary = {}

const REQUIRED: Dictionary = {
	"fade": ["share", "min_share"],
	"caps": ["glow_lights", "beam_spots", "city_signs", "shopfronts", "billboards", "plumes", "chunk_bu"],
	"frontage": ["along_pad", "depth_max", "min_top", "sign_share", "shop_share", "billboard_share", "plume_share", "sign_w", "sign_h_min",
		"sign_h_max", "shop_h", "shop_z", "billboard_w", "billboard_h", "billboard_up"],
	"sign": ["neon_emit", "panel_emit", "band_emit", "flicker_emit", "depth", "pole", "gap", "flicker_bursts",
		"panel_level", "core_level", "core_max", "frame_w", "cell", "stroke_h", "fill", "cell_gap", "bright_var", "hero_panels", "hero_mix", "hero_mix_cut",
		"hero_panel_bright", "hero_panel_w", "pole_gain"],
	"lamp": ["dot", "spill_radius", "spill_gain", "dot_gain"],
	"glow": ["radius", "gain", "wash_radius", "wash_gain"],
	"plume": ["puffs", "rise", "size0", "size1", "alpha", "emit", "col", "loop_s", "ground_clear"],
}


## Problems of this config: a missing key, a bad range. Empty when sound.
func validate() -> PackedStringArray:
	var errs := PackedStringArray()
	for field: String in REQUIRED:
		var d: Dictionary = get(field)
		for key: String in REQUIRED[field]:
			if not d.has(key):
				errs.append("%s.%s missing" % [field, key])
	if groups.is_empty():
		errs.append("groups empty")
	if not palettes.has("common"):
		errs.append("palettes.common missing")
	if hq_bands.is_empty():
		errs.append("hq_bands empty")
	if errs.is_empty():
		if float(fade["min_share"]) < 0.1:
			errs.append("fade.min_share must be at least 0.1")
		for g: String in groups:
			if not (groups[g] as Dictionary).has("asset") or not (groups[g] as Dictionary).has("tier"):
				errs.append("groups.%s needs asset and tier" % g)
		for t: String in districts:
			if not palettes.has(String(districts[t]["palette"])):
				errs.append("districts.%s palette %s is not a set" % [t, districts[t]["palette"]])
		for s: String in palettes:
			if s == "common":
				continue
			for id: String in ["district_a", "district_b", "accent_warm", "accent_cool"]:
				if not (palettes[s] as Dictionary).has(id):
					errs.append("palettes.%s.%s missing" % [s, id])
	return errs


## The shipped config (loaded once, then cached).
static func shipped() -> DressingConfigData:
	if _shipped == null:
		_shipped = load(CONFIG_PATH) as DressingConfigData
	return _shipped
