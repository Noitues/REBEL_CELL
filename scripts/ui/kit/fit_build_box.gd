class_name FitBuildBox
extends Container
## M14 BIG-TEXT: holds one panel built by `builder` and builds it again, smaller, until its
## whole height fits the room it is given (never clipped mid-line, and no Control.scale: the
## panel's rects are true). The builder runs with the text scale temporarily set to the player's
## scale times `mul`, so every font, margin and minimum the panel reads is the smaller one.
##
## `fit(width, room)` tries each detail level in `details` in order. At each it starts from the
## player's own scale and shrinks `mul` towards `HqLayout.FIT_FLOOR` (never below it); the first
## level that fits wins. When none fits, the last level stays built at the floor (`overflow`).
## The result is a pure function of (width, room, details, text scale): the same inputs rebuild
## the same panel. View only.

## Emitted after `fit` built something new.
signal rebuilt

## (mul: float, detail: int) -> Control. Runs with Settings.text_scale scaled by `mul`.
var builder: Callable = Callable()
## The detail levels to try, most complete first (0 = the whole panel).
var details: Array[int] = [0]
## The smallest share of the player's text scale a panel may be built at.
var floor_mul: float = HqLayout.FIT_FLOOR
## Per-detail floors (detail -> share) where a folded level may go lower than `floor_mul`.
var floors: Dictionary = {}
## The share of the player's text scale the panel is built at now, and its detail level.
var mul: float = 1.0
var detail: int = 0
## True when even the last detail at the floor is taller than the room it was given.
var overflow: bool = false
var panel: Control = null

## The share a panel is being built at right now (1.0 outside a build): a builder that keys a choice off the
## text scale reads the player's through this (`Settings.text_scale` is the lent, smaller one).
static var building_mul: float = 1.0

var _key: String = ""
var _need: float = 0.0


func _get_minimum_size() -> Vector2:
	return panel.get_combined_minimum_size() if panel != null and is_instance_valid(panel) else Vector2.ZERO


func _notification(what: int) -> void:
	if what == NOTIFICATION_SORT_CHILDREN and panel != null and is_instance_valid(panel):
		panel.position = Vector2.ZERO
		panel.size = Vector2(size.x, maxf(size.y, panel.get_combined_minimum_size().y))


## The smallest share of the player's scale detail level `d` may be built at.
func floor_for(d: int) -> float:
	return float(floors.get(d, floor_mul))


## Builds the panel to fit `width` x `room` (px); `room_folded` is the room a folded level
## (any detail but 0) has, when something beside it takes some (the MORE tab). Does nothing when
## nothing changed since.
func fit(width: float, room: float, room_folded: float = -1.0) -> void:
	var rf := room if room_folded < 0.0 else room_folded
	var key := "%d|%d|%d|%s|%.3f" % [roundi(width), roundi(room), roundi(rf), str(details), Settings.text_scale]
	if key == _key and panel != null and is_instance_valid(panel):
		return
	_key = key
	overflow = true
	for d in details:
		var r := room if d == 0 else rf
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
	var last: int = details[details.size() - 1]
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
