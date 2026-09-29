class_name ZineSlider
extends Range
## ART_BIBLE §6.5 slider: a track, a handle and a **value readout** ("1.6×") to its right,
## formatted by `format` (a Callable value -> String; default: the value at the step's
## decimals). A GLASS component: the filled part of the track in NET_CYAN, a PAPER handle,
## the readout in mono `label`. Mouse: press or drag on the track; keys and pad: left /
## right step by `step` (a step past either end is refused). All six §6 states (KitState),
## `disabled` refuses any press. `value` and `value_changed` are Range's. View only.

## A press or a step while disabled, or past either end.
signal refused

## Track size at text scale 1.0 (px): its least width and its thickness; the handle's
## radius; the gap before the readout.
const TRACK_MIN_W := 160.0
const TRACK_H := 6.0
const HANDLE_R := 9.0
const READOUT_GAP := UiTheme.SP_S

## Unavailable: no changes, presses are refused.
var disabled: bool = false:
	set(v):
		disabled = v
		focus_mode = Control.FOCUS_ALL
		queue_redraw()
## value -> the readout's words ("1.6×"); invalid = the plain value.
var format: Callable = Callable()
## A sample of the widest readout (keeps the track still while the value changes); "" =
## measured from the min and max.
var readout_sample: String = ""
var _dragging := false


func _init(p_min: float = 0.0, p_max: float = 1.0, p_step: float = 0.05, p_value: float = 0.0) -> void:
	min_value = p_min
	max_value = p_max
	step = p_step
	value = p_value
	focus_mode = Control.FOCUS_ALL
	mouse_filter = Control.MOUSE_FILTER_STOP
	mouse_default_cursor_shape = Control.CURSOR_POINTING_HAND
	KitState.track(self)
	value_changed.connect(func(_v: float) -> void: queue_redraw())


## The readout for `v` (format, or the value at the step's decimals).
func readout(v: float = value) -> String:
	if format.is_valid():
		return String(format.call(v))
	var decimals := maxi(0, -floori(log(step) / log(10.0))) if step > 0.0 and step < 1.0 else 0
	return String.num(v, decimals)


func _font_px() -> int:
	return UiTheme.font_px(UiTheme.LABEL)


func _readout_w() -> float:
	var f := Palette.mono()
	var sample := readout_sample
	if sample == "":
		sample = readout(min_value) if readout(min_value).length() > readout(max_value).length() else readout(max_value)
	return f.get_string_size(sample, HORIZONTAL_ALIGNMENT_LEFT, -1, _font_px()).x


## The track's rect (local, at rest).
func track_rect() -> Rect2:
	var s := Settings.text_scale
	var hr := HANDLE_R * s
	var w := maxf(1.0, size.x - _readout_w() - READOUT_GAP - hr * 2.0)
	return Rect2(Vector2(hr, (size.y - TRACK_H * s) * 0.5), Vector2(w, TRACK_H * s))


func _get_minimum_size() -> Vector2:
	var s := Settings.text_scale
	return Vector2(TRACK_MIN_W * s + HANDLE_R * s * 2.0 + READOUT_GAP + _readout_w(), maxf(HANDLE_R * s * 2.0 + UiTheme.SP_XS, Palette.mono().get_height(_font_px())))


func _gui_input(event: InputEvent) -> void:
	if event is InputEventMouseButton and (event as InputEventMouseButton).button_index == MOUSE_BUTTON_LEFT:
		var mb := event as InputEventMouseButton
		if mb.pressed and disabled:
			refuse()
		elif mb.pressed:
			_dragging = true
			KitState.set_pressed(self, true)
			_set_from_x(mb.position.x)
		else:
			_dragging = false
			KitState.set_pressed(self, false)
		accept_event()
	elif event is InputEventMouseMotion and _dragging and not disabled:
		_set_from_x((event as InputEventMouseMotion).position.x)
		accept_event()
	elif event.is_action_pressed(&"ui_left", true) or event.is_action_pressed(&"ui_right", true):
		nudge(-1 if event.is_action(&"ui_left") else 1)
		accept_event()


## Steps the value `dir` steps (keys, pad); refused while disabled or past either end.
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


func _set_from_x(x: float) -> void:
	var t := track_rect()
	value = lerpf(min_value, max_value, clampf((x - t.position.x) / t.size.x, 0.0, 1.0))


## The state drawn now (KitState).
func state() -> StringName:
	return KitState.of(self)


func _draw() -> void:
	var st := state()
	var s := Settings.text_scale
	var t := track_rect()
	t.position.y += KitState.lift(st)
	var k := clampf(get_as_ratio(), 0.0, 1.0)
	draw_rect(t, Palette.TERMINAL_BG)
	var fill := Palette.NET_CYAN if st != KitState.DISABLED else Palette.DISABLED
	draw_rect(Rect2(t.position, Vector2(t.size.x * k, t.size.y)), fill)
	draw_rect(t, KitState.edge_color(st, Palette.TEXT_MID), false, 1.0)
	var hc := Vector2(t.position.x + t.size.x * k, t.get_center().y)
	var hr := HANDLE_R * s
	if st == KitState.HOVER or st == KitState.PRESSED:
		draw_circle(hc, hr + UiTheme.GLOW_PX * 0.5 * KitState.glow(st), Color(Palette.TEXT_HI, UiTheme.GLOW_ALPHA * KitState.glow(st) * KitState.GLOW_SHARE))
	draw_circle(hc, hr, Palette.PAPER if st != KitState.DISABLED else Palette.TEXT_MID)
	draw_arc(hc, hr, 0, TAU, 20, Palette.INK, 1.5, true)
	var f := Palette.mono()
	var px := _font_px()
	var base := (size.y + f.get_ascent(px) - f.get_descent(px)) * 0.5 + KitState.lift(st)
	draw_string(f, Vector2(size.x - _readout_w(), base), readout(), HORIZONTAL_ALIGNMENT_RIGHT, _readout_w(), px, KitState.label_color(st))
	var face := Rect2(Vector2(0, KitState.lift(st)), size)
	KitState.draw_frame(self, face, st)
