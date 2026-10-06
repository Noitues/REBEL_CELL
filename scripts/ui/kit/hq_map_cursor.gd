class_name HqMapCursor
extends Control
## HQ-B (M14, HQ redesign direction B): the pad's place on the HQ's map. It covers the map's
## free part and takes focus (no clicks: the map under it takes the mouse); focused, left /
## right step through the Sites (`stepped`, the scene selects the next one and the camera
## keeps it in view) and A presses the selected thing's verb or card (the scene's links). A
## thin lime frame round the free part says the map has the focus (§2.10: lime is focus).
## View only.

signal stepped(step: int)

## The focus frame's stroke and inset (px).
const FRAME := 2.0
const INSET := 4.0


func _init() -> void:
	focus_mode = Control.FOCUS_ALL
	mouse_filter = Control.MOUSE_FILTER_IGNORE
	focus_entered.connect(queue_redraw)
	focus_exited.connect(queue_redraw)


func _gui_input(event: InputEvent) -> void:
	if event.is_action_pressed(&"ui_left", true):
		stepped.emit(-1)
		accept_event()
	elif event.is_action_pressed(&"ui_right", true):
		stepped.emit(1)
		accept_event()


func _draw() -> void:
	if has_focus():
		draw_rect(Rect2(Vector2.ONE * INSET, size - Vector2.ONE * INSET * 2.0), Color(Palette.FOCUS, 0.6), false, FRAME)
