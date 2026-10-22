class_name RcPencilAnchor
extends RefCounted
## LOOK-TOOLBOX 12: the one seam from the 3D world to grease pencil on screen (AUDIT: "no world-space anchor API; world
## anchoring done per view"). A projector is a Camera3D (its own unproject) or a Callable (Vector3) -> Vector2 for a
## view with its own projection (the netrun's NetrunPose.proj); either way a point behind the camera comes back as
## Vector2.INF. Points come out in viewport px; `to_canvas` maps them into a CanvasItem's local px (the pencil layer a
## view draws on). Pure: no state, no scene changes.


## World point `p` on screen (viewport px) through `projector`; INF when behind the camera or unprojectable.
static func screen_point(projector: Variant, p: Vector3) -> Vector2:
	if projector is Camera3D:
		var cam := projector as Camera3D
		if not is_instance_valid(cam) or cam.is_position_behind(p):
			return Vector2.INF
		return cam.unproject_position(p)
	if projector is Callable and (projector as Callable).is_valid():
		var v: Variant = (projector as Callable).call(p)
		if v is Vector2 and (v as Vector2).is_finite():
			return v
	return Vector2.INF


## A world polyline on screen; a point behind the camera breaks it, so the result is the visible runs (each 2+ points).
static func screen_path(projector: Variant, pts: PackedVector3Array) -> Array[PackedVector2Array]:
	var out: Array[PackedVector2Array] = []
	var run := PackedVector2Array()
	for p in pts:
		var s := screen_point(projector, p)
		if s.is_finite():
			run.append(s)
		else:
			if run.size() >= 2:
				out.append(run)
			run = PackedVector2Array()
	if run.size() >= 2:
		out.append(run)
	return out


## Screen px per world unit at `p` (a ring sized in metres stays the size of the thing it circles); 0 when behind.
static func px_per_unit(projector: Variant, p: Vector3, axis: Vector3 = Vector3.RIGHT) -> float:
	var a := screen_point(projector, p)
	var b := screen_point(projector, p + axis.normalized())
	if not a.is_finite() or not b.is_finite():
		return 0.0
	return a.distance_to(b)


## Viewport px `s` in `ci`'s local px (INF stays INF).
static func to_canvas(ci: CanvasItem, s: Vector2) -> Vector2:
	if not s.is_finite():
		return Vector2.INF
	return ci.get_global_transform_with_canvas().affine_inverse() * s
