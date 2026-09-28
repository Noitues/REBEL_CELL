class_name MotionSkip
extends RefCounted
## The one input rule for motion (ANIM-R1, STYLE_GUIDE 5.1): which presses complete a
## motion, and what happens to such a press.
##
## - **A press** (`is_press`): a key going down (not an auto-repeat echo), mouse button 1-3
##   going down (left, right, middle; the wheel's buttons are scrolling, not presses) or a
##   pad button going down. Motion, drags and joystick axes are never presses.
## - **The consume rule**: a press that completes a motion is consumed and does nothing
##   else. The helper ends its motion (the end state shows at once) and marks the event
##   handled, so no control, page or scene behind it sees the press (a B that ends a
##   viewer's landing never also leaves the Modem; a click that ends SEND IT's replay never
##   ends a second turn). A press when no motion plays is untouched.
##
## Every helper that ends its motion on a press uses this: the combat replay skip, DropLayer,
## FlightFx, MenuMotion, Typing, the Dialogue subtitles, PageTransition and the netrun's
## route travel. View only.


## True when `event` is a press that completes a motion (see the class notes).
static func is_press(event: InputEvent) -> bool:
	if event == null or not event.is_pressed() or event.is_echo():
		return false
	if event is InputEventKey or event is InputEventJoypadButton:
		return true
	if event is InputEventMouseButton:
		var b := (event as InputEventMouseButton).button_index
		return b == MOUSE_BUTTON_LEFT or b == MOUSE_BUTTON_RIGHT or b == MOUSE_BUTTON_MIDDLE
	return false


## Consumes `event` for `node`'s viewport (the consume rule). Call it after the motion
## has been completed.
static func consume(node: Node) -> void:
	if node == null or not node.is_inside_tree():
		return
	var vp := node.get_viewport()
	if vp != null:
		vp.set_input_as_handled()
