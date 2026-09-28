class_name FocusTip
extends PanelContainer
## A control's tooltip shown while it has keyboard or pad focus (H23 S8: a shop card's
## text is cut on the sticker and a pad player never hovers, so the whole text never
## showed). The tip hangs under the control (over it when there is no room below), inside
## the screen, in the theme's tooltip look; it goes when focus leaves. Not shown while the
## mouse is over the control (the ordinary tooltip does that). View only.

## Gap between the control and the tip (px).
const GAP := 6.0


## Shows `control`'s tooltip while it has focus (not while the mouse is over it).
static func attach(control: Control) -> void:
	if control.focus_entered.is_connected(_show_for.bind(control)):
		return
	control.focus_entered.connect(_show_for.bind(control))
	control.focus_exited.connect(_hide_for.bind(control))


## The tip on screen for `control` (null when none).
static func tip_of(control: Control) -> FocusTip:
	return control.get_node_or_null(^"FocusTip") as FocusTip


static func _show_for(control: Control) -> void:
	if not is_instance_valid(control) or control.tooltip_text == "" or not control.is_inside_tree():
		return
	if control.get_global_rect().has_point(control.get_global_mouse_position()) and not Settings.pad_active:
		return
	_hide_for(control)
	var tip := FocusTip.new()
	tip.name = "FocusTip"
	tip.theme_type_variation = &"TooltipPanel"
	tip.top_level = true
	tip.mouse_filter = Control.MOUSE_FILTER_IGNORE
	tip.z_index = 50
	tip.add_child(UiTip.make(control.tooltip_text))
	control.add_child(tip)
	tip._place.call_deferred(control)
	# Animation pass ANIM-6: the tip fades in (`focus_tip_in`).
	tip.modulate.a = 0.0
	Motion.fade(tip, 1.0, &"focus_tip_in")


static func _hide_for(control: Control) -> void:
	if not is_instance_valid(control):
		return
	var old := tip_of(control)
	if old != null:
		control.remove_child(old)
		old.queue_free()


func _place(control: Control) -> void:
	if not is_instance_valid(control):
		return
	size = get_combined_minimum_size()
	var screen := control.get_viewport_rect()
	global_position = spot(control.get_global_rect(), size, screen, avoid_rects(control))


## ANIM-R1 M11: where a `tip`-sized tip for a control at `r` goes on `screen`: under it,
## beside it (right, then left) or over it, the first spot inside the screen that covers
## none of `avoid` (the page's buttons, tags and titles: the loot's tip hid Skip and the
## window's title); else the one covering the least. Pure (tests).
static func spot(r: Rect2, tip: Vector2, screen: Rect2, avoid: Array[Rect2]) -> Vector2:
	var tries: Array[Vector2] = [Vector2(r.position.x, r.end.y + GAP), Vector2(r.end.x + GAP, r.position.y),
		Vector2(r.position.x - GAP - tip.x, r.position.y), Vector2(r.position.x, r.position.y - GAP - tip.y),
		Vector2(r.end.x + GAP, r.end.y - tip.y), Vector2(r.position.x - GAP - tip.x, r.end.y - tip.y)]
	var best := Vector2.INF
	var best_hits := INF
	for at in tries:
		var p := Vector2(clampf(at.x, screen.position.x, maxf(screen.position.x, screen.end.x - tip.x)),
			clampf(at.y, screen.position.y, maxf(screen.position.y, screen.end.y - tip.y)))
		var box := Rect2(p, tip)
		var hits := 0.0
		for a in avoid:
			if box.intersects(a):
				hits += box.intersection(a).get_area() + 1.0
		# The tip never covers its own control either.
		if box.intersects(r):
			hits += box.intersection(r).get_area() + 1.0
		if hits < best_hits:
			best_hits = hits
			best = p
			if hits == 0.0:
				break
	return best


## What a tip keeps off (screen rects): the usable controls and legends on screen (as the
## SAVED stamp does), graffiti titles and terminal window title bars, except `control`
## and what is inside it.
static func avoid_rects(control: Control) -> Array[Rect2]:
	var out: Array[Rect2] = []
	if not control.is_inside_tree():
		return out
	var own := control.get_global_rect()
	for r in Fx.avoid_rects(control.get_tree().root):
		if not own.encloses(r):
			out.append(r)
	_titles(control.get_tree().root, out)
	return out


static func _titles(node: Node, out: Array[Rect2]) -> void:
	for c in node.get_children():
		if c is CanvasItem and not (c as CanvasItem).visible:
			continue
		if c is GraffitiTag or (c is Label and c.name == &"TerminalTitle"):
			out.append((c as Control).get_global_rect())
		_titles(c, out)
