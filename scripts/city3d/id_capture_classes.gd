class_name IdCaptureClasses
extends RefCounted
## NA-ID: the class table of the 12.0 id capture (PIPELINE_SPEC 12.0; docs/handoff/plan2/drafts/NA_ID_CLASSES.md).
## R of an id.png pixel is the class; G and B carry the room's place in the run graph and its layer on class 5 and on the walls of
## route columns (NA02_FIELDS "id.png encoding"). Pure constants and byte helpers.

const SKY := 0
const LANDMARK := 1
const CITY := 2
const LINK := 3
const ROOM := 5
const MOVER := 6
## NA-ID-b: class 4 is the ground: the ground meshes, and the parts of a landmark compound that lie on it (plaza carpet, apron trims,
## rails at grade). A hidden ground would read as class 0 and join the {0, 2} background mask of the 12.2 / R-FOCUS-1 checks.
const GROUND := 4
const CLASSES: Array[int] = [SKY, LANDMARK, CITY, LINK, GROUND, ROOM, MOVER]

## Scene groups a builder sets on a node (and, for a mover or a link, on any mesh under it): the id pass paints every mesh of a
## tagged node with that class. Landmark compounds need no group (everything under the `landmarks` layer is class 1).
const GROUP_LINK := &"id_link"
const GROUP_MOVER := &"id_mover"
## A builder sets this on any node whose meshes lie on the ground (the whole mesh is then class 4, even under the landmarks layer).
const GROUP_GROUND := &"id_ground"
## The glb compounds and landmarks carry a root-level node of this name (tools/art_pipeline/city/id_ground.py, one material slot per
## role) holding every part that lies on the ground (plaza carpet, aprons, rails, moat water, shaft floor): the whole node is class 4.
const GROUND_NODE_NAME := "id_ground"
## The `stub` byte of an occluded building (class 2, G = STUB_G, B = 0).
const STUB_G := 255
## The `capture.json` float precision.
const JSON_STEP := 0.0001


## The three bytes (R, G, B) of an id pixel; each clamped to 0..255.
static func bytes(cls: int, g: int = 0, b: int = 0) -> Vector3i:
	return Vector3i(clampi(cls, 0, 255), clampi(g, 0, 255), clampi(b, 0, 255))


## The room column / room colour of a run-graph room: class 5, G = its 1-based place in the run graph, B = its layer.
static func room_bytes(place_1based: int, layer: int) -> Vector3i:
	return bytes(ROOM, place_1based, layer)


## True when `cls` is a class Godot writes (0, 1, 2, 3, 4, 5, 6).
static func is_written(cls: int) -> bool:
	return CLASSES.has(cls)


## The pixel count of every class of `img` (id.png, any 8-bit format): {class byte: count}.
static func count_classes(img: Image) -> Dictionary:
	var rgb := img.duplicate() as Image
	rgb.convert(Image.FORMAT_RGB8)
	var data := rgb.get_data()
	var out: Dictionary = {}
	var i := 0
	while i < data.size():
		var c := int(data[i])
		out[c] = int(out.get(c, 0)) + 1
		i += 3
	return out


## True when every pixel of `img` has an R in the written set.
static func only_written_classes(img: Image) -> bool:
	for c: int in count_classes(img):
		if not is_written(c):
			return false
	return true


## `v` with every float rounded to JSON_STEP and every Dictionary left for JSON.stringify to sort (canonical capture.json).
static func canonical(v: Variant) -> Variant:
	match typeof(v):
		TYPE_FLOAT:
			return snappedf(float(v), JSON_STEP)
		TYPE_DICTIONARY:
			var d: Dictionary = {}
			for k: Variant in (v as Dictionary):
				d[k] = canonical((v as Dictionary)[k])
			return d
		TYPE_ARRAY:
			var a: Array = []
			for e: Variant in (v as Array):
				a.append(canonical(e))
			return a
		TYPE_VECTOR3:
			var p := v as Vector3
			return [snappedf(p.x, JSON_STEP), snappedf(p.y, JSON_STEP), snappedf(p.z, JSON_STEP)]
	return v


## The canonical capture.json text: sorted keys, floats rounded to JSON_STEP, one-space indent, LF line ends.
static func capture_json(cap: Dictionary) -> String:
	return JSON.stringify(canonical(cap), " ", true)
