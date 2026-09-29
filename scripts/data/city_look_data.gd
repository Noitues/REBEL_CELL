class_name CityLookData
extends Resource
## The city's presentation numbers (art pass W7, ART_BIBLE §9, §8 T0, §13): lighting, the
## per-context grade, T0 life, Heat reactivity, territory, maps over the city, the UI calm
## zones and the quality tiers. One read-only resource, `content/config/city_look.tres`;
## the city's views read it (`CityLookData.shipped()`) and never change it. No game rule
## reads it.

const PATH := "res://content/config/city_look.tres"
## The contexts a screen names (`CityAtmosphere.set_context`).
## Art pass W9F: &"flatline" is the grey of a lost run or campaign (ART_BIBLE §11 "Run
## failed", "Campaign end" LOST): the whole city desaturated and dimmed, the corp lean gone.
const CONTEXTS: Array[StringName] = [&"title", &"hq", &"net", &"combat", &"flatline"]
## Art pass W9F: an optional grade key: the share of the campaign's corp lean a context
## keeps (1 when absent; the flatline keeps none, so the grey is grey).
const LEAN_KEY := "lean"
## The grade keys each context carries (see `grades`).
const GRADE_KEYS: Array[String] = ["contrast", "saturation", "warmth", "lift", "dim"]
## Neon inks the glow is tuned for (CityPalette.INKS order).
const INK_COUNT := 5
## Heat bands (Palette.heat_band: COOL, NOTICED, FLAGGED, HUNTED).
const BAND_COUNT := 4
## ART_BIBLE §8 T0: the slowest-allowed ambient loop period (s). Equal to VfxTier.T0_MIN_PERIOD
## (a test checks it); a data schema never depends on the view kit.
const T0_MIN_PERIOD := 3.0

@export_group("Lighting (§9.1)")
## Per-ink glow gain (amber, violet, pink, cyan, green): how strongly each ink blooms.
@export var ink_glow: PackedFloat32Array = PackedFloat32Array([0.9, 1.15, 1.0, 0.8, 0.85])
## Brightness a baked pixel must pass before it glows (0..1 luma), the glow's reach (texture
## px) and its overall strength.
@export var glow_threshold: float = 0.3
@export var glow_radius_px: float = 5.0
@export var glow_strength: float = 0.8
## Haze bands in depth: centre (0 top .. 1 bottom of the view), half-width (same units) and
## density (0..1) each; their slow drift's period (s, T0: at least 3) and reach (share of
## the view).
@export var haze_band_y: PackedFloat32Array = PackedFloat32Array([0.16, 0.46, 0.8])
@export var haze_band_width: PackedFloat32Array = PackedFloat32Array([0.1, 0.13, 0.16])
@export var haze_band_alpha: PackedFloat32Array = PackedFloat32Array([0.2, 0.13, 0.1])
@export var haze_drift_period: float = 26.0
@export var haze_drift: float = 0.02
## Wet streets: how much of the lights above a dark ground pixel reflects, how far up the
## reflection reaches (texture px) and its ripple's period (s, T0) and sway (texture px).
@export var reflection_strength: float = 0.45
@export var reflection_reach_px: float = 16.0
@export var reflection_ripple_period: float = 5.0
@export var reflection_ripple_px: float = 1.5
## Rim light from the brightest signs: how many signs light their surroundings, their reach
## (share of the view's height) and strength.
@export var rim_lights_max: int = 6
@export var rim_radius: float = 0.16
@export var rim_strength: float = 1.6

