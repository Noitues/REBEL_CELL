class_name CityState
extends RefCounted
## What the city shows about the game (art pass W7, ART_BIBLE §9.3), as the screens pass it
## down: the screen's context, Heat, the campaign's progress and target corporation, the
## Cell's claimed Sites, map mode and the UI calm zones. A plain value object: the city's
## views read it and never write game state (signal up, call down). Pure: the Heat band
## comes from `Palette.heat_band` (the campaign config's MAJOR levels), never a copied
## number.

## Heat states (§9.3), the Palette.heat_band values.
enum Band { COOL, NOTICED, FLAGGED, HUNTED }
const BAND_NAMES: Array[String] = ["COOL", "NOTICED", "FLAGGED", "HUNTED"]

## &"title", &"hq", &"net" or &"combat" (CityLookData.CONTEXTS).
var context: StringName = &"title"
var heat: int = 0
## Heat band (Band); set with `set_heat`.
var band: int = Band.COOL
## Campaign progress 0..1 and the target corporation (its hue leans the grade).
var progress: float = 0.0
var corp_id: StringName = &""
## Grid lots (Vector2) of the Cell's claimed Sites.
var claims: PackedVector2Array = PackedVector2Array()
## Maps over the city (§9.5).
var map_mode: bool = false
## UI calm zones: rects in the city's local px (§2: nothing saturated or moving behind text).
var calm_zones: Array[Rect2] = []


## Sets Heat and its band. `major_levels` as in Palette.heat_band (empty: the config's).
func set_heat(p_heat: int, major_levels: Array[int] = []) -> void:
	heat = p_heat
	band = Palette.heat_band(p_heat, major_levels)


## The band's name (COOL, NOTICED, FLAGGED, HUNTED).
func band_name() -> String:
	return BAND_NAMES[clampi(band, 0, BAND_NAMES.size() - 1)]


## NOTICED and up: searchlights sweep the target corp's district.
func searchlights() -> bool:
	return band >= Band.NOTICED


## FLAGGED and up: patrol drones and the red/blue rim flicker on corp buildings.
func patrols() -> bool:
	return band >= Band.FLAGGED


## HUNTED: the desaturated grade and heavier haze.
func hunted() -> bool:
	return band >= Band.HUNTED


## A copy (the lab and tests compare states).
func duplicate_state() -> CityState:
	var s := CityState.new()
	s.context = context
	s.heat = heat
	s.band = band
	s.progress = progress
	s.corp_id = corp_id
	s.claims = claims.duplicate()
	s.map_mode = map_mode
	s.calm_zones = calm_zones.duplicate()
	return s
