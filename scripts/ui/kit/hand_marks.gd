class_name HandMarks
extends RefCounted
## Hand-drawn selection marks: a scrawled X (remove) and a loose loop (upgrade). LOOK-TOOLBOX 12
## (AUDIT: "hand_marks draws raw lines"): the marks are grease pencil on the one wax engine; this
## class only gives their strokes (PencilShapes' hand, seeded: never game RNG) and lays them
## with PencilSet.show_on, so a remove is red (THREAT: a loss) and an upgrade yellow (PLAN), with
## the wax's pressure, under-shadow and write-on. The pink drip-marker drawing is gone (wax
## never drips). View only.

## The X's inset (share of the rect) and how far each arm runs past its corner (widths).
const X_INSET := 0.12
const X_OVERSHOOT := 0.8


## The X over `r`: two strokes in writing order (top-left down, then top-right down), each a
## hand line with its overshoot.
static func x_strokes(r: Rect2, seed: int) -> Array[PackedVector2Array]:
	var inset := r.size * X_INSET
	var w := GreasePencilMark.stroke_width()
	var a := r.position + inset
	var b := r.end - inset
	var c := Vector2(r.end.x - inset.x, r.position.y + inset.y)
	var d := Vector2(r.position.x + inset.x, r.end.y - inset.y)
	var out: Array[PackedVector2Array] = []
	for arm: Array in [[a, b], [c, d]]:
		var from: Vector2 = arm[0]
		var to: Vector2 = arm[1]
		var dir := (to - from).normalized()
		out.append(PencilShapes.hand_path(PackedVector2Array([from - dir * w * X_OVERSHOOT, to + dir * w * X_OVERSHOOT]), seed + out.size(), w))
	return out


## A loose loop round `c` (radii `r`): one hand loop with its overlap and tail.
static func loop_strokes(c: Vector2, r: Vector2, seed: int) -> Array[PackedVector2Array]:
	return [PencilShapes.hand_circle(c, r, seed)] as Array[PackedVector2Array]


## Shows the X over `r` on `host` (a view that draws in `_draw`), in threat red.
static func show_x(host: CanvasItem, r: Rect2, seed: int) -> void:
	PencilSet.show_on(host, x_strokes(r, seed), GreasePencilMark.Ink.THREAT, seed)


## Shows the loop round `c` on `host`, in plan yellow.
static func show_loop(host: CanvasItem, c: Vector2, r: Vector2, seed: int) -> void:
	PencilSet.show_on(host, loop_strokes(c, r, seed), GreasePencilMark.Ink.PLAN, seed)


## Clears `host`'s hand mark (it wipes off).
static func clear(host: CanvasItem) -> void:
	PencilSet.show_on(host, [], GreasePencilMark.Ink.PLAN)
