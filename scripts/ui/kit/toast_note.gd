class_name ToastNote
extends PanelContainer
## A short-lived note at the foot of the screen for what the player must see once (H20:
## the system log is an optional record, so refusals, saves and unlocks can't live only
## there): pink edge for a refusal, acid for news. One per screen (a new one replaces
## it); ignores the mouse and focus; gone after `toast_note_hold`'s duration (a reading
## time: reduce effects and a faster speed never shorten it; ANIM-R6 B7: a slower speed
## lengthens it, `hold_seconds`). View only.

const HOLD_MOTION := &"toast_note_hold"
## Gap to the screen's bottom edge (px).
const BOTTOM_GAP := 18.0
## The least gap to the screen's side edges (px).
const SIDE_GAP := 24.0
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
		host.get_tree().create_timer(hold_seconds()).timeout.connect(t.queue_free)
	return t


## ANIM-R6 B7: how long a note stays (s): `toast_note_hold` at the motion speed when that is
## slower (a slowed-down capture or a slow speed setting holds the words longer, as every
## other motion), never shorter than its raw duration (a raid at 4x never cuts the reading
## time; reduce effects neither).
static func hold_seconds() -> float:
	var e := Motion.entry(HOLD_MOTION)
	if e == null:
		return 0.0
	return maxf(e.duration, Motion.seconds(HOLD_MOTION))


func _place() -> void:
	var host := get_parent() as Control
	if host == null:
		return
	# ANIM-R1 M10: never wider than the screen (less its margins): a long refusal wraps,
	# whole, instead of running off the edges.
	var room := maxf(1.0, host.size.x - SIDE_GAP * 2.0)
	size = get_combined_minimum_size()
	if size.x > room:
		label.autowrap_mode = TextServer.AUTOWRAP_WORD_SMART
		label.custom_minimum_size.x = room - (size.x - label.get_combined_minimum_size().x)
		size = Vector2.ZERO
		size = get_combined_minimum_size()
		# ANIM-R2 E9: a wrapped label reports its height a frame late (a drag's refusal showed
		# its first line only, "...has no f"): take the size again then.
		_resize.call_deferred()
	_put(host)


func _resize() -> void:
	var host := get_parent() as Control
	if host == null:
		return
	size = Vector2.ZERO
	size = get_combined_minimum_size()
	_put(host)


func _put(host: Control) -> void:
	position = Vector2(clampf((host.size.x - size.x) * 0.5, 0.0, maxf(0.0, host.size.x - size.x)), host.size.y - size.y - BOTTOM_GAP)


## True when every line of the note's words shows (tests).
func whole() -> bool:
	return label.get_line_count() <= label.get_visible_line_count() and size.y + 0.5 >= label.get_combined_minimum_size().y
