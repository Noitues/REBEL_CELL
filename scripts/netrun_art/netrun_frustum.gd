class_name NetrunFrustum
extends RefCounted
## NA-21: maps a twin pose (`NetrunPose`) to the Godot `Camera3D` settings that reproduce it (DERIVE_V2_REVIEW Q1.8, AD 5):
## `PROJECTION_FRUSTUM`, `keep_aspect = KEEP_WIDTH`, `size` = the frame height at the near plane (Godot multiplies it by the aspect; 36 mm sensor, horizontal
## fit), `frustum_offset` = the lens shift (`shift_x` / `shift_y`, fractions of the frame width) times that width. A
## positive shift moves the picture left (x) and down (y), which is the frustum window moving right / up.
## Plan coordinates (x east, y north, z up) map to Godot world space as `(x, z, -y)`.


## The frame width in world units at the near plane for lens `lens_mm`: `near * sensor / lens`.
static func frame_width(lens_mm: float, near: float) -> float:
	var sensor: float = NetrunArtConfigData.shipped().rig["sensor_mm"]
	return near * sensor / lens_mm


## `Camera3D.size` for the pose at near plane `near`.
static func frustum_size(pose: NetrunPose, near: float) -> float:
	# Measured against Godot 4.7: with PROJECTION_FRUSTUM `size` is multiplied by the viewport aspect, so it is the frame
	# HEIGHT at the near plane (frame width x ref_h / ref_w); the offset stays in absolute near-plane units.
	var rg: Dictionary = NetrunArtConfigData.shipped().rig
	return frame_width(pose.lens, near) * float(rg["ref_h"]) / float(rg["ref_w"])


## `Camera3D.frustum_offset` for the pose at near plane `near`.
static func frustum_offset(pose: NetrunPose, near: float) -> Vector2:
	var w := frame_width(pose.lens, near)
	return Vector2(pose.sx * w, pose.sy * w)


## A plan point `[x, y, z]` as a Godot world position.
static func to_world(p: Array) -> Vector3:
	return Vector3(p[0], p[2], -p[1])


## The camera's global transform (position `loc`, looking along the pose direction with +Z-up plan as +Y-up world).
static func camera_transform(pose: NetrunPose) -> Transform3D:
	var d := pose.dir()
	var basis := Basis.looking_at(to_world([d[0], d[1], d[2]]), Vector3.UP)
	return Transform3D(basis, to_world(pose.loc()))


## Sets `cam` (a Camera3D) to the pose: frustum projection, size, offset, near/far and the transform.
static func apply(cam: Camera3D, pose: NetrunPose, near: float, far: float) -> void:
	cam.keep_aspect = Camera3D.KEEP_WIDTH
	cam.projection = Camera3D.PROJECTION_FRUSTUM
	cam.near = near
	cam.far = far
	cam.size = frustum_size(pose, near)
	cam.frustum_offset = frustum_offset(pose, near)
	cam.global_transform = camera_transform(pose)
