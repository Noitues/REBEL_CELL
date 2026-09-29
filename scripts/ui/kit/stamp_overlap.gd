class_name StampOverlap
extends Container
## Art pass W8d (ART_BIBLE §6.6, §11 Campaign end): a verdict stamp slapped across the foot
## of a piece of art (the corp's billboard, the Cell's hexagon), as a layout. The first
## child (the art) sits centred at the top; the second (the stamp) is centred under it and
## overlaps its lower edge by OVERLAP of the stamp's height. The box is exactly as big as
## the two together (never clipping either). Layout only.

## The share of the stamp's height laid over the art.
const OVERLAP := 0.3


func _init() -> void:
	name = "StampOverlap"
	mouse_filter = Control.MOUSE_FILTER_IGNORE


func _pieces() -> Array[Control]:
	var out: Array[Control] = []
	for c in get_children():
		if c is Control and not (c as Control).top_level:
			out.append(c as Control)
	return out


func _get_minimum_size() -> Vector2:
	var p := _pieces()
	if p.size() < 2:
		return p[0].get_combined_minimum_size() if p.size() == 1 else Vector2.ZERO
	var a := p[0].get_combined_minimum_size()
	var s := p[1].get_combined_minimum_size()
	return Vector2(maxf(a.x, s.x), a.y + s.y * (1.0 - OVERLAP))


func _notification(what: int) -> void:
	if what == NOTIFICATION_SORT_CHILDREN:
		var p := _pieces()
		if p.is_empty():
			return
		var a := p[0].get_combined_minimum_size()
		fit_child_in_rect(p[0], Rect2(Vector2((size.x - a.x) * 0.5, 0.0), a))
		if p.size() > 1:
			var s := p[1].get_combined_minimum_size()
			fit_child_in_rect(p[1], Rect2(Vector2((size.x - s.x) * 0.5, a.y - s.y * OVERLAP), s))


## The art's and the stamp's rects (local; tests).
func art_and_stamp() -> Array[Rect2]:
	var out: Array[Rect2] = []
	for c in _pieces():
		out.append(Rect2(c.position, c.size))
	return out
