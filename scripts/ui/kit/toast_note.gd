class_name ToastNote
extends PanelContainer
## A short-lived note at the foot of the screen for what the player must see once (H20:
## the system log is an optional record, so refusals, saves and unlocks can't live only
## there): pink edge for a refusal, acid for news. One per screen (a new one replaces
## it); ignores the mouse and focus; gone after `toast_note_hold`'s duration (read raw:
## it is how long words stay to be read, so reduce effects and a raid's speed never
## shorten it). View only.

const HOLD_MOTION := &"toast_note_hold"
## Gap to the screen's bottom edge (px).
const BOTTOM_GAP := 18.0
const NODE_NAME := "Toast"

var label: Label


func _init(text: String = "", warn: bool = false) -> void:
	name = NODE_NAME
	mouse_filter = Control.MOUSE_FILTER_IGNORE
	focus_mode = Control.FOCUS_NONE
	var style := UiTheme.box(Color(0.02, 0.03, 0.08, 0.96), Palette.CELL_PINK if warn else Palette.CELL_ACID, 1, 16, 8)
	style.border_width_left = 4
	style.shadow_color = Palette.SHADOW
	style.shadow_size = 8
	add_theme_stylebox_override("panel", style)
	label = Label.new()
	label.text = UiTip.fold(text)
	label.mouse_filter = Control.MOUSE_FILTER_IGNORE
	label.add_theme_color_override("font_color", Palette.PAPER)
	add_child(label)


## Shows `text` on `host` (a full-screen scene), replacing a note already there.
static func show_on(host: Control, text: String, warn: bool = false) -> ToastNote:
	var old := host.get_node_or_null(NODE_NAME)
	if old != null:
		host.remove_child(old)
		old.queue_free()
	var t := ToastNote.new(text, warn)
	host.add_child(t)
	t._place.call_deferred()
	if host.is_inside_tree():
		# Bound to the note itself: a note already replaced or freed drops the call.
		host.get_tree().create_timer(Motion.entry(HOLD_MOTION).duration).timeout.connect(t.queue_free)
	return t


func _place() -> void:
	var host := get_parent() as Control
	if host == null:
		return
	size = get_combined_minimum_size()
	position = Vector2((host.size.x - size.x) * 0.5, host.size.y - size.y - BOTTOM_GAP)
