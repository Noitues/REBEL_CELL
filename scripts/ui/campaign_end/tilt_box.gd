class_name TiltBox
extends Container
## ART-11 4D: holds one piece tilted inside a container layout (a print, a sheet, a sticker on
## the glass). A Container resets its children's rotation when it lays them out, so the tilt
## is set here after the fit, about the piece's centre. Look only.

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


func _get_minimum_size() -> Vector2:
	var m := Vector2.ZERO
	for c in get_children():
		if c is Control and (c as Control).visible:
			m = m.max((c as Control).get_combined_minimum_size())
	return m


func _notification(what: int) -> void:
	if what == NOTIFICATION_SORT_CHILDREN:
		for c in get_children():
			if c is Control:
				var ctl := c as Control
				fit_child_in_rect(ctl, Rect2(Vector2.ZERO, size))
				ctl.pivot_offset = ctl.size * 0.5
				ctl.rotation_degrees = tilt
