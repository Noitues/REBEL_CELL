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
##
## - **Menus pass presses on (ANIM-R2)**: in a menu (MenuMotion) a focus move and a press
##   that works the menu (ui_accept, a click on one of its lines) complete the line's motion
##   and are let through, so a fast Down then Enter always activates; only presses that don't
##   work the menu are consumed.
## - **Words together (ANIM-R2)**: a press that completes typing shows every word typing on
##   screen at once (the page's text and the subtitle), so one press reads the whole event.
## - **Under the jack (ANIM-R2)**: while `Fx.transitioning()` nothing is a press: no helper
##   acts under the jack's cover (Fx swallows the press itself).


## True when `event` is a press that completes a motion (see the class notes).
static func is_press(event: InputEvent) -> bool:
	if event == null or not event.is_pressed() or event.is_echo():
		return false
	if jacking():
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


## True while a jack (Fx.transitioning) covers the screen. Looked up at run time: the kit
## must compile in `-s` tool scripts, where autoloads don't exist yet.
static func jacking() -> bool:
	var tree := Engine.get_main_loop() as SceneTree
	if tree == null or tree.root == null:
		return false
	var fx := tree.root.get_node_or_null(^"Fx")
	return fx != null and fx.has_method(&"transitioning") and bool(fx.call(&"transitioning"))
