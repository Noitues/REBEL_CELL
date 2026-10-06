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
## The share of the player's text scale the panel is built at now, and its detail level.
var mul: float = 1.0
var detail: int = 0
## True when even the last detail at the floor is taller than the room it was given.
var overflow: bool = false
var panel: Control = null

var _key: String = ""


func _get_minimum_size() -> Vector2:
	return panel.get_combined_minimum_size() if panel != null and is_instance_valid(panel) else Vector2.ZERO


func _notification(what: int) -> void:
	if what == NOTIFICATION_SORT_CHILDREN and panel != null and is_instance_valid(panel):
		panel.position = Vector2.ZERO
		panel.size = Vector2(size.x, maxf(size.y, panel.get_combined_minimum_size().y))


## Builds the panel to fit `width` x `room` (px); does nothing when nothing changed since.
func fit(width: float, room: float) -> void:
	var key := "%d|%d|%s|%.3f" % [roundi(width), roundi(room), str(details), Settings.text_scale]
	if key == _key and panel != null and is_instance_valid(panel):
		return
	_key = key
	overflow = true
	var last := 0
	for d in details:
		last = d
		var m := 1.0
		for _pass in HqLayout.FIT_PASSES:
			var need := _build(m, d, width)
			if need <= room + 0.5:
				overflow = false
				return
			if m <= floor_mul + 0.001:
				break
			m = maxf(floor_mul, m * room / maxf(need, 1.0))
		# Nothing fit at this detail: its floor build is measured once more below.
		if m > floor_mul + 0.001:
			if _build(floor_mul, d, width) <= room + 0.5:
				overflow = false
				return
	if panel == null or detail != last or not is_equal_approx(mul, floor_mul):
		_build(floor_mul, last, width)


## Builds the panel at `m` x the player's scale and `d`, lays it out at `width`; returns its
## settled height.
func _build(m: float, d: int, width: float) -> float:
	if panel != null and is_instance_valid(panel):
		remove_child(panel)
		panel.queue_free()
	var saved := Settings.text_scale
	Settings.text_scale = saved * m  # the one place the global is lent (restored at once)
	panel = builder.call(m, d) as Control
	Settings.text_scale = saved
	mul = m
	detail = d
	add_child(panel)
	update_minimum_size()
	rebuilt.emit()
	return settle(panel, width)


## Lays `root` out at `width` top-down (each container sorts, so wrapped labels know their
## width) and returns its height.
static func settle(root: Control, width: float) -> float:
	for _round in 2:
		root.size = Vector2(width, root.get_combined_minimum_size().y)
		_sort(root)
	return root.get_combined_minimum_size().y


static func _sort(n: Control) -> void:
	if n is Container:
		n.notification(Container.NOTIFICATION_SORT_CHILDREN)
	for ch in n.get_children():
		if ch is Control and (ch as Control).visible:
			_sort(ch as Control)
