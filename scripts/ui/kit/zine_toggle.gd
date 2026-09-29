class_name ZineToggle
extends BaseButton
## ART_BIBLE §6.5 toggle: a pill switch placed **next to** its label (label left, the
## switch SP_M (16 px) right of the longest label in its group, `align_group`), with both
## states drawn as pills: ON is a filled NET_CYAN pill with the knob right and a tick, OFF
## an empty glass pill with the knob left (readable in greyscale by shape and side). A
## GLASS component (mono label, TEXT_HI). All six §6 states (KitState): hover lifts and
## glows, focus brackets and the 1.03 scale (UiFocus), pressed drops, disabled has the
## DISABLED outline and a lock, a press while disabled is refused (HARM flash, no-entry
## mark) and emits `refused`. View only: it emits, the screen decides.

## The value changed (true = on); `toggled` fires too (BaseButton).
signal value_changed(value: bool)
## A press while disabled.
signal refused

## The pill's size at text scale 1.0 (px) and the knob's inset.
const PILL_W := 44.0
const PILL_H := 24.0
const KNOB_INSET := 4.0
## The gap between the label column and the pill (§6.5: 16 px).
const GAP := UiTheme.SP_M
## The knob's travel motion (T1).
const SLIDE_MOTION := &"toggle_slide"

## The words left of the switch (translated by the caller).
var text: String = "":
	set(v):
		text = v
		update_minimum_size()
		queue_redraw()
## The label column's width (px) shared by a group (align_group); 0 = this label's own.
var label_width: float = 0.0:
	set(v):
		label_width = v
		update_minimum_size()
		queue_redraw()
## The knob's side, 0 (off) .. 1 (on), tweened by `toggle_slide`.
var knob: float = 0.0:
	set(v):
		knob = v
		queue_redraw()

## On (true) or off.
var value: bool:
	get:
		return button_pressed
	set(v):
		set_pressed_no_signal(v)
		knob = 1.0 if v else 0.0


func _init(p_text: String = "", on: bool = false) -> void:
	toggle_mode = true
	focus_mode = Control.FOCUS_ALL
	mouse_default_cursor_shape = Control.CURSOR_POINTING_HAND
	text = p_text
	value = on
	KitState.track(self)
	toggled.connect(_on_toggled)


func _on_toggled(on: bool) -> void:
	Motion.run(SLIDE_MOTION, self, ^"knob", 1.0 if on else 0.0)
	value_changed.emit(on)


func _gui_input(event: InputEvent) -> void:
	if disabled and (event.is_action_pressed(&"ui_accept") or (event is InputEventMouseButton and (event as InputEventMouseButton).pressed
			and (event as InputEventMouseButton).button_index == MOUSE_BUTTON_LEFT)):
		refuse()
		accept_event()


## Shows the refused state (§6) and emits `refused`.
func refuse() -> void:
	KitState.refuse(self)
	refused.emit()


## Lines up a group's switches: each label column takes the longest label's width, so every
## pill sits GAP right of the longest line (§6.5).
static func align_group(toggles: Array) -> void:
	var w := 0.0
	for t in toggles:
		w = maxf(w, (t as ZineToggle).own_label_width())
	for t in toggles:
		(t as ZineToggle).label_width = w


## This label's own width at the player's text size (px).
func own_label_width() -> float:
	return Palette.mono().get_string_size(text, HORIZONTAL_ALIGNMENT_LEFT, -1, _font_px()).x if text != "" else 0.0


func _font_px() -> int:
	return UiTheme.font_px(UiTheme.BODY)


## The pill's rect (local, at rest).
func pill_rect() -> Rect2:
	var s := Settings.text_scale
	var lw := maxf(label_width, own_label_width())
	var x := lw + GAP if lw > 0.0 else 0.0
	return Rect2(Vector2(x, (size.y - PILL_H * s) * 0.5), Vector2(PILL_W, PILL_H) * s)


func _get_minimum_size() -> Vector2:
	var s := Settings.text_scale
	var lw := maxf(label_width, own_label_width())
	var h := maxf(PILL_H * s, Palette.mono().get_height(_font_px()))
	return Vector2((lw + GAP if lw > 0.0 else 0.0) + PILL_W * s, h)


## The state drawn now (KitState).
func state() -> StringName:
	return KitState.of(self)


func _draw() -> void:
	var st := state()
	var f := Palette.mono()
	var px := _font_px()
	if text != "":
		var base := (size.y + f.get_ascent(px) - f.get_descent(px)) * 0.5
		draw_string(f, Vector2(0, base), text, HORIZONTAL_ALIGNMENT_LEFT, -1, px, KitState.label_color(st))
	var pill := pill_rect()
	pill.position.y += KitState.lift(st)
	var r := pill.size.y * 0.5
	var on_fill := Palette.NET_CYAN if st != KitState.DISABLED else Palette.DISABLED
	var k := knob
	_pill(pill, r, Palette.TERMINAL_BG, KitState.edge_color(st, Palette.TEXT_MID))
	if k > 0.0:
		var filled := Rect2(pill.position, Vector2(lerpf(pill.size.y, pill.size.x, k), pill.size.y))
		_pill(filled, r, on_fill, on_fill)
	var kr := r - KNOB_INSET * Settings.text_scale
	var kc := Vector2(lerpf(pill.position.x + r, pill.end.x - r, k), pill.get_center().y)
	draw_circle(kc, kr, Palette.INK if k >= 0.5 else KitState.label_color(st))
	if k >= 0.5:
		StatIcon.draw(self, kc, kr * 0.75, StatIcon.CHECK, on_fill)
	if st == KitState.HOVER or st == KitState.PRESSED:
		draw_arc(kc, kr + 1.0, 0, TAU, 20, Color(Palette.TEXT_HI, UiTheme.GLOW_ALPHA * KitState.glow(st)), 2.0, true)
	KitState.draw_frame(self, Rect2(Vector2(0, KitState.lift(st)), size) if st == KitState.FOCUS else pill, st)


func _pill(rect: Rect2, r: float, fill: Color, edge: Color) -> void:
	draw_circle(Vector2(rect.position.x + r, rect.get_center().y), r, fill)
	draw_circle(Vector2(rect.end.x - r, rect.get_center().y), r, fill)
	draw_rect(Rect2(rect.position + Vector2(r, 0), Vector2(maxf(0.0, rect.size.x - r * 2.0), rect.size.y)), fill)
	draw_arc(Vector2(rect.position.x + r, rect.get_center().y), r, PI * 0.5, PI * 1.5, 12, edge, 1.0, true)
	draw_arc(Vector2(rect.end.x - r, rect.get_center().y), r, -PI * 0.5, PI * 0.5, 12, edge, 1.0, true)
	draw_line(rect.position + Vector2(r, 0), Vector2(rect.end.x - r, rect.position.y), edge, 1.0)
	draw_line(Vector2(rect.position.x + r, rect.end.y), rect.end - Vector2(r, 0), edge, 1.0)
