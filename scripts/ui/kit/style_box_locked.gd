class_name StyleBoxLocked
extends StyleBox
## ART_BIBLE §6 "Disabled" and §3.7: an unavailable control keeps its shape with a 1 px
## `DISABLED` outline on an opaque glass fill, and a small lock badge on its top-right
## corner (the "lock or reason": the reason goes in the tooltip). Never a faded version of
## an active colour (critique #8, the faded magenta Continue). The label colour is the
## theme's `font_disabled_color` (TEXT_MID, above 4.5:1 on this fill). The badge hangs half
## outside the corner, so it adds nothing to the control's size. Draw-only.

## Badge radius (px) and the lock drawn in it, as shares of the radius.
const BADGE_R := 7.0
const LOCK_BODY_W := 0.9
const LOCK_BODY_H := 0.7
const SHACKLE_R := 0.36
const SHACKLE_W := 1.5
const SHACKLE_SEGMENTS := 8

## Fill behind the label (opaque glass by default).
var fill: Color = Palette.TERMINAL_BG
## The outline (§3.3 DISABLED).
var edge: Color = Palette.DISABLED
## Outline width (px).
var border: float = 1.0
## Whether the lock badge shows.
var show_lock: bool = true


func _draw(to_canvas_item: RID, rect: Rect2) -> void:
	if fill.a > 0.0:
		RenderingServer.canvas_item_add_rect(to_canvas_item, rect, fill)
	if border > 0.0:
		for r in [Rect2(rect.position, Vector2(rect.size.x, border)), Rect2(Vector2(rect.position.x, rect.end.y - border), Vector2(rect.size.x, border)),
				Rect2(rect.position, Vector2(border, rect.size.y)), Rect2(Vector2(rect.end.x - border, rect.position.y), Vector2(border, rect.size.y))]:
			RenderingServer.canvas_item_add_rect(to_canvas_item, r, edge)
	if show_lock:
		draw_lock_badge(to_canvas_item, Vector2(rect.end.x, rect.position.y))


func _get_draw_rect(rect: Rect2) -> Rect2:
	return rect.grow(BADGE_R + 1.0)


## A lock in a dark badge centred on `c` (on canvas item `rid`), `r` px radius.
static func draw_lock_badge(rid: RID, c: Vector2, r: float = BADGE_R) -> void:
	RenderingServer.canvas_item_add_circle(rid, c, r + 1.0, Palette.DISABLED)
	RenderingServer.canvas_item_add_circle(rid, c, r, Palette.DESK_DARK)
	var bw := r * LOCK_BODY_W
	var bh := r * LOCK_BODY_H
	var body := Rect2(c + Vector2(-bw * 0.5, -bh * 0.15), Vector2(bw, bh))
	RenderingServer.canvas_item_add_rect(rid, body, Palette.TEXT_MID)
	var sc := Vector2(c.x, body.position.y)
	var pts := PackedVector2Array()
	for k in SHACKLE_SEGMENTS + 1:
		var a := PI + PI * float(k) / SHACKLE_SEGMENTS
		pts.append(sc + Vector2(cos(a), sin(a)) * r * SHACKLE_R)
	RenderingServer.canvas_item_add_polyline(rid, pts, PackedColorArray([Palette.TEXT_MID]), SHACKLE_W, true)
