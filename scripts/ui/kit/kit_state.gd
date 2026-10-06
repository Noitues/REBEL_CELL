class_name KitState
extends RefCounted
## ART_BIBLE v1 §6 (kept by v2, §2.10): the six states every kit component defines, in one
## place. A component asks `of(control)` which state it is in and draws its marks with
## `draw_frame` (focus brackets, the disabled lock, the refused HARM outline and no-entry
## mark); hover lifts it by `lift` and glows by `glow`. Tests (and a lab) force a state with
## `force`. Theme-styled native Buttons get hover / pressed / focus from UiTheme; their
## refused flash is `RefusalMark.flash`. View only; no game state.
## ART-0 F: ported from art-pass (W2) onto main's kit; the stickers keep their own lime halo
## for focus (v2 §2.10), the other components draw the brackets.

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
## The refused flash's motion entry (T2; amplitude = the flash's peak alpha).
const REFUSED_MOTION := &"button_refused"
## The no-entry mark's radius on a refused control, as a share of its height (and a cap, px).
const MARK_SHARE := 0.32
const MARK_MAX := 11.0
## The no-entry mark's stroke (px) and its bar's length (share of the radius).
const MARK_STROKE := 2.0
const MARK_BAR := 0.6
## The HARM outline of a refused control (px).
const REFUSED_BORDER := 2.0
## The flash fills the face at this share of its peak alpha; the outline fades by this share.
const FLASH_FILL_SHARE := 0.35
const OUTLINE_FADE := 0.5
## Milliseconds in a second (the refusal's clock).
const MSEC := 1000.0
## The disabled lock badge's radius (px) and the lock drawn in it, as shares of the radius.
const BADGE_R := 7.0
const LOCK_BODY_W := 0.9
const LOCK_BODY_H := 0.7
const SHACKLE_R := 0.36
const SHACKLE_W := 1.5
const SHACKLE_SEGMENTS := 8
## Arc segments of the drawn marks.
const MARK_SEGMENTS := 20


## Starts tracking pointer hover and presses on `c` (a kit component calls it in _init).
static func track(c: Control) -> void:
	c.mouse_entered.connect(KitState._set_meta_redraw.bind(c, META_HOVER, true))
	c.mouse_exited.connect(KitState._left.bind(c))
	c.focus_entered.connect(c.queue_redraw)
	c.focus_exited.connect(KitState._set_meta_redraw.bind(c, META_PRESS, false))
	if c is BaseButton:
		(c as BaseButton).button_down.connect(KitState.set_pressed.bind(c, true))
		(c as BaseButton).button_up.connect(KitState.set_pressed.bind(c, false))


static func _set_meta_redraw(c: Control, key: StringName, on: bool) -> void:
	c.set_meta(key, on)
	c.queue_redraw()


static func _left(c: Control) -> void:
	c.set_meta(META_HOVER, false)
	c.set_meta(META_PRESS, false)
	c.queue_redraw()


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


## Shows the §6 refused state on `c` for the `button_refused` entry's seconds (the mark must
## be seen: switched off or under reduce effects it holds still instead of flashing).
static func refuse(c: Control) -> void:
	var e := Motion.entry(REFUSED_MOTION)
	var secs := e.duration if e != null else 0.0
	c.set_meta(META_REFUSED, Time.get_ticks_msec() + secs * MSEC)
	c.queue_redraw()
	if c.is_inside_tree() and secs > 0.0:
		# Redraw every frame of the flash (its fade), and once more when it ends.
		var tw := c.create_tween()
		tw.tween_method(KitState._redraw_step.bind(c), 0.0, 1.0, secs)
		tw.tween_callback(c.queue_redraw)


static func _redraw_step(_k: float, c: Control) -> void:
	c.queue_redraw()


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
	edge = PaletteSkins.chrome(edge)  # ART-12 12s-b: a glass component's edge is chrome
	match state:
		DISABLED:
			return Palette.DISABLED
		REFUSED:
			return Palette.HARM
		HOVER, FOCUS:
			return edge.lightened(UiTheme.FILL_SHIFT)
	return edge


