class_name GridMarkerProjection
extends RefCounted
## ART-5 5d: the one seam between the City Grid's Site markers (UI) and the city under them:
## where each Site's marker stands on screen (its pad, on the Site building's roof) for the
## camera now. Markers are UI over the unified 3D city (bible §4.1); they attach to 5a's
## seam: CityView3D (`project`, `top_at`, `camera_changed` / `band_changed` to re-place)
## or, headless, a CityModel with a CityIsoCamera (the same calls), so placement, labels
## and picking are tested without a window. Without a model (`from_camera`) the anchors lie
## on the street. Sites' lots come from `CityLayout.site_points` (the game's own layout).
## Pure apart from reading the view.

var camera: CityIsoCamera = null
var config: CityConfig = null
## The city model (roof heights); null: anchors on the street.
var model: CityModel = null
## The live view (its camera and viewport pixels); null: `camera` is used.
var view: CityView3D = null
## Site id -> lot point (CityLayout.site_points; the Site's lot, not its centre).
var lots: Dictionary = {}


## A projection of corporation `corp`'s Sites on the city model `p_model` through camera
## `cam` (headless: the same maths as the view).
static func from_model(p_model: CityModel, cam: CityIsoCamera, corp: CorporationData) -> GridMarkerProjection:
	var p := GridMarkerProjection.new()
	p.model = p_model
	p.config = p_model.cfg
	p.camera = cam
	p.lots = CityLayout.site_points(corp)
	return p


## A projection on the live 3D city `p_view` (5a's CityView3D); re-place the markers on its
## `camera_changed` and `band_changed`.
static func from_view(p_view: CityView3D, corp: CorporationData) -> GridMarkerProjection:
	var p := GridMarkerProjection.new()
	p.view = p_view
	p.model = p_view.model
	p.config = p_view.cfg
	p.camera = p_view.iso
	p.lots = CityLayout.site_points(corp)
	return p


## A projection through a camera alone, for config `cfg`'s view `view_name` at viewport
## `size`, aimed at the Sites' middle (anchors on the street).
static func from_camera(cfg: CityConfig, corp: CorporationData, size: Vector2, view_name: String = "grid") -> GridMarkerProjection:
	var p := GridMarkerProjection.new()
	p.config = cfg
	p.camera = CityIsoCamera.for_view(cfg, view_name, size)
	p.lots = CityLayout.site_points(corp)
	p.aim_at_sites()
	return p


## Points the camera at the Sites' middle (the Grid's framing before its fit).
func aim_at_sites() -> void:
	if lots.is_empty() or camera == null:
		return
	var mid := Vector2.ZERO
	for id in lots:
		mid += lots[id] as Vector2
	mid /= float(lots.size())
	camera.target = CityIsoCamera.lot_to_world(config, mid + Vector2(0.5, 0.5))


## The lots' bounding rect, grown by `margin` lots (the part of the city the Grid needs).
func lots_rect(margin: int = 0) -> Rect2i:
	var out := Rect2i()
	var first := true
	for id in lots:
		var l := Vector2i((lots[id] as Vector2).floor())
		out = Rect2i(l, Vector2i.ONE) if first else out.expand(l).expand(l + Vector2i.ONE)
		first = false
	return out.grow(margin)


## Height (BU) of Site `id`'s pad: the roof of its building (0: the street).
func height_of(id: StringName) -> float:
	var lot: Vector2 = lots.get(id, Vector2.INF)
	if lot.x == INF or model == null:
		return 0.0
	return model.top_at(Vector2i(lot.floor()))


## The world point of Site `id`'s pad (its lot's centre, on its roof).
func world_of(id: StringName) -> Vector3:
	var lot: Vector2 = lots.get(id, Vector2.INF)
	if lot.x == INF:
		return Vector3.INF
	return CityIsoCamera.lot_to_world(config, lot + Vector2(0.5, 0.5), height_of(id))


## Screen px of Site `id`'s anchor (INF when the Site is not on this map).
func anchor_of(id: StringName) -> Vector2:
	var w := world_of(id)
	if w == Vector3.INF:
		return Vector2.INF
	return view.project(w) if view != null else camera.project(w)


## Every Site's anchor (id -> screen px), ids sorted.
func anchors() -> Dictionary:
	var ids := lots.keys()
	ids.sort_custom(func(a: StringName, b: StringName) -> bool: return String(a) < String(b))
	var out := {}
	for id in ids:
		out[id] = anchor_of(id)
	return out


## The lot point under screen px `p` at Site `id`'s pad height (the inverse of `anchor_of`).
func lot_under(p: Vector2, id: StringName = &"") -> Vector2:
	var cam := view.iso if view != null else camera
	return CityIsoCamera.world_to_lot(config, cam.unproject(p, height_of(id))) - Vector2(0.5, 0.5)
