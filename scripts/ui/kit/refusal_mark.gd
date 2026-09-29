class_name RefusalMark
extends Control
## ART_BIBLE §6 "Error / refused" for any control, including theme-styled native Buttons:
## a `HARM` outline flash over the control and a no-entry mark on its corner (STYLE_GUIDE
## 5.4), for the `button_refused` entry's seconds, then gone. With a reason it also pops the
## one toast (§6.7) beside the control. Ignores the mouse and focus; never resizes its
## control. Kit components draw the same look themselves (KitState.draw_frame). View only.

const NODE_NAME := "RefusalMark"


## Flashes the refused state on `target`; `reason` (translated) also shows as a refusal
## toast anchored to it. Returns the mark (a second refusal restarts the one there).
static func flash(target: Control, reason: String = "") -> RefusalMark:
	var m := target.get_node_or_null(NODE_NAME) as RefusalMark
	if m == null:
		m = RefusalMark.new()
		target.add_child(m)
	m.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	KitState.refuse(m)
	var e := Motion.entry(KitState.REFUSED_MOTION)
	if m._end != null and m._end.is_valid():
		m._end.kill()
	if m.is_inside_tree() and e != null:
		m._end = m.create_tween()
		m._end.tween_interval(e.duration)
		m._end.tween_callback(m.queue_free)
	if reason != "":
		var host := Toast.host_of(target)
		if host != null:
			Toast.pop_on(host, reason, true, target)
	return m


## The mark on `target` now (null when none).
static func of(target: Control) -> RefusalMark:
	return target.get_node_or_null(NODE_NAME) as RefusalMark


var _end: Tween = null


func _init() -> void:
	name = NODE_NAME
	mouse_filter = Control.MOUSE_FILTER_IGNORE
	focus_mode = Control.FOCUS_NONE


func _draw() -> void:
	KitState.draw_frame(self, Rect2(Vector2.ZERO, size), KitState.REFUSED)
