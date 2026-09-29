class_name StyleBoxBrackets
extends StyleBox
## ART_BIBLE §6 "Focus (pad/keys)": `FOCUS` 4-corner brackets, 2 px thick, 4 px outside the
## control, visible from 3 m on a TV. The theme's "focus" stylebox for every focusable kind
## (UiTheme), replacing the old 2 px acid ring. A thin `INK` keyline sits under each arm so
## the acid reads on paper stock and over the bright city alike (§3.7: an icon carrying
## meaning needs 3:1 against its background). Draws outside the rect only: it never adds
## to a control's minimum size (no content margins) and never reflows layout.
## `draw_on` paints the same brackets from a control's own draw pass (drawn stickers, the
## kit components). Draw-only.

## §6: bracket thickness and offset outside the control (px, reference 1280x720).
const THICKNESS := 2.0
const OFFSET := 4.0
## Arm length: this share of the shorter side of the bracketed box, held between ARM_MIN and
## ARM_MAX px (short enough to read as four marks, long enough to see at TV distance).
const ARM_SHARE := 0.3
const ARM_MIN := 8.0
const ARM_MAX := 18.0
## The dark keyline under the brackets (px each side).
const KEYLINE := 1.0

## Bracket colour (the §3.3 FOCUS token; a drop-target highlight may pass another role).
var color: Color = Palette.FOCUS
## Distance outside the rect (px).
var offset: float = OFFSET
## Stroke width (px).
var thickness: float = THICKNESS


func _init(p_color: Color = Palette.FOCUS, p_offset: float = OFFSET, p_thickness: float = THICKNESS) -> void:
	color = p_color
	offset = p_offset
	thickness = p_thickness


func _draw(to_canvas_item: RID, rect: Rect2) -> void:
	draw_rid(to_canvas_item, rect.grow(offset), color, thickness)


func _get_draw_rect(rect: Rect2) -> Rect2:
	return rect.grow(offset + thickness + KEYLINE)


func _get_minimum_size() -> Vector2:
	return Vector2.ZERO


## The arm length (px) for brackets round `box`.
static func arm_for(box: Rect2) -> float:
	return clampf(minf(box.size.x, box.size.y) * ARM_SHARE, ARM_MIN, ARM_MAX)


## The eight arm rects (2 per corner) of brackets round `box` at stroke `w`: the brackets'
## own geometry, pure (tests).
static func arm_rects(box: Rect2, w: float = THICKNESS) -> Array[Rect2]:
	var arm := minf(arm_for(box), minf(box.size.x, box.size.y) * 0.5)
	var p := box.position
	var e := box.end
	return [
		Rect2(p, Vector2(arm, w)), Rect2(p, Vector2(w, arm)),
		Rect2(Vector2(e.x - arm, p.y), Vector2(arm, w)), Rect2(Vector2(e.x - w, p.y), Vector2(w, arm)),
		Rect2(Vector2(p.x, e.y - w), Vector2(arm, w)), Rect2(Vector2(p.x, e.y - arm), Vector2(w, arm)),
		Rect2(Vector2(e.x - arm, e.y - w), Vector2(arm, w)), Rect2(Vector2(e.x - w, e.y - arm), Vector2(w, arm)),
	]


## Paints brackets round `box` (already offset) on canvas item `rid`.
static func draw_rid(rid: RID, box: Rect2, col: Color = Palette.FOCUS, w: float = THICKNESS) -> void:
	var arms := arm_rects(box, w)
	for r in arms:
		RenderingServer.canvas_item_add_rect(rid, r.grow(KEYLINE), Color(Palette.INK, col.a))
	for r in arms:
		RenderingServer.canvas_item_add_rect(rid, r, col)


## Paints the focus brackets round `rect` (local to `ci`, the control's own rect) from a
## draw pass, OFFSET outside it.
static func draw_on(ci: CanvasItem, rect: Rect2, col: Color = Palette.FOCUS) -> void:
	draw_rid(ci.get_canvas_item(), rect.grow(OFFSET), col, THICKNESS)