@export_group("Grade (§9.1, §9.3)")
## Per context: {"contrast", "saturation", "warmth" (-1 cool .. +1 warm), "lift" (raised,
## dirty blacks), "dim" (the city's total darkening the context asks for, 0..1)}.
@export var grades: Dictionary = {
	&"title": {"contrast": 1.05, "saturation": 1.0, "warmth": 0.0, "lift": 0.0, "dim": 0.0},
	&"hq": {"contrast": 0.94, "saturation": 0.82, "warmth": 0.45, "lift": 0.035, "dim": 0.0},
	&"net": {"contrast": 1.22, "saturation": 1.08, "warmth": -0.4, "lift": 0.0, "dim": 0.0},
	&"combat": {"contrast": 1.3, "saturation": 0.92, "warmth": -0.25, "lift": 0.0, "dim": 0.35},
	&"flatline": {"contrast": 1.0, "saturation": 0.0, "warmth": 0.0, "lift": 0.0, "dim": 0.35, "lean": 0.0},
}
## Campaign progress: the grade leans this far (at progress 1) toward the target corp's hue.
@export var progress_max_shift: float = 0.2

@export_group("Heat (§9.3)")
## NOTICED searchlights: how many sweep, their sweep period (s, T0), half-arc (degrees),
## beam half-width (degrees), length (share of the view's height) and brightness.
@export var searchlight_count: int = 2
@export var searchlight_period: float = 11.0
@export var searchlight_arc_deg: float = 38.0
@export var searchlight_width_deg: float = 6.0
@export var searchlight_length: float = 0.9
@export var searchlight_alpha: float = 0.45
## FLAGGED: the red/blue rim flicker's rate (Hz, at most 1: §9.3) and strength, and the
## patrol drones added to the life layer.
@export var flagged_flicker_hz: float = 0.8
@export var flagged_rim_strength: float = 3.0
@export var flagged_drones: int = 3
## HUNTED: the grade's saturation drop (§9.3: 25%) and how much heavier the haze gets.
@export var hunted_desaturate: float = 0.25
@export var hunted_haze_gain: float = 1.8

@export_group("Territory (§9.3)")
## Claimed districts: spray tags per claimed Site, their size (px), the CELL_TURF hatch's
## alpha, spacing and line width (px), its reach round the Site (lots), and the light
## leaking into the haze (strength, radius in lots).
@export var tags_per_site: int = 3
@export var tag_size_px: float = 26.0
@export var tag_alpha: float = 0.9
@export var hatch_alpha: float = 0.32
@export var hatch_spacing_px: float = 7.0
@export var hatch_width_px: float = 1.6
@export var hatch_reach_lots: float = 3.2
@export var leak_strength: float = 0.12
@export var leak_radius_lots: float = 6.0
## The territory spread's lasting wash (a hatch now, not the flat khaki): its strength.
@export var wash_gain: float = 0.4

@export_group("Maps over the city (§9.5) and calm zones (§2)")
## Map mode: the city's dim (§9.5: 40%) and blur (texture px).
@export var map_dim: float = 0.4
@export var map_blur_px: float = 2.5
## UI calm zones: how much darker and less saturated the city is behind text, their soft
## edge (px) and the extra darkening under high contrast.
@export var calm_dim: float = 0.45
@export var calm_desaturate: float = 0.75
@export var calm_feather_px: float = 28.0
@export var high_contrast_calm_dim: float = 0.3

@export_group("Life (§9.2, §8 T0)")
## Density of life per Heat band (COOL, NOTICED, FLAGGED, HUNTED): multiplies the counts.
@export var life_density: PackedFloat32Array = PackedFloat32Array([0.6, 0.8, 1.0, 1.3])
## Aircraft: at most this many at full density; seconds to cross the view (T0), their
## blinker's period (s, T0) and lit share.
@export var aircraft_max: int = 5
@export var aircraft_cross_seconds: float = 34.0
@export var aircraft_blink_period: float = 3.0
@export var aircraft_blink_on: float = 0.12
## Drone patrols: at most this many at full density, their loop period (s, T0), the share
## of each loop a drone is out (occasional), and their loop radius (lots).
@export var drones_max: int = 3
@export var drone_period: float = 20.0
@export var drone_out_share: float = 0.55
@export var drone_radius_lots: float = 5.0
## Billboards: at most this many at full density, their loop period (s, T0), size (px) and
## brightness.
@export var billboards_max: int = 7
@export var billboard_period: float = 9.0
@export var billboard_size_px: Vector2 = Vector2(30, 16)
@export var billboard_alpha: float = 0.8
## Window lights toggling (NeonCity's GPU layer): the shortest toggle period (s, T0).
@export var window_period_min: float = 3.0

