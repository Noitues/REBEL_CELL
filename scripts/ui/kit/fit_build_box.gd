class_name FitBuildBox
extends Container
## M14 BIG-TEXT: holds one panel built by `builder` and builds it again, smaller, until its
## whole height fits the room it is given (never clipped mid-line, and no Control.scale: the
## panel's rects are true). The builder runs with the text scale temporarily set to the player's
## scale times `mul`, so every font, margin and minimum the panel reads is the smaller one.
##
## `fit(width, room)` tries each detail level in `details` in order. At each it starts from the
## player's own scale and shrinks `mul` towards the level's floor (`floor_for`: never below
## `HqLayout.base_floor`, so the text is never smaller than at 1.0); the first level that fits
## wins. When none fits, the last level stays built at the floor (`overflow`).
## BIG-TEXT b (art director): past the floor a panel pages. A level code `fold(n, step)` is a fold
## in `n` pages (its builder details are `code + 1 .. code + n`, `page_of` / `pages_of` read them
## back); a fold fits only when every one of its pages fits at its floor, and the page shown is
## `page` (the owner's MORE / BACK). A paged panel wears a page `tab` (kept across rebuilds so it
## keeps the focus) sticking out of the panel's foot, turned with it (a tilted sheet); the box is
## that much taller while the tab shows. The result is a pure function of (width, room, details,
## page, text scale): the same inputs rebuild the same panel. View only.

## Emitted after `fit` built something new.
signal rebuilt

## (mul: float, detail: int) -> Control. Runs with Settings.text_scale scaled by `mul`.
var builder: Callable = Callable()
## The detail levels to try, most complete first (0 = the whole panel).
var details: Array[int] = [0]
## The smallest share of the player's text scale the whole panel (detail 0) may be built at; a
## page goes down to `HqLayout.base_floor` (the 1.0 size).
var floor_mul: float = HqLayout.FIT_FLOOR
## The page of a fold shown (0 = its first; clamped to the fold's pages).
var page: int = 0
## The share of the player's text scale the panel is built at now, its builder detail (a page's
## when folded) and the level that detail belongs to.
var mul: float = 1.0
var detail: int = 0
var level: int = 0
## True when even the last detail at the floor is taller than the room it was given.
var overflow: bool = false
var panel: Control = null
## BIG-TEXT b: the page tab under the panel's foot (null for none; shown by the owner), its x
## from the panel's left and how far its top tucks under the panel (px).
var tab: Control = null
var tab_x: float = 0.0
var tab_tuck: float = 0.0
## The global x the tab's left edge keeps right of, turned corners and all (a screen margin).
var tab_left_min: float = -INF

## The share a panel is being built at right now (1.0 outside a build): a builder that keys a choice off the
## text scale reads the player's through this (`Settings.text_scale` is the lent, smaller one).
static var building_mul: float = 1.0

var _key: String = ""
var _need: float = 0.0
## The last fit's rooms (whole, folded; px) and each detail's height at its last build (tests).
var last_rooms: Vector2 = Vector2.ZERO
var heights: Dictionary = {}


func _get_minimum_size() -> Vector2:
	var m := panel.get_combined_minimum_size() if panel != null and is_instance_valid(panel) else Vector2.ZERO
	return m + Vector2(0.0, tab_out())


## BIG-TEXT b: how far the page tab reaches below the panel (px; 0 while it is hidden).
func tab_out() -> float:
	if tab == null or not is_instance_valid(tab) or not tab.visible:
		return 0.0
	return maxf(tab.get_combined_minimum_size().y - tab_tuck, 0.0)


## BIG-TEXT b: shows or hides the page tab (and the room it takes under the panel).
func show_tab(on: bool) -> void:
	if tab != null and is_instance_valid(tab) and tab.visible != on:
		tab.visible = on
		update_minimum_size()
		queue_sort()


func _notification(what: int) -> void:
	if what == NOTIFICATION_SORT_CHILDREN and panel != null and is_instance_valid(panel):
		panel.position = Vector2.ZERO
		panel.size = Vector2(size.x, maxf(size.y - tab_out(), panel.get_combined_minimum_size().y))
		_place_tab()


## BIG-TEXT b: the tab hangs from the panel's foot at `tab_x`, turned with the panel (a sheet's tilt).
func _place_tab() -> void:
	if tab == null or not is_instance_valid(tab) or panel == null or not is_instance_valid(panel):
		return
	tab.size = tab.get_combined_minimum_size()
	tab.pivot_offset = Vector2.ZERO
	tab.rotation = panel.rotation
	tab.position = panel.get_transform() * Vector2(tab_x, panel.size.y - tab_tuck)
	if is_inside_tree() and tab_left_min > -INF:
		var xf := get_global_transform() * tab.get_transform()
		var left := INF
		for corner in [Vector2.ZERO, Vector2(tab.size.x, 0.0), Vector2(0.0, tab.size.y), tab.size]:
			left = minf(left, (xf * corner).x)
		if left < tab_left_min:
			tab.position.x += tab_left_min - left


