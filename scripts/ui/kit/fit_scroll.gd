class_name FitScroll
extends VBoxContainer
## A panel's content that sizes to itself up to a maximum (ART_BIBLE §5.3): while it fits,
## the view is exactly as tall as the content (no empty band); past `max_height` it
## scrolls **inside** the panel, with the kit's ScrollHint ("MORE BELOW") in a room of its
## own under the view (it never covers a row) and the view ending above the first row it
## would cut (`ScrollHint.snap_rows`), so it never clips mid-row. Focus moves scroll the
## view (`follow_focus`, the pad path). View only.

## The view's least height when it scrolls (px at text scale 1.0): a view shorter than this
## shows too little to scroll through.
const MIN_VIEW := 96.0

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


func _fit() -> void:
	if scroll == null or content == null:
		return
	var h := content_height()
	if max_height > 0.0:
		h = minf(h, maxf(max_height, minf(h, MIN_VIEW * Settings.text_scale)))
	scroll.custom_minimum_size.y = ceilf(h)
	# The widest row sets the width (the view never scrolls sideways).
	scroll.custom_minimum_size.x = content.get_combined_minimum_size().x
	if hint != null and hint.is_inside_tree():
		hint.refresh()
