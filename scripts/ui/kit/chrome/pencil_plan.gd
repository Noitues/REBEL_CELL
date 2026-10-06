class_name PencilPlan
extends Control
## ART-10 4C: the grease-pencil plan beside the title's three verb stickers (ART_BIBLE v2
## §1.2 "Grease pencil", §4.13 title option A "the plan"; round 33 `title_screen.jpg`). The art
## is the concept's own (round 33 title.py `static_ui`: the numbers 1. 2. 3. and the plan
## bracket in `ui31.Pencil`, baked by tools/art/bake_menus_r33.py into
## `assets/ui/menus/pencil/plan.png`); the verb rows keep its 112 px board pitch
## (`row_pitch`) so each number sits on its row. `wax_text` / `wax_line` remain for pencil
## words the concept never drew (the HQ's new-campaign motto). View only.

const ART := "res://assets/ui/menus/pencil/plan.png"
const META := "res://assets/ui/menus/pencil/meta.json"
## The concept board (1920 wide) to the game's 1280.
const BOARD_TO_GAME := 2.0 / 3.0
## Wax alpha and the under-shadow offset (px) (§1.2: opaque wax 0.96, a dark under-shadow).
const WAX_ALPHA := 0.96
const SHADOW := Vector2(2, 2)
## Stroke width (px).
const STROKE := 4.0

static var _meta: Dictionary = {}

## The column whose rows the numbers stand beside (kept for the layout's reference).
var rows: Control = null
var _tex: Texture2D = null


static func meta() -> Dictionary:
	if _meta.is_empty():
		var f := FileAccess.open(META, FileAccess.READ)
		if f != null:
			_meta = JSON.parse_string(f.get_as_text())
	return _meta


## The art's scale with the text (stickers and the plan scale as whole objects, up to
## VerbSticker.SCALE_MAX).
static func art_scale() -> float:
	return BOARD_TO_GAME * clampf(Settings.text_scale, 1.0, VerbSticker.SCALE_MAX)


## The verb rows' pitch (px): the concept's 112 board px, scaled.
static func row_pitch() -> float:
	return float(meta().get("row_pitch", 112)) * art_scale()


func _init(p_rows: Control = null) -> void:
	rows = p_rows
	name = "PencilPlan"
	mouse_filter = Control.MOUSE_FILTER_IGNORE
	auto_translate_mode = Node.AUTO_TRANSLATE_MODE_DISABLED
	_tex = load(ART) as Texture2D
	custom_minimum_size = Vector2(_tex.get_size().x * art_scale(), 0.0) if _tex != null else Vector2.ZERO


## Draws `text` as wax at `at` (baseline) with its under-shadow (pencil words with no concept
## art).
static func wax_text(ci: CanvasItem, at: Vector2, text: String, px: int, color: Color = Palette.PENCIL_PLAN) -> void:
	var f := Chrome.pencil_font()
	ci.draw_string(f, at + SHADOW, text, HORIZONTAL_ALIGNMENT_LEFT, -1, px, Palette.PENCIL_SHADOW)
	ci.draw_string(f, at, text, HORIZONTAL_ALIGNMENT_LEFT, -1, px, Color(color, WAX_ALPHA))


## Draws a wax stroke along `pts` with its under-shadow.
static func wax_line(ci: CanvasItem, pts: PackedVector2Array, width: float = STROKE, color: Color = Palette.PENCIL_PLAN) -> void:
	var shadow := PackedVector2Array()
	for p in pts:
		shadow.append(p + SHADOW)
	ci.draw_polyline(shadow, Palette.PENCIL_SHADOW, width, true)
	ci.draw_polyline(pts, Color(color, WAX_ALPHA), width, true)


func _draw() -> void:
	if _tex == null:
		return
	# The plan art's first number sits on the first row's centre (the concept's row_y[0]).
	var box: Array = meta().get("plan_box", [0, 300, 0, 0])
	var row_y: Array = meta().get("row_y", [392])
	var k := art_scale()
	var y := row_pitch() * 0.5 - (float(row_y[0]) - float(box[1])) * k
	draw_texture_rect(_tex, Rect2(Vector2(0, y), _tex.get_size() * k), false)