## The smallest share of the player's scale detail level `d` may be built at (never below
## `HqLayout.base_floor`: the text is never smaller than at 1.0).
func floor_for(d: int) -> float:
	return maxf(floor_mul if d == 0 else 0.0, HqLayout.base_floor(Settings.text_scale))


## The level code of a fold in `n` pages (n 2..9) at step `step` (an owner's own variant: fewer
## rows, no strip); its pages' details are the code + 1 .. code + n.
static func fold(n: int, step: int = 0) -> int:
	return step * FOLD_STEP + n * FOLD_PAGES


## A detail's page (1-based; 0 for the whole panel) and its fold's page count (0 unfolded).
static func page_of(d: int) -> int:
	return d % FOLD_PAGES


static func pages_of(d: int) -> int:
	return (d % FOLD_STEP) / FOLD_PAGES


## A detail's step (`fold`).
static func step_of(d: int) -> int:
	return d / FOLD_STEP


## The level code's digits: pages count in tens, the step in hundreds.
const FOLD_PAGES := 10
const FOLD_STEP := 100


## The builder details of level `lv` (one for the whole panel; each page of a fold).
static func details_of(lv: int) -> Array[int]:
	var out: Array[int] = []
	var n := pages_of(lv)
	if n == 0:
		out.append(lv)
	for i in n:
		out.append(lv + i + 1)
	return out


## Builds the panel to fit `width` x `room` (px); `room_folded` is the room a folded level
## (any detail but 0) has, when something beside it takes some (the MORE tab). Does nothing when
## nothing changed since.
func fit(width: float, room: float, room_folded: float = -1.0) -> void:
	var rf := room if room_folded < 0.0 else room_folded
	var key := "%d|%d|%d|%s|%d|%.3f" % [roundi(width), roundi(room), roundi(rf), str(details), page, Settings.text_scale]
	if key == _key and panel != null and is_instance_valid(panel):
		return
	_key = key
	overflow = true
	last_rooms = Vector2(room, rf)
	heights.clear()
	for lv in details:
		var r := room if lv == 0 else rf
		var pages := details_of(lv)
		var d: int = pages[clampi(page, 0, pages.size() - 1)]
		# A fold fits only when each of its other pages fits at its floor (the 1.0 size).
		var others_fit := true
		for p in pages:
			if p != d and _build(floor_for(p), p, width) > r + 0.5:
				others_fit = false
				break
		if not others_fit:
			continue
		level = lv
		var fl := floor_for(d)
		var m := 1.0
		for _pass in HqLayout.FIT_PASSES:
			if _build(m, d, width) <= r + 0.5:
				overflow = false
				return
			if m <= fl + 0.001:
				break
			m = maxf(fl, minf(m * r / maxf(_need, 1.0), m - HqLayout.FIT_STEP_MIN))
		if m > fl + 0.001 and _build(fl, d, width) <= r + 0.5:
			overflow = false
			return
	# Nothing fit: the last level stays built at its floor.
	level = details[details.size() - 1]
	var last_pages := details_of(level)
	var last: int = last_pages[clampi(page, 0, last_pages.size() - 1)]
	if panel == null or detail != last or not is_equal_approx(mul, floor_for(last)):
		_build(floor_for(last), last, width)


## Builds the panel at `m` x the player's scale and `d`, lays it out at `width`; returns its
## settled height.
func _build(m: float, d: int, width: float) -> float:
	if panel != null and is_instance_valid(panel):
		remove_child(panel)
		panel.queue_free()
	var saved := Settings.text_scale
	Settings.text_scale = saved * m  # the one place the global is lent (restored at once)
	building_mul = m
	panel = builder.call(m, d) as Control
	Settings.text_scale = saved
	building_mul = 1.0
	mul = m
	detail = d
	add_child(panel)
	update_minimum_size()
	rebuilt.emit()
	_need = settle(panel, width)
	heights[d] = _need
	if tab != null and is_instance_valid(tab):
		move_child(tab, 0)  # under the panel: the sheet covers the tab's tucked top
	return _need


## Lays `root` out at `width` top-down (each container sorts, so wrapped labels know their
## width) and returns its height.
static func settle(root: Control, width: float) -> float:
	for _round in SETTLE_ROUNDS:
		root.size = Vector2(width, root.get_combined_minimum_size().y)
		_sort(root)
		_invalidate(root)  # wrapped labels know their width now: their heights are stale up the tree
	root.size = Vector2(width, root.get_combined_minimum_size().y)
	return root.get_combined_minimum_size().y


## Passes of (sort down, refresh minimums up) `settle` makes.
const SETTLE_ROUNDS := 3


static func _sort(n: Control) -> void:
	if n is Container:
		n.notification(Container.NOTIFICATION_SORT_CHILDREN)
	for ch in n.get_children():
		if ch is Control and (ch as Control).visible:
			_sort(ch as Control)


static func _invalidate(n: Control) -> void:
	for ch in n.get_children():
		if ch is Control and (ch as Control).visible:
			_invalidate(ch as Control)
	n.update_minimum_size()
