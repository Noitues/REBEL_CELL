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
## - **Presses that work the screen pass (ANIM-R3)**: outside menus too, a press that works
##   the screen (`works_ui`: a focus move, Settings' key, accept on the focused usable
##   button, a click on a usable button) completes the motion and passes on; only presses
##   aimed at the motion itself are consumed (the raid playout's step, ambient typing, the
##   subtitles). A consumed press still switches the key hints between keys and pad
##   (`consume` tells Settings which device it came from).

## Focus-move actions (a menu's D-pad / arrows / Tab).
const FOCUS_ACTIONS: Array[StringName] = [&"ui_up", &"ui_down", &"ui_left", &"ui_right", &"ui_focus_next", &"ui_focus_prev"]
## The group every open PauseMenu is in (presses belong to it while it is open).
const PAUSE_GROUP := &"pause_menu"


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
## has been completed. ANIM-R3 A4: Settings sees the press first (a pad press that ends a
## motion still switches the prompts to the pad; Settings' own _input never gets it).
static func consume(node: Node, event: InputEvent = null) -> void:
	if node == null or not node.is_inside_tree():
		return
	if event != null:
		var settings := node.get_tree().root.get_node_or_null(^"Settings")
		if settings != null and settings.has_method(&"observe_device"):
			settings.call(&"observe_device", event)
	var vp := node.get_viewport()
	if vp != null:
		vp.set_input_as_handled()


## True when `event` works the screen (ANIM-R3): a focus move, the Settings key, accept on
## the focused usable button, or a click on a usable button (the one under the pointer).
## Such a press completes a motion and passes on to what it works.
static func works_ui(event: InputEvent, node: Node) -> bool:
	if event == null:
		return false
	if is_focus_move(event) or event.is_action(&"open_settings"):
		return true
	if node == null or not node.is_inside_tree():
		return false
	var vp := node.get_viewport()
	if vp == null:
		return false
	if event.is_action(&"ui_accept") and not (event is InputEventMouseButton):
		return usable_button(vp.gui_get_focus_owner()) != null
	if event is InputEventMouseButton:
		return button_at(vp, (event as InputEventMouseButton).global_position) != null
	return false


## True when `event` is a focus move (arrows, D-pad, Tab).
static func is_focus_move(event: InputEvent) -> bool:
	for a in FOCUS_ACTIONS:
		if event.is_action(a):
			return true
	return false


## The usable (visible, enabled) button `c` is or sits in, or null.
static func usable_button(c: Node) -> BaseButton:
	var n := c
	while n != null and n is Control:
		if n is BaseButton:
			var b := n as BaseButton
			return b if b.is_visible_in_tree() and not b.disabled else null
		n = n.get_parent()
	return null


## The usable button at `at` (global) in `vp`: the hovered control's, else the topmost
## button whose rect holds the point (a click pushed without a mouse move first).
static func button_at(vp: Viewport, at: Vector2) -> BaseButton:
	var hovered := usable_button(vp.gui_get_hovered_control())
	if hovered != null and hovered.get_global_rect().has_point(at):
		return hovered
	var best: BaseButton = null
	for b in vp.get_tree().root.find_children("*", "BaseButton", true, false):
		var btn := b as BaseButton
		if btn.get_viewport() == vp and btn.is_visible_in_tree() and not btn.disabled and btn.mouse_filter != Control.MOUSE_FILTER_IGNORE \
				and btn.get_global_rect().has_point(at):
			best = btn  # tree order: the last one found draws on top
	return best


## True while a PauseMenu is open (its presses are its own).
static func pause_open(node: Node) -> bool:
	return node != null and node.is_inside_tree() and not node.get_tree().get_nodes_in_group(PAUSE_GROUP).is_empty()


## True while a jack (Fx.transitioning) covers the screen. Looked up at run time: the kit
## must compile in `-s` tool scripts, where autoloads don't exist yet.
static func jacking() -> bool:
	var tree := Engine.get_main_loop() as SceneTree
	if tree == null or tree.root == null:
		return false
	var fx := tree.root.get_node_or_null(^"Fx")
	return fx != null and fx.has_method(&"transitioning") and bool(fx.call(&"transitioning"))
