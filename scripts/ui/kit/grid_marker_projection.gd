class_name GridMarkerProjection
extends RefCounted
## ART-5 5d: the one seam between the City Grid's Site markers (UI) and the city under them:
## where each Site's marker stands on screen (its street point, the pad) for the camera now.
## Markers are UI over the unified 3D city (bible §4.1, 1D's report "What ART-5 needs" 1):
## until 5a's production CityModel and camera land, this projects through 1D's spike classes
## (`CityIsoCamera`, the locked yaw 135 / pitch 40 ortho camera) from the Sites' lots
## (`CityLayout.site_points`, the game's own layout); 5a's model attaches here and nothing
## above it changes. Pure (no Node): the placement and picking tests run headless.

var camera: CityIsoCamera = null
var config: CitySpikeConfig = null
## Site id -> lot point (CityLayout.site_points; the Site's lot, not its centre).
var lots: Dictionary = {}
## Height (BU) the anchor sits at: the pad lies on the street.
var anchor_height: float = 0.0


## A projection of corporation `corp`'s Sites through the spike camera for view `view_name`
## of `cfg` at viewport `size`, aimed at the Sites' middle.
static func from_spike(cfg: CitySpikeConfig, corp: CorporationData, size: Vector2, view_name: String = "grid") -> GridMarkerProjection:
	var p := GridMarkerProjection.new()
	p.config = cfg
	p.camera = CityIsoCamera.for_view(cfg, view_name, size)
	p.lots = CityLayout.site_points(corp)
	if not p.lots.is_empty():
		var mid := Vector2.ZERO
		for id in p.lots:
			mid += p.lots[id] as Vector2
		mid /= float(p.lots.size())
		p.camera.target = CityIsoCamera.lot_to_world(cfg, mid + Vector2(0.5, 0.5))
	return p


## The world point of Site `id`'s street point (its lot's centre).
func world_of(id: StringName) -> Vector3:
	var lot: Vector2 = lots.get(id, Vector2.INF)
	if lot.x == INF:
		return Vector3.INF
	return CityIsoCamera.lot_to_world(config, lot + Vector2(0.5, 0.5), anchor_height)


## Screen px of Site `id`'s anchor (INF when the Site is not on this map).
func anchor_of(id: StringName) -> Vector2:
	var w := world_of(id)
	return Vector2.INF if w == Vector3.INF else camera.project(w)


## Every Site's anchor (id -> screen px), ids sorted.
func anchors() -> Dictionary:
	var ids := lots.keys()
	ids.sort_custom(func(a: StringName, b: StringName) -> bool: return String(a) < String(b))
	var out := {}
	for id in ids:
		out[id] = anchor_of(id)
	return out


## The lot under screen px `p` on the street plane (the inverse of `anchor_of`).
func lot_under(p: Vector2) -> Vector2:
	return CityIsoCamera.world_to_lot(config, camera.unproject(p, anchor_height)) - Vector2(0.5, 0.5)
