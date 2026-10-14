class_name PressDip
extends RefCounted
## Plan 1 ANIM-FLOW M10: press feedback and entrance motion for the plain buttons of menus,
## dialogs, the loot sheet and the run-end pages. View only; no game state.
##
## `attach(root)` makes every plain button under `root` dip on a press (`press_dip`: scale to the
## entry's amplitude about its centre, back on release) so a click is acknowledged at once.
## Buttons that animate their own press (stickers, drips, card faces, menu chips) are left alone.
## `rise(rows)` brings rows in one after another (`menu_page_in`: fade, the entry's delay between
## rows). Reduce effects and headless: no dip, rows at rest at once.

## Node meta marking a button already attached (one connection each).
const META_ATTACHED := &"press_dip_attached"
## Node meta a button sets to opt out (its own press motion).
const META_OFF := &"press_dip_off"


## True when `b` takes the dip: a plain button, not one with a press of its own.
static func takes_dip(b: BaseButton) -> bool:
	if b.has_meta(META_OFF):
		return false
	return not (b is HoloSticker or b is DripButton or b is RaidSticker or b is MenuChip or b is ZineCard)


## Attaches the dip to every plain button under `root` (and `root` itself); returns how many are
## attached now. Safe to call again on the same tree.
static func attach(root: Node) -> int:
	var n := 0
	if root is BaseButton and takes_dip(root as BaseButton):
		n += 1 if _attach_one(root as BaseButton) else 0
	for c in root.get_children():
		n += attach(c)
	return n


static func _attach_one(b: BaseButton) -> bool:
	if b.has_meta(META_ATTACHED):
		return false
	b.set_meta(META_ATTACHED, true)
	b.button_down.connect(_down.bind(b))
	b.button_up.connect(_up.bind(b))
	return true


static func _down(b: BaseButton) -> void:
	if not is_instance_valid(b) or b.disabled or not Motion.live(&"press_dip"):
		return
	b.pivot_offset = b.size * 0.5
	var k := Motion.amplitude(&"press_dip")
	Motion.run(&"press_dip", b, ^"scale", Vector2.ONE * k)


static func _up(b: BaseButton) -> void:
	if not is_instance_valid(b) or not Motion.live(&"press_dip"):
		return
	Motion.run(&"press_dip", b, ^"scale", Vector2.ONE)


static func _start_row(c: CanvasItem, wait: float) -> void:
	if not is_instance_valid(c):
		return
	var tw := c.create_tween()
	tw.tween_interval(wait)
	tw.tween_callback(Motion.fade.bind(c, 1.0, &"menu_page_in"))


## True while `b` is dipped or springing back (tests).
static func dipped(b: BaseButton) -> bool:
	return Motion.held(b, ^"scale")


## Rows come in one after another: each fades from clear after the entry's delay x its index
## (`menu_page_in`). At rest at once when the motion doesn't play. Returns the seconds the last
## row takes to be whole (0 when nothing plays).
static func rise(rows: Array) -> float:
	var live := Motion.live(&"menu_page_in")
	var gap := Motion.delay_of(&"menu_page_in")
	var secs := Motion.seconds(&"menu_page_in")
	var i := 0
	for r in rows:
		var c := r as CanvasItem
		if c == null or not is_instance_valid(c):
			continue
		if not live:
			c.modulate.a = 1.0
			continue
		c.modulate.a = 0.0
		if c.is_inside_tree():
			_start_row(c, gap * float(i))
		else:
			c.tree_entered.connect(_start_row.bind(c, gap * float(i)), CONNECT_ONE_SHOT)
		i += 1
	return (gap * float(i) + secs) if live and i > 0 else 0.0
