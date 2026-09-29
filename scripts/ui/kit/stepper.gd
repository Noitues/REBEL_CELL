class_name Stepper
extends Range
## ART_BIBLE §6.5 stepper: `[−] value [+]` chips with the value between them in the
## `label` step (Anton, it is a number), replacing the native SpinBox (ICE, seeds). A GLASS
## component. Mouse: press a chip; keys and pad: left / right (or the D-pad) step by
## `step`; a step past either end is refused (HARM flash, no-entry mark) and the chip at the
## end is drawn DISABLED. All six §6 states (KitState); `disabled` refuses every press.
## `value` and `value_changed` are Range's; `format` words the value. View only.

## A step while disabled, or past either end.
signal refused

## A chip's side at text scale 1.0 (px), the gap between chip and value, and the chip
## icon's share of the chip.
const CHIP := 28.0
const GAP := UiTheme.SP_S
const ICON_SHARE := 0.32

## Unavailable: no changes, presses are refused.
var disabled: bool = false:
	set(v):
		disabled = v
		queue_redraw()
## value -> its words; invalid = the whole number.
var format: Callable = Callable()
## A sample of the widest value (keeps the chips still); "" = from the min and max.
var value_sample: String = ""


func _init(p_min: float = 0.0, p_max: float = 10.0, p_step: float = 1.0, p_value: float = 0.0) -> void:
	min_value = p_min
	max_value = p_max
	step = p_step
	value = p_value
	focus_mode = Control.FOCUS_ALL
	mouse_filter = Control.MOUSE_FILTER_STOP
	KitState.track(self)
	value_changed.connect(func(_v: float) -> void: queue_redraw())


## The value's words (format, or the number).
func words(v: float = value) -> String:
	if format.is_valid():
		return String(format.call(v))
	return str(int(v)) if is_equal_approx(step, roundf(step)) else String.num(v, 2)


func _font_px() -> int:
	return UiTheme.font_px(UiTheme.LABEL)


func _value_w() -> float:
	var sample := value_sample
	if sample == "":
		sample = words(min_value) if words(min_value).length() > words(max_value).length() else words(max_value)
	return Palette.display().get_string_size(sample, HORIZONTAL_ALIGNMENT_LEFT, -1, _font_px()).x


func _chip() -> float:
	return maxf(CHIP * Settings.text_scale, Palette.display().get_height(_font_px()))


## The minus chip's rect (local, at rest).
func minus_rect() -> Rect2:
	var c := _chip()
	return Rect2(Vector2(0, (size.y - c) * 0.5), Vector2(c, c))


## The plus chip's rect (local, at rest).
func plus_rect() -> Rect2:
	var c := _chip()
	return Rect2(Vector2(size.x - c, (size.y - c) * 0.5), Vector2(c, c))


func _get_minimum_size() -> Vector2:
	var c := _chip()
	return Vector2(c * 2.0 + GAP * 2.0 + _value_w(), c)


func _gui_input(event: InputEvent) -> void:
	if event is InputEventMouseButton and (event as InputEventMouseButton).button_index == MOUSE_BUTTON_LEFT:
		var mb := event as InputEventMouseButton
		KitState.set_pressed(self, mb.pressed)
		if mb.pressed:
			if minus_rect().has_point(mb.position):
				nudge(-1)
			elif plus_rect().has_point(mb.position):
				nudge(1)
		accept_event()
	elif event.is_action_pressed(&"ui_left", true) or event.is_action_pressed(&"ui_right", true):
		nudge(-1 if event.is_action(&"ui_left") else 1)
		accept_event()


## Steps `dir` steps; refused while disabled or past either end.
func nudge(dir: int) -> void:
	var to := clampf(value + dir * step, min_value, max_value)
	if disabled or is_equal_approx(to, value):
		refuse()
		return
	value = to


## Shows the refused state (§6) and emits `refused`.
func refuse() -> void:
	KitState.refuse(self)
	refused.emit()


## The state drawn now (KitState).
func state() -> StringName:
	return KitState.of(self)


func _draw() -> void:
	var st := state()
	var dy := KitState.lift(st)
	for side in [-1, 1]:
		var r := minus_rect() if side < 0 else plus_rect()
		r.position.y += dy
		var at_end := is_equal_approx(value, min_value if side < 0 else max_value)
		var chip_state := KitState.DISABLED if at_end and st != KitState.REFUSED else st
		KitState.draw_box(self, r, chip_state if chip_state != KitState.FOCUS else KitState.IDLE)
		StatIcon.draw(self, r.get_center(), r.size.y * ICON_SHARE, StatIcon.MINUS if side < 0 else StatIcon.PLUS, KitState.label_color(chip_state))
	var f := Palette.display()
	var px := _font_px()
	var base := (size.y + f.get_ascent(px) - f.get_descent(px)) * 0.5 + dy
	var x := minus_rect().end.x + GAP
	draw_string(f, Vector2(x, base), words(), HORIZONTAL_ALIGNMENT_CENTER, maxf(1.0, plus_rect().position.x - GAP - x), px, KitState.label_color(st))
	KitState.draw_frame(self, Rect2(Vector2(0, dy), size), st)
