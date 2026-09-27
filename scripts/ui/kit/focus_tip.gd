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
	var r := control.get_global_rect()
	var at := Vector2(r.position.x, r.end.y + GAP)
	if at.y + size.y > screen.end.y:
		at.y = r.position.y - GAP - size.y
	at.x = clampf(at.x, screen.position.x, maxf(screen.position.x, screen.end.x - size.x))
	at.y = clampf(at.y, screen.position.y, maxf(screen.position.y, screen.end.y - size.y))
	global_position = at
