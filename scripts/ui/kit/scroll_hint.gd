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
## ART-0 F (ported from art-pass WF fc477fc): a view taller than this (px at text scale 1.0)
## is a pre-layout measure, not a page (FitScroll.MAX_VIEW_PX).
const DEGENERATE_PX := 4096.0


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
	_base_min = scroll.custom_minimum_size.y
	var box := scroll.get_parent() as BoxContainer
	if box != null and room == null:
		room = Control.new()
		room.name = "ScrollHintRoom"
		room.mouse_filter = Control.MOUSE_FILTER_IGNORE
		box.add_child(room)
		box.move_child(room, scroll.get_index() + 1)
	var bar := scroll.get_v_scroll_bar()
	bar.value_changed.connect(func(_v: float) -> void: refresh())
	# ART-6 3A: an outer scroll view moving this one shows or hides the tag (in_outer_views).
	var up := scroll.get_parent()
	while up != null:
		if up is ScrollContainer:
			(up as ScrollContainer).get_v_scroll_bar().value_changed.connect(refresh.unbind(1))
		up = up.get_parent()
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
	# ART-1 1A: a view held at its least height (a list inside a scrolling column: the raid's
	# NODE ORDERS at 2.0) does not give the room out of its own height, the column grows
	# instead; its page without the room is that least height. Measured against page + room
	# the two states disagreed (room -> no overflow -> no room -> overflow) and the layout
	# flipped every frame until the process crashed (signal 11, with MSDF metrics).
	if reserved > 0.0 and _base_min > 0.0 and scroll.size.y <= scroll.custom_minimum_size.y + 0.5:
		return bar.max_value > _base_min + 1.0
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
## What the snap reserve was worked out for, how often and when last (see _refresh).
var _snap_key: Array = []
var _snap_passes: int = 0
var _snap_frame: int = -1
## The most times a content's snap is worked out (its layout settles in a pass or two).
const SNAP_PASSES := 3
## ANIM-R6 C8: the view's own least height (its custom minimum when the tag came).
var _base_min: float = 0.0
## ANIM-R6 C8: the most times one content's snap is worked out in all (its height changes).
const SNAP_PASSES_MAX := 12
var _snap_total: int = 0


func _refresh() -> void:
	size = get_combined_minimum_size()
	# ART-0 F (ported from art-pass WF): a view not laid out yet (a pre-layout height past any
	# real page) says nothing about what is below; its resize calls back in here once it is.
	if degenerate_view():
		visible = false
		return
	if room != null and is_instance_valid(room):
		# ANIM-R3 B13: the snap is worked out at most once a frame and SNAP_PASSES times per
		# content (a new page's content, or the text size), never while the room is still
		# being laid out: the room it sets can move the rows it measured (a scroll bar coming
		# and going rewraps them), and an unbounded snap made the layout chase itself through
		# the deferred calls until the message queue ran out (the sweep tests crashed).
		if snap_rows and scroll.scroll_vertical == 0 and scroll.get_child_count() > 0:
			var content := scroll.get_child(0)
			# ANIM-R6 C8: the content's height is part of the key (a row that wraps later, a
			# withdraw row that comes, re-lays it out: the snap ran out on the first layout and
			# YOUR NODES cut its last row at 1.6), and the content resizing refreshes the tag;
			# SNAP_PASSES_MAX in all per content keeps it bounded.
			if content is Control and not (content as Control).resized.is_connected(refresh):
				(content as Control).resized.connect(refresh)
			var key := [content.get_instance_id(), Settings.text_scale, roundi((content as Control).size.y) if content is Control else 0]
			if key != _snap_key:
				if _snap_key.is_empty() or _snap_key[0] != key[0] or _snap_key[1] != key[1]:
					_snap_total = 0
				_snap_key = key
				_snap_passes = 0
			var frame := Engine.get_process_frames()
			if _snap_passes < SNAP_PASSES and _snap_total < SNAP_PASSES_MAX and frame != _snap_frame and is_equal_approx(room.size.y, room.custom_minimum_size.y):
				_snap_frame = frame
				_snap_passes += 1
				_snap_total += 1
				snap_reserve = cut_row_reserve()
			elif _snap_passes < SNAP_PASSES and _snap_total < SNAP_PASSES_MAX and is_inside_tree() \
					and not get_tree().process_frame.is_connected(refresh):
				# Not worked out now (this frame's done, or the room is still laying out): on the
				# next frame (never a deferred call in this one: the layout would chase itself).
				get_tree().process_frame.connect(refresh, CONNECT_ONE_SHOT)
		var want := size.y + MARGIN.y * 2.0 + snap_reserve if overflows() else 0.0
		if not is_equal_approx(room.custom_minimum_size.y, want):
			room.custom_minimum_size.y = want
		# ANIM-R6 C8: a view held at its least height (YOUR NODES at 1.6) gives the snap's room
		# out of that height, so it ends above the row it would cut instead of growing its window.
		var least := maxf(0.0, _base_min - (snap_reserve if want > 0.0 else 0.0))
		if not is_equal_approx(scroll.custom_minimum_size.y, least):
			scroll.custom_minimum_size.y = least
	var r := scroll.get_global_rect()
	if room != null and is_instance_valid(room) and room.custom_minimum_size.y > 0.0:
		global_position = Vector2(r.get_center().x - size.x * 0.5, room.get_global_rect().position.y + MARGIN.y)
	else:
		global_position = Vector2(r.get_center().x - size.x * 0.5, r.end.y - size.y - MARGIN.y)
	visible = more_below() and in_outer_views()


