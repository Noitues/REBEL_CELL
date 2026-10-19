class_name NetrunInstancePack
extends RefCounted
## NA-22: the per-instance occlusion state of a city building, packed into `INSTANCE_CUSTOM.w` of the `city_building`
## MultiMesh (x = taper, y = trim ink slot, z = seed stay as they were). `w = crest + 2 * bits`, where `bits` is an integer
## below 2^23, so the float is exact (a float32 holds integers to 2^24). All four fields are stored so that 0 means "nothing
## happens": a building that was never touched keeps the old `w` (0 or the crest flag) and draws as before.
##
## bits (low to high): cut 9, opacity 5, edge 3, dissolve 5, route 1 = 23 bits (NA-23 added `route`; still below 2^23 + 1).
##   cut      0..511  share of the building's height removed from the top (`cut_h = h * (1 - code / 511)`); 0 = no cut
##   ghost    0..16   `16 - round(opacity * 16)`: Bayer 4 x 4 coverage 16 - code of 16 pixels; 0 = opaque
##   edge     0..7    ghost edge-line strength `code / 7`; 0 = no edge lines
##   dissolve 0..16   route-wall dissolve share (a second Bayer order); 0 = solid
## The shader (`shaders/city/city_building.gdshader`) decodes with the same shifts; the render test checks both.

const CUT_BITS := 9
const GHOST_BITS := 5
const EDGE_BITS := 3
const DISSOLVE_BITS := 5
const CUT_MAX := 511
const GHOST_LEVELS := 16
const EDGE_MAX := 7
const DISSOLVE_LEVELS := 16
const GHOST_SHIFT := CUT_BITS
const EDGE_SHIFT := CUT_BITS + GHOST_BITS
const DISSOLVE_SHIFT := CUT_BITS + GHOST_BITS + EDGE_BITS
const ROUTE_SHIFT := CUT_BITS + GHOST_BITS + EDGE_BITS + DISSOLVE_BITS


## The `w` value for a building of height `top` (BU) cut at `cut_height` (BU above its base; >= top = no cut) drawn at
## `opacity` (0..1; 1 = opaque) with `edge` (0..1) ghost edge lines and `dissolve` (0..1) route-wall dissolve. `crest`
## keeps the red-window flag the old `w` carried; `route` marks a route building (NA-23: the shader cuts the room windows
## out of its walls).
static func pack(top: float, cut_height: float, opacity: float, edge: float, dissolve: float, crest: bool = false, route: bool = false) -> float:
	var cut_code: int = 0
	if top > 0.0 and cut_height < top:
		cut_code = clampi(roundi((1.0 - maxf(cut_height, 0.0) / top) * float(CUT_MAX)), 0, CUT_MAX)
	var ghost_code: int = clampi(GHOST_LEVELS - roundi(clampf(opacity, 0.0, 1.0) * float(GHOST_LEVELS)), 0, GHOST_LEVELS)
	var edge_code: int = clampi(roundi(clampf(edge, 0.0, 1.0) * float(EDGE_MAX)), 0, EDGE_MAX)
	var dis_code: int = clampi(roundi(clampf(dissolve, 0.0, 1.0) * float(DISSOLVE_LEVELS)), 0, DISSOLVE_LEVELS)
	var bits: int = cut_code | (ghost_code << GHOST_SHIFT) | (edge_code << EDGE_SHIFT) | (dis_code << DISSOLVE_SHIFT)
	if route:
		bits |= 1 << ROUTE_SHIFT
	return float(bits * 2 + (1 if crest else 0))


## The fields of a `w` value: `crest` (bool), `cut_frac` (share of the height removed, 0..1), `opacity`, `edge`, `dissolve`.
static func unpack(w: float) -> Dictionary:
	var iw: int = roundi(w)
	var bits: int = iw >> 1
	return {
		"crest": (iw & 1) == 1,
		"cut_frac": float(bits & CUT_MAX) / float(CUT_MAX),
		"opacity": 1.0 - float((bits >> GHOST_SHIFT) & 31) / float(GHOST_LEVELS),
		"edge": float((bits >> EDGE_SHIFT) & 7) / float(EDGE_MAX),
		"dissolve": float((bits >> DISSOLVE_SHIFT) & 31) / float(DISSOLVE_LEVELS),
		"route": ((bits >> ROUTE_SHIFT) & 1) == 1,
	}


## True when the packed state changes how the building draws (a cut, a ghost or a dissolve): the id pass writes class 2
## with G = 255, B = 0 for these (PIPELINE_SPEC 12.0).
static func is_occluded(w: float) -> bool:
	var bits: int = roundi(w) >> 1
	return (bits & CUT_MAX) != 0 or ((bits >> GHOST_SHIFT) & 31) != 0 or ((bits >> DISSOLVE_SHIFT) & 31) != 0


## The 4 x 4 Bayer threshold at pixel (x, y) in (0, 1), the ghost and dissolve pattern the shader uses (spec 7.4 rule 5).
static func bayer4(x: int, y: int) -> float:
	var m: Array[int] = [0, 8, 2, 10, 12, 4, 14, 6, 3, 11, 1, 9, 15, 7, 13, 5]
	return (float(m[(y & 3) * 4 + (x & 3)]) + 0.5) / 16.0


## Share of pixels a ghost of `opacity` draws (the Bayer coverage after quantizing to 16 levels).
static func coverage(opacity: float) -> float:
	return float(roundi(clampf(opacity, 0.0, 1.0) * float(GHOST_LEVELS))) / float(GHOST_LEVELS)
