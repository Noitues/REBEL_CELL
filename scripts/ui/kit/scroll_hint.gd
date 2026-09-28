class_name ScrollHint
extends Button
## "More below" (H21 #15: the HQ's BLACK MARKET sat under the fold with nothing to say so):
## a small tag with a double chevron at the foot of a ScrollContainer (centred), shown while there is
## more content below the view; pressing it scrolls on by most of a page. Mouse only (a
## pad scrolls by moving focus, follow_focus). View only.
## H22 #10: the tag never covers a control. It sits in a room of its own under the scroll
## view (`room`, a strip inserted after the ScrollContainer in its box container), outside
## the scrolling content: while the content overflows, the strip takes the tag's height
## and the view ends above it, so a Loadout button or a Grid row is never under the tag.

## Share of a page one press scrolls.
const PAGE_STEP := 0.8
## Gap between the tag and the room's edges (px; the autosave note has the bottom right
## corner).
const MARGIN := Vector2(0, 4)

var scroll: ScrollContainer
## The strip under the scroll view the tag sits in (null when the scroll's parent is not a
## box container: the tag then sits at the view's foot, as before H22).
var room: Control = null
## ANIM-R3 B13: when on, the view (at the top of its content) ends above the first list row
## it would cut (a row of a box container, shorter than ROW_SHARE of the view): at 1.6 the
## Grid's RUNS OPEN NOW list ended in a half-drawn row.
var snap_rows: bool = false
## The extra room the snap keeps (px; worked out at the top of the content, kept while it
## scrolls so the view never jumps).
var snap_reserve: float = 0.0
const ROW_SHARE := 1.0 / 3.0


func _init(p_scroll: ScrollContainer) -> void:
	name = "ScrollHint"
	scroll = p_scroll
	TextDb.shown_as_given(self)  # H24 S4: translated here, shown as given
	text = tr("MORE BELOW")
	focus_mode = Control.FOCUS_NONE
	tooltip_text = UiTip.fold(tr("There is more further down this page: scroll, or press this."))
	visible = false
	IconMark.attach(self, StatIcon.MORE, Palette.CELL_ACID)
	add_theme_color_override("font_color", Palette.CELL_ACID)
	pressed.connect(scroll_on)


func _ready() -> void:
	var box := scroll.get_parent() as BoxContainer
	if box != null and room == null:
		room = Control.new()
		room.name = "ScrollHintRoom"
		room.mouse_filter = Control.MOUSE_FILTER_IGNORE
		box.add_child(room)
		box.move_child(room, scroll.get_index() + 1)
	var bar := scroll.get_v_scroll_bar()
	bar.value_changed.connect(func(_v: float) -> void: refresh())
	bar.changed.connect(refresh)
	scroll.resized.connect(refresh)
	if room != null:
		room.resized.connect(refresh)
	refresh.call_deferred()


func _exit_tree() -> void:
	if room != null and is_instance_valid(room):
		room.queue_free()
	room = null


## Whether the page has more below its view now.
func more_below() -> bool:
	var bar := scroll.get_v_scroll_bar()
	return bar.max_value - bar.page > 1.0 and bar.value < bar.max_value - bar.page - 1.0


## Whether the content is taller than the view and the room together (the room is kept
## while it is, so the view does not jump as the tag comes and goes).
func overflows() -> bool:
	var bar := scroll.get_v_scroll_bar()
	var reserved := room.custom_minimum_size.y if room != null else 0.0
	return bar.max_value > bar.page + reserved + 1.0


## Shows or hides the tag and keeps it centred under the view (in its room).
func refresh() -> void:
	# ANIM-R3 B13: a room change resizes the view, which calls back in here; one pass at a
	# time (the snap measures the laid-out view on the next call).
	if _refreshing or not is_instance_valid(scroll) or not scroll.is_inside_tree():
		return
	_refreshing = true
	_refresh()
	_refreshing = false


var _refreshing: bool = false


func _refresh() -> void:
	size = get_combined_minimum_size()
	if room != null and is_instance_valid(room):
		if snap_rows and scroll.scroll_vertical == 0 and is_equal_approx(room.size.y, room.custom_minimum_size.y):
			snap_reserve = cut_row_reserve()
		var want := size.y + MARGIN.y * 2.0 + snap_reserve if overflows() else 0.0
		if not is_equal_approx(room.custom_minimum_size.y, want):
			room.custom_minimum_size.y = want
	visible = more_below()
	var r := scroll.get_global_rect()
	if room != null and is_instance_valid(room) and room.custom_minimum_size.y > 0.0:
		global_position = Vector2(r.get_center().x - size.x * 0.5, room.get_global_rect().position.y + MARGIN.y)
	else:
		global_position = Vector2(r.get_center().x - size.x * 0.5, r.end.y - size.y - MARGIN.y)


## ANIM-R3 B13: how far above the view's foot the first row it cuts starts (0 when no row
## is cut): the rows are the children of box containers inside the content, each shorter
## than ROW_SHARE of the view; the smallest one crossing the foot decides.
func cut_row_reserve() -> float:
	if scroll.get_child_count() == 0:
		return 0.0
	var view := scroll.get_global_rect()
	# The view's foot as it would be with no snap reserve (the reserve itself moves it; the
	# room is laid out: the caller checks).
	var foot := view.end.y + (snap_reserve if room.custom_minimum_size.y > 0.0 else 0.0)
	var best := 0.0
	var best_h := INF
	for n in scroll.get_child(0).find_children("*", "Control", true, false):
		var c := n as Control
		if not c.is_visible_in_tree() or not (c.get_parent() is BoxContainer):
			continue
		var r := c.get_global_rect()
		if r.size.y <= 0.0 or r.size.y > view.size.y * ROW_SHARE:
			continue
		if r.position.y < foot and r.end.y > foot + 0.5 and r.position.y > view.position.y and r.size.y < best_h:
			best_h = r.size.y
			best = foot - r.position.y
	return best


## Scrolls the page on by most of a view.
func scroll_on() -> void:
	var bar := scroll.get_v_scroll_bar()
	scroll.scroll_vertical = int(minf(bar.max_value - bar.page, bar.value + bar.page * PAGE_STEP))
