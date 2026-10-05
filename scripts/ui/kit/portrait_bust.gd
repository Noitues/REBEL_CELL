class_name PortraitBust
extends RefCounted
## ART-9 4B (ART_BIBLE v2 §4.12): the operatives' pre-rendered low-poly cel busts. One atlas
## per class (`assets/portraits/busts_<class>.png`, written by
## tools/art_gen/portraits/render_busts.py from the round 39 bust rig): columns are the
## frames (Frame), rows the rookie variants (VARIANTS seeds of the class's gear). The corp's
## photo print of each variant is `prints_<class>.jpg` (one column). Which variant an
## operative wears is a hash of its class and id (never game RNG), so an operative keeps one
## face on every screen and in every session. View only.

## The frames of one rookie (atlas columns): eyes open, eyes shut (the blink and the
## flatlined "dead eyes"), mouth open (talking), grimace + squint (hurt).
enum Frame { IDLE, BLINK, TALK, HURT }
## Rookie variants per class (atlas rows; render_busts.py SEEDS).
const VARIANTS := 4
const FRAMES := 4
## One atlas cell (px; render_busts.py CELL). Its aspect is the bust's.
const CELL := Vector2i(240, 266)
const SHEET_PATH := "res://assets/portraits/busts_%s.png"
const PRINT_PATH := "res://assets/portraits/prints_%s.jpg"

static var _sheets: Dictionary = {}
static var _prints: Dictionary = {}
static var _atlases: Dictionary = {}


## True when `class_id` has a bust set.
static func has_class(class_id: StringName) -> bool:
	return sheet(class_id) != null


## The class's atlas (null for a class with no bust set).
static func sheet(class_id: StringName) -> Texture2D:
	if not _sheets.has(class_id):
		var path := SHEET_PATH % class_id
		_sheets[class_id] = load(path) as Texture2D if class_id != &"" and ResourceLoader.exists(path) else null
	return _sheets[class_id]


## The class's print sheet (null for a class with no bust set).
static func print_sheet(class_id: StringName) -> Texture2D:
	if not _prints.has(class_id):
		var path := PRINT_PATH % class_id
		_prints[class_id] = load(path) as Texture2D if class_id != &"" and ResourceLoader.exists(path) else null
	return _prints[class_id]


## The rookie variant `operative_id` wears (0..VARIANTS-1): a hash of class and id, so it is
## the same on every screen and run; an empty id (a class's own face, an unhired rookie) is 0.
static func variant_for(class_id: StringName, operative_id: StringName) -> int:
	if operative_id == &"":
		return 0
	return posmod(hash("%s/%s" % [class_id, operative_id]), VARIANTS)


## The atlas cell of `variant` / `frame` (px).
static func region(variant: int, frame: int) -> Rect2:
	return Rect2(Vector2(clampi(frame, 0, FRAMES - 1) * CELL.x, clampi(variant, 0, VARIANTS - 1) * CELL.y), Vector2(CELL))


## The cell as uv (x, y, w, h) of the class's atlas (the feed shader's `bust_uv`).
static func uv_rect(class_id: StringName, variant: int, frame: int) -> Rect2:
	var tex := sheet(class_id)
	if tex == null:
		return Rect2(0, 0, 1, 1)
	var r := region(variant, frame)
	var s := Vector2(tex.get_size())
	return Rect2(r.position / s, r.size / s)


## One frame of one variant (an AtlasTexture of the class's atlas; null without a set).
static func texture(class_id: StringName, variant: int, frame: int) -> Texture2D:
	var key := [class_id, variant, frame, false]
	if not _atlases.has(key):
		var tex := sheet(class_id)
		var at: AtlasTexture = null
		if tex != null:
			at = AtlasTexture.new()
			at.atlas = tex
			at.region = region(variant, frame)
		_atlases[key] = at
	return _atlases[key]


## The corp's photo print of one variant (an AtlasTexture of the print sheet; null without).
static func print_texture(class_id: StringName, variant: int) -> Texture2D:
	var key := [class_id, variant, 0, true]
	if not _atlases.has(key):
		var tex := print_sheet(class_id)
		var at: AtlasTexture = null
		if tex != null:
			at = AtlasTexture.new()
			at.atlas = tex
			at.region = Rect2(Vector2(0, clampi(variant, 0, VARIANTS - 1) * CELL.y), Vector2(CELL))
		_atlases[key] = at
	return _atlases[key]


## The part of a cell that fills a square picture: the head and the top of the shoulders
## (the cell is taller than wide; its top is the head room).
static func square_region(cell: Rect2) -> Rect2:
	return Rect2(cell.position, Vector2(cell.size.x, cell.size.x))
