class_name KitState
extends RefCounted
## ART_BIBLE §6: the six states every kit component defines, in one place. A component
## asks `of(control)` which state it is in and draws it with `draw_frame` (hover lift and
## glow, focus brackets, disabled outline and lock, the refused HARM flash and no-entry
## mark). The components lab and the tests force a state with `force`. Theme-styled native
## Buttons get the same looks from UiTheme; their refused flash is `RefusalMark.flash`.
## View only; no game state.

const IDLE := &"idle"
const HOVER := &"hover"
const FOCUS := &"focus"
const PRESSED := &"pressed"
const DISABLED := &"disabled"
const REFUSED := &"refused"
## The §6 states in the bible's order.
const ALL: Array[StringName] = [IDLE, HOVER, FOCUS, PRESSED, DISABLED, REFUSED]

## Meta keys on the control: a forced state (lab, tests), the refusal's end (msec), the
## pointer over it, a press held on it.
const META_FORCED := &"kit_forced_state"
const META_REFUSED := &"kit_refused_until"
const META_HOVER := &"kit_hover"
const META_PRESS := &"kit_press"
## The refused flash's motion entry (T2).
const REFUSED_MOTION := &"button_refused"
## The no-entry mark's radius on a refused control, as a share of its height (and a cap, px).
const MARK_SHARE := 0.32
const MARK_MAX := 11.0
## The HARM outline of a refused control (px).
const REFUSED_BORDER := 2.0
## The flash fills the face at this share of its peak alpha; the outline fades by this share.
const FLASH_FILL_SHARE := 0.35
const OUTLINE_FADE := 0.5
## Milliseconds in a second (the refusal's clock).
const MSEC := 1000.0


## Starts tracking pointer hover and presses on `c` (a kit component calls it in _init).
static func track(c: Control) -> void:
	c.mouse_entered.connect(func() -> void: c.set_meta(META_HOVER, true); c.queue_redraw())
	c.mouse_exited.connect(func() -> void: c.set_meta(META_HOVER, false); c.set_meta(META_PRESS, false); c.queue_redraw())
	c.focus_entered.connect(c.queue_redraw)
	c.focus_exited.connect(func() -> void: c.set_meta(META_PRESS, false); c.queue_redraw())
	if c is BaseButton:
		(c as BaseButton).button_down.connect(KitState.set_pressed.bind(c, true))
		(c as BaseButton).button_up.connect(KitState.set_pressed.bind(c, false))


## Marks a press held (true) or let go (false) on `c` (components call it from _gui_input).
static func set_pressed(c: Control, on: bool) -> void:
	c.set_meta(META_PRESS, on)
	c.queue_redraw()


## Forces `c` into `state` (one of ALL) until clear_force; &"" clears it.
static func force(c: Control, state: StringName) -> void:
	if state == &"":
		clear_force(c)
		return
	assert(ALL.has(state), "KitState: unknown state %s" % state)
	c.set_meta(META_FORCED, state)
	c.queue_redraw()


## Drops a forced state.
static func clear_force(c: Control) -> void:
	if c.has_meta(META_FORCED):
		c.remove_meta(META_FORCED)
	c.queue_redraw()


## True when `c` is disabled (a BaseButton's own flag, or a kit Range's `disabled`).
static func is_disabled(c: Control) -> bool:
	if c is BaseButton:
		return (c as BaseButton).disabled
	var d: Variant = c.get(&"disabled")
	return d is bool and d


## Shows the §6 refused state on `c` for the `button_refused` entry's seconds (read raw:
## the mark must be seen; under reduce effects it holds still instead of flashing).
static func refuse(c: Control) -> void:
	var e := Motion.entry(REFUSED_MOTION)
	var secs := e.duration if e != null else 0.0
	c.set_meta(META_REFUSED, Time.get_ticks_msec() + secs * MSEC)
	c.queue_redraw()
	if c.is_inside_tree() and secs > 0.0:
		# Redraw every frame of the flash (its fade), and once more when it ends.
		var tw := c.create_tween()
		tw.tween_method(func(_k: float) -> void: c.queue_redraw(), 0.0, 1.0, secs)
		tw.tween_callback(c.queue_redraw)


## True while `c` shows its refused state.
static func refused(c: Control) -> bool:
	return c.has_meta(META_REFUSED) and Time.get_ticks_msec() < float(c.get_meta(META_REFUSED))


## The refusal's progress 0..1 (0 just refused; 1 over), for the flash's fade.
static func refused_progress(c: Control) -> float:
	var e := Motion.entry(REFUSED_MOTION)
	if e == null or e.duration <= 0.0 or not c.has_meta(META_REFUSED):
		return 1.0
	var left := (float(c.get_meta(META_REFUSED)) - Time.get_ticks_msec()) / MSEC
	return clampf(1.0 - left / e.duration, 0.0, 1.0)


## The state `c` shows now: forced, else refused, disabled, pressed, focus, hover, idle.
static func of(c: Control) -> StringName:
	if c.has_meta(META_FORCED):
		return StringName(c.get_meta(META_FORCED))
	if refused(c):
		return REFUSED
	if is_disabled(c):
		return DISABLED
	var pressing := bool(c.get_meta(META_PRESS, false))
	if c is BaseButton:
		pressing = pressing or (c as BaseButton).is_pressed() and not (c as BaseButton).toggle_mode
	if pressing:
		return PRESSED
	if c.has_focus():
		return FOCUS
	var hovering := bool(c.get_meta(META_HOVER, false))
	if c is BaseButton:
		hovering = hovering or (c as BaseButton).is_hovered()
	return HOVER if hovering else IDLE


