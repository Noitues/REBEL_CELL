class_name TideLookData
extends Resource
## The look numbers of the Infected Tide raid screen (sizes, alphas, timings that are look, not rules). The shipped values live in
## `content/config/tide_look.tres`; `TideFx` reads them. Art-pass owns the values; build owns flow / layout / rules. Read-only at runtime.

## Where the shipped look lives.
const CONFIG_PATH := "res://content/config/tide_look.tres"

# ---- the map layer
## Dash lengths of a dashed beam (px).
@export var dash_on: float = 10.0
@export var dash_off: float = 7.0
## The radii of the front / TAKEN tint, an INFECTED disk and a HOME tier glyph (px).
@export var front_r: float = 30.0
@export var infect_r: float = 22.0
@export var home_glyph_r: float = 11.0
## The black under-stroke of a beam, as a share of its alpha.
@export var ink_alpha: float = 0.7
## A beam that is not the focused one keeps this share of its alpha.
@export var focus_dim: float = 0.18
## An impact on a Site: ring radius, spoke count, the swell period (s).
@export var impact_r: float = 16.0
@export var impact_spokes: int = 8
@export var impact_period: float = 0.9
## A route chip's radius (px).
@export var chip_r: float = 8.0
## The pulse's head radius (px) and the share of the drawn beam its bright tail covers.
@export var pulse_r: float = 9.0
@export var pulse_tail: float = 0.22
## The padding of a label plate (px).
@export var label_pad: float = 5.0
## The flying INFECTED card (px) and how far it arcs up on the way.
@export var flight_w: float = 20.0
@export var flight_h: float = 28.0
@export var flight_arc: float = 46.0
## The infection bloom's radius, the burst spoke count and the radius a heavy hit swells to (px).
@export var bloom_r: float = 44.0
@export var burst_spokes: int = 12
@export var slam_r: float = 72.0
## A sentry's scale on the map and the alpha of a ghosted (previewed) response.
@export var sentry_scale: float = 1.3
@export var ghost_alpha: float = 0.7

# ---- glyphs and widgets
## The shade of a sentry's disk.
@export var disk_alpha: float = 0.62
## A forecast tile's fill alpha.
@export var tile_fill_alpha: float = 0.3
## The INFECTED meter: gap between cells and the widest cell (px).
@export var meter_gap: float = 2.0
@export var meter_cell_max: float = 16.0
## The odds bar: the narrowest segment that carries a tier glyph (px).
@export var odds_glyph_min_w: float = 26.0
## The thickness of a selected card's outline (px).
@export var select_edge_w: float = 3.0

# ---- screen flashes and the art hooks
## The alpha of the full-map flash a heavy hit (slam) and a HOME hit start at.
@export var slam_flash_alpha: float = 0.16
@export var home_flash_alpha: float = 0.2
## The CITY LOST wash: how far the red is darkened and its alpha.
@export var lost_wash_darken: float = 0.82
@export var lost_wash_alpha: float = 0.93
## Camera shake on a HOME hit and on CITY LOST: strength (px of the map frame; 0 = none, the shipped look) and seconds.
@export var home_hit_shake_strength: float = 0.0
@export var home_hit_shake_secs: float = 0.25
@export var city_lost_shake_strength: float = 0.0
@export var city_lost_shake_secs: float = 0.4


## The shipped look (loaded once). Read-only.
static func shipped() -> TideLookData:
	if _shipped == null:
		_shipped = load(CONFIG_PATH) as TideLookData
		if _shipped == null:
			_shipped = TideLookData.new()
	return _shipped


static var _shipped: TideLookData = null


## The problems of this look: empty when valid.
func validate() -> PackedStringArray:
	var errs := PackedStringArray()
	for f in ["dash_on", "dash_off", "front_r", "infect_r", "home_glyph_r", "impact_r", "chip_r", "pulse_r", "label_pad", "flight_w",
			"flight_h", "bloom_r", "slam_r", "sentry_scale", "meter_cell_max", "select_edge_w", "impact_period"]:
		if float(get(f)) <= 0.0:
			errs.append("%s must be > 0" % f)
	for f in ["ink_alpha", "focus_dim", "pulse_tail", "ghost_alpha", "disk_alpha", "tile_fill_alpha", "slam_flash_alpha", "home_flash_alpha",
			"lost_wash_darken", "lost_wash_alpha"]:
		var v := float(get(f))
		if v < 0.0 or v > 1.0:
			errs.append("%s must be in 0..1" % f)
	for f in ["home_hit_shake_strength", "home_hit_shake_secs", "city_lost_shake_strength", "city_lost_shake_secs"]:
		if float(get(f)) < 0.0:
			errs.append("%s must be >= 0" % f)
	if impact_spokes < 1 or burst_spokes < 1:
		errs.append("spoke counts must be >= 1")
	return errs
