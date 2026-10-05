class_name FitScroll
extends VBoxContainer
## A panel's content that sizes to itself up to a maximum (ART_BIBLE §5.3): while it fits,
## the view is exactly as tall as the content (no empty band); past `max_height` it
## scrolls **inside** the panel, with the kit's ScrollHint ("MORE BELOW") in a room of its
## own under the view (it never covers a row) and the view ending above the first row it
## would cut (`ScrollHint.snap_rows`), so it never clips mid-row. Focus moves scroll the
## view (`follow_focus`, the pad path). View only.
## ART-0 F: ported from art-pass (W8a d91a26f, its pre-layout guards from WF fc477fc) onto
## main's ScrollHint (`set_view_min`). The shared panels adopt it when ART-4 / ART-10 restyle
## them; today it is the kit piece and its guards.

## The view's least height when it scrolls (px at text scale 1.0): a view shorter than this
## shows too little to scroll through.
const MIN_VIEW := 96.0
## Art pass WF: the tallest the view ever gets (px at text scale 1.0), capped or not, and the
## height past which a measure counts as pre-layout (see degenerate). Far below the GPU's
## texture limit that a glass blur or a bake of the panel would hit.
const MAX_VIEW_PX := 4096.0
## How many frames a pre-layout measure is waited out before it is taken (clamped).
const DEGENERATE_FRAMES := 3

var scroll: ScrollContainer
var hint: ScrollHint
var content: Control
## The tallest the view gets (px); 0 = no cap (it always sizes to the content).
var max_height: float = 0.0:
	set(v):
		max_height = maxf(0.0, v)
		_fit()


func _init(p_content: Control, p_max_height: float = 0.0) -> void:
	name = "FitScroll"
	add_theme_constant_override("separation", 0)
	scroll = ScrollContainer.new()
	scroll.name = "Scroll"
	scroll.horizontal_scroll_mode = ScrollContainer.SCROLL_MODE_DISABLED
	scroll.follow_focus = true
	scroll.size_flags_vertical = Control.SIZE_EXPAND_FILL
	add_child(scroll)
	content = p_content
	content.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	scroll.add_child(content)
	content.minimum_size_changed.connect(_fit)
	hint = ScrollHint.new(scroll)
	hint.snap_rows = true
	# The hint's room under the view, made here (the hint would add it while this box is
	# still setting up its children).
	var room := Control.new()
	room.name = "ScrollHintRoom"
	room.mouse_filter = Control.MOUSE_FILTER_IGNORE
	add_child(room)
	hint.room = room
	# Top level: no container lays the tag out (it places itself in its room).
	hint.top_level = true
	add_child(hint)
	max_height = p_max_height


## The content's own height (px).
func content_height() -> float:
	return content.get_combined_minimum_size().y


## True when the content is taller than the view (it scrolls).
func overflowing() -> bool:
	return max_height > 0.0 and content_height() > max_height + 0.5


## Art pass WF: true when the content's height is a pre-layout measure, not a real one (a
## wrapped label at width 0 wraps one word per line and measures thousands of px for a
## frame): taller than MAX_VIEW_PX at the text scale.
func degenerate(h: float) -> bool:
	return not is_finite(h) or h > MAX_VIEW_PX * Settings.text_scale


func _fit() -> void:
	if scroll == null or content == null:
		return
	var h := content_height()
	if degenerate(h):
		# Art pass WF: never take a pre-layout height. Keep the last good view (or the least
		# scrolling one) and measure again once the layout has given the rows their width,
		# up to DEGENERATE_FRAMES times; past that the height is real and only clamped.
		if _degenerate_frames < DEGENERATE_FRAMES:
			_degenerate_frames += 1
			h = _last_good if _last_good > 0.0 else MIN_VIEW * Settings.text_scale
			_refit_next_frame()
		else:
			h = MAX_VIEW_PX * Settings.text_scale
	else:
		_degenerate_frames = 0
		_last_good = h
	if max_height > 0.0:
		h = minf(h, maxf(max_height, minf(h, MIN_VIEW * Settings.text_scale)))
	var view_h := ceilf(minf(h, MAX_VIEW_PX * Settings.text_scale))
	if hint != null and hint.is_inside_tree():
		# ART-0 F: main's ScrollHint holds the view at its own least height (ANIM-R6 C8); the
		# hint takes the new height as that least height (its snap room comes out of it).
		hint.set_view_min(view_h)
	else:
		scroll.custom_minimum_size.y = view_h
	# The widest row sets the width (the view never scrolls sideways).
	scroll.custom_minimum_size.x = content.get_combined_minimum_size().x
	if hint != null and hint.is_inside_tree():
		hint.refresh()


## The last height measured outside a degenerate frame (px; 0 before the first).
var _last_good: float = 0.0
## Degenerate measures in a row (see _fit).
var _degenerate_frames: int = 0
var _refit_queued: bool = false


func _refit_next_frame() -> void:
	if _refit_queued or not is_inside_tree():
		return
	_refit_queued = true
	# A method on the frame signal, never a lambda (the frame-lambda rule).
	get_tree().process_frame.connect(_refit, CONNECT_ONE_SHOT)


func _refit() -> void:
	_refit_queued = false
	_fit()


func _exit_tree() -> void:
	if _refit_queued and get_tree().process_frame.is_connected(_refit):
		get_tree().process_frame.disconnect(_refit)
	_refit_queued = false
