class_name RaidMapAnchor
extends RefCounted
## ART-6 3A: the one projection seam every raid mark goes through (pencil routes, state marks,
## the drag's dock circle, threat icons' anchors): a raid Site or a street on the map as a
## point in global (screen) px. It reads the CityMapOverlay; ART-3 6w: on the unified 3D city
## the overlay's projection is the city camera's (NeonCity city-3D mode: yaw 135°, pitch 40°,
## roofs at their 3D height), so every mark follows the city camera through this one seam
## unchanged. INF / empty when the Site is off the map.


## Site `id`'s node on `overlay`'s map (global px; INF off the map).
static func site(overlay: CityMapOverlay, id: StringName) -> Vector2:
	if overlay == null or not is_instance_valid(overlay):
		return Vector2.INF
	var p := overlay.icon_at(id)
	if p.x == INF:
		return Vector2.INF
	return overlay.get_global_transform() * p


## The street from Site `a` to Site `b` on `overlay`'s map (global px, node to node).
static func street(overlay: CityMapOverlay, a: StringName, b: StringName) -> PackedVector2Array:
	var out := PackedVector2Array()
	if overlay == null or not is_instance_valid(overlay):
		return out
	var xf := overlay.get_global_transform()
	for q in overlay.route_between(a, b):
		out.append(xf * overlay.grid_point_local(q))
	return out


## Global px per map local px (the map's zoom), for sizes given in local px.
static func scale(overlay: CityMapOverlay) -> float:
	if overlay == null or not is_instance_valid(overlay):
		return 1.0
	return overlay.get_global_transform().get_scale().x
