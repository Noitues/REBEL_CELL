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
## - **One rule everywhere (ANIM-R4 C2, `verdict`)**: every helper asks `verdict`: IGNORE
##   while a PauseMenu is open (the menu keeps its presses; the motion plays on), PASS for a
##   press that works the screen (complete the motion, let the press through), CONSUME for
##   any other press. `works_ui` trusts the hovered control under the point (a button
##   covered by a panel is not clicked), requires the button's `button_mask` (a right-click
##   on a button works nothing), and searches rects only when nothing hovered holds the
##   point (a click pushed without a mouse move first). A helper may name buttons whose
##   press it keeps (`keep`: the combat replay keeps SEND IT, RESPIN, UNDO and the hand, so
##   a press that ends the replay never also plays the next turn blind).
## - **The raid playout's own controls (ANIM-R5, the one exception)**: the playout asks
##   `verdict` like every helper, but a PASS that drives the playout itself (a focus move,
##   which walks to 1x / 2x / 4x and Skip, or a press on one of them:
##   `RaidPlayoutPanel.drives_playout`) does not end the current step: speeding the raid up
##   never skips the step being watched. STYLE_GUIDE 5.1 says so.

## Focus-move actions (a menu's D-pad / arrows / Tab).
const FOCUS_ACTIONS: Array[StringName] = [&"ui_up", &"ui_down", &"ui_left", &"ui_right", &"ui_focus_next", &"ui_focus_prev"]
## The group every open PauseMenu is in (presses belong to it while it is open).
const PAUSE_GROUP := &"pause_menu"
## What a helper does with a press while its motion plays (`verdict`).
enum Verdict { IGNORE, PASS, CONSUME }


## ANIM-R4 C2: the one press rule as a verdict. IGNORE: not a press, or an open PauseMenu
## owns it (the motion goes on); PASS: a press that works the screen (`works_ui`, and not
## on a button in `keep`): complete the motion and let it through; CONSUME: complete the
## motion and `consume` the press.
static func verdict(event: InputEvent, node: Node, keep: Array = []) -> Verdict:
	if not is_press(event) or pause_open(node):
		return Verdict.IGNORE
	if works_ui(event, node, keep):
		return Verdict.PASS
	return Verdict.CONSUME


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
## Such a press completes a motion and passes on to what it works. ANIM-R4 C2: the click's
## mouse button must be in the button's `button_mask`; a button in `keep` (or inside one)
## doesn't count (its helper keeps that press).
static func works_ui(event: InputEvent, node: Node, keep: Array = []) -> bool:
	if event == null:
		return false
	if is_focus_move(event) or event.is_action(&"open_settings"):
		return true
	if node == null or not node.is_inside_tree():
		return false
	var vp := node.get_viewport()
	if vp == null:
		return false
	var b: BaseButton = null
	if event is InputEventMouseButton:
		var mb := event as InputEventMouseButton
		b = button_at(vp, mb.global_position, mb.button_index)
	elif event.is_action(&"ui_accept"):
		b = usable_button(vp.gui_get_focus_owner())
	return b != null and not kept(b, keep)


## True when `b` is one of `keep` or inside one of them.
static func kept(b: Node, keep: Array) -> bool:
	for k in keep:
		if k is Node and is_instance_valid(k) and (k == b or (k as Node).is_ancestor_of(b)):
			return true
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


## The usable button at `at` (global) in `vp` that mouse button `button` (an index; 0 =
## any) presses. ANIM-R4 C2: the hovered control is trusted when it holds the point (a
## button under a panel isn't clicked: the panel is what is hovered); only when nothing
## hovered holds the point (a click pushed without a mouse move first) is the topmost
## usable button whose rect holds it taken. A button whose `button_mask` leaves out
## `button` (a right-click on a left-click button) works nothing.
static func button_at(vp: Viewport, at: Vector2, button: int = 0) -> BaseButton:
	var hovered := vp.gui_get_hovered_control()
	if hovered != null and is_instance_valid(hovered) and hovered.is_visible_in_tree() and hovered.get_global_rect().has_point(at):
		var hb := usable_button(hovered)
		return hb if hb != null and takes(hb, button) else null
	# Nothing hovered holds the point: the topmost control that takes the mouse there (a
	# higher canvas layer first, then the later in tree order: it draws on top) is what the
	# click reaches, as the viewport would find it; a button only when it is (or holds) that.
	var top: Control = null
	var top_layer := -INF
	for n in vp.get_tree().root.find_children("*", "Control", true, false):
		var c := n as Control
		if c.get_viewport() != vp or c.mouse_filter == Control.MOUSE_FILTER_IGNORE or not c.is_visible_in_tree() or not c.get_global_rect().has_point(at):
			continue
		var cl := c.get_canvas_layer_node()
		var layer := float(cl.layer) if cl != null else 0.0
		if layer >= top_layer:
			top_layer = layer
			top = c
	var best := usable_button(top)
	return best if best != null and takes(best, button) else null


## True when mouse button `button` (an index; 0 = any) presses `b` (its `button_mask`).
static func takes(b: BaseButton, button: int) -> bool:
	if button <= 0:
		return true
	return (b.button_mask & (1 << (button - 1))) != 0


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