## §6: the vertical offset a state draws its face at (hover lifts, pressed drops; px).
static func lift(state: StringName) -> float:
	match state:
		HOVER:
			return -UiTheme.HOVER_LIFT
		PRESSED:
			return UiTheme.PRESS_DROP
	return 0.0


## §6: the glow share a state draws with (hover +20%, pressed -20%).
static func glow(state: StringName) -> float:
	match state:
		HOVER:
			return UiTheme.GLOW_HOVER
		PRESSED:
			return UiTheme.GLOW_PRESSED
	return 1.0


## The label colour of a state on glass: TEXT_HI, or TEXT_MID when disabled (§3.7: 4.5:1).
static func label_color(state: StringName) -> Color:
	return Palette.TEXT_MID if state == DISABLED else Palette.TEXT_HI


## The edge colour of a state for a glass component whose rest edge is `edge`.
static func edge_color(state: StringName, edge: Color = Palette.TERMINAL_EDGE) -> Color:
	match state:
		DISABLED:
			return Palette.DISABLED
		REFUSED:
			return Palette.HARM
		HOVER, FOCUS:
			return edge.lightened(UiTheme.FILL_SHIFT)
	return edge


## Draws the state marks over a component's face `rect` (local): focus brackets, the
## disabled lock badge, the refused HARM outline and no-entry mark. The component draws
## its own face first (lifted by `lift(state)`, edged by `edge_color(state)`).
static func draw_frame(c: Control, rect: Rect2, state: StringName) -> void:
	match state:
		FOCUS:
			StyleBoxBrackets.draw_on(c, rect)
		DISABLED:
			StyleBoxLocked.draw_lock_badge(c.get_canvas_item(), Vector2(rect.end.x, rect.position.y))
		REFUSED:
			var k := refused_progress(c) if c.has_meta(META_REFUSED) and not c.has_meta(META_FORCED) else 0.0
			var a := 1.0 if not Fx.effects_enabled() else 1.0 - k * OUTLINE_FADE
			c.draw_rect(rect, Color(Palette.HARM, a), false, REFUSED_BORDER)
			var peak := Motion.amplitude(REFUSED_MOTION)
			if Fx.effects_enabled():
				c.draw_rect(rect, Color(Palette.HARM, peak * (1.0 - k) * FLASH_FILL_SHARE))
			var r := minf(rect.size.y * MARK_SHARE, MARK_MAX)
			StatIcon.draw(c, Vector2(rect.end.x - r, rect.position.y), r, StatIcon.NO_ENTRY, Palette.HARM, true)


## Draws a glass face `rect` for `state`: `fill` (dimmed when disabled to opaque glass), a
## 1 px edge (edge_color), and the hover / pressed glow (§6: +20% / -20% of GLOW_ALPHA).
static func draw_box(c: CanvasItem, rect: Rect2, state: StringName, fill: Color = Palette.TERMINAL_BG,
		edge: Color = Palette.TERMINAL_EDGE) -> void:
	var k := glow(state)
	if state == HOVER or state == PRESSED:
		c.draw_rect(rect.grow(UiTheme.GLOW_PX * 0.5 * k), Color(edge, UiTheme.GLOW_ALPHA * k * GLOW_SHARE))
	c.draw_rect(rect, Palette.TERMINAL_BG if state == DISABLED else fill)
	c.draw_rect(rect, edge_color(state, edge), false, 1.0)


## A drawn glow's alpha relative to the theme's GLOW_ALPHA (a flat rect reads stronger than
## the theme's soft shadow).
const GLOW_SHARE := 0.5
## The node that shows a forced state on a native control (force_native).
const FORCED_NODE := "ForcedState"


## Shows `state` on a theme-styled native control `c` (the components lab, tests): its
## normal box becomes the state's box (hover, pressed, disabled), focus draws the brackets,
## refused holds the RefusalMark look. IDLE clears it.
static func force_native(c: Control, state: StringName) -> void:
	for key in [&"normal", &"hover"]:
		c.remove_theme_stylebox_override(key)
	var old := c.get_node_or_null(FORCED_NODE)
	if old != null:
		c.remove_child(old)
		old.free()
	if c is BaseButton:
		(c as BaseButton).disabled = state == DISABLED
	c.set_meta(META_FORCED, state)
	match state:
		HOVER, PRESSED:
			var sb := c.get_theme_stylebox(&"hover" if state == HOVER else &"pressed")
			c.add_theme_stylebox_override(&"normal", sb)
			c.add_theme_stylebox_override(&"hover", sb)
			if c is Button:
				var col := c.get_theme_color(&"font_hover_color" if state == HOVER else &"font_pressed_color")
				c.add_theme_color_override(&"font_color", col)
		FOCUS, REFUSED, DISABLED:
			if state == DISABLED and c is BaseButton:
				return  # the theme's disabled box carries the lock
			var mark := _ForcedMark.new()
			mark.name = FORCED_NODE
			mark.state = state
			mark.set_meta(META_FORCED, state)
			c.add_child(mark)
			mark.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)


## Draws a forced focus / refused frame over a native control (force_native).
class _ForcedMark extends Control:
	var state: StringName = FOCUS

	func _init() -> void:
		mouse_filter = Control.MOUSE_FILTER_IGNORE
		focus_mode = Control.FOCUS_NONE

	func _draw() -> void:
		KitState.draw_frame(self, Rect2(Vector2.ZERO, size), state)