## Draws the state marks over a component's face `rect` (local): focus brackets (unless
## `brackets` is off: a sticker shows focus by its own halo, v2 §2.10), the disabled lock
## badge, the refused HARM outline and no-entry mark. The component draws its own face
## first (lifted by `lift(state)`).
static func draw_frame(c: Control, rect: Rect2, state: StringName, brackets: bool = true) -> void:
	match state:
		FOCUS:
			if brackets:
				StyleBoxBrackets.draw_on(c, rect)
		DISABLED:
			draw_lock_badge(c, Vector2(rect.end.x, rect.position.y))
		REFUSED:
			var k := refused_progress(c) if c.has_meta(META_REFUSED) and not c.has_meta(META_FORCED) else 0.0
			var flashing := Motion.live(REFUSED_MOTION)
			var a := 1.0 - k * OUTLINE_FADE if flashing else 1.0
			c.draw_rect(rect, Color(Palette.HARM, a), false, REFUSED_BORDER)
			if flashing:
				c.draw_rect(rect, Color(Palette.HARM, Motion.amplitude(REFUSED_MOTION) * (1.0 - k) * FLASH_FILL_SHARE))
			var r := minf(rect.size.y * MARK_SHARE, MARK_MAX)
			draw_no_entry(c, Vector2(rect.end.x - r, rect.position.y), r)


## The no-entry mark (STYLE_GUIDE 5.4): a HARM ring with a bar across, centred on `at`.
static func draw_no_entry(ci: CanvasItem, at: Vector2, r: float) -> void:
	ci.draw_circle(at, r, Palette.DESK_DARK)
	ci.draw_arc(at, r - MARK_STROKE * 0.5, 0.0, TAU, MARK_SEGMENTS, Palette.HARM, MARK_STROKE, true)
	ci.draw_line(at - Vector2(r * MARK_BAR, 0.0), at + Vector2(r * MARK_BAR, 0.0), Palette.HARM, MARK_STROKE)


## A lock in a dark badge centred on `at` (§6 Disabled: the lock or reason; the reason goes in
## the tooltip). It hangs half outside the corner, so it adds nothing to the control's size.
static func draw_lock_badge(ci: CanvasItem, at: Vector2, r: float = BADGE_R) -> void:
	ci.draw_circle(at, r + 1.0, Palette.DISABLED)
	ci.draw_circle(at, r, Palette.DESK_DARK)
	var bw := r * LOCK_BODY_W
	var bh := r * LOCK_BODY_H
	var body := Rect2(at + Vector2(-bw * 0.5, -bh * 0.15), Vector2(bw, bh))
	ci.draw_rect(body, Palette.TEXT_MID)
	var sc := Vector2(at.x, body.position.y)
	ci.draw_arc(sc, r * SHACKLE_R, PI, TAU, SHACKLE_SEGMENTS, Palette.TEXT_MID, SHACKLE_W, true)


## The node that shows a forced state on a native control (force_native).
const FORCED_NODE := "ForcedState"


## Shows `state` on a theme-styled native control `c` (tests, a lab): its normal box becomes
## the state's box (hover, pressed), disabled sets the flag, focus and refused draw their
## marks over it. IDLE clears it.
static func force_native(c: Control, state: StringName) -> void:
	for key in [&"normal", &"hover"]:
		c.remove_theme_stylebox_override(key)
	if c is Button:
		c.remove_theme_color_override(&"font_color")
	var old := c.get_node_or_null(FORCED_NODE)
	if old != null:
		c.remove_child(old)
		old.free()
	if c is BaseButton:
		(c as BaseButton).disabled = state == DISABLED
	if state == IDLE:
		clear_force(c)
		return
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
			var mark := _ForcedMark.new()
			mark.name = FORCED_NODE
			mark.state = state
			mark.set_meta(META_FORCED, state)
			c.add_child(mark)
			mark.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)


## Draws a forced focus / refused / disabled frame over a native control (force_native).
class _ForcedMark extends Control:
	var state: StringName = FOCUS

	func _init() -> void:
		mouse_filter = Control.MOUSE_FILTER_IGNORE
		focus_mode = Control.FOCUS_NONE

	func _draw() -> void:
		KitState.draw_frame(self, Rect2(Vector2.ZERO, size), state)
