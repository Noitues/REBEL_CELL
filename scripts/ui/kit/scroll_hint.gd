class_name ScrollHint
extends Button
## "More below" (H21 #15: the HQ's BLACK MARKET sat under the fold with nothing to say so):
## a small tag with a double chevron at the foot of a ScrollContainer (centred), shown while there is
## more content below the view; pressing it scrolls on by most of a page. Mouse only (a
## pad scrolls by moving focus, follow_focus). View only.

## Share of a page one press scrolls.
const PAGE_STEP := 0.8
## Gap from the scroll view's bottom edge, where the tag sits centred (px; the autosave
## note has the bottom right corner).
const MARGIN := Vector2(0, 10)

var scroll: ScrollContainer


func _init(p_scroll: ScrollContainer) -> void:
	name = "ScrollHint"
	scroll = p_scroll
	text = "MORE BELOW"
	focus_mode = Control.FOCUS_NONE
	tooltip_text = UiTip.fold("There is more further down this page: scroll, or press this.")
	visible = false
	IconMark.attach(self, StatIcon.MORE, Palette.CELL_ACID)
	add_theme_color_override("font_color", Palette.CELL_ACID)
	pressed.connect(scroll_on)


func _ready() -> void:
	var bar := scroll.get_v_scroll_bar()
	bar.value_changed.connect(func(_v: float) -> void: refresh())
	bar.changed.connect(refresh)
	scroll.resized.connect(refresh)
	refresh.call_deferred()


## Whether the page has more below its view now.
func more_below() -> bool:
	var bar := scroll.get_v_scroll_bar()
	return bar.max_value - bar.page > 1.0 and bar.value < bar.max_value - bar.page - 1.0


## Shows or hides the tag and keeps it at the view's bottom right.
func refresh() -> void:
	if not is_instance_valid(scroll) or not scroll.is_inside_tree():
		return
	visible = more_below()
	size = get_combined_minimum_size()
	var r := scroll.get_global_rect()
	global_position = Vector2(r.get_center().x - size.x * 0.5, r.end.y - size.y - MARGIN.y)


## Scrolls the page on by most of a view.
func scroll_on() -> void:
	var bar := scroll.get_v_scroll_bar()
	scroll.scroll_vertical = int(minf(bar.max_value - bar.page, bar.value + bar.page * PAGE_STEP))
