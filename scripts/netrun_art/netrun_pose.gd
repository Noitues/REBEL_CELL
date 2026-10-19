class_name NetrunPose
extends RefCounted
## NA-21 twin of `rig.Pose`: a camera pose `(F, yaw, pitch, dist, lens, sx, sy)` in the rig convention.
## `yaw` 0 looks along +y (north), positive turns clockwise seen from above (toward +x);
## `dir = (sin yaw cos pitch, cos yaw cos pitch, -sin pitch)`; the camera is at `F - dist * dir`; pitch is positive looking
## down. `sx` / `sy` are the lens shift as fractions of the frame width (36 mm sensor, 1920 x 1080 reference frame).
## Points are plain float Arrays (64-bit). Reads its frame constants from NetrunArtConfigData.rig.

## The focus point `[x, y, z]`.
var F: Array = [0.0, 0.0, 0.0]
var yaw: float = 0.0
var pitch: float = 0.0
var dist: float = 0.0
var lens: float = 0.0
var sx: float = 0.0
var sy: float = 0.0


## A pose from its parts (the focus is copied).
static func make(focus: Array, yaw_deg: float, pitch_deg: float, dist_bu: float, lens_mm: float, shift_x: float = 0.0,
		shift_y: float = 0.0) -> NetrunPose:
	var p := NetrunPose.new()
	p.F = [float(focus[0]), float(focus[1]), float(focus[2])]
	p.yaw = yaw_deg
	p.pitch = pitch_deg
	p.dist = dist_bu
	p.lens = lens_mm
	p.sx = shift_x
	p.sy = shift_y
	return p


## Unit view direction.
func dir() -> Array:
	var y := deg_to_rad(yaw)
	var p := deg_to_rad(pitch)
	return [sin(y) * cos(p), cos(y) * cos(p), -sin(p)]


## Camera position.
func loc() -> Array:
	var d := dir()
	return [F[0] - d[0] * dist, F[1] - d[1] * dist, F[2] - d[2] * dist]


## Pixel `[x, y]` of world point `P` in the 1920 x 1080 reference frame, or an empty Array behind the camera.
func proj(P: Array, shift: bool = true) -> Array:
	var rg: Dictionary = NetrunArtConfigData.shipped().rig
	var sensor: float = rg["sensor_mm"]
	var ref_w: float = rg["ref_w"]
	var ref_h: float = rg["ref_h"]
	var f := dir()
	var r := NetrunArtUnits.norm3(NetrunArtUnits.cross3(f, [0.0, 0.0, 1.0]))
	var u := NetrunArtUnits.cross3(r, f)
	var l := loc()
	var d := [P[0] - l[0], P[1] - l[1], P[2] - l[2]]
	var z := NetrunArtUnits.dot3(d, f)
	if z <= NetrunArtUnits.NEAR_Z:
		return []
	var k := lens / sensor
	var nx := k * NetrunArtUnits.dot3(d, r) / z
	var ny := k * NetrunArtUnits.dot3(d, u) / z
	var ssx := sx if shift else 0.0
	var ssy := sy if shift else 0.0
	return [ref_w / 2 + (nx - ssx) * ref_w, ref_h / 2 - (ny - ssy) * ref_w]


## `{loc, tgt, lens, shift_x, shift_y, yaw, pitch, dist}` (the v2 pose shape).
func to_json() -> Dictionary:
	return {"loc": loc(), "tgt": F.duplicate(), "lens": lens, "shift_x": sx, "shift_y": sy, "yaw": yaw, "pitch": pitch,
		"dist": dist}


## Pose from the v2 shape.
static func from_json(js: Dictionary) -> NetrunPose:
	return NetrunPose.make(js["tgt"], js["yaw"], js["pitch"], js["dist"], js["lens"], js["shift_x"], js["shift_y"])


## Interpolate toward `o`: F, yaw, pitch, lens, shift linear; dist in log space.
func mix(o: NetrunPose, t: float) -> NetrunPose:
	var focus: Array = []
	for i in 3:
		focus.append(NetrunArtUnits.lerp_f(F[i], o.F[i], t))
	return NetrunPose.make(focus, NetrunArtUnits.lerp_f(yaw, o.yaw, t), NetrunArtUnits.lerp_f(pitch, o.pitch, t),
		exp(NetrunArtUnits.lerp_f(log(dist), log(o.dist), t)), NetrunArtUnits.lerp_f(lens, o.lens, t),
		NetrunArtUnits.lerp_f(sx, o.sx, t), NetrunArtUnits.lerp_f(sy, o.sy, t))
