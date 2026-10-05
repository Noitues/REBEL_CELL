class_name TiltBox
extends Container
## ART-11 4D: holds one piece tilted inside a container layout (a print, a sheet, a sticker on
## the glass). A Container resets its children's rotation when it lays them out, so the tilt
## is set here after the fit, about the piece's centre. A VinylSticker (1B) is held by its body:
## its art carries a shadow pad round the body, which takes no room in the layout. Look only.

## The tilt (degrees).
var tilt: float = 0.0:
	set(v):
		tilt = v
		queue_sort()


func _init(p_tilt: float = 0.0, child: Control = null) -> void:
	tilt = p_tilt
	mouse_filter = Control.MOUSE_FILTER_IGNORE
	if child != null:
		add_child(child)
		child.resized.connect(update_minimum_size)


## The room a child takes: a sticker's body, any other piece's minimum size.
static func room_of(c: Control) -> Rect2:
	if c is VinylSticker:
		return (c as VinylSticker).body_rect
	return Rect2(Vector2.ZERO, c.get_combined_minimum_size())


func _get_minimum_size() -> Vector2:
	var m := Vector2.ZERO
	for c in get_children():
		if c is Control and (c as Control).visible:
			m = m.max(room_of(c as Control).size)
	return m


func _notification(what: int) -> void:
	if what == NOTIFICATION_SORT_CHILDREN:
		for c in get_children():
			if c is VinylSticker:
				var v := c as VinylSticker
				v.position = (size - v.body_rect.size) * 0.5 - v.body_rect.position
				if not is_equal_approx(v.tilt_deg, tilt):
					v.tilt_deg = tilt  # its slap settles at this tilt too
			elif c is Control:
				var ctl := c as Control
				fit_child_in_rect(ctl, Rect2(Vector2.ZERO, size))
				ctl.pivot_offset = ctl.size * 0.5
				ctl.rotation_degrees = tilt
