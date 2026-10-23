class_name L7Cam
extends RefCounted
## The Blender target camera (tools/raid_concepts/target/raid_scene.py) as a pure pinhole projection, so the 2D overlay
## (beams, glyphs, pills) lands exactly on the 3D board that L7Board draws behind it. Board space is Blender's: x right,
## y away from the camera, z up; row 0 of the lab is the far row (R1), column 0 the left one. L7Board maps it to Godot
## (x, z, -y) and aims its Camera3D with `aim_point()`, so both agree. No Node, no randomness.

const CAM_POS := Vector3(-3.0, -48.0, 56.0)
const AIM := Vector3(4.4, 3.4, 0.8)
## Column x and row y of the lab's grid (row 0 = far row R1), the target frames' spacing.
const COLS: Array = [0.0, 2.9, 5.8, 8.7]
const ROWS: Array = [7.0, 3.5, 0.0]
## 116 mm lens on a 36 mm sensor, as pixels of a 1920-wide frame.
const F_REF: float = 116.0 / 36.0 * 1920.0
## The lab draws the board at this fraction of the target frame.
const SCALE: float = 0.54
const VIEW := Vector2(1280, 720)
## Where the board's aim point lands on the 1280x720 screen (the board sits left of the side panel).
const AIM_SCREEN := Vector2(376, 308)
## Heights (board units) of the beam plane and of the chips that float over a node.
const BEAM_Z: float = 0.9
const CHIP_Z: float = 2.0
const HOME_CHIP_Z: float = 3.3
## The slab the board stands on (board units): it must fit left of the side panel and under the HUD (checked in flow_check).
const SLAB_X0: float = -3.1
const SLAB_X1: float = 11.85
const SLAB_Y0: float = -2.2
const SLAB_Y1: float = 9.2
## Entry pylons stand this far outside the end nodes (x for rows, y for columns).
const PYLON_X: Array = [-2.75, 11.45]
const PYLON_Y: float = 9.9

static var _ready_basis: bool = false
static var _f: Vector3
static var _r: Vector3
static var _u: Vector3
static var _aim: Vector3 = AIM


static func _basis_for(aim: Vector3) -> Array:
	var f: Vector3 = (aim - CAM_POS).normalized()
	var r: Vector3 = f.cross(Vector3(0, 0, 1)).normalized()
	var u: Vector3 = r.cross(f)
	return [f, r, u]


static func _setup() -> void:
	if _ready_basis:
		return
	_ready_basis = true
	# Aim the camera a little off the Blender target until AIM lands on AIM_SCREEN (a pure shift of the picture).
	var b: Array = _basis_for(AIM)
	var z0: float = (AIM - CAM_POS).dot(b[0] as Vector3)
	var a := 0.0
	var h := 0.0
	var sc: float = F_REF * SCALE
	for _i in range(6):
		var bb: Array = _basis_for(AIM + (b[1] as Vector3) * a + (b[2] as Vector3) * h)
		_f = bb[0]
		_r = bb[1]
		_u = bb[2]
		var cur: Vector2 = _proj_raw(AIM)
		a += (cur.x - AIM_SCREEN.x) / sc * z0
		h += (AIM_SCREEN.y - cur.y) / sc * z0
	_aim = AIM + (b[1] as Vector3) * a + (b[2] as Vector3) * h
	var fin: Array = _basis_for(_aim)
	_f = fin[0]
	_r = fin[1]
	_u = fin[2]


static func _proj_raw(p: Vector3) -> Vector2:
	var d: Vector3 = p - CAM_POS
	var z: float = d.dot(_f)
	return VIEW * 0.5 + Vector2(d.dot(_r), -d.dot(_u)) * (F_REF * SCALE) / z


## Board point (x, y, z) to screen pixels of the 1280x720 view.
static func project(p: Vector3) -> Vector2:
	_setup()
	return _proj_raw(p)


## Screen position of a lab cell at height z (board units).
static func cell_at(c: Vector2i, z: float) -> Vector2:
	return project(Vector3(COLS[c.x], ROWS[c.y], z))


## The beam plane over a cell: where beams, rings and the hunter's arrow sit.
static func beam_pos(c: Vector2i) -> Vector2:
	return cell_at(c, BEAM_Z)


## Where a node's chip (value, glyph, pips) floats: over the tower.
static func chip_pos(c: Vector2i, tall: bool = false) -> Vector2:
	return cell_at(c, HOME_CHIP_Z if tall else CHIP_Z)


## The point the Godot Camera3D must look at (Blender coordinates), and the horizontal field of view in degrees.
static func aim_point() -> Vector3:
	_setup()
	return _aim


static func hfov_deg() -> float:
	return rad_to_deg(2.0 * atan(VIEW.x * 0.5 / (F_REF * SCALE)))


## Blender (x, y, z) to Godot (x, z, -y).
static func to_godot(p: Vector3) -> Vector3:
	return Vector3(p.x, p.z, -p.y)
