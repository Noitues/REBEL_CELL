class_name PencilPlan
extends Control
## ART-10 4C: the grease-pencil plan beside the title's three verb stickers (ART_BIBLE v2
## §1.2 "Grease pencil", §4.13 title option A "the plan"; round 33 `title_screen.jpg`): a
## yellow wax stroke down the left and a number before each sticker ("1." "2." "3."), in
## Permanent Marker with a dark under-shadow so it reads day and night. Plans only: no
## live numbers, no body text. It reads the rows' centres from `rows` (the stickers'
## column) each frame it draws. View only.

## Wax alpha and the under-shadow offset (px) (§1.2: opaque wax 0.96, a dark under-shadow).
const WAX_ALPHA := 0.96
const SHADOW := Vector2(2, 2)
## Stroke width (px) and the number lettering step.
const STROKE := 4.0
const NUMBER_STEP := UiTheme.HEADING
## The column's width (px at text scale 1.0).
const WIDTH := 46.0

## The column whose children the numbers stand beside.
var rows: Control = null


func _init(p_rows: Control = null) -> void:
	rows = p_rows
	name = "PencilPlan"
	mouse_filter = Control.MOUSE_FILTER_IGNORE
	custom_minimum_size = Vector2(WIDTH, 0)
	auto_translate_mode = Node.AUTO_TRANSLATE_MODE_DISABLED


func _process(_delta: float) -> void:
	queue_redraw()


## Draws `text` as wax at `at` (baseline) with its under-shadow.
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
	if rows == null or not is_instance_valid(rows) or rows.get_child_count() == 0:
		return
	var inv := get_global_transform().affine_inverse()
	var px := Chrome.px(NUMBER_STEP)
	var top := INF
	var bottom := -INF
	var n := 0
	for c in rows.get_children():
		if not (c is Control) or not (c as Control).visible:
			continue
		n += 1
		var g := (c as Control).get_global_rect()
		var y := (inv * g.get_center()).y
		top = minf(top, (inv * g.position).y)
		bottom = maxf(bottom, (inv * g.end).y)
		wax_text(self, Vector2(STROKE * 2.5, y + px * 0.35), "%d." % n, px)
	if n > 0:
		wax_line(self, PackedVector2Array([Vector2(STROKE, top - 6.0), Vector2(STROKE + 1.5, (top + bottom) * 0.5), Vector2(STROKE - 1.0, bottom + 18.0)]))
