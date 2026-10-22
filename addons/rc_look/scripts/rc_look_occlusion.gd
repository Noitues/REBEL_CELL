class_name RcLookOcclusion
extends RefCounted
## LOOK-TOOLBOX: the sight rule every framed view shares (designer 2026-10-21: "hide or flatten all obstacles between
## the camera and any part of the netrun; combat included"). An obstacle gives way when it stands nearer the eye than
## the subject's middle, is not one of the subject's own buildings, and either
##   - rises above the sight line inside the wedge from the eye to the subject's sides (the street-level rule), or
##   - its screen box overlaps the subject's screen box grown by `pad_px` (the screen rule).
## Camera-agnostic: the camera is a `project` Callable (world Vector3 -> screen px Vector2, non-finite behind the eye).
## A Callable does not keep a RefCounted camera alive: the caller holds it (e.g. in the record) while the record is used.
## This is the hard cut for stills (the combat backdrop); netrun's moving rig fades the same obstacles through its cone
## (OcclusionHelper, cut / ghost / dissolve packed in INSTANCE_CUSTOM.w). Pure.


## The screen box (px) of world box `box`'s eight corners (Rect2() when a corner is behind the eye).
static func screen_box(project: Callable, box: AABB) -> Rect2:
	var out := Rect2()
	for k in 8:
		var p: Vector2 = project.call(box.get_endpoint(k))
		if not p.is_finite():
			return Rect2()
		out = Rect2(p, Vector2.ZERO) if k == 0 else out.expand(p)
	return out


## The sight record for eye `eye` looking along `forward` at world box `subject`: `pad_bu` widens the wedge and pulls
## its depth in, `sight_share` is the subject's height share the sight line aims at, `pad_px` grows the subject's
## screen box, `half_bu` is an obstacle's half footprint for the screen rule. Read it only through `hides`.
static func sight(project: Callable, eye: Vector3, forward: Vector3, subject: AABB, pad_bu: float, sight_share: float,
		pad_px: float, half_bu: float) -> Dictionary:
	var fwd := Vector2(forward.x, forward.z).normalized()
	var right := Vector2(-fwd.y, fwd.x)
	var e2 := Vector2(eye.x, eye.z)
	var front := INF
	var lo := INF
	var hi := -INF
	for k in 8:
		var p := subject.get_endpoint(k)
		var v := Vector2(p.x, p.z) - e2
		var d := maxf(v.dot(fwd), 0.001)
		front = minf(front, d)
		lo = minf(lo, v.dot(right) / d)
		hi = maxf(hi, v.dot(right) / d)
	var mid := subject.get_center()
	return {"eye": eye, "fwd": fwd, "right": right, "front": front - pad_bu, "sub": front, "lo": lo, "hi": hi,
		"pad": pad_bu, "base_y": subject.position.y + subject.size.y * sight_share,
		"sub_xz": Rect2(Vector2(subject.position.x, subject.position.z), Vector2(subject.size.x, subject.size.z)),
		"mid": Vector2(mid.x - eye.x, mid.z - eye.z).dot(fwd), "project": project,
		"sub_rect": screen_box(project, subject).grow(pad_px), "half": half_bu}


## Whether an obstacle standing on ground point `centre` (world X/Z) with its roof at `top` hides the subject of
## sight record `s` (`sight`).
static func hides(s: Dictionary, centre: Vector2, top: float) -> bool:
	var eye: Vector3 = s["eye"]
	var v := centre - Vector2(eye.x, eye.z)
	var d := v.dot(s["fwd"])
	if d <= 0.0 or d >= float(s["mid"]):
		return false
	if (s["sub_xz"] as Rect2).has_point(centre):
		return false  # the subject's own buildings
	var side := v.dot(s["right"])
	var pad := float(s["pad"])
	var in_wedge := d < float(s["front"]) and side >= float(s["lo"]) * d - pad and side <= float(s["hi"]) * d + pad
	var line := eye.y + (float(s["base_y"]) - eye.y) * d / maxf(float(s["sub"]), 0.001)
	if in_wedge and top > line:
		return true
	var h := float(s["half"])
	var box := AABB(Vector3(centre.x - h, 0.0, centre.y - h), Vector3(h * 2.0, maxf(top, 0.01), h * 2.0))
	return screen_box(s["project"], box).intersects(s["sub_rect"])
