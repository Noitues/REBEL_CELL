class_name CityIsoCamera
extends RefCounted
## ART-1 1D: the one orthographic iso camera of the unified city (bible §4.1: yaw 135°,
## pitch 40°; only target and zoom change). Pure maths shared by the 3D view, the baked
## view and the tests: world <-> screen projection, ground picking, the zoom's `lod` and a
## raid fit. World: X = (lot x - centre x) * lot_bu, Z = (lot y - centre y) * lot_bu,
## Y up (the concept's Blender frame (x, y, z) is Godot (x, z, -y)). `ortho` is the
## view's WIDTH in world units (Blender ortho_scale, 16:9).

var yaw_deg: float = 135.0
var pitch_deg: float = 40.0
var target: Vector3 = Vector3.ZERO
var ortho: float = 440.0
var viewport: Vector2 = Vector2(1920, 1080)
var distance: float = 2600.0


## A camera from the config for view `view_name` ("grid", "raid", "netrun", "close").
static func for_view(cfg: CitySpikeConfig, view_name: String, size: Vector2) -> CityIsoCamera:
	var c := CityIsoCamera.new()
	c.yaw_deg = cfg.yaw_deg
	c.pitch_deg = cfg.pitch_deg
	c.distance = cfg.camera_distance
	c.viewport = size
	var v: Array = cfg.views[view_name]
	c.target = lot_to_world(cfg, Vector2(float(v[0]), float(v[1])))
	c.ortho = float(v[2])
	return c


## World position (height 0) of lot point `lot` (lots, not lot centres).
static func lot_to_world(cfg: CitySpikeConfig, lot: Vector2, height: float = 0.0) -> Vector3:
	return Vector3((lot.x - cfg.district_centre.x) * cfg.lot_bu, height, (lot.y - cfg.district_centre.y) * cfg.lot_bu)


## Lot point of world position `w`.
static func world_to_lot(cfg: CitySpikeConfig, w: Vector3) -> Vector2:
	return Vector2(w.x / cfg.lot_bu + cfg.district_centre.x, w.z / cfg.lot_bu + cfg.district_centre.y)


## The view direction (from the camera into the scene).
func forward() -> Vector3:
	var yw := deg_to_rad(yaw_deg)
	var pt := deg_to_rad(pitch_deg)
	return Vector3(cos(yw) * cos(pt), -sin(pt), -sin(yw) * cos(pt))


## Screen right in world space.
func right() -> Vector3:
	var yw := deg_to_rad(yaw_deg)
	return Vector3(sin(yw), 0.0, cos(yw))


## Screen up in world space.
func up() -> Vector3:
	return right().cross(forward())


## The Camera3D transform (looks along forward(), `distance` back from the target).
func transform() -> Transform3D:
	var b := Basis(right(), up(), -forward())
	return Transform3D(b, target - forward() * distance)


## Screen pixel of world point `w`.
func project(w: Vector3) -> Vector2:
	var d := w - target
	var xc := d.dot(right())
	var yc := d.dot(up())
	var oh := ortho * viewport.y / viewport.x
	return Vector2((xc / ortho + 0.5) * viewport.x, (0.5 - yc / oh) * viewport.y)


## The world point at height `height` under screen pixel `p` (ground picking).
func unproject(p: Vector2, height: float = 0.0) -> Vector3:
	var o := ray_origin(p)
	var f := forward()
	return o + f * ((height - o.y) / f.y)


## The ray origin (on the plane through the target) for screen pixel `p`.
func ray_origin(p: Vector2) -> Vector3:
	var oh := ortho * viewport.y / viewport.x
	var xc := (p.x / viewport.x - 0.5) * ortho
	var yc := (0.5 - p.y / viewport.y) * oh
	return target + right() * xc + up() * yc


## World units per screen pixel.
func bu_per_px() -> float:
	return ortho / viewport.x


## The continuous zoom level (post40.lod_of): 0 transit, 1 raid, 2 city.
static func lod_of(cfg: CitySpikeConfig, p_ortho: float) -> float:
	if p_ortho >= cfg.lod_ortho_raid:
		return 1.0 + minf(1.0, log(p_ortho / cfg.lod_ortho_raid) / log(cfg.lod_ortho_city / cfg.lod_ortho_raid))
	return maxf(0.0, log(p_ortho / cfg.lod_ortho_transit) / log(cfg.lod_ortho_raid / cfg.lod_ortho_transit))


## Fits target and ortho to world points `pts` plus `margin` BU, ortho clamped to
## [lo, hi] (the raid fitted to the network, Appendix C #13).
func fit(pts: Array[Vector3], margin: float, lo: float, hi: float) -> void:
	if pts.is_empty():
		return
	var r := right()
	var u := up()
	var min_x := INF
	var max_x := -INF
	var min_y := INF
	var max_y := -INF
	for w in pts:
		min_x = minf(min_x, w.dot(r))
		max_x = maxf(max_x, w.dot(r))
		min_y = minf(min_y, w.dot(u))
		max_y = maxf(max_y, w.dot(u))
	var cx := (min_x + max_x) * 0.5
	var cy := (min_y + max_y) * 0.5
	var need := maxf(max_x - min_x, (max_y - min_y) * viewport.x / viewport.y) + margin * 2.0
	ortho = clampf(need, lo, hi)
	# The point on the ground whose screen-plane coordinates are (cx, cy).
	var o := r * cx + u * cy
	var f := forward()
	target = o + f * ((0.0 - o.y) / f.y)