@export_group("Silhouette (§9.4)")
## The pre-render while a bake runs: a mass's height when the placement doesn't know it
## (px), the share of its face cells lit as windows, and the masses' alpha.
@export var silhouette_height_px: float = 40.0
@export var silhouette_window_share: float = 0.07
@export var silhouette_alpha: float = 0.95

@export_group("Quality (§13)")
## Glow taps per quality tier (0 low .. 2 high); the default tier.
@export var quality_glow_taps: PackedInt32Array = PackedInt32Array([0, 6, 12])
@export var quality_default: int = 2


static var _shipped: CityLookData = null


## The shipped look (loaded once, read only).
static func shipped() -> CityLookData:
	if _shipped == null:
		_shipped = load(PATH) as CityLookData
		if _shipped == null:
			_shipped = CityLookData.new()
	return _shipped


## The grade values of `context` (the title's when unknown), each GRADE_KEYS key present.
func grade_of(context: StringName) -> Dictionary:
	var g: Dictionary = grades.get(context, grades.get(&"title", {}))
	var out := {"contrast": 1.0, "saturation": 1.0, "warmth": 0.0, "lift": 0.0, "dim": 0.0, LEAN_KEY: 1.0}
	for k in GRADE_KEYS:
		if g.has(k):
			out[k] = float(g[k])
	if g.has(LEAN_KEY):
		out[LEAN_KEY] = clampf(float(g[LEAN_KEY]), 0.0, 1.0)
	return out


## Every problem with the values (content validation).
func validate() -> PackedStringArray:
	var errors := PackedStringArray()
	if ink_glow.size() != INK_COUNT:
		errors.append("ink_glow needs %d gains (one per ink)" % INK_COUNT)
	if haze_band_y.size() != haze_band_width.size() or haze_band_y.size() != haze_band_alpha.size():
		errors.append("haze bands: y, width and alpha need the same count")
	if haze_band_y.size() < 2 or haze_band_y.size() > 3:
		errors.append("two or three haze bands (§9.1)")
	if life_density.size() != BAND_COUNT:
		errors.append("life_density needs %d values (one per Heat band)" % BAND_COUNT)
	for c in CONTEXTS:
		if not grades.has(c):
			errors.append("no grade for context '%s'" % c)
	# §8 T0: ambient loops are slow (a period of at least VfxTier.T0_MIN_PERIOD).
	var loops := {"haze_drift_period": haze_drift_period, "reflection_ripple_period": reflection_ripple_period,
		"searchlight_period": searchlight_period, "aircraft_cross_seconds": aircraft_cross_seconds,
		"aircraft_blink_period": aircraft_blink_period, "drone_period": drone_period,
		"billboard_period": billboard_period, "window_period_min": window_period_min}
	for k: String in loops:
		if float(loops[k]) < T0_MIN_PERIOD:
			errors.append("%s under the T0 floor of %.1f s" % [k, T0_MIN_PERIOD])
	if flagged_flicker_hz <= 0.0 or flagged_flicker_hz > 1.0:
		errors.append("flagged_flicker_hz must be in (0, 1] (§9.3: at most 1 Hz)")
	if progress_max_shift < 0.0 or progress_max_shift > 0.2:
		errors.append("progress_max_shift in 0..0.2 (§9.3)")
	if quality_glow_taps.size() != 3 or quality_default < 0 or quality_default > 2:
		errors.append("three quality tiers, default 0..2")
	return errors
