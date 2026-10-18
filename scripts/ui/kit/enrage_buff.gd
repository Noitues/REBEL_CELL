class_name EnrageBuff
extends RefCounted
## N4 (plan 2 R4, ruling Q33): the enrage buff on an enemy wheel. Nothing shows before step 1
## (no countdown); from step 1 a Badge in the wheel's top-right corner reads the step and its
## tooltip says what the enrage does and when the next step comes. Reads only
## CombatResolver.enrage_buff_state; view only.

## The badge node's name on the wheel view.
const NODE_NAME := "EnrageBuff"
## Inset from the wheel view's top-right corner (px at text scale 1.0).
const INSET := 8.0


## Adds, updates or removes the buff badge on `view` for `state` (an enrage_buff_state).
static func sync(view: Control, state: Dictionary) -> void:
	var badge := view.get_node_or_null(NODE_NAME) as Badge
	if not bool(state.get("visible", false)):
		if badge != null:
			badge.queue_free()
		return
	if badge == null:
		badge = Badge.new()
		badge.name = NODE_NAME
		badge.glyph = "!"
		badge.color = Palette.CELL_PINK
		badge.mouse_filter = Control.MOUSE_FILTER_PASS
		badge.tooltip_auto_translate_mode = Node.AUTO_TRANSLATE_MODE_DISABLED
		view.add_child(badge)
	badge.text = label(state)
	badge.tooltip_text = UiTip.fold(tooltip(state))
	badge.update_minimum_size()
	badge.size = badge.get_combined_minimum_size()
	var inset := INSET * Settings.text_scale
	badge.position = Vector2(view.size.x - badge.size.x - inset, inset)
	if view is WheelView:
		# On a wheel it sits off the disc's upper right rim: the view's corner is under the key-hint bar.
		var corner := (view as WheelView).badge_corner()
		badge.position = Vector2(minf(corner.x, view.size.x - badge.size.x - inset), maxf(inset, corner.y - badge.size.y))
	badge.queue_redraw()


## The badge's words: the step ("ENRAGE 2").
static func label(state: Dictionary) -> String:
	return TranslationServer.translate("ENRAGE %d") % int(state.get("step", 0))


## The badge's tooltip: the hit factor, the per-step gain, any resistance, the next step.
static func tooltip(state: Dictionary) -> String:
	var lines := PackedStringArray()
	lines.append(TranslationServer.translate("Enraged, step %d: its hits deal %d%% damage (+%d%% each step).") % [
		int(state.get("step", 0)), int(state.get("percent", RC.PERCENT_MAX)), int(state.get("step_percent", 0))])
	if int(state.get("resistance", 0)) > 0:
		lines.append(TranslationServer.translate("+%d resistance each turn from its enrage.") % int(state["resistance"]))
	lines.append(TranslationServer.translate("Next step on turn %d (in %d turns).") % [int(state.get("next_turn", 0)), int(state.get("turns_to_next", 0))])
	return "\n".join(lines)