## ART-6 3A (M14 resume): false while the tag's spot is scrolled out of an outer scroll view
## holding this one (YOUR NETWORK's list inside the raid setup's scrolling column): the tag
## is not in that view's content, so it drew over what sits below the view (START DEFENSE).
## The outer view's own tag says there is more.
func in_outer_views() -> bool:
	var spot := Rect2(global_position, size)
	var up := scroll.get_parent()
	while up != null:
		if up is ScrollContainer and not (up as ScrollContainer).get_global_rect().grow(0.5).encloses(spot):
			return false
		up = up.get_parent()
	return true


## ART-0 F: the view's own least height is now `h` (px): a FitScroll sizing its view to its
## content says so here, so the snap's room comes out of that height (ANIM-R6 C8) instead of
## the hint holding the view at the height it had when the tag came.
func set_view_min(h: float) -> void:
	_base_min = h
	var least := maxf(0.0, h - (snap_reserve if room != null and is_instance_valid(room) and room.custom_minimum_size.y > 0.0 else 0.0))
	if not is_equal_approx(scroll.custom_minimum_size.y, least):
		scroll.custom_minimum_size.y = least


## ANIM-R3 B13: how far above the view's foot the first row it cuts starts (0 when no row
## is cut): the rows are the children of box containers inside the content, each shorter
## than ROW_SHARE of the view; the smallest one crossing the foot decides.
func cut_row_reserve() -> float:
	if scroll.get_child_count() == 0:
		return 0.0
	var view := scroll.get_global_rect()
	# The view's foot as it would be with no snap reserve: the view and its room share a
	# fixed height, so the foot is their bottom less the tag's own room (whatever reserve the
	# room holds now).
	var tag_room := size.y + MARGIN.y * 2.0 if room.custom_minimum_size.y > 0.0 else 0.0
	var foot := view.end.y + room.size.y - tag_room
	var best := 0.0
	var best_h := INF
	for n in scroll.get_child(0).find_children("*", "Control", true, false):
		var c := n as Control
		# ANIM-R6 C8: a flow's lines count too (a node's "Withdraw Turret | Withdraw ICE Lock"
		# buttons in YOUR NODES were cut in half: their flow, taller than a row, was skipped).
		if not c.is_visible_in_tree() or not (c.get_parent() is BoxContainer or c.get_parent() is FlowContainer):
			continue
		var r := c.get_global_rect()
		# ANIM-R6 C8: a row's share of the view as it is with no snap (the snap shrinks the view:
		# its rows then read as too tall, the next pass found no cut and the view grew back).
		if r.size.y <= 0.0 or r.size.y > (foot - view.position.y) * ROW_SHARE:
			continue
		if r.position.y < foot and r.end.y > foot + 0.5 and r.position.y > view.position.y and r.size.y < best_h:
			best_h = r.size.y
			best = foot - r.position.y
	return best


## ANIM-R6 C15: the view's content changed in place (a page scroll whose host stays while its
## pages come and go): the snap is worked out afresh for it.
func reset_snap() -> void:
	_snap_key = []
	_snap_total = 0
	snap_reserve = 0.0
	refresh.call_deferred()


## Scrolls the page on by most of a view.
func scroll_on() -> void:
	var bar := scroll.get_v_scroll_bar()
	scroll.scroll_vertical = int(minf(bar.max_value - bar.page, bar.value + bar.page * PAGE_STEP))


## ART-0 F (ported from art-pass WF): true while the view has no real layout: a height or
## scroll range that isn't finite or is past DEGENERATE_PX at the text scale (a wrapped label
## at width 0 measures thousands of px tall for a frame).
func degenerate_view() -> bool:
	var bar := scroll.get_v_scroll_bar()
	var limit := DEGENERATE_PX * Settings.text_scale
	return not is_finite(scroll.size.y) or scroll.size.y > limit or not is_finite(bar.max_value)
